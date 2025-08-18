#!/usr/bin/env python3
"""
Direct test of the brainstorm module without full UI simulation
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

def test_brainstorm_import():
    """Test that we can import and access the brainstorm function"""
    print("🧪 Testing Direct Brainstorm Module Access")
    print("=" * 50)
    
    try:
        # Import lizzy module
        import lizzy
        
        # Check if brainstorm_module exists
        if hasattr(lizzy, 'brainstorm_module'):
            print("✅ brainstorm_module function found")
            
            # Get the function
            brainstorm_func = getattr(lizzy, 'brainstorm_module')
            print(f"✅ Function type: {type(brainstorm_func)}")
            
            # Check function signature
            import inspect
            sig = inspect.signature(brainstorm_func)
            print(f"✅ Function signature: {sig}")
            
            # Get function source and check key components
            source = inspect.getsource(brainstorm_func)
            print(f"✅ Function source length: {len(source)} chars")
            
            # Check for integration components
            components = [
                ('Prompt Studio text', 'Dynamic Prompt Studio'),
                ('Threading import', 'import threading'),  
                ('Webbrowser import', 'import webbrowser'),
                ('Server launch', 'prompt_studio_dynamic.py'),
                ('URL definition', 'localhost:8002'),
                ('Browser open call', 'webbrowser.open'),
                ('Subprocess call', 'subprocess.run')
            ]
            
            print(f"\n🔍 Checking integration components:")
            all_present = True
            for name, pattern in components:
                if pattern in source:
                    print(f"✅ {name}")
                else:
                    print(f"❌ {name}")
                    all_present = False
            
            if all_present:
                print(f"\n🎉 All integration components found!")
                print(f"✅ brainstorm_module() is properly configured")
                return True
            else:
                print(f"\n❌ Some components missing")
                return False
                
        else:
            print("❌ brainstorm_module function not found")
            return False
            
    except Exception as e:
        print(f"❌ Error importing or testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_prompt_studio_file():
    """Test that the prompt studio file exists and is accessible"""
    print(f"\n🧪 Testing Prompt Studio File Access")
    print("=" * 40)
    
    studio_file = 'prompt_studio_dynamic.py'
    
    if os.path.exists(studio_file):
        print(f"✅ {studio_file} exists")
        
        # Check file size
        size = os.path.getsize(studio_file)
        print(f"✅ File size: {size} bytes")
        
        # Check if it's executable
        if os.access(studio_file, os.R_OK):
            print(f"✅ File is readable")
        else:
            print(f"❌ File is not readable")
            return False
            
        # Try to read the first few lines
        try:
            with open(studio_file, 'r') as f:
                lines = f.readlines()[:10]
            print(f"✅ File content accessible ({len(lines)} lines read)")
            
            # Check for key markers
            content = ''.join(lines)
            if 'Flask' in content:
                print(f"✅ Flask backend detected")
            if 'app.run' in content:
                print(f"✅ Server startup code detected")
                
            return True
            
        except Exception as e:
            print(f"❌ Error reading file: {str(e)}")
            return False
    else:
        print(f"❌ {studio_file} not found")
        return False

def simulate_brainstorm_call():
    """Simulate calling the brainstorm function with proper session setup"""
    print(f"\n🧪 Testing Brainstorm Function Call Simulation")
    print("=" * 50)
    
    try:
        import lizzy
        
        # Check if we can set up a minimal session
        if hasattr(lizzy, 'session'):
            print("✅ Session object found")
            
            # Set up minimal session
            lizzy.session.current_project = 'gamma'
            lizzy.session.api_key_set = True
            print("✅ Session configured with gamma project")
            
            print(f"📋 Would call brainstorm_module() now...")
            print(f"   Current project: {lizzy.session.current_project}")
            print(f"   API key set: {lizzy.session.api_key_set}")
            
            # Note: We don't actually call it to avoid launching the server
            print(f"✅ Session setup successful - ready for brainstorm call")
            return True
            
        else:
            print(f"❌ Session object not found")
            return False
            
    except Exception as e:
        print(f"❌ Error simulating call: {str(e)}")
        return False

def main():
    """Run all direct tests"""
    print("🎯 DIRECT BRAINSTORM INTEGRATION TESTING")
    print("=" * 60)
    
    # Test 1: Import and function check
    import_ok = test_brainstorm_import()
    
    # Test 2: File access
    file_ok = test_prompt_studio_file()
    
    # Test 3: Simulate call setup
    call_ok = simulate_brainstorm_call()
    
    # Summary
    print(f"\n📊 DIRECT TEST RESULTS")
    print("=" * 30)
    
    if import_ok and file_ok and call_ok:
        print("🎉 ALL DIRECT TESTS PASSED!")
        print("✅ Integration is properly configured")
        print("✅ brainstorm_module() function ready")
        print("✅ prompt_studio_dynamic.py accessible")
        print("✅ Session setup works")
        print(f"\n🚀 Manual test procedure:")
        print("   python3 lizzy.py")
        print("   → Select 2 (Open Existing Project)")  
        print("   → Select 1 (gamma)")
        print("   → Press Enter")
        print("   → Select 2 (Brainstorm)")
        print("   → Browser should open to localhost:8002!")
    else:
        print("❌ Some direct tests failed:")
        if not import_ok:
            print("  - Function import/check failed")
        if not file_ok:
            print("  - Prompt studio file access failed")
        if not call_ok:
            print("  - Call simulation failed")

if __name__ == "__main__":
    main()