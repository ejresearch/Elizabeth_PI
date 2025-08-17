#!/usr/bin/env python3
"""
Quick launcher for the web-based project editor
"""

import os
import sys
from web_server import launch_web_editor

def main():
    """Launch the web editor for testing"""
    
    # Check for gamma project
    project_path = "projects/gamma"
    
    if not os.path.exists(project_path):
        print("❌ Gamma project not found. Please create it first using lizzy.py")
        return
    
    print("🌐 Launching Lizzy Web Editor")
    print("🚀 Project: gamma")
    print("📝 Opening browser to: http://localhost:8080")
    print()
    
    try:
        launch_web_editor(project_path, port=8080)
    except KeyboardInterrupt:
        print("\n✅ Web server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()