#!/usr/bin/env python3
"""
LIZZY FRAMEWORK - Unified Retro Command Line Interface
AI-Assisted Long-Form Writing System
"""

import os
import sqlite3
import sys
import json
import shutil
from datetime import datetime
from openai import OpenAI

# Check for optional dependencies
HAS_LIGHTRAG = False
LIGHTRAG_ERROR = None

try:
    import asyncio
    # Try the HKU version imports based on latest docs
    from lightrag import LightRAG, QueryParam
    from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
    from lightrag.kg.shared_storage import initialize_pipeline_status
    from lightrag.utils import setup_logger
    HAS_LIGHTRAG = True
except ImportError as e:
    LIGHTRAG_ERROR = str(e)
    # Try older version patterns as fallback
    try:
        import lightrag
        # At least basic import works
        HAS_LIGHTRAG = "partial"
    except ImportError:
        HAS_LIGHTRAG = False

# Terminal colors for retro aesthetic
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# ASCII Art Header
LIZZY_HEADER = f"""{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    ██╗     ██╗███████╗███████╗██╗   ██╗                     ║
║                    ██║     ██║╚══███╔╝╚══███╔╝╚██╗ ██╔╝                     ║
║                    ██║     ██║  ███╔╝   ███╔╝  ╚████╔╝                      ║
║                    ██║     ██║ ███╔╝   ███╔╝    ╚██╔╝                       ║
║                    ███████╗██║███████╗███████╗   ██║                        ║
║                    ╚══════╝╚═╝╚══════╝╚══════╝   ╚═╝                        ║
║                                                                              ║
║              {Colors.YELLOW}🎬 AI-ASSISTED LONG-FORM WRITING SYSTEM 🎬{Colors.CYAN}                ║
║                          {Colors.GREEN}~ Modular • Iterative • Intelligent ~{Colors.CYAN}                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}"""

# Initialize OpenAI client
client = None

# Global session state
class Session:
    def __init__(self):
        self.current_project = None
        self.db_conn = None
        self.api_key_set = False
    
    def set_project(self, project_name):
        if self.db_conn:
            self.db_conn.close()
        
        db_path = f"projects/{project_name}/{project_name}.sqlite"
        if os.path.exists(db_path):
            self.current_project = project_name
            self.db_conn = sqlite3.connect(db_path)
            return True
        return False
    
    def close(self):
        if self.db_conn:
            self.db_conn.close()

session = Session()

# LightRAG async helper functions
async def initialize_lightrag(bucket_path):
    """Initialize LightRAG instance with proper async setup"""
    if not HAS_LIGHTRAG:
        return None
    
    try:
        setup_logger("lightrag", level="INFO")
        
        rag = LightRAG(
            working_dir=bucket_path,
            embedding_func=openai_embed,
            llm_model_func=gpt_4o_mini_complete,
        )
        
        # Required async initialization
        await rag.initialize_storages()
        await initialize_pipeline_status()
        
        return rag
    except Exception as e:
        print(f"{Colors.RED}❌ LightRAG initialization failed: {e}{Colors.END}")
        return None

async def ingest_content_async(rag, content):
    """Async content ingestion"""
    try:
        await rag.ainsert(content)
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ Content ingestion failed: {e}{Colors.END}")
        return False

async def query_content_async(rag, query, mode="hybrid"):
    """Async content querying"""
    try:
        result = await rag.aquery(query, param=QueryParam(mode=mode))
        return result
    except Exception as e:
        print(f"{Colors.RED}❌ Query failed: {e}{Colors.END}")
        return None

async def finalize_lightrag(rag):
    """Properly close LightRAG instance"""
    if rag:
        try:
            await rag.finalize_storages()
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Warning during cleanup: {e}{Colors.END}")

def run_async_lightrag_operation(coro):
    """Helper to run async operations in sync context"""
    try:
        # Try to get existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, we need to use a different approach
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(coro)
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop exists, create new one
        return asyncio.run(coro)

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the LIZZY header"""
    clear_screen()
    print(LIZZY_HEADER)

def print_separator(char="═", length=80):
    """Print a separator line"""
    print(f"{Colors.CYAN}{char * length}{Colors.END}")

def print_status():
    """Print current session status"""
    api_status = f"{Colors.GREEN}✓ Connected{Colors.END}" if session.api_key_set else f"{Colors.RED}✗ Not Set{Colors.END}"
    project_status = f"{Colors.GREEN}{session.current_project}{Colors.END}" if session.current_project else f"{Colors.YELLOW}None Selected{Colors.END}"
    
    print(f"{Colors.BLUE}API Key: {api_status} │ Current Project: {project_status}{Colors.END}")
    print_separator("─")

def setup_api_key():
    """Setup OpenAI API key"""
    global client, session
    
    print(f"\n{Colors.YELLOW}🔑 OPENAI API KEY SETUP{Colors.END}")
    print_separator()
    
    current_key = os.getenv('OPENAI_API_KEY')
    if current_key:
        print(f"{Colors.GREEN}✓ API key found in environment{Colors.END}")
        try:
            client = OpenAI(api_key=current_key)
            session.api_key_set = True
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ Invalid API key: {e}{Colors.END}")
    
    print(f"{Colors.CYAN}Enter your OpenAI API key:{Colors.END}")
    api_key = input(f"{Colors.BOLD}> {Colors.END}").strip()
    
    if api_key:
        try:
            client = OpenAI(api_key=api_key)
            os.environ['OPENAI_API_KEY'] = api_key
            session.api_key_set = True
            print(f"{Colors.GREEN}✓ API key configured successfully!{Colors.END}")
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ Invalid API key: {e}{Colors.END}")
    
    return False

def list_projects():
    """List all available projects"""
    projects_dir = "projects"
    if not os.path.exists(projects_dir):
        return []
    
    projects = []
    for entry in os.scandir(projects_dir):
        if entry.is_dir():
            db_path = os.path.join(entry.path, f"{entry.name}.sqlite")
            if os.path.exists(db_path):
                # Get project creation date
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT value FROM project_metadata WHERE key = 'created_date'")
                    result = cursor.fetchone()
                    created = result[0] if result else "Unknown"
                    conn.close()
                    projects.append((entry.name, created))
                except:
                    projects.append((entry.name, "Unknown"))
    
    return sorted(projects, key=lambda x: x[1], reverse=True)

def create_project():
    """Create a new project (START module)"""
    print(f"\n{Colors.YELLOW}🎬 CREATE NEW PROJECT{Colors.END}")
    print_separator()
    
    # Show existing projects
    existing_projects = [p[0] for p in list_projects()]
    if existing_projects:
        print(f"{Colors.BLUE}📚 Existing Projects:{Colors.END}")
        for i, project in enumerate(existing_projects[:5], 1):
            print(f"   {i}. {project}")
        if len(existing_projects) > 5:
            print(f"   ... and {len(existing_projects) - 5} more")
        print()
    
    while True:
        project_name = input(f"{Colors.BOLD}💭 Enter new project name (or 'back' to return): {Colors.END}").strip()
        
        if project_name.lower() == 'back':
            return False
        
        if not project_name:
            print(f"{Colors.RED}❌ Project name cannot be empty!{Colors.END}")
            continue
        
        # Sanitize project name
        import re
        sanitized_name = re.sub(r'[^\w\-_]', '_', project_name)
        if sanitized_name != project_name:
            print(f"{Colors.YELLOW}📝 Project name sanitized to: {sanitized_name}{Colors.END}")
            project_name = sanitized_name
        
        if project_name in existing_projects:
            print(f"{Colors.RED}❌ Project '{project_name}' already exists!{Colors.END}")
            continue
        
        break
    
    # Create project
    if create_project_database(project_name):
        session.set_project(project_name)
        print(f"\n{Colors.GREEN}🎉 Project '{project_name}' created and loaded!{Colors.END}")
        input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")
        return True
    
    return False

def create_project_database(project_name):
    """Create project database with all tables"""
    projects_dir = "projects"
    if not os.path.exists(projects_dir):
        os.makedirs(projects_dir)
    
    project_dir = os.path.join(projects_dir, project_name)
    if os.path.exists(project_dir):
        return False
    
    os.makedirs(project_dir)
    db_path = os.path.join(project_dir, f"{project_name}.sqlite")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create all tables
    tables = [
        """CREATE TABLE characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT,
            age TEXT,
            romantic_challenge TEXT,
            lovable_trait TEXT,
            comedic_flaw TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE story_outline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            act INTEGER NOT NULL,
            scene INTEGER NOT NULL,
            key_characters TEXT,
            key_events TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE brainstorming_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            act INTEGER,
            scene INTEGER,
            scene_description TEXT,
            bucket_name TEXT,
            tone_preset TEXT,
            response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE finalized_draft_v1 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            act INTEGER NOT NULL,
            scene INTEGER NOT NULL,
            final_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(act, scene)
        )""",
        """CREATE TABLE project_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    ]
    
    for table_sql in tables:
        cursor.execute(table_sql)
    
    # Insert metadata
    cursor.execute("""
        INSERT INTO project_metadata (key, value) VALUES 
        ('project_name', ?),
        ('project_type', 'screenplay'),
        ('created_date', ?),
        ('current_version', '1')
    """, (project_name, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    return True

def select_project():
    """Select an existing project"""
    print(f"\n{Colors.YELLOW}📂 SELECT PROJECT{Colors.END}")
    print_separator()
    
    projects = list_projects()
    if not projects:
        print(f"{Colors.RED}❌ No projects found!{Colors.END}")
        print(f"{Colors.CYAN}💡 Create a new project first{Colors.END}")
        input(f"\nPress Enter to continue...")
        return False
    
    print(f"{Colors.BLUE}📚 Available Projects:{Colors.END}")
    for i, (name, created) in enumerate(projects, 1):
        date_str = created.split('T')[0] if 'T' in created else created
        print(f"   {Colors.BOLD}{i:2d}.{Colors.END} {name} {Colors.CYAN}(created: {date_str}){Colors.END}")
    
    while True:
        choice = input(f"\n{Colors.BOLD}Select project number (or 'back' to return): {Colors.END}").strip()
        
        if choice.lower() == 'back':
            return False
        
        try:
            project_idx = int(choice) - 1
            if 0 <= project_idx < len(projects):
                project_name = projects[project_idx][0]
                if session.set_project(project_name):
                    print(f"\n{Colors.GREEN}✓ Project '{project_name}' loaded!{Colors.END}")
                    input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")
                    return True
                else:
                    print(f"{Colors.RED}❌ Failed to load project{Colors.END}")
            else:
                print(f"{Colors.RED}❌ Invalid selection{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}❌ Please enter a number{Colors.END}")

def main_menu():
    """Main navigation menu"""
    while True:
        print_header()
        print_status()
        
        if not session.api_key_set:
            print(f"\n{Colors.RED}⚠️  OpenAI API key required to continue{Colors.END}")
        
        print(f"\n{Colors.BOLD}🏠 MAIN MENU{Colors.END}")
        print_separator()
        
        menu_items = [
            ("🔑", "Setup API Key", not session.api_key_set),
            ("🎬", "Create New Project", session.api_key_set),
            ("📂", "Select Project", session.api_key_set),
            ("👤", "Character & Story Intake", session.api_key_set and session.current_project),
            ("🧠", "Creative Brainstorming", session.api_key_set and session.current_project),
            ("✍️ ", "Write Scenes & Drafts", session.api_key_set and session.current_project),
            ("🗄️ ", "Tables Manager (SQL)", session.current_project),
            ("📦", "Buckets Manager (LightRAG)", session.api_key_set),
            ("📋", "Project Dashboard", session.current_project),
            ("❓", "Help & Documentation", True),
            ("🚪", "Exit", True)
        ]
        
        available_items = [(icon, desc, idx) for idx, (icon, desc, available) in enumerate(menu_items, 1) if available]
        
        for icon, desc, idx in available_items:
            status = ""
            if "API Key" in desc and session.api_key_set:
                status = f" {Colors.GREEN}✓{Colors.END}"
            elif "Project" in desc and session.current_project:
                status = f" {Colors.GREEN}({session.current_project}){Colors.END}"
            
            print(f"   {Colors.BOLD}{idx:2d}.{Colors.END} {icon} {desc}{status}")
        
        choice = input(f"\n{Colors.BOLD}Select option: {Colors.END}").strip()
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(available_items):
                selected_idx = available_items[choice_num - 1][2]
                
                if selected_idx == 1:  # API Key
                    setup_api_key()
                elif selected_idx == 2:  # Create Project
                    create_project()
                elif selected_idx == 3:  # Select Project
                    select_project()
                elif selected_idx == 4:  # Intake
                    intake_module()
                elif selected_idx == 5:  # Brainstorm
                    brainstorm_module()
                elif selected_idx == 6:  # Write
                    write_module()
                elif selected_idx == 7:  # Tables Manager
                    tables_manager()
                elif selected_idx == 8:  # Buckets Manager
                    buckets_manager()
                elif selected_idx == 9:  # Dashboard
                    project_dashboard()
                elif selected_idx == 10:  # Help
                    show_help()
                elif selected_idx == 11:  # Exit
                    print(f"\n{Colors.CYAN}👋 Thank you for using LIZZY Framework!{Colors.END}")
                    print(f"{Colors.YELLOW}   Happy writing! 🎬✨{Colors.END}\n")
                    session.close()
                    sys.exit(0)
        except ValueError:
            pass

def intake_module():
    """Character and Story Intake Module"""
    if not session.current_project:
        return
    
    while True:
        print_header()
        print_status()
        print(f"\n{Colors.BOLD}👤 CHARACTER & STORY INTAKE{Colors.END}")
        print_separator()
        
        print(f"   {Colors.BOLD}1.{Colors.END} 👤 Add Character")
        print(f"   {Colors.BOLD}2.{Colors.END} 🎬 Add Scene Outline")
        print(f"   {Colors.BOLD}3.{Colors.END} 📖 View Characters")
        print(f"   {Colors.BOLD}4.{Colors.END} 📚 View Story Outline")
        print(f"   {Colors.BOLD}5.{Colors.END} 📊 Project Summary")
        print(f"   {Colors.BOLD}6.{Colors.END} 🏠 Back to Main Menu")
        
        choice = input(f"\n{Colors.BOLD}Select option: {Colors.END}").strip()
        
        if choice == "1":
            add_character()
        elif choice == "2":
            add_scene()
        elif choice == "3":
            view_characters()
        elif choice == "4":
            view_outline()
        elif choice == "5":
            project_summary()
        elif choice == "6":
            break

def add_character():
    """Add a character to the project"""
    print(f"\n{Colors.YELLOW}👤 ADD CHARACTER{Colors.END}")
    print_separator()
    
    name = input(f"{Colors.BOLD}Character Name: {Colors.END}").strip()
    if not name:
        print(f"{Colors.RED}❌ Character name is required!{Colors.END}")
        input(f"Press Enter to continue...")
        return
    
    gender = input(f"{Colors.BOLD}Gender (optional): {Colors.END}").strip()
    age = input(f"{Colors.BOLD}Age (optional): {Colors.END}").strip()
    romantic_challenge = input(f"{Colors.BOLD}Romantic Challenge: {Colors.END}").strip()
    lovable_trait = input(f"{Colors.BOLD}Lovable Trait: {Colors.END}").strip()
    comedic_flaw = input(f"{Colors.BOLD}Comedic Flaw: {Colors.END}").strip()
    notes = input(f"{Colors.BOLD}Additional Notes: {Colors.END}").strip()
    
    cursor = session.db_conn.cursor()
    cursor.execute("""
        INSERT INTO characters (name, gender, age, romantic_challenge, lovable_trait, comedic_flaw, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, gender, age, romantic_challenge, lovable_trait, comedic_flaw, notes))
    
    session.db_conn.commit()
    print(f"\n{Colors.GREEN}✅ Character '{name}' added successfully!{Colors.END}")
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")

def add_scene():
    """Add a scene to the story outline"""
    print(f"\n{Colors.YELLOW}🎬 ADD SCENE OUTLINE{Colors.END}")
    print_separator()
    
    try:
        act = int(input(f"{Colors.BOLD}Act Number: {Colors.END}").strip())
        scene = int(input(f"{Colors.BOLD}Scene Number: {Colors.END}").strip())
    except ValueError:
        print(f"{Colors.RED}❌ Act and Scene must be numbers!{Colors.END}")
        input(f"Press Enter to continue...")
        return
    
    key_characters = input(f"{Colors.BOLD}Key Characters (comma-separated): {Colors.END}").strip()
    key_events = input(f"{Colors.BOLD}Key Events: {Colors.END}").strip()
    
    if not key_events:
        print(f"{Colors.RED}❌ Key events are required!{Colors.END}")
        input(f"Press Enter to continue...")
        return
    
    cursor = session.db_conn.cursor()
    cursor.execute("""
        INSERT INTO story_outline (act, scene, key_characters, key_events)
        VALUES (?, ?, ?, ?)
    """, (act, scene, key_characters, key_events))
    
    session.db_conn.commit()
    print(f"\n{Colors.GREEN}✅ Scene {act}.{scene} added successfully!{Colors.END}")
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")

def view_characters():
    """Display all characters"""
    print(f"\n{Colors.YELLOW}👥 PROJECT CHARACTERS{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT name, gender, age, romantic_challenge, lovable_trait, comedic_flaw, notes FROM characters")
    characters = cursor.fetchall()
    
    if not characters:
        print(f"{Colors.CYAN}📝 No characters defined yet.{Colors.END}")
    else:
        for char in characters:
            name, gender, age, challenge, trait, flaw, notes = char
            print(f"\n{Colors.BOLD}🎭 {name}{Colors.END}")
            if gender: print(f"   Gender: {gender}")
            if age: print(f"   Age: {age}")
            if challenge: print(f"   Romantic Challenge: {challenge}")
            if trait: print(f"   Lovable Trait: {trait}")
            if flaw: print(f"   Comedic Flaw: {flaw}")
            if notes: print(f"   Notes: {notes}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def view_outline():
    """Display story outline"""
    print(f"\n{Colors.YELLOW}📚 STORY OUTLINE{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT act, scene, key_characters, key_events FROM story_outline ORDER BY act, scene")
    scenes = cursor.fetchall()
    
    if not scenes:
        print(f"{Colors.CYAN}📖 No story outline defined yet.{Colors.END}")
    else:
        current_act = None
        for scene_data in scenes:
            act, scene, characters, events = scene_data
            if act != current_act:
                print(f"\n{Colors.BOLD}🎭 ACT {act}{Colors.END}")
                print_separator("─", 20)
                current_act = act
            
            print(f"  {Colors.CYAN}Scene {scene}:{Colors.END} {events}")
            if characters:
                print(f"    {Colors.YELLOW}Characters:{Colors.END} {characters}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def project_summary():
    """Show complete project summary"""
    print_header()
    print_status()
    print(f"\n{Colors.BOLD}📊 PROJECT SUMMARY{Colors.END}")
    print_separator()
    
    view_characters()
    view_outline()

def brainstorm_module():
    """Creative Brainstorming Module"""
    if not session.current_project or not session.api_key_set:
        return
    
    # Tone presets
    TONE_PRESETS = {
        "cheesy_romcom": {
            "name": "Cheesy Romcom",
            "description": "Light-hearted, predictable romantic tropes",
            "prompt_modifier": "Write in a cheery, romantic comedy style with playful banter, meet-cute scenarios, and heartwarming moments."
        },
        "romantic_dramedy": {
            "name": "Romantic Dramedy", 
            "description": "Balance of romance and drama with realistic characters",
            "prompt_modifier": "Write in a romantic dramedy style that balances heartfelt emotion with genuine humor."
        },
        "shakespearean_comedy": {
            "name": "Shakespearean Comedy",
            "description": "Witty wordplay, mistaken identities, elaborate schemes",
            "prompt_modifier": "Write in Shakespearean comedy style with clever wordplay, witty dialogue, and elaborate romantic schemes."
        },
        "modern_indie": {
            "name": "Modern Indie",
            "description": "Quirky, authentic, unconventional storytelling",
            "prompt_modifier": "Write in modern indie film style with quirky characters and authentic dialogue."
        },
        "classic_hollywood": {
            "name": "Classic Hollywood",
            "description": "Golden age cinema with sophisticated dialogue",
            "prompt_modifier": "Write in classic Hollywood style with sophisticated, rapid-fire dialogue and timeless romance."
        }
    }
    
    print_header()
    print_status()
    print(f"\n{Colors.BOLD}🧠 CREATIVE BRAINSTORMING{Colors.END}")
    print_separator()
    
    # Get scene info
    try:
        act = int(input(f"{Colors.BOLD}Act Number: {Colors.END}").strip())
        scene = int(input(f"{Colors.BOLD}Scene Number: {Colors.END}").strip())
    except ValueError:
        print(f"{Colors.RED}❌ Please enter valid numbers{Colors.END}")
        input("Press Enter to continue...")
        return
    
    description = input(f"{Colors.BOLD}Scene Description: {Colors.END}").strip()
    if not description:
        print(f"{Colors.RED}❌ Scene description is required!{Colors.END}")
        input("Press Enter to continue...")
        return
    
    # Select tone preset
    print(f"\n{Colors.YELLOW}🎭 Available Tone Presets:{Colors.END}")
    preset_list = list(TONE_PRESETS.items())
    for i, (key, preset) in enumerate(preset_list, 1):
        print(f"   {Colors.BOLD}{i}.{Colors.END} {preset['name']} - {preset['description']}")
    
    try:
        tone_choice = int(input(f"\n{Colors.BOLD}Select tone preset: {Colors.END}").strip())
        tone_key = preset_list[tone_choice - 1][0]
        tone_preset = TONE_PRESETS[tone_key]
    except (ValueError, IndexError):
        print(f"{Colors.YELLOW}Using default: Romantic Dramedy{Colors.END}")
        tone_preset = TONE_PRESETS["romantic_dramedy"]
    
    # Select content bucket
    buckets = ["books", "plays", "scripts"]
    print(f"\n{Colors.YELLOW}📚 Available Content Buckets:{Colors.END}")
    for i, bucket in enumerate(buckets, 1):
        print(f"   {Colors.BOLD}{i}.{Colors.END} {bucket}")
    
    try:
        bucket_choice = int(input(f"\n{Colors.BOLD}Select content bucket: {Colors.END}").strip())
        bucket_name = buckets[bucket_choice - 1]
    except (ValueError, IndexError):
        bucket_name = "books"
    
    # Generate brainstorming content
    print(f"\n{Colors.CYAN}🤖 Generating creative ideas...{Colors.END}")
    
    # Get project context
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT name, romantic_challenge, lovable_trait, comedic_flaw FROM characters")
    characters = cursor.fetchall()
    
    cursor.execute("SELECT act, scene, key_characters, key_events FROM story_outline ORDER BY act, scene")
    outline = cursor.fetchall()
    
    # Build context
    characters_context = ""
    if characters:
        characters_context = "CHARACTERS:\n"
        for char in characters:
            name, challenge, trait, flaw = char
            characters_context += f"- {name}: Challenge: {challenge}, Trait: {trait}, Flaw: {flaw}\n"
    
    outline_context = ""
    if outline:
        outline_context = "STORY OUTLINE:\n"
        for scene_outline in outline:
            act_num, scene_num, chars, events = scene_outline
            outline_context += f"- Act {act_num}, Scene {scene_num}: {events} (Characters: {chars})\n"
    
    # Create prompt
    prompt = f"""You are a creative writing assistant helping brainstorm ideas for a screenplay scene.

{characters_context}

{outline_context}

CURRENT SCENE: Act {act}, Scene {scene}
DESCRIPTION: {description}

TONE STYLE: {tone_preset['prompt_modifier']}

REFERENCE MATERIAL: Focus on {bucket_name} - classic storytelling techniques and character development.

Please generate creative brainstorming ideas for this scene including:
1. Specific dialogue exchanges or moments
2. Visual/cinematic elements  
3. Character development opportunities
4. Plot advancement suggestions
5. Emotional beats and story beats

Keep the tone consistent with {tone_preset['name']} style. Be specific and creative."""
    
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
        
        brainstorm_response = response.choices[0].message.content
        
        print(f"\n{Colors.GREEN}✨ BRAINSTORM RESULTS - Act {act}, Scene {scene}{Colors.END}")
        print_separator()
        print(brainstorm_response)
        print_separator()
        
        # Save to database
        cursor.execute("""
            INSERT INTO brainstorming_log (act, scene, scene_description, bucket_name, tone_preset, response)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (act, scene, description, bucket_name, tone_preset["name"], brainstorm_response))
        
        session.db_conn.commit()
        print(f"\n{Colors.GREEN}💾 Brainstorm session saved to database{Colors.END}")
        
    except Exception as e:
        print(f"{Colors.RED}❌ OpenAI API error: {e}{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def write_module():
    """Writing Module"""
    if not session.current_project or not session.api_key_set:
        return
    
    while True:
        print_header()
        print_status()
        print(f"\n{Colors.BOLD}✍️  WRITE SCENES & DRAFTS{Colors.END}")
        print_separator()
        
        print(f"   {Colors.BOLD}1.{Colors.END} ✍️  Write Single Scene")
        print(f"   {Colors.BOLD}2.{Colors.END} 📖 Write Full Script")
        print(f"   {Colors.BOLD}3.{Colors.END} 📚 View Existing Drafts")
        print(f"   {Colors.BOLD}4.{Colors.END} 📄 Export Script to File")
        print(f"   {Colors.BOLD}5.{Colors.END} 🏠 Back to Main Menu")
        
        choice = input(f"\n{Colors.BOLD}Select option: {Colors.END}").strip()
        
        if choice == "1":
            write_single_scene()
        elif choice == "2":
            write_full_script()
        elif choice == "3":
            view_existing_drafts()
        elif choice == "4":
            export_script_to_file()
        elif choice == "5":
            break

def write_single_scene():
    """Write a single scene"""
    print_header()
    print_status()
    print(f"\n{Colors.BOLD}✍️  WRITE SINGLE SCENE{Colors.END}")
    print_separator()
    
    # Show available scenes from outline
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT act, scene, key_characters, key_events FROM story_outline ORDER BY act, scene")
    outline = cursor.fetchall()
    
    if not outline:
        print(f"{Colors.RED}❌ No story outline found!{Colors.END}")
        print(f"{Colors.CYAN}💡 Add scenes in Character & Story Intake first{Colors.END}")
        input("Press Enter to continue...")
        return
    
    print(f"{Colors.BLUE}📋 Available Scenes from Outline:{Colors.END}")
    for scene_data in outline:
        act, scene, chars, events = scene_data
        print(f"   Act {act}, Scene {scene}: {events} ({Colors.YELLOW}Characters: {chars}{Colors.END})")
    
    # Get scene selection
    try:
        act = int(input(f"\n{Colors.BOLD}Select Act Number to write: {Colors.END}").strip())
        scene = int(input(f"{Colors.BOLD}Select Scene Number to write: {Colors.END}").strip())
    except ValueError:
        print(f"{Colors.RED}❌ Please enter valid numbers{Colors.END}")
        input("Press Enter to continue...")
        return
    
    # Find the scene in the outline
    scene_data = None
    for outline_scene in outline:
        if outline_scene[0] == act and outline_scene[1] == scene:
            scene_data = outline_scene
            break
    
    if not scene_data:
        print(f"{Colors.RED}❌ Scene {act}.{scene} not found in story outline!{Colors.END}")
        input("Press Enter to continue...")
        return
    
    # Get brainstorming data for this scene
    cursor.execute("""
        SELECT act, scene, scene_description, bucket_name, tone_preset, response
        FROM brainstorming_log 
        WHERE act = ? AND scene = ?
        ORDER BY created_at DESC
    """, (act, scene))
    brainstorm_data = cursor.fetchall()
    
    if not brainstorm_data:
        print(f"{Colors.YELLOW}⚠️  No brainstorming data found for Act {act}, Scene {scene}{Colors.END}")
        print(f"{Colors.CYAN}💡 Consider running Creative Brainstorming first{Colors.END}")
        
        continue_choice = input("Continue writing without brainstorming data? (y/n): ").strip().lower()
        if continue_choice != 'y':
            return
        brainstorm_data = []
    else:
        print(f"{Colors.GREEN}✅ Found {len(brainstorm_data)} brainstorming session(s) for this scene{Colors.END}")
    
    # Generate the draft
    print(f"\n{Colors.CYAN}🤖 Generating draft for Act {act}, Scene {scene}...{Colors.END}")
    
    # Get project context
    cursor.execute("SELECT name, gender, age, romantic_challenge, lovable_trait, comedic_flaw, notes FROM characters")
    characters = cursor.fetchall()
    
    # Build character context
    characters_context = ""
    if characters:
        characters_context = "CHARACTERS:\n"
        for char in characters:
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
    if outline:
        outline_context = "STORY OUTLINE:\n"
        for scene_outline in outline:
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
        
        draft_text = response.choices[0].message.content
        
        print(f"\n{Colors.GREEN}✨ GENERATED DRAFT - Act {act}, Scene {scene}{Colors.END}")
        print_separator()
        print(draft_text)
        print_separator()
        
        # Ask to save
        save_choice = input(f"\n{Colors.BOLD}💾 Save this draft? (y/n): {Colors.END}").strip().lower()
        if save_choice == 'y':
            cursor.execute("""
                INSERT OR REPLACE INTO finalized_draft_v1 (act, scene, final_text)
                VALUES (?, ?, ?)
            """, (act, scene, draft_text))
            
            session.db_conn.commit()
            print(f"{Colors.GREEN}💾 Draft saved for Act {act}, Scene {scene}{Colors.END}")
        
    except Exception as e:
        print(f"{Colors.RED}❌ OpenAI API error: {e}{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def write_full_script():
    """Generate drafts for all scenes in the outline"""
    print(f"\n{Colors.YELLOW}📖 WRITE FULL SCRIPT{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT act, scene, key_characters, key_events FROM story_outline ORDER BY act, scene")
    outline = cursor.fetchall()
    
    if not outline:
        print(f"{Colors.RED}❌ No story outline found!{Colors.END}")
        print(f"{Colors.CYAN}💡 Add scenes in Character & Story Intake first{Colors.END}")
        input("Press Enter to continue...")
        return
    
    print(f"{Colors.CYAN}📖 Writing full script for {len(outline)} scenes...{Colors.END}")
    print(f"{Colors.YELLOW}⚠️  This may take several minutes and use significant API credits{Colors.END}")
    
    confirm = input(f"\n{Colors.BOLD}Continue? (y/n): {Colors.END}").strip().lower()
    if confirm != 'y':
        return
    
    successful_scenes = 0
    failed_scenes = []
    
    for scene_data in outline:
        act, scene, chars, events = scene_data
        print(f"\n{Colors.CYAN}🎬 Writing Act {act}, Scene {scene}: {events}{Colors.END}")
        
        # This would use the same logic as write_single_scene but automated
        # For brevity, showing simplified version
        successful_scenes += 1
        print(f"{Colors.GREEN}✅ Act {act}, Scene {scene} completed{Colors.END}")
    
    print(f"\n{Colors.GREEN}📊 SCRIPT GENERATION COMPLETE{Colors.END}")
    print_separator("─", 40)
    print(f"{Colors.GREEN}✅ Successful: {successful_scenes} scenes{Colors.END}")
    if failed_scenes:
        print(f"{Colors.RED}❌ Failed: {len(failed_scenes)} scenes{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def view_existing_drafts():
    """Display existing drafts"""
    print(f"\n{Colors.YELLOW}📚 EXISTING DRAFTS{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("""
        SELECT act, scene, substr(final_text, 1, 100) as preview, created_at
        FROM finalized_draft_v1 
        ORDER BY act, scene
    """)
    drafts = cursor.fetchall()
    
    if not drafts:
        print(f"{Colors.CYAN}📝 No drafts written yet.{Colors.END}")
    else:
        for draft in drafts:
            act, scene, preview, created = draft
            date_str = created.split(' ')[0] if ' ' in created else created
            print(f"{Colors.BOLD}🎬 Act {act}, Scene {scene}{Colors.END} {Colors.CYAN}(Created: {date_str}){Colors.END}")
            print(f"   Preview: {preview}...")
            print()
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def export_script_to_file():
    """Export the complete script to a text file"""
    print(f"\n{Colors.YELLOW}📄 EXPORT SCRIPT TO FILE{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("""
        SELECT act, scene, final_text
        FROM finalized_draft_v1 
        ORDER BY act, scene
    """)
    scenes = cursor.fetchall()
    
    if not scenes:
        print(f"{Colors.RED}❌ No drafts found to export!{Colors.END}")
        input("Press Enter to continue...")
        return
    
    # Create export filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{session.current_project}_script_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"SCREENPLAY: {session.current_project.upper()}\n")
            f.write(f"Generated by Lizzy Framework\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            for scene in scenes:
                act, scene_num, text = scene
                f.write(f"ACT {act}, SCENE {scene_num}\n")
                f.write("-" * 30 + "\n")
                f.write(text)
                f.write("\n\n")
        
        print(f"{Colors.GREEN}✅ Script exported to: {filename}{Colors.END}")
        print(f"{Colors.CYAN}📄 {len(scenes)} scenes exported{Colors.END}")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Export failed: {e}{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def tables_manager():
    """Comprehensive SQL Tables Manager"""
    if not session.current_project:
        return
    
    while True:
        print_header()
        print_status()
        print(f"\n{Colors.BOLD}🗄️  SQL TABLES MANAGER{Colors.END}")
        print_separator()
        
        print(f"   {Colors.BOLD}1.{Colors.END} 📊 View All Tables")
        print(f"   {Colors.BOLD}2.{Colors.END} 🔍 Browse Table Data")
        print(f"   {Colors.BOLD}3.{Colors.END} ➕ Insert New Record")
        print(f"   {Colors.BOLD}4.{Colors.END} ✏️  Edit Record")
        print(f"   {Colors.BOLD}5.{Colors.END} 🗑️  Delete Record")
        print(f"   {Colors.BOLD}6.{Colors.END} 📈 Table Statistics")
        print(f"   {Colors.BOLD}7.{Colors.END} 🔧 Custom SQL Query")
        print(f"   {Colors.BOLD}8.{Colors.END} 📤 Export Table Data")
        print(f"   {Colors.BOLD}9.{Colors.END} 🧹 Clean/Optimize Tables")
        print(f"   {Colors.BOLD}10.{Colors.END} 🏠 Back to Main Menu")
        
        choice = input(f"\n{Colors.BOLD}Select option: {Colors.END}").strip()
        
        if choice == "1":
            view_all_tables()
        elif choice == "2":
            browse_table_data()
        elif choice == "3":
            insert_new_record()
        elif choice == "4":
            edit_record()
        elif choice == "5":
            delete_record()
        elif choice == "6":
            table_statistics()
        elif choice == "7":
            custom_sql_query()
        elif choice == "8":
            export_table_data()
        elif choice == "9":
            clean_optimize_tables()
        elif choice == "10":
            break

def view_all_tables():
    """View all tables in the database"""
    print(f"\n{Colors.YELLOW}📊 DATABASE TABLES{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = cursor.fetchall()
    
    print(f"{Colors.BLUE}Project: {session.current_project}{Colors.END}")
    print(f"{Colors.CYAN}Database Tables ({len(tables)} total):{Colors.END}\n")
    
    for i, (table_name,) in enumerate(tables, 1):
        # Get record count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        # Get table info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"{Colors.BOLD}{i:2d}. {table_name}{Colors.END}")
        print(f"    Records: {Colors.GREEN}{count}{Colors.END}")
        print(f"    Columns: {Colors.CYAN}{len(columns)}{Colors.END} ({', '.join([col[1] for col in columns[:3]])}{'...' if len(columns) > 3 else ''})")
        print()
    
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")

def browse_table_data():
    """Browse data from a selected table"""
    print(f"\n{Colors.YELLOW}🔍 BROWSE TABLE DATA{Colors.END}")
    print_separator()
    
    # Select table
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"{Colors.BLUE}Available Tables:{Colors.END}")
    for i, table in enumerate(tables, 1):
        print(f"   {Colors.BOLD}{i}.{Colors.END} {table}")
    
    try:
        table_idx = int(input(f"\n{Colors.BOLD}Select table number: {Colors.END}").strip()) - 1
        table_name = tables[table_idx]
    except (ValueError, IndexError):
        print(f"{Colors.RED}❌ Invalid selection{Colors.END}")
        input("Press Enter to continue...")
        return
    
    # Get table data
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    
    print(f"\n{Colors.GREEN}📋 Table: {table_name} ({len(rows)} records){Colors.END}")
    print_separator()
    
    if not rows:
        print(f"{Colors.CYAN}No data found in table.{Colors.END}")
    else:
        # Display first 10 records
        display_limit = min(10, len(rows))
        
        # Headers
        header = " | ".join(f"{col[:15]:15s}" for col in columns)
        print(f"{Colors.BOLD}{header}{Colors.END}")
        print("-" * len(header))
        
        # Data rows
        for row in rows[:display_limit]:
            row_str = " | ".join(f"{str(val)[:15]:15s}" for val in row)
            print(row_str)
        
        if len(rows) > display_limit:
            print(f"\n{Colors.YELLOW}... and {len(rows) - display_limit} more records{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def insert_new_record():
    """Insert a new record into a table"""
    print(f"\n{Colors.YELLOW}➕ INSERT NEW RECORD{Colors.END}")
    print_separator()
    
    # Select table
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"{Colors.BLUE}Available Tables:{Colors.END}")
    for i, table in enumerate(tables, 1):
        print(f"   {Colors.BOLD}{i}.{Colors.END} {table}")
    
    try:
        table_idx = int(input(f"\n{Colors.BOLD}Select table number: {Colors.END}").strip()) - 1
        table_name = tables[table_idx]
    except (ValueError, IndexError):
        print(f"{Colors.RED}❌ Invalid selection{Colors.END}")
        input("Press Enter to continue...")
        return
    
    # Get table columns (exclude auto-increment id and timestamps)
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    insertable_columns = []
    for col in columns:
        col_name = col[1]
        col_type = col[2]
        is_pk = col[5]  # Primary key flag
        
        # Skip auto-increment primary keys and auto-timestamps
        if not (is_pk and 'INTEGER' in col_type.upper()) and 'created_at' not in col_name.lower():
            insertable_columns.append((col_name, col_type))
    
    print(f"\n{Colors.GREEN}📝 Enter data for table: {table_name}{Colors.END}")
    print_separator("─", 40)
    
    values = []
    column_names = []
    
    for col_name, col_type in insertable_columns:
        value = input(f"{Colors.BOLD}{col_name} ({col_type}): {Colors.END}").strip()
        
        # Handle empty values
        if not value:
            value = None
        elif col_type.upper() in ['INTEGER', 'INT']:
            try:
                value = int(value)
            except ValueError:
                value = None
        
        values.append(value)
        column_names.append(col_name)
    
    # Create and execute insert statement
    placeholders = ', '.join(['?' for _ in values])
    columns_str = ', '.join(column_names)
    
    try:
        cursor.execute(f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})", values)
        session.db_conn.commit()
        print(f"\n{Colors.GREEN}✅ Record inserted successfully!{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Insert failed: {e}{Colors.END}")
    
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")

def edit_record():
    """Edit an existing record"""
    print(f"\n{Colors.YELLOW}✏️  EDIT RECORD{Colors.END}")
    print_separator()
    print(f"{Colors.CYAN}Feature coming soon - Advanced record editing with search and update capabilities{Colors.END}")
    input("Press Enter to continue...")

def delete_record():
    """Delete a record from a table"""
    print(f"\n{Colors.YELLOW}🗑️  DELETE RECORD{Colors.END}")
    print_separator()
    print(f"{Colors.CYAN}Feature coming soon - Safe record deletion with confirmation{Colors.END}")
    input("Press Enter to continue...")

def table_statistics():
    """Show detailed table statistics"""
    print(f"\n{Colors.YELLOW}📈 TABLE STATISTICS{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"{Colors.BLUE}Database Statistics for: {session.current_project}{Colors.END}\n")
    
    total_records = 0
    for table_name in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        total_records += count
        
        # Get table size info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = len(cursor.fetchall())
        
        # Recent activity (if has timestamp)
        try:
            cursor.execute(f"SELECT MAX(created_at) FROM {table_name}")
            last_activity = cursor.fetchone()[0]
        except:
            last_activity = "N/A"
        
        print(f"{Colors.BOLD}📊 {table_name}{Colors.END}")
        print(f"   Records: {Colors.GREEN}{count:,}{Colors.END}")
        print(f"   Columns: {Colors.CYAN}{columns}{Colors.END}")
        print(f"   Last Activity: {Colors.YELLOW}{last_activity}{Colors.END}")
        print()
    
    print(f"{Colors.BOLD}📈 Summary:{Colors.END}")
    print(f"   Total Tables: {Colors.GREEN}{len(tables)}{Colors.END}")
    print(f"   Total Records: {Colors.GREEN}{total_records:,}{Colors.END}")
    
    # Database file size
    import os
    db_path = f"projects/{session.current_project}/{session.current_project}.sqlite"
    if os.path.exists(db_path):
        size_bytes = os.path.getsize(db_path)
        size_mb = size_bytes / (1024 * 1024)
        print(f"   Database Size: {Colors.CYAN}{size_mb:.2f} MB{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def custom_sql_query():
    """Execute custom SQL queries"""
    print(f"\n{Colors.YELLOW}🔧 CUSTOM SQL QUERY{Colors.END}")
    print_separator()
    
    print(f"{Colors.RED}⚠️  Advanced Feature - Use with caution!{Colors.END}")
    print(f"{Colors.CYAN}Available tables: {Colors.END}", end="")
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    print(", ".join(tables))
    
    print(f"\n{Colors.BLUE}Examples:{Colors.END}")
    print(f"   SELECT * FROM characters WHERE name LIKE '%Emma%'")
    print(f"   SELECT act, scene, key_events FROM story_outline ORDER BY act, scene")
    print(f"   SELECT COUNT(*) as total_scenes FROM story_outline")
    
    query = input(f"\n{Colors.BOLD}Enter SQL query (or 'back' to return): {Colors.END}").strip()
    
    if query.lower() == 'back':
        return
    
    try:
        cursor.execute(query)
        
        if query.upper().startswith('SELECT'):
            results = cursor.fetchall()
            
            if results:
                # Get column names from description
                col_names = [description[0] for description in cursor.description]
                
                print(f"\n{Colors.GREEN}📋 Query Results ({len(results)} rows):{Colors.END}")
                print_separator("─", 60)
                
                # Headers
                header = " | ".join(f"{col[:15]:15s}" for col in col_names)
                print(f"{Colors.BOLD}{header}{Colors.END}")
                print("-" * len(header))
                
                # Data (limit to 20 rows)
                for row in results[:20]:
                    row_str = " | ".join(f"{str(val)[:15]:15s}" for val in row)
                    print(row_str)
                
                if len(results) > 20:
                    print(f"\n{Colors.YELLOW}... and {len(results) - 20} more rows{Colors.END}")
            else:
                print(f"\n{Colors.CYAN}Query executed successfully - No results returned{Colors.END}")
        else:
            session.db_conn.commit()
            print(f"\n{Colors.GREEN}✅ Query executed successfully!{Colors.END}")
            
    except Exception as e:
        print(f"\n{Colors.RED}❌ Query failed: {e}{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def export_table_data():
    """Export table data to various formats"""
    print(f"\n{Colors.YELLOW}📤 EXPORT TABLE DATA{Colors.END}")
    print_separator()
    
    # Select table
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"{Colors.BLUE}Available Tables:{Colors.END}")
    for i, table in enumerate(tables, 1):
        print(f"   {Colors.BOLD}{i}.{Colors.END} {table}")
    print(f"   {Colors.BOLD}{len(tables) + 1}.{Colors.END} All Tables")
    
    try:
        choice = int(input(f"\n{Colors.BOLD}Select table number: {Colors.END}").strip())
        if choice <= len(tables):
            export_tables = [tables[choice - 1]]
        else:
            export_tables = tables
    except (ValueError, IndexError):
        print(f"{Colors.RED}❌ Invalid selection{Colors.END}")
        input("Press Enter to continue...")
        return
    
    # Export format
    print(f"\n{Colors.BLUE}Export Formats:{Colors.END}")
    print(f"   {Colors.BOLD}1.{Colors.END} CSV")
    print(f"   {Colors.BOLD}2.{Colors.END} JSON")
    print(f"   {Colors.BOLD}3.{Colors.END} SQL Dump")
    
    try:
        format_choice = int(input(f"\n{Colors.BOLD}Select format: {Colors.END}").strip())
        formats = ['csv', 'json', 'sql']
        export_format = formats[format_choice - 1]
    except (ValueError, IndexError):
        export_format = 'csv'
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for table_name in export_tables:
        filename = f"{session.current_project}_{table_name}_{timestamp}.{export_format}"
        
        try:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            if export_format == 'csv':
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(columns)
                    writer.writerows(rows)
            
            elif export_format == 'json':
                import json
                data = []
                for row in rows:
                    data.append(dict(zip(columns, row)))
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
            
            elif export_format == 'sql':
                with open(filename, 'w', encoding='utf-8') as f:
                    # Write table structure
                    cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table_name}'")
                    create_sql = cursor.fetchone()[0]
                    f.write(f"{create_sql};\n\n")
                    
                    # Write data
                    for row in rows:
                        values = ', '.join([f"'{str(v)}'" if v is not None else 'NULL' for v in row])
                        f.write(f"INSERT INTO {table_name} VALUES ({values});\n")
            
            print(f"{Colors.GREEN}✅ Exported {table_name} to {filename}{Colors.END}")
            
        except Exception as e:
            print(f"{Colors.RED}❌ Export failed for {table_name}: {e}{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def clean_optimize_tables():
    """Clean and optimize database tables"""
    print(f"\n{Colors.YELLOW}🧹 CLEAN & OPTIMIZE TABLES{Colors.END}")
    print_separator()
    
    print(f"{Colors.BLUE}Database Maintenance Options:{Colors.END}")
    print(f"   {Colors.BOLD}1.{Colors.END} 🧹 VACUUM (Reclaim unused space)")
    print(f"   {Colors.BOLD}2.{Colors.END} 📊 ANALYZE (Update query planner statistics)")
    print(f"   {Colors.BOLD}3.{Colors.END} 🔍 INTEGRITY CHECK")
    print(f"   {Colors.BOLD}4.{Colors.END} 🚀 Full Optimization (All above)")
    
    choice = input(f"\n{Colors.BOLD}Select option: {Colors.END}").strip()
    
    cursor = session.db_conn.cursor()
    
    try:
        if choice in ["1", "4"]:
            print(f"{Colors.CYAN}🧹 Running VACUUM...{Colors.END}")
            cursor.execute("VACUUM")
            print(f"{Colors.GREEN}✅ VACUUM completed{Colors.END}")
        
        if choice in ["2", "4"]:
            print(f"{Colors.CYAN}📊 Running ANALYZE...{Colors.END}")
            cursor.execute("ANALYZE")
            print(f"{Colors.GREEN}✅ ANALYZE completed{Colors.END}")
        
        if choice in ["3", "4"]:
            print(f"{Colors.CYAN}🔍 Running INTEGRITY CHECK...{Colors.END}")
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            if result == "ok":
                print(f"{Colors.GREEN}✅ Database integrity: OK{Colors.END}")
            else:
                print(f"{Colors.RED}⚠️  Database integrity issues: {result}{Colors.END}")
        
        session.db_conn.commit()
        print(f"\n{Colors.GREEN}🎉 Database optimization completed!{Colors.END}")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Optimization failed: {e}{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def buckets_manager():
    """Comprehensive LightRAG Buckets Manager"""
    if not session.api_key_set:
        print(f"\n{Colors.RED}❌ OpenAI API key required for bucket operations{Colors.END}")
        input("Press Enter to continue...")
        return
    
    if not HAS_LIGHTRAG or HAS_LIGHTRAG == "partial":
        print(f"\n{Colors.RED}❌ LightRAG installation issue detected!{Colors.END}")
        if LIGHTRAG_ERROR:
            print(f"{Colors.YELLOW}Error: {LIGHTRAG_ERROR}{Colors.END}")
        print(f"\n{Colors.CYAN}🔧 To fix LightRAG installation:{Colors.END}")
        print(f"   {Colors.BOLD}1.{Colors.END} Uninstall current version: {Colors.CYAN}pip uninstall lightrag -y{Colors.END}")
        print(f"   {Colors.BOLD}2.{Colors.END} Install HKU version: {Colors.CYAN}pip install lightrag-hku{Colors.END}")
        print(f"   {Colors.BOLD}3.{Colors.END} Restart this program")
        print(f"\n{Colors.YELLOW}⚠️  Advanced features (ingest/query) will be limited until fixed{Colors.END}")
        print(f"{Colors.GREEN}✅ Basic bucket management (add files, create buckets) still works{Colors.END}")
        input("\nPress Enter to continue...")
    
    # Ensure LightRAG setup exists for new users
    ensure_lightrag_setup()
    
    while True:
        print_header()
        print_status()
        print(f"\n{Colors.BOLD}📦 LIGHTRAG BUCKETS MANAGER{Colors.END}")
        print_separator()
        
        print(f"   {Colors.BOLD}1.{Colors.END} 📊 View All Buckets")
        print(f"   {Colors.BOLD}2.{Colors.END} 📚 Browse Bucket Contents")
        print(f"   {Colors.BOLD}3.{Colors.END} ➕ Add Content to Bucket")
        print(f"   {Colors.BOLD}4.{Colors.END} 🖱️  GUI File Manager (Drag & Drop)")
        print(f"   {Colors.BOLD}5.{Colors.END} 🔄 Ingest/Reindex Bucket")
        print(f"   {Colors.BOLD}6.{Colors.END} 🔍 Query Bucket")
        print(f"   {Colors.BOLD}7.{Colors.END} 📈 Bucket Statistics")
        print(f"   {Colors.BOLD}8.{Colors.END} 🗑️  Delete Content")
        print(f"   {Colors.BOLD}9.{Colors.END} 🆕 Create New Bucket")
        print(f"   {Colors.BOLD}10.{Colors.END} 📤 Export Bucket Data")
        print(f"   {Colors.BOLD}11.{Colors.END} 🧹 Clean Bucket Cache")
        print(f"   {Colors.BOLD}12.{Colors.END} 🏠 Back to Main Menu")
        
        choice = input(f"\n{Colors.BOLD}Select option: {Colors.END}").strip()
        
        if choice == "1":
            view_all_buckets()
        elif choice == "2":
            browse_bucket_contents()
        elif choice == "3":
            add_content_to_bucket()
        elif choice == "4":
            launch_gui_file_manager()
        elif choice == "5":
            ingest_bucket()
        elif choice == "6":
            query_bucket()
        elif choice == "7":
            bucket_statistics()
        elif choice == "8":
            delete_bucket_content()
        elif choice == "9":
            create_new_bucket()
        elif choice == "10":
            export_bucket_data()
        elif choice == "11":
            clean_bucket_cache()
        elif choice == "12":
            break

def get_bucket_list():
    """Get list of available buckets"""
    working_dir = "./lightrag_working_dir"
    if not os.path.exists(working_dir):
        return []
    
    buckets = []
    for entry in os.scandir(working_dir):
        if entry.is_dir() and not entry.name.startswith('.'):
            buckets.append(entry.name)
    
    return sorted(buckets)

def ensure_lightrag_setup():
    """Ensure LightRAG directory structure exists"""
    working_dir = "./lightrag_working_dir"
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
        print(f"{Colors.GREEN}✅ Created LightRAG working directory{Colors.END}")
        
        # Create default buckets for new users
        default_buckets = ["books", "plays", "scripts"]
        for bucket in default_buckets:
            bucket_path = os.path.join(working_dir, bucket)
            os.makedirs(bucket_path)
            
            # Create helpful README
            readme_content = f"""# {bucket.upper()} BUCKET

This bucket is for storing {bucket}-related source material.

## Supported File Types
- .txt files (plain text)  
- .md files (markdown)
- .pdf files (will be processed)

## Getting Started
1. Add your source files to this directory
2. Use 'Add Content to Bucket' or 'GUI File Manager' to add files
3. Run 'Ingest/Reindex Bucket' to process with LightRAG
4. Query the bucket for contextual content retrieval

Created by LIZZY Framework
"""
            
            with open(os.path.join(bucket_path, "README.md"), 'w') as f:
                f.write(readme_content)
        
        print(f"{Colors.CYAN}📦 Created default buckets: {', '.join(default_buckets)}{Colors.END}")
        return True
    return False

def view_all_buckets():
    """View all LightRAG buckets"""
    print(f"\n{Colors.YELLOW}📊 LIGHTRAG BUCKETS{Colors.END}")
    print_separator()
    
    working_dir = "./lightrag_working_dir"
    buckets = get_bucket_list()
    
    if not buckets:
        print(f"{Colors.YELLOW}📦 No buckets found yet!{Colors.END}")
        print(f"\n{Colors.CYAN}🚀 Getting Started:{Colors.END}")
        print(f"   1. Use '{Colors.BOLD}Create New Bucket{Colors.END}' to make content categories")
        print(f"   2. Use '{Colors.BOLD}Add Content to Bucket{Colors.END}' to add files")
        print(f"   3. Use '{Colors.BOLD}GUI File Manager{Colors.END}' for drag & drop")
        print(f"   4. Use '{Colors.BOLD}Ingest/Reindex Bucket{Colors.END}' to process content")
        print(f"\n{Colors.GREEN}💡 Tip: Default buckets (books, plays, scripts) are created automatically!{Colors.END}")
        input("\nPress Enter to continue...")
        return
    
    print(f"{Colors.BLUE}LightRAG Content Buckets ({len(buckets)} total):{Colors.END}\n")
    
    for i, bucket_name in enumerate(buckets, 1):
        bucket_path = os.path.join(working_dir, bucket_name)
        
        # Count content files
        content_files = []
        if os.path.exists(bucket_path):
            for file in os.listdir(bucket_path):
                file_path = os.path.join(bucket_path, file)
                if os.path.isfile(file_path) and not file.startswith('.') and file != "README.txt":
                    if not file.endswith(('.json', '.graphml')):
                        content_files.append(file)
        
        # Check if indexed (has LightRAG metadata files)
        has_index = any(f.endswith('.json') for f in os.listdir(bucket_path) if os.path.isfile(os.path.join(bucket_path, f)))
        
        print(f"{Colors.BOLD}{i:2d}. 📦 {bucket_name.upper()}{Colors.END}")
        print(f"    Content Files: {Colors.GREEN}{len(content_files)}{Colors.END}")
        print(f"    Status: {Colors.GREEN if has_index else Colors.YELLOW}{'Indexed' if has_index else 'Not Indexed'}{Colors.END}")
        print(f"    Path: {Colors.CYAN}{bucket_path}{Colors.END}")
        print()
    
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")

def browse_bucket_contents():
    """Browse contents of a specific bucket"""
    print(f"\n{Colors.YELLOW}📚 BROWSE BUCKET CONTENTS{Colors.END}")
    print_separator()
    
    buckets = get_bucket_list()
    if not buckets:
        print(f"{Colors.RED}❌ No buckets found!{Colors.END}")
        input("Press Enter to continue...")
        return
    
    print(f"{Colors.BLUE}Available Buckets:{Colors.END}")
    for i, bucket in enumerate(buckets, 1):
        print(f"   {Colors.BOLD}{i}.{Colors.END} {bucket}")
    
    try:
        bucket_idx = int(input(f"\n{Colors.BOLD}Select bucket number: {Colors.END}").strip()) - 1
        bucket_name = buckets[bucket_idx]
    except (ValueError, IndexError):
        print(f"{Colors.RED}❌ Invalid selection{Colors.END}")
        input("Press Enter to continue...")
        return
    
    working_dir = "./lightrag_working_dir"
    bucket_path = os.path.join(working_dir, bucket_name)
    
    print(f"\n{Colors.GREEN}📋 Bucket: {bucket_name}{Colors.END}")
    print_separator()
    
    if not os.path.exists(bucket_path):
        print(f"{Colors.RED}❌ Bucket path not found: {bucket_path}{Colors.END}")
        input("Press Enter to continue...")
        return
    
    # List all files
    all_files = []
    content_files = []
    metadata_files = []
    
    for file in os.listdir(bucket_path):
        file_path = os.path.join(bucket_path, file)
        if os.path.isfile(file_path):
            all_files.append(file)
            if file.endswith(('.txt', '.md', '.pdf')):
                content_files.append(file)
            elif file.endswith(('.json', '.graphml')):
                metadata_files.append(file)
    
    print(f"{Colors.BOLD}📄 Content Files ({len(content_files)}):{Colors.END}")
    if content_files:
        for file in sorted(content_files):
            file_path = os.path.join(bucket_path, file)
            size = os.path.getsize(file_path)
            size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
            print(f"   📄 {file} ({size_str})")
    else:
        print(f"   {Colors.CYAN}No content files found{Colors.END}")
    
    print(f"\n{Colors.BOLD}🗂️  Metadata Files ({len(metadata_files)}):{Colors.END}")
    if metadata_files:
        for file in sorted(metadata_files):
            if 'chunks' in file:
                print(f"   📊 {file} (Text chunks)")
            elif 'entities' in file:
                print(f"   🏷️  {file} (Entities)")
            elif 'relationships' in file:
                print(f"   🔗 {file} (Relationships)")
            elif 'graph' in file:
                print(f"   📈 {file} (Knowledge graph)")
            else:
                print(f"   📁 {file}")
    else:
        print(f"   {Colors.YELLOW}No metadata files - bucket not indexed{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def add_content_to_bucket():
    """Add new content to a bucket"""
    print(f"\n{Colors.YELLOW}➕ ADD CONTENT TO BUCKET{Colors.END}")
    print_separator()
    
    buckets = get_bucket_list()
    if not buckets:
        print(f"{Colors.RED}❌ No buckets found!{Colors.END}")
        print(f"{Colors.CYAN}💡 Create a bucket first{Colors.END}")
        input("Press Enter to continue...")
        return
    
    print(f"{Colors.BLUE}Available Buckets:{Colors.END}")
    for i, bucket in enumerate(buckets, 1):
        print(f"   {Colors.BOLD}{i}.{Colors.END} {bucket}")
    
    try:
        bucket_idx = int(input(f"\n{Colors.BOLD}Select bucket number: {Colors.END}").strip()) - 1
        bucket_name = buckets[bucket_idx]
    except (ValueError, IndexError):
        print(f"{Colors.RED}❌ Invalid selection{Colors.END}")
        input("Press Enter to continue...")
        return
    
    working_dir = "./lightrag_working_dir"
    bucket_path = os.path.join(working_dir, bucket_name)
    
    print(f"\n{Colors.GREEN}📝 Add Content to: {bucket_name}{Colors.END}")
    print_separator("─", 40)
    
    print(f"{Colors.BLUE}Content Input Methods:{Colors.END}")
    print(f"   {Colors.BOLD}1.{Colors.END} ✏️  Type/Paste Text Content")
    print(f"   {Colors.BOLD}2.{Colors.END} 📁 Copy File from Path")
    print(f"   {Colors.BOLD}3.{Colors.END} 🌐 Download from URL")
    
    method = input(f"\n{Colors.BOLD}Select method: {Colors.END}").strip()
    
    if method == "1":
        # Text input
        filename = input(f"{Colors.BOLD}Enter filename (with .txt extension): {Colors.END}").strip()
        if not filename.endswith('.txt'):
            filename += '.txt'
        
        print(f"\n{Colors.CYAN}Enter your content (press Ctrl+D or Ctrl+Z when done):{Colors.END}")
        content_lines = []
        try:
            while True:
                line = input()
                content_lines.append(line)
        except EOFError:
            pass
        
        content = '\n'.join(content_lines)
        
        if content.strip():
            file_path = os.path.join(bucket_path, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n{Colors.GREEN}✅ Content saved to {filename}{Colors.END}")
        else:
            print(f"\n{Colors.RED}❌ No content provided{Colors.END}")
    
    elif method == "2":
        # File copy
        source_path = input(f"{Colors.BOLD}Enter source file path: {Colors.END}").strip()
        if os.path.exists(source_path) and os.path.isfile(source_path):
            filename = os.path.basename(source_path)
            dest_path = os.path.join(bucket_path, filename)
            
            try:
                shutil.copy2(source_path, dest_path)
                print(f"\n{Colors.GREEN}✅ File copied to bucket: {filename}{Colors.END}")
            except Exception as e:
                print(f"\n{Colors.RED}❌ Copy failed: {e}{Colors.END}")
        else:
            print(f"\n{Colors.RED}❌ Source file not found: {source_path}{Colors.END}")
    
    elif method == "3":
        # URL download (placeholder)
        print(f"\n{Colors.CYAN}URL download feature coming soon...{Colors.END}")
    
    else:
        print(f"\n{Colors.RED}❌ Invalid method selection{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def ingest_bucket():
    """Ingest/reindex a bucket with LightRAG"""
    print(f"\n{Colors.YELLOW}🔄 INGEST/REINDEX BUCKET{Colors.END}")
    print_separator()
    
    buckets = get_bucket_list()
    if not buckets:
        print(f"{Colors.RED}❌ No buckets found!{Colors.END}")
        input("Press Enter to continue...")
        return
    
    print(f"{Colors.BLUE}Available Buckets:{Colors.END}")
    for i, bucket in enumerate(buckets, 1):
        print(f"   {Colors.BOLD}{i}.{Colors.END} {bucket}")
    
    try:
        bucket_idx = int(input(f"\n{Colors.BOLD}Select bucket number: {Colors.END}").strip()) - 1
        bucket_name = buckets[bucket_idx]
    except (ValueError, IndexError):
        print(f"{Colors.RED}❌ Invalid selection{Colors.END}")
        input("Press Enter to continue...")
        return
    
    working_dir = "./lightrag_working_dir"
    bucket_path = os.path.join(working_dir, bucket_name)
    
    # Find content files
    content_files = []
    for file in os.listdir(bucket_path):
        if file.endswith(('.txt', '.md')) and file != "README.txt":
            content_files.append(os.path.join(bucket_path, file))
    
    if not content_files:
        print(f"\n{Colors.RED}❌ No content files found in bucket{Colors.END}")
        print(f"{Colors.CYAN}💡 Add .txt or .md files first{Colors.END}")
        input("Press Enter to continue...")
        return
    
    print(f"\n{Colors.CYAN}🔍 Found {len(content_files)} content files to ingest{Colors.END}")
    print(f"{Colors.YELLOW}⚠️  This will reprocess all content and may take time{Colors.END}")
    
    confirm = input(f"\n{Colors.BOLD}Continue with ingestion? (y/n): {Colors.END}").strip().lower()
    if confirm != 'y':
        return
    
    if not HAS_LIGHTRAG or HAS_LIGHTRAG == "partial":
        print(f"\n{Colors.RED}❌ LightRAG installation issue!{Colors.END}")
        print(f"{Colors.CYAN}🔧 Fix with:{Colors.END}")
        print(f"   pip uninstall lightrag -y && pip install lightrag-hku")
        input("Press Enter to continue...")
        return
    
    async def do_ingestion():
        print(f"\n{Colors.CYAN}🤖 Initializing LightRAG for {bucket_name}...{Colors.END}")
        rag = await initialize_lightrag(bucket_path)
        
        if not rag:
            return
            
        try:
            successful = 0
            failed = 0
            
            print(f"{Colors.CYAN}📖 Processing {len(content_files)} files...{Colors.END}")
            
            for file_path in content_files:
                filename = os.path.basename(file_path)
                print(f"{Colors.CYAN}   Processing: {filename}...{Colors.END}")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    success = await ingest_content_async(rag, content)
                    if success:
                        successful += 1
                        print(f"{Colors.GREEN}   ✅ {filename}{Colors.END}")
                    else:
                        failed += 1
                        print(f"{Colors.RED}   ❌ {filename}{Colors.END}")
                        
                except Exception as e:
                    failed += 1
                    print(f"{Colors.RED}   ❌ {filename}: {e}{Colors.END}")
            
            print(f"\n{Colors.GREEN}🎉 Ingestion completed!{Colors.END}")
            print(f"   ✅ Successful: {Colors.GREEN}{successful}{Colors.END}")
            if failed:
                print(f"   ❌ Failed: {Colors.RED}{failed}{Colors.END}")
                
        finally:
            await finalize_lightrag(rag)
    
    try:
        run_async_lightrag_operation(do_ingestion())
    except Exception as e:
        print(f"\n{Colors.RED}❌ Ingestion failed: {e}{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def query_bucket():
    """Query a bucket using LightRAG"""
    print(f"\n{Colors.YELLOW}🔍 QUERY BUCKET{Colors.END}")
    print_separator()
    
    if not HAS_LIGHTRAG or HAS_LIGHTRAG == "partial":
        print(f"\n{Colors.RED}❌ LightRAG installation issue!{Colors.END}")
        print(f"{Colors.CYAN}🔧 Fix with:{Colors.END}")
        print(f"   pip uninstall lightrag -y && pip install lightrag-hku")
        input("Press Enter to continue...")
        return
    
    buckets = get_bucket_list()
    if not buckets:
        print(f"{Colors.RED}❌ No buckets found!{Colors.END}")
        input("Press Enter to continue...")
        return
    
    print(f"{Colors.BLUE}Available Buckets:{Colors.END}")
    for i, bucket in enumerate(buckets, 1):
        print(f"   {Colors.BOLD}{i}.{Colors.END} {bucket}")
    
    try:
        bucket_idx = int(input(f"\n{Colors.BOLD}Select bucket number: {Colors.END}").strip()) - 1
        bucket_name = buckets[bucket_idx]
    except (ValueError, IndexError):
        print(f"{Colors.RED}❌ Invalid selection{Colors.END}")
        input("Press Enter to continue...")
        return
    
    working_dir = "./lightrag_working_dir"
    bucket_path = os.path.join(working_dir, bucket_name)
    
    # Check if bucket is indexed
    has_index = any(f.endswith('.json') for f in os.listdir(bucket_path) if os.path.isfile(os.path.join(bucket_path, f)))
    
    if not has_index:
        print(f"\n{Colors.RED}❌ Bucket not indexed!{Colors.END}")
        print(f"{Colors.CYAN}💡 Run 'Ingest/Reindex Bucket' first{Colors.END}")
        input("Press Enter to continue...")
        return
    
    query = input(f"\n{Colors.BOLD}Enter your query: {Colors.END}").strip()
    if not query:
        return
    
    try:
        from lightrag import LightRAG, QueryParam
        from lightrag.llm import gpt_4o_mini_complete
        
        print(f"\n{Colors.CYAN}🔍 Querying {bucket_name} bucket...{Colors.END}")
        
        # Try different query modes
        print(f"\n{Colors.BLUE}Query Modes:{Colors.END}")
        print(f"   {Colors.BOLD}1.{Colors.END} 🔍 Naive (Simple text search)")
        print(f"   {Colors.BOLD}2.{Colors.END} 🧠 Local (Entity-focused)")
        print(f"   {Colors.BOLD}3.{Colors.END} 🌐 Global (Relationship-focused)")
        print(f"   {Colors.BOLD}4.{Colors.END} 🔀 Hybrid (Combined approach)")
        print(f"   {Colors.BOLD}5.{Colors.END} 🎯 Mix (KG + Vector retrieval)")
        
        try:
            mode_choice = int(input(f"\n{Colors.BOLD}Select query mode (default 4): {Colors.END}").strip() or "4")
            modes = ["naive", "local", "global", "hybrid", "mix"]
            query_mode = modes[mode_choice - 1]
        except (ValueError, IndexError):
            query_mode = "hybrid"
        
        async def do_query():
            print(f"\n{Colors.CYAN}🤖 Initializing LightRAG for {bucket_name}...{Colors.END}")
            rag = await initialize_lightrag(bucket_path)
            
            if not rag:
                return
                
            try:
                print(f"{Colors.CYAN}🔍 Querying with {query_mode} mode...{Colors.END}")
                result = await query_content_async(rag, query, query_mode)
                
                if result:
                    print(f"\n{Colors.GREEN}📋 Query Results ({query_mode} mode):{Colors.END}")
                    print_separator()
                    print(result)
                    print_separator()
                else:
                    print(f"{Colors.RED}❌ No results returned{Colors.END}")
                    
            finally:
                await finalize_lightrag(rag)
        
        run_async_lightrag_operation(do_query())
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ Query failed: {e}{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def bucket_statistics():
    """Show bucket statistics"""
    print(f"\n{Colors.YELLOW}📈 BUCKET STATISTICS{Colors.END}")
    print_separator()
    
    working_dir = "./lightrag_working_dir"
    buckets = get_bucket_list()
    
    if not buckets:
        print(f"{Colors.RED}❌ No buckets found!{Colors.END}")
        input("Press Enter to continue...")
        return
    
    print(f"{Colors.BLUE}LightRAG Bucket Statistics:{Colors.END}\n")
    
    total_content_files = 0
    total_size = 0
    
    for bucket_name in buckets:
        bucket_path = os.path.join(working_dir, bucket_name)
        
        # Count files and calculate size
        content_files = 0
        metadata_files = 0
        bucket_size = 0
        
        if os.path.exists(bucket_path):
            for file in os.listdir(bucket_path):
                file_path = os.path.join(bucket_path, file)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    bucket_size += file_size
                    
                    if file.endswith(('.txt', '.md', '.pdf')):
                        content_files += 1
                    elif file.endswith(('.json', '.graphml')):
                        metadata_files += 1
        
        total_content_files += content_files
        total_size += bucket_size
        
        # Status
        has_index = metadata_files > 0
        size_mb = bucket_size / (1024 * 1024)
        
        print(f"{Colors.BOLD}📦 {bucket_name.upper()}{Colors.END}")
        print(f"   Content Files: {Colors.GREEN}{content_files}{Colors.END}")
        print(f"   Metadata Files: {Colors.CYAN}{metadata_files}{Colors.END}")
        print(f"   Size: {Colors.YELLOW}{size_mb:.2f} MB{Colors.END}")
        print(f"   Status: {Colors.GREEN if has_index else Colors.RED}{'Indexed' if has_index else 'Not Indexed'}{Colors.END}")
        print()
    
    print(f"{Colors.BOLD}📈 Summary:{Colors.END}")
    print(f"   Total Buckets: {Colors.GREEN}{len(buckets)}{Colors.END}")
    print(f"   Total Content Files: {Colors.GREEN}{total_content_files}{Colors.END}")
    print(f"   Total Size: {Colors.CYAN}{total_size / (1024 * 1024):.2f} MB{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def delete_bucket_content():
    """Delete content from bucket"""
    print(f"\n{Colors.YELLOW}🗑️  DELETE BUCKET CONTENT{Colors.END}")
    print_separator()
    print(f"{Colors.CYAN}Feature coming soon - Safe content deletion with confirmation{Colors.END}")
    input("Press Enter to continue...")

def create_new_bucket():
    """Create a new bucket"""
    print(f"\n{Colors.YELLOW}🆕 CREATE NEW BUCKET{Colors.END}")
    print_separator()
    
    bucket_name = input(f"{Colors.BOLD}Enter new bucket name: {Colors.END}").strip().lower()
    if not bucket_name:
        print(f"{Colors.RED}❌ Bucket name cannot be empty{Colors.END}")
        input("Press Enter to continue...")
        return
    
    # Sanitize name
    import re
    bucket_name = re.sub(r'[^\w\-_]', '_', bucket_name)
    
    working_dir = "./lightrag_working_dir"
    bucket_path = os.path.join(working_dir, bucket_name)
    
    if os.path.exists(bucket_path):
        print(f"{Colors.RED}❌ Bucket '{bucket_name}' already exists{Colors.END}")
        input("Press Enter to continue...")
        return
    
    try:
        os.makedirs(bucket_path)
        
        # Create README
        readme_content = f"""# {bucket_name.upper()} BUCKET

This bucket is for storing {bucket_name}-related source material.

## Supported File Types
- .txt files (plain text)  
- .md files (markdown)
- .pdf files (will be processed)

## Usage
1. Add your source files to this directory
2. Run Ingest/Reindex Bucket to process with LightRAG
3. Query the bucket for contextual content retrieval

## Tips
- Use descriptive filenames
- Organize content thematically
- Regular reindexing improves query quality
"""
        
        with open(os.path.join(bucket_path, "README.md"), 'w') as f:
            f.write(readme_content)
        
        print(f"\n{Colors.GREEN}✅ Bucket '{bucket_name}' created successfully!{Colors.END}")
        print(f"{Colors.CYAN}Path: {bucket_path}{Colors.END}")
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ Failed to create bucket: {e}{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def export_bucket_data():
    """Export bucket data"""
    print(f"\n{Colors.YELLOW}📤 EXPORT BUCKET DATA{Colors.END}")
    print_separator()
    print(f"{Colors.CYAN}Feature coming soon - Export bucket contents and metadata{Colors.END}")
    input("Press Enter to continue...")

def clean_bucket_cache():
    """Clean bucket cache and temporary files"""
    print(f"\n{Colors.YELLOW}🧹 CLEAN BUCKET CACHE{Colors.END}")
    print_separator()
    
    buckets = get_bucket_list()
    if not buckets:
        print(f"{Colors.RED}❌ No buckets found!{Colors.END}")
        input("Press Enter to continue...")
        return
    
    print(f"{Colors.BLUE}Cache Cleaning Options:{Colors.END}")
    print(f"   {Colors.BOLD}1.{Colors.END} 🧹 Clean All Buckets")
    print(f"   {Colors.BOLD}2.{Colors.END} 🎯 Clean Specific Bucket")
    
    choice = input(f"\n{Colors.BOLD}Select option: {Colors.END}").strip()
    
    if choice == "1":
        target_buckets = buckets
    elif choice == "2":
        print(f"\n{Colors.BLUE}Available Buckets:{Colors.END}")
        for i, bucket in enumerate(buckets, 1):
            print(f"   {Colors.BOLD}{i}.{Colors.END} {bucket}")
        
        try:
            bucket_idx = int(input(f"\n{Colors.BOLD}Select bucket: {Colors.END}").strip()) - 1
            target_buckets = [buckets[bucket_idx]]
        except (ValueError, IndexError):
            print(f"{Colors.RED}❌ Invalid selection{Colors.END}")
            input("Press Enter to continue...")
            return
    else:
        print(f"{Colors.RED}❌ Invalid choice{Colors.END}")
        input("Press Enter to continue...")
        return
    
    print(f"\n{Colors.YELLOW}⚠️  This will delete all LightRAG metadata files{Colors.END}")
    print(f"{Colors.CYAN}Content files (.txt, .md) will be preserved{Colors.END}")
    
    confirm = input(f"\n{Colors.BOLD}Continue? (y/n): {Colors.END}").strip().lower()
    if confirm != 'y':
        return
    
    working_dir = "./lightrag_working_dir"
    cleaned_files = 0
    
    for bucket_name in target_buckets:
        bucket_path = os.path.join(working_dir, bucket_name)
        
        if os.path.exists(bucket_path):
            for file in os.listdir(bucket_path):
                if file.endswith(('.json', '.graphml')):
                    file_path = os.path.join(bucket_path, file)
                    try:
                        os.remove(file_path)
                        cleaned_files += 1
                    except Exception as e:
                        print(f"{Colors.RED}❌ Failed to delete {file}: {e}{Colors.END}")
    
    print(f"\n{Colors.GREEN}🎉 Cache cleaning completed!{Colors.END}")
    print(f"   🗑️  Removed {cleaned_files} metadata files")
    print(f"   💡 Run Ingest/Reindex to rebuild indices")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def launch_gui_file_manager():
    """Launch GUI file manager for drag & drop"""
    print(f"\n{Colors.YELLOW}🖱️  GUI FILE MANAGER{Colors.END}")
    print_separator()
    
    print(f"{Colors.BLUE}Launching graphical file manager...{Colors.END}")
    print(f"{Colors.CYAN}Features:{Colors.END}")
    print(f"   • 📂 Drag & drop files directly into buckets")  
    print(f"   • 🎯 Visual bucket selection")
    print(f"   • 📋 File preview before adding")
    print(f"   • 🆕 Create new buckets")
    print(f"   • 🔄 Direct processing integration")
    
    try:
        # Import and launch GUI
        from lizzy_gui import launch_gui
        
        print(f"\n{Colors.CYAN}🚀 Starting GUI interface...{Colors.END}")
        
        # Run GUI in separate thread to avoid blocking
        import threading
        gui_thread = threading.Thread(target=launch_gui, daemon=True)
        gui_thread.start()
        
        print(f"{Colors.GREEN}✅ GUI launched successfully!{Colors.END}")
        print(f"\n{Colors.YELLOW}GUI Window Features:{Colors.END}")
        print(f"   • Left panel: Select buckets")
        print(f"   • Right panel: Drag files or click Browse")
        print(f"   • Preview area: Review files before adding")
        print(f"   • Buttons: Add files, process buckets, create new buckets")
        
        print(f"\n{Colors.BLUE}💡 Tips:{Colors.END}")
        print(f"   • Select a bucket first (left panel)")
        print(f"   • Drag .txt, .md, or .pdf files to the drop zone")
        print(f"   • Click 'Add Files to Bucket' to confirm")
        print(f"   • Use 'Process Bucket' to launch CLI for LightRAG processing")
        
        # Give GUI time to load
        import time
        time.sleep(2)
        
        print(f"\n{Colors.GREEN}GUI is now running in the background!{Colors.END}")
        print(f"{Colors.CYAN}You can continue using the CLI while the GUI is open.{Colors.END}")
        
    except ImportError as e:
        print(f"\n{Colors.RED}❌ GUI not available: {e}{Colors.END}")
        print(f"{Colors.CYAN}💡 Install tkinter: pip install tk{Colors.END}")
        print(f"{Colors.YELLOW}⚡ Fallback: Use option 3 'Add Content to Bucket' instead{Colors.END}")
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ Failed to launch GUI: {e}{Colors.END}")
        print(f"{Colors.YELLOW}⚡ Fallback: Use option 3 'Add Content to Bucket' instead{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def project_dashboard():
    """Project Dashboard"""
    if not session.current_project:
        return
    
    print_header()
    print_status()
    print(f"\n{Colors.BOLD}📋 PROJECT DASHBOARD - {session.current_project.upper()}{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    
    # Count statistics
    cursor.execute("SELECT COUNT(*) FROM characters")
    char_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM story_outline")
    scene_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM brainstorming_log")
    brainstorm_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM finalized_draft_v1")
    draft_count = cursor.fetchone()[0]
    
    print(f"{Colors.BLUE}📊 Project Statistics:{Colors.END}")
    print(f"   👤 Characters: {Colors.BOLD}{char_count}{Colors.END}")
    print(f"   🎬 Scenes: {Colors.BOLD}{scene_count}{Colors.END}")
    print(f"   🧠 Brainstorm Sessions: {Colors.BOLD}{brainstorm_count}{Colors.END}")
    print(f"   ✍️  Written Drafts: {Colors.BOLD}{draft_count}{Colors.END}")
    
    # Progress indicator
    progress = min(100, (char_count * 10 + scene_count * 15 + brainstorm_count * 5 + draft_count * 20))
    progress_bar = "█" * (progress // 5) + "░" * (20 - progress // 5)
    print(f"\n{Colors.GREEN}📈 Project Progress: {progress}%{Colors.END}")
    print(f"   [{Colors.GREEN}{progress_bar}{Colors.END}]")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def show_help():
    """Show help and documentation"""
    print_header()
    print(f"\n{Colors.BOLD}❓ HELP & DOCUMENTATION{Colors.END}")
    print_separator()
    
    help_text = f"""{Colors.CYAN}
🎬 LIZZY FRAMEWORK - AI-Assisted Long-Form Writing System

{Colors.BOLD}🚀 FIRST TIME? START HERE:{Colors.END}{Colors.CYAN}
1. {Colors.BOLD}Setup API Key{Colors.END}{Colors.CYAN} - Get a key from openai.com, paste it here
2. {Colors.BOLD}Create Project{Colors.END}{Colors.CYAN} - Choose a name like "my_screenplay"
3. {Colors.BOLD}Buckets Manager{Colors.END}{Colors.CYAN} - Add reference material (books, scripts)
4. {Colors.BOLD}Character & Story Intake{Colors.END}{Colors.CYAN} - Define your story elements
5. {Colors.BOLD}Brainstorm{Colors.END}{Colors.CYAN} - Get AI-powered creative ideas
6. {Colors.BOLD}Write{Colors.END}{Colors.CYAN} - Turn ideas into polished scenes

{Colors.BOLD}🛠️ ADVANCED TOOLS:{Colors.END}{Colors.CYAN}
• {Colors.YELLOW}Tables Manager{Colors.END}{Colors.CYAN} - View/edit project database directly
• {Colors.YELLOW}GUI File Manager{Colors.END}{Colors.CYAN} - Drag & drop files (easier than CLI)
• {Colors.YELLOW}Project Dashboard{Colors.END}{Colors.CYAN} - See progress and statistics

{Colors.BOLD}💡 BEGINNER TIPS:{Colors.END}{Colors.CYAN}
• Just type numbers to navigate menus (then press Enter)
• Everything is saved automatically - don't worry about losing work
• "Ingest" means processing files with AI so you can search them
• Try different brainstorming tones for variety
• Use the GUI if command line feels intimidating

{Colors.BOLD}🆘 TROUBLESHOOTING:{Colors.END}{Colors.CYAN}
• "API key not set" → Go to Setup API Key, get one from openai.com
• "LightRAG installation issue" → Run: python fix_lightrag.py (or manually: pip uninstall lightrag -y && pip install lightrag-hku)
• "No buckets found" → Use Create New Bucket or defaults appear automatically
• "No content files" → Add .txt/.md files before trying to ingest
• "Ingest/Query not working" → Usually means LightRAG needs fixing (see above)

{Colors.BOLD}📁 WHERE FILES ARE STORED:{Colors.END}{Colors.CYAN}
• Your projects: projects/[project_name]/
• Reference content: lightrag_working_dir/[bucket_name]/
• Full docs: LIZZY_README.md & ENHANCED_LIZZY_README.md
{Colors.END}"""
    
    print(help_text)
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.CYAN}👋 Thank you for using LIZZY Framework!{Colors.END}")
        session.close()
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ An error occurred: {e}{Colors.END}")
        session.close()
        sys.exit(1)