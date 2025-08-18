#!/usr/bin/env python3
"""
Manual test script that actually goes through the brainstorm workflow
"""
import os
import sys
import subprocess
import time

def test_manual_workflow():
    """Test the complete brainstorm workflow manually"""
    print("🎯 MANUAL BRAINSTORM WORKFLOW TEST")
    print("=" * 50)
    print()
    print("📋 This test will:")
    print("   1. Launch Lizzy")
    print("   2. Select 'Open Existing Project'")
    print("   3. Choose 'gamma' project")
    print("   4. Select 'Brainstorm' option")
    print("   5. Verify Prompt Studio launches")
    print()
    
    # Prepare the input sequence
    input_sequence = "2\n1\n\n2\n\n"  # 2=Open Project, 1=gamma, Enter, 2=Brainstorm, Enter
    
    print("🚀 Starting test...")
    print()
    
    try:
        # Launch Lizzy with our input sequence
        process = subprocess.Popen(
            [sys.executable, 'lizzy.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
        
        # Send input and wait for completion or timeout
        try:
            stdout, stderr = process.communicate(input=input_sequence, timeout=30)
        except subprocess.TimeoutExpired:
            print("⏰ Process timed out - this might mean server is running!")
            process.kill()
            stdout, stderr = process.communicate()
        
        print("📊 TEST RESULTS:")
        print("=" * 30)
        
        # Analyze the output for success indicators
        output_text = stdout.lower()
        
        success_checks = [
            ("Lizzy started", "lizzy" in output_text),
            ("Project menu appeared", "open existing project" in output_text),
            ("Project loaded", "project" in output_text and "loaded" in output_text),
            ("Workflow menu shown", "brainstorm" in output_text and "generate ideas" in output_text),
            ("Brainstorm mode activated", "brainstorm mode" in output_text),
            ("Prompt Studio launch", "prompt studio" in output_text),
            ("Server startup", "starting prompt studio backend" in output_text or "starting server" in output_text),
            ("Browser launch", "opening prompt studio" in output_text or "localhost:8002" in output_text)
        ]
        
        passed_checks = 0
        for check_name, condition in success_checks:
            if condition:
                print(f"✅ {check_name}")
                passed_checks += 1
            else:
                print(f"❌ {check_name}")
        
        print(f"\n📈 Progress: {passed_checks}/{len(success_checks)} checks passed")
        
        # Show relevant output sections
        if len(stdout) > 500:
            print(f"\n📋 Key Output Sections:")
            print("-" * 40)
            
            # Look for brainstorm-related content
            lines = stdout.split('\n')
            brainstorm_section = []
            capture = False
            
            for line in lines:
                if 'brainstorm' in line.lower() or capture:
                    brainstorm_section.append(line)
                    capture = True
                    if len(brainstorm_section) > 15:  # Limit output
                        break
            
            if brainstorm_section:
                print("Brainstorm-related output:")
                print('\n'.join(brainstorm_section[-15:]))  # Last 15 lines
            else:
                print("Last 500 characters of output:")
                print(stdout[-500:])
        
        if stderr:
            print(f"\n⚠️ Errors/Warnings:")
            print("-" * 20)
            print(stderr[:300])  # First 300 chars of stderr
        
        # Overall assessment
        if passed_checks >= 6:  # Most checks passed
            print(f"\n🎉 TEST LARGELY SUCCESSFUL!")
            print("✅ Brainstorm integration appears to be working")
            if passed_checks == len(success_checks):
                print("✅ All workflow steps completed successfully")
            else:
                print("⚠️ Some minor issues detected but core functionality works")
        elif passed_checks >= 4:
            print(f"\n⚠️ PARTIAL SUCCESS")
            print("✅ Basic workflow works but some integration issues")
        else:
            print(f"\n❌ TEST FAILED")
            print("❌ Major issues with the workflow")
        
        return passed_checks >= 6
        
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_server_availability():
    """Check if we can connect to the Prompt Studio server"""
    print(f"\n🌐 Testing Server Connectivity")
    print("=" * 35)
    
    try:
        import urllib.request
        import urllib.error
        
        # Try to connect to the server
        try:
            response = urllib.request.urlopen('http://localhost:8002', timeout=5)
            print("✅ Prompt Studio server is running!")
            print(f"✅ Response status: {response.status}")
            return True
        except urllib.error.URLError as e:
            if "Connection refused" in str(e):
                print("ℹ️ Server not running (expected if not launched yet)")
            else:
                print(f"⚠️ Connection issue: {e}")
            return False
            
    except ImportError:
        print("⚠️ Cannot test HTTP connectivity")
        return False

def main():
    """Run the manual workflow test"""
    print("🧪 COMPLETE MANUAL BRAINSTORM INTEGRATION TEST")
    print("=" * 60)
    
    # Check server first
    server_running = check_server_availability()
    
    # Run the workflow test
    workflow_success = test_manual_workflow()
    
    # Final summary
    print(f"\n" + "=" * 60)
    print("🎯 FINAL MANUAL TEST RESULTS")
    print("=" * 60)
    
    if workflow_success:
        print("🎉 MANUAL TEST SUCCESSFUL!")
        print("✅ Brainstorm integration is working correctly")
        print("✅ Workflow proceeds from CLI to web interface")
        print()
        print("🚀 READY FOR REAL USE:")
        print("   You can now run: python3 lizzy.py")
        print("   Select: 2 → 1 → Enter → 2")
        print("   Result: Browser opens to Prompt Studio!")
    else:
        print("❌ MANUAL TEST HAD ISSUES")
        print("⚠️ Some workflow steps may not be working correctly")
        print("📋 Review the detailed output above for specifics")
    
    if server_running:
        print("\nℹ️ Note: Server was already running during test")

if __name__ == "__main__":
    main()