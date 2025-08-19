#!/usr/bin/env python3
"""
Bucket Manager Server - Backend for the bucket management GUI
Provides REST API for LightRAG bucket operations
"""

# Import os first
import os

# Auto-load environment variables from .env file
try:
    from load_env import load_env_file
    load_env_file()
except ImportError:
    pass

# Ensure API key is available
try:
    from util_apikey import APIKeyManager
    api_manager = APIKeyManager()
    api_key = api_manager.get_openai_key()
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key
        print(f"✅ API key loaded for server: {api_key[:10]}...")
        print(f"✅ Environment OPENAI_API_KEY set: {bool(os.environ.get('OPENAI_API_KEY'))}")
    else:
        print("❌ No API key found - processing will fail")
        # Try direct from config file as fallback
        try:
            import json
            with open('api_config.json', 'r') as f:
                config = json.load(f)
                fallback_key = config.get('api_keys', {}).get('openai')
                if fallback_key:
                    os.environ['OPENAI_API_KEY'] = fallback_key
                    print(f"✅ Fallback API key loaded: {fallback_key[:10]}...")
        except Exception as fe:
            print(f"❌ Fallback also failed: {fe}")
except Exception as e:
    print(f"⚠️ Could not load API key: {e}")

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import networkx as nx
from datetime import datetime
from pathlib import Path
import shutil
import zipfile
from io import BytesIO

# Import LightRAG components
try:
    from lightrag import LightRAG, QueryParam
    from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
    import asyncio
    HAS_LIGHTRAG = True
    
    # Create wrapper classes that preserve the required attributes
    class SyncEmbeddingWrapper:
        """Sync wrapper for OpenAI embedding that preserves attributes"""
        def __init__(self, async_embed_func):
            self.async_func = async_embed_func
            # Copy over required attributes
            self.embedding_dim = getattr(async_embed_func, 'embedding_dim', 1536)
            self.max_token_size = getattr(async_embed_func, 'max_token_size', 8192)
        
        def __call__(self, text_list):
            try:
                # Check if we're in an event loop already
                try:
                    loop = asyncio.get_running_loop()
                    # We're in a running loop, create a new thread
                    import concurrent.futures
                    import threading
                    
                    def run_in_thread():
                        # Create a new event loop for this thread
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        try:
                            return new_loop.run_until_complete(self.async_func(text_list))
                        finally:
                            new_loop.close()
                    
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(run_in_thread)
                        return future.result(timeout=30)
                        
                except RuntimeError:
                    # No running loop, we can use asyncio.run
                    return asyncio.run(self.async_func(text_list))
                    
            except Exception as e:
                print(f"Embedding error: {e}")
                # Return dummy embeddings to prevent crashes
                import numpy as np
                return [np.zeros(self.embedding_dim).tolist() for _ in text_list]
    
    class SyncLLMWrapper:
        """Sync wrapper for GPT completion"""
        def __init__(self, async_llm_func):
            self.async_func = async_llm_func
        
        def __call__(self, prompt, **kwargs):
            try:
                # Check if we're in an event loop already
                try:
                    loop = asyncio.get_running_loop()
                    # We're in a running loop, create a new thread
                    import concurrent.futures
                    
                    def run_in_thread():
                        # Create a new event loop for this thread
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        try:
                            return new_loop.run_until_complete(self.async_func(prompt, **kwargs))
                        finally:
                            new_loop.close()
                    
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(run_in_thread)
                        return future.result(timeout=60)
                        
                except RuntimeError:
                    # No running loop, we can use asyncio.run
                    return asyncio.run(self.async_func(prompt, **kwargs))
                    
            except Exception as e:
                print(f"LLM completion error: {e}")
                return "Error: Could not complete request"
    
    # Create the wrapped functions
    sync_openai_embed = SyncEmbeddingWrapper(openai_embed)
    sync_gpt_4o_mini_complete = SyncLLMWrapper(gpt_4o_mini_complete)
    
except ImportError:
    HAS_LIGHTRAG = False
    print("⚠️ LightRAG not installed. Running in demo mode.")

app = Flask(__name__)
CORS(app)

# Configuration
BASE_DIR = "lightrag_working_dir"
BUCKET_CONFIG_FILE = os.path.join(BASE_DIR, "bucket_config.json")

class BucketManager:
    """Manages LightRAG buckets and provides API operations"""
    
    def __init__(self):
        self.base_dir = BASE_DIR
        os.makedirs(self.base_dir, exist_ok=True)
        self.load_config()
    
    def load_config(self):
        """Load bucket configuration"""
        if os.path.exists(BUCKET_CONFIG_FILE):
            with open(BUCKET_CONFIG_FILE, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {"buckets": [], "metadata": {}}
    
    def save_config(self):
        """Save bucket configuration"""
        with open(BUCKET_CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_bucket_stats(self, bucket_name):
        """Get statistics for a bucket"""
        bucket_dir = os.path.join(self.base_dir, bucket_name)
        graphml_file = os.path.join(bucket_dir, "graph_chunk_entity_relation.graphml")
        
        stats = {
            "nodes": 0,
            "edges": 0,
            "files": [],
            "size": "0 MB"
        }
        
        # Get graph stats
        if os.path.exists(graphml_file):
            try:
                G = nx.read_graphml(graphml_file)
                stats["nodes"] = len(G.nodes())
                stats["edges"] = len(G.edges())
            except:
                pass
        
        # Get files
        if os.path.exists(bucket_dir):
            files = []
            for f in os.listdir(bucket_dir):
                if f.endswith(('.txt', '.md', '.pdf', '.docx')):
                    file_path = os.path.join(bucket_dir, f)
                    file_stat = os.stat(file_path)
                    files.append({
                        "name": f,
                        "size": file_stat.st_size,
                        "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                    })
            stats["files"] = files
            
            # Calculate total size
            total_size = sum(os.path.getsize(os.path.join(bucket_dir, f)) 
                           for f in os.listdir(bucket_dir) 
                           if os.path.isfile(os.path.join(bucket_dir, f)))
            stats["size"] = f"{total_size / (1024*1024):.1f} MB"
        
        return stats
    
    def get_all_buckets(self):
        """Get all buckets with their stats"""
        buckets = []
        
        # Scan directory for buckets
        if os.path.exists(self.base_dir):
            for item in os.listdir(self.base_dir):
                item_path = os.path.join(self.base_dir, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    # Check if it's a valid bucket (has graphml file or is in config)
                    graphml_file = os.path.join(item_path, "graph_chunk_entity_relation.graphml")
                    if os.path.exists(graphml_file) or item in self.config.get("buckets", []):
                        stats = self.get_bucket_stats(item)
                        
                        # Get metadata from config
                        metadata = self.config.get("metadata", {}).get(item, {})
                        
                        bucket_info = {
                            "id": item,
                            "name": item,
                            "description": metadata.get("description", "No description"),
                            "nodes": stats["nodes"],
                            "edges": stats["edges"],
                            "files": [f["name"] for f in stats["files"]],
                            "file_details": stats["files"],
                            "size": stats["size"],
                            "updated": metadata.get("last_updated", datetime.now().isoformat().split('T')[0])
                        }
                        buckets.append(bucket_info)
        
        return buckets
    
    def create_bucket(self, name, description=""):
        """Create a new bucket"""
        if not name or not name.replace('_', '').isalnum():
            return {"success": False, "error": "Invalid bucket name"}
        
        bucket_dir = os.path.join(self.base_dir, name)
        if os.path.exists(bucket_dir):
            return {"success": False, "error": "Bucket already exists"}
        
        # Create directory
        os.makedirs(bucket_dir, exist_ok=True)
        
        # Update config
        if name not in self.config["buckets"]:
            self.config["buckets"].append(name)
        
        self.config["metadata"][name] = {
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        self.save_config()
        
        # Initialize LightRAG if available
        if HAS_LIGHTRAG:
            try:
                rag = LightRAG(
                    working_dir=bucket_dir,
                    embedding_func=sync_openai_embed,
                    llm_model_func=sync_gpt_4o_mini_complete
                )
                print(f"✅ Initialized LightRAG for bucket: {name}")
            except Exception as e:
                print(f"⚠️ Error initializing LightRAG: {e}")
        
        return {"success": True, "bucket": name}
    
    def delete_bucket(self, name):
        """Delete a bucket"""
        bucket_dir = os.path.join(self.base_dir, name)
        
        if not os.path.exists(bucket_dir):
            return {"success": False, "error": "Bucket not found"}
        
        # Remove directory
        shutil.rmtree(bucket_dir)
        
        # Update config
        if name in self.config["buckets"]:
            self.config["buckets"].remove(name)
        if name in self.config["metadata"]:
            del self.config["metadata"][name]
        
        self.save_config()
        
        return {"success": True}
    
    def add_file_to_bucket(self, bucket_name, file_content, filename):
        """Add a file to a bucket"""
        bucket_dir = os.path.join(self.base_dir, bucket_name)
        
        if not os.path.exists(bucket_dir):
            return {"success": False, "error": "Bucket not found"}
        
        # Save file
        file_path = os.path.join(bucket_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        # Update metadata
        if bucket_name in self.config["metadata"]:
            self.config["metadata"][bucket_name]["last_updated"] = datetime.now().isoformat()
            self.save_config()
        
        # Process with LightRAG if available
        if HAS_LIGHTRAG:
            try:
                # For now, save to a processing queue file for manual processing
                # This ensures files are saved and can be processed later
                processing_queue_file = os.path.join(bucket_dir, "processing_queue.json")
                
                queue_data = []
                if os.path.exists(processing_queue_file):
                    with open(processing_queue_file, 'r') as f:
                        queue_data = json.load(f)
                
                queue_data.append({
                    "filename": filename,
                    "content_preview": file_content[:200] + "..." if len(file_content) > 200 else file_content,
                    "timestamp": datetime.now().isoformat(),
                    "status": "pending_processing",
                    "content_length": len(file_content)
                })
                
                with open(processing_queue_file, 'w') as f:
                    json.dump(queue_data, f, indent=2)
                
                print(f"📁 {filename} saved and queued for LightRAG processing")
                print(f"💡 Note: Due to async compatibility issues, use CLI for LightRAG processing")
                
            except Exception as e:
                print(f"Error queuing for LightRAG: {e}")
                print("📁 File saved but not queued for processing")
        
        return {"success": True, "file": filename}
    
    def delete_file_from_bucket(self, bucket_name, filename):
        """Delete a file from a bucket"""
        file_path = os.path.join(self.base_dir, bucket_name, filename)
        
        if not os.path.exists(file_path):
            return {"success": False, "error": "File not found"}
        
        os.remove(file_path)
        
        # Update metadata
        if bucket_name in self.config["metadata"]:
            self.config["metadata"][bucket_name]["last_updated"] = datetime.now().isoformat()
            self.save_config()
        
        return {"success": True}
    
    def export_bucket(self, bucket_name):
        """Export a bucket as a zip file"""
        bucket_dir = os.path.join(self.base_dir, bucket_name)
        
        if not os.path.exists(bucket_dir):
            return None
        
        # Create zip file in memory
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(bucket_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, bucket_dir)
                    zip_file.write(file_path, arc_name)
        
        zip_buffer.seek(0)
        return zip_buffer

# Initialize manager
manager = BucketManager()

# API Routes

@app.route('/')
def index():
    """Serve the bucket manager HTML"""
    return send_file('bucket_manager.html')

@app.route('/api/buckets', methods=['GET'])
def get_buckets():
    """Get all buckets"""
    buckets = manager.get_all_buckets()
    return jsonify(buckets)

@app.route('/api/buckets/<bucket_name>', methods=['GET'])
def get_bucket(bucket_name):
    """Get a specific bucket"""
    stats = manager.get_bucket_stats(bucket_name)
    metadata = manager.config.get("metadata", {}).get(bucket_name, {})
    
    return jsonify({
        "name": bucket_name,
        "description": metadata.get("description", ""),
        "stats": stats,
        "metadata": metadata
    })

@app.route('/api/buckets', methods=['POST'])
def create_bucket():
    """Create a new bucket"""
    data = request.json
    result = manager.create_bucket(
        data.get('name'),
        data.get('description', '')
    )
    return jsonify(result)

@app.route('/api/buckets/<bucket_name>', methods=['DELETE'])
def delete_bucket(bucket_name):
    """Delete a bucket"""
    result = manager.delete_bucket(bucket_name)
    return jsonify(result)

@app.route('/api/buckets/<bucket_name>/files', methods=['POST'])
def add_file(bucket_name):
    """Add a file to a bucket and automatically process it"""
    data = request.json
    filename = data.get('filename', 'document.txt')
    content = data.get('content', '')
    
    # First, add the file to the bucket
    result = manager.add_file_to_bucket(bucket_name, content, filename)
    
    if result.get('success'):
        # Automatically trigger processing to build knowledge graph
        try:
            from core_knowledge import LightRAGManager
            kg_manager = LightRAGManager()
            
            # Process the newly added file immediately
            process_result = kg_manager.add_document_to_bucket(
                bucket_name, 
                content, 
                metadata={"source_file": filename, "filename": filename}
            )
            
            if process_result.get('success'):
                # Get updated stats
                stats = kg_manager.get_knowledge_graph_stats(bucket_name)
                result['processing'] = {
                    'success': True,
                    'stats': stats,
                    'message': f'✅ Successfully processed {process_result.get("filename", "document")}',
                    'details': {
                        'document_length': process_result.get('document_length'),
                        'new_document_count': process_result.get('new_document_count'),
                        'processing_step': process_result.get('step')
                    }
                }
            else:
                result['processing'] = {
                    'success': False,
                    'message': f'❌ Processing failed at {process_result.get("step", "unknown")} step',
                    'error': process_result.get('error', 'Unknown error'),
                    'error_type': process_result.get('error_type'),
                    'filename': process_result.get('filename')
                }
                
        except Exception as e:
            result['processing'] = {
                'success': False,
                'error': str(e),
                'message': 'File uploaded but auto-processing failed'
            }
    
    return jsonify(result)

@app.route('/api/buckets/<bucket_name>/files/<filename>', methods=['DELETE'])
def delete_file(bucket_name, filename):
    """Delete a file from a bucket"""
    result = manager.delete_file_from_bucket(bucket_name, filename)
    return jsonify(result)

@app.route('/api/buckets/<bucket_name>/export', methods=['GET'])
def export_bucket(bucket_name):
    """Export a bucket as zip"""
    zip_buffer = manager.export_bucket(bucket_name)
    if zip_buffer:
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'{bucket_name}_export.zip'
        )
    return jsonify({"error": "Bucket not found"}), 404

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    buckets = manager.get_all_buckets()
    
    total_nodes = sum(b['nodes'] for b in buckets)
    total_edges = sum(b['edges'] for b in buckets)
    total_files = sum(len(b['files']) for b in buckets)
    
    return jsonify({
        "total_buckets": len(buckets),
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "total_files": total_files
    })

@app.route('/api/apikey/status', methods=['GET'])
def get_api_key_status():
    """Get current API key status"""
    try:
        from util_apikey import APIKeyManager
        api_manager = APIKeyManager()
        status = api_manager.get_api_status()
        return jsonify(status)
    except ImportError:
        return jsonify({"error": "API key management not available"}), 500

@app.route('/api/apikey/set', methods=['POST'])
def set_api_key():
    """Set and test API key"""
    try:
        from util_apikey import APIKeyManager
        data = request.get_json()
        api_key = data.get('apiKey', '').strip()
        
        if not api_key:
            return jsonify({"success": False, "error": "API key is required"}), 400
        
        api_manager = APIKeyManager()
        
        # Set the key
        if not api_manager.set_openai_key(api_key):
            return jsonify({"success": False, "error": "Invalid API key format"}), 400
        
        # Test the key immediately
        test_result = api_manager.test_openai_key(api_key)
        
        return jsonify({
            "success": test_result["success"],
            "test_result": test_result
        })
        
    except ImportError:
        return jsonify({"success": False, "error": "API key management not available"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/apikey/test', methods=['POST'])
def test_api_key():
    """Test current API key"""
    try:
        from util_apikey import APIKeyManager
        api_manager = APIKeyManager()
        result = api_manager.test_openai_key()
        return jsonify(result)
    except ImportError:
        return jsonify({"error": "API key management not available"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/buckets/<bucket_name>/process', methods=['POST'])
def process_bucket_files(bucket_name):
    """Process all queued files in a bucket to build knowledge graph"""
    try:
        from core_knowledge import LightRAGManager
        
        # bucket_name is already passed as parameter
        kg_manager = LightRAGManager()
        
        # Check if bucket exists
        if bucket_name not in [b['name'] for b in kg_manager.get_bucket_list()]:
            return jsonify({"success": False, "error": "Bucket not found"}), 404
        
        # Process queued files
        result = kg_manager.batch_process_files(bucket_name)
        
        if "error" in result:
            return jsonify({"success": False, "error": result["error"]}), 400
        
        return jsonify({
            "success": True,
            "processed": result.get("processed", 0),
            "failed": result.get("failed", 0),
            "stats": result.get("final_stats", {})
        })
        
    except ImportError:
        return jsonify({"success": False, "error": "LightRAG not available"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Bucket Manager Server...")
    print("📊 Access the interface at http://localhost:8002")
    print("✨ LightRAG integration:", "Enabled" if HAS_LIGHTRAG else "Disabled (demo mode)")
    app.run(host='0.0.0.0', port=8002, debug=False)