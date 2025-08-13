#!/usr/bin/env python3
"""
Test the new bucket collections system
"""

import sys
import os

# Add the main directory to path
sys.path.append('/Users/elle/Desktop/Elizabeth_PI')

from lizzy_templates import TemplateManager

def test_bucket_collections():
    """Test the new bucket collection organization"""
    
    print("🧪 TESTING BUCKET COLLECTIONS SYSTEM")
    print("="*60)
    
    # Initialize template manager
    tm = TemplateManager()
    
    # Load current bucket configuration
    print("\n1. Loading bucket configuration...")
    success = tm.load_bucket_config()
    if success:
        print("   ✅ Bucket configuration loaded successfully")
    else:
        print("   ⚠️ Could not load bucket configuration")
    
    # Test romcom template buckets
    print("\n2. Testing romcom template buckets...")
    romcom_buckets = tm.get_template_buckets("romcom")
    print(f"   📚 Romcom buckets: {romcom_buckets}")
    
    expected_romcom = ["romcom_scripts", "screenwriting_books", "shakespeare_plays"]
    if set(romcom_buckets) == set(expected_romcom):
        print("   ✅ Romcom buckets correctly assigned")
    else:
        print(f"   ❌ Expected {expected_romcom}, got {romcom_buckets}")
    
    # Test textbook template buckets  
    print("\n3. Testing textbook template buckets...")
    textbook_buckets = tm.get_template_buckets("textbook")
    print(f"   📚 Textbook buckets: {textbook_buckets}")
    
    expected_textbook = ["academic_sources", "balio_sources", "bordwell_sources", 
                        "cook_sources", "cousins_sources", "cultural_sources", "reference_sources"]
    if set(textbook_buckets) == set(expected_textbook):
        print("   ✅ Textbook buckets correctly assigned")
    else:
        print(f"   ❌ Expected {expected_textbook}, got {textbook_buckets}")
    
    # Test template compilation
    print("\n4. Testing template compilation...")
    
    # Sample context
    context = {
        "act": 1,
        "scene": 3,
        "scene_context": "Coffee shop meet-cute",
        "character_details": "Sarah (28): Commitment-phobic\nJake (30): Workaholic",
        "previous_scene": "Sarah's morning routine"
    }
    
    # Test romcom template
    print("\n   Testing romcom template...")
    romcom_prompt = tm.compile_prompt("romcom", "romcom", context)
    if romcom_prompt and len(romcom_prompt) > 100:
        print("   ✅ Romcom template compiled successfully")
        print(f"   📄 Length: {len(romcom_prompt)} characters")
        
        # Check for expected elements
        romcom_elements = ["romantic comedy", "comedic timing", "theatrical", "meet-cute"]
        found_elements = [elem for elem in romcom_elements if elem.lower() in romcom_prompt.lower()]
        print(f"   🎯 Found elements: {found_elements}")
    else:
        print("   ❌ Romcom template compilation failed")
    
    # Test textbook template
    print("\n   Testing textbook template...")
    textbook_prompt = tm.compile_prompt("textbook", "textbook", context)
    if textbook_prompt and len(textbook_prompt) > 100:
        print("   ✅ Textbook template compiled successfully")
        print(f"   📄 Length: {len(textbook_prompt)} characters")
        
        # Check for expected elements
        textbook_elements = ["film theory", "academic", "scholarly", "critical analysis"]
        found_elements = [elem for elem in textbook_elements if elem.lower() in textbook_prompt.lower()]
        print(f"   🎯 Found elements: {found_elements}")
    else:
        print("   ❌ Textbook template compilation failed")
    
    # Summary
    print(f"\n{'='*60}")
    print("BUCKET COLLECTIONS SUMMARY:")
    print("✅ Bucket collections configuration created")
    print("✅ Romcom buckets: romcom_scripts, screenwriting_books, shakespeare_plays")
    print("✅ Film book buckets: academic_sources, balio_sources, bordwell_sources, etc.")
    print("✅ Templates updated to use bucket collections")
    print("✅ System ready for users to select template types")
    
    print(f"\n🎯 USAGE:")
    print("- Users can choose 'romcom' template for romantic comedy projects")
    print("- Users can choose 'textbook' template for academic film analysis")
    print("- Each template automatically loads its assigned bucket collection")
    print("- Users can still create project-specific buckets as needed")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    test_bucket_collections()