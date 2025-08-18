#!/usr/bin/env python3
"""
LIZZY FRAMEWORK - Retro Command Line Interface (Polished)
AI-Assisted Screenwriting System - Clean & Simple
"""

import os
import sqlite3
import sys
import json
import shutil
import re
from datetime import datetime
from openai import OpenAI

# Terminal colors for retro aesthetic
class Colors:
    HEADER = '\033[95m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
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
║                      AI-ASSISTED SCREENWRITING SYSTEM                       ║
║                       Structure • Intelligence • Craft                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}"""

# Global session state
class Session:
    def __init__(self):
        self.current_project = None
        self.db_conn = None
        self.api_key_set = False
        self.client = None
    
    def set_project(self, project_name):
        if self.db_conn:
            self.db_conn.close()
        
        db_path = f"projects/{project_name}/{project_name}.sqlite"
        if os.path.exists(db_path):
            self.current_project = project_name
            self.db_conn = sqlite3.connect(db_path)
            self.ensure_tables_exist()
            return True
        return False
    
    def ensure_tables_exist(self):
        """Ensure all required tables exist"""
        if not self.db_conn:
            return
        
        cursor = self.db_conn.cursor()
        tables = {
            'characters': """CREATE TABLE characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT,
                age TEXT,
                traits TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            'scenes': """CREATE TABLE scenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                act INTEGER,
                scene INTEGER,
                location TEXT,
                characters TEXT,
                summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            'notes': """CREATE TABLE notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            'brainstorms': """CREATE TABLE brainstorms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                prompt TEXT,
                response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            'drafts': """CREATE TABLE drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version INTEGER,
                content TEXT,
                word_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        }
        
        for table_name, create_sql in tables.items():
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not cursor.fetchone():
                cursor.execute(create_sql)
        
        self.db_conn.commit()
    
    def close(self):
        if self.db_conn:
            self.db_conn.close()

session = Session()

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
    
    print(f"{Colors.CYAN}API Key: {api_status} │ Current Project: {project_status}{Colors.END}")
    print_separator("─")

def setup_api_key():
    """Setup OpenAI API key"""
    print(f"\n{Colors.YELLOW}🔑 OPENAI API KEY SETUP{Colors.END}")
    print_separator()
    
    current_key = os.getenv('OPENAI_API_KEY')
    if current_key:
        print(f"{Colors.GREEN}✓ API key found in environment{Colors.END}")
        try:
            session.client = OpenAI(api_key=current_key)
            session.api_key_set = True
            return True
        except Exception as e:
            print(f"{Colors.RED}⚠ Invalid API key: {e}{Colors.END}")
    
    print(f"{Colors.CYAN}Enter your OpenAI API key (from platform.openai.com):{Colors.END}")
    api_key = input(f"{Colors.BOLD}> {Colors.END}").strip()
    
    if api_key:
        try:
            session.client = OpenAI(api_key=api_key)
            os.environ['OPENAI_API_KEY'] = api_key
            session.api_key_set = True
            print(f"{Colors.GREEN}✓ API key configured successfully!{Colors.END}")
            return True
        except Exception as e:
            print(f"{Colors.RED}⚠ Invalid API key: {e}{Colors.END}")
    
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
                projects.append(entry.name)
    
    return sorted(projects)

def create_project():
    """Create a new project"""
    print(f"\n{Colors.YELLOW}📝 CREATE NEW PROJECT{Colors.END}")
    print_separator()
    
    existing_projects = list_projects()
    if existing_projects:
        print(f"{Colors.CYAN}Existing Projects: {', '.join(existing_projects[:3])}{Colors.END}")
        if len(existing_projects) > 3:
            print(f"{Colors.CYAN}... and {len(existing_projects) - 3} more{Colors.END}")
        print()
    
    project_name = input(f"{Colors.BOLD}Enter project name (or 'back'): {Colors.END}").strip()
    
    if project_name.lower() == 'back' or not project_name:
        return False
    
    # Sanitize project name
    sanitized_name = re.sub(r'[^\w\-_]', '_', project_name)
    if sanitized_name != project_name:
        print(f"{Colors.YELLOW}Name sanitized to: {sanitized_name}{Colors.END}")
        project_name = sanitized_name
    
    if project_name in existing_projects:
        print(f"{Colors.RED}Project '{project_name}' already exists!{Colors.END}")
        input("Press Enter to continue...")
        return False
    
    # Create project directory and database
    projects_dir = "projects"
    if not os.path.exists(projects_dir):
        os.makedirs(projects_dir)
    
    project_dir = os.path.join(projects_dir, project_name)
    os.makedirs(project_dir)
    
    # Set project and create tables
    if session.set_project(project_name):
        # Add sample data for romcom template
        add_sample_data()
        print(f"\n{Colors.GREEN}✓ Project '{project_name}' created successfully!{Colors.END}")
        print(f"{Colors.CYAN}✓ Sample romcom template data added{Colors.END}")
        input("Press Enter to continue...")
        return True
    
    return False

def add_sample_data():
    """Add sample romcom template data"""
    cursor = session.db_conn.cursor()
    
    # Sample characters
    sample_characters = [
        ("Maya Chen", "Protagonist", "28", "Creative, passionate, organized but spontaneous when inspired", "Freelance graphic designer afraid of commitment"),
        ("Jake Thompson", "Love Interest", "30", "Charming, slightly messy, romantic at heart", "Coffee shop owner with big dreams"),
        ("Sophie Rodriguez", "Best Friend", "27", "Witty, loyal, brutally honest", "Wedding planner who's seen it all"),
    ]
    
    for char in sample_characters:
        cursor.execute("INSERT INTO characters (name, role, age, traits, notes) VALUES (?, ?, ?, ?, ?)", char)
    
    # Sample scenes
    sample_scenes = [
        (1, 1, "Coffee Shop - Morning", "Maya, Jake", "Meet-cute collision with coffee spills"),
        (1, 2, "Maya's Apartment", "Maya, Sophie", "Best friend gives relationship advice"),
        (2, 1, "Park", "Maya, Jake", "Unexpected second encounter during morning jog"),
    ]
    
    for scene in sample_scenes:
        cursor.execute("INSERT INTO scenes (act, scene, location, characters, summary) VALUES (?, ?, ?, ?, ?)", scene)
    
    # Sample notes
    sample_notes = [
        ("Theme", "Love requires vulnerability and taking chances", "Story"),
        ("Visual Style", "Warm, golden hour lighting for romantic scenes", "Direction"),
        ("Dialogue Note", "Keep banter light but meaningful - show personality through word choice", "Writing"),
    ]
    
    for note in sample_notes:
        cursor.execute("INSERT INTO notes (title, content, category) VALUES (?, ?, ?)", note)
    
    session.db_conn.commit()

def select_project():
    """Select an existing project"""
    print(f"\n{Colors.YELLOW}📂 SELECT PROJECT{Colors.END}")
    print_separator()
    
    projects = list_projects()
    if not projects:
        print(f"{Colors.RED}No projects found!{Colors.END}")
        print(f"{Colors.CYAN}Create a new project first{Colors.END}")
        input("Press Enter to continue...")
        return False
    
    print(f"{Colors.CYAN}Available Projects:{Colors.END}")
    for i, name in enumerate(projects, 1):
        print(f"   {Colors.BOLD}{i:2d}.{Colors.END} {name}")
    
    try:
        choice = input(f"\n{Colors.BOLD}Select project number (or 'back'): {Colors.END}").strip()
        
        if choice.lower() == 'back':
            return False
        
        project_idx = int(choice) - 1
        if 0 <= project_idx < len(projects):
            project_name = projects[project_idx]
            if session.set_project(project_name):
                print(f"\n{Colors.GREEN}✓ Project '{project_name}' loaded!{Colors.END}")
                input("Press Enter to continue...")
                return True
    except (ValueError, IndexError):
        print(f"{Colors.RED}Invalid selection{Colors.END}")
        input("Press Enter to continue...")
    
    return False

def main_menu():
    """Main navigation menu"""
    while True:
        print_header()
        
        if not session.api_key_set:
            print(f"\n{Colors.RED}⚠ OpenAI API key required{Colors.END}")
            if not setup_api_key():
                print(f"{Colors.YELLOW}API key required to use AI features{Colors.END}")
        
        print(f"\n{Colors.BOLD}🦎 LIZZY - AI Screenwriting Assistant{Colors.END}")
        print_separator()
        
        print(f"{Colors.CYAN}Get started quickly with the 4-step workflow:{Colors.END}")
        print()
        print(f"   {Colors.BOLD}1.{Colors.END} 🆕 Create New Project")
        print(f"   {Colors.BOLD}2.{Colors.END} 📂 Open Existing Project")
        print(f"   {Colors.BOLD}3.{Colors.END} ❓ Help & Getting Started")
        print(f"   {Colors.BOLD}4.{Colors.END} 🚪 Exit")
        
        choice = input(f"\n{Colors.BOLD}lizzy> {Colors.END}").strip()
        
        if choice == "1":
            create_project()
            if session.current_project:
                project_menu()
        elif choice == "2":
            if select_project():
                project_menu()
        elif choice == "3":
            show_help()
        elif choice in ["4", "quit", "exit", "q"]:
            print(f"\n{Colors.CYAN}Thank you for using LIZZY! 🎬{Colors.END}")
            print(f"{Colors.YELLOW}Happy writing!{Colors.END}\n")
            break
        else:
            print(f"{Colors.RED}Invalid choice. Enter 1, 2, 3, or 4.{Colors.END}")
            input("Press Enter to continue...")

def project_menu():
    """Streamlined project workflow menu"""
    while True:
        print_header()
        print_status()
        
        print(f"\n{Colors.BOLD}📝 PROJECT WORKFLOW - {session.current_project.upper()}{Colors.END}")
        print_separator()
        
        print(f"{Colors.CYAN}Complete your screenplay in 4 simple steps:{Colors.END}")
        print()
        print(f"   {Colors.BOLD}1.{Colors.END} ✏️  Edit Story Elements (Characters, Scenes, Notes)")
        print(f"   {Colors.BOLD}2.{Colors.END} 💭 Brainstorm Ideas (AI-powered creative suggestions)")
        print(f"   {Colors.BOLD}3.{Colors.END} ✍️  Write Scenes (Generate screenplay content)")
        print(f"   {Colors.BOLD}4.{Colors.END} 📤 Export Results (Save your work)")
        print()
        print(f"   {Colors.BOLD}5.{Colors.END} 📊 View Project Summary")
        print(f"   {Colors.BOLD}0.{Colors.END} 🏠 Back to Main Menu")
        
        choice = input(f"\n{Colors.BOLD}workflow> {Colors.END}").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            edit_story_elements()
        elif choice == "2":
            brainstorm_menu()
        elif choice == "3":
            write_menu()
        elif choice == "4":
            export_menu()
        elif choice == "5":
            project_summary()
        else:
            print(f"{Colors.RED}Invalid choice. Enter 0-5.{Colors.END}")
            input("Press Enter to continue...")

def edit_story_elements():
    """Edit characters, scenes, and notes"""
    while True:
        print_header()
        print_status()
        
        print(f"\n{Colors.BOLD}✏️ EDIT STORY ELEMENTS{Colors.END}")
        print_separator()
        
        print(f"   {Colors.BOLD}1.{Colors.END} 👥 Characters")
        print(f"   {Colors.BOLD}2.{Colors.END} 🎬 Scenes")  
        print(f"   {Colors.BOLD}3.{Colors.END} 📝 Notes")
        print(f"   {Colors.BOLD}0.{Colors.END} Back")
        
        choice = input(f"\n{Colors.BOLD}edit> {Colors.END}").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            manage_characters()
        elif choice == "2":
            manage_scenes()
        elif choice == "3":
            manage_notes()

def manage_characters():
    """Character management"""
    while True:
        print_header()
        print_status()
        
        print(f"\n{Colors.BOLD}👥 CHARACTER MANAGEMENT{Colors.END}")
        print_separator()
        
        # Show existing characters
        cursor = session.db_conn.cursor()
        cursor.execute("SELECT name, role FROM characters")
        characters = cursor.fetchall()
        
        if characters:
            print(f"{Colors.CYAN}Current Characters:{Colors.END}")
            for name, role in characters:
                print(f"   • {name} ({role})")
            print()
        
        print(f"   {Colors.BOLD}1.{Colors.END} Add Character")
        print(f"   {Colors.BOLD}2.{Colors.END} View Characters")
        print(f"   {Colors.BOLD}3.{Colors.END} Edit Character")
        print(f"   {Colors.BOLD}0.{Colors.END} Back")
        
        choice = input(f"\n{Colors.BOLD}characters> {Colors.END}").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            add_character()
        elif choice == "2":
            view_characters()
        elif choice == "3":
            edit_character()

def add_character():
    """Add a new character"""
    print(f"\n{Colors.YELLOW}👤 ADD CHARACTER{Colors.END}")
    print_separator()
    
    name = input(f"{Colors.BOLD}Character Name: {Colors.END}").strip()
    if not name:
        return
    
    role = input(f"{Colors.BOLD}Role (Protagonist, Love Interest, etc.): {Colors.END}").strip()
    age = input(f"{Colors.BOLD}Age: {Colors.END}").strip()
    traits = input(f"{Colors.BOLD}Key Traits: {Colors.END}").strip()
    notes = input(f"{Colors.BOLD}Additional Notes: {Colors.END}").strip()
    
    cursor = session.db_conn.cursor()
    cursor.execute("""
        INSERT INTO characters (name, role, age, traits, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (name, role, age, traits, notes))
    
    session.db_conn.commit()
    print(f"\n{Colors.GREEN}✓ Character '{name}' added successfully!{Colors.END}")
    input("Press Enter to continue...")

def view_characters():
    """Display all characters"""
    print(f"\n{Colors.YELLOW}👥 PROJECT CHARACTERS{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT name, role, age, traits, notes FROM characters")
    characters = cursor.fetchall()
    
    if not characters:
        print(f"{Colors.CYAN}No characters defined yet.{Colors.END}")
    else:
        for char in characters:
            name, role, age, traits, notes = char
            print(f"\n{Colors.BOLD}📋 {name}{Colors.END}")
            if role: print(f"   Role: {role}")
            if age: print(f"   Age: {age}")
            if traits: print(f"   Traits: {traits}")
            if notes: print(f"   Notes: {notes}")
    
    input(f"\nPress Enter to continue...")

def edit_character():
    """Edit an existing character"""
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT id, name FROM characters")
    characters = cursor.fetchall()
    
    if not characters:
        print(f"{Colors.CYAN}No characters to edit.{Colors.END}")
        input("Press Enter to continue...")
        return
    
    print(f"\n{Colors.YELLOW}Select character to edit:{Colors.END}")
    for idx, (char_id, name) in enumerate(characters, 1):
        print(f"   {Colors.BOLD}{idx}.{Colors.END} {name}")
    
    try:
        choice = int(input(f"\n{Colors.BOLD}Select character: {Colors.END}").strip())
        if 1 <= choice <= len(characters):
            char_id = characters[choice-1][0]
            
            # Get current data
            cursor.execute("SELECT * FROM characters WHERE id = ?", (char_id,))
            char_data = cursor.fetchone()
            
            print(f"\nEditing: {char_data[1]} (press Enter to keep current value)")
            
            new_name = input(f"Name [{char_data[1]}]: ").strip() or char_data[1]
            new_role = input(f"Role [{char_data[2] or ''}]: ").strip() or char_data[2]
            new_age = input(f"Age [{char_data[3] or ''}]: ").strip() or char_data[3]
            new_traits = input(f"Traits [{char_data[4] or ''}]: ").strip() or char_data[4]
            new_notes = input(f"Notes [{char_data[5] or ''}]: ").strip() or char_data[5]
            
            cursor.execute("""
                UPDATE characters SET name=?, role=?, age=?, traits=?, notes=? WHERE id=?
            """, (new_name, new_role, new_age, new_traits, new_notes, char_id))
            
            session.db_conn.commit()
            print(f"\n{Colors.GREEN}✓ Character updated successfully!{Colors.END}")
        
    except (ValueError, IndexError):
        print(f"{Colors.RED}Invalid selection{Colors.END}")
    
    input("Press Enter to continue...")

def manage_scenes():
    """Scene management"""
    print(f"\n{Colors.YELLOW}🎬 SCENE MANAGEMENT{Colors.END}")
    print_separator()
    print(f"{Colors.CYAN}Scene management coming in next update!{Colors.END}")
    print(f"For now, use the character and notes features.")
    input("Press Enter to continue...")

def manage_notes():
    """Notes management"""
    print(f"\n{Colors.YELLOW}📝 NOTES MANAGEMENT{Colors.END}")
    print_separator()
    print(f"{Colors.CYAN}Notes management coming in next update!{Colors.END}")
    print(f"For now, focus on characters and brainstorming.")
    input("Press Enter to continue...")

def brainstorm_menu():
    """AI-powered brainstorming"""
    if not session.api_key_set:
        print(f"\n{Colors.RED}⚠ OpenAI API key required for brainstorming{Colors.END}")
        input("Press Enter to continue...")
        return
    
    print(f"\n{Colors.YELLOW}💭 AI BRAINSTORMING{Colors.END}")
    print_separator()
    
    print(f"{Colors.CYAN}What would you like to brainstorm?{Colors.END}")
    print()
    print(f"   {Colors.BOLD}1.{Colors.END} Character Development")
    print(f"   {Colors.BOLD}2.{Colors.END} Scene Ideas")
    print(f"   {Colors.BOLD}3.{Colors.END} Dialogue Concepts")
    print(f"   {Colors.BOLD}4.{Colors.END} Plot Twists")
    print(f"   {Colors.BOLD}0.{Colors.END} Back")
    
    choice = input(f"\n{Colors.BOLD}brainstorm> {Colors.END}").strip()
    
    brainstorm_types = {
        "1": ("Character Development", "Help me develop deeper character backgrounds, motivations, and arcs for my screenplay characters."),
        "2": ("Scene Ideas", "Generate creative scene concepts and situations for my romantic comedy screenplay."),
        "3": ("Dialogue Concepts", "Create witty, natural dialogue ideas that reveal character and advance the plot."),
        "4": ("Plot Twists", "Suggest unexpected but organic plot developments and story turns.")
    }
    
    if choice in brainstorm_types:
        topic, base_prompt = brainstorm_types[choice]
        run_brainstorm_session(topic, base_prompt)

def run_brainstorm_session(topic, base_prompt):
    """Run an AI brainstorming session"""
    print(f"\n{Colors.CYAN}🧠 {topic.upper()} BRAINSTORM{Colors.END}")
    print_separator()
    
    # Get project context
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT name, role, traits FROM characters")
    characters = cursor.fetchall()
    
    context = f"PROJECT: {session.current_project}\n\n"
    if characters:
        context += "CHARACTERS:\n"
        for name, role, traits in characters:
            context += f"- {name} ({role}): {traits}\n"
        context += "\n"
    
    # Get user guidance
    user_input = input(f"{Colors.BOLD}Any specific focus or questions? {Colors.END}").strip()
    
    prompt = f"{context}{base_prompt}\n"
    if user_input:
        prompt += f"\nSpecific focus: {user_input}\n"
    prompt += "\nProvide 5-7 creative, specific suggestions that fit the romantic comedy genre."
    
    print(f"\n{Colors.CYAN}🤖 Generating ideas...{Colors.END}")
    
    try:
        response = session.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a creative screenwriting assistant specializing in romantic comedies. Provide specific, actionable suggestions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.8
        )
        
        result = response.choices[0].message.content
        
        # Display result
        print(f"\n{Colors.GREEN}✨ {topic.upper()} IDEAS:{Colors.END}")
        print_separator()
        print(result)
        print_separator()
        
        # Save to database
        session_id = f"{topic.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        cursor.execute("""
            INSERT INTO brainstorms (session_id, prompt, response)
            VALUES (?, ?, ?)
        """, (session_id, prompt, result))
        
        session.db_conn.commit()
        print(f"\n{Colors.GREEN}✓ Brainstorm saved as: {session_id}{Colors.END}")
        
    except Exception as e:
        print(f"\n{Colors.RED}⚠ AI Error: {str(e)}{Colors.END}")
        print(f"{Colors.YELLOW}Please check your API key and try again.{Colors.END}")
    
    input(f"\nPress Enter to continue...")

def write_menu():
    """Writing menu"""
    print(f"\n{Colors.YELLOW}✍️ WRITE SCENES{Colors.END}")
    print_separator()
    print(f"{Colors.CYAN}Scene writing coming in next update!{Colors.END}")
    print(f"Focus on characters and brainstorming for now.")
    input("Press Enter to continue...")

def export_menu():
    """Export menu"""
    print(f"\n{Colors.YELLOW}📤 EXPORT RESULTS{Colors.END}")
    print_separator()
    
    print(f"   {Colors.BOLD}1.{Colors.END} Export Characters (TXT)")
    print(f"   {Colors.BOLD}2.{Colors.END} Export Brainstorms (TXT)")
    print(f"   {Colors.BOLD}3.{Colors.END} Export All Data (JSON)")
    print(f"   {Colors.BOLD}0.{Colors.END} Back")
    
    choice = input(f"\n{Colors.BOLD}export> {Colors.END}").strip()
    
    if choice == "1":
        export_characters()
    elif choice == "2":
        export_brainstorms()
    elif choice == "3":
        export_all_data()

def export_characters():
    """Export characters to text file"""
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT name, role, age, traits, notes FROM characters")
    characters = cursor.fetchall()
    
    if not characters:
        print(f"{Colors.YELLOW}No characters to export.{Colors.END}")
        input("Press Enter to continue...")
        return
    
    filename = f"{session.current_project}_characters.txt"
    
    with open(filename, 'w') as f:
        f.write(f"CHARACTERS - {session.current_project.upper()}\n")
        f.write("=" * 50 + "\n\n")
        
        for char in characters:
            name, role, age, traits, notes = char
            f.write(f"CHARACTER: {name}\n")
            if role: f.write(f"Role: {role}\n")
            if age: f.write(f"Age: {age}\n")
            if traits: f.write(f"Traits: {traits}\n")
            if notes: f.write(f"Notes: {notes}\n")
            f.write("\n" + "-" * 30 + "\n\n")
    
    print(f"\n{Colors.GREEN}✓ Characters exported to: {filename}{Colors.END}")
    input("Press Enter to continue...")

def export_brainstorms():
    """Export brainstorming sessions"""
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT session_id, response, created_at FROM brainstorms ORDER BY created_at DESC")
    brainstorms = cursor.fetchall()
    
    if not brainstorms:
        print(f"{Colors.YELLOW}No brainstorms to export.{Colors.END}")
        input("Press Enter to continue...")
        return
    
    filename = f"{session.current_project}_brainstorms.txt"
    
    with open(filename, 'w') as f:
        f.write(f"BRAINSTORMS - {session.current_project.upper()}\n")
        f.write("=" * 50 + "\n\n")
        
        for session_id, response, created_at in brainstorms:
            f.write(f"SESSION: {session_id}\n")
            f.write(f"Created: {created_at}\n")
            f.write("-" * 30 + "\n")
            f.write(response)
            f.write("\n\n" + "=" * 50 + "\n\n")
    
    print(f"\n{Colors.GREEN}✓ Brainstorms exported to: {filename}{Colors.END}")
    input("Press Enter to continue...")

def export_all_data():
    """Export all project data as JSON"""
    cursor = session.db_conn.cursor()
    
    # Get all data
    cursor.execute("SELECT * FROM characters")
    characters = cursor.fetchall()
    
    cursor.execute("SELECT * FROM brainstorms")
    brainstorms = cursor.fetchall()
    
    data = {
        "project_name": session.current_project,
        "export_date": datetime.now().isoformat(),
        "characters": [
            {
                "id": row[0], "name": row[1], "role": row[2], 
                "age": row[3], "traits": row[4], "notes": row[5],
                "created_at": row[6]
            } for row in characters
        ],
        "brainstorms": [
            {
                "id": row[0], "session_id": row[1], "prompt": row[2],
                "response": row[3], "created_at": row[4]
            } for row in brainstorms
        ]
    }
    
    filename = f"{session.current_project}_export.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n{Colors.GREEN}✓ All data exported to: {filename}{Colors.END}")
    input("Press Enter to continue...")

def project_summary():
    """Show project summary"""
    print_header()
    print_status()
    
    print(f"\n{Colors.BOLD}📊 PROJECT SUMMARY - {session.current_project.upper()}{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    
    # Count statistics
    cursor.execute("SELECT COUNT(*) FROM characters")
    char_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM scenes")
    scene_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM notes")
    notes_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM brainstorms")
    brainstorm_count = cursor.fetchone()[0]
    
    print(f"{Colors.CYAN}Content Summary:{Colors.END}")
    print(f"   Characters: {Colors.BOLD}{char_count}{Colors.END}")
    print(f"   Scenes: {Colors.BOLD}{scene_count}{Colors.END}")
    print(f"   Notes: {Colors.BOLD}{notes_count}{Colors.END}")
    print(f"   Brainstorm Sessions: {Colors.BOLD}{brainstorm_count}{Colors.END}")
    
    # Show recent activity
    if brainstorm_count > 0:
        cursor.execute("SELECT session_id, created_at FROM brainstorms ORDER BY created_at DESC LIMIT 3")
        recent = cursor.fetchall()
        print(f"\n{Colors.CYAN}Recent Brainstorms:{Colors.END}")
        for session_id, created_at in recent:
            print(f"   • {session_id} ({created_at.split(' ')[0]})")
    
    # Progress indicator
    progress = min(100, char_count * 20 + brainstorm_count * 15)
    progress_bar = "█" * (progress // 5) + "░" * (20 - progress // 5)
    print(f"\n{Colors.GREEN}Project Progress: {progress}%{Colors.END}")
    print(f"   [{Colors.GREEN}{progress_bar}{Colors.END}]")
    
    input(f"\nPress Enter to continue...")

def show_help():
    """Show help and getting started guide"""
    print_header()
    
    print(f"\n{Colors.BOLD}❓ GETTING STARTED WITH LIZZY{Colors.END}")
    print_separator()
    
    help_text = f"""{Colors.CYAN}
🦎 LIZZY FRAMEWORK - AI Screenwriting Assistant

{Colors.BOLD}QUICK START:{Colors.END}{Colors.CYAN}
1. {Colors.BOLD}Get OpenAI API Key{Colors.END}{Colors.CYAN} - Visit platform.openai.com, create account, get API key
2. {Colors.BOLD}Create New Project{Colors.END}{Colors.CYAN} - Choose option 1 from main menu
3. {Colors.BOLD}Add Characters{Colors.END}{Colors.CYAN} - Define your main characters and their traits
4. {Colors.BOLD}Brainstorm Ideas{Colors.END}{Colors.CYAN} - Use AI to generate creative suggestions
5. {Colors.BOLD}Export Your Work{Colors.END}{Colors.CYAN} - Save your progress as text files

{Colors.BOLD}THE 4-STEP WORKFLOW:{Colors.END}{Colors.CYAN}
• {Colors.YELLOW}Edit Story Elements{Colors.END}{Colors.CYAN} - Build your character roster and story structure
• {Colors.YELLOW}Brainstorm Ideas{Colors.END}{Colors.CYAN} - Get AI-powered creative suggestions
• {Colors.YELLOW}Write Scenes{Colors.END}{Colors.CYAN} - Generate screenplay content (coming soon)
• {Colors.YELLOW}Export Results{Colors.END}{Colors.CYAN} - Save your work in various formats

{Colors.BOLD}TIPS:{Colors.END}{Colors.CYAN}
• Start with 3-4 main characters (Protagonist, Love Interest, Best Friend, etc.)
• Use brainstorming to explore character backgrounds and scene ideas
• Each brainstorm session is saved automatically
• Export your work regularly to backup your progress

{Colors.BOLD}CURRENT FEATURES:{Colors.END}{Colors.CYAN}
✓ Character management with detailed profiles
✓ AI brainstorming for character development, scenes, dialogue
✓ Project organization and data persistence
✓ Multiple export formats (TXT, JSON)

{Colors.BOLD}COMING SOON:{Colors.END}{Colors.CYAN}
• Scene writing and screenplay generation
• Complete story outline management
• Advanced export options (PDF, Fountain format)
{Colors.END}"""
    
    print(help_text)
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def main():
    """Main entry point"""
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.CYAN}Thank you for using LIZZY! 🎬{Colors.END}")
        session.close()
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}")
        session.close()
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    main()