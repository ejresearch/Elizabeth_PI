#!/usr/bin/env python3
"""
Database initialization script for Miranda Reference Backup
Creates the required database tables for all projects
"""

import sqlite3
import os
import sys

def create_tables(db_path):
    """Create all required tables in the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create characters table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT,
            age TEXT,
            romantic_challenge TEXT,
            lovable_trait TEXT,
            comedic_flaw TEXT,
            notes TEXT
        )
    """)
    
    # Create story_outline table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS story_outline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            act INTEGER NOT NULL,
            scene INTEGER NOT NULL,
            key_characters TEXT,
            key_events TEXT
        )
    """)
    
    # Create brainstorming_log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS brainstorming_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            act INTEGER,
            scene INTEGER,
            scene_description TEXT,
            bucket_name TEXT,
            response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create finalized_draft_3 table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS finalized_draft_3 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            act INTEGER NOT NULL,
            scene INTEGER NOT NULL,
            final_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(act, scene)
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized: {db_path}")

def main():
    """Initialize all project databases"""
    projects_dir = "projects"
    
    if not os.path.exists(projects_dir):
        print(f"Projects directory '{projects_dir}' not found")
        return
    
    initialized_count = 0
    
    # Initialize existing project databases
    for project_name in os.listdir(projects_dir):
        project_path = os.path.join(projects_dir, project_name)
        if os.path.isdir(project_path):
            db_path = os.path.join(project_path, f"{project_name}.sqlite")
            if os.path.exists(db_path):
                create_tables(db_path)
                initialized_count += 1
    
    if initialized_count == 0:
        print("No project databases found to initialize")
    else:
        print(f"🎉 Initialized {initialized_count} project database(s)")

if __name__ == "__main__":
    main()