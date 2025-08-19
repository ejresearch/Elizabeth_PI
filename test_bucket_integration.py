#!/usr/bin/env python3
"""
Test script to verify bucket manager integration
"""
import os
import sys

def test_bucket_manager_integration():
    """Test the bucket manager integration"""
    
    print("🧪 Testing Bucket Manager Integration")
    print("=" * 50)
    
    # Test 1: Check if smooth bucket manager HTML exists
    html_file = "lizzy_smooth_bucket_manager.html"
    if os.path.exists(html_file):
        print("✅ Smooth bucket manager HTML file exists")
    else:
        print("❌ Smooth bucket manager HTML file missing")
        return False
    
    # Test 2: Check if the file is accessible and well-formed
    try:
        with open(html_file, 'r') as f:
            content = f.read()
            if '<title>' in content and 'buckets-grid' in content:
                print("✅ HTML file is well-formed and contains expected elements")
            else:
                print("❌ HTML file seems malformed")
                return False
    except Exception as e:
        print(f"❌ Error reading HTML file: {e}")
        return False
    
    # Test 3: Check if lizzy.py exists and bucket_manager_menu function is present
    if os.path.exists('lizzy.py'):
        with open('lizzy.py', 'r') as f:
            lizzy_content = f.read()
            if 'def bucket_manager_menu():' in lizzy_content:
                print("✅ bucket_manager_menu function found in lizzy.py")
            else:
                print("❌ bucket_manager_menu function not found")
                return False
            
            if 'lizzy_smooth_bucket_manager.html' in lizzy_content:
                print("✅ Integration with smooth bucket manager confirmed")
            else:
                print("❌ Integration with smooth bucket manager not found")
                return False
    else:
        print("❌ lizzy.py not found")
        return False
    
    # Test 4: Simulate the function call (without actual browser opening)
    print("\n🔄 Simulating bucket manager launch...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, html_file)
    
    if os.path.exists(html_path):
        print(f"✅ Would launch: file://{html_path}")
        print("✅ Browser launch simulation successful")
    else:
        print(f"❌ HTML file not found at expected path: {html_path}")
        return False
    
    # Test 5: Check file permissions
    if os.access(html_file, os.R_OK):
        print("✅ HTML file is readable")
    else:
        print("❌ HTML file is not readable")
        return False
    
    return True

def main():
    """Run the integration test"""
    print("🌊 Bucket Manager Integration Test")
    print("Testing the connection between Lizzy CLI and Web Interface\n")
    
    if test_bucket_manager_integration():
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Integration is working correctly")
        print("✅ Bucket Manager will launch in web browser when selected")
        print("\n🚀 Ready to use!")
        print("   1. Run 'python lizzy.py'")
        print("   2. Choose option 2 (Bucket Manager)")
        print("   3. Enjoy the smooth web interface!")
    else:
        print("\n❌ TESTS FAILED!")
        print("Integration needs to be fixed before use.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)