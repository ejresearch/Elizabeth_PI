#!/usr/bin/env python3
"""
Test loading existing LightRAG buckets
"""

import os
import json
from lizzy_lightrag_manager import LightRAGManager, BucketInterface

print("=" * 80)
print("LOADING EXISTING LIGHTRAG BUCKETS")
print("=" * 80)

# Initialize manager with the main lightrag_working_dir
manager = LightRAGManager(base_dir="lightrag_working_dir")

# Load existing configuration
if os.path.exists("lightrag_working_dir/bucket_config.json"):
    manager.load_bucket_config()
    print("✅ Loaded bucket configuration")
    
# Create interface
interface = BucketInterface(manager)

# Display status
print("\nCurrent Bucket Status:")
interface.display_bucket_status()

print("\n" + "=" * 80)
print("BUCKET DETAILS")
print("=" * 80)

# Show bucket collections
with open("lightrag_working_dir/bucket_config.json", 'r') as f:
    config = json.load(f)
    
print("\n📚 Romcom Buckets (for screenplay writing):")
for bucket in config["bucket_collections"]["romcom_buckets"]["buckets"]:
    metadata = config["metadata"].get(bucket, {})
    print(f"  • {bucket}: {metadata.get('description', 'No description')}")

print("\n📚 Film Book Buckets (for textbook writing):")
for bucket in config["bucket_collections"]["film_book_buckets"]["buckets"]:
    metadata = config["metadata"].get(bucket, {})
    print(f"  • {bucket}: {metadata.get('description', 'No description')}")

print("\n" + "=" * 80)
print("YOUR LIGHTRAG DATA LOCATION")
print("=" * 80)

print(f"""
The LightRAG data is stored in:
📁 /Users/elle/Desktop/Elizabeth_PI/lightrag_working_dir/

This directory contains:
• 10 knowledge buckets with film/screenplay data
• Each bucket has its own subdirectory with:
  - graph_chunk_entity_relation.graphml (knowledge graph)
  - kv_store_* files (key-value stores)
  - vdb_* files (vector databases)
  
These buckets provide contextual knowledge for:
• Brainstorming scenes
• Writing dialogue and action
• Understanding film theory and structure
""")