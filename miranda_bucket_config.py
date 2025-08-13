#!/usr/bin/env python3
"""
Simple Miranda bucket configuration script
"""

import os
import json
from datetime import datetime

def configure_miranda_buckets():
    """Configure Miranda buckets for the new system"""
    
    print("🔧 CONFIGURING MIRANDA BUCKETS")
    print("="*50)
    
    # Base directories
    lightrag_dir = "/Users/elle/Desktop/Elizabeth_PI/lightrag_working_dir"
    miranda_dir = "/Users/elle/Desktop/Elizabeth_PI/lightrag_buckets"
    
    # Ensure base directory exists
    os.makedirs(lightrag_dir, exist_ok=True)
    
    # Miranda bucket configuration
    miranda_buckets = {
        "miranda_scripts": {
            "original_path": os.path.join(miranda_dir, "miranda_scripts"),
            "description": "Romantic comedy screenplay knowledge from Miranda legacy system",
            "active": True
        },
        "miranda_books": {
            "original_path": os.path.join(miranda_dir, "miranda_books"), 
            "description": "Writing craft knowledge including 'On Writing' and techniques",
            "active": True
        },
        "miranda_plays": {
            "original_path": os.path.join(miranda_dir, "miranda_plays"),
            "description": "Theatrical and dramatic structure knowledge",
            "active": True
        }
    }
    
    # Check bucket data
    for bucket_name, config in miranda_buckets.items():
        bucket_path = config["original_path"]
        print(f"\n📚 Checking {bucket_name}...")
        
        if not os.path.exists(bucket_path):
            print(f"❌ Directory not found: {bucket_path}")
            continue
        
        # Check for key files
        key_files = [
            "kv_store_full_docs.json",
            "vdb_entities.json", 
            "vdb_relationships.json",
            "vdb_chunks.json"
        ]
        
        missing = [f for f in key_files if not os.path.exists(os.path.join(bucket_path, f))]
        if missing:
            print(f"❌ Missing files: {missing}")
            continue
        
        # Get file sizes to estimate data
        stats = {}
        for file in key_files:
            file_path = os.path.join(bucket_path, file)
            if os.path.exists(file_path):
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                stats[file] = f"{size_mb:.1f}MB"
        
        print(f"✅ {bucket_name} has complete data:")
        for file, size in stats.items():
            print(f"   📄 {file}: {size}")
    
    # Create bucket configuration for the new system
    bucket_config = {
        "buckets": list(miranda_buckets.keys()),
        "metadata": {},
        "active": []
    }
    
    for bucket_name, config in miranda_buckets.items():
        bucket_config["metadata"][bucket_name] = {
            "name": bucket_name,
            "description": config["description"],
            "created_at": "2025-01-09T00:00:00",
            "document_count": 0,  # Will be populated when loaded
            "entity_count": 0,
            "relationship_count": 0,
            "last_updated": "2025-08-13T14:27:31",
            "source": "LEGACY_miranda_2",
            "working_dir": config["original_path"]
        }
        
        if config["active"]:
            bucket_config["active"].append(bucket_name)
    
    # Save configuration
    config_file = os.path.join(lightrag_dir, "bucket_config.json")
    with open(config_file, 'w') as f:
        json.dump(bucket_config, f, indent=2)
    
    print(f"\n✅ Bucket configuration saved to: {config_file}")
    print(f"Active buckets: {bucket_config['active']}")
    
    # Create symlinks in the main working directory for easy access
    for bucket_name, config in miranda_buckets.items():
        source_path = config["original_path"]
        target_path = os.path.join(lightrag_dir, bucket_name)
        
        if os.path.exists(source_path) and not os.path.exists(target_path):
            try:
                os.symlink(source_path, target_path)
                print(f"🔗 Created symlink: {bucket_name} -> {source_path}")
            except OSError as e:
                print(f"⚠️ Could not create symlink for {bucket_name}: {e}")
    
    print(f"\n{'='*50}")
    print("✅ Miranda bucket configuration complete!")

if __name__ == "__main__":
    configure_miranda_buckets()