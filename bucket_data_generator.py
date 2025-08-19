#!/usr/bin/env python3
"""
Generate real bucket data from LightRAG directories for web interface
"""

import json
import os
import sys
from datetime import datetime

def scan_bucket_directories():
    """Scan both lightrag_working_dir and lightrag_buckets for real bucket data"""
    buckets = []
    bucket_id = 1
    
    # Scan both directories
    directories = [
        ("lightrag_working_dir", "Working"),
        ("lightrag_buckets", "Archive")
    ]
    
    for base_dir, group_name in directories:
        if not os.path.exists(base_dir):
            continue
            
        for bucket_name in os.listdir(base_dir):
            bucket_path = os.path.join(base_dir, bucket_name)
            
            # Skip files, only process directories
            if not os.path.isdir(bucket_path):
                continue
                
            # Skip hidden directories
            if bucket_name.startswith('.'):
                continue
            
            bucket_info = analyze_bucket(bucket_path, bucket_name, group_name, bucket_id)
            if bucket_info:
                buckets.append(bucket_info)
                bucket_id += 1
    
    return buckets

def analyze_bucket(bucket_path, bucket_name, group_name, bucket_id):
    """Analyze a single bucket directory and extract statistics"""
    
    # Count documents from kv_store_full_docs.json
    doc_count = 0
    docs_file = os.path.join(bucket_path, "kv_store_full_docs.json")
    if os.path.exists(docs_file):
        try:
            with open(docs_file, 'r') as f:
                content = f.read().strip()
                if content and content != "{}":
                    data = json.loads(content)
                    # Handle both dict and list formats
                    if isinstance(data, dict):
                        doc_count = len(data.get('data', {}))
                    elif isinstance(data, list):
                        doc_count = len(data)
        except:
            doc_count = 0
    
    # Count entities from vdb_entities.json
    entity_count = 0
    entities_file = os.path.join(bucket_path, "vdb_entities.json")
    if os.path.exists(entities_file):
        try:
            with open(entities_file, 'r') as f:
                data = json.load(f)
                entity_count = len(data.get('data', []))
        except:
            entity_count = 0
    
    # Count relationships from vdb_relationships.json
    relation_count = 0
    relations_file = os.path.join(bucket_path, "vdb_relationships.json")
    if os.path.exists(relations_file):
        try:
            with open(relations_file, 'r') as f:
                data = json.load(f)
                relation_count = len(data.get('data', []))
        except:
            relation_count = 0
    
    # Count chunks from vdb_chunks.json
    chunk_count = 0
    chunks_file = os.path.join(bucket_path, "vdb_chunks.json")
    if os.path.exists(chunks_file):
        try:
            with open(chunks_file, 'r') as f:
                data = json.load(f)
                chunk_count = len(data.get('data', []))
        except:
            chunk_count = 0
    
    # Get last modified time
    try:
        # Check the most recent file in the bucket
        files = [f for f in os.listdir(bucket_path) if f.endswith('.json')]
        if files:
            most_recent_file = max([os.path.join(bucket_path, f) for f in files], 
                                 key=os.path.getmtime)
            mod_time = os.path.getmtime(most_recent_file)
            last_edited = format_time_ago(mod_time)
        else:
            last_edited = "Unknown"
    except:
        last_edited = "Unknown"
    
    # Only include buckets that have some data
    if doc_count > 0 or entity_count > 0 or relation_count > 0:
        # Create a better description
        description = get_bucket_description(bucket_name, entity_count, chunk_count)
        
        return {
            "id": bucket_id,
            "name": bucket_name,
            "group": group_name,
            "lastEdited": last_edited,
            "docCount": chunk_count,  # Use chunks as document count since it's more meaningful
            "nodeCount": entity_count,
            "edgeCount": relation_count,
            "chunkCount": chunk_count,
            "description": description,
            "selected": False
        }
    
    return None

def get_bucket_description(bucket_name, entity_count, chunk_count):
    """Generate meaningful descriptions for buckets based on their names"""
    descriptions = {
        "shakespeare_plays": "Complete works and analysis of Shakespeare's plays",
        "screenwriting_books": "Books and guides on screenwriting craft and technique", 
        "romcom_scripts": "Romantic comedy screenplay collection and examples",
        "academic_sources": "Academic papers and scholarly articles on film theory",
        "reference_sources": "General reference materials and foundational texts",
        "cultural_sources": "Cultural studies and contextual materials",
        "bordwell_sources": "David Bordwell's film analysis and theory works",
        "cook_sources": "Pam Cook's film studies and criticism materials",
        "balio_sources": "Tino Balio's film industry and history research",
        "knight_sources": "Arthur Knight's film history and criticism",
        "cousins_sources": "Mark Cousins' film history and documentary work",
        "dixon_foster_sources": "Wheeler Winston Dixon and Gwendolyn Audrey Foster's film scholarship",
        "gomery_sources": "Douglas Gomery's film industry economics and history",
        "american_cinema_series": "American cinema history and development analysis",
        "miranda_plays": "Archive of Miranda's theatrical works",
        "miranda_books": "Archive of Miranda's book collection",
        "miranda_scripts": "Archive of Miranda's screenplay collection"
    }
    
    if bucket_name in descriptions:
        return descriptions[bucket_name]
    else:
        return f"Knowledge repository with {entity_count:,} entities and {chunk_count} text segments"

def format_time_ago(timestamp):
    """Format timestamp as human readable 'time ago' string"""
    now = datetime.now().timestamp()
    diff = now - timestamp
    
    if diff < 3600:  # Less than 1 hour
        minutes = int(diff / 60)
        return f"{minutes} minutes ago" if minutes > 1 else "Just now"
    elif diff < 86400:  # Less than 1 day
        hours = int(diff / 3600)
        return f"{hours} hours ago" if hours > 1 else "1 hour ago"
    elif diff < 2592000:  # Less than 1 month
        days = int(diff / 86400)
        return f"{days} days ago" if days > 1 else "1 day ago"
    else:
        weeks = int(diff / 604800)
        return f"{weeks} weeks ago" if weeks > 1 else "1 week ago"

def generate_javascript_data():
    """Generate JavaScript code with real bucket data"""
    buckets = scan_bucket_directories()
    
    js_code = f"""// Real bucket data generated from LightRAG directories
        let buckets = {json.dumps(buckets, indent=8)};"""
    
    return js_code

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        # Output just JSON for API use
        buckets = scan_bucket_directories()
        print(json.dumps(buckets, indent=2))
    else:
        # Output JavaScript code
        print(generate_javascript_data())