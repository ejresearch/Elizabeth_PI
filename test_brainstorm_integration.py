#!/usr/bin/env python3
"""
Test script to verify the brainstorm integration works properly
"""
import os
import sys
import subprocess
import time
import webbrowser

def test_prompt_studio_launch():
    """Test launching the prompt studio"""
    print("🧪 Testing Prompt Studio Integration")
    print("=" * 50)
    
    # Check if prompt_studio_dynamic.py exists
    if not os.path.exists('prompt_studio_dynamic.py'):
        print("❌ prompt_studio_dynamic.py not found")
        return False
    
    print("✅ prompt_studio_dynamic.py found")
    
    # Test launching the server
    print("🚀 Testing server launch...")
    
    try:
        # Launch server in background
        process = subprocess.Popen([
            sys.executable, 'prompt_studio_dynamic.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment
        time.sleep(2)
        
        # Check if process is running
        if process.poll() is None:
            print("✅ Server started successfully")
            
            # Test opening browser (simulate)
            studio_url = "http://localhost:8002"
            print(f"✅ Would open browser to: {studio_url}")
            
            # Terminate test server
            process.terminate()
            print("✅ Server terminated cleanly")
            
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start")
            print(f"stdout: {stdout.decode()}")
            print(f"stderr: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing server: {str(e)}")
        return False

def test_lizzy_integration():
    """Test that lizzy.py has the correct brainstorm_module function"""
    print("\n🧪 Testing Lizzy Integration")
    print("=" * 50)
    
    try:
        # Read lizzy.py and check for the updated brainstorm_module
        with open('lizzy.py', 'r') as f:
            content = f.read()
            
        # Check for key components
        checks = [
            ('brainstorm_module function', 'def brainstorm_module():'),
            ('Prompt Studio launch', 'Dynamic Prompt Studio'),
            ('webbrowser import', 'import webbrowser'),
            ('subprocess launch', 'prompt_studio_dynamic.py'),
            ('URL opening', 'http://localhost:8002')
        ]
        
        for name, pattern in checks:
            if pattern in content:
                print(f"✅ {name} found")
            else:
                print(f"❌ {name} missing")
                return False
                
        print("✅ All integration components found")
        return True
        
    except Exception as e:
        print(f"❌ Error checking lizzy.py: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🎯 Testing Brainstorm -> Prompt Studio Integration")
    print("=" * 60)
    
    # Test 1: Prompt Studio launch
    studio_ok = test_prompt_studio_launch()
    
    # Test 2: Lizzy integration
    lizzy_ok = test_lizzy_integration()
    
    # Summary
    print("\n📊 Test Results")
    print("=" * 30)
    
    if studio_ok and lizzy_ok:
        print("🎉 All tests passed!")
        print("✅ Brainstorm integration is working correctly")
        print("\nTo test manually:")
        print("1. Run: python3 lizzy.py")
        print("2. Select or create a project")
        print("3. Choose option '2' (Brainstorm)")
        print("4. Browser should open to Prompt Studio")
    else:
        print("❌ Some tests failed")
        if not studio_ok:
            print("  - Prompt Studio launch issues")
        if not lizzy_ok:
            print("  - Lizzy integration issues")

if __name__ == "__main__":
    main()