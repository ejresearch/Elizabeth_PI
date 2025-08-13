#!/usr/bin/env python3
"""
Test script to verify Miranda buckets are working
"""

import os
import sys
from lightrag import LightRAG, QueryParam

try:
    from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
    print("✅ Successfully imported LightRAG functions")
except ImportError as e:
    print(f"❌ Could not import LightRAG functions: {e}")
    gpt_4o_mini_complete = None
    openai_embed = None

def test_miranda_buckets():
    """Test that Miranda buckets are accessible and working"""
    
    base_dir = "/Users/elle/Desktop/Elizabeth_PI/lightrag_buckets"
    
    # Check if bucket directories exist
    buckets = {
        "miranda_scripts": os.path.join(base_dir, "miranda_scripts"),
        "miranda_books": os.path.join(base_dir, "miranda_books"), 
        "miranda_plays": os.path.join(base_dir, "miranda_plays")
    }
    
    print("🔍 TESTING MIRANDA BUCKETS")
    print("="*50)
    
    for bucket_name, bucket_path in buckets.items():
        print(f"\n📚 Testing {bucket_name}...")
        
        # Check if directory exists
        if not os.path.exists(bucket_path):
            print(f"❌ Directory not found: {bucket_path}")
            continue
        
        # Check for key files
        key_files = [
            "kv_store_full_docs.json",
            "vdb_entities.json", 
            "vdb_relationships.json"
        ]
        
        missing_files = []
        for file in key_files:
            if not os.path.exists(os.path.join(bucket_path, file)):
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Missing files: {missing_files}")
            continue
        
        # Try to initialize LightRAG
        try:
            if gpt_4o_mini_complete and openai_embed:
                rag = LightRAG(
                    working_dir=bucket_path,
                    embedding_func=openai_embed,
                    llm_model_func=gpt_4o_mini_complete
                )
            else:
                print(f"❌ Missing LLM functions: gpt_4o_mini_complete={gpt_4o_mini_complete is not None}, openai_embed={openai_embed is not None}")
                continue
            print(f"✅ LightRAG initialized successfully")
            
            # Try a simple query
            test_query = "What are some examples of romantic comedy dialogue techniques?"
            
            try:
                response = rag.query(test_query, param=QueryParam(mode="local"))
                
                if response and len(response.strip()) > 10:
                    print(f"✅ Query successful - Response length: {len(response)} chars")
                    print(f"📄 Preview: {response[:100]}...")
                else:
                    print(f"⚠️ Query returned minimal response")
                    
            except Exception as e:
                print(f"❌ Query failed: {e}")
                
        except Exception as e:
            print(f"❌ LightRAG initialization failed: {e}")
    
    print(f"\n{'='*50}")
    print("Miranda bucket testing complete!")

if __name__ == "__main__":
    test_miranda_buckets()