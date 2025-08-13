#!/usr/bin/env python3
"""
Async test to verify Miranda buckets work with queries
"""

import os
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed

async def test_miranda_query():
    """Test Miranda buckets with async queries"""
    
    base_dir = "/Users/elle/Desktop/Elizabeth_PI/lightrag_buckets"
    
    buckets = {
        "miranda_scripts": "romantic comedy dialogue techniques",
        "miranda_books": "writing advice and techniques", 
        "miranda_plays": "dramatic structure and character development"
    }
    
    print("🎬 TESTING MIRANDA BUCKET QUERIES")
    print("="*50)
    
    for bucket_name, test_query in buckets.items():
        bucket_path = os.path.join(base_dir, bucket_name)
        
        print(f"\n📚 Testing {bucket_name}...")
        print(f"Query: '{test_query}'")
        
        try:
            rag = LightRAG(
                working_dir=bucket_path,
                embedding_func=openai_embed,
                llm_model_func=gpt_4o_mini_complete
            )
            
            # Try the query
            response = await rag.aquery(test_query, param=QueryParam(mode="local"))
            
            if response and len(response.strip()) > 20:
                print(f"✅ Query successful!")
                print(f"📄 Response ({len(response)} chars):")
                print(f"   {response[:200]}...")
                
                # Test if it actually has relevant content
                relevant_words = ["dialogue", "character", "scene", "story", "script", "comedy"]
                found_words = [word for word in relevant_words if word.lower() in response.lower()]
                print(f"🎯 Relevant terms found: {found_words}")
                
            else:
                print(f"⚠️ Query returned minimal response: '{response}'")
                
        except Exception as e:
            print(f"❌ Query failed: {e}")
    
    print(f"\n{'='*50}")
    print("Miranda bucket query testing complete!")

if __name__ == "__main__":
    asyncio.run(test_miranda_query())