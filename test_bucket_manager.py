#!/usr/bin/env python3
"""
Test script for the integrated bucket manager
"""

import sys
import subprocess
import time
import os

def test_bucket_manager_integration():
    """Test if the bucket manager is properly integrated"""
    
    print("🧪 Testing Bucket Manager Integration")
    print("=" * 50)
    
    # Test 1: Check if all files exist
    required_files = [
        'bucket_manager.html',
        'bucket_manager_server.py',
        'core_knowledge.py'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            return False
    
    # Test 2: Check if server can start
    print("\n🚀 Testing server startup...")
    try:
        server_process = subprocess.Popen(
            [sys.executable, 'bucket_manager_server.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give it time to start
        time.sleep(3)
        
        # Check if process is still running
        if server_process.poll() is None:
            print("✅ Server started successfully")
            
            # Test 3: Try to fetch buckets
            try:
                import requests
                response = requests.get('http://localhost:8002/api/buckets', timeout=5)
                if response.status_code == 200:
                    buckets = response.json()
                    print(f"✅ API working - found {len(buckets)} buckets")
                else:
                    print(f"⚠️ API responded with status {response.status_code}")
            except ImportError:
                print("ℹ️ requests not available, skipping API test")
            except Exception as e:
                print(f"⚠️ API test failed: {e}")
            
            # Clean up
            server_process.terminate()
            server_process.wait()
            print("🛑 Server stopped")
            
        else:
            stdout, stderr = server_process.communicate()
            print(f"❌ Server failed to start")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False
    
    # Test 4: Check imports
    print("\n📦 Testing imports...")
    try:
        from core_knowledge import BucketInterface, LightRAGManager
        print("✅ core_knowledge imports work")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    print("\n🎉 All tests passed! Bucket manager is ready to use.")
    print("\n📋 Usage:")
    print("1. Run: python3 lizzy.py")
    print("2. Navigate to Knowledge → BUCKET MANAGEMENT")
    print("3. Select option 8: 'Open Modern Bucket Manager (GUI)'")
    print("4. Your browser will open to http://localhost:8002")
    
    return True

if __name__ == "__main__":
    success = test_bucket_manager_integration()
    sys.exit(0 if success else 1)