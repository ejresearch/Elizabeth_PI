#!/usr/bin/env python3
"""
Simple launcher for the Beta project table editor
"""
import sys
import os

# Add the tools directory to the path
sys.path.append('tools')

from polished_table_editor import PolishedTableEditor

if __name__ == "__main__":
    project_path = "projects/Beta"
    if os.path.exists(project_path):
        print(f"Launching table editor for Beta project...")
        print(f"Project path: {os.path.abspath(project_path)}")
        editor = PolishedTableEditor(project_path)
        editor.launch()
    else:
        print(f"Error: Beta project not found at {project_path}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Available directories: {os.listdir('.')}")