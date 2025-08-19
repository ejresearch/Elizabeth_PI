"""
Template Management System for Lizzy
Handles all prompts, templates, and configurations
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


class TemplateManager:
    """Manages all templates and prompts for the Lizzy system"""
    
    def __init__(self, template_dir="templates"):
        self.template_dir = template_dir
        os.makedirs(template_dir, exist_ok=True)
        self.templates = {}
        self.active_template = None
        self.load_defaults()
    
    def load_defaults(self):
        """Load default templates"""
        self.templates = {
            "romcom": {
                "bucket_collection": "romcom_buckets",
                "buckets": ["romcom_scripts", "screenwriting_books", "shakespeare_plays"],
                "name": "Romantic Comedy Expert",
                "system_prompt": """You are an expert in romantic comedy screenwriting, 
                drawing from successful romcom scripts, writing craft knowledge, and theatrical techniques.""",
                "focus_areas": [
                    "Romantic comedy tropes and conventions",
                    "Comedic timing and physical comedy",
                    "Dialogue techniques and witty banter",
                    "Character chemistry and meet-cute moments",
                    "Three-act structure for romance",
                    "Theatrical dramatic techniques"
                ],
                "context_template": """
                Act {act}, Scene {scene}
                
                SCENE CONTEXT:
                {scene_context}
                
                CHARACTER DYNAMICS:
                {character_details}
                
                PREVIOUS SCENE:
                {previous_scene}
                
                ROMCOM FOCUS AREAS:
                {focus_areas}
                
                TASK:
                Using knowledge from successful romantic comedies, writing craft books, and theatrical techniques,
                provide specific brainstorming insights for this scene.
                """,
                "active": True,
                "weight": 1.0
            },
            "textbook": {
                "bucket_collection": "film_book_buckets", 
                "buckets": ["academic_sources", "balio_sources", "bordwell_sources", "cook_sources", "cousins_sources", "cultural_sources", "reference_sources"],
                "name": "Film Theory & Academic Expert",
                "system_prompt": """You are an expert in film theory, criticism, and academic analysis,
                drawing from authoritative film studies texts and scholarly sources.""",
                "focus_areas": [
                    "Film theory and critical analysis",
                    "Narrative structure and storytelling",
                    "Cinematic techniques and visual language",
                    "Cultural and historical context",
                    "Genre conventions and industry practices",
                    "Character development and psychology"
                ],
                "context_template": """
                Act {act}, Scene {scene}
                
                SCENE CONTEXT:
                {scene_context}
                
                CHARACTER ANALYSIS:
                {character_details}
                
                PREVIOUS SCENE:
                {previous_scene}
                
                ACADEMIC FOCUS AREAS:
                {focus_areas}
                
                TASK:
                Using film theory, academic analysis, and scholarly perspectives,
                provide theoretical framework and critical insights for this scene.
                """,
                "active": True,
                "weight": 1.0
            },
            "screenplay": {
                "bucket_collection": "screenplay_buckets",
                "buckets": ["romcom_scripts", "screenwriting_books", "shakespeare_plays"],
                "name": "Screenplay Expert",
                "system_prompt": """You are **Lizzy**, an expert screenwriter specializing in romantic comedies. The goal of Brainstorm is to bring the ideas in the SQL tables to life and ground them in rich, real-world reference material from LightRAG. Treat this as a collaborative writers' room session — exploring possibilities, testing beats, and gathering inspiration for the Write phase.""",
                "focus_areas": [
                    "Screenplay format and structure",
                    "Character development and arcs", 
                    "Romantic comedy tropes and conventions",
                    "Comedic timing and dialogue",
                    "Visual storytelling techniques",
                    "Three-act structure for screenplays",
                    "Scene transitions and pacing"
                ],
                "context_template": """
# Brainstorming with Lizzy

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
Act {act}, Scene {scene}

REQUIRED EVENTS:
{key_events}

CHARACTERS IN SCENE:
{character_details}

SCENE DESCRIPTION:
{scene_context}

## Brainstorming Task
Generate a set of organized, well-supported creative ideas for this scene. Focus on **possibility and inspiration**, not execution. This will give the Write phase a strong, organized mission to build from.
                """,
                "active": True,
                "weight": 1.0
            },
            "write": {
                "main": {
                    "name": "Screenplay Writer",
                    "system_prompt": """You are writing a Hollywood romantic comedy screenplay.
                    Style: Late 90s/early 2000s romantic comedies - genuine, witty, heartfelt.
                    Format: Standard screenplay format with scene headings, action lines, and dialogue.""",
                    "requirements": [
                        "Standard screenplay format",
                        "Natural, witty dialogue",
                        "Visual storytelling",
                        "Character authenticity",
                        "Comedic timing"
                    ],
                    "structure_template": """
                    WRITE SCENE: Act {act}, Scene {scene}
                    
                    KEY EVENTS THAT MUST HAPPEN:
                    {key_events}
                    
                    CHARACTERS IN SCENE:
                    {character_list}
                    
                    CONTINUITY FROM PREVIOUS SCENE:
                    {previous_scene_ending}
                    
                    BRAINSTORMING INSIGHTS:
                    {brainstorm_insights}
                    
                    SPECIFIC REQUIREMENTS:
                    {requirements}
                    
                    USER GUIDANCE:
                    {user_guidance}
                    
                    WRITE THE COMPLETE SCENE NOW:
                    """
                },
                "screenplay": {
                    "name": "Lizzy - Professional Screenplay Writer",
                    "system_prompt": """You are **Lizzy**, an expert screenwriter specializing in romantic comedies.
Your mission: revitalize the lost art of the rom-com — creating scripts that feel magnetic, romantic, and warm; timeless, witty, and emotionally resonant — while steering clear of formulaic, overproduced content often found on streaming services and cable movie channels.""",
                    "requirements": [
                        "Standard screenplay format",
                        "Natural, witty dialogue",
                        "Visual storytelling",
                        "Character authenticity",
                        "Comedic timing",
                        "Show don't tell philosophy"
                    ],
                    "structure_template": """
# Writing a Screenplay with Lizzy

## General Instructions

### Who You Are
You are **Lizzy**, an expert screenwriter specializing in romantic comedies.
Your mission: revitalize the lost art of the rom-com — creating scripts that feel magnetic, romantic, and warm; timeless, witty, and emotionally resonant — while steering clear of formulaic, overproduced content often found on streaming services and cable movie channels.

### Your Dataset
You have access to three curated collections:
- **Pinnacle Romantic Comedies** – Screenplays from cult classics and box-office successes that set the gold standard for the genre.
- **The Complete Works of William Shakespeare** – While the language is archaic, his structures, tropes, and archetypes remain foundational for timeless romantic storytelling.
- **Essential Screenwriting Craft Guides** – Books that focus on character arcs, comedic timing, emotional beats, and dialogue mastery.

### Using the Dataset
- Draw **tone and pacing** from the rom-com screenplays.
- Borrow **plot frameworks and thematic depth** from Shakespeare's works.
- Apply **structural discipline and craft principles** from the screenwriting guides.

## Scene Generation Workflow

When writing a scene, you must:
1. **Review** the SQL outline for act, scene, and required events.
2. **Review** the character table for relevant characters and traits.
3. **Review** the previous finalized scene for continuity.
4. **Query** each LightRAG bucket in order, gathering tonal and structural insights.
5. **Synthesize** bucket outputs into a "Reference Insights" section.
6. **Write** the complete scene in standard Hollywood screenplay format.

## Scene Context
WRITE SCENE: Act {act}, Scene {scene}

KEY EVENTS THAT MUST HAPPEN:
{key_events}

CHARACTERS IN SCENE:
{character_list}

CONTINUITY FROM PREVIOUS SCENE:
{previous_scene_ending}

BRAINSTORMING INSIGHTS:
{brainstorm_insights}

SPECIFIC REQUIREMENTS:
{requirements}

USER GUIDANCE:
{user_guidance}

WRITE THE COMPLETE SCENE NOW:
                    """
                }
            },
            "intake": {
                "character": {
                    "name": "Character Template",
                    "fields": [
                        {"name": "name", "type": "text", "required": True},
                        {"name": "gender", "type": "select", "options": ["Male", "Female", "Non-binary", "Other"]},
                        {"name": "age", "type": "number", "min": 1, "max": 120},
                        {"name": "romantic_challenge", "type": "text", "prompt": "What prevents them from finding love?"},
                        {"name": "lovable_trait", "type": "text", "prompt": "What makes them endearing?"},
                        {"name": "comedic_flaw", "type": "text", "prompt": "What quirk creates comedy?"}
                    ]
                },
                "scene": {
                    "name": "Scene Template",
                    "fields": [
                        {"name": "act", "type": "number", "required": True},
                        {"name": "scene", "type": "number", "required": True},
                        {"name": "key_characters", "type": "multiselect", "source": "characters"},
                        {"name": "key_events", "type": "textarea", "prompt": "What happens in this scene?"},
                        {"name": "location", "type": "text"},
                        {"name": "time_of_day", "type": "select", "options": ["DAY", "NIGHT", "DAWN", "DUSK"]}
                    ]
                }
            }
        }
    
    def get_template(self, category: str, name: str) -> Dict:
        """Get a specific template"""
        if category in self.templates:
            # For new style templates (romcom, textbook) the category and name are the same
            if category == name and isinstance(self.templates[category], dict):
                # Return the template data directly if it's the top-level template
                if "context_template" in self.templates[category]:
                    return self.templates[category]
            # For old style nested templates
            elif isinstance(self.templates[category], dict) and name in self.templates[category]:
                return self.templates[category][name]
        return None
    
    def update_template(self, category: str, name: str, updates: Dict):
        """Update a template with new values"""
        if category not in self.templates:
            self.templates[category] = {}
        
        if name not in self.templates[category]:
            self.templates[category][name] = {}
        
        self.templates[category][name].update(updates)
        self.save_templates()
    
    def toggle_bucket(self, bucket_name: str, active: bool):
        """Toggle a bucket on or off"""
        if "brainstorm" in self.templates and bucket_name in self.templates["brainstorm"]:
            self.templates["brainstorm"][bucket_name]["active"] = active
            return True
        return False
    
    def get_active_buckets(self) -> List[str]:
        """Get list of currently active buckets"""
        active = []
        if "brainstorm" in self.templates:
            for bucket, config in self.templates["brainstorm"].items():
                if config.get("active", False):
                    active.append(bucket)
        return active
    
    def get_bucket_collection(self, template_name: str) -> List[str]:
        """Get buckets for a specific template by collection"""
        if template_name in self.templates:
            template = self.templates[template_name]
            return template.get("buckets", [])
        return []
    
    def get_template_buckets(self, template_type: str) -> List[str]:
        """Get buckets assigned to a template type (romcom or textbook)"""
        return self.get_bucket_collection(template_type)
    
    def load_bucket_config(self, config_path: str = None):
        """Load bucket configuration from bucket_config.json"""
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), "lightrag_working_dir", "bucket_config.json")
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                bucket_config = json.load(f)
            
            # Update templates with current bucket collections
            collections = bucket_config.get("bucket_collections", {})
            
            for collection_name, collection_data in collections.items():
                template_name = collection_data.get("template")
                if template_name and template_name in self.templates:
                    self.templates[template_name]["buckets"] = collection_data["buckets"]
                    self.templates[template_name]["bucket_collection"] = collection_name
            
            return True
        return False
    
    def compile_prompt(self, category: str, template_name: str, context: Dict) -> str:
        """Compile a template with context into a final prompt"""
        template = self.get_template(category, template_name)
        if not template:
            return ""
        
        # Get the appropriate template string
        if category in ["brainstorm", "romcom", "textbook"]:
            prompt_template = template.get("context_template", "")
        elif category == "write":
            prompt_template = template.get("structure_template", "")
        else:
            return ""
        
        # Format with context
        try:
            # Add focus areas if present
            if "focus_areas" in template:
                context["focus_areas"] = "\n".join(f"- {area}" for area in template["focus_areas"])
            
            # Add requirements if present
            if "requirements" in template:
                context["requirements"] = "\n".join(f"- {req}" for req in template["requirements"])
            
            prompt = prompt_template.format(**context)
            
            # Add system prompt if present
            if "system_prompt" in template:
                prompt = template["system_prompt"] + "\n\n" + prompt
            
            return prompt
        except KeyError as e:
            return f"Error: Missing context key {e}"
    
    def save_templates(self):
        """Save templates to disk"""
        filepath = os.path.join(self.template_dir, "templates.json")
        with open(filepath, 'w') as f:
            json.dump(self.templates, f, indent=2)
    
    def load_templates(self):
        """Load templates from disk"""
        filepath = os.path.join(self.template_dir, "templates.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                self.templates = json.load(f)
    
    def create_custom_template(self, category: str, name: str, template_data: Dict):
        """Create a new custom template"""
        if category not in self.templates:
            self.templates[category] = {}
        
        self.templates[category][name] = {
            "name": template_data.get("name", name),
            "system_prompt": template_data.get("system_prompt", ""),
            "context_template": template_data.get("context_template", ""),
            "focus_areas": template_data.get("focus_areas", []),
            "active": template_data.get("active", True),
            "weight": template_data.get("weight", 1.0),
            "created_at": datetime.now().isoformat(),
            "custom": True
        }
        
        self.save_templates()
        return True
    
    def get_template_preview(self, category: str, template_name: str, sample_context: Dict = None) -> str:
        """Get a preview of how a template will look with sample data"""
        if not sample_context:
            sample_context = {
                "act": 1,
                "scene": 1,
                "scene_context": "Sarah meets Jake at a coffee shop",
                "character_details": "Sarah (28, Female): Afraid of commitment\nJake (30, Male): Workaholic",
                "previous_scene": "Opening montage of the city",
                "key_events": "Accidental meeting leads to spilled coffee",
                "character_list": "SARAH, JAKE, BARISTA",
                "previous_scene_ending": "Sarah rushes into the coffee shop",
                "brainstorm_insights": "Focus on awkward chemistry",
                "user_guidance": "Make it funny but genuine"
            }
        
        return self.compile_prompt(category, template_name, sample_context)
    
    def export_template_config(self) -> Dict:
        """Export complete template configuration"""
        return {
            "templates": self.templates,
            "active_buckets": self.get_active_buckets(),
            "export_date": datetime.now().isoformat()
        }
    
    def import_template_config(self, config: Dict):
        """Import template configuration"""
        if "templates" in config:
            self.templates = config["templates"]
            self.save_templates()
            return True
        return False
    
    def create_project_from_template(self, project_name: str, template_key: str) -> bool:
        """Create a new project using a specified template"""
        import sqlite3
        
        # Map template keys to template files
        template_map = {
            "screenplay": "romcom_extended.json",  # Use romcom as default for screenplays
            "romcom": "romcom_extended.json",
            "textbook": "textbook.json"
        }
        
        template_file = template_map.get(template_key, "romcom_extended.json")
        template_path = os.path.join("templates", template_file)
        
        if not os.path.exists(template_path):
            print(f"Template file not found: {template_path}")
            return False
        
        try:
            # Load template configuration
            with open(template_path, 'r') as f:
                template_config = json.load(f)
            
            # Create project directory
            project_dir = os.path.join("projects", project_name)
            os.makedirs(project_dir, exist_ok=True)
            
            # Create database
            db_path = os.path.join(project_dir, f"{project_name}.sqlite")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create tables from template
            tables = template_config.get("tables", {})
            for table_name, table_config in tables.items():
                fields = table_config.get("fields", {})
                
                # Build CREATE TABLE statement
                field_definitions = []
                for field_name, field_type in fields.items():
                    field_definitions.append(f"{field_name} {field_type}")
                
                create_statement = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        {', '.join(field_definitions)}
                    )
                """
                cursor.execute(create_statement)
                
                # Initialize with default data if template mode
                self._populate_template_data(cursor, table_name, table_config, template_config)
            
            conn.commit()
            conn.close()
            
            print(f"✅ Project '{project_name}' created successfully with {template_key} template")
            return True
            
        except Exception as e:
            print(f"❌ Error creating project: {e}")
            return False
    
    def _populate_template_data(self, cursor, table_name: str, table_config: Dict, template_config: Dict):
        """Populate table with template data based on initialization settings"""
        initialization = template_config.get("initialization", {})
        
        # Handle character template population
        if table_name == "characters" and "character_options" in initialization:
            default_data = table_config.get("default_data", {})
            template_characters = default_data.get("template", [])
            
            if template_characters:
                for char_data in template_characters:
                    # Build INSERT statement for character template
                    fields = list(char_data.keys())
                    placeholders = ["?" for _ in fields]
                    values = [char_data[field] for field in fields]
                    
                    insert_statement = f"""
                        INSERT INTO characters ({', '.join(fields)})
                        VALUES ({', '.join(placeholders)})
                    """
                    cursor.execute(insert_statement, values)
        
        # Handle story outline template population
        elif table_name == "story_outline_extended" and "outline_options" in initialization:
            default_data = table_config.get("default_data", {})
            template_outline = default_data.get("template", [])
            
            if template_outline:
                scene_counter = 1
                for beat_data in template_outline:
                    act = beat_data["act"]
                    act_number = beat_data["act_number"]
                    beat = beat_data["beat"]
                    scenes = beat_data.get("scenes", [])
                    
                    for scene_data in scenes:
                        insert_statement = """
                            INSERT INTO story_outline_extended 
                            (act, act_number, beat, scene_number, description, status)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """
                        cursor.execute(insert_statement, (
                            act,
                            act_number,
                            beat,
                            scene_counter,
                            scene_data["description"],
                            "placeholder"
                        ))
                        scene_counter += 1
                
                # Add outline metadata (only if the table exists)
                try:
                    cursor.execute("""
                        INSERT INTO outline_metadata (outline_mode, template_used, total_scenes, acts_structure)
                        VALUES (?, ?, ?, ?)
                    """, (
                        "template",
                        "romcom_default",
                        scene_counter - 1,
                        json.dumps({"acts": 3, "structure": "romcom"})
                    ))
                except Exception:
                    # outline_metadata table doesn't exist, skip it
                    pass
        
        # Handle notes template population
        elif table_name == "notes":
            default_data = table_config.get("default_data", {})
            template_notes = default_data.get("template", [])
            
            if template_notes:
                for note_data in template_notes:
                    insert_statement = """
                        INSERT INTO notes (title, content, category)
                        VALUES (?, ?, ?)
                    """
                    cursor.execute(insert_statement, (
                        note_data["title"],
                        note_data["content"],
                        note_data["category"]
                    ))


class PromptInspector:
    """Tool to inspect and debug prompts in real-time"""
    
    def __init__(self, template_manager: TemplateManager):
        self.template_manager = template_manager
        self.history = []
    
    def inspect_prompt(self, category: str, template_name: str, context: Dict) -> Dict:
        """Inspect a prompt compilation step by step"""
        inspection = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "template_name": template_name,
            "input_context": context,
            "template_used": self.template_manager.get_template(category, template_name),
            "compiled_prompt": self.template_manager.compile_prompt(category, template_name, context),
            "active_buckets": self.template_manager.get_active_buckets() if category == "brainstorm" else [],
            "steps": []
        }
        
        # Track compilation steps
        template = inspection["template_used"]
        if template:
            inspection["steps"].append({
                "step": "Load Template",
                "detail": f"Loaded {template.get('name', template_name)}"
            })
            
            if "system_prompt" in template:
                inspection["steps"].append({
                    "step": "Add System Prompt",
                    "detail": template["system_prompt"][:100] + "..."
                })
            
            if "focus_areas" in template:
                inspection["steps"].append({
                    "step": "Add Focus Areas",
                    "detail": template["focus_areas"]
                })
            
            inspection["steps"].append({
                "step": "Insert Context",
                "detail": f"Filled {len(context)} context variables"
            })
        
        self.history.append(inspection)
        return inspection
    
    def get_history(self) -> List[Dict]:
        """Get inspection history"""
        return self.history
    
    def compare_templates(self, category: str, template1: str, template2: str, context: Dict) -> Dict:
        """Compare two template outputs side by side"""
        return {
            "template1": {
                "name": template1,
                "output": self.template_manager.compile_prompt(category, template1, context)
            },
            "template2": {
                "name": template2,
                "output": self.template_manager.compile_prompt(category, template2, context)
            },
            "context_used": context
        }


# Utility functions for template management
def initialize_templates() -> TemplateManager:
    """Initialize the template system"""
    tm = TemplateManager()
    
    # Check if custom templates exist
    template_file = os.path.join(tm.template_dir, "templates.json")
    if os.path.exists(template_file):
        tm.load_templates()
        print("✅ Loaded existing templates")
    else:
        tm.save_templates()
        print("✅ Created default templates")
    
    return tm


def demo_template_usage():
    """Demonstrate template usage"""
    tm = initialize_templates()
    inspector = PromptInspector(tm)
    
    print("\n" + "="*60)
    print("TEMPLATE SYSTEM DEMO")
    print("="*60)
    
    # Show active buckets
    print(f"\n📚 Active Buckets: {', '.join(tm.get_active_buckets())}")
    
    # Demo context
    context = {
        "act": 1,
        "scene": 2,
        "scene_context": "Coffee shop, morning rush",
        "character_details": "Sarah (28): Commitment-phobic artist\nJake (30): Workaholic lawyer",
        "previous_scene": "Sarah's morning routine",
        "key_events": "Accidental meeting, coffee spill, awkward flirtation"
    }
    
    # Show prompt compilation
    print("\n📝 Brainstorm Prompt (Scripts Bucket):")
    print("-"*40)
    prompt = tm.compile_prompt("brainstorm", "scripts", context)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    
    # Inspect the prompt
    print("\n🔍 Prompt Inspection:")
    print("-"*40)
    inspection = inspector.inspect_prompt("brainstorm", "scripts", context)
    for step in inspection["steps"]:
        print(f"  → {step['step']}: {step['detail'][:100] if len(step['detail']) > 100 else step['detail']}")
    
    # Toggle a bucket
    print("\n⚡ Toggling 'plays' bucket off...")
    tm.toggle_bucket("plays", False)
    print(f"📚 Active Buckets: {', '.join(tm.get_active_buckets())}")
    
    print("\n✨ Template system ready!")


if __name__ == "__main__":
    demo_template_usage()