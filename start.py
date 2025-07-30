#!/usr/bin/env python3
"""
Lizzy Framework - Start Module
Creates and initializes new writing projects with dedicated SQLite databases
"""

import os
import sqlite3
import sys
from datetime import datetime

def create_project_database(project_name):
    """Create a new SQLite database for the project with all required tables"""
    
    # Create projects directory if it doesn't exist
    projects_dir = "projects"
    if not os.path.exists(projects_dir):
        os.makedirs(projects_dir)
    
    # Create project-specific directory
    project_dir = os.path.join(projects_dir, project_name)
    if os.path.exists(project_dir):
        print(f"❌ Project '{project_name}' already exists!")
        return False
    
    os.makedirs(project_dir)
    
    # Create database file
    db_path = os.path.join(project_dir, f"{project_name}.sqlite")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create characters table
    cursor.execute("""
        CREATE TABLE characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT,
            age TEXT,
            romantic_challenge TEXT,
            lovable_trait TEXT,
            comedic_flaw TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create story_outline table
    cursor.execute("""
        CREATE TABLE story_outline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            act INTEGER NOT NULL,
            scene INTEGER NOT NULL,
            key_characters TEXT,
            key_events TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create brainstorming_log table
    cursor.execute("""
        CREATE TABLE brainstorming_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            act INTEGER,
            scene INTEGER,
            scene_description TEXT,
            bucket_name TEXT,
            tone_preset TEXT,
            response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create finalized_draft_v1 table (versioned)
    cursor.execute("""
        CREATE TABLE finalized_draft_v1 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            act INTEGER NOT NULL,
            scene INTEGER NOT NULL,
            final_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(act, scene)
        )
    """)
    
    # Create project_metadata table
    cursor.execute("""
        CREATE TABLE project_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert initial metadata
    cursor.execute("""
        INSERT INTO project_metadata (key, value) VALUES 
        ('project_name', ?),
        ('project_type', 'screenplay'),
        ('created_date', ?),
        ('current_version', '1')
    """, (project_name, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Project '{project_name}' created successfully!")
    print(f"📁 Database: {db_path}")
    print(f"📋 Tables created: characters, story_outline, brainstorming_log, finalized_draft_v1, project_metadata")
    
    return True

def list_existing_projects():
    """List all existing projects"""
    projects_dir = "projects"
    if not os.path.exists(projects_dir):
        print("📂 No projects directory found.")
        return []
    
    projects = []
    for entry in os.scandir(projects_dir):
        if entry.is_dir():
            db_path = os.path.join(entry.path, f"{entry.name}.sqlite")
            if os.path.exists(db_path):
                projects.append(entry.name)
    
    return projects

def main():
    """Main function for the Start module"""
    print("🎬 LIZZY FRAMEWORK - START MODULE")
    print("=" * 50)
    print("Initialize new writing projects with structured databases")
    print()
    
    # Show existing projects
    existing_projects = list_existing_projects()
    if existing_projects:
        print("📚 Existing Projects:")
        for i, project in enumerate(existing_projects, 1):
            print(f"  {i}. {project}")
        print()
    
    # Get project name from user
    while True:
        project_name = input("💭 Enter new project name (or 'quit' to exit): ").strip()
        
        if project_name.lower() == 'quit':
            print("👋 Goodbye!")
            sys.exit(0)
        
        if not project_name:
            print("❌ Project name cannot be empty!")
            continue
        
        # Sanitize project name (remove special characters)
        import re
        sanitized_name = re.sub(r'[^\w\-_]', '_', project_name)
        if sanitized_name != project_name:
            print(f"📝 Project name sanitized to: {sanitized_name}")
            project_name = sanitized_name
        
        if project_name in existing_projects:
            print(f"❌ Project '{project_name}' already exists!")
            continue
        
        break
    
    # Create the project
    success = create_project_database(project_name)
    
    if success:
        print()
        print("🚀 Next Steps:")
        print(f"   1. Run: python intake.py {project_name}")
        print("   2. Define your characters and story outline")
        print("   3. Use brainstorm.py for creative ideation")
        print("   4. Generate final drafts with write.py")
        print()
        print("💡 Tip: Each module can be run independently for iterative refinement!")

if __name__ == "__main__":
    main()