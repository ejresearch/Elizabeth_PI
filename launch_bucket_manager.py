#!/usr/bin/env python3
"""
Direct launcher for the smooth bucket manager
"""
import os
import webbrowser

def launch_bucket_manager():
    """Launch the smooth bucket manager interface"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_file = os.path.join(current_dir, "lizzy_smooth_bucket_manager.html")
    
    if os.path.exists(html_file):
        print("🚀 Launching Smooth Bucket Manager...")
        print("🌐 Opening in your default web browser...")
        
        webbrowser.open(f"file://{html_file}")
        
        print("✅ Bucket Manager launched successfully!")
        print(f"📂 File: {html_file}")
        
        return True
    else:
        print(f"❌ HTML file not found: {html_file}")
        return False

if __name__ == "__main__":
    launch_bucket_manager()