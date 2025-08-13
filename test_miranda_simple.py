#!/usr/bin/env python3
"""
Simple test of Miranda buckets without complex dependencies
"""

import os
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed

async def test_miranda_simple():
    """Simple test of Miranda buckets"""
    
    print("🎬 TESTING MIRANDA BUCKETS - SIMPLE")
    print("="*50)
    
    # Test just one bucket
    bucket_path = "/Users/elle/Desktop/Elizabeth_PI/lightrag_working_dir/miranda_scripts"
    
    if not os.path.exists(bucket_path):
        print(f"❌ Bucket not found: {bucket_path}")
        return
    
    print(f"📚 Testing miranda_scripts bucket...")
    
    try:
        # Initialize LightRAG
        rag = LightRAG(
            working_dir=bucket_path,
            embedding_func=openai_embed,
            llm_model_func=gpt_4o_mini_complete
        )
        print("✅ LightRAG initialized")
        
        # Simple query
        query = "dialogue techniques"
        print(f"🔍 Query: '{query}'")
        
        # Try different query modes
        modes = ["local", "global", "hybrid"]
        
        for mode in modes:
            try:
                print(f"\n   Testing {mode} mode...")
                response = await rag.aquery(query, param=QueryParam(mode=mode))
                
                if response and len(response.strip()) > 20:
                    print(f"   ✅ {mode}: {len(response)} chars")
                    print(f"   📄 Preview: {response[:100]}...")
                    
                    # Check for relevant content
                    keywords = ["dialogue", "character", "scene", "script", "comedy", "romantic"]
                    found = [kw for kw in keywords if kw.lower() in response.lower()]
                    if found:
                        print(f"   🎯 Found keywords: {found}")
                        return True
                else:
                    print(f"   ⚠️ {mode}: Minimal response")
                    
            except Exception as e:
                print(f"   ❌ {mode}: {e}")
        
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False
    
    return False

if __name__ == "__main__":
    success = asyncio.run(test_miranda_simple())
    if success:
        print("\n🎉 Miranda buckets are working!")
    else:
        print("\n❌ Miranda buckets need troubleshooting")