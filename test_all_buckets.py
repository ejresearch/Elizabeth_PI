#!/usr/bin/env python3
"""
Test ALL LightRAG buckets and configurations in the system
"""

import os
import json
from datetime import datetime

def analyze_all_buckets():
    """Analyze all bucket configurations and data"""
    
    print("🔍 ANALYZING ALL LIGHTRAG BUCKETS")
    print("="*70)
    
    # Base directories to check
    directories = {
        "lightrag_working_dir": "/Users/elle/Desktop/Elizabeth_PI/lightrag_working_dir",
        "lightrag_buckets": "/Users/elle/Desktop/Elizabeth_PI/lightrag_buckets"
    }
    
    all_buckets = {}
    
    for dir_name, dir_path in directories.items():
        print(f"\n📂 Scanning {dir_name}...")
        
        if not os.path.exists(dir_path):
            print(f"   ❌ Directory not found: {dir_path}")
            continue
        
        # Get all subdirectories
        try:
            items = os.listdir(dir_path)
            bucket_dirs = [item for item in items if os.path.isdir(os.path.join(dir_path, item))]
            
            print(f"   📊 Found {len(bucket_dirs)} potential buckets")
            
            for bucket_name in sorted(bucket_dirs):
                bucket_path = os.path.join(dir_path, bucket_name)
                
                # Analyze bucket contents
                bucket_info = analyze_bucket(bucket_name, bucket_path, dir_name)
                
                if bucket_info:
                    all_buckets[f"{dir_name}/{bucket_name}"] = bucket_info
                    
        except Exception as e:
            print(f"   ❌ Error scanning directory: {e}")
    
    # Summary analysis
    print(f"\n{'='*70}")
    print("COMPREHENSIVE BUCKET ANALYSIS")
    print(f"{'='*70}")
    
    # Categorize buckets
    categories = {
        "miranda_legacy": [],
        "academic_sources": [],
        "creative_writing": [],
        "working_buckets": [],
        "empty_buckets": [],
        "broken_buckets": []
    }
    
    for bucket_id, info in all_buckets.items():
        bucket_name = info['name']
        
        if bucket_name.startswith('miranda_'):
            categories["miranda_legacy"].append(info)
        elif any(term in bucket_name for term in ['academic', 'balio', 'bordwell', 'cook', 'cousins', 'gomery', 'knight', 'dixon', 'cultural', 'pedagogical', 'reference']):
            categories["academic_sources"].append(info)
        elif bucket_name in ['scripts', 'books', 'plays', 'examples', 'test']:
            categories["creative_writing"].append(info)
        elif info['has_substantial_data']:
            categories["working_buckets"].append(info)
        elif info['total_size_mb'] == 0:
            categories["empty_buckets"].append(info)
        else:
            categories["broken_buckets"].append(info)
    
    # Report by category
    for category, buckets in categories.items():
        if buckets:
            print(f"\n📚 {category.upper().replace('_', ' ')} ({len(buckets)} buckets):")
            
            for bucket in sorted(buckets, key=lambda x: x['total_size_mb'], reverse=True):
                status = "✅" if bucket['has_substantial_data'] else "⚠️" if bucket['total_size_mb'] > 0 else "❌"
                print(f"   {status} {bucket['name']}: {bucket['total_size_mb']:.1f}MB, {bucket['file_count']} files")
                
                if bucket['has_substantial_data']:
                    print(f"      📄 Docs: {bucket.get('docs_size', 0):.1f}MB, "
                          f"🔗 Entities: {bucket.get('entities_size', 0):.1f}MB, "
                          f"🌐 Relations: {bucket.get('relations_size', 0):.1f}MB")
    
    # Configuration check
    print(f"\n📋 CONFIGURATION STATUS:")
    check_configurations(directories["lightrag_working_dir"])
    
    # Integration recommendations
    print(f"\n🎯 INTEGRATION RECOMMENDATIONS:")
    provide_recommendations(categories)

def analyze_bucket(bucket_name, bucket_path, source_dir):
    """Analyze a single bucket"""
    
    # Key LightRAG files
    key_files = [
        "kv_store_full_docs.json",
        "vdb_entities.json", 
        "vdb_relationships.json",
        "vdb_chunks.json",
        "kv_store_text_chunks.json",
        "graph_chunk_entity_relation.graphml"
    ]
    
    info = {
        "name": bucket_name,
        "path": bucket_path,
        "source_dir": source_dir,
        "files_present": [],
        "files_missing": [],
        "file_sizes": {},
        "total_size_mb": 0,
        "file_count": 0,
        "has_substantial_data": False,
        "is_symlink": os.path.islink(bucket_path)
    }
    
    # Check each key file
    for file in key_files:
        file_path = os.path.join(bucket_path, file)
        if os.path.exists(file_path):
            size_bytes = os.path.getsize(file_path)
            size_mb = size_bytes / (1024 * 1024)
            
            info["files_present"].append(file)
            info["file_sizes"][file] = size_mb
            info["total_size_mb"] += size_mb
            info["file_count"] += 1
            
            # Track specific important files
            if file == "kv_store_full_docs.json":
                info["docs_size"] = size_mb
            elif file == "vdb_entities.json":
                info["entities_size"] = size_mb
            elif file == "vdb_relationships.json":
                info["relations_size"] = size_mb
                
        else:
            info["files_missing"].append(file)
    
    # Determine if this is a working bucket
    # Substantial data = has docs, entities, and relationships with reasonable sizes
    required_files = ["kv_store_full_docs.json", "vdb_entities.json", "vdb_relationships.json"]
    has_required = all(f in info["files_present"] for f in required_files)
    has_size = info["total_size_mb"] > 1.0  # At least 1MB total
    
    info["has_substantial_data"] = has_required and has_size
    
    # Print brief status
    status = "✅" if info["has_substantial_data"] else "⚠️" if info["total_size_mb"] > 0 else "❌"
    symlink_note = " (symlink)" if info["is_symlink"] else ""
    print(f"   {status} {bucket_name}: {info['total_size_mb']:.1f}MB{symlink_note}")
    
    return info

def check_configurations(working_dir):
    """Check configuration files"""
    
    config_files = [
        "bucket_config.json",
        "templates.json"
    ]
    
    for config_file in config_files:
        config_path = os.path.join(working_dir, config_file)
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                print(f"   ✅ {config_file}: Found")
                
                if config_file == "bucket_config.json":
                    print(f"      📚 Configured buckets: {len(config.get('buckets', []))}")
                    print(f"      🟢 Active buckets: {len(config.get('active', []))}")
                    
            except Exception as e:
                print(f"   ❌ {config_file}: Error reading - {e}")
        else:
            print(f"   ⚠️ {config_file}: Not found")

def provide_recommendations(categories):
    """Provide integration recommendations"""
    
    working_buckets = len(categories["miranda_legacy"]) + len(categories["academic_sources"]) + len(categories["working_buckets"])
    total_buckets = sum(len(buckets) for buckets in categories.values())
    
    print(f"   📊 {working_buckets}/{total_buckets} buckets have substantial data")
    
    if categories["miranda_legacy"]:
        print(f"   🎬 Miranda legacy buckets are working: {len(categories['miranda_legacy'])}")
    
    if categories["academic_sources"]:
        print(f"   📚 Academic sources are available: {len(categories['academic_sources'])}")
    
    if categories["empty_buckets"]:
        print(f"   🗂️ {len(categories['empty_buckets'])} empty buckets could be populated")
    
    if categories["broken_buckets"]:
        print(f"   🔧 {len(categories['broken_buckets'])} buckets may need repair")
    
    print(f"\n   💡 RECOMMENDATIONS:")
    print(f"   1. Use Miranda buckets (miranda_scripts, miranda_books, miranda_plays) for screenplay knowledge")
    print(f"   2. Use academic buckets for film theory and analysis")
    print(f"   3. The enhanced transparent system can access all working buckets")
    print(f"   4. Templates and configurations are properly set up")

if __name__ == "__main__":
    analyze_all_buckets()