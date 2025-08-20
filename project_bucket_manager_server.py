#!/usr/bin/env python3
"""
Project-Specific Bucket Manager Server
Each project gets its own lightrag_projectname directory
Supports cross-project bucket browsing and importing via symlinks
"""

import os
import json
import shutil
import asyncio
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import networkx as nx

# Import LightRAG components
try:
    from lightrag import LightRAG, QueryParam
    from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
    from lightrag.kg.shared_storage import initialize_pipeline_status
    from lightrag.utils import setup_logger
    HAS_LIGHTRAG = True
except ImportError:
    print("⚠️ LightRAG not available - file processing will be limited")
    HAS_LIGHTRAG = False

# Auto-load environment variables
try:
    from load_env import load_env_file
    load_env_file()
except ImportError:
    pass

# API key management
try:
    from util_apikey import APIKeyManager
    api_manager = APIKeyManager()
    api_key = api_manager.get_openai_key()
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key
        print(f"✅ API key loaded for server process")
except Exception as e:
    print(f"⚠️ Could not load API key: {e}")

app = Flask(__name__)
CORS(app)

class ProjectBucketManager:
    """Manages buckets for individual projects with cross-project browsing"""
    
    def __init__(self):
        self.base_dir = Path("/Users/elle/Desktop/Elizabeth_PI")
        self.projects_dir = self.base_dir / "projects"
        self.current_project = self.detect_current_project()
        self.lightrag_dir = self.base_dir / f"lightrag_{self.current_project.lower()}"
        
        # Create the project-specific lightrag directory
        self.lightrag_dir.mkdir(exist_ok=True)
        
        # Migrate existing buckets if this is the first time
        self.migrate_existing_buckets_if_needed()
        
        # Initialize LightRAG instances cache
        self.lightrag_instances = {}
        
        # Setup LightRAG logging
        if HAS_LIGHTRAG:
            setup_logger("lightrag", level="INFO")
        
        print(f"🎯 Current Project: {self.current_project}")
        print(f"📁 LightRAG Directory: {self.lightrag_dir}")
    
    def detect_current_project(self):
        """Detect the current project from Lizzy's state file or fallback methods"""
        
        # Method 1: Read from Lizzy's current project state file
        state_file = self.base_dir / '.lizzy_current_project'
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    project_name = state.get('current_project')
                    if project_name:
                        print(f"📍 Detected current project from Lizzy: {project_name}")
                        return project_name
            except Exception as e:
                print(f"⚠️ Could not read Lizzy state file: {e}")
        
        # Method 2: Check environment variable (set by Lizzy launcher)
        env_project = os.environ.get('LIZZY_PROJECT', os.environ.get('CURRENT_PROJECT'))
        if env_project:
            print(f"📍 Detected project from environment: {env_project}")
            return env_project
        
        # Method 3: Check if we're inside a project directory
        current_dir = Path.cwd()
        if current_dir.name in ['Alpha', 'Beta', 'Delta', 'gamma', 'test_project_2024']:
            print(f"📍 Detected project from working directory: {current_dir.name}")
            return current_dir.name
        
        # Method 4: Check for most recently accessed project
        projects_dir = self.base_dir / 'projects'
        if projects_dir.exists():
            most_recent_project = None
            most_recent_time = 0
            
            for project_dir in projects_dir.iterdir():
                if project_dir.is_dir():
                    sqlite_file = project_dir / f"{project_dir.name}.sqlite"
                    if sqlite_file.exists():
                        try:
                            mtime = sqlite_file.stat().st_mtime
                            if mtime > most_recent_time:
                                most_recent_time = mtime
                                most_recent_project = project_dir.name
                        except:
                            pass
            
            if most_recent_project:
                print(f"📍 Using most recently accessed project: {most_recent_project}")
                return most_recent_project
        
        # Default fallback
        print("📍 Using default project: Alpha")
        return "Alpha"
    
    def migrate_existing_buckets_if_needed(self):
        """Migrate existing buckets from lightrag_working_dir to lightrag_alpha"""
        old_lightrag = self.base_dir / "lightrag_working_dir"
        
        # If lightrag_alpha doesn't exist but lightrag_working_dir does, migrate
        if not self.lightrag_dir.exists() and old_lightrag.exists():
            print(f"🔄 Migrating existing buckets to {self.lightrag_dir}")
            shutil.copytree(old_lightrag, self.lightrag_dir)
            print("✅ Migration completed")
    
    def get_all_projects(self):
        """Get all available projects"""
        projects = []
        
        # Check if projects directory exists
        if not self.projects_dir.exists():
            print(f"Projects directory not found: {self.projects_dir}")
            return projects
        
        print(f"Looking for projects in: {self.projects_dir}")
        
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                project_name = project_dir.name
                print(f"Found project directory: {project_name}")
                
                # Check if it has a sqlite file (indicates it's a real project)
                sqlite_file = project_dir / f"{project_name}.sqlite"
                if not sqlite_file.exists():
                    print(f"  No sqlite file found for {project_name}, skipping")
                    continue
                
                lightrag_project_dir = self.base_dir / f"lightrag_{project_name.lower()}"
                print(f"  Looking for lightrag dir: {lightrag_project_dir}")
                
                # Count buckets in this project
                bucket_count = 0
                if lightrag_project_dir.exists():
                    bucket_dirs = [d for d in lightrag_project_dir.iterdir() 
                                 if d.is_dir() and not d.name.startswith('_') 
                                 and d.name not in ['imported', 'local']]
                    bucket_count = len(bucket_dirs)
                    print(f"  Found {bucket_count} buckets: {[d.name for d in bucket_dirs]}")
                else:
                    print(f"  LightRAG directory doesn't exist yet")
                
                # Get last modified time
                try:
                    last_modified = sqlite_file.stat().st_mtime
                    import time
                    last_active = time.strftime("%Y-%m-%d", time.localtime(last_modified))
                except:
                    last_active = "Unknown"
                
                projects.append({
                    "name": project_name,
                    "bucket_count": bucket_count,
                    "lightrag_dir": str(lightrag_project_dir),
                    "last_active": last_active,
                    "is_current": project_name.lower() == self.current_project.lower()
                })
                print(f"  Added project: {project_name} with {bucket_count} buckets")
        
        print(f"Total projects found: {len(projects)}")
        return projects
    
    def get_project_buckets(self, project_name=None):
        """Get buckets for a specific project"""
        if project_name is None:
            project_name = self.current_project
        
        lightrag_project_dir = self.base_dir / f"lightrag_{project_name.lower()}"
        buckets = []
        
        if not lightrag_project_dir.exists():
            return buckets
        
        # Get all bucket directories (excluding special directories)
        for bucket_dir in lightrag_project_dir.iterdir():
            if (bucket_dir.is_dir() and 
                not bucket_dir.name.startswith('_') and 
                bucket_dir.name not in ['imported', 'local']):
                
                bucket_info = self.get_bucket_stats(bucket_dir, project_name)
                if bucket_info:
                    buckets.append(bucket_info)
        
        return buckets
    
    def get_bucket_stats(self, bucket_dir, project_name):
        """Get statistics for a bucket"""
        try:
            stats = {
                "id": bucket_dir.name,
                "name": bucket_dir.name,
                "description": "Knowledge base",
                "project": project_name,
                "type": "local",
                "nodes": 0,
                "edges": 0,
                "files": [],
                "file_details": [],
                "size": "0 MB",
                "updated": "Unknown"
            }
            
            # Check if it's a symlink (imported bucket)
            if bucket_dir.is_symlink():
                stats["type"] = "imported"
                stats["description"] = f"Imported from another project"
            
            # Get graph stats
            graphml_file = bucket_dir / "graph_chunk_entity_relation.graphml"
            if graphml_file.exists():
                try:
                    G = nx.read_graphml(graphml_file)
                    stats["nodes"] = len(G.nodes())
                    stats["edges"] = len(G.edges())
                except Exception as e:
                    print(f"Warning: Could not read graph for {bucket_dir.name}: {e}")
            
            # Get files
            files = []
            file_extensions = ['.txt', '.md', '.pdf', '.docx']
            for file_path in bucket_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in file_extensions:
                    try:
                        file_stat = file_path.stat()
                        files.append({
                            "name": file_path.name,
                            "size": file_stat.st_size,
                            "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                        })
                    except Exception:
                        files.append({"name": file_path.name, "size": 0, "modified": "Unknown"})
            
            stats["files"] = [f["name"] for f in files]
            stats["file_details"] = files
            
            # Calculate total size
            total_size = 0
            try:
                for file_path in bucket_dir.rglob('*'):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
            except Exception:
                pass
            
            stats["size"] = f"{total_size / (1024*1024):.1f} MB"
            
            # Get last modified time
            try:
                stats["updated"] = datetime.fromtimestamp(bucket_dir.stat().st_mtime).strftime('%Y-%m-%d')
            except Exception:
                pass
            
            return stats
        
        except Exception as e:
            print(f"Error getting stats for {bucket_dir}: {e}")
            return None
    
    def create_bucket(self, name, description="", project_name=None):
        """Create a new bucket in the specified project"""
        if project_name is None:
            project_name = self.current_project
        
        if not name or not name.replace('_', '').replace('-', '').isalnum():
            return {"success": False, "error": "Invalid bucket name"}
        
        lightrag_project_dir = self.base_dir / f"lightrag_{project_name.lower()}"
        lightrag_project_dir.mkdir(exist_ok=True)
        
        bucket_dir = lightrag_project_dir / name
        
        if bucket_dir.exists():
            return {"success": False, "error": f"Bucket {name} already exists"}
        
        bucket_dir.mkdir()
        
        # Create a simple metadata file
        metadata = {
            "name": name,
            "description": description,
            "created": datetime.now().isoformat(),
            "project": project_name
        }
        
        with open(bucket_dir / "bucket_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {"success": True, "bucket": name, "project": project_name}
    
    def delete_bucket(self, bucket_name, project_name=None):
        """Delete a bucket from the specified project"""
        if project_name is None:
            project_name = self.current_project
        
        lightrag_project_dir = self.base_dir / f"lightrag_{project_name.lower()}"
        bucket_dir = lightrag_project_dir / bucket_name
        
        if not bucket_dir.exists():
            return {"success": False, "error": "Bucket not found"}
        
        # If it's a symlink, just remove the link
        if bucket_dir.is_symlink():
            bucket_dir.unlink()
        else:
            # Remove the entire directory
            shutil.rmtree(bucket_dir)
        
        return {"success": True, "message": f"Deleted bucket: {bucket_name}"}
    
    def import_bucket_from_project(self, source_bucket_name, source_project, target_project=None):
        """Import a bucket from another project via symlink"""
        if target_project is None:
            target_project = self.current_project
        
        source_lightrag_dir = self.base_dir / f"lightrag_{source_project.lower()}"
        target_lightrag_dir = self.base_dir / f"lightrag_{target_project.lower()}"
        
        source_bucket = source_lightrag_dir / source_bucket_name
        target_bucket = target_lightrag_dir / source_bucket_name
        
        if not source_bucket.exists():
            return {"success": False, "error": f"Source bucket not found in {source_project}"}
        
        if target_bucket.exists():
            return {"success": False, "error": f"Bucket {source_bucket_name} already exists in {target_project}"}
        
        target_lightrag_dir.mkdir(exist_ok=True)
        
        try:
            # Create symlink
            target_bucket.symlink_to(source_bucket)
            return {"success": True, "message": f"Imported {source_bucket_name} from {source_project}"}
        except Exception as e:
            return {"success": False, "error": f"Failed to create symlink: {str(e)}"}
    
    async def get_lightrag_instance(self, bucket_name, project_name=None):
        """Get or create a LightRAG instance for a bucket"""
        if not HAS_LIGHTRAG:
            return None
            
        if project_name is None:
            project_name = self.current_project
        
        bucket_key = f"{project_name}_{bucket_name}"
        
        if bucket_key not in self.lightrag_instances:
            lightrag_project_dir = self.base_dir / f"lightrag_{project_name.lower()}"
            bucket_dir = lightrag_project_dir / bucket_name
            
            if not bucket_dir.exists():
                return None
            
            try:
                # Initialize LightRAG instance
                rag = LightRAG(
                    working_dir=str(bucket_dir),
                    embedding_func=openai_embed,
                    llm_model_func=gpt_4o_mini_complete,
                )
                
                # IMPORTANT: Both initialization calls are required per LightRAG docs
                await rag.initialize_storages()
                await initialize_pipeline_status()
                
                self.lightrag_instances[bucket_key] = rag
                print(f"✅ Initialized LightRAG for {project_name}/{bucket_name}")
                
            except Exception as e:
                print(f"⚠️ Failed to initialize LightRAG for {bucket_name}: {e}")
                return None
        
        return self.lightrag_instances.get(bucket_key)

    def add_file_to_bucket(self, bucket_name, file_content, filename, project_name=None):
        """Add a file to a bucket and process with LightRAG"""
        if project_name is None:
            project_name = self.current_project
        
        lightrag_project_dir = self.base_dir / f"lightrag_{project_name.lower()}"
        bucket_dir = lightrag_project_dir / bucket_name
        
        if not bucket_dir.exists():
            return {"success": False, "error": "Bucket not found"}
        
        file_path = bucket_dir / filename
        
        try:
            # Save the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            # Process with LightRAG if available
            if HAS_LIGHTRAG:
                try:
                    # Run async LightRAG processing
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(self._process_file_with_lightrag(bucket_name, file_content, project_name))
                    loop.close()
                    
                    if result:
                        return {"success": True, "file": filename, "processed": True, "message": "File saved and processed with LightRAG"}
                    else:
                        return {"success": True, "file": filename, "processed": False, "message": "File saved but LightRAG processing failed"}
                        
                except Exception as e:
                    print(f"⚠️ LightRAG processing error: {e}")
                    return {"success": True, "file": filename, "processed": False, "error": f"File saved but processing failed: {str(e)}"}
            
            return {"success": True, "file": filename, "processed": False, "message": "File saved (LightRAG not available)"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _process_file_with_lightrag(self, bucket_name, file_content, project_name):
        """Process file content with LightRAG"""
        try:
            rag = await self.get_lightrag_instance(bucket_name, project_name)
            if rag is None:
                return False
            
            # Insert content into LightRAG
            await rag.ainsert(file_content)
            print(f"✅ Processed file content with LightRAG for {project_name}/{bucket_name}")
            return True
            
        except Exception as e:
            print(f"⚠️ LightRAG processing error: {e}")
            return False
    
    def delete_file_from_bucket(self, bucket_name, filename, project_name=None):
        """Delete a file from a bucket"""
        if project_name is None:
            project_name = self.current_project
        
        lightrag_project_dir = self.base_dir / f"lightrag_{project_name.lower()}"
        file_path = lightrag_project_dir / bucket_name / filename
        
        if not file_path.exists():
            return {"success": False, "error": "File not found"}
        
        try:
            file_path.unlink()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Initialize the manager
manager = ProjectBucketManager()

# API Routes

@app.route('/')
def index():
    """Serve the modern bucket manager HTML"""
    return send_file('modern_bucket_manager.html')

@app.route('/modern_bucket_manager.html')
def serve_html():
    """Serve the modern bucket manager HTML"""
    return send_file('modern_bucket_manager.html')

@app.route('/api/current-project')
def get_current_project():
    """Get the current project info"""
    return jsonify({
        "name": manager.current_project,
        "lightrag_dir": str(manager.lightrag_dir)
    })

@app.route('/api/projects')
def get_all_projects():
    """Get all available projects"""
    projects = manager.get_all_projects()
    return jsonify(projects)

@app.route('/api/buckets')
def get_current_project_buckets():
    """Get buckets for the current project"""
    buckets = manager.get_project_buckets()
    return jsonify(buckets)

@app.route('/api/projects/<project_name>/buckets')
def get_project_buckets(project_name):
    """Get buckets for a specific project"""
    buckets = manager.get_project_buckets(project_name)
    return jsonify(buckets)

@app.route('/api/buckets', methods=['POST'])
def create_bucket():
    """Create a new bucket in the current project"""
    data = request.json
    result = manager.create_bucket(
        data.get('name'),
        data.get('description', '')
    )
    return jsonify(result)

@app.route('/api/buckets/<bucket_name>', methods=['DELETE'])
def delete_bucket(bucket_name):
    """Delete a bucket from the current project"""
    result = manager.delete_bucket(bucket_name)
    return jsonify(result)

@app.route('/api/import/<source_project>/<bucket_name>', methods=['POST'])
def import_bucket(source_project, bucket_name):
    """Import a bucket from another project"""
    result = manager.import_bucket_from_project(bucket_name, source_project)
    return jsonify(result)

@app.route('/api/buckets/<bucket_name>/files', methods=['POST'])
def add_file_to_bucket(bucket_name):
    """Add a file to a bucket"""
    data = request.json
    result = manager.add_file_to_bucket(
        bucket_name,
        data.get('content', ''),
        data.get('filename', 'document.txt')
    )
    return jsonify(result)

@app.route('/api/buckets/<bucket_name>/files/<filename>', methods=['DELETE'])
def delete_file(bucket_name, filename):
    """Delete a file from a bucket"""
    result = manager.delete_file_from_bucket(bucket_name, filename)
    return jsonify(result)

@app.route('/api/buckets/<bucket_name>/process', methods=['POST'])
def process_bucket_files(bucket_name):
    """Process all files in a bucket with LightRAG"""
    
    if not HAS_LIGHTRAG:
        return jsonify({"success": False, "error": "LightRAG not available"})
    
    try:
        # Get bucket directory
        lightrag_project_dir = manager.base_dir / f"lightrag_{manager.current_project.lower()}"
        bucket_dir = lightrag_project_dir / bucket_name
        
        if not bucket_dir.exists():
            return jsonify({"success": False, "error": "Bucket not found"})
        
        # Find all text files
        text_files = []
        for file_path in bucket_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in ['.txt', '.md', '.csv']:
                text_files.append(file_path)
        
        if not text_files:
            return jsonify({"success": False, "error": "No processable files found"})
        
        # Process files with LightRAG
        processed_files = []
        failed_files = []
        
        # Run async processing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def process_all():
            rag = await manager.get_lightrag_instance(bucket_name)
            if rag is None:
                return False
            
            for file_path in text_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    await rag.ainsert(content)
                    processed_files.append(file_path.name)
                    print(f"✅ Processed {file_path.name}")
                    
                except Exception as e:
                    failed_files.append({"file": file_path.name, "error": str(e)})
                    print(f"⚠️ Failed to process {file_path.name}: {e}")
            
            return True
        
        success = loop.run_until_complete(process_all())
        loop.close()
        
        return jsonify({
            "success": success,
            "processed_files": processed_files,
            "failed_files": failed_files,
            "total_processed": len(processed_files),
            "total_failed": len(failed_files)
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/stats')
def get_stats():
    """Get overall statistics for the current project"""
    buckets = manager.get_project_buckets()
    
    total_nodes = sum(b['nodes'] for b in buckets)
    total_edges = sum(b['edges'] for b in buckets)
    total_files = sum(len(b['files']) for b in buckets)
    
    return jsonify({
        "total_buckets": len(buckets),
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "total_files": total_files,
        "project": manager.current_project
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint for system status"""
    return jsonify({
        "status": "healthy",
        "lightrag_available": HAS_LIGHTRAG,
        "current_project": manager.current_project,
        "lightrag_dir": str(manager.lightrag_dir),
        "api_key_available": bool(os.environ.get('OPENAI_API_KEY')),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/debug')
def debug_info():
    """Debug endpoint to check paths and data"""
    return jsonify({
        "current_project": manager.current_project,
        "lightrag_dir": str(manager.lightrag_dir),
        "lightrag_dir_exists": manager.lightrag_dir.exists(),
        "projects_dir": str(manager.projects_dir),
        "projects_dir_exists": manager.projects_dir.exists(),
        "base_dir": str(manager.base_dir),
        "all_projects": manager.get_all_projects()
    })

@app.route('/api/switch-project/<project_name>', methods=['POST'])
def switch_project(project_name):
    """Switch to a different project"""
    global manager
    
    # Verify the project exists
    projects_dir = Path("/Users/elle/Desktop/Elizabeth_PI/projects")
    project_dir = projects_dir / project_name
    sqlite_file = project_dir / f"{project_name}.sqlite"
    
    if not sqlite_file.exists():
        return jsonify({"success": False, "error": f"Project {project_name} not found"})
    
    # Reinitialize the manager with the new project
    old_project = manager.current_project
    
    # Update the current project
    manager.current_project = project_name
    manager.lightrag_dir = manager.base_dir / f"lightrag_{project_name.lower()}"
    manager.lightrag_dir.mkdir(exist_ok=True)
    
    print(f"🔄 Switched from {old_project} to {project_name}")
    print(f"📁 New LightRAG Directory: {manager.lightrag_dir}")
    
    return jsonify({
        "success": True, 
        "old_project": old_project,
        "new_project": project_name,
        "lightrag_dir": str(manager.lightrag_dir)
    })

if __name__ == '__main__':
    print("🚀 Starting Project-Specific Bucket Manager Server...")
    print(f"📊 Current Project: {manager.current_project}")
    print(f"📁 LightRAG Directory: {manager.lightrag_dir}")
    print("🌐 Access at http://localhost:8002")
    app.run(host='0.0.0.0', port=8002, debug=False)