#!/usr/bin/env python3
"""
LIZZY FRAMEWORK - Unified Retro Command Line Interface
AI-Assisted Long-Form Writing System with Template Support
"""

import os
import sqlite3
import sys
import json
import shutil
import re
from datetime import datetime
from openai import OpenAI

# Optional imports with graceful fallbacks
try:
    from core_templates import TemplateManager
    from util_admin import LizzyAdmin
    from util_agent import AutonomousAgent
    HAS_TEMPLATE_SYSTEM = True
    HAS_AUTONOMOUS_AGENT = True
except ImportError:
    HAS_TEMPLATE_SYSTEM = False
    HAS_AUTONOMOUS_AGENT = False

# Import enhanced modules for transparent workflows
try:
    from core_brainstorm import TransparentBrainstormer
    from core_write import TransparentWriter
    from core_export import LizzyExporter
    from core_knowledge import LightRAGManager, BucketInterface
    from util_apikey import APIKeyManager
    HAS_TRANSPARENT_MODULES = True
except ImportError:
    HAS_TRANSPARENT_MODULES = False

# Import intake GUI for enhanced data entry
try:
    from core_editor import launch_intake_gui, InteractiveIntake
    HAS_INTAKE_GUI = True
except ImportError:
    HAS_INTAKE_GUI = False

# Import romcom outline module
try:
    from core_outline import RomcomOutlineGUI, RomcomOutlineManager
    HAS_OUTLINE_MODULE = True
except ImportError:
    HAS_OUTLINE_MODULE = False

# Platform-specific imports for keyboard handling
try:
    import termios
    import tty
    HAS_TERMIOS = True
except ImportError:
    HAS_TERMIOS = False

# Terminal colors for retro aesthetic
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# ASCII Art Collection
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
            
            # Write current project to shared state file for bucket manager
            try:
                state_file = os.path.join(os.getcwd(), '.lizzy_current_project')
                with open(state_file, 'w') as f:
                    json.dump({
                        'current_project': project_name,
                        'timestamp': datetime.now().isoformat(),
                        'project_path': f"projects/{project_name}"
                    }, f)
            except Exception as e:
                print(f"{Colors.YELLOW}⚠ Could not write project state: {e}{Colors.END}")
            
            # Ensure all required tables exist
            self.ensure_all_tables_exist()
            
            return True
        return False
    
    def ensure_all_tables_exist(self):
        """Ensure all required tables exist in the database"""
        if not self.db_conn:
            return
        
        cursor = self.db_conn.cursor()
        
        # Define all required tables with their creation SQL
        required_tables = {
            'characters': """CREATE TABLE characters (
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
            'story_outline': """CREATE TABLE story_outline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                act INTEGER NOT NULL,
                scene INTEGER NOT NULL,
                key_characters TEXT,
                key_events TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            'brainstorming_log': """CREATE TABLE brainstorming_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                tone_preset TEXT,
                scenes_selected TEXT,
                bucket_selection TEXT,
                lightrag_context TEXT,
                ai_suggestions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            'finalized_draft_v1': """CREATE TABLE finalized_draft_v1 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version_number INTEGER NOT NULL,
                content TEXT,
                word_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            'project_metadata': """CREATE TABLE project_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        }
        
        # Check and create missing tables
        tables_created = []
        for table_name, create_sql in required_tables.items():
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                cursor.execute(create_sql)
                tables_created.append(table_name)
        
        if tables_created:
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
    
    print(f"{Colors.BLUE}API Key: {api_status} │ Current Project: {project_status}{Colors.END}")
    print_separator("─")

def setup_api_key():
    """Enhanced API key setup with testing and validation"""
    global client, session
    
    if HAS_TRANSPARENT_MODULES:
        # Use enhanced API key manager
        try:
            api_manager = APIKeyManager()
            
            # Check if we already have a working key
            current_key = api_manager.get_openai_key()
            if current_key:
                print(f"\n{Colors.YELLOW}🔍 Testing existing API key...{Colors.END}")
                result = api_manager.test_openai_key()
                
                if result["success"]:
                    client = OpenAI(api_key=current_key)
                    session.api_key_set = True
                    print(f"{Colors.GREEN}✅ Existing API key is working!{Colors.END}")
                    return True
                else:
                    print(f"{Colors.RED}❌ Existing API key failed: {result['error']}{Colors.END}")
            
            # Interactive setup
            api_manager.interactive_setup()
            
            # Test the key after setup
            final_key = api_manager.get_openai_key()
            if final_key:
                client = OpenAI(api_key=final_key)
                session.api_key_set = True
                return True
            
        except ImportError:
            pass
    
    # Fallback to simple setup
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
            print(f"{Colors.RED}⚠ Invalid API key: {e}{Colors.END}")
    
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

def wait_for_key(prompt="Press any key to continue..."):
    """Wait for any key press"""
    print(f"\n{Colors.CYAN}{prompt}{Colors.END}")
    input()

def create_project():
    """Create a new project"""
    print(f"\n{Colors.YELLOW}📝 CREATE NEW PROJECT{Colors.END}")
    print_separator()
    
    # Show existing projects
    existing_projects = [p[0] for p in list_projects()]
    if existing_projects:
        print(f"{Colors.BLUE}Existing Projects:{Colors.END}")
        for i, project in enumerate(existing_projects[:5], 1):
            print(f"   {i}. {project}")
        if len(existing_projects) > 5:
            print(f"   ... and {len(existing_projects) - 5} more")
        print()
    
    while True:
        project_name = input(f"{Colors.BOLD}Enter new project name (or 'back' to return): {Colors.END}").strip()
        
        if project_name.lower() == 'back':
            return False
        
        if not project_name:
            print(f"{Colors.RED}Project name cannot be empty!{Colors.END}")
            continue
        
        # Sanitize project name
        sanitized_name = re.sub(r'[^\w\-_]', '_', project_name)
        if sanitized_name != project_name:
            print(f"{Colors.YELLOW}Project name sanitized to: {sanitized_name}{Colors.END}")
            project_name = sanitized_name
        
        if project_name in existing_projects:
            print(f"{Colors.RED}Project '{project_name}' already exists!{Colors.END}")
            continue
        
        break
    
    # Create project using template if available
    if HAS_TEMPLATE_SYSTEM:
        from core_templates import TemplateManager
        tm = TemplateManager()
        if tm.create_project_from_template(project_name, "romcom"):
            session.set_project(project_name)
            print(f"\n{Colors.GREEN}✓ Project '{project_name}' created with romcom template!{Colors.END}")
            print(f"{Colors.GREEN}✓ 6 Character archetypes ready to customize{Colors.END}")
            print(f"{Colors.GREEN}✓ 30-scene romcom outline pre-populated{Colors.END}")
            print(f"{Colors.GREEN}✓ 6 Starter notes with romcom writing guidance{Colors.END}")
            wait_for_key()
            return True
        else:
            print(f"{Colors.RED}Failed to create project with template{Colors.END}")
            return False
    else:
        # Fallback to basic project creation
        if create_project_database(project_name):
            session.set_project(project_name)
            print(f"\n{Colors.GREEN}✓ Project '{project_name}' created and loaded!{Colors.END}")
            wait_for_key()
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
    
    # Create basic tables for fallback
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
        """CREATE TABLE story_outline_extended (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            act INTEGER NOT NULL,
            act_number INTEGER,
            scene_number INTEGER NOT NULL,
            beat TEXT,
            description TEXT,
            status TEXT DEFAULT 'pending',
            key_characters TEXT,
            key_events TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE brainstorming_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            tone_preset TEXT,
            scenes_selected TEXT,
            bucket_selection TEXT,
            lightrag_context TEXT,
            ai_suggestions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE finalized_draft_v1 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version_number INTEGER NOT NULL,
            content TEXT,
            word_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        print(f"{Colors.RED}No projects found!{Colors.END}")
        print(f"{Colors.CYAN}Create a new project first{Colors.END}")
        wait_for_key()
        return False
    
    print(f"{Colors.BLUE}Available Projects:{Colors.END}")
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
                    wait_for_key()
                    return True
                else:
                    print(f"{Colors.RED}Failed to load project{Colors.END}")
            else:
                print(f"{Colors.RED}Invalid selection{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}Please enter a number{Colors.END}")

def main_menu():
    """Main navigation menu - LIZZY"""
    while True:
        print_header()
        
        if not session.api_key_set:
            print(f"\n{Colors.RED}⚠ OpenAI API key required to continue{Colors.END}")
            setup_api_key()
            continue
        
        print(f"\n{Colors.BOLD}LIZZY - Romantic Comedy Screenplay Generator{Colors.END}")
        print_separator()
        
        print(f"{Colors.CYAN}Get started in 30 seconds with a complete romcom template:{Colors.END}")
        print(f"{Colors.CYAN}📝 6 character archetypes + 30-scene outline + writing guides{Colors.END}")
        print()
        print(f"   {Colors.BOLD}1.{Colors.END} 🆕 Create New Romcom Project")
        print(f"   {Colors.BOLD}2.{Colors.END} 📂 Open Existing Project")
        print(f"   {Colors.BOLD}3.{Colors.END} ❓ Help & Getting Started")
        print(f"   {Colors.BOLD}4.{Colors.END} 🚪 Exit")
        
        choice = input(f"\n{Colors.BOLD}Select option: {Colors.END}").strip()
        
        if choice == "1":
            create_project()
            if session.current_project:
                project_menu()
        elif choice == "2":
            if select_project():
                project_menu()
        elif choice == "3":
            show_help()
        elif choice == "4":
            print(f"\n{Colors.CYAN}Thank you for using LIZZY!{Colors.END}")
            print(f"{Colors.YELLOW}Happy writing! 🎬{Colors.END}\n")
            session.close()
            sys.exit(0)
        else:
            print(f"{Colors.RED}Invalid choice. Please select 1-4.{Colors.END}")
            wait_for_key()

def project_menu():
    """Streamlined project workflow menu"""
    while True:
        print_header()
        print_status()
        
        print(f"\n{Colors.BOLD}LIZZY WORKFLOW{Colors.END}")
        print_separator()
        
        print(f"{Colors.CYAN}📝 Complete your romantic comedy in 5 simple steps:{Colors.END}")
        print()
        print(f"   {Colors.BOLD}1.{Colors.END} 🎨 Edit Tables (Characters, Scenes, Notes)")
        print(f"   {Colors.BOLD}2.{Colors.END} 🗂️  Bucket Manager (Knowledge Base Manager)")
        print(f"   {Colors.BOLD}3.{Colors.END} 💭 Brainstorm (Generate ideas for scenes)")
        print(f"   {Colors.BOLD}4.{Colors.END} ✍️  Write (Create screenplay scenes)")
        print(f"   {Colors.BOLD}5.{Colors.END} 📤 Export (Final screenplay output)")
        print()
        print(f"   {Colors.BOLD}0.{Colors.END} 🏠 Back to Main Menu")
        
        choice = input(f"\n{Colors.BOLD}Select step: {Colors.END}").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            edit_tables_menu()
        elif choice == "2":
            bucket_manager_menu()
        elif choice == "3":
            brainstorm_module()
        elif choice == "4":
            write_module()
        elif choice == "5":
            export_options()
        else:
            print(f"{Colors.RED}Invalid choice. Please select 1-5 or 0.{Colors.END}")
            wait_for_key()

def show_help():
    """Display help information"""
    print_header()
    
    print(f"\n{Colors.BOLD}❓ GETTING STARTED WITH LIZZY{Colors.END}")
    print_separator()
    
    help_text = f"""{Colors.CYAN}
🦎 LIZZY FRAMEWORK - AI Screenwriting Assistant

{Colors.BOLD}QUICK START:{Colors.END}{Colors.CYAN}
1. {Colors.BOLD}Get OpenAI API Key{Colors.END}{Colors.CYAN} - Visit platform.openai.com, create account, get API key
2. {Colors.BOLD}Create New Project{Colors.END}{Colors.CYAN} - Choose option 1 from main menu
3. {Colors.BOLD}Edit Tables{Colors.END}{Colors.CYAN} - Define your characters, scenes, and notes
4. {Colors.BOLD}Brainstorm Ideas{Colors.END}{Colors.CYAN} - Use AI to generate creative suggestions
5. {Colors.BOLD}Write Scenes{Colors.END}{Colors.CYAN} - Turn ideas into screenplay content
6. {Colors.BOLD}Export Your Work{Colors.END}{Colors.CYAN} - Save your progress in various formats

{Colors.BOLD}THE 5-STEP WORKFLOW:{Colors.END}{Colors.CYAN}
• {Colors.YELLOW}Edit Tables{Colors.END}{Colors.CYAN} - Build your character roster and story structure
• {Colors.YELLOW}Bucket Manager{Colors.END}{Colors.CYAN} - Manage LightRAG knowledge base for context
• {Colors.YELLOW}Brainstorm{Colors.END}{Colors.CYAN} - Get AI-powered creative suggestions  
• {Colors.YELLOW}Write{Colors.END}{Colors.CYAN} - Generate screenplay content
• {Colors.YELLOW}Export{Colors.END}{Colors.CYAN} - Save your work in various formats

{Colors.BOLD}FEATURES:{Colors.END}{Colors.CYAN}
✓ Romcom template with 6 character archetypes
✓ 30-scene story outline structure
✓ AI brainstorming for character development
✓ Professional screenplay formatting
✓ Multiple export formats
{Colors.END}"""
    
    print(help_text)
    wait_for_key()

# Enhanced functionality with graceful fallbacks
def bucket_manager_menu():
    """Launch Bucket Manager for current project"""
    if not session.current_project:
        print(f"\n{Colors.RED}⚠ No project loaded{Colors.END}")
        print(f"{Colors.CYAN}Please create or select a project first{Colors.END}")
        wait_for_key()
        return
    
    print(f"\n{Colors.CYAN}🗂️ Launching Bucket Manager for {session.current_project}...{Colors.END}")
    print(f"{Colors.YELLOW}Features:{Colors.END}")
    print(f"  • Manage knowledge bases for {session.current_project}")
    print(f"  • Import buckets from other projects")
    print(f"  • Upload and process documents")
    print(f"  • View knowledge graph statistics")
    print()
    
    import subprocess
    import sys
    
    try:
        # Start the bucket manager server
        server_script = "project_bucket_manager_server.py"
        if os.path.exists(server_script):
            print(f"{Colors.GREEN}✅ Starting bucket manager server...{Colors.END}")
            
            # Launch server in background
            server_process = subprocess.Popen([
                sys.executable, server_script
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            import time
            time.sleep(2)  # Give server time to start
            
            print(f"{Colors.GREEN}🌐 Bucket Manager available at: http://localhost:8002{Colors.END}")
            print(f"{Colors.CYAN}📝 Press Enter when done to stop the server...{Colors.END}")
            
            input()  # Wait for user
            
            # Stop the server
            server_process.terminate()
            server_process.wait()
            print(f"{Colors.GREEN}✅ Bucket manager closed{Colors.END}")
            
        else:
            print(f"{Colors.RED}⚠ Bucket manager server not found{Colors.END}")
            print(f"{Colors.CYAN}Please ensure project_bucket_manager_server.py exists{Colors.END}")
    
    except Exception as e:
        print(f"{Colors.RED}⚠ Error launching bucket manager: {e}{Colors.END}")
    
    wait_for_key()


def edit_tables_menu():
    """Edit Tables - Launch Functional Web Project Editor"""
    if not session.current_project:
        print(f"\n{Colors.RED}⚠ No project loaded{Colors.END}")
        print(f"{Colors.CYAN}Please create or select a project first{Colors.END}")
        wait_for_key()
        return
    
    print(f"\n{Colors.YELLOW}🎨 EDIT TABLES{Colors.END}")
    print_separator()
    print(f"{Colors.CYAN}📋 Launching Functional Project Editor...{Colors.END}")
    print(f"{Colors.YELLOW}Full-featured project editor with data display will open in your browser{Colors.END}")
    
    try:
        import webbrowser
        import subprocess
        import time
        import os
        from pathlib import Path
        import requests
        
        print(f"\n{Colors.GREEN}🚀 Starting project editor server...{Colors.END}")
        
        # Kill any existing processes on port 8080
        try:
            os.system("lsof -ti:8080 | xargs kill -9 2>/dev/null")
            time.sleep(1)
        except:
            pass
        
        # Start the web server (web_editor_server.py) - serves functional web_editor.html
        backend_file = Path(__file__).parent / "web_editor_server.py"
        if backend_file.exists():
            # Pass current project to server via environment variable
            env = os.environ.copy()
            env['CURRENT_PROJECT'] = session.current_project
            
            # Start the backend server on port 8080
            server_process = subprocess.Popen([
                "python", str(backend_file)
            ], cwd=str(Path(__file__).parent),
               stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            
            # Wait for server to start
            print(f"{Colors.CYAN}Waiting for server to start...{Colors.END}")
            server_ready = False
            for i in range(15):
                try:
                    response = requests.get("http://localhost:8080", timeout=2)
                    if response.status_code == 200:
                        server_ready = True
                        break
                except:
                    time.sleep(1)
            
            if not server_ready:
                raise Exception("Project editor server failed to start on port 8080")
            
            # Open the interface in browser
            print(f"\n{Colors.GREEN}🌐 Opening functional project editor in browser...{Colors.END}")
            webbrowser.open("http://localhost:8080")
            
            print(f"\n{Colors.GREEN}✅ Functional project editor launched at http://localhost:8080{Colors.END}")
            print(f"{Colors.YELLOW}Close the browser tab when you're done editing{Colors.END}")
            print(f"{Colors.CYAN}Press Enter to return to main menu...{Colors.END}")
            
            # Wait for user to finish editing
            input()
            
            # Clean up server process
            try:
                server_process.terminate()
                server_process.wait(timeout=5)
            except:
                try:
                    server_process.kill()
                    server_process.wait(timeout=2)
                except:
                    # Force kill via system command
                    os.system("lsof -ti:8080 | xargs kill -9 2>/dev/null")
        else:
            raise FileNotFoundError("web_editor_server.py not found")
        
    except Exception as e:
        print(f"{Colors.RED}⚠️ Error launching project editor: {str(e)}{Colors.END}")
        print(f"{Colors.CYAN}Falling back to basic table editor...{Colors.END}")
        
        # Fallback to intake GUI if available
        if HAS_INTAKE_GUI:
            try:
                project_path = f"projects/{session.current_project}"
                launch_intake_gui(project_path)
                print(f"\n{Colors.GREEN}✅ Table editor closed{Colors.END}")
            except Exception as e2:
                print(f"{Colors.RED}⚠️ Error launching fallback editor: {str(e2)}{Colors.END}")
        else:
            print(f"{Colors.RED}⚠️ No table editor available{Colors.END}")
    
    wait_for_key()

def launch_gui_editor():
    """Launch the GUI editor for table management"""
    print(f"\n{Colors.CYAN}🖥️ Launching GUI Editor...{Colors.END}")
    print(f"{Colors.YELLOW}A new window will open for visual editing{Colors.END}")
    
    try:
        project_path = f"projects/{session.current_project}"
        launch_intake_gui(project_path)
        print(f"\n{Colors.GREEN}✅ GUI editor closed{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}⚠️ Error launching GUI: {str(e)}{Colors.END}")
    
    wait_for_key()

def basic_table_editor():
    """Advanced Interactive Table Editor"""
    print(f"\n{Colors.YELLOW}📝 ADVANCED TABLE EDITOR{Colors.END}")
    print_separator()
    print(f"{Colors.GREEN}✨ Launching Advanced Interactive Editor{Colors.END}")
    print(f"{Colors.CYAN}Features:{Colors.END}")
    print(f"  • Modern visual interface")
    print(f"  • Multi-table editing")
    print(f"  • CSV import/export")
    print(f"  • Search and filtering")
    print(f"  • Data visualization")
    
    try:
        project_path = f"projects/{session.current_project}"
        if HAS_INTAKE_GUI:
            intake_gui = InteractiveIntake(project_path)
            intake_gui.launch_gui()
            print(f"\n{Colors.GREEN}✅ Advanced editor closed{Colors.END}")
        else:
            print(f"\n{Colors.RED}⚠️ Advanced GUI not available{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}⚠️ Error launching advanced editor: {str(e)}{Colors.END}")
    
    wait_for_key()

def bucket_manager_menu():
    """Modern Bucket Manager - Web Interface"""
    print_header()
    print(f"\n{Colors.BOLD}🗂️ MODERN BUCKET MANAGER{Colors.END}")
    print_separator()
    
    print(f"{Colors.CYAN}🚀 Starting Modern Bucket Manager...{Colors.END}")
    print(f"{Colors.YELLOW}✨ Features: Modern UI, drag & drop, real-time stats{Colors.END}")
    print(f"{Colors.GREEN}📊 Will open in your browser at http://localhost:8002{Colors.END}\n")
    
    try:
        import subprocess
        import time
        import webbrowser
        
        # Start the server in a separate process
        current_dir = os.path.dirname(os.path.abspath(__file__))
        server_file = os.path.join(current_dir, "bucket_manager_server.py")
        
        if os.path.exists(server_file):
            print(f"{Colors.CYAN}Starting server...{Colors.END}")
            
            # Ensure API key is available for subprocess
            env = os.environ.copy()
            try:
                from util_apikey import APIKeyManager
                api_manager = APIKeyManager()
                api_key = api_manager.get_openai_key()
                if api_key:
                    env['OPENAI_API_KEY'] = api_key
                    print(f"{Colors.GREEN}✅ API key loaded for server process{Colors.END}")
            except Exception as e:
                print(f"{Colors.YELLOW}⚠️ Could not load API key: {e}{Colors.END}")
            
            # Start server in background
            server_process = subprocess.Popen(
                [sys.executable, server_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=current_dir,
                env=env
            )
            
            # Give it time to start
            time.sleep(2)
            
            # Open browser
            webbrowser.open('http://localhost:8002')
            
            print(f"{Colors.GREEN}✅ Bucket Manager launched successfully!{Colors.END}")
            print(f"{Colors.GREEN}🌐 Access it at: http://localhost:8002{Colors.END}")
            print(f"{Colors.YELLOW}💡 Use your browser to manage knowledge buckets{Colors.END}")
            print(f"{Colors.CYAN}   • View all buckets with real-time stats{Colors.END}")
            print(f"{Colors.CYAN}   • Create new buckets and upload files{Colors.END}")
            print(f"{Colors.CYAN}   • Search, filter, and organize knowledge bases{Colors.END}")
            print()
            print(f"{Colors.BOLD}Press Enter when done (server will stop){Colors.END}")
            
            try:
                input()  # Wait for user input
                server_process.terminate()  # Stop server when user is done
                print(f"{Colors.GREEN}Server stopped.{Colors.END}")
            except KeyboardInterrupt:
                server_process.terminate()
                print(f"\n{Colors.GREEN}Server stopped.{Colors.END}")
            
        else:
            print(f"{Colors.RED}❌ Bucket manager server not found at: {server_file}{Colors.END}")
            print(f"{Colors.YELLOW}💡 Make sure bucket_manager_server.py is in the same directory{Colors.END}")
            
    except Exception as e:
        print(f"{Colors.RED}❌ Error starting server: {e}{Colors.END}")
    
    wait_for_key()

def brainstorm_module():
    """Creative Brainstorming Module - Launch GUI"""
    if not session.current_project or not session.api_key_set:
        print(f"{Colors.RED}⚠ Project and API key required for brainstorming{Colors.END}")
        wait_for_key()
        return
    
    print(f"\n{Colors.YELLOW}💭 BRAINSTORM IDEAS{Colors.END}")
    print_separator()
    print(f"{Colors.CYAN}💭 Launching Dynamic Prompt Studio...{Colors.END}")
    print(f"{Colors.YELLOW}Interactive brainstorm interface with prompt editor and AI chat will open in your browser{Colors.END}")
    
    try:
        # Launch the HTML-based brainstorm interface using the refactored backend
        import webbrowser
        import subprocess
        import time
        import os
        from pathlib import Path
        import requests
        import signal
        
        print(f"\n{Colors.GREEN}🚀 Starting creative brainstorm studio server...{Colors.END}")
        
        # Kill any existing processes on port 8002
        try:
            os.system("lsof -ti:8002 | xargs kill -9 2>/dev/null")
            time.sleep(1)
        except:
            pass
        
        # Start the actual brainstorm backend (web_brainstorm_server.py) - serves web_brainstorm.html with chat/prompt toggle
        backend_file = Path(__file__).parent / "web_brainstorm_server.py"
        if backend_file.exists():
            # Start the backend server on port 8002
            server_process = subprocess.Popen([
                "python", str(backend_file)
            ], cwd=str(Path(__file__).parent), 
               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            print(f"{Colors.CYAN}Waiting for server to start...{Colors.END}")
            server_ready = False
            for i in range(15):
                try:
                    response = requests.get("http://localhost:8003", timeout=2)
                    if response.status_code == 200:
                        server_ready = True
                        break
                except:
                    time.sleep(1)
            
            if not server_ready:
                raise Exception("Brainstorm server failed to start on port 8003")
            
            # Open the interface in browser
            print(f"\n{Colors.GREEN}🌐 Opening creative brainstorm studio in browser...{Colors.END}")
            webbrowser.open("http://localhost:8003")
            
            print(f"\n{Colors.GREEN}✅ Creative brainstorm studio launched at http://localhost:8003{Colors.END}")
            print(f"{Colors.YELLOW}Close the browser tab when you're done brainstorming{Colors.END}")
            print(f"{Colors.CYAN}Press Enter to return to main menu...{Colors.END}")
            
            # Wait for user to finish brainstorming
            input()
            
            # Clean up server process
            try:
                server_process.terminate()
                server_process.wait(timeout=5)
            except:
                try:
                    server_process.kill()
                    server_process.wait(timeout=2)
                except:
                    # Force kill via system command
                    os.system("lsof -ti:8002 | xargs kill -9 2>/dev/null")
        else:
            raise FileNotFoundError("web_brainstorm_server.py not found")
        
    except Exception as e:
        print(f"{Colors.RED}⚠️ Error launching brainstorm GUI: {str(e)}{Colors.END}")
        print(f"{Colors.CYAN}Falling back to CLI brainstorming...{Colors.END}")
        
        # Fallback to CLI-based brainstorming
        if HAS_TRANSPARENT_MODULES:
            try:
                project_path = f"projects/{session.current_project}"
                brainstormer = TransparentBrainstormer(project_path=project_path)
                
                print(f"\n{Colors.CYAN}🧠 Starting CLI brainstorming session...{Colors.END}")
                
                # Quick setup with default options
                selected_buckets = ["scripts", "books"]
                user_guidance = "Generate creative romantic comedy ideas"
                
                print(f"\n{Colors.GREEN}🚀 Running brainstorming with defaults...{Colors.END}")
                
                # Run async brainstorming
                import asyncio
                
                async def run_brainstorm():
                    session_id = await brainstormer.brainstorm_all_scenes(
                        buckets=selected_buckets,
                        user_guidance=user_guidance
                    )
                    return session_id
                
                session_id = asyncio.run(run_brainstorm())
                print(f"\n{Colors.GREEN}✅ Brainstorming session '{session_id}' completed!{Colors.END}")
                
            except Exception as fallback_error:
                print(f"{Colors.RED}⚠️ Fallback error: {str(fallback_error)}{Colors.END}")
        else:
            print(f"{Colors.RED}⚠️ Brainstorming modules not available{Colors.END}")
    
    wait_for_key()

def write_module():
    """Writing Module - CLI Only (No GUI Yet)"""
    if not session.current_project or not session.api_key_set:
        print(f"{Colors.RED}⚠ Project and API key required for writing{Colors.END}")
        wait_for_key()
        return
    
    print(f"\n{Colors.YELLOW}✍️ WRITE SCREENPLAY{Colors.END}")
    print_separator()
    print(f"{Colors.CYAN}📝 Enhanced Writing Mode{Colors.END}")
    print(f"{Colors.YELLOW}GUI coming soon! Using enhanced CLI writing for now{Colors.END}")
    
    if HAS_TRANSPARENT_MODULES:
        print(f"\n{Colors.GREEN}✨ Using Enhanced Transparent Writing{Colors.END}")
        print(f"{Colors.CYAN}Features:{Colors.END}")
        print(f"  • Context from brainstorming sessions")
        print(f"  • Style guidance from buckets")
        print(f"  • Professional screenplay formatting")
        print(f"  • Real-time generation tracking")
        
        try:
            project_path = f"projects/{session.current_project}"
            from core_write import TransparentWriter
            writer = TransparentWriter(project_path=project_path)
            
            print(f"\n{Colors.CYAN}✍️ Starting enhanced writing session...{Colors.END}")
            print(f"{Colors.YELLOW}Advanced CLI writing tools ready!{Colors.END}")
            
        except Exception as e:
            print(f"\n{Colors.RED}⚠️ Enhanced writing error: {str(e)}{Colors.END}")
            print(f"{Colors.CYAN}Basic writing mode available{Colors.END}")
    else:
        print(f"\n{Colors.CYAN}Basic Writing Features:{Colors.END}")
        print(f"  • Scene content generation")
        print(f"  • Character dialogue")
        print(f"  • Story progression")
        print(f"  • Export to various formats")
        print(f"\n{Colors.YELLOW}Enhanced writing modules coming soon!{Colors.END}")
    
    wait_for_key()

def export_options():
    """Export menu with Enhanced Options"""
    if not session.current_project:
        print(f"{Colors.RED}⚠ No project loaded{Colors.END}")
        wait_for_key()
        return
    
    if HAS_TRANSPARENT_MODULES:
        print(f"\n{Colors.YELLOW}📤 ENHANCED EXPORT{Colors.END}")
        print_separator()
        
        print(f"{Colors.GREEN}✨ Enhanced Export Available{Colors.END}")
        print(f"   {Colors.BOLD}1.{Colors.END} 📦 Complete Package (Everything)")
        print(f"   {Colors.BOLD}2.{Colors.END} 🎬 Screenplay Only")
        print(f"   {Colors.BOLD}3.{Colors.END} 📊 Data & Analysis")
        print(f"   {Colors.BOLD}4.{Colors.END} 📝 All Sessions")
        print(f"   {Colors.BOLD}0.{Colors.END} Back")
        
        choice = input(f"\n{Colors.BOLD}Select option: {Colors.END}").strip()
        
        if choice in ["1", "2", "3", "4"]:
            enhanced_export(choice)
        elif choice == "0":
            return
    else:
        print(f"\n{Colors.YELLOW}📤 EXPORT{Colors.END}")
        print_separator()
        print(f"{Colors.CYAN}Export functionality coming soon!{Colors.END}")
        print(f"This will save your work in multiple formats (TXT, PDF, Fountain).")
        wait_for_key()

def enhanced_export(export_type):
    """Use enhanced export system"""
    try:
        # Initialize export system
        exporter = ExportSystem(
            project_path=f"projects/{session.current_project}",
            project_name=session.current_project
        )
        
        type_map = {
            "1": "complete",
            "2": "screenplay", 
            "3": "data",
            "4": "sessions"
        }
        
        selected_type = type_map.get(export_type, "complete")
        
        print(f"\n{Colors.CYAN}📦 Creating {selected_type} export package...{Colors.END}")
        
        # Create export with basic formats
        zip_path = exporter.create_export_package(
            export_type=selected_type,
            formats=["json", "txt"],
            include_metadata=True
        )
        
        print(f"\n{Colors.GREEN}✅ Export completed!{Colors.END}")
        print(f"Package saved to: {zip_path}")
        
    except Exception as e:
        print(f"\n{Colors.RED}⚠️ Export error: {str(e)}{Colors.END}")
    
    wait_for_key()

def main():
    """Main entry point"""
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.CYAN}Thank you for using LIZZY Framework!{Colors.END}")
        session.close()
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}An error occurred: {e}{Colors.END}")
        session.close()
        sys.exit(1)

if __name__ == "__main__":
    main()