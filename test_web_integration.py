#!/usr/bin/env python3
"""
Test script to demonstrate the web editor integration
"""

import os
import sys
from web_server import launch_web_editor

def main():
    """Test the web editor integration"""
    
    print("🧪 Testing Lizzy Web Editor Integration")
    print("=" * 50)
    
    # Check for gamma project
    project_path = "projects/gamma"
    
    if not os.path.exists(project_path):
        print("❌ Gamma project not found")
        print("💡 To test the full integration:")
        print("   1. Run: python lizzy.py")
        print("   2. Create a new project called 'gamma'")
        print("   3. Then run this test again")
        return
    
    print(f"✅ Found project: {project_path}")
    print()
    print("🌐 Starting Modern Web Editor...")
    print("🚀 This simulates what happens when you choose 'Edit Tables' in Lizzy")
    print("📱 Your browser should open automatically")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    try:
        # Launch with auto browser opening
        launch_web_editor(project_path, port=8080, auto_open=True)
    except KeyboardInterrupt:
        print("\n✅ Web server stopped")
        print("🔄 In real Lizzy, you'd return to the workflow menu now")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()