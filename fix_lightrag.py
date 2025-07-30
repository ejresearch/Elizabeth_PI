#!/usr/bin/env python3
"""
LightRAG Installation Fixer for Lizzy Framework
Fixes broken LightRAG installations and installs the correct HKU version
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def main():
    print("🎬 LIZZY FRAMEWORK - LightRAG Installation Fixer")
    print("=" * 60)
    
    print("\n📋 This script will:")
    print("   1. Remove any existing broken LightRAG installations")
    print("   2. Install the correct HKU version (lightrag-hku)")
    print("   3. Test the installation")
    
    confirm = input(f"\nContinue? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Installation cancelled")
        return
    
    print("\n🚀 Starting LightRAG fix...")
    
    # Step 1: Remove existing installations
    commands_to_try = [
        ("pip uninstall lightrag -y", "Removing old lightrag"),
        ("pip uninstall lightrag-hku -y", "Removing old lightrag-hku (if exists)"),
    ]
    
    for cmd, desc in commands_to_try:
        run_command(cmd, desc)
    
    # Step 2: Install correct version
    success = run_command("pip install lightrag-hku", "Installing lightrag-hku")
    
    if not success:
        print("\n❌ Installation failed!")
        print("💡 Try manually:")
        print("   pip install lightrag-hku")
        return
    
    # Step 3: Test installation
    print("\n🧪 Testing installation...")
    
    test_code = '''
import sys
try:
    from lightrag import LightRAG, QueryParam
    from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
    from lightrag.kg.shared_storage import initialize_pipeline_status
    print("✅ All imports successful!")
    sys.exit(0)
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
'''
    
    try:
        result = subprocess.run([sys.executable, "-c", test_code], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ LightRAG installation test passed!")
            print("\n🎉 SUCCESS! LightRAG is now properly installed.")
            print("\n🚀 Next steps:")
            print("   1. Run: python lizzy.py")
            print("   2. Go to Buckets Manager")
            print("   3. Try 'Ingest/Reindex Bucket' - it should now work!")
            print("   4. Use 'Query Bucket' to test knowledge graph retrieval")
            
        else:
            print("❌ Installation test failed:")
            print(result.stdout)
            print(result.stderr)
            print("\n💡 You may need to restart your terminal/Python environment")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("💡 Try restarting your terminal and running 'python lizzy.py'")

if __name__ == "__main__":
    main()