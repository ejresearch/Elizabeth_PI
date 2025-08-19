#!/usr/bin/env python3
"""
Quick test script for LightRAG Explorer
"""

import sys
import os
import subprocess
import time
import webbrowser

def test_lightrag_explorer():
    """Test if the LightRAG Explorer can be launched"""
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_file = os.path.join(current_dir, "bucket_alt", "web_lightrag_server.py")
    
    print(f"🔍 Testing LightRAG Explorer...")
    print(f"📁 Server file: {server_file}")
    print(f"✅ File exists: {os.path.exists(server_file)}")
    
    if os.path.exists(server_file):
        print(f"🚀 Starting LightRAG Explorer server...")
        
        try:
            # Start server in background
            server_process = subprocess.Popen(
                [sys.executable, server_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.join(current_dir, "bucket_alt")  # Change working directory
            )
            
            # Give it a moment to start
            time.sleep(2)
            
            # Check if process is running
            if server_process.poll() is None:
                print(f"✅ Server started successfully!")
                print(f"🌐 Open http://localhost:8001 in your browser")
                print(f"🛑 Press Ctrl+C to stop the server")
                
                # Wait for user to stop
                try:
                    server_process.wait()
                except KeyboardInterrupt:
                    print(f"\n🛑 Stopping server...")
                    server_process.terminate()
                    server_process.wait()
                    print(f"✅ Server stopped")
            else:
                stdout, stderr = server_process.communicate()
                print(f"❌ Server failed to start")
                print(f"Output: {stdout.decode()}")
                print(f"Error: {stderr.decode()}")
                
        except Exception as e:
            print(f"❌ Error starting server: {e}")
    else:
        print(f"❌ Server file not found")

if __name__ == "__main__":
    test_lightrag_explorer()