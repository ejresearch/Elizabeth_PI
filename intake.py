#!/usr/bin/env python3
"""
Lizzy Framework - Intake Module
Captures essential story elements and foundational metadata
"""

import os
import sqlite3
import sys
from datetime import datetime

def get_project_database(project_name):
    """Get database connection for the specified project"""
    db_path = f"projects/{project_name}/{project_name}.sqlite"
    if not os.path.exists(db_path):
        print(f" Project '{project_name}' not found!")
        print(" Run 'python start.py' to create a new project")
        return None
    return sqlite3.connect(db_path)

def input_character(conn, project_name):
    """Interactive character input"""
    print("\n CHARACTER INTAKE")
    print("-" * 20)
    
    name = input("Character Name: ").strip()
    if not name:
        print(" Character name is required!")
        return False
    
    gender = input("Gender (optional): ").strip()
    age = input("Age (optional): ").strip()
    romantic_challenge = input("Romantic Challenge: ").strip()
    lovable_trait = input("Lovable Trait: ").strip()
    comedic_flaw = input("Comedic Flaw: ").strip()
    notes = input("Additional Notes: ").strip()
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO characters (name, gender, age, romantic_challenge, lovable_trait, comedic_flaw, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, gender, age, romantic_challenge, lovable_trait, comedic_flaw, notes))
    
    conn.commit()
    print(f" Character '{name}' added successfully!")
    return True

def input_scene(conn, project_name):
    """Interactive scene outline input"""
    print("\n SCENE OUTLINE INTAKE")
    print("-" * 25)
    
    try:
        act = int(input("Act Number: ").strip())
        scene = int(input("Scene Number: ").strip())
    except ValueError:
        print(" Act and Scene must be numbers!")
        return False
    
    key_characters = input("Key Characters (comma-separated): ").strip()
    key_events = input("Key Events: ").strip()
    
    if not key_events:
        print(" Key events are required!")
        return False
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO story_outline (act, scene, key_characters, key_events)
        VALUES (?, ?, ?, ?)
    """, (act, scene, key_characters, key_events))
    
    conn.commit()
    print(f" Scene {act}.{scene} added successfully!")
    return True

def view_characters(conn):
    """Display all characters"""
    cursor = conn.cursor()
    cursor.execute("SELECT name, gender, age, romantic_challenge, lovable_trait, comedic_flaw FROM characters")
    characters = cursor.fetchall()
    
    if not characters:
        print("\n No characters defined yet.")
        return
    
    print("\n👥 CURRENT CHARACTERS")
    print("=" * 50)
    for char in characters:
        name, gender, age, challenge, trait, flaw = char
        print(f" {name}")
        if gender: print(f"   Gender: {gender}")
        if age: print(f"   Age: {age}")
        if challenge: print(f"   Romantic Challenge: {challenge}")
        if trait: print(f"   Lovable Trait: {trait}")
        if flaw: print(f"   Comedic Flaw: {flaw}")
        print()

def view_outline(conn):
    """Display story outline"""
    cursor = conn.cursor()
    cursor.execute("SELECT act, scene, key_characters, key_events FROM story_outline ORDER BY act, scene")
    scenes = cursor.fetchall()
    
    if not scenes:
        print("\n No story outline defined yet.")
        return
    
    print("\n STORY OUTLINE")
    print("=" * 40)
    current_act = None
    for scene_data in scenes:
        act, scene, characters, events = scene_data
        if act != current_act:
            print(f"\n ACT {act}")
            print("-" * 15)
            current_act = act
        
        print(f"  Scene {scene}: {events}")
        if characters:
            print(f"    Characters: {characters}")
        print()

def interactive_menu(conn, project_name):
    """Main interactive menu"""
    while True:
        print(f"\n LIZZY INTAKE - Project: {project_name}")
        print("=" * 50)
        print("1. Add Character")
        print("2. Add Scene Outline")
        print("3. View Characters")
        print("4. View Story Outline")
        print("5. Project Summary")
        print("6. Exit to Brainstorm Module")
        print("0. Quit")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            input_character(conn, project_name)
        elif choice == "2":
            input_scene(conn, project_name)
        elif choice == "3":
            view_characters(conn)
        elif choice == "4":
            view_outline(conn)
        elif choice == "5":
            print(f"\n PROJECT SUMMARY: {project_name}")
            print("=" * 40)
            view_characters(conn)
            view_outline(conn)
        elif choice == "6":
            print(f"\n🚀 Ready for brainstorming!")
            print(f"   Next: python brainstorm.py {project_name}")
            break
        elif choice == "0":
            print(" Goodbye!")
            break
        else:
            print(" Invalid choice. Please try again.")

def main():
    """Main function for the Intake module"""
    if len(sys.argv) != 2:
        print(" LIZZY FRAMEWORK - INTAKE MODULE")
        print("=" * 50)
        print("Usage: python intake.py <project_name>")
        print("\n Available Projects:")
        
        # List available projects
        if os.path.exists("projects"):
            projects = []
            for entry in os.scandir("projects"):
                if entry.is_dir():
                    db_path = os.path.join(entry.path, f"{entry.name}.sqlite")
                    if os.path.exists(db_path):
                        projects.append(entry.name)
            
            if projects:
                for i, project in enumerate(projects, 1):
                    print(f"  {i}. {project}")
                print(f"\nExample: python intake.py {projects[0]}")
            else:
                print("  No projects found.")
                print("   Run 'python start.py' to create a new project")
        else:
            print("  No projects found.")
            print("   Run 'python start.py' to create a new project")
        
        sys.exit(1)
    
    project_name = sys.argv[1]
    conn = get_project_database(project_name)
    
    if conn:
        try:
            interactive_menu(conn, project_name)
        finally:
            conn.close()

if __name__ == "__main__":
    main()