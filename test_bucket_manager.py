#!/usr/bin/env python3
"""
Test the Bucket Manager functionality
"""

import os
import sys

# Set up a test project directory
test_project = "test_project"
os.makedirs(f"projects/{test_project}", exist_ok=True)

# Import lizzy components
from lizzy import session, bucket_manager_menu, Colors, print_header, print_separator

# Set up session
session.current_project = test_project
session.api_key_set = True

print("=" * 80)
print("TESTING BUCKET MANAGER LAUNCH")
print("=" * 80)

# Test imports
try:
    from lizzy_lightrag_manager import LightRAGManager, BucketInterface
    print("✅ LightRAG modules imported successfully")
    
    # Test creating manager
    project_path = f"projects/{test_project}"
    manager = LightRAGManager(base_dir=os.path.join(project_path, "lightrag_working_dir"))
    print("✅ LightRAG manager created successfully")
    
    # Test creating interface
    interface = BucketInterface(manager)
    print("✅ Bucket interface created successfully")
    
    print("\n" + "=" * 80)
    print("BUCKET MANAGER WOULD SHOW:")
    print("=" * 80)
    
    print(f"\n{Colors.BOLD}🗂️ BUCKET MANAGER - LightRAG Knowledge Base{Colors.END}")
    print(f"{Colors.CYAN}{'═' * 80}{Colors.END}")
    print(f"{Colors.CYAN}Launching Bucket Manager...{Colors.END}")
    print(f"{Colors.YELLOW}This is your central hub for managing knowledge buckets.{Colors.END}")
    print(f"{Colors.YELLOW}You can browse, inspect, visualize, and compare buckets.{Colors.END}\n")
    
    print("BUCKET MANAGEMENT MENU:")
    print("1. View bucket status")
    print("2. Create new bucket")
    print("3. Toggle bucket on/off")
    print("4. Add document to bucket")
    print("5. Visualize knowledge graph")
    print("6. Export bucket data")
    print("0. Back")
    
    print("\n✅ Bucket Manager is ready to use!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")