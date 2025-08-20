#!/usr/bin/env python3
"""
Test the brainstorm integration with bucket library
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

def test_brainstorm_bucket_integration():
    """Test that brainstorm server can discover bucket library buckets"""
    print("🧪 Testing Brainstorm-Bucket Library Integration\n")
    
    try:
        # Create a test project structure
        test_project_dir = Path(tempfile.mkdtemp(prefix="test_brainstorm_project_"))
        projects_dir = test_project_dir / "projects"
        projects_dir.mkdir()
        
        project_name = "test_screenplay"
        project_path = projects_dir / project_name
        project_path.mkdir()
        
        # Create a basic project database
        import sqlite3
        db_path = project_path / f"{project_name}.sqlite"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create a simple table for testing
        cursor.execute("""
            CREATE TABLE characters (
                id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT
            )
        """)
        
        cursor.execute("""
            INSERT INTO characters (name, description) VALUES 
            ('Alice', 'The protagonist'),
            ('Bob', 'The love interest')
        """)
        
        conn.commit()
        conn.close()
        
        # Change to test directory
        original_cwd = os.getcwd()
        os.chdir(test_project_dir)
        
        # Initialize bucket library integration
        from bucket_library_integration import BucketLibraryIntegration
        integration = BucketLibraryIntegration(
            project_dir=str(project_path),
            project_name=project_name
        )
        
        # Create some test buckets
        print("1. Creating test buckets...")
        
        # Create a library bucket
        lib_result = integration.create_bucket(
            "test_scripts", 
            "Collection of test scripts", 
            scope="library"
        )
        print(f"   Library bucket: {lib_result}")
        
        # Create a local bucket
        local_result = integration.create_bucket(
            "project_notes",
            "Local project notes",
            scope="local"
        )
        print(f"   Local bucket: {local_result}")
        
        # Test the brainstorm server discovery
        print("\n2. Testing brainstorm server integration...")
        
        from web_brainstorm_server import ProjectDiscovery
        discovery = ProjectDiscovery()
        
        # Analyze the test project
        schema = discovery.analyze_project_schema(project_name)
        
        print(f"   Schema discovery result: {schema.get('error', 'Success')}")
        
        if 'data_blocks' in schema:
            print(f"   SQL blocks found: {len(schema['data_blocks']['sql'])}")
            print(f"   LightRAG blocks found: {len(schema['data_blocks']['lightrag'])}")
            print(f"   Context blocks found: {len(schema['data_blocks']['context'])}")
            
            # Show LightRAG block details
            for block in schema['data_blocks']['lightrag']:
                print(f"   - {block['label']} ({block.get('type', 'unknown')}) - {block['description']}")
        
        print("\n✅ Brainstorm-Bucket integration test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        if 'original_cwd' in locals():
            os.chdir(original_cwd)
        if 'test_project_dir' in locals():
            shutil.rmtree(test_project_dir, ignore_errors=True)

if __name__ == "__main__":
    test_brainstorm_bucket_integration()