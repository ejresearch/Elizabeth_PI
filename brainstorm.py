#!/usr/bin/env python3
"""
Lizzy Framework - Brainstorm Module
Generates creative ideas using LightRAG and OpenAI integration
"""

import os
import sqlite3
import sys
import json
from datetime import datetime
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Tone presets for different narrative styles
TONE_PRESETS = {
    "cheesy_romcom": {
        "name": "Cheesy Romcom",
        "description": "Light-hearted, predictable, with obvious romantic tropes",
        "prompt_modifier": "Write in a cheery, romantic comedy style with playful banter, meet-cute scenarios, and heartwarming moments. Use light humor and optimistic tone."
    },
    "romantic_dramedy": {
        "name": "Romantic Dramedy", 
        "description": "Balance of romance and drama with realistic characters",
        "prompt_modifier": "Write in a romantic dramedy style that balances heartfelt emotion with genuine humor. Characters should feel real and relatable, with authentic dialogue and meaningful conflicts."
    },
    "shakespearean_comedy": {
        "name": "Shakespearean Comedy",
        "description": "Witty wordplay, mistaken identities, elaborate schemes",
        "prompt_modifier": "Write in the style of Shakespearean comedy with clever wordplay, witty dialogue, mistaken identities, and elaborate romantic schemes. Use elevated language but keep it accessible."
    },
    "modern_indie": {
        "name": "Modern Indie",
        "description": "Quirky, authentic, with unconventional storytelling",
        "prompt_modifier": "Write in a modern indie film style with quirky characters, authentic dialogue, and unconventional narrative choices. Focus on subtle humor and genuine human moments."
    },
    "classic_hollywood": {
        "name": "Classic Hollywood",
        "description": "Golden age cinema with sophisticated dialogue",
        "prompt_modifier": "Write in classic Hollywood style with sophisticated, rapid-fire dialogue, glamorous settings, and timeless romantic tension reminiscent of 1940s cinema."
    },
    "academic_discovery": {
        "name": "Academic Discovery",
        "description": "Research-focused discovery for educational content",
        "prompt_modifier": """ACADEMIC CONTENT DISCOVERY AND RESEARCH PHASE

RESEARCH METHODOLOGY:
Your job is to DISCOVER and ORGANIZE the most important information from academic sources. Focus on:

1. KEY FIGURES AND INNOVATORS
   - Who were the most important people in this period?
   - What made them significant to cinema history?
   - What specific contributions did they make?

2. BREAKTHROUGH MOMENTS AND INNOVATIONS  
   - What were the major technological developments?
   - What business model innovations occurred?
   - What artistic/narrative breakthroughs happened?

3. CAUSE-AND-EFFECT RELATIONSHIPS
   - How did technical capabilities enable business opportunities?
   - How did competition drive innovation?
   - How did economic factors influence artistic development?

4. SPECIFIC EXAMPLES AND EVIDENCE
   - Concrete dates, names, and events students can anchor learning to
   - Primary source evidence and contemporary accounts
   - Technical specifications and business details

5. BROADER PATTERNS AND SIGNIFICANCE
   - How do these developments connect to larger industry changes?
   - What patterns would repeat in later periods?
   - Why does this matter for understanding cinema history?

RESEARCH OUTPUT FORMAT:
Organize findings into:
• Key People (with roles and significance)
• Major Innovations (technical, business, artistic)
• Important Events (with dates and context)
• Cause-Effect Relationships
• Primary Source Evidence
• Teaching Examples (concrete cases students can visualize)

ACADEMIC STANDARDS:
- Prioritize scholarly sources and verified historical information
- Include specific dates, names, and technical details
- Balance technical accuracy with accessibility
- Focus on developments that shaped the industry long-term"""
    }
}

def get_project_database(project_name):
    """Get database connection for the specified project"""
    db_path = f"projects/{project_name}/{project_name}.sqlite"
    if not os.path.exists(db_path):
        print(f" Project '{project_name}' not found!")
        return None
    return sqlite3.connect(db_path)

def get_project_context(conn):
    """Retrieve project context from database"""
    cursor = conn.cursor()
    
    # Get characters
    cursor.execute("SELECT name, romantic_challenge, lovable_trait, comedic_flaw FROM characters")
    characters = cursor.fetchall()
    
    # Get story outline
    cursor.execute("SELECT act, scene, key_characters, key_events FROM story_outline ORDER BY act, scene")
    outline = cursor.fetchall()
    
    return {
        "characters": characters,
        "outline": outline
    }

def setup_lightrag():
    """Initialize LightRAG with thematic buckets"""
    try:
        from lightrag import LightRAG, QueryParam
        from lightrag.llm import gpt_4o_mini_complete
        
        # Set up LightRAG working directory
        working_dir = "./lightrag_working_dir"
        
        # Initialize LightRAG instance
        rag = LightRAG(
            working_dir=working_dir,
            llm_model_func=gpt_4o_mini_complete
        )
        
        return rag
    except ImportError:
        print("  LightRAG not available. Using fallback content retrieval.")
        return None
    except Exception as e:
        print(f"  LightRAG setup failed: {e}")
        return None

def query_lightrag(rag, bucket_name, scene_context):
    """Query LightRAG for relevant content"""
    if not rag:
        return fallback_content_retrieval(bucket_name, scene_context)
    
    try:
        # Create query based on scene context and bucket
        query = f"Find relevant content for {bucket_name} about: {scene_context}"
        
        result = rag.query(query, param=QueryParam(mode="hybrid"))
        return result
    except Exception as e:
        print(f"  LightRAG query failed: {e}")
        return fallback_content_retrieval(bucket_name, scene_context)

def fallback_content_retrieval(bucket_name, scene_context):
    """Fallback content retrieval when LightRAG is unavailable"""
    fallback_content = {
        "books": "Reference classic storytelling techniques focusing on character development, three-act structure, and emotional arcs that resonate with audiences.",
        "plays": "Draw from theatrical traditions emphasizing dialogue-driven scenes, character relationships, and dramatic tension that builds naturally.",
        "scripts": "Consider contemporary screenplay conventions including scene pacing, visual storytelling, and authentic character voices that feel modern and relatable."
    }
    
    return fallback_content.get(bucket_name, "Focus on strong character motivations and clear narrative progression.")

def generate_brainstorm_content(project_context, scene_info, tone_preset, rag_content):
    """Generate brainstorming content using OpenAI"""
    
    # Build context from project data
    characters_context = ""
    if project_context["characters"]:
        characters_context = "CHARACTERS:\n"
        for char in project_context["characters"]:
            name, challenge, trait, flaw = char
            characters_context += f"- {name}: Romantic challenge: {challenge}, Lovable trait: {trait}, Comedic flaw: {flaw}\n"
    
    outline_context = ""
    if project_context["outline"]:
        outline_context = "STORY OUTLINE:\n"
        for scene in project_context["outline"]:
            act, scene_num, chars, events = scene
            outline_context += f"- Act {act}, Scene {scene_num}: {events} (Characters: {chars})\n"
    
    # Create the prompt
    prompt = f"""You are a creative writing assistant helping brainstorm ideas for a screenplay scene.

{characters_context}

{outline_context}

CURRENT SCENE: Act {scene_info['act']}, Scene {scene_info['scene']}
DESCRIPTION: {scene_info['description']}

TONE STYLE: {tone_preset['prompt_modifier']}

REFERENCE MATERIAL: {rag_content}

Please generate creative brainstorming ideas for this scene including:
1. Specific dialogue exchanges or moments
2. Visual/cinematic elements
3. Character development opportunities
4. Plot advancement suggestions
5. Emotional beats and story beats

Keep the tone consistent with the {tone_preset['name']} style. Be specific and creative, providing concrete ideas the writer can develop further."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional screenplay consultant and creative writing expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.8
        )
        
        return response.choices[0].message.content
    except Exception as e:
        # Sanitize error message to prevent API key leakage
        error_msg = str(e)
        if 'api' in error_msg.lower() and ('key' in error_msg.lower() or 'auth' in error_msg.lower()):
            error_msg = "Authentication failed - please check your API key"
        print(f" OpenAI API error: {error_msg}")
        return None

def save_brainstorm_log(conn, act, scene, description, bucket_name, tone_preset, response):
    """Save brainstorming session to database"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO brainstorming_log (act, scene, scene_description, bucket_name, tone_preset, response)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (act, scene, description, bucket_name, tone_preset, response))
    conn.commit()

def interactive_brainstorm(conn, project_name):
    """Interactive brainstorming session"""
    
    # Get project context
    project_context = get_project_context(conn)
    
    # Initialize LightRAG
    print(" Initializing LightRAG...")
    rag = setup_lightrag()
    
    # Available content buckets
    buckets = ["books", "plays", "scripts"]
    
    while True:
        print(f"\n BRAINSTORM SESSION - Project: {project_name}")
        print("=" * 50)
        
        # Get scene information
        try:
            act = int(input("Act Number: ").strip())
            scene = int(input("Scene Number: ").strip())
        except ValueError:
            print(" Please enter valid numbers for act and scene")
            continue
        
        description = input("Scene Description: ").strip()
        if not description:
            print(" Scene description is required!")
            continue
        
        # Select tone preset
        print("\n Available Tone Presets:")
        for i, (key, preset) in enumerate(TONE_PRESETS.items(), 1):
            print(f"  {i}. {preset['name']} - {preset['description']}")
        
        try:
            tone_choice = int(input("Select tone preset (number): ").strip())
            tone_key = list(TONE_PRESETS.keys())[tone_choice - 1]
            tone_preset = TONE_PRESETS[tone_key]
        except (ValueError, IndexError):
            print(" Invalid tone selection, using Romantic Dramedy")
            tone_preset = TONE_PRESETS["romantic_dramedy"]
        
        # Select content bucket
        print("\n Available Content Buckets:")
        for i, bucket in enumerate(buckets, 1):
            print(f"  {i}. {bucket}")
        
        try:
            bucket_choice = int(input("Select content bucket (number): ").strip())
            bucket_name = buckets[bucket_choice - 1]
        except (ValueError, IndexError):
            print(" Invalid bucket selection, using 'books'")
            bucket_name = "books"
        
        # Query LightRAG for relevant content
        print(f"\n Querying {bucket_name} for relevant content...")
        scene_info = {"act": act, "scene": scene, "description": description}
        rag_content = query_lightrag(rag, bucket_name, description)
        
        # Generate brainstorming content
        print("\n🤖 Generating creative ideas...")
        brainstorm_response = generate_brainstorm_content(
            project_context, scene_info, tone_preset, rag_content
        )
        
        if brainstorm_response:
            print(f"\n BRAINSTORM RESULTS - Act {act}, Scene {scene}")
            print("=" * 60)
            print(brainstorm_response)
            print("=" * 60)
            
            # Save to database
            save_brainstorm_log(conn, act, scene, description, bucket_name, 
                              tone_preset["name"], brainstorm_response)
            print(f"💾 Brainstorm session saved to database")
        else:
            print(" Failed to generate brainstorming content")
        
        # Continue or exit
        continue_choice = input("\n Continue brainstorming? (y/n): ").strip().lower()
        if continue_choice != 'y':
            print(f"\n🚀 Ready for writing!")
            print(f"   Next: python write.py {project_name}")
            break

def main():
    """Main function for the Brainstorm module"""
    if len(sys.argv) != 2:
        print(" LIZZY FRAMEWORK - BRAINSTORM MODULE")
        print("=" * 50)
        print("Usage: python brainstorm.py <project_name>")
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
            interactive_brainstorm(conn, project_name)
        finally:
            conn.close()

if __name__ == "__main__":
    main()

