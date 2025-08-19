"""
LightRAG Management and Visualization Layer for Lizzy
Handles knowledge graph operations, bucket management, and data queries
"""

import os
import sys
import json
import sqlite3
import webbrowser
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status
import networkx as nx
import matplotlib.pyplot as plt
from io import StringIO
from bucket_alt.util_visualizer import create_interactive_graph, create_multi_graph_explorer

# Auto-load environment variables from .env file
try:
    from load_env import load_env_file
    load_env_file()
except ImportError:
    pass


class LightRAGManager:
    """Manages LightRAG instances and provides visualization/query capabilities"""
    
    def __init__(self, base_dir="lightrag_working_dir"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        self.buckets = {}
        self.bucket_metadata = {}
        self.active_buckets = set()
        self.performance_stats = {}
        self.query_history = []
        self.system_metrics = {}
        self.load_bucket_config()
        # Load performance statistics after bucket config
        self.load_performance_stats()
        self.initialize_statistics_tracking()
    
    def create_bucket(self, bucket_name: str, description: str = "", auto_activate: bool = True) -> bool:
        """Create a new LightRAG bucket"""
        if bucket_name in self.buckets:
            print(f"⚠️ Bucket '{bucket_name}' already exists")
            return False
        
        bucket_dir = os.path.join(self.base_dir, bucket_name)
        os.makedirs(bucket_dir, exist_ok=True)
        
        # Initialize LightRAG instance
        rag = LightRAG(
            working_dir=bucket_dir,
            embedding_func=openai_embed,
            llm_model_func=gpt_4o_mini_complete
        )
        
        # Initialize storages synchronously for now (async version would be better)
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Initialize LightRAG v1.4.7+ requirements
        async def init_rag():
            await rag.initialize_storages()
            await initialize_pipeline_status()
        
        loop.run_until_complete(init_rag())
        self.buckets[bucket_name] = rag
        
        # Store metadata
        self.bucket_metadata[bucket_name] = {
            "name": bucket_name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "document_count": 0,
            "entity_count": 0,
            "relationship_count": 0,
            "last_updated": datetime.now().isoformat()
        }
        
        if auto_activate:
            self.active_buckets.add(bucket_name)
        
        self.save_bucket_config()
        print(f"✅ Created bucket: {bucket_name}")
        return True
    
    def load_bucket(self, bucket_name: str) -> bool:
        """Load an existing bucket"""
        bucket_dir = os.path.join(self.base_dir, bucket_name)
        
        if not os.path.exists(bucket_dir):
            print(f"❌ Bucket directory not found: {bucket_name}")
            return False
        
        if bucket_name not in self.buckets:
            # Create LightRAG instance
            rag = LightRAG(
                working_dir=bucket_dir,
                embedding_func=openai_embed,
                llm_model_func=gpt_4o_mini_complete
            )
            
            # Initialize storages synchronously for LightRAG v1.4.7+
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Initialize LightRAG v1.4.7+ requirements
            async def init_rag():
                await rag.initialize_storages()
                await initialize_pipeline_status()
            
            loop.run_until_complete(init_rag())
            self.buckets[bucket_name] = rag
        
        return True
    
    def add_document_to_bucket(self, bucket_name: str, document: str, metadata: Dict = None) -> Dict:
        """Add a document to a specific bucket with performance tracking"""
        if bucket_name not in self.buckets:
            if not self.load_bucket(bucket_name):
                return {"success": False, "error": "Failed to load bucket", "step": "initialization"}
        
        start_time = time.time()
        try:
            # Insert document into LightRAG using async method
            print(f"🔄 Processing document: {metadata.get('filename', 'document')} ({len(document)} characters)")
            print(f"📊 Step 1/4: Preparing document for LightRAG insertion...")
            
            # Use async insertion method
            import asyncio
            async def insert_doc():
                print(f"📊 Step 2/4: Generating embeddings and extracting entities...")
                await self.buckets[bucket_name].ainsert(document)
                print(f"📊 Step 3/4: Building knowledge graph relationships...")
            
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            loop.run_until_complete(insert_doc())
            print(f"📊 Step 4/4: Updating metadata and saving to storage...")
            print(f"✅ Document processing completed successfully!")
            
            # Update metadata
            if bucket_name in self.bucket_metadata:
                if "document_count" not in self.bucket_metadata[bucket_name]:
                    self.bucket_metadata[bucket_name]["document_count"] = 0
                self.bucket_metadata[bucket_name]["document_count"] += 1
                self.bucket_metadata[bucket_name]["last_updated"] = datetime.now().isoformat()
            
            # Store document metadata
            doc_meta_file = os.path.join(self.base_dir, bucket_name, "documents.json")
            doc_metadata = []
            if os.path.exists(doc_meta_file):
                with open(doc_meta_file, 'r') as f:
                    doc_metadata = json.load(f)
            
            doc_metadata.append({
                "timestamp": datetime.now().isoformat(),
                "content_preview": document[:200],
                "metadata": metadata or {},
                "length": len(document)
            })
            
            with open(doc_meta_file, 'w') as f:
                json.dump(doc_metadata, f, indent=2)
            
            print(f"✅ Added document to {bucket_name}")
            
            # Track performance
            end_time = time.time()
            self.track_processing_performance(
                bucket_name, "document_insert", start_time, end_time, True,
                {"document_length": len(document), "filename": metadata.get('filename', 'document')}
            )
            
            # Return detailed success info
            return {
                "success": True,
                "step": "completed",
                "filename": metadata.get('filename', 'document'),
                "document_length": len(document),
                "bucket": bucket_name,
                "new_document_count": self.bucket_metadata[bucket_name].get("document_count", 0),
                "processing_time": round(end_time - start_time, 3)
            }
            
        except Exception as e:
            end_time = time.time()
            print(f"❌ Error adding document to {bucket_name}: {e}")
            print(f"❌ Error type: {type(e).__name__}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            
            # Track failed processing
            self.track_processing_performance(
                bucket_name, "document_insert", start_time, end_time, False,
                {"error": str(e), "filename": metadata.get('filename', 'document') if metadata else 'document'}
            )
            
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "step": "processing",
                "filename": metadata.get('filename', 'document') if metadata else 'document',
                "processing_time": round(end_time - start_time, 3)
            }
    
    def toggle_bucket(self, bucket_name: str, active: bool) -> bool:
        """Toggle a bucket on or off"""
        if bucket_name not in self.bucket_metadata:
            print(f"❌ Bucket not found: {bucket_name}")
            return False
        
        if active:
            self.active_buckets.add(bucket_name)
        else:
            self.active_buckets.discard(bucket_name)
        
        self.save_bucket_config()
        status = "activated" if active else "deactivated"
        print(f"✅ Bucket '{bucket_name}' {status}")
        return True
    
    def query_bucket(self, bucket_name: str, query: str, mode: str = "hybrid") -> Dict:
        """Query a specific bucket with performance tracking"""
        if bucket_name not in self.buckets:
            if not self.load_bucket(bucket_name):
                return {"error": f"Bucket not found: {bucket_name}"}
        
        start_time = time.time()
        try:
            result = self.buckets[bucket_name].query(
                query,
                param=QueryParam(mode=mode)
            )
            
            end_time = time.time()
            
            # Track performance
            result_length = len(str(result)) if result else 0
            self.track_query_performance(bucket_name, query, mode, start_time, end_time, result_length)
            
            return {
                "bucket": bucket_name,
                "query": query,
                "mode": mode,
                "response": result,
                "timestamp": datetime.now().isoformat(),
                "response_time": round(end_time - start_time, 3)
            }
            
        except Exception as e:
            end_time = time.time()
            # Track failed query
            self.track_query_performance(bucket_name, query, mode, start_time, end_time, 0)
            return {
                "error": str(e),
                "bucket": bucket_name,
                "query": query,
                "response_time": round(end_time - start_time, 3)
            }
    
    def query_active_buckets(self, query: str, mode: str = "hybrid") -> List[Dict]:
        """Query all active buckets"""
        results = []
        
        for bucket_name in self.active_buckets:
            result = self.query_bucket(bucket_name, query, mode)
            results.append(result)
        
        return results
    
    def get_knowledge_graph_stats(self, bucket_name: str) -> Dict:
        """Get statistics about a bucket's knowledge graph"""
        bucket_dir = os.path.join(self.base_dir, bucket_name)
        
        stats = {
            "bucket": bucket_name,
            "entities": 0,
            "relationships": 0,
            "documents": 0
        }
        
        # Count entities from vector database
        entities_file = os.path.join(bucket_dir, "vdb_entities.json")
        if os.path.exists(entities_file):
            try:
                with open(entities_file, 'r') as f:
                    data = json.load(f)
                    if 'data' in data:
                        stats["entities"] = len(data['data'])
            except:
                pass
        
        # Count relationships from vector database
        relations_file = os.path.join(bucket_dir, "vdb_relationships.json")
        if os.path.exists(relations_file):
            try:
                with open(relations_file, 'r') as f:
                    data = json.load(f)
                    if 'data' in data:
                        stats["relationships"] = len(data['data'])
            except:
                pass
        
        # Count chunks (documents) from vector database
        chunks_file = os.path.join(bucket_dir, "vdb_chunks.json")
        if os.path.exists(chunks_file):
            try:
                with open(chunks_file, 'r') as f:
                    data = json.load(f)
                    if 'data' in data:
                        stats["documents"] = len(data['data'])
            except:
                pass
        
        # Fallback to old format if new files don't exist
        if stats["entities"] == 0 and stats["relationships"] == 0:
            graph_file = os.path.join(bucket_dir, "graph_chunk_entity_relation.json")
            if os.path.exists(graph_file):
                try:
                    with open(graph_file, 'r') as f:
                        graph_data = json.load(f)
                        stats["entities"] = len(graph_data.get("entities", {}))
                        stats["relationships"] = len(graph_data.get("relationships", {}))
                except:
                    pass
        
        # Add performance and usage metrics
        stats.update(self.get_bucket_performance_stats(bucket_name))
        
        return stats
    
    def visualize_knowledge_graph(self, bucket_name: str, max_nodes: int = 100, auto_open: bool = True) -> Optional[str]:
        """Generate an interactive HTML visualization of the knowledge graph"""
        try:
            # Use our enhanced interactive graph visualizer
            html_file = create_interactive_graph(bucket_name, self.base_dir, max_nodes)
            
            if html_file:
                print(f"✅ Interactive graph saved to: {html_file}")
                
                if auto_open:
                    try:
                        # Auto-launch in default browser
                        webbrowser.open(f"file://{os.path.abspath(html_file)}")
                        print(f"🚀 Opening graph in your default browser...")
                    except Exception as e:
                        print(f"⚠️ Could not auto-open browser: {e}")
                        print(f"🌐 Manually open: {html_file}")
                else:
                    print(f"🌐 Open in browser to explore interactively!")
                
                return html_file
            else:
                # Fallback to creating a basic static graph if no data
                print(f"❌ No graph data found for bucket '{bucket_name}'")
                print(f"   Make sure the bucket has documents and a knowledge graph has been built.")
                return None
                
        except Exception as e:
            print(f"❌ Error creating interactive graph: {e}")
            print(f"   Bucket: {bucket_name}")
            return None
    
    def compare_multiple_graphs(self, bucket_names: List[str], max_nodes_each: int = 30, auto_open: bool = True) -> Optional[str]:
        """Create a multi-graph comparison explorer for multiple buckets"""
        try:
            # Filter out non-existent buckets
            valid_buckets = []
            for bucket_name in bucket_names:
                if bucket_name in self.buckets or os.path.exists(os.path.join(self.base_dir, bucket_name)):
                    valid_buckets.append(bucket_name)
                else:
                    print(f"⚠️ Bucket '{bucket_name}' not found, skipping...")
            
            if len(valid_buckets) < 2:
                print("❌ Need at least 2 valid buckets for comparison")
                return None
            
            print(f"🔍 Creating multi-graph explorer for: {', '.join(valid_buckets)}")
            
            # Use our multi-graph visualizer
            html_file = create_multi_graph_explorer(valid_buckets, self.base_dir, max_nodes_each)
            
            if html_file:
                print(f"✅ Multi-graph explorer saved to: {html_file}")
                
                if auto_open:
                    try:
                        # Auto-launch in default browser
                        webbrowser.open(f"file://{os.path.abspath(html_file)}")
                        print(f"🚀 Opening multi-graph explorer in your browser...")
                    except Exception as e:
                        print(f"⚠️ Could not auto-open browser: {e}")
                        print(f"🌐 Manually open: {html_file}")
                else:
                    print(f"🌐 Open in browser to explore multiple graphs!")
                
                return html_file
            else:
                print("❌ Failed to create multi-graph explorer")
                return None
                
        except Exception as e:
            print(f"❌ Error creating multi-graph explorer: {e}")
            return None
    
    def extract_entities_from_text(self, text: str, bucket_name: str = None) -> List[Dict]:
        """Extract entities from text using LightRAG's entity extraction"""
        # This would use LightRAG's internal entity extraction
        # For now, returning a simplified version
        entities = []
        
        # Simple entity extraction (would be replaced with LightRAG's actual extraction)
        import re
        
        # Extract capitalized words as potential entities
        words = re.findall(r'\b[A-Z][a-z]+\b', text)
        for word in set(words):
            entities.append({
                "text": word,
                "type": "PERSON" if word in text else "ENTITY",
                "confidence": 0.8
            })
        
        return entities
    
    def save_bucket_config(self):
        """Save bucket configuration to disk"""
        config = {
            "buckets": list(self.bucket_metadata.keys()),
            "metadata": self.bucket_metadata,
            "active": list(self.active_buckets)
        }
        
        config_file = os.path.join(self.base_dir, "bucket_config.json")
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_bucket_config(self):
        """Load bucket configuration from disk"""
        config_file = os.path.join(self.base_dir, "bucket_config.json")
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            self.bucket_metadata = config.get("metadata", {})
            self.active_buckets = set(config.get("active", []))
            
            # Load active buckets
            for bucket_name in self.active_buckets:
                self.load_bucket(bucket_name)
            
            # Performance stats are loaded in __init__
    
    def get_bucket_list(self) -> List[Dict]:
        """Get list of all buckets with their status"""
        bucket_list = []
        
        for name, metadata in self.bucket_metadata.items():
            stats = self.get_knowledge_graph_stats(name)
            bucket_list.append({
                "name": name,
                "active": name in self.active_buckets,
                "description": metadata.get("description", ""),
                "documents": stats["documents"],
                "entities": stats["entities"],
                "relationships": stats["relationships"],
                "created": metadata.get("created_at", ""),
                "updated": metadata.get("last_updated", "")
            })
        
        return bucket_list
    
    def compare_bucket_responses(self, query: str, buckets: List[str] = None) -> Dict:
        """Compare responses from multiple buckets side by side"""
        if not buckets:
            buckets = list(self.active_buckets)
        
        comparison = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "responses": {}
        }
        
        for bucket in buckets:
            result = self.query_bucket(bucket, query)
            comparison["responses"][bucket] = result
        
        return comparison
    
    def initialize_statistics_tracking(self):
        """Initialize comprehensive statistics tracking"""
        stats_dir = os.path.join(self.base_dir, "_statistics")
        os.makedirs(stats_dir, exist_ok=True)
        
        # Initialize performance tracking file
        self.perf_file = os.path.join(stats_dir, "performance_metrics.json")
        if not os.path.exists(self.perf_file):
            with open(self.perf_file, 'w') as f:
                json.dump({
                    "session_start": datetime.now().isoformat(),
                    "query_history": [],
                    "processing_times": {},
                    "bucket_usage": {},
                    "system_metrics": []
                }, f, indent=2)
    
    def track_query_performance(self, bucket_name: str, query: str, mode: str, start_time: float, end_time: float, result_length: int):
        """Track query performance metrics"""
        duration = end_time - start_time
        
        query_record = {
            "timestamp": datetime.now().isoformat(),
            "bucket": bucket_name,
            "query": query[:100] + "..." if len(query) > 100 else query,
            "mode": mode,
            "duration_seconds": duration,
            "result_length": result_length,
            "success": True
        }
        
        # Store in memory
        self.query_history.append(query_record)
        
        # Update bucket usage stats
        if bucket_name not in self.performance_stats:
            self.performance_stats[bucket_name] = {
                "total_queries": 0,
                "total_time": 0,
                "avg_response_time": 0,
                "fastest_query": float('inf'),
                "slowest_query": 0,
                "mode_usage": {"naive": 0, "local": 0, "global": 0, "hybrid": 0}
            }
        
        stats = self.performance_stats[bucket_name]
        stats["total_queries"] += 1
        stats["total_time"] += duration
        stats["avg_response_time"] = stats["total_time"] / stats["total_queries"]
        stats["fastest_query"] = min(stats["fastest_query"], duration)
        stats["slowest_query"] = max(stats["slowest_query"], duration)
        stats["mode_usage"][mode] += 1
        
        # Save to disk
        self.save_performance_stats()
    
    def track_processing_performance(self, bucket_name: str, operation: str, start_time: float, end_time: float, success: bool, metadata: Dict = None):
        """Track document processing performance"""
        duration = end_time - start_time
        
        processing_record = {
            "timestamp": datetime.now().isoformat(),
            "bucket": bucket_name,
            "operation": operation,
            "duration_seconds": duration,
            "success": success,
            "metadata": metadata or {}
        }
        
        # Update processing stats
        if bucket_name not in self.performance_stats:
            self.performance_stats[bucket_name] = {}
        
        if "processing" not in self.performance_stats[bucket_name]:
            self.performance_stats[bucket_name]["processing"] = {
                "total_operations": 0,
                "successful_operations": 0,
                "total_time": 0,
                "avg_processing_time": 0
            }
        
        proc_stats = self.performance_stats[bucket_name]["processing"]
        proc_stats["total_operations"] += 1
        if success:
            proc_stats["successful_operations"] += 1
        proc_stats["total_time"] += duration
        proc_stats["avg_processing_time"] = proc_stats["total_time"] / proc_stats["total_operations"]
        
        self.save_performance_stats()
    
    def get_bucket_performance_stats(self, bucket_name: str) -> Dict:
        """Get detailed performance statistics for a bucket"""
        bucket_dir = os.path.join(self.base_dir, bucket_name)
        
        perf_stats = {
            "performance": {
                "total_queries": 0,
                "avg_query_time": 0,
                "fastest_query": 0,
                "slowest_query": 0,
                "success_rate": 100.0,
                "processing_time": 0,
                "storage_size_mb": 0,
                "last_accessed": None
            }
        }
        
        # Get from in-memory stats
        if bucket_name in self.performance_stats:
            bucket_perf = self.performance_stats[bucket_name]
            perf_stats["performance"].update({
                "total_queries": bucket_perf.get("total_queries", 0),
                "avg_query_time": round(bucket_perf.get("avg_response_time", 0), 3),
                "fastest_query": round(bucket_perf.get("fastest_query", 0), 3) if bucket_perf.get("fastest_query") != float('inf') else 0,
                "slowest_query": round(bucket_perf.get("slowest_query", 0), 3)
            })
        
        # Calculate storage size
        if os.path.exists(bucket_dir):
            total_size = 0
            for root, dirs, files in os.walk(bucket_dir):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                    except:
                        pass
            perf_stats["performance"]["storage_size_mb"] = round(total_size / (1024 * 1024), 2)
            
            # Get last accessed time
            try:
                perf_stats["performance"]["last_accessed"] = datetime.fromtimestamp(
                    os.path.getmtime(bucket_dir)
                ).isoformat()
            except:
                pass
        
        return perf_stats
    
    def get_system_performance_metrics(self) -> Dict:
        """Get current system performance metrics"""
        try:
            # CPU and Memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_usage_percent": cpu_percent,
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_percent": round((disk.used / disk.total) * 100, 1)
                },
                "active_buckets": len(self.active_buckets),
                "total_buckets": len(self.bucket_metadata)
            }
            
            return metrics
        except Exception as e:
            return {"error": f"Could not gather system metrics: {e}"}
    
    def get_comprehensive_analytics(self) -> Dict:
        """Get comprehensive analytics across all buckets"""
        analytics = {
            "overview": {
                "total_buckets": len(self.bucket_metadata),
                "active_buckets": len(self.active_buckets),
                "total_entities": 0,
                "total_relationships": 0,
                "total_documents": 0,
                "total_queries": len(self.query_history),
                "analysis_date": datetime.now().isoformat()
            },
            "bucket_stats": {},
            "performance_summary": {
                "avg_query_time": 0,
                "total_processing_time": 0,
                "success_rate": 100.0,
                "most_used_bucket": None,
                "most_used_query_mode": None
            },
            "recent_activity": {
                "last_24h_queries": 0,
                "last_7d_queries": 0,
                "recent_query_trends": []
            },
            "system_health": self.get_system_performance_metrics()
        }
        
        # Aggregate bucket statistics
        total_query_time = 0
        total_queries = 0
        bucket_query_counts = {}
        mode_usage = {"naive": 0, "local": 0, "global": 0, "hybrid": 0}
        
        for bucket_name in self.bucket_metadata:
            bucket_stats = self.get_knowledge_graph_stats(bucket_name)
            analytics["bucket_stats"][bucket_name] = bucket_stats
            
            # Aggregate totals
            analytics["overview"]["total_entities"] += bucket_stats.get("entities", 0)
            analytics["overview"]["total_relationships"] += bucket_stats.get("relationships", 0)
            analytics["overview"]["total_documents"] += bucket_stats.get("documents", 0)
            
            # Performance aggregation
            if bucket_name in self.performance_stats:
                perf = self.performance_stats[bucket_name]
                bucket_queries = perf.get("total_queries", 0)
                bucket_query_counts[bucket_name] = bucket_queries
                total_queries += bucket_queries
                total_query_time += perf.get("total_time", 0)
                
                # Mode usage aggregation
                for mode, count in perf.get("mode_usage", {}).items():
                    mode_usage[mode] += count
        
        # Calculate performance summary
        if total_queries > 0:
            analytics["performance_summary"]["avg_query_time"] = round(total_query_time / total_queries, 3)
            analytics["performance_summary"]["most_used_bucket"] = max(bucket_query_counts, key=bucket_query_counts.get) if bucket_query_counts else None
            analytics["performance_summary"]["most_used_query_mode"] = max(mode_usage, key=mode_usage.get) if any(mode_usage.values()) else None
        
        # Recent activity analysis
        now = datetime.now()
        last_24h = now - timedelta(days=1)
        last_7d = now - timedelta(days=7)
        
        for query in self.query_history:
            query_time = datetime.fromisoformat(query["timestamp"].replace('Z', '+00:00').replace('+00:00', ''))
            if query_time >= last_24h:
                analytics["recent_activity"]["last_24h_queries"] += 1
            if query_time >= last_7d:
                analytics["recent_activity"]["last_7d_queries"] += 1
        
        return analytics
    
    def get_bucket_usage_trends(self, bucket_name: str, days: int = 30) -> Dict:
        """Get usage trends for a specific bucket over time"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        trends = {
            "bucket": bucket_name,
            "period_days": days,
            "daily_queries": [],
            "query_modes": {"naive": 0, "local": 0, "global": 0, "hybrid": 0},
            "avg_response_times": [],
            "total_activity": 0
        }
        
        # Group queries by day
        daily_counts = {}
        daily_response_times = {}
        
        for query in self.query_history:
            if query["bucket"] == bucket_name:
                query_date = datetime.fromisoformat(query["timestamp"].replace('Z', '+00:00').replace('+00:00', ''))
                if query_date >= cutoff_date:
                    day_key = query_date.strftime('%Y-%m-%d')
                    
                    if day_key not in daily_counts:
                        daily_counts[day_key] = 0
                        daily_response_times[day_key] = []
                    
                    daily_counts[day_key] += 1
                    daily_response_times[day_key].append(query["duration_seconds"])
                    trends["query_modes"][query["mode"]] += 1
                    trends["total_activity"] += 1
        
        # Convert to lists for frontend consumption
        for day, count in sorted(daily_counts.items()):
            trends["daily_queries"].append({
                "date": day,
                "queries": count,
                "avg_response_time": sum(daily_response_times[day]) / len(daily_response_times[day])
            })
        
        return trends
    
    def save_performance_stats(self):
        """Save performance statistics to disk"""
        try:
            stats_data = {
                "last_updated": datetime.now().isoformat(),
                "performance_stats": self.performance_stats,
                "query_history": self.query_history[-1000:],  # Keep last 1000 queries
                "system_metrics": self.system_metrics
            }
            
            with open(self.perf_file, 'w') as f:
                json.dump(stats_data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save performance stats: {e}")
    
    def load_performance_stats(self):
        """Load performance statistics from disk"""
        try:
            if os.path.exists(self.perf_file):
                with open(self.perf_file, 'r') as f:
                    stats_data = json.load(f)
                
                self.performance_stats = stats_data.get("performance_stats", {})
                self.query_history = stats_data.get("query_history", [])
                self.system_metrics = stats_data.get("system_metrics", {})
        except Exception as e:
            print(f"⚠️ Could not load performance stats: {e}")
    
    def export_analytics_report(self, format_type: str = "json") -> str:
        """Export comprehensive analytics report"""
        analytics = self.get_comprehensive_analytics()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "json":
            filename = f"lightrag_analytics_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(analytics, f, indent=2)
        
        elif format_type == "csv":
            import csv
            filename = f"lightrag_analytics_{timestamp}.csv"
            
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write overview
                writer.writerow(["Metric", "Value"])
                for key, value in analytics["overview"].items():
                    writer.writerow([key, value])
                
                writer.writerow([])  # Empty row
                writer.writerow(["Bucket", "Entities", "Relationships", "Documents"])
                
                # Write bucket stats
                for bucket, stats in analytics["bucket_stats"].items():
                    writer.writerow([
                        bucket,
                        stats.get("entities", 0),
                        stats.get("relationships", 0),
                        stats.get("documents", 0)
                    ])
        
        return filename
    
    def batch_process_files(self, bucket_name: str, file_paths: List[str] = None, 
                           directory_path: str = None, file_extensions: List[str] = None) -> Dict:
        """Batch process files to build knowledge graph and vector database"""
        if bucket_name not in self.bucket_metadata:
            print(f"❌ Bucket not found: {bucket_name}")
            return {"error": "Bucket not found"}
        
        # Determine files to process
        files_to_process = []
        
        if directory_path:
            # Process all files in directory
            if not os.path.exists(directory_path):
                print(f"❌ Directory not found: {directory_path}")
                return {"error": "Directory not found"}
            
            extensions = file_extensions or ['.txt', '.md', '.pdf', '.docx']
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in extensions):
                        files_to_process.append(os.path.join(root, file))
        
        elif file_paths:
            # Process specific files
            for path in file_paths:
                if os.path.exists(path):
                    files_to_process.append(path)
                else:
                    print(f"⚠️ File not found, skipping: {path}")
        
        else:
            # Check for processing queue
            bucket_dir = os.path.join(self.base_dir, bucket_name)
            queue_file = os.path.join(bucket_dir, "processing_queue.json")
            if os.path.exists(queue_file):
                with open(queue_file, 'r') as f:
                    queue_data = json.load(f)
                
                # Process queued files
                for item in queue_data:
                    if item.get("status") == "pending_processing":
                        # Look for the actual file
                        potential_files = []
                        for root, dirs, files in os.walk(bucket_dir):
                            for file in files:
                                if file == item["filename"]:
                                    potential_files.append(os.path.join(root, file))
                        
                        if potential_files:
                            files_to_process.extend(potential_files)
                        else:
                            print(f"⚠️ Queued file not found: {item['filename']}")
        
        if not files_to_process:
            print(f"❌ No files found to process")
            return {"error": "No files to process"}
        
        # Load the bucket
        if not self.load_bucket(bucket_name):
            print(f"❌ Failed to load bucket: {bucket_name}")
            return {"error": "Failed to load bucket"}
        
        print(f"🚀 Starting batch processing for bucket '{bucket_name}'")
        print(f"📁 Processing {len(files_to_process)} files...")
        
        processed = 0
        failed = 0
        results = []
        
        for file_path in files_to_process:
            try:
                print(f"📄 Processing: {os.path.basename(file_path)}")
                
                # Read file content
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Add to LightRAG bucket
                success = self.add_document_to_bucket(
                    bucket_name, 
                    content, 
                    metadata={"source_file": file_path, "filename": os.path.basename(file_path)}
                )
                
                if success:
                    processed += 1
                    results.append({
                        "file": file_path,
                        "status": "success",
                        "size": len(content)
                    })
                    print(f"  ✅ Successfully processed")
                else:
                    failed += 1
                    results.append({
                        "file": file_path,
                        "status": "failed",
                        "error": "LightRAG processing failed"
                    })
                    print(f"  ❌ Processing failed")
                
            except Exception as e:
                failed += 1
                results.append({
                    "file": file_path,
                    "status": "error",
                    "error": str(e)
                })
                print(f"  ❌ Error: {e}")
        
        # Update queue status if processing from queue
        bucket_dir = os.path.join(self.base_dir, bucket_name)
        queue_file = os.path.join(bucket_dir, "processing_queue.json")
        if os.path.exists(queue_file):
            try:
                with open(queue_file, 'r') as f:
                    queue_data = json.load(f)
                
                # Mark processed files as complete
                for item in queue_data:
                    if item.get("status") == "pending_processing":
                        item["status"] = "processed"
                        item["processed_at"] = datetime.now().isoformat()
                
                with open(queue_file, 'w') as f:
                    json.dump(queue_data, f, indent=2)
            except Exception as e:
                print(f"⚠️ Could not update processing queue: {e}")
        
        # Generate final statistics
        stats = self.get_knowledge_graph_stats(bucket_name)
        
        summary = {
            "bucket": bucket_name,
            "total_files": len(files_to_process),
            "processed": processed,
            "failed": failed,
            "results": results,
            "final_stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"\n📊 BATCH PROCESSING COMPLETE")
        print(f"📁 Bucket: {bucket_name}")
        print(f"✅ Processed: {processed}/{len(files_to_process)} files")
        print(f"❌ Failed: {failed}")
        print(f"🔗 Entities: {stats['entities']}")
        print(f"🔗 Relationships: {stats['relationships']}")
        print(f"📚 Total Documents: {stats['documents']}")
        
        return summary

    def export_bucket_data(self, bucket_name: str) -> Dict:
        """Export all data from a bucket"""
        bucket_dir = os.path.join(self.base_dir, bucket_name)
        
        export_data = {
            "bucket_name": bucket_name,
            "metadata": self.bucket_metadata.get(bucket_name, {}),
            "documents": [],
            "graph": {},
            "export_date": datetime.now().isoformat()
        }
        
        # Export documents
        doc_file = os.path.join(bucket_dir, "documents.json")
        if os.path.exists(doc_file):
            with open(doc_file, 'r') as f:
                export_data["documents"] = json.load(f)
        
        # Export graph
        graph_file = os.path.join(bucket_dir, "graph_chunk_entity_relation.json")
        if os.path.exists(graph_file):
            with open(graph_file, 'r') as f:
                export_data["graph"] = json.load(f)
        
        return export_data


class BucketInterface:
    """Interactive interface for bucket management"""
    
    def __init__(self, manager: LightRAGManager):
        self.manager = manager
    
    def display_bucket_status(self):
        """Display current bucket status"""
        buckets = self.manager.get_bucket_list()
        
        print("\n" + "="*70)
        print("LIGHTRAG BUCKET STATUS")
        print("="*70)
        print(f"{'Bucket':<15} {'Active':<8} {'Docs':<6} {'Entities':<10} {'Relations':<10}")
        print("-"*70)
        
        for bucket in buckets:
            active = "✓" if bucket["active"] else "✗"
            print(f"{bucket['name']:<15} {active:<8} {bucket['documents']:<6} "
                  f"{bucket['entities']:<10} {bucket['relationships']:<10}")
        
        print("-"*70)
        print(f"Total buckets: {len(buckets)} | Active: {len([b for b in buckets if b['active']])}")
    
    def interactive_query(self):
        """Interactive query interface"""
        print("\n" + "="*60)
        print("INTERACTIVE QUERY MODE")
        print("="*60)
        
        # Show active buckets
        active = list(self.manager.active_buckets)
        if not active:
            print("❌ No active buckets. Please activate at least one bucket.")
            return
        
        print(f"Active buckets: {', '.join(active)}")
        
        while True:
            query = input("\n📝 Enter query (or 'exit'): ").strip()
            if query.lower() == 'exit':
                break
            
            print("\n🔍 Querying active buckets...")
            results = self.manager.query_active_buckets(query)
            
            for result in results:
                print(f"\n📚 {result['bucket']}:")
                print("-"*40)
                if "error" in result:
                    print(f"❌ Error: {result['error']}")
                else:
                    response = result.get("response", "No response")
                    print(response[:500] + "..." if len(response) > 500 else response)
    
    def manage_buckets_menu(self):
        """Interactive bucket management menu"""
        while True:
            print("\n" + "="*60)
            print("BUCKET MANAGEMENT")
            print("="*60)
            print("1. View bucket status")
            print("2. Create new bucket")
            print("3. Toggle bucket on/off")
            print("4. Add document to bucket")
            print("5. 🚀 Batch process files (Build Knowledge Graph)")
            print("6. Visualize knowledge graph")
            print("7. Compare multiple graphs")
            print("8. Export bucket data")
            print("9. 🔑 API Key Management")
            print("10. 🎯 Open Modern Bucket Manager (GUI)")
            print("0. Back")
            
            choice = input("\nChoice: ").strip()
            
            if choice == "1":
                self.display_bucket_status()
            
            elif choice == "2":
                name = input("Bucket name: ").strip()
                desc = input("Description: ").strip()
                self.manager.create_bucket(name, desc)
            
            elif choice == "3":
                buckets = self.manager.get_bucket_list()
                for i, b in enumerate(buckets, 1):
                    status = "ON" if b["active"] else "OFF"
                    print(f"{i}. {b['name']} [{status}]")
                
                idx = int(input("Select bucket: ")) - 1
                if 0 <= idx < len(buckets):
                    bucket = buckets[idx]
                    new_state = not bucket["active"]
                    self.manager.toggle_bucket(bucket["name"], new_state)
            
            elif choice == "4":
                buckets = list(self.manager.bucket_metadata.keys())
                for i, b in enumerate(buckets, 1):
                    print(f"{i}. {b}")
                
                idx = int(input("Select bucket: ")) - 1
                if 0 <= idx < len(buckets):
                    bucket = buckets[idx]
                    doc = input("Enter document text: ").strip()
                    self.manager.add_document_to_bucket(bucket, doc)
            
            elif choice == "5":
                # Batch processing
                buckets = list(self.manager.bucket_metadata.keys())
                if not buckets:
                    print("❌ No buckets found. Create a bucket first.")
                    continue
                    
                print("\nSelect bucket for batch processing:")
                for i, b in enumerate(buckets, 1):
                    print(f"{i}. {b}")
                
                try:
                    idx = int(input("Select bucket: ")) - 1
                    if not (0 <= idx < len(buckets)):
                        print("❌ Invalid bucket selection")
                        continue
                    
                    bucket = buckets[idx]
                    
                    print("\nBatch processing options:")
                    print("1. Process files from directory")
                    print("2. Process specific files")
                    print("3. Process queued files (from web uploads)")
                    
                    batch_choice = input("Choice: ").strip()
                    
                    if batch_choice == "1":
                        # Directory processing
                        dir_path = input("Enter directory path: ").strip()
                        if dir_path and os.path.exists(dir_path):
                            print("File extensions (comma-separated, e.g., .txt,.md,.pdf):")
                            ext_input = input("Extensions (or Enter for default): ").strip()
                            extensions = [e.strip() for e in ext_input.split(',')] if ext_input else None
                            
                            result = self.manager.batch_process_files(
                                bucket, 
                                directory_path=dir_path, 
                                file_extensions=extensions
                            )
                            
                        else:
                            print("❌ Invalid directory path")
                    
                    elif batch_choice == "2":
                        # Specific files
                        print("Enter file paths (one per line, empty line to finish):")
                        file_paths = []
                        while True:
                            path = input("File path: ").strip()
                            if not path:
                                break
                            file_paths.append(path)
                        
                        if file_paths:
                            result = self.manager.batch_process_files(bucket, file_paths=file_paths)
                        else:
                            print("❌ No files specified")
                    
                    elif batch_choice == "3":
                        # Process queue
                        print(f"🔄 Processing queued files for bucket '{bucket}'...")
                        result = self.manager.batch_process_files(bucket)
                        
                    else:
                        print("❌ Invalid choice")
                        
                except ValueError:
                    print("❌ Invalid input")
            
            elif choice == "6":
                buckets = list(self.manager.bucket_metadata.keys())
                for i, b in enumerate(buckets, 1):
                    print(f"{i}. {b}")
                
                idx = int(input("Select bucket: ")) - 1
                if 0 <= idx < len(buckets):
                    viz_file = self.manager.visualize_knowledge_graph(buckets[idx])
                    if viz_file:
                        print(f"✅ Graph saved to: {viz_file}")
                    else:
                        print("❌ No graph data available")
            
            elif choice == "7":
                # Multi-graph comparison
                buckets = list(self.manager.bucket_metadata.keys())
                print("\nSelect buckets for comparison:")
                for i, b in enumerate(buckets, 1):
                    print(f"{i}. {b}")
                
                print("\nEnter bucket numbers separated by commas (e.g., 1,2,3):")
                selection = input("Buckets: ").strip()
                
                try:
                    indices = [int(x.strip()) - 1 for x in selection.split(',')]
                    selected_buckets = []
                    
                    for idx in indices:
                        if 0 <= idx < len(buckets):
                            selected_buckets.append(buckets[idx])
                        else:
                            print(f"⚠️ Invalid bucket number: {idx + 1}")
                    
                    if len(selected_buckets) >= 2:
                        print(f"\n🔍 Creating multi-graph comparison for: {', '.join(selected_buckets)}")
                        viz_file = self.manager.compare_multiple_graphs(selected_buckets)
                        if viz_file:
                            print(f"✅ Multi-graph explorer created and opened in browser!")
                        else:
                            print("❌ Failed to create multi-graph explorer")
                    else:
                        print("❌ Please select at least 2 buckets for comparison")
                        
                except ValueError:
                    print("❌ Invalid input format. Use comma-separated numbers (e.g., 1,2,3)")
                    
            elif choice == "8":
                buckets = list(self.manager.bucket_metadata.keys())
                for i, b in enumerate(buckets, 1):
                    print(f"{i}. {b}")
                
                idx = int(input("Select bucket: ")) - 1
                if 0 <= idx < len(buckets):
                    data = self.manager.export_bucket_data(buckets[idx])
                    filename = f"{buckets[idx]}_export.json"
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"✅ Exported to: {filename}")
            
            elif choice == "9":
                # API Key Management
                try:
                    from util_apikey import APIKeyManager
                    api_manager = APIKeyManager()
                    api_manager.interactive_setup()
                except ImportError:
                    print("❌ API Key management not available")
            
            elif choice == "10":
                self.launch_modern_bucket_manager()
            
            elif choice == "0":
                break
    
    def launch_modern_bucket_manager(self):
        """Launch the modern web-based bucket manager"""
        import subprocess
        import threading
        import time
        import webbrowser
        
        print(f"🚀 Starting Modern Bucket Manager...")
        print(f"✨ Features: Modern UI, drag & drop, real-time stats")
        print(f"📊 Will open in your browser at http://localhost:8002")
        
        # Start the server in a separate process
        current_dir = os.path.dirname(os.path.abspath(__file__))
        server_file = os.path.join(current_dir, "bucket_manager_server.py")
        
        if os.path.exists(server_file):
            print(f"🔄 Starting server...")
            
            # Start server in background
            try:
                server_process = subprocess.Popen(
                    [sys.executable, server_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=current_dir
                )
                
                # Give it a moment to start
                time.sleep(2)
                
                # Open browser
                webbrowser.open('http://localhost:8002')
                
                print(f"✅ Bucket Manager launched successfully!")
                print(f"🌐 Access it at: http://localhost:8002")
                print(f"🛑 Press Enter to stop the server...")
                
                # Wait for user to press Enter
                input()
                
                # Stop the server
                server_process.terminate()
                server_process.wait()
                print(f"🛑 Bucket Manager server stopped")
                
            except Exception as e:
                print(f"❌ Error starting server: {e}")
        else:
            print(f"❌ Bucket manager server not found at: {server_file}")
            print(f"💡 Make sure bucket_manager_server.py is in the same directory")


def demo_lightrag_manager():
    """Demonstrate LightRAG manager capabilities"""
    manager = LightRAGManager()
    interface = BucketInterface(manager)
    
    print("\n" + "="*60)
    print("LIGHTRAG MANAGER DEMO")
    print("="*60)
    
    # Create sample buckets if they don't exist
    sample_buckets = [
        ("scripts", "Romantic comedy screenplays"),
        ("books", "Screenwriting theory and guides"),
        ("plays", "Theatrical works and drama")
    ]
    
    for name, desc in sample_buckets:
        manager.create_bucket(name, desc)
    
    # Display status
    interface.display_bucket_status()
    
    # Add sample document
    print("\n📄 Adding sample document to 'scripts' bucket...")
    sample_doc = """
    FADE IN:
    
    INT. COFFEE SHOP - DAY
    
    Sarah enters the bustling coffee shop, scanning for an empty table.
    She spots Jake at a corner table, typing furiously on his laptop.
    Their eyes meet. A moment of recognition - they know each other.
    """
    
    manager.add_document_to_bucket("scripts", sample_doc)
    
    # Query demonstration
    print("\n🔍 Query demonstration...")
    results = manager.query_active_buckets("Tell me about coffee shop scenes")
    
    for result in results:
        if "error" not in result:
            print(f"\n📚 {result['bucket']}: {result['response'][:200]}...")
    
    print("\n✨ LightRAG Manager ready!")


if __name__ == "__main__":
    demo_lightrag_manager()