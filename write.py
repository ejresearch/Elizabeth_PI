#!/usr/bin/env python3
"""
Lizzy Framework - Write Module
Synthesizes brainstorming content into polished drafts
"""

import os
import sqlite3
import sys
from datetime import datetime
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_project_database(project_name):
    """Get database connection for the specified project"""
    db_path = f"projects/{project_name}/{project_name}.sqlite"
    if not os.path.exists(db_path):
        print(f" Project '{project_name}' not found!")
        return None
    return sqlite3.connect(db_path)

def get_project_context(conn):
    """Retrieve comprehensive project context from database"""
    cursor = conn.cursor()
    
    # Get characters with full details
    cursor.execute("""
        SELECT name, gender, age, romantic_challenge, lovable_trait, comedic_flaw, notes 
        FROM characters
    """)
    characters = cursor.fetchall()
    
    # Get story outline
    cursor.execute("""
        SELECT act, scene, key_characters, key_events 
        FROM story_outline 
        ORDER BY act, scene
    """)
    outline = cursor.fetchall()
    
    # Get project metadata
    cursor.execute("""
        SELECT key, value FROM project_metadata
    """)
    metadata = dict(cursor.fetchall())
    
    return {
        "characters": characters,
        "outline": outline,
        "metadata": metadata
    }

def get_brainstorm_data(conn, act=None, scene=None):
    """Retrieve brainstorming data for specific scenes or all scenes"""
    cursor = conn.cursor()
    
    if act and scene:
        # Get brainstorm data for specific scene
        cursor.execute("""
            SELECT act, scene, scene_description, bucket_name, tone_preset, response
            FROM brainstorming_log 
            WHERE act = ? AND scene = ?
            ORDER BY created_at DESC
        """, (act, scene))
    else:
        # Get all brainstorm data
        cursor.execute("""
            SELECT act, scene, scene_description, bucket_name, tone_preset, response
            FROM brainstorming_log 
            ORDER BY act, scene, created_at DESC
        """)
    
    return cursor.fetchall()

def generate_scene_draft(project_context, scene_data, brainstorm_data):
    """Generate a polished scene draft using OpenAI"""
    
    # Build character context
    characters_context = ""
    if project_context["characters"]:
        characters_context = "CHARACTERS:\n"
        for char in project_context["characters"]:
            name, gender, age, challenge, trait, flaw, notes = char
            characters_context += f"- {name}"
            if gender: characters_context += f" ({gender}"
            if age: characters_context += f", {age}"
            if gender or age: characters_context += ")"
            characters_context += f"\n  Romantic Challenge: {challenge}"
            characters_context += f"\n  Lovable Trait: {trait}"
            characters_context += f"\n  Comedic Flaw: {flaw}"
            if notes: characters_context += f"\n  Notes: {notes}"
            characters_context += "\n"
    
    # Build story context from outline
    outline_context = ""
    if project_context["outline"]:
        outline_context = "STORY OUTLINE:\n"
        for scene_outline in project_context["outline"]:
            act_num, scene_num, chars, events = scene_outline
            outline_context += f"- Act {act_num}, Scene {scene_num}: {events}"
            if chars:
                outline_context += f" (Characters: {chars})"
            outline_context += "\n"
    
    # Build brainstorm synthesis
    brainstorm_synthesis = ""
    if brainstorm_data:
        brainstorm_synthesis = "BRAINSTORMING IDEAS TO INCORPORATE:\n"
        for brainstorm in brainstorm_data:
            b_act, b_scene, desc, bucket, tone, response = brainstorm
            brainstorm_synthesis += f"\n[{bucket.upper()} - {tone}]\n{response}\n"
    
    # Get current scene info
    act, scene, key_chars, events = scene_data
    
    # Create the writing prompt
    prompt = f"""You are a professional screenwriter creating a polished screenplay scene.

{characters_context}

{outline_context}

{brainstorm_synthesis}

CURRENT SCENE TO WRITE:
Act {act}, Scene {scene}
Key Characters: {key_chars}
Key Events: {events}

Please write a complete, properly formatted screenplay scene that:
1. Uses proper screenplay format (INT./EXT., character names in caps, action lines, dialogue)
2. Incorporates the brainstorming ideas naturally and seamlessly
3. Maintains character consistency and voice
4. Advances the plot as outlined
5. Creates engaging, cinematic moments
6. Balances dialogue with action/description

Write the scene as a complete, production-ready screenplay segment. Focus on visual storytelling, authentic dialogue, and emotional resonance."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an award-winning screenwriter with expertise in romantic comedies and character-driven stories. Write in proper screenplay format."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        # Sanitize error message to prevent API key leakage
        error_msg = str(e)
        if 'api' in error_msg.lower() and ('key' in error_msg.lower() or 'auth' in error_msg.lower()):
            error_msg = "Authentication failed - please check your API key"
        print(f" OpenAI API error: {error_msg}")
        return None

def save_draft(conn, act, scene, draft_text):
    """Save the generated draft to database"""
    cursor = conn.cursor()
    
    # Use INSERT OR REPLACE to handle updates to existing scenes
    cursor.execute("""
        INSERT OR REPLACE INTO finalized_draft_v1 (act, scene, final_text)
        VALUES (?, ?, ?)
    """, (act, scene, draft_text))
    
    conn.commit()
    print(f"💾 Draft saved for Act {act}, Scene {scene}")

def view_existing_drafts(conn):
    """Display existing drafts"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT act, scene, substr(final_text, 1, 100) as preview, created_at
        FROM finalized_draft_v1 
        ORDER BY act, scene
    """)
    drafts = cursor.fetchall()
    
    if not drafts:
        print("\n No drafts written yet.")
        return
    
    print("\n EXISTING DRAFTS")
    print("=" * 50)
    for draft in drafts:
        act, scene, preview, created = draft
        print(f" Act {act}, Scene {scene} (Created: {created})")
        print(f"   Preview: {preview}...")
        print()

def write_single_scene(conn, project_name):
    """Write a single scene interactively"""
    project_context = get_project_context(conn)
    
    # Show available scenes from outline
    if project_context["outline"]:
        print("\n Available Scenes from Outline:")
        for scene_data in project_context["outline"]:
            act, scene, chars, events = scene_data
            print(f"  Act {act}, Scene {scene}: {events} (Characters: {chars})")
        print()
    
    # Get scene selection
    try:
        act = int(input("Select Act Number to write: ").strip())
        scene = int(input("Select Scene Number to write: ").strip())
    except ValueError:
        print(" Please enter valid numbers")
        return False
    
    # Find the scene in the outline
    scene_data = None
    for outline_scene in project_context["outline"]:
        if outline_scene[0] == act and outline_scene[1] == scene:
            scene_data = outline_scene
            break
    
    if not scene_data:
        print(f" Scene {act}.{scene} not found in story outline!")
        print(" Add it using: python intake.py {project_name}")
        return False
    
    # Get brainstorming data for this scene
    brainstorm_data = get_brainstorm_data(conn, act, scene)
    
    if not brainstorm_data:
        print(f"  No brainstorming data found for Act {act}, Scene {scene}")
        print(f" Run: python brainstorm.py {project_name}")
        
        continue_choice = input("Continue writing without brainstorming data? (y/n): ").strip().lower()
        if continue_choice != 'y':
            return False
        brainstorm_data = []
    else:
        print(f" Found {len(brainstorm_data)} brainstorming session(s) for this scene")
    
    # Generate the draft
    print(f"\n🤖 Generating draft for Act {act}, Scene {scene}...")
    draft_text = generate_scene_draft(project_context, scene_data, brainstorm_data)
    
    if draft_text:
        print(f"\n GENERATED DRAFT - Act {act}, Scene {scene}")
        print("=" * 60)
        print(draft_text)
        print("=" * 60)
        
        # Ask to save
        save_choice = input("\n💾 Save this draft? (y/n): ").strip().lower()
        if save_choice == 'y':
            save_draft(conn, act, scene, draft_text)
            return True
    else:
        print(" Failed to generate draft")
    
    return False

def write_full_script(conn, project_name):
    """Generate drafts for all scenes in the outline"""
    project_context = get_project_context(conn)
    
    if not project_context["outline"]:
        print(" No story outline found!")
        print(f" Add scenes using: python intake.py {project_name}")
        return
    
    print(f"\n Writing full script for {len(project_context['outline'])} scenes...")
    
    successful_scenes = 0
    failed_scenes = []
    
    for scene_data in project_context["outline"]:
        act, scene, chars, events = scene_data
        print(f"\n Writing Act {act}, Scene {scene}: {events}")
        
        # Get brainstorming data for this scene
        brainstorm_data = get_brainstorm_data(conn, act, scene)
        
        if not brainstorm_data:
            print(f"  No brainstorming data for Act {act}, Scene {scene}")
        
        # Generate draft
        draft_text = generate_scene_draft(project_context, scene_data, brainstorm_data)
        
        if draft_text:
            save_draft(conn, act, scene, draft_text)
            successful_scenes += 1
            print(f" Act {act}, Scene {scene} completed")
        else:
            failed_scenes.append(f"Act {act}, Scene {scene}")
            print(f" Failed to generate Act {act}, Scene {scene}")
    
    # Summary
    print(f"\n SCRIPT GENERATION COMPLETE")
    print("=" * 40)
    print(f" Successful: {successful_scenes} scenes")
    if failed_scenes:
        print(f" Failed: {len(failed_scenes)} scenes")
        for failed in failed_scenes:
            print(f"   - {failed}")
    
    if successful_scenes > 0:
        print(f"\n Script drafts saved to database!")
        print(f" Review and refine individual scenes as needed")

def interactive_write_menu(conn, project_name):
    """Main interactive writing menu"""
    while True:
        print(f"\n  LIZZY WRITE MODULE - Project: {project_name}")
        print("=" * 50)
        print("1. Write Single Scene")
        print("2. Write Full Script (All Scenes)")
        print("3. View Existing Drafts")
        print("4. Export Script to File")
        print("0. Exit")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            write_single_scene(conn, project_name)
        elif choice == "2":
            write_full_script(conn, project_name)
        elif choice == "3":
            view_existing_drafts(conn)
        elif choice == "4":
            export_script_to_file(conn, project_name)
        elif choice == "0":
            print(" Writing session complete!")
            break
        else:
            print(" Invalid choice. Please try again.")

def export_script_to_file(conn, project_name):
    """Export the complete script to a text file"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT act, scene, final_text
        FROM finalized_draft_v1 
        ORDER BY act, scene
    """)
    scenes = cursor.fetchall()
    
    if not scenes:
        print(" No drafts found to export!")
        return
    
    # Create export filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{project_name}_script_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"SCREENPLAY: {project_name.upper()}\n")
            f.write(f"Generated by Lizzy Framework\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            for scene in scenes:
                act, scene_num, text = scene
                f.write(f"ACT {act}, SCENE {scene_num}\n")
                f.write("-" * 30 + "\n")
                f.write(text)
                f.write("\n\n")
        
        print(f" Script exported to: {filename}")
        print(f" {len(scenes)} scenes exported")
        
    except Exception as e:
        print(f" Export failed: {e}")

def main():
    """Main function for the Write module"""
    if len(sys.argv) != 2:
        print("  LIZZY FRAMEWORK - WRITE MODULE")
        print("=" * 50)
        print("Usage: python write.py <project_name>")
        sys.exit(1)
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print(" OpenAI API key not found!")
        print(" Set your API key: export OPENAI_API_KEY=your_key_here")
        sys.exit(1)
    
    project_name = sys.argv[1]
    conn = get_project_database(project_name)
    
    if conn:
        try:
            interactive_write_menu(conn, project_name)
        finally:
            conn.close()

if __name__ == "__main__":
    main()