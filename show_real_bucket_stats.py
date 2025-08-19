#!/usr/bin/env python3
"""
Show the actual bucket statistics by reading the vector database files
"""

import json
import os

print("=" * 80)
print("ACTUAL BUCKET STATISTICS FROM VECTOR DATABASES")
print("=" * 80)

lightrag_dir = "lightrag_working_dir"
buckets = [
    "romcom_scripts", "screenwriting_books", "shakespeare_plays",
    "academic_sources", "balio_sources", "bordwell_sources",
    "cook_sources", "cousins_sources", "cultural_sources", "reference_sources"
]

print(f"\n{'Bucket':<20} {'Entities':<12} {'Relations':<12} {'Chunks':<12}")
print("-" * 70)

total_entities = 0
total_relations = 0
total_chunks = 0

for bucket in buckets:
    bucket_dir = os.path.join(lightrag_dir, bucket)
    
    # Count entities
    entities_file = os.path.join(bucket_dir, "vdb_entities.json")
    entities_count = 0
    if os.path.exists(entities_file):
        with open(entities_file, 'r') as f:
            data = json.load(f)
            if 'data' in data:
                entities_count = len(data['data'])
    
    # Count relationships
    relations_file = os.path.join(bucket_dir, "vdb_relationships.json")
    relations_count = 0
    if os.path.exists(relations_file):
        with open(relations_file, 'r') as f:
            data = json.load(f)
            if 'data' in data:
                relations_count = len(data['data'])
    
    # Count chunks
    chunks_file = os.path.join(bucket_dir, "vdb_chunks.json")
    chunks_count = 0
    if os.path.exists(chunks_file):
        with open(chunks_file, 'r') as f:
            data = json.load(f)
            if 'data' in data:
                chunks_count = len(data['data'])
    
    print(f"{bucket:<20} {entities_count:<12,} {relations_count:<12,} {chunks_count:<12,}")
    
    total_entities += entities_count
    total_relations += relations_count
    total_chunks += chunks_count

print("-" * 70)
print(f"{'TOTAL':<20} {total_entities:<12,} {total_relations:<12,} {total_chunks:<12,}")

print("\n" + "=" * 80)
print("WHAT THIS MEANS:")
print("=" * 80)
print(f"""
Your LightRAG knowledge base contains:

📊 {total_entities:,} named entities (people, places, concepts)
🔗 {total_relations:,} relationships between entities
📄 {total_chunks:,} text chunks from source materials

This rich knowledge base is used to:
• Provide context when brainstorming scenes
• Suggest authentic dialogue and situations
• Maintain consistency with genre conventions
• Draw from real screenplay examples and theory

The INFO messages you see are the system loading these vector databases
into memory so they can be searched efficiently when you brainstorm or write.
""")