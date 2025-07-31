#!/usr/bin/env python3
"""
Export screenplay from agent-created project
"""

import os
import sqlite3
import json
from datetime import datetime

def export_project_screenplay(project_name):
    """Export screenplay content from a project"""
    print(f"🎬 Exporting screenplay for: {project_name}")
    
    db_path = os.path.join("projects", project_name, f"{project_name}.sqlite")
    if not os.path.exists(db_path):
        print(f"❌ Project database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get project info
        cursor.execute("SELECT key, value FROM project_metadata WHERE key IN ('template_type', 'template_name')")
        metadata = dict(cursor.fetchall())
        
        print(f"📋 Template: {metadata.get('template_name', 'Unknown')}")
        
        # Export based on template type
        if metadata.get('template_type') == 'romcom':
            export_romcom_screenplay(cursor, project_name)
        else:
            export_generic_content(cursor, project_name)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error exporting: {e}")
        return False

def export_romcom_screenplay(cursor, project_name):
    """Export romantic comedy screenplay format"""
    
    # Get characters
    cursor.execute("SELECT name, gender, age, romantic_challenge, lovable_trait, comedic_flaw FROM characters")
    characters = cursor.fetchall()
    
    # Get story outline
    cursor.execute("SELECT act, scene, key_characters, key_events FROM story_outline ORDER BY act, scene")
    scenes = cursor.fetchall()
    
    # Get notes
    cursor.execute("SELECT title, content, category FROM notes")
    notes = cursor.fetchall()
    
    # Create screenplay content
    screenplay = generate_screenplay_content(project_name, characters, scenes, notes)
    
    # Write to file
    export_dir = os.path.join("exports", project_name)
    os.makedirs(export_dir, exist_ok=True)
    
    screenplay_file = os.path.join(export_dir, f"{project_name}_screenplay.txt")
    with open(screenplay_file, 'w') as f:
        f.write(screenplay)
    
    print(f"✅ Screenplay exported: {screenplay_file}")
    
    # Also create a character sheet
    character_file = os.path.join(export_dir, f"{project_name}_characters.txt")
    with open(character_file, 'w') as f:
        f.write(generate_character_sheet(characters))
    
    print(f"✅ Character sheet exported: {character_file}")

def generate_screenplay_content(project_name, characters, scenes, notes):
    """Generate screenplay format content"""
    
    screenplay = f"""
{project_name.upper().replace('_', ' ')}

A Romantic Comedy

Created by LIZZY Autonomous Agent
Generated on {datetime.now().strftime('%B %d, %Y')}

FADE IN:

"""
    
    # Add character introductions from the data
    if characters:
        screenplay += "\n" + "="*50 + "\n"
        screenplay += "MAIN CHARACTERS\n"
        screenplay += "="*50 + "\n\n"
        
        for char in characters:
            name, gender, age, challenge, trait, flaw = char
            screenplay += f"{name.upper()}\n"
            if age and gender:
                screenplay += f"({age}, {gender})\n"
            if trait:
                screenplay += f"Lovable trait: {trait}\n"
            if flaw:
                screenplay += f"Comedic flaw: {flaw}\n"
            if challenge:
                screenplay += f"Romantic challenge: {challenge}\n"
            screenplay += "\n"
    
    # Add story scenes
    if scenes:
        screenplay += "\n" + "="*50 + "\n"
        screenplay += "STORY OUTLINE\n"
        screenplay += "="*50 + "\n\n"
        
        current_act = None
        for scene in scenes:
            act, scene_num, characters_involved, events = scene
            
            if act != current_act:
                screenplay += f"\n--- ACT {act} ---\n\n"
                current_act = act
            
            screenplay += f"Scene {act}.{scene_num}\n"
            if characters_involved:
                screenplay += f"Characters: {characters_involved}\n"
            if events:
                screenplay += f"Events: {events}\n"
            screenplay += "\n"
    
    # Add sample scene in screenplay format
    screenplay += "\n" + "="*50 + "\n"
    screenplay += "SAMPLE SCENE\n"
    screenplay += "="*50 + "\n\n"
    
    if characters and len(characters) >= 2:
        char1_name = characters[0][0]
        char2_name = characters[1][0]
        
        screenplay += f"""
INT. COFFEE SHOP - MORNING

{char1_name.upper()} enters the bustling coffee shop, looking around nervously. 
The morning rush is in full swing.

{char1_name.upper()} spots an empty table near the window and makes a beeline 
for it, not noticing {char2_name.upper()} approaching from the opposite direction.

COLLISION.

Coffee flies everywhere. Papers scatter.

                    {char1_name.upper()}
          Oh no! I'm so sorry!

                    {char2_name.upper()}
          No, that was totally my fault.
          I wasn't looking where I was going.

They both kneel to pick up the scattered papers, their hands touching 
briefly as they reach for the same document.

                    {char1_name.upper()}
          I have this amazing talent for turning
          simple tasks into disasters.

                    {char2_name.upper()}
          Well, if it helps, you just made my
          morning a lot more interesting.

They lock eyes. A moment of connection.

FADE OUT.

THE END

---

This screenplay was generated by the LIZZY Autonomous Agent
using template-based story development and AI assistance.

Characters developed from agent-populated database.
Story structure follows romantic comedy conventions.
Sample scene demonstrates character chemistry and comedic timing.
"""
    
    return screenplay

def generate_character_sheet(characters):
    """Generate character development sheet"""
    
    sheet = f"""
CHARACTER DEVELOPMENT SHEET
Generated by LIZZY Autonomous Agent
Created on {datetime.now().strftime('%B %d, %Y')}

{'='*60}

"""
    
    for i, char in enumerate(characters, 1):
        name, gender, age, challenge, trait, flaw = char
        
        sheet += f"""
CHARACTER {i}: {name.upper()}
{'-'*40}

Basic Info:
  • Name: {name}
  • Gender: {gender or 'Not specified'}
  • Age: {age or 'Not specified'}

Character Arc:
  • Lovable Trait: {trait or 'Not specified'}
  • Comedic Flaw: {flaw or 'Not specified'}
  • Romantic Challenge: {challenge or 'Not specified'}

Development Notes:
  • This character was generated by the autonomous agent
  • Traits are designed to create romantic comedy situations
  • Flaws provide opportunities for character growth
  • Challenge creates obstacles to overcome in the story

"""
    
    return sheet

def export_generic_content(cursor, project_name):
    """Export generic content for non-romcom templates"""
    
    # Get all table data
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    export_dir = os.path.join("exports", project_name)
    os.makedirs(export_dir, exist_ok=True)
    
    content_file = os.path.join(export_dir, f"{project_name}_content.txt")
    
    with open(content_file, 'w') as f:
        f.write(f"CONTENT EXPORT: {project_name.upper()}\n")
        f.write(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n")
        f.write("="*60 + "\n\n")
        
        for table in tables:
            if table != 'project_metadata':
                f.write(f"TABLE: {table.upper()}\n")
                f.write("-" * 40 + "\n")
                
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                
                # Get column names
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                for row in rows:
                    for i, value in enumerate(row):
                        if value and columns[i] not in ['id', 'created_at']:
                            f.write(f"{columns[i]}: {value}\n")
                    f.write("\n")
                f.write("\n")
    
    print(f"✅ Content exported: {content_file}")

def main():
    """Find latest project and export it"""
    
    # Find the most recent project created by the agent
    projects_dir = "projects"
    if not os.path.exists(projects_dir):
        print("❌ No projects directory found")
        return
    
    projects = []
    for item in os.listdir(projects_dir):
        project_path = os.path.join(projects_dir, item)
        if os.path.isdir(project_path):
            # Check if it's an agent-created project (has timestamp in name)
            if any(char.isdigit() for char in item[-8:]):  # Check if ends with timestamp
                projects.append(item)
    
    if not projects:
        print("❌ No agent-created projects found")
        return
    
    # Get the most recent one
    latest_project = sorted(projects)[-1]
    print(f"🎯 Found latest project: {latest_project}")
    
    # Export it
    success = export_project_screenplay(latest_project)
    
    if success:
        print(f"\n🎉 Export completed for {latest_project}")
        print(f"📁 Check the exports/{latest_project}/ directory for files")
    else:
        print("❌ Export failed")

if __name__ == "__main__":
    main()