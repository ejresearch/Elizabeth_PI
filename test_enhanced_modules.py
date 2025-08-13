#!/usr/bin/env python3
"""
Test script for enhanced brainstorm and write modules
Run this to verify the modules work with your current project
"""

import os
import sys
from enhanced_brainstorm import run_enhanced_brainstorm
from enhanced_write import run_enhanced_write


def test_enhanced_modules():
    """Test the enhanced modules with the current project"""
    
    # Check for existing project
    project_path = "exports/the_wrong_wedding_20250813_1253"
    
    if not os.path.exists(project_path):
        print(f"❌ Project not found at: {project_path}")
        print("Please ensure you have a project created first.")
        return
    
    print(f"✅ Found project: {project_path}")
    
    # Test buckets
    test_buckets = ["scripts", "books", "plays"]
    
    print("\n" + "="*60)
    print("TESTING ENHANCED BRAINSTORM MODULE")
    print("="*60)
    
    try:
        # Run brainstorming for all scenes
        brainstorm_session = run_enhanced_brainstorm(
            project_path=project_path,
            selected_buckets=test_buckets[:1],  # Start with just "scripts" to test
            user_guidance="Focus on witty dialogue and romantic tension"
        )
        print(f"✅ Brainstorming completed: {brainstorm_session}")
    except Exception as e:
        print(f"❌ Brainstorming failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*60)
    print("TESTING ENHANCED WRITE MODULE")
    print("="*60)
    
    try:
        # Run writing for all scenes
        write_version = run_enhanced_write(
            project_path=project_path,
            selected_buckets=test_buckets[:1],  # Start with just "scripts" to test
            user_guidance="Very well written with natural dialogue"
        )
        print(f"✅ Writing completed: {write_version}")
    except Exception as e:
        print(f"❌ Writing failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*60)
    print("✨ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\nThe enhanced modules are ready to use.")
    print("You can now integrate them into your lizzy.py workflow.")
    

def quick_test():
    """Quick test to verify basic functionality"""
    print("\n🔍 QUICK MODULE TEST")
    print("-"*40)
    
    # Test imports
    try:
        from enhanced_brainstorm import EnhancedBrainstormAgent
        print("✅ Enhanced brainstorm module imported")
    except ImportError as e:
        print(f"❌ Failed to import brainstorm module: {e}")
        return False
    
    try:
        from enhanced_write import EnhancedWriteAgent
        print("✅ Enhanced write module imported")
    except ImportError as e:
        print(f"❌ Failed to import write module: {e}")
        return False
    
    # Test initialization
    try:
        brainstorm_agent = EnhancedBrainstormAgent()
        print("✅ Brainstorm agent initialized")
    except Exception as e:
        print(f"❌ Failed to initialize brainstorm agent: {e}")
        return False
    
    try:
        write_agent = EnhancedWriteAgent()
        print("✅ Write agent initialized")
    except Exception as e:
        print(f"❌ Failed to initialize write agent: {e}")
        return False
    
    print("\n✨ Quick test passed! Modules are functional.")
    return True


if __name__ == "__main__":
    print("ENHANCED LIZZY MODULES TEST SUITE")
    print("="*60)
    
    # Run quick test first
    if quick_test():
        print("\nProceed with full test? (y/n): ", end="")
        choice = input().strip().lower()
        
        if choice == 'y':
            test_enhanced_modules()
    else:
        print("\n❌ Quick test failed. Please check module files.")