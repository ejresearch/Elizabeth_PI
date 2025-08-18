"""
Prompt Studio Backend - Integrates with TransparentBrainstormer
Provides database functions to save/load custom prompt templates
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, Optional
from lightrag import QueryParam


class PromptStudioManager:
    """Manages custom prompt templates for brainstorming with full project integration"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.project_name = os.path.basename(project_path)
        self.db_path = os.path.join(project_path, f"{self.project_name}.sqlite")
        self.setup_database()
        
        # Initialize LightRAG integration
        from lizzy_lightrag_manager import LightRAGManager
        self.lightrag_manager = LightRAGManager()
        self.lightrag_manager.load_bucket_config()
    
    def setup_database(self):
        """Setup database table for prompt templates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create prompt_configs table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompt_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_name TEXT NOT NULL,
                prompt_template TEXT NOT NULL,
                buckets TEXT DEFAULT '{"scripts": true, "plays": true, "books": true}',
                is_active BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_template(self, template_name: str, prompt_template: str, buckets: Dict[str, bool]) -> int:
        """Save a prompt template and make it active"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Deactivate all existing templates
        cursor.execute("UPDATE prompt_configs SET is_active = 0")
        
        # Insert new template as active
        cursor.execute('''
            INSERT INTO prompt_configs (template_name, prompt_template, buckets, is_active, modified_at)
            VALUES (?, ?, ?, 1, ?)
        ''', (template_name, prompt_template, json.dumps(buckets), datetime.now()))
        
        template_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return template_id
    
    def get_active_template(self) -> Optional[Dict]:
        """Get the currently active prompt template"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT template_name, prompt_template, buckets, created_at, modified_at
            FROM prompt_configs 
            WHERE is_active = 1
            ORDER BY modified_at DESC
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "template_name": result[0],
                "prompt_template": result[1],
                "buckets": json.loads(result[2]),
                "created_at": result[3],
                "modified_at": result[4]
            }
        
        return None
    
    def get_project_context(self) -> Dict:
        """Get comprehensive project context for prompt building"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        context = {
            "project_name": self.project_name,
            "characters": [],
            "scenes": [],
            "metadata": {},
            "notes": [],
            "bucket_status": {}
        }
        
        try:
            # Get all characters with rich data
            cursor.execute("""
                SELECT name, archetype, romantic_challenge, lovable_trait, comedic_flaw, notes
                FROM characters ORDER BY name
            """)
            characters = cursor.fetchall()
            context["characters"] = [{
                "name": char[0],
                "archetype": char[1] or "",
                "romantic_challenge": char[2] or "",
                "lovable_trait": char[3] or "", 
                "comedic_flaw": char[4] or "",
                "notes": char[5] or ""
            } for char in characters]
            
            # Get story outline
            cursor.execute("""
                SELECT act, scene, key_characters, key_events 
                FROM story_outline ORDER BY act, scene
            """)
            scenes = cursor.fetchall()
            context["scenes"] = [{
                "act": scene[0],
                "scene": scene[1],
                "characters": scene[2] or "",
                "events": scene[3] or ""
            } for scene in scenes]
            
            # Get extended outline if available
            cursor.execute("""
                SELECT act_number, scene_number, description, location, characters
                FROM story_outline_extended ORDER BY act_number, scene_number
            """)
            extended_scenes = cursor.fetchall()
            context["extended_scenes"] = [{
                "act": scene[0],
                "scene": scene[1], 
                "description": scene[2] or "",
                "location": scene[3] or "",
                "characters": scene[4] or ""
            } for scene in extended_scenes]
            
            # Get project metadata
            cursor.execute("SELECT key, value FROM project_metadata")
            metadata = cursor.fetchall()
            context["metadata"] = {row[0]: row[1] for row in metadata}
            
            # Get recent brainstorming history
            cursor.execute("""
                SELECT scenes_selected, bucket_selection, ai_suggestions, timestamp
                FROM brainstorming_log 
                ORDER BY timestamp DESC LIMIT 5
            """)
            history = cursor.fetchall()
            context["recent_sessions"] = [{
                "scenes": hist[0] or "",
                "buckets": hist[1] or "",
                "suggestions": hist[2] or "",
                "timestamp": hist[3]
            } for hist in history]
            
            # Get LightRAG bucket status
            context["bucket_status"] = self.get_bucket_intelligence()
            
        except Exception as e:
            print(f"⚠️ Error loading project context: {e}")
        finally:
            conn.close()
            
        return context
    
    def get_bucket_intelligence(self) -> Dict:
        """Get intelligent bucket status and recommendations"""
        bucket_info = {}
        
        try:
            # Get active buckets from LightRAG manager
            for bucket_name in self.lightrag_manager.buckets.keys():
                if bucket_name in self.lightrag_manager.active_buckets:
                    metadata = self.lightrag_manager.bucket_metadata.get(bucket_name, {})
                    bucket_info[bucket_name] = {
                        "active": True,
                        "document_count": metadata.get("document_count", 0),
                        "description": metadata.get("description", ""),
                        "last_updated": metadata.get("last_updated", "Unknown")
                    }
                    
                    # Get sample content preview
                    try:
                        rag_instance = self.lightrag_manager.buckets[bucket_name]
                        # Quick query to get sample content
                        sample_query = "romance dialogue"
                        preview = rag_instance.query(sample_query, param=QueryParam(mode="local"))
                        bucket_info[bucket_name]["content_preview"] = preview[:200] + "..."
                    except:
                        bucket_info[bucket_name]["content_preview"] = "Content available"
                        
        except Exception as e:
            print(f"⚠️ Error loading bucket intelligence: {e}")
            
        return bucket_info
    
    def get_scene_context(self, act: int, scene: int) -> Dict:
        """Get detailed context for a specific scene"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        scene_context = {
            "current_scene": {},
            "previous_scene": {},
            "characters_in_scene": [],
            "location_context": "",
            "continuity_notes": ""
        }
        
        try:
            # Get current scene
            cursor.execute("""
                SELECT key_characters, key_events 
                FROM story_outline WHERE act=? AND scene=?
            """, (act, scene))
            current = cursor.fetchone()
            if current:
                scene_context["current_scene"] = {
                    "characters": current[0] or "",
                    "events": current[1] or ""
                }
            
            # Get extended scene info
            cursor.execute("""
                SELECT description, location, characters, notes
                FROM story_outline_extended 
                WHERE act_number=? AND scene_number=?
            """, (act, scene))
            extended = cursor.fetchone()
            if extended:
                scene_context["current_scene"]["description"] = extended[0] or ""
                scene_context["location_context"] = extended[1] or ""
                scene_context["characters_in_scene"] = (extended[2] or "").split(", ")
                scene_context["continuity_notes"] = extended[3] or ""
            
            # Get previous scene for continuity
            if scene > 1:
                cursor.execute("""
                    SELECT key_events FROM story_outline 
                    WHERE act=? AND scene=?
                """, (act, scene-1))
                prev = cursor.fetchone()
                if prev:
                    scene_context["previous_scene"]["events"] = prev[0] or ""
            elif act > 1:
                # Get last scene of previous act
                cursor.execute("""
                    SELECT key_events FROM story_outline 
                    WHERE act=? ORDER BY scene DESC LIMIT 1
                """, (act-1,))
                prev = cursor.fetchone()
                if prev:
                    scene_context["previous_scene"]["events"] = prev[0] or ""
                    
            # Get character details for characters in scene
            if scene_context["characters_in_scene"]:
                placeholders = ",".join(["?" for _ in scene_context["characters_in_scene"]])
                cursor.execute(f"""
                    SELECT name, romantic_challenge, lovable_trait, comedic_flaw
                    FROM characters WHERE name IN ({placeholders})
                """, scene_context["characters_in_scene"])
                char_details = cursor.fetchall()
                scene_context["character_details"] = [{
                    "name": char[0],
                    "challenge": char[1] or "",
                    "trait": char[2] or "",
                    "flaw": char[3] or ""
                } for char in char_details]
                
        except Exception as e:
            print(f"⚠️ Error loading scene context: {e}")
        finally:
            conn.close()
            
        return scene_context
    
    def get_default_template(self) -> str:
        """Return the default Lizzy brainstorming template"""
        return """# Brainstorming with Lizzy

## General Instructions
You are **Lizzy**, an expert screenwriter specializing in romantic comedies. The goal of Brainstorm is to bring the ideas in the SQL tables to life and ground them in rich, real-world reference material from LightRAG. Treat this as a collaborative writers' room session — exploring possibilities, testing beats, and gathering inspiration for the Write phase.

## Using SQL
- **SQL is the foundation** for all brainstorming. Scene descriptions, characters, logline, and concept are the anchor points.
- From **Outline** (`story_outline`): `act`, `scene`, `key_characters`, `key_events`. These guide what must be considered.
- From **Characters** (`characters`): draw on `romantic_challenge`, `lovable_trait`, and `comedic_flaw` to shape ideas.
- Consider the scene's **position in the larger arc** — how it builds from the previous and sets up the next.

## Using LightRAG
- In Brainstorm, you **may use quotes and explicit references** from LightRAG sources.
- Purpose: surface tonal, thematic, and structural insights that feel alive, grounded, and relevant.
- **Two-Pass Strategy**:
  1. **Sequential Queries**
     - **Scripts:** find comparable moments, highlight tone, pacing, and humor beats.
     - **Plays:** uncover dramatic irony, archetypal moves, thematic resonance.
     - **Books:** extract structural principles, craft techniques, and professional writing advice.
  2. **Cross-Bucket Reflection**
     - Compare insights, remove redundancies, and integrate into a coherent set of possibilities.
- Use `mix` mode for all queries.

## Brainstorming Output Guidelines
- Output is **idea-rich, not a finished scene**.
- Suggest possible directions, setups, reversals, emotional beats, and comedic devices.
- Include concrete examples (quotes, moments, devices) from sources.
- Organize into a clear, concise "Reference Insights" section.
- Ensure the ideas respect SQL continuity and character logic.

## Scene Context
SCENE TO BRAINSTORM:
Act {context.act}, Scene {context.scene}

REQUIRED EVENTS:
{context.scene_description}

CHARACTERS IN SCENE:
{character_details}

PROJECT LOGLINE:
{logline}

PREVIOUS SCENE CONTEXT:
{previous_scene}

USER GUIDANCE:
{user_guidance}

## Output Specification
1) **SQL Snapshot (Ground Truth)** — 3–5 bullets reiterating must-hit facts from SQL.
2) **Bucket Notes — Scripts** — 3–5 items; may include short quotes with titles.
3) **Bucket Notes — Plays** — 3–5 items; may include short quotes with titles.
4) **Bucket Notes — Books** — 3–5 items; may include short quotes with titles/pages.
5) **Unified Strategy (≤ 50 words)** — one paragraph merging the above.
6) **Beat Sketch (6–10 beats)** — numbered list mapping from opening image to button; tag beats with [Tone], [Plot], or [Craft].
7) **Opportunities & Risks (max 6 bullets)** — list potential payoffs and pitfalls.
8) **Open Questions (max 5)** — crisp questions to resolve before writing.

## Brainstorming Task
Generate a set of organized, well-supported creative ideas for this scene. Focus on **possibility and inspiration**, not execution. This will give the Write phase a strong, organized mission to build from."""


# Integration function for TransparentBrainstormer
def get_brainstorm_template(project_path: str) -> str:
    """
    Get the active brainstorm template for a project.
    Used by TransparentBrainstormer.compile_prompts()
    """
    try:
        manager = PromptStudioManager(project_path)
        template_data = manager.get_active_template()
        
        if template_data:
            print(f"📝 Using custom template: {template_data['template_name']}")
            return template_data['prompt_template']
        else:
            print("📝 Using default Lizzy template")
            return manager.get_default_template()
            
    except Exception as e:
        print(f"⚠️ Error loading template, using default: {e}")
        # Return default template without trying to create manager
        return """# Brainstorming with Lizzy

## Scene Context
SCENE TO BRAINSTORM:
Act {context.act}, Scene {context.scene}

REQUIRED EVENTS:
{context.scene_description}

CHARACTERS IN SCENE:
{character_details}

PROJECT LOGLINE:
{logline}

PREVIOUS SCENE CONTEXT:
{context.previous_scene}

USER GUIDANCE:
{context.user_guidance}

## Task
Generate creative ideas for this scene using the knowledge buckets.
Focus on possibility and inspiration, not execution."""


# API endpoints for the web interface
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for web interface

@app.route('/api/project-context/<project_name>')
def get_project_context_api(project_name):
    """API endpoint to get project context"""
    project_path = f"projects/{project_name}"
    if not os.path.exists(project_path):
        return jsonify({"error": "Project not found"}), 404
        
    manager = PromptStudioManager(project_path)
    context = manager.get_project_context()
    return jsonify(context)

@app.route('/api/scene-context/<project_name>/<int:act>/<int:scene>')
def get_scene_context_api(project_name, act, scene):
    """API endpoint to get specific scene context"""
    project_path = f"projects/{project_name}"
    if not os.path.exists(project_path):
        return jsonify({"error": "Project not found"}), 404
        
    manager = PromptStudioManager(project_path)
    context = manager.get_scene_context(act, scene)
    return jsonify(context)

@app.route('/api/bucket-preview/<bucket_name>')
def get_bucket_preview(bucket_name):
    """API endpoint to preview bucket content"""
    try:
        from lizzy_lightrag_manager import LightRAGManager
        lightrag_manager = LightRAGManager()
        
        if bucket_name not in lightrag_manager.buckets:
            return jsonify({"error": "Bucket not found"}), 404
            
        # Get sample queries and metadata
        metadata = lightrag_manager.bucket_metadata.get(bucket_name, {})
        return jsonify({
            "name": bucket_name,
            "description": metadata.get("description", ""),
            "document_count": metadata.get("document_count", 0),
            "sample_entities": metadata.get("sample_entities", []),
            "last_updated": metadata.get("last_updated", "Unknown")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Launch function for integration with main system
def launch_prompt_studio(project_path: str = None, port: int = 8001):
    """Launch the prompt studio interface with API backend"""
    if project_path is None:
        project_path = input("Enter project path: ").strip()
    
    if not os.path.exists(project_path):
        print(f"❌ Project path not found: {project_path}")
        return
    
    print(f"🎬 Launching Enhanced Prompt Studio for: {os.path.basename(project_path)}")
    print(f"📁 Database: {project_path}/{os.path.basename(project_path)}.sqlite")
    print(f"🔗 Web Interface: http://localhost:8000/prompt_studio.html?project={os.path.basename(project_path)}")
    print(f"📡 API Backend: http://localhost:{port}")
    print("💾 Full project integration with characters, scenes, and LightRAG buckets")
    
    # Start the API backend
    app.run(host='0.0.0.0', port=port, debug=True)


if __name__ == "__main__":
    # Demo the integration
    demo_project = "exports/the_wrong_wedding_20250813_1253"
    if os.path.exists(demo_project):
        launch_prompt_studio(demo_project)
    else:
        launch_prompt_studio()