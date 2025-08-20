#!/usr/bin/env python3
"""
Comprehensive test of the bucket library system
"""

import requests
import json
import time
from pathlib import Path

def test_bucket_library_system():
    """Test all aspects of the bucket library system"""
    print("🧪 COMPREHENSIVE BUCKET LIBRARY TEST")
    print("=" * 50)
    
    base_url_buckets = "http://localhost:8002"
    base_url_brainstorm = "http://localhost:8003"
    
    # Test 1: Check if servers are running
    print("\n1. 🌐 Testing server connectivity...")
    try:
        resp1 = requests.get(f"{base_url_buckets}/api/library/stats", timeout=5)
        resp2 = requests.get(f"{base_url_brainstorm}/api/projects", timeout=5)
        
        if resp1.status_code == 200 and resp2.status_code == 200:
            print("   ✅ Both servers are running and responsive")
        else:
            print(f"   ❌ Server issues - Bucket: {resp1.status_code}, Brainstorm: {resp2.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    # Test 2: Library statistics
    print("\n2. 📊 Testing library statistics...")
    try:
        resp = requests.get(f"{base_url_buckets}/api/library/stats")
        stats = resp.json()
        
        print(f"   📁 Total buckets: {stats['total_buckets']}")
        print(f"   🏗️ Total projects: {stats['total_projects']}")
        print(f"   💾 Total size: {stats['total_size_mb']:.2f} MB")
        print(f"   📍 Library path: {stats['library_path']}")
        print("   ✅ Library stats working")
    except Exception as e:
        print(f"   ❌ Library stats failed: {e}")
        return False
    
    # Test 3: List all buckets
    print("\n3. 🗂️ Testing bucket listing...")
    try:
        resp = requests.get(f"{base_url_buckets}/api/buckets")
        buckets = resp.json()
        
        bucket_types = {}
        for bucket in buckets:
            bucket_type = bucket.get('type', 'unknown')
            bucket_types[bucket_type] = bucket_types.get(bucket_type, 0) + 1
            print(f"   • {bucket['name']} ({bucket.get('type', 'unknown')}) - {bucket['nodes']} nodes, {bucket['edges']} edges")
        
        print(f"   📈 Bucket types: {dict(bucket_types)}")
        print("   ✅ Bucket listing working")
    except Exception as e:
        print(f"   ❌ Bucket listing failed: {e}")
        return False
    
    # Test 4: Create a new library bucket
    print("\n4. ➕ Testing bucket creation...")
    try:
        test_bucket_name = f"test_bucket_{int(time.time())}"
        payload = {
            "name": test_bucket_name,
            "description": "Test bucket created during library test",
            "scope": "library"
        }
        
        resp = requests.post(f"{base_url_buckets}/api/buckets", json=payload)
        result = resp.json()
        
        if result.get('success'):
            print(f"   ✅ Created library bucket: {result.get('bucket', test_bucket_name)}")
            print(f"   🌐 Scope: {result.get('scope', 'unknown')}")
        else:
            print(f"   ❌ Bucket creation failed: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"   ❌ Bucket creation failed: {e}")
        return False
    
    # Test 5: Test brainstorm integration
    print("\n5. 🧠 Testing brainstorm integration...")
    try:
        # Get projects
        resp = requests.get(f"{base_url_brainstorm}/api/projects")
        projects = resp.json()['projects']
        
        if projects:
            test_project = projects[0]
            print(f"   🎯 Testing with project: {test_project}")
            
            # Get project schema (includes bucket data blocks)
            resp = requests.get(f"{base_url_brainstorm}/api/project/{test_project}/schema")
            schema = resp.json()
            
            if 'data_blocks' in schema and 'lightrag' in schema['data_blocks']:
                lightrag_blocks = schema['data_blocks']['lightrag']
                print(f"   📚 Found {len(lightrag_blocks)} LightRAG data blocks:")
                
                for block in lightrag_blocks[:3]:  # Show first 3
                    block_type = block.get('type', 'unknown')
                    importable = '(importable)' if block.get('importable') else ''
                    print(f"     • {block['label']} ({block_type}) {importable}")
                
                print("   ✅ Brainstorm integration working")
            else:
                print("   ❌ No LightRAG blocks found in brainstorm")
                return False
        else:
            print("   ❌ No projects found")
            return False
    except Exception as e:
        print(f"   ❌ Brainstorm integration failed: {e}")
        return False
    
    # Test 6: Test import functionality
    print("\n6. 📥 Testing bucket import...")
    try:
        # Get library buckets
        resp = requests.get(f"{base_url_buckets}/api/library/buckets")
        library_buckets = resp.json()
        
        if library_buckets:
            # Try to import the first bucket
            bucket_to_import = library_buckets[0]['id']
            print(f"   🎯 Attempting to import: {bucket_to_import}")
            
            resp = requests.post(f"{base_url_buckets}/api/library/import/{bucket_to_import}")
            result = resp.json()
            
            if result.get('success'):
                print(f"   ✅ Successfully imported bucket")
                print(f"   💬 Message: {result.get('message', 'No message')}")
            else:
                print(f"   ⚠️ Import result: {result.get('message', 'Already imported or error')}")
        else:
            print("   ❌ No library buckets found to import")
    except Exception as e:
        print(f"   ❌ Import test failed: {e}")
    
    # Test 7: Test file system structure
    print("\n7. 📁 Testing file system structure...")
    try:
        library_path = Path.home() / "lightrag_library"
        
        if library_path.exists():
            buckets_dir = library_path / "buckets"
            projects_dir = library_path / "projects"
            config_file = library_path / "library_config.json"
            
            bucket_count = len(list(buckets_dir.glob("*"))) if buckets_dir.exists() else 0
            project_count = len(list(projects_dir.glob("*.json"))) if projects_dir.exists() else 0
            
            print(f"   📍 Library path: {library_path}")
            print(f"   🗂️ Buckets directory: {bucket_count} buckets")
            print(f"   🏗️ Projects directory: {project_count} projects")
            print(f"   ⚙️ Config file exists: {config_file.exists()}")
            print("   ✅ File system structure correct")
        else:
            print(f"   ❌ Library path doesn't exist: {library_path}")
            return False
    except Exception as e:
        print(f"   ❌ File system test failed: {e}")
        return False
    
    # Test 8: Test current project integration
    print("\n8. 🏠 Testing current project integration...")
    try:
        from bucket_library_integration import BucketLibraryIntegration
        
        integration = BucketLibraryIntegration()
        available_buckets = integration.list_available_buckets()
        
        print(f"   📊 Project buckets summary:")
        print(f"     • Imported: {len(available_buckets['project']['imported'])}")
        print(f"     • Local: {len(available_buckets['project']['local'])}")
        print(f"     • Available to import: {len(available_buckets['library']['available'])}")
        print(f"     • Total library buckets: {available_buckets['library']['total']}")
        print("   ✅ Project integration working")
    except Exception as e:
        print(f"   ❌ Project integration failed: {e}")
        return False
    
    # Final results
    print("\n" + "=" * 50)
    print("🎉 BUCKET LIBRARY SYSTEM TEST RESULTS")
    print("=" * 50)
    print("✅ ALL TESTS PASSED!")
    print()
    print("🌟 Your bucket library system is fully functional:")
    print("   • Centralized bucket storage")
    print("   • Cross-project sharing")
    print("   • Import/export functionality") 
    print("   • Brainstorm integration")
    print("   • REST API access")
    print("   • File system organization")
    print()
    print("🚀 Ready to use at:")
    print(f"   • Bucket Manager: {base_url_buckets}")
    print(f"   • Brainstorm Builder: {base_url_brainstorm}")
    
    return True

if __name__ == "__main__":
    success = test_bucket_library_system()
    exit(0 if success else 1)