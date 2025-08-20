#!/usr/bin/env python3
"""
Test script for the bucket library system
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

def test_bucket_library():
    """Test the bucket library functionality"""
    print("🧪 Testing Bucket Library System\n")
    
    results = {
        "passed": [],
        "failed": [],
        "errors": []
    }
    
    # Test 1: Import modules
    print("1. Testing module imports...")
    try:
        from core_bucket_library import BucketLibrary, ProjectLightRAGManager
        from bucket_library_integration import BucketLibraryIntegration
        results["passed"].append("Module imports")
        print("   ✅ Modules imported successfully")
    except ImportError as e:
        results["failed"].append(f"Module imports: {e}")
        print(f"   ❌ Failed to import modules: {e}")
        return results
    
    # Test 2: Initialize library
    print("\n2. Testing library initialization...")
    try:
        # Use temp directory for testing
        test_lib_path = Path(tempfile.mkdtemp(prefix="test_lightrag_library_"))
        library = BucketLibrary(library_path=str(test_lib_path))
        
        # Check if directories were created
        assert (test_lib_path / "buckets").exists()
        assert (test_lib_path / "projects").exists()
        assert (test_lib_path / "library_config.json").exists()
        
        results["passed"].append("Library initialization")
        print(f"   ✅ Library initialized at: {test_lib_path}")
    except Exception as e:
        results["failed"].append(f"Library initialization: {e}")
        print(f"   ❌ Failed to initialize library: {e}")
        return results
    
    # Test 3: Create bucket in library
    print("\n3. Testing bucket creation...")
    try:
        result = library.create_bucket(
            bucket_name="test_bucket",
            project_name="TestProject",
            description="Test bucket for validation"
        )
        
        assert result["success"] == True
        bucket_id = result["bucket_id"]
        bucket_path = Path(result["path"])
        assert bucket_path.exists()
        
        # Check metadata file
        metadata_file = bucket_path / "bucket_metadata.json"
        assert metadata_file.exists()
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
            assert metadata["name"] == "test_bucket"
            assert metadata["description"] == "Test bucket for validation"
            assert "TestProject" in metadata["projects"]
        
        results["passed"].append("Bucket creation")
        print(f"   ✅ Created bucket: {bucket_id}")
    except Exception as e:
        results["failed"].append(f"Bucket creation: {e}")
        print(f"   ❌ Failed to create bucket: {e}")
    
    # Test 4: Project manager initialization
    print("\n4. Testing project manager...")
    try:
        test_project_dir = Path(tempfile.mkdtemp(prefix="test_project_"))
        project_manager = ProjectLightRAGManager(
            project_dir=str(test_project_dir),
            project_name="TestProject",
            library=library
        )
        
        # Check project structure
        assert (test_project_dir / "lightrag_working_dir").exists()
        assert (test_project_dir / "lightrag_working_dir" / "imported").exists()
        assert (test_project_dir / "lightrag_working_dir" / "local").exists()
        
        results["passed"].append("Project manager")
        print(f"   ✅ Project manager initialized")
    except Exception as e:
        results["failed"].append(f"Project manager: {e}")
        print(f"   ❌ Failed to initialize project manager: {e}")
    
    # Test 5: Import bucket to project
    print("\n5. Testing bucket import...")
    try:
        import_result = project_manager.import_from_library(bucket_id)
        assert import_result["success"] == True
        
        # Check if symlink or copy was created
        imported_path = test_project_dir / "lightrag_working_dir" / "imported" / bucket_id
        assert imported_path.exists()
        
        results["passed"].append("Bucket import")
        print(f"   ✅ Imported bucket to project")
    except Exception as e:
        results["failed"].append(f"Bucket import: {e}")
        print(f"   ❌ Failed to import bucket: {e}")
    
    # Test 6: Create local bucket
    print("\n6. Testing local bucket creation...")
    try:
        local_result = project_manager.create_local_bucket(
            bucket_name="local_test",
            description="Local bucket test"
        )
        assert local_result["success"] == True
        
        local_path = Path(local_result["path"])
        assert local_path.exists()
        
        results["passed"].append("Local bucket creation")
        print(f"   ✅ Created local bucket")
    except Exception as e:
        results["failed"].append(f"Local bucket creation: {e}")
        print(f"   ❌ Failed to create local bucket: {e}")
    
    # Test 7: List buckets
    print("\n7. Testing bucket listing...")
    try:
        all_buckets = project_manager.list_all_buckets()
        print(f"   Debug: Buckets = {all_buckets}")
        
        # More lenient checks since we might have either imported or local
        assert "imported" in all_buckets
        assert "local" in all_buckets
        assert "total" in all_buckets
        assert all_buckets["total"] > 0
        
        results["passed"].append("Bucket listing")
        print(f"   ✅ Listed buckets - Imported: {len(all_buckets['imported'])}, Local: {len(all_buckets['local'])}, Total: {all_buckets['total']}")
    except Exception as e:
        results["failed"].append(f"Bucket listing: {e}")
        print(f"   ❌ Failed to list buckets: {e}")
    
    # Test 8: Search functionality
    print("\n8. Testing search...")
    try:
        search_results = library.search_buckets("test")
        assert len(search_results) > 0
        
        results["passed"].append("Search functionality")
        print(f"   ✅ Search found {len(search_results)} buckets")
    except Exception as e:
        results["failed"].append(f"Search functionality: {e}")
        print(f"   ❌ Failed search: {e}")
    
    # Test 9: Library stats
    print("\n9. Testing library stats...")
    try:
        stats = library.get_library_stats()
        assert stats["total_buckets"] > 0
        assert "library_path" in stats
        
        results["passed"].append("Library stats")
        print(f"   ✅ Got library stats - Total buckets: {stats['total_buckets']}")
    except Exception as e:
        results["failed"].append(f"Library stats: {e}")
        print(f"   ❌ Failed to get stats: {e}")
    
    # Test 10: Integration layer
    print("\n10. Testing integration layer...")
    try:
        test_integration_dir = Path(tempfile.mkdtemp(prefix="test_integration_"))
        os.chdir(test_integration_dir)  # Change to test directory
        
        integration = BucketLibraryIntegration(
            project_dir=str(test_integration_dir),
            project_name="IntegrationTest"
        )
        
        # Test creating through integration
        create_result = integration.create_bucket(
            bucket_name="integration_test",
            description="Test via integration",
            scope="library"
        )
        
        if create_result["success"]:
            results["passed"].append("Integration layer")
            print(f"   ✅ Integration layer working")
        else:
            results["failed"].append(f"Integration layer: {create_result.get('error', 'Unknown error')}")
            print(f"   ❌ Integration failed: {create_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        results["failed"].append(f"Integration layer: {e}")
        print(f"   ❌ Failed integration test: {e}")
    
    # Cleanup
    print("\n11. Cleaning up test files...")
    try:
        if 'test_lib_path' in locals():
            shutil.rmtree(test_lib_path, ignore_errors=True)
        if 'test_project_dir' in locals():
            shutil.rmtree(test_project_dir, ignore_errors=True)
        if 'test_integration_dir' in locals():
            shutil.rmtree(test_integration_dir, ignore_errors=True)
        print("   ✅ Cleanup complete")
    except Exception as e:
        print(f"   ⚠️ Cleanup warning: {e}")
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    print(f"✅ Passed: {len(results['passed'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    
    if results["passed"]:
        print("\nPassed tests:")
        for test in results["passed"]:
            print(f"  • {test}")
    
    if results["failed"]:
        print("\nFailed tests:")
        for test in results["failed"]:
            print(f"  • {test}")
    
    return results

def test_server_integration():
    """Test the server integration"""
    print("\n🌐 Testing Server Integration\n")
    
    try:
        # Check if server modifications work
        print("1. Checking if bucket_manager_server.py imports correctly...")
        
        # Save current directory
        original_dir = os.getcwd()
        
        # Try to import the server module
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # We can't actually run the server in test, but we can check imports
        import bucket_manager_server
        
        print("   ✅ Server module imports successfully")
        
        # Check for the BucketManager class
        assert hasattr(bucket_manager_server, 'BucketManager')
        print("   ✅ BucketManager class found")
        
        # Restore directory
        os.chdir(original_dir)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Server integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Bucket Library System Test Suite")
    print("="*50)
    
    # Run main tests
    results = test_bucket_library()
    
    # Run server integration test
    print("\n" + "="*50)
    server_ok = test_server_integration()
    
    # Final verdict
    print("\n" + "="*50)
    print("🏁 FINAL RESULTS")
    print("="*50)
    
    if len(results["failed"]) == 0 and server_ok:
        print("✅ ALL TESTS PASSED! The bucket library system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please review the errors above.")
        print("\nRecommendations:")
        print("1. Ensure all dependencies are installed")
        print("2. Check file permissions for creating directories")
        print("3. Verify Python version compatibility (3.7+)")
        
    sys.exit(0 if len(results["failed"]) == 0 else 1)