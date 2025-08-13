#!/usr/bin/env python3
"""
Fix Miranda bucket integration in the new transparent system
"""

import os
import json
from lizzy_lightrag_manager import LightRAGManager

def integrate_miranda_buckets():
    """Integrate Miranda buckets into the new system"""
    
    print("🔧 INTEGRATING MIRANDA BUCKETS")
    print("="*50)
    
    # Initialize the LightRAG manager
    manager = LightRAGManager()
    
    # Path to Miranda buckets
    miranda_base = "/Users/elle/Desktop/Elizabeth_PI/lightrag_buckets"
    
    miranda_buckets = {
        "miranda_scripts": {
            "path": os.path.join(miranda_base, "miranda_scripts"),
            "description": "Romantic comedy screenplay knowledge from Miranda legacy system"
        },
        "miranda_books": {
            "path": os.path.join(miranda_base, "miranda_books"), 
            "description": "Writing craft knowledge including 'On Writing' and techniques"
        },
        "miranda_plays": {
            "path": os.path.join(miranda_base, "miranda_plays"),
            "description": "Theatrical and dramatic structure knowledge"
        }
    }
    
    # Add each Miranda bucket to the manager
    for bucket_name, info in miranda_buckets.items():
        bucket_path = info["path"]
        description = info["description"]
        
        print(f"\n📚 Integrating {bucket_name}...")
        
        # Check if bucket has data
        key_files = [
            "kv_store_full_docs.json",
            "vdb_entities.json", 
            "vdb_relationships.json"
        ]
        
        missing = [f for f in key_files if not os.path.exists(os.path.join(bucket_path, f))]
        if missing:
            print(f"❌ Missing files: {missing}")
            continue
        
        # Get stats
        stats = manager.get_knowledge_graph_stats(bucket_name)
        
        # Create/update bucket metadata
        manager.bucket_metadata[bucket_name] = {
            "name": bucket_name,
            "description": description,
            "created_at": "2025-01-09T00:00:00",  # From file timestamps
            "document_count": stats.get("documents", 0),
            "entity_count": stats.get("entities", 0), 
            "relationship_count": stats.get("relationships", 0),
            "last_updated": "2025-08-13T14:27:31",  # From migration log
            "source": "LEGACY_miranda_2",
            "working_dir": bucket_path
        }
        
        # Activate bucket by default
        manager.active_buckets.add(bucket_name)
        
        print(f"✅ {bucket_name} integrated:")
        print(f"   📄 Documents: {stats.get('documents', 0)}")
        print(f"   🔗 Entities: {stats.get('entities', 0)}")
        print(f"   🌐 Relations: {stats.get('relationships', 0)}")
    
    # Save configuration
    manager.save_bucket_config()
    
    print(f"\n{'='*50}")
    print("✅ Miranda buckets integrated successfully!")
    print(f"Active buckets: {list(manager.active_buckets)}")
    
    # Test bucket listing
    bucket_list = manager.get_bucket_list()
    print(f"\nBucket Status:")
    for bucket in bucket_list:
        status = "✓" if bucket["active"] else "✗"
        print(f"  {status} {bucket['name']}: {bucket['entities']} entities, {bucket['relationships']} relations")

if __name__ == "__main__":
    integrate_miranda_buckets()