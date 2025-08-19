"""
LightRAG Management and Visualization Layer for Lizzy
Handles knowledge graph operations, bucket management, and data queries
"""

import os
import json
import sqlite3
import webbrowser
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
import networkx as nx
import matplotlib.pyplot as plt
from io import StringIO
from graph_visualizer import create_interactive_graph, create_multi_graph_explorer


class LightRAGManager:
    """Manages LightRAG instances and provides visualization/query capabilities"""
    
    def __init__(self, base_dir="lightrag_working_dir"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        self.buckets = {}
        self.bucket_metadata = {}
        self.active_buckets = set()
        self.load_bucket_config()
    
    def create_bucket(self, bucket_name: str, description: str = "", auto_activate: bool = True) -> bool:
        """Create a new LightRAG bucket"""
        if bucket_name in self.buckets:
            print(f"⚠️ Bucket '{bucket_name}' already exists")
            return False
        
        bucket_dir = os.path.join(self.base_dir, bucket_name)
        os.makedirs(bucket_dir, exist_ok=True)
        
        # Initialize LightRAG instance
        self.buckets[bucket_name] = LightRAG(
            working_dir=bucket_dir,
            embedding_func=openai_embed,
            llm_model_func=gpt_4o_mini_complete
        )
        
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
            self.buckets[bucket_name] = LightRAG(
                working_dir=bucket_dir,
                embedding_func=openai_embed,
                llm_model_func=gpt_4o_mini_complete
            )
        
        return True
    
    def add_document_to_bucket(self, bucket_name: str, document: str, metadata: Dict = None) -> bool:
        """Add a document to a specific bucket"""
        if bucket_name not in self.buckets:
            if not self.load_bucket(bucket_name):
                return False
        
        try:
            # Insert document into LightRAG
            self.buckets[bucket_name].insert(document)
            
            # Update metadata
            if bucket_name in self.bucket_metadata:
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
            return True
            
        except Exception as e:
            print(f"❌ Error adding document: {e}")
            return False
    
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
        """Query a specific bucket"""
        if bucket_name not in self.buckets:
            if not self.load_bucket(bucket_name):
                return {"error": f"Bucket not found: {bucket_name}"}
        
        try:
            result = self.buckets[bucket_name].query(
                query,
                param=QueryParam(mode=mode)
            )
            
            return {
                "bucket": bucket_name,
                "query": query,
                "mode": mode,
                "response": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
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
            print("5. Visualize knowledge graph")
            print("6. Compare multiple graphs")
            print("7. Export bucket data")
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
            
            elif choice == "6":
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
                    
            elif choice == "7":
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
            
            elif choice == "0":
                break


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