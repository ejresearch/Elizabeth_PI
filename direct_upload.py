#!/usr/bin/env python3
"""Direct upload to LightRAG system bypassing API issues"""

import os
import sys
sys.path.append('/Users/elle/Desktop/Elizabeth_PI')

from core_knowledge import LightRAGManager
import time

def main():
    # Check for OpenAI API key in environment
    if not os.environ.get('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable")
        sys.exit(1)
    
    print("🚀 Starting direct LightRAG upload...")
    
    # Initialize manager
    manager = LightRAGManager()
    
    # Create bucket if it doesn't exist
    bucket_name = "scifi_screenplays"
    print(f"📦 Creating bucket: {bucket_name}")
    manager.create_bucket(bucket_name, "Science fiction screenplays and stories collection for testing", auto_activate=True)
    
    # Upload documents
    documents = [
        ("blade_runner_2049_scenes.txt", "Blade Runner 2049 inspired scenes"),
        ("matrix_inspired_scenes.txt", "Matrix inspired scenes"), 
        ("alien_inspired_scenes.txt", "Alien inspired scenes")
    ]
    
    for filename, description in documents:
        print(f"📄 Uploading {filename}...")
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clean content
            content = content[:10000]  # Limit size for testing
            
            success = manager.add_document_to_bucket(bucket_name, content, {"filename": filename, "description": description})
            if success:
                print(f"✅ Successfully uploaded {filename}")
            else:
                print(f"❌ Failed to upload {filename}")
                
            time.sleep(2)  # Brief pause between uploads
            
        except Exception as e:
            print(f"❌ Error uploading {filename}: {e}")
    
    print("\n🔍 Testing bucket functionality...")
    
    # Test bucket stats
    try:
        stats = manager.get_knowledge_graph_stats(bucket_name)
        print(f"📊 Bucket stats: {stats}")
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
    
    # Test query
    try:
        print("\n🔍 Testing query...")
        result = manager.query_bucket(bucket_name, "What are the main themes in Blade Runner?", "hybrid")
        print(f"Query result: {result}")
    except Exception as e:
        print(f"❌ Error querying: {e}")
    
    print("\n✅ Upload test complete!")

if __name__ == "__main__":
    main()