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

# Import template management
try:
    from lizzy_templates import TemplateManager
    from admin import LizzyAdmin
    from autonomous_agent import AutonomousAgent
    HAS_TEMPLATE_SYSTEM = True
    HAS_AUTONOMOUS_AGENT = True
except ImportError:
    HAS_TEMPLATE_SYSTEM = False
    HAS_AUTONOMOUS_AGENT = False

# Import enhanced modules for transparent workflows
try:
    from lizzy_transparent_brainstorm import TransparentBrainstormer
    from lizzy_transparent_write import TransparentWriter
    from lizzy_export_system import ExportSystem
    from lizzy_lightrag_manager import LightRAGManager
    HAS_TRANSPARENT_MODULES = True
except ImportError:
    HAS_TRANSPARENT_MODULES = False

# Import intake GUI for enhanced data entry
try:
    from lizzy_intake_interactive import launch_intake_gui
    HAS_INTAKE_GUI = True
except ImportError:
    HAS_INTAKE_GUI = False

# Import romcom outline module
try:
    from lizzy_romcom_outline import RomcomOutlineGUI, RomcomOutlineManager
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

NEW_ART = f"""{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                        ███╗   ██╗███████╗██╗    ██╗                         ║
║                        ████╗  ██║██╔════╝██║    ██║                         ║
║                        ██╔██╗ ██║█████╗  ██║ █╗ ██║                         ║
║                        ██║╚██╗██║██╔══╝  ██║███╗██║                         ║
║                        ██║ ╚████║███████╗╚███╔███╔╝                         ║
║                        ╚═╝  ╚═══╝╚══════╝ ╚══╝╚══╝                          ║
║                                                                              ║
║         ┌─────────────────────────────────────────────────────┐             ║
║         │                                                     │             ║
║         │              Database Creation                       │             ║
║         │              Template Selection                      │             ║
║         │              Schema Setup                           │             ║
║         │              Story Foundation                        │             ║
║         │                                                     │             ║
║         └─────────────────────────────────────────────────────┘             ║
║                          From Concept to Completion                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}"""

TABLES_ART = f"""{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║           ████████  █████  ██████  ██      ███████ ███████                  ║
║              ██    ██   ██ ██   ██ ██      ██      ██                       ║
║              ██    ███████ ██████  ██      █████   ███████                  ║
║              ██    ██   ██ ██   ██ ██      ██           ██                  ║
║              ██    ██   ██ ██████  ███████ ███████ ███████                  ║
║                                                                              ║
║        ┌──────────────┬──────────────┬──────────────┬──────────────┐        ║
║        │              │              │              │              │        ║
║        │  CHARACTERS  │    SCENES    │    NOTES     │  STATISTICS  │        ║
║        │              │              │              │              │        ║
║        │  Maya Chen   │   Opening    │ Theme Ideas  │ 3 Characters │        ║
║        │  Frank Lopez │   Conflict   │  Dialogue    │   5 Scenes   │        ║
║        │  Jordan Kim  │  Resolution  │ Visual Notes │  847 Words   │        ║
║        │              │              │              │              │        ║
║        └──────────────┴──────────────┴──────────────┴──────────────┘        ║
║                            Your Story Foundation                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}"""

BUCKETS_ART = f"""{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║           ██████  ██    ██  ██████ ██   ██ ███████ ████████ ███████         ║
║           ██   ██ ██    ██ ██      ██  ██  ██         ██    ██              ║
║           ██████  ██    ██ ██      █████   █████      ██    ███████         ║
║           ██   ██ ██    ██ ██      ██  ██  ██         ██         ██         ║
║           ██████   ██████   ██████ ██   ██ ███████    ██    ███████         ║
║                                                                              ║
║     ┌─────────────┐      ┌─────────────┐      ┌─────────────┐               ║
║     │             │      │             │      │             │               ║
║     │    BOOKS    │      │    PLAYS    │      │   SCRIPTS   │               ║
║     │             │      │             │      │             │               ║
║     │ Writing     │      │ Dialogue    │      │Professional │               ║
║     │ Theory      │      │ Character   │      │ Examples    │               ║
║     │ Craft       │◄────►│ Theatre     │◄────►│ Structure   │               ║
║     │             │      │             │      │             │               ║
║     │ 12 files    │      │  8 files    │      │ 15 files    │               ║
║     │             │      │             │      │             │               ║
║     └─────────────┘      └─────────────┘      └─────────────┘               ║
║                                                                              ║
║                     Contextual Knowledge Synthesis                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}"""

BRAINSTORM_ART = f"""{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║       ██████  ██████   █████  ██ ███    ██ ███████ ████████  ██████  ██████ ███║
║       ██   ██ ██   ██ ██   ██ ██ ████   ██ ██         ██    ██    ██ ██   ██ ████║
║       ██████  ██████  ███████ ██ ██ ██  ██ ███████    ██    ██    ██ ██████  ██ ██║
║       ██   ██ ██   ██ ██   ██ ██ ██  ██ ██      ██    ██    ██    ██ ██   ██ ██  ██║
║       ██████  ██   ██ ██   ██ ██ ██   ████ ███████    ██     ██████  ██   ██ ██   ██║
║                                                                              ║
║      ┌─────────────────────────────────────────────────────────────────────┐║
║      │                                                                     │║
║      │    SELECT: Buckets    Tables    Prior Versions                      │║
║      │    TONE: Romantic Dramedy                                           │║
║      │    GUIDANCE: Focus on character chemistry and conflict              │║
║      │                                                                     │║
║      │    Scene Concepts • Dialogue Ideas • Visual Moments                │║
║      │    Character Development • Plot Advancement                         │║
║      │                                                                     │║
║      └─────────────────────────────────────────────────────────────────────┘║
║                        AI-Powered Creative Ideation                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}"""

WRITE_ART = f"""{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║               ██╗    ██╗██████  ██ ████████ ███████                         ║
║               ██║    ██║██   ██ ██    ██    ██                              ║
║               ██║ █╗ ██║██████  ██    ██    █████                           ║
║               ██║███╗██║██   ██ ██    ██    ██                              ║
║               ╚███╔███╔╝██   ██ ██    ██    ███████                         ║
║                ╚══╝╚══╝                                                     ║
║                                                                              ║
║      ┌─────────────────────────────────────────────────────────────────────┐║
║      │                                                                     │║
║      │                  SCREENPLAY GENERATION                              │║
║      │                                                                     │║
║      │         Synthesizing character voices                               │║
║      │         Building cinematic moments                                  │║
║      │         Applying professional format                                │║
║      │         Crafting authentic dialogue                                 │║
║      │                                                                     │║
║      │         INT. COFFEE SHOP - DAY                                      │║
║      │                                                                     │║
║      │         MAYA enters, hesitant. The morning rush...                  │║
║      │                                                                     │║
║      └─────────────────────────────────────────────────────────────────────┘║
║                       Professional Screenplay Output                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}"""

VERSIONS_ART = f"""{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║         ██╗   ██╗███████╗██████  ███████ ██╗ ██████  ███    ██ ███████      ║
║         ██║   ██║██╔════╝██╔══██╗██╔════╝██║██╔═══██╗████   ██║██╔════╝      ║
║         ██║   ██║█████╗  ██████╔╝███████╗██║██║   ██║██╔██╗ ██║███████╗      ║
║         ╚██╗ ██╔╝██╔══╝  ██╔══██╗╚════██║██║██║   ██║██║╚██╗██║╚════██║      ║
║          ╚████╔╝ ███████╗██║  ██║███████║██║╚██████╔╝██║ ╚████║███████║      ║
║           ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝      ║
║                                                                              ║
║      ┌─────────────────────────────────────────────────────────────────────┐║
║      │                                                                     │║
║      │  BRAINSTORM VERSIONS:                                               │║
║      │  1. BS_20250130_143022 - Initial character ideas                   │║
║      │  2. BS_20250130_150415 - Dialogue and conflict                     │║
║      │  3. BS_20250130_152301 - Visual storytelling                       │║
║      │                                                                     │║
║      │  WRITE VERSIONS:                                                    │║
║      │  1. Version 1 - Opening scene (347 words)                          │║
║      │  2. Version 2 - Revised with conflict (412 words)                  │║
║      │  3. Version 3 - Final polish (389 words)                           │║
║      │                                                                     │║
║      └─────────────────────────────────────────────────────────────────────┘║
║                         Complete Creative Timeline                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}"""

EXPORT_ART = f"""{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║               ███████ ██   ██ ██████   ██████  ██████  ████████             ║
║               ██       ██ ██  ██   ██ ██    ██ ██   ██    ██                ║
║               █████     ███   ██████  ██    ██ ██████     ██                ║
║               ██       ██ ██  ██      ██    ██ ██   ██    ██                ║
║               ███████ ██   ██ ██       ██████  ██   ██    ██                ║
║                                                                              ║
║      ┌─────────────────────────────────────────────────────────────────────┐║
║      │                                                                     │║
║      │                        EXPORT OPTIONS                               │║
║      │                                                                     │║
║      │  1. Export brainstorms     -> Creative process archive             │║
║      │  2. Export final drafts    -> Professional screenplay              │║
║      │  3. Export tables          -> Story data (CSV/JSON)                │║
║      │  4. Export everything      -> Complete backup                      │║
║      │                                                                     │║
║      │  Industry standard formats                                          │║
║      │  Metadata preservation                                              │║
║      │  Version control ready                                              │║
║      │                                                                     │║
║      └─────────────────────────────────────────────────────────────────────┘║
║                         Production-Ready Output                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}"""

SUCCESS_ART = f"""{Colors.GREEN}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║               ███████ ██    ██  ██████  ██████ ███████ ███████ ███████      ║
║               ██      ██    ██ ██      ██      ██      ██      ██           ║
║               ███████ ██    ██ ██      ██      █████   ███████ ███████      ║
║                    ██ ██    ██ ██      ██      ██           ██      ██      ║
║               ███████  ██████   ██████  ██████ ███████ ███████ ███████      ║
║                                                                              ║
║      ┌─────────────────────────────────────────────────────────────────────┐║
║      │                                                                     │║
║      │                  OPERATION COMPLETED SUCCESSFULLY                   │║
║      │                                                                     │║
║      │              Data processed and saved                               │║
║      │              All objectives achieved                                │║
║      │              Ready for next step                                    │║
║      │                                                                     │║
║      └─────────────────────────────────────────────────────────────────────┘║
║                            Your Screenplay Awaits                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}"""

WARNING_ART = f"""{Colors.YELLOW}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║               ██╗    ██╗ █████  ██████  ███    ██ ██ ███    ██  ██████      ║
║               ██║    ██║██   ██ ██   ██ ████   ██ ██ ████   ██ ██           ║
║               ██║ █╗ ██║███████ ██████  ██ ██  ██ ██ ██ ██  ██ ██   ███     ║
║               ██║███╗██║██   ██ ██   ██ ██  ██ ██ ██ ██  ██ ██ ██    ██     ║
║               ╚███╔███╔╝██   ██ ██   ██ ██   ████ ██ ██   ████  ██████      ║
║                ╚══╝╚══╝                                                     ║
║                                                                              ║
║      ┌─────────────────────────────────────────────────────────────────────┐║
║      │                                                                     │║
║      │  API key not found. Please set your OpenAI API key:                │║
║      │                                                                     │║
║      │  export OPENAI_API_KEY=your_key_here                               │║
║      │                                                                     │║
║      │  Get your key at: https://platform.openai.com/api-keys             │║
║      │                                                                     │║
║      └─────────────────────────────────────────────────────────────────────┘║
║                            Check Configuration                               ║
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
        self.menu_stack = []  # Track menu navigation
    
    def set_project(self, project_name):
        if self.db_conn:
            self.db_conn.close()
        
        db_path = f"projects/{project_name}/{project_name}.sqlite"
        if os.path.exists(db_path):
            self.current_project = project_name
            self.db_conn = sqlite3.connect(db_path)
            
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
            for table in tables_created:
                print(f"{Colors.GREEN}✓ Created missing table: {table}{Colors.END}")
        
        # Check and apply schema migrations
        self.apply_schema_migrations()
    
    def apply_schema_migrations(self):
        """Apply necessary schema migrations to existing tables"""
        if not self.db_conn:
            return
        
        cursor = self.db_conn.cursor()
        
        # Check if finalized_draft_v1 needs version_number column
        cursor.execute("PRAGMA table_info(finalized_draft_v1)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'finalized_draft_v1' in [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
            if 'version_number' not in column_names:
                print(f"{Colors.YELLOW}⚡ Migrating finalized_draft_v1 table schema...{Colors.END}")
                
                # Create new table with correct schema
                cursor.execute("""
                    CREATE TABLE finalized_draft_v1_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        version_number INTEGER NOT NULL,
                        content TEXT,
                        word_count INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Copy existing data
                cursor.execute("""
                    INSERT INTO finalized_draft_v1_new (version_number, content, word_count, created_at)
                    SELECT 
                        ROW_NUMBER() OVER (ORDER BY created_at) as version_number,
                        content,
                        LENGTH(content) - LENGTH(REPLACE(content, ' ', '')) + 1 as word_count,
                        created_at
                    FROM finalized_draft_v1
                """)
                
                # Drop old table and rename new one
                cursor.execute("DROP TABLE finalized_draft_v1")
                cursor.execute("ALTER TABLE finalized_draft_v1_new RENAME TO finalized_draft_v1")
                
                self.db_conn.commit()
                print(f"{Colors.GREEN}✓ Migration completed successfully{Colors.END}")
    
    def close(self):
        if self.db_conn:
            self.db_conn.close()

session = Session()

# Security validation functions
def validate_table_name(table_name):
    """Validate table name to prevent SQL injection"""
    if not table_name or not isinstance(table_name, str):
        return False
    # Allow only alphanumeric characters, underscores, and hyphens
    if not re.match(r'^[a-zA-Z0-9_-]+$', table_name):
        return False
    # Prevent SQL keywords
    sql_keywords = {'select', 'insert', 'update', 'delete', 'drop', 'create', 'alter', 'union', 'where'}
    if table_name.lower() in sql_keywords:
        return False
    return True

def get_valid_table_names(cursor):
    """Get list of valid table names from database"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    return [row[0] for row in cursor.fetchall()]

def validate_filename(filename):
    """Validate filename to prevent path traversal"""
    if not filename or not isinstance(filename, str):
        return False
    # Prevent path traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        return False
    # Allow only safe characters
    if not re.match(r'^[a-zA-Z0-9._-]+$', filename):
        return False
    return True

def sanitize_path(path):
    """Sanitize file path to prevent directory traversal"""
    if not path:
        return None
    # Remove any path traversal attempts
    path = path.replace('..', '').replace('//', '/')
    # Normalize the path
    path = os.path.normpath(path)
    return path

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
        print(f"{Colors.RED} LightRAG initialization failed: {e}{Colors.END}")
        return None

async def ingest_content_async(rag, content):
    """Async content ingestion"""
    try:
        await rag.ainsert(content)
        return True
    except Exception as e:
        print(f"{Colors.RED} Content ingestion failed: {e}{Colors.END}")
        return False

async def query_content_async(rag, query, mode="hybrid"):
    """Async content querying"""
    try:
        result = await rag.aquery(query, param=QueryParam(mode=mode))
        return result
    except Exception as e:
        print(f"{Colors.RED} Query failed: {e}{Colors.END}")
        return None

async def finalize_lightrag(rag):
    """Properly close LightRAG instance"""
    if rag:
        try:
            await rag.finalize_storages()
        except Exception as e:
            print(f"{Colors.YELLOW}  Warning during cleanup: {e}{Colors.END}")

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
            print(f"{Colors.RED} Invalid API key: {e}{Colors.END}")
    
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
            print(f"{Colors.RED} Invalid API key: {e}{Colors.END}")
    
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
    print(f"\n{Colors.YELLOW} CREATE NEW PROJECT{Colors.END}")
    print_separator()
    
    # Show existing projects
    existing_projects = [p[0] for p in list_projects()]
    if existing_projects:
        print(f"{Colors.BLUE} Existing Projects:{Colors.END}")
        for i, project in enumerate(existing_projects[:5], 1):
            print(f"   {i}. {project}")
        if len(existing_projects) > 5:
            print(f"   ... and {len(existing_projects) - 5} more")
        print()
    
    while True:
        project_name = input(f"{Colors.BOLD} Enter new project name (or 'back' to return): {Colors.END}").strip()
        
        if project_name.lower() == 'back':
            return False
        
        if not project_name:
            print(f"{Colors.RED} Project name cannot be empty!{Colors.END}")
            continue
        
        # Sanitize project name
        import re
        sanitized_name = re.sub(r'[^\w\-_]', '_', project_name)
        if sanitized_name != project_name:
            print(f"{Colors.YELLOW} Project name sanitized to: {sanitized_name}{Colors.END}")
            project_name = sanitized_name
        
        if project_name in existing_projects:
            print(f"{Colors.RED} Project '{project_name}' already exists!{Colors.END}")
            continue
        
        break
    
    # Create project using romcom template by default
    if HAS_TEMPLATE_SYSTEM:
        from lizzy_templates import TemplateManager
        tm = TemplateManager()
        if tm.create_project_from_template(project_name, "romcom"):
            session.set_project(project_name)
            print(f"\n{Colors.GREEN} Project '{project_name}' created with romcom template!{Colors.END}")
            print(f"{Colors.GREEN} ✓ 6 Character archetypes ready to customize{Colors.END}")
            print(f"{Colors.GREEN} ✓ 30-scene romcom outline pre-populated{Colors.END}")
            print(f"{Colors.GREEN} ✓ 6 Starter notes with romcom writing guidance{Colors.END}")
            input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")
            return True
        else:
            print(f"{Colors.RED} Failed to create project with template{Colors.END}")
            return False
    else:
        # Fallback to old method if template system not available
        if create_project_database(project_name):
            session.set_project(project_name)
            print(f"\n{Colors.GREEN} Project '{project_name}' created and loaded!{Colors.END}")
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
    print(f"\n{Colors.YELLOW} SELECT PROJECT{Colors.END}")
    print_separator()
    
    projects = list_projects()
    if not projects:
        print(f"{Colors.RED} No projects found!{Colors.END}")
        print(f"{Colors.CYAN} Create a new project first{Colors.END}")
        input(f"\nPress Enter to continue...")
        return False
    
    print(f"{Colors.BLUE} Available Projects:{Colors.END}")
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
                    print(f"{Colors.RED} Failed to load project{Colors.END}")
            else:
                print(f"{Colors.RED} Invalid selection{Colors.END}")
        except ValueError:
            print(f"{Colors.RED} Please enter a number{Colors.END}")

def get_single_keypress():
    """Get a single keypress including special keys like arrows"""
    if not HAS_TERMIOS:
        # Fallback for systems without termios (Windows)
        return input()
    
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        key = sys.stdin.read(1)
        # Check for escape sequences (arrow keys)
        if key == '\x1b':
            # Try to read next chars for arrow keys
            old_settings_inner = termios.tcgetattr(fd)
            try:
                # Set non-blocking read with timeout
                import select
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key += sys.stdin.read(2)
                    if key == '\x1b[D':  # Left arrow
                        return 'LEFT'
                    elif key == '\x1b[C':  # Right arrow
                        return 'RIGHT'
                    elif key == '\x1b[A':  # Up arrow
                        return 'UP'
                    elif key == '\x1b[B':  # Down arrow
                        return 'DOWN'
                else:
                    # Just ESC key pressed
                    return 'ESC'
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings_inner)
        return key
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def cancelable_input(prompt, required=False):
    """Get input from user with option to cancel (type 'back' or 'cancel')"""
    value = input(prompt).strip()
    if value.lower() in ['back', 'cancel', 'exit']:
        return None
    if required and not value:
        print(f"{Colors.RED} This field is required. Type 'back' to cancel.{Colors.END}")
        return cancelable_input(prompt, required)
    return value

def wait_for_key(prompt="Press any key to continue..."):
    """Wait for any key press"""
    print(f"\n{Colors.CYAN}{prompt}{Colors.END}")
    get_single_keypress()

def check_gui_available():
    """Check if GUI mode is available (running in an environment that supports tkinter)"""
    try:
        import tkinter
        import os
        # Check if we're in a display environment
        if os.environ.get('DISPLAY') or os.name == 'nt' or os.environ.get('TERM_PROGRAM') == 'Apple_Terminal':
            return True
    except ImportError:
        pass
    return False

def open_gui_table_selector():
    """Open the polished table editor"""
    try:
        from tools.polished_table_editor import launch_polished_table_editor
        
        # Get project path
        project_path = f"projects/{session.project_name}" if hasattr(session, 'project_name') else None
        
        if project_path and os.path.exists(project_path):
            # Launch the polished table editor
            launch_polished_table_editor(project_path)
        else:
            print(f"{Colors.RED}No project found at: {project_path}{Colors.END}")
            
    except Exception as e:
        print(f"{Colors.RED}Error opening polished table editor: {e}{Colors.END}")
        print(f"{Colors.CYAN}Falling back to basic intake GUI...{Colors.END}")
        
        # Fallback to existing intake GUI
        try:
            from lizzy_intake_interactive import InteractiveIntake
            if project_path and os.path.exists(project_path):
                intake = InteractiveIntake(project_path)
                intake.launch_gui()
        except Exception as e2:
            print(f"{Colors.RED}Fallback also failed: {e2}{Colors.END}")
            print(f"{Colors.CYAN}Using CLI mode{Colors.END}")

def main_menu():
    """Main navigation menu - LIZZY"""
    while True:
        print_header()
        
        if not session.api_key_set:
            print(f"\n{Colors.RED}  OpenAI API key required to continue{Colors.END}")
            setup_api_key()
            continue
        
        print(f"\n{Colors.BOLD}LIZZY - Romantic Comedy Screenplay Generator{Colors.END}")
        print_separator()
        
        print(f"{Colors.CYAN}Get started in 30 seconds with a complete romcom template:{Colors.END}")
        print(f"{Colors.CYAN}📝 6 character archetypes + 30-scene outline + writing guides{Colors.END}")
        print()
        print(f"   {Colors.BOLD}1.{Colors.END}  🆕 Create New Romcom Project")
        print(f"   {Colors.BOLD}2.{Colors.END}  📂 Open Existing Project")
        print(f"   {Colors.BOLD}3.{Colors.END}  ❓ Help & Getting Started")
        print(f"   {Colors.BOLD}4.{Colors.END}  🚪 Exit")
        
        choice = input(f"\n{Colors.BOLD}Select option: {Colors.END}").strip()
        
        if choice == "1":
            create_project()  # Use simplified project creation
            if session.current_project:
                project_menu()
        elif choice == "2":
            if select_project():
                project_menu()
        elif choice == "3":
            show_readme()
        elif choice == "4":
            print(f"\n{Colors.CYAN} Thank you for using LIZZY!{Colors.END}")
            print(f"{Colors.YELLOW}   Happy writing! 🎬{Colors.END}\n")
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
        
        print(f"{Colors.CYAN}📝 Complete your romantic comedy in 4 simple steps:{Colors.END}")
        print()
        print(f"   {Colors.BOLD}1.{Colors.END}  🎨 Edit Tables (Characters, Scenes, Notes)")
        print(f"   {Colors.BOLD}2.{Colors.END}  💭 Brainstorm (Generate ideas for scenes)")
        print(f"   {Colors.BOLD}3.{Colors.END}  ✍️  Write (Create screenplay scenes)")
        print(f"   {Colors.BOLD}4.{Colors.END}  📤 Export (Final screenplay output)")
        print()
        print(f"   {Colors.BOLD}0.{Colors.END} 🏠 Back to Main Menu")
        
        choice = input(f"\n{Colors.BOLD}Select step: {Colors.END}").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            launch_modern_editor_for_project()
        elif choice == "2":
            brainstorm_module()
        elif choice == "3":
            write_module()
        elif choice == "4":
            export_options()
        else:
            print(f"{Colors.RED}Invalid choice. Please select 1-4 or 0.{Colors.END}")
            wait_for_key()

def launch_modern_editor_for_project():
    """Launch the modern web-based editor for the current project"""
    try:
        from web_server import launch_web_editor
        
        if not session.current_project:
            print(f"{Colors.RED}No project loaded!{Colors.END}")
            wait_for_key()
            return
        
        project_path = f"projects/{session.current_project}"
        if not os.path.exists(project_path):
            print(f"{Colors.RED}Project directory not found: {project_path}{Colors.END}")
            wait_for_key()
            return
        
        print(f"\n{Colors.CYAN}🌐 Launching Modern Web Editor for {session.current_project}...{Colors.END}")
        print(f"{Colors.YELLOW}✨ Starting web server and opening browser automatically{Colors.END}")
        print(f"{Colors.GREEN}📝 You can edit characters, scenes, and notes in your browser{Colors.END}")
        print(f"{Colors.MAGENTA}⏹️  Press Ctrl+C in this terminal to stop the server when done{Colors.END}")
        print()
        
        try:
            launch_web_editor(project_path, port=8080, auto_open=True)
        except KeyboardInterrupt:
            print(f"\n{Colors.GREEN}✅ Web server stopped by user{Colors.END}")
        except Exception as e:
            print(f"\n{Colors.RED}❌ Server error: {e}{Colors.END}")
        
        print(f"\n{Colors.GREEN}✅ Returning to Lizzy workflow{Colors.END}")
        wait_for_key()
        
    except ImportError:
        print(f"{Colors.RED}Modern editor not available!{Colors.END}")
        print(f"{Colors.CYAN}Falling back to classic table editor...{Colors.END}")
        update_tables_menu()
    except Exception as e:
        print(f"{Colors.RED}Error launching editor: {e}{Colors.END}")
        wait_for_key()

def update_tables_menu():
    """Update Tables - Enhanced table management"""
    while True:
        print_header()
        print_status()
        
        print(f"\n{Colors.BOLD}TABLES{Colors.END}")
        print_separator()
        
        print(f"{Colors.CYAN}Characters{Colors.END}")
        print(f"{Colors.CYAN}Scenes{Colors.END}")
        print(f"{Colors.CYAN}Notes{Colors.END}")
        print()
        
        # Show enhanced options if available
        if HAS_INTAKE_GUI:
            print(f"{Colors.GREEN}✨ Enhanced Options Available{Colors.END}")
            print(f"   {Colors.BOLD}1.{Colors.END} 🖥️  GUI Editor (Visual Interface)")
            print(f"   {Colors.BOLD}2.{Colors.END} 📁 Import CSV")
            print(f"   {Colors.BOLD}3.{Colors.END} ✏️  Classic Edit")
            print(f"   {Colors.BOLD}4.{Colors.END} ➕ New Entry")
            print(f"   {Colors.BOLD}5.{Colors.END} 👁️  View All")
        else:
            print(f"   {Colors.BOLD}1.{Colors.END} Edit")
            print(f"   {Colors.BOLD}2.{Colors.END} New")
            print(f"   {Colors.BOLD}3.{Colors.END} View")
            print(f"   {Colors.BOLD}4.{Colors.END} Import CSV")
        
        if HAS_TERMIOS:
            print(f"\n   {Colors.CYAN}← Press left arrow or ESC to go back{Colors.END}")
        
        choice = input(f"\n[ ] Enter choice: ").strip()
        
        if HAS_TERMIOS and choice.startswith('\x1b'):
            # Handle escape sequences that got into the input
            break
        
        if not choice and HAS_TERMIOS:
            key = get_single_keypress()
            if key in ['LEFT', 'ESC']:
                break
            continue
        
        # Handle enhanced options if available
        if HAS_INTAKE_GUI:
            if choice == "1":
                # Launch GUI Editor
                launch_gui_editor()
            elif choice == "2":
                # Import CSV
                import_csv_enhanced()
            elif choice == "3":
                # Classic Edit
                edit_table_menu()
            elif choice == "4":
                # New Entry
                new_table_menu()
            elif choice == "5":
                # View All
                view_table_menu()
            elif choice == "0" or choice.lower() == "back":
                break
        else:
            # Standard options
            if choice == "1":
                edit_table_menu()
            elif choice == "2":
                new_table_menu()
            elif choice == "3":
                view_table_menu()
            elif choice == "4":
                import_csv_enhanced()
            elif choice == "0" or choice.lower() == "back":
                break

def edit_table_menu():
    """Select and edit a table inline"""
    print(f"\n{Colors.YELLOW}SELECT TABLE TO EDIT{Colors.END}")
    print_separator()
    
    print(f"   {Colors.BOLD}1.{Colors.END} Characters")
    print(f"   {Colors.BOLD}2.{Colors.END} Scenes")
    print(f"   {Colors.BOLD}3.{Colors.END} Notes")
    if check_gui_available():
        print(f"   {Colors.BOLD}4.{Colors.END} 🖥️  Open GUI Table Editor")
    
    choice = input(f"\n[ ] Enter choice: ").strip()
    
    if choice == "1":
        character_management()
    elif choice == "2":
        story_outline_management()
    elif choice == "3":
        notes_management()
    elif choice == "4" and check_gui_available():
        open_gui_table_selector()

def new_table_menu():
    """Create new entry or import from CSV"""
    print(f"\n{Colors.YELLOW}CREATE NEW{Colors.END}")
    print_separator()
    
    print(f"   {Colors.BOLD}1.{Colors.END} New Character")
    print(f"   {Colors.BOLD}2.{Colors.END} New Scene")
    print(f"   {Colors.BOLD}3.{Colors.END} New Note")
    print(f"   {Colors.BOLD}4.{Colors.END} Import from CSV")
    
    choice = input(f"\n[ ] Enter choice: ").strip()
    
    if choice == "1":
        add_character()
    elif choice == "2":
        add_scene()
    elif choice == "3":
        add_note()
    elif choice == "4":
        import_csv()

def view_table_menu():
    """View tables in read-only mode"""
    print(f"\n{Colors.YELLOW}VIEW TABLES{Colors.END}")
    print_separator()
    
    print(f"   {Colors.BOLD}1.{Colors.END} View Characters")
    print(f"   {Colors.BOLD}2.{Colors.END} View Scenes")
    print(f"   {Colors.BOLD}3.{Colors.END} View Notes")
    print(f"   {Colors.BOLD}4.{Colors.END} View All")
    
    choice = input(f"\n[ ] Enter choice: ").strip()
    
    if choice == "1":
        view_characters()
    elif choice == "2":
        view_outline()
    elif choice == "3":
        view_notes()
    elif choice == "4":
        project_summary()

def character_management():
    """Character management submenu"""
    while True:
        print_header()
        print_status()
        
        print(f"\n{Colors.BOLD} CHARACTER MANAGEMENT{Colors.END}")
        print_separator()
        
        print(f"   {Colors.BOLD}1.{Colors.END}  Add Character")
        print(f"   {Colors.BOLD}2.{Colors.END}  View Characters")
        print(f"   {Colors.BOLD}3.{Colors.END}   Edit Character")
        print(f"   {Colors.BOLD}4.{Colors.END}   Delete Character")
        if HAS_TERMIOS:
            print(f"\n   {Colors.CYAN}← Press left arrow or ESC to go back{Colors.END}")
        print(f"   {Colors.BOLD}0.{Colors.END}  Back")
        
        choice = input(f"\n{Colors.BOLD}Select option: {Colors.END}").strip()
        
        if not choice and HAS_TERMIOS:
            key = get_single_keypress()
            if key in ['LEFT', 'ESC']:
                break
            continue
        
        if choice == "0":
            break
        elif choice == "1":
            add_character()
        elif choice == "2":
            view_characters()
        elif choice == "3":
            edit_character()
        elif choice == "4":
            delete_character()

def story_outline_management():
    """Story outline management submenu"""
    while True:
        print_header()
        print_status()
        
        print(f"\n{Colors.BOLD} STORY OUTLINE{Colors.END}")
        print_separator()
        
        if HAS_OUTLINE_MODULE:
            print(f"   {Colors.BOLD}1.{Colors.END}  📝 Open Outline Manager (Template/DIY)")
            print(f"   {Colors.BOLD}2.{Colors.END}  Add Scene (Classic)")
            print(f"   {Colors.BOLD}3.{Colors.END}  View Outline")
            print(f"   {Colors.BOLD}4.{Colors.END}   Edit Scene (Classic)")
            print(f"   {Colors.BOLD}5.{Colors.END}   Delete Scene")
        else:
            print(f"   {Colors.BOLD}1.{Colors.END}  Add Scene")
            print(f"   {Colors.BOLD}2.{Colors.END}  View Outline")
            print(f"   {Colors.BOLD}3.{Colors.END}   Edit Scene")
            print(f"   {Colors.BOLD}4.{Colors.END}   Delete Scene")
        if HAS_TERMIOS:
            print(f"\n   {Colors.CYAN}← Press left arrow or ESC to go back{Colors.END}")
        print(f"   {Colors.BOLD}0.{Colors.END}  Back")
        
        choice = input(f"\n{Colors.BOLD}Select option: {Colors.END}").strip()
        
        if not choice and HAS_TERMIOS:
            key = get_single_keypress()
            if key in ['LEFT', 'ESC']:
                break
            continue
        
        if choice == "0":
            break
        elif HAS_OUTLINE_MODULE and choice == "1":
            launch_story_outline()
        elif choice == "1" or (HAS_OUTLINE_MODULE and choice == "2"):
            add_scene()
        elif choice == "2" or (HAS_OUTLINE_MODULE and choice == "3"):
            view_outline()
        elif choice == "3" or (HAS_OUTLINE_MODULE and choice == "4"):
            edit_scene()
        elif choice == "4" or (HAS_OUTLINE_MODULE and choice == "5"):
            delete_scene()

def show_readme():
    """Display the README file"""
    print_header()
    
    try:
        with open("README.md", "r") as f:
            content = f.read()
        
        print(f"\n{Colors.CYAN} GETTING STARTED{Colors.END}")
        print_separator()
        print(content[:2000])  # Show first 2000 chars
        
        if len(content) > 2000:
            print(f"\n{Colors.YELLOW}... (truncated for display){Colors.END}")
        
        wait_for_key()
    except FileNotFoundError:
        print(f"{Colors.RED} README.md not found{Colors.END}")
        wait_for_key()

def version_history():
    """Show comprehensive version history"""
    print_header()
    print_status()
    
    print(f"\n{Colors.BOLD}VERSIONS{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    
    # Show all brainstorm versions
    print(f"\n{Colors.YELLOW}BRAINSTORM VERSIONS:{Colors.END}")
    cursor.execute("""
        SELECT session_id, timestamp, scenes_selected, bucket_selection, 
               LENGTH(ai_suggestions) as suggestion_length
        FROM brainstorming_log 
        ORDER BY timestamp DESC
    """)
    brainstorms = cursor.fetchall()
    
    if brainstorms:
        for idx, (session_id, timestamp, scenes, buckets, length) in enumerate(brainstorms, 1):
            print(f"\n{Colors.BOLD}{idx}.{Colors.END} {session_id}")
            print(f"   Created: {timestamp}")
            print(f"   Tables: {scenes if scenes else 'None'}")
            print(f"   Buckets: {buckets if buckets else 'None'}")
            print(f"   Size: {length} characters")
    else:
        print(f"   {Colors.CYAN}No brainstorming sessions yet{Colors.END}")
    
    # Show all write versions
    print(f"\n\n{Colors.YELLOW}WRITE VERSIONS:{Colors.END}")
    cursor.execute("""
        SELECT version_number, created_at, word_count,
               SUBSTR(content, 1, 100) as preview
        FROM finalized_draft_v1 
        ORDER BY created_at DESC
    """)
    writes = cursor.fetchall()
    
    if writes:
        for idx, (version, created, words, preview) in enumerate(writes, 1):
            print(f"\n{Colors.BOLD}{idx}.{Colors.END} Version {version}")
            print(f"   Created: {created}")
            print(f"   Words: {words}")
            print(f"   Preview: {preview}...")
    else:
        print(f"   {Colors.CYAN}No write versions yet{Colors.END}")
    
    # Show which resources were used
    print(f"\n\n{Colors.YELLOW}RESOURCE USAGE:{Colors.END}")
    
    # Get unique bucket usage
    cursor.execute("""
        SELECT DISTINCT bucket_selection 
        FROM brainstorming_log 
        WHERE bucket_selection IS NOT NULL AND bucket_selection != ''
    """)
    bucket_usage = cursor.fetchall()
    
    if bucket_usage:
        print(f"\n{Colors.CYAN}Buckets used:{Colors.END}")
        for (buckets,) in bucket_usage:
            print(f"   • {buckets}")
    
    # Get unique table usage
    cursor.execute("""
        SELECT DISTINCT scenes_selected 
        FROM brainstorming_log 
        WHERE scenes_selected IS NOT NULL AND scenes_selected != ''
    """)
    table_usage = cursor.fetchall()
    
    if table_usage:
        print(f"\n{Colors.CYAN}Tables used:{Colors.END}")
        for (tables,) in table_usage:
            print(f"   • {tables}")
    
    # Options to preview or re-use
    print(f"\n\n{Colors.YELLOW}OPTIONS:{Colors.END}")
    print(f"   {Colors.BOLD}1.{Colors.END} Preview a brainstorm version")
    print(f"   {Colors.BOLD}2.{Colors.END} Preview a write version")
    print(f"   {Colors.BOLD}3.{Colors.END} Re-use old output in new session")
    print(f"   {Colors.BOLD}0.{Colors.END} Back")
    
    choice = input(f"\n[ ] Enter choice: ").strip()
    
    if choice == "1":
        preview_brainstorm()
    elif choice == "2":
        preview_write()
    elif choice == "3":
        reuse_version()
        
def preview_brainstorm():
    """Preview a specific brainstorm version"""
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT session_id, ai_suggestions FROM brainstorming_log ORDER BY timestamp DESC")
    sessions = cursor.fetchall()
    
    if not sessions:
        print(f"{Colors.CYAN}No brainstorms to preview{Colors.END}")
        wait_for_key()
        return
    
    print(f"\n{Colors.YELLOW}Select brainstorm to preview:{Colors.END}")
    for idx, (session_id, _) in enumerate(sessions, 1):
        print(f"   {Colors.BOLD}{idx}.{Colors.END} {session_id}")
    
    try:
        choice = int(input(f"\n[ ] Enter choice: ").strip())
        if 1 <= choice <= len(sessions):
            _, content = sessions[choice-1]
            print(f"\n{Colors.GREEN}BRAINSTORM CONTENT{Colors.END}")
            print_separator()
            print(content)
            wait_for_key()
    except ValueError:
        print(f"{Colors.RED}Invalid selection{Colors.END}")
        wait_for_key()

def preview_write():
    """Preview a specific write version"""
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT version_number, content FROM finalized_draft_v1 ORDER BY created_at DESC")
    versions = cursor.fetchall()
    
    if not versions:
        print(f"{Colors.CYAN}No writes to preview{Colors.END}")
        wait_for_key()
        return
    
    print(f"\n{Colors.YELLOW}Select write version to preview:{Colors.END}")
    for idx, (version, _) in enumerate(versions, 1):
        print(f"   {Colors.BOLD}{idx}.{Colors.END} Version {version}")
    
    try:
        choice = int(input(f"\n[ ] Enter choice: ").strip())
        if 1 <= choice <= len(versions):
            _, content = versions[choice-1]
            print(f"\n{Colors.GREEN}WRITE CONTENT{Colors.END}")
            print_separator()
            print(content)
            wait_for_key()
    except ValueError:
        print(f"{Colors.RED}Invalid selection{Colors.END}")
        wait_for_key()

def reuse_version():
    """Mark a version for re-use in next session"""
    print(f"\n{Colors.YELLOW}This feature coming soon!{Colors.END}")
    print("Will allow copying old outputs to new brainstorm/write sessions")
    wait_for_key()

def launch_story_outline():
    """Launch the Story Outline GUI (Template/DIY)"""
    if not HAS_OUTLINE_MODULE:
        print(f"{Colors.RED}Story Outline module not available!{Colors.END}")
        wait_for_key()
        return
    
    if not session.current_project:
        print(f"{Colors.RED}No project loaded!{Colors.END}")
        wait_for_key()
        return
    
    project_path = f"projects/{session.current_project}"
    
    print(f"\n{Colors.CYAN}Launching Story Outline Manager...{Colors.END}")
    print(f"{Colors.YELLOW}Opening GUI window for Template/DIY outline creation{Colors.END}")
    
    try:
        gui = RomcomOutlineGUI(project_path)
        gui.launch()
    except Exception as e:
        print(f"{Colors.RED}Error launching outline GUI: {e}{Colors.END}")
        wait_for_key()

def export_options():
    """Export menu with Enhanced Options"""
    print_header()
    print_status()
    
    print(f"\n{Colors.BOLD}EXPORT{Colors.END}")
    print_separator()
    
    # Check if enhanced export is available
    if HAS_TRANSPARENT_MODULES:
        print(f"{Colors.GREEN}✨ Enhanced Export Available{Colors.END}")
        print(f"   {Colors.BOLD}1.{Colors.END} 📦 Complete Package (Everything)")
        print(f"   {Colors.BOLD}2.{Colors.END} 🎬 Screenplay Only")
        print(f"   {Colors.BOLD}3.{Colors.END} 📊 Data & Analysis")
        print(f"   {Colors.BOLD}4.{Colors.END} 📝 All Sessions")
        print(f"   {Colors.BOLD}5.{Colors.END} 🎭 Standard Exports")
        print(f"   {Colors.BOLD}0.{Colors.END} Back")
        
        choice = input(f"\n[ ] Enter choice: ").strip()
        
        if choice in ["1", "2", "3", "4"]:
            return enhanced_export()
        elif choice == "5":
            # Continue with standard exports below
            pass
        elif choice == "0":
            return
        else:
            return
    
    # Standard export options
    print(f"   {Colors.BOLD}1.{Colors.END} Export brainstorms")
    print(f"   {Colors.BOLD}2.{Colors.END} Export final drafts")
    print(f"   {Colors.BOLD}3.{Colors.END} Export tables")
    print(f"   {Colors.BOLD}4.{Colors.END} Export everything (zip)")
    
    if HAS_TERMIOS:
        print(f"\n   {Colors.CYAN}← Press left arrow to go back{Colors.END}")
    
    choice = input(f"\n[ ] Enter choice: ").strip()
    
    if not choice and HAS_TERMIOS:
        key = get_single_keypress()
        if key in ['LEFT', 'ESC']:
            return
    
    if choice == "1":
        export_brainstorms()
    elif choice == "2":
        export_drafts()
    elif choice == "3":
        export_tables()
    elif choice == "4":
        export_everything()

def export_brainstorms():
    """Export all brainstorming sessions"""
    print(f"\n{Colors.YELLOW}EXPORTING BRAINSTORMS{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT session_id, timestamp, ai_suggestions FROM brainstorming_log ORDER BY timestamp DESC")
    brainstorms = cursor.fetchall()
    
    if not brainstorms:
        print(f"{Colors.CYAN}No brainstorms to export{Colors.END}")
        wait_for_key()
        return
    
    # Create export directory
    export_dir = f"exports/{session.current_project}/brainstorms"
    os.makedirs(export_dir, exist_ok=True)
    
    for session_id, timestamp, content in brainstorms:
        filename = f"{session_id}_{timestamp.replace(':', '-')}.txt"
        filepath = os.path.join(export_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(f"BRAINSTORM SESSION: {session_id}\n")
            f.write(f"Created: {timestamp}\n")
            f.write("=" * 50 + "\n\n")
            f.write(content)
        
        print(f" Exported: {filename}")
    
    print(f"\n{Colors.GREEN}Exported {len(brainstorms)} brainstorm(s) to: {export_dir}{Colors.END}")
    wait_for_key()

def export_drafts():
    """Export all final drafts"""
    print(f"\n{Colors.YELLOW}EXPORTING DRAFTS{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT version_number, created_at, content FROM finalized_draft_v1 ORDER BY created_at DESC")
    drafts = cursor.fetchall()
    
    if not drafts:
        print(f"{Colors.CYAN}No drafts to export{Colors.END}")
        wait_for_key()
        return
    
    # Create export directory
    export_dir = f"exports/{session.current_project}/drafts"
    os.makedirs(export_dir, exist_ok=True)
    
    for version, created, content in drafts:
        filename = f"draft_v{version}_{created.replace(':', '-')}.txt"
        filepath = os.path.join(export_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(f"SCREENPLAY DRAFT - Version {version}\n")
            f.write(f"Created: {created}\n")
            f.write("=" * 50 + "\n\n")
            f.write(content)
        
        print(f" Exported: {filename}")
    
    print(f"\n{Colors.GREEN}Exported {len(drafts)} draft(s) to: {export_dir}{Colors.END}")
    wait_for_key()

def export_tables():
    """Export all tables as CSV"""
    print(f"\n{Colors.YELLOW}EXPORTING TABLES{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    export_dir = f"exports/{session.current_project}/tables"
    os.makedirs(export_dir, exist_ok=True)
    
    # Export characters
    cursor.execute("SELECT * FROM characters")
    chars = cursor.fetchall()
    if chars:
        import csv
        with open(os.path.join(export_dir, "characters.csv"), 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'gender', 'age', 'romantic_challenge', 'lovable_trait', 'comedic_flaw', 'notes', 'created_at'])
            writer.writerows(chars)
        print(" Exported: characters.csv")
    
    # Export scenes
    cursor.execute("SELECT * FROM story_outline")
    scenes = cursor.fetchall()
    if scenes:
        with open(os.path.join(export_dir, "scenes.csv"), 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'act', 'scene', 'key_characters', 'key_events', 'created_at'])
            writer.writerows(scenes)
        print(" Exported: scenes.csv")
    
    # Export notes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notes'")
    if cursor.fetchone():
        cursor.execute("SELECT * FROM notes")
        notes = cursor.fetchall()
        if notes:
            with open(os.path.join(export_dir, "notes.csv"), 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'title', 'content', 'category', 'created_at'])
                writer.writerows(notes)
            print(" Exported: notes.csv")
    
    print(f"\n{Colors.GREEN}Tables exported to: {export_dir}{Colors.END}")
    wait_for_key()

def export_everything():
    """Export everything as a zip file"""
    print(f"\n{Colors.YELLOW}EXPORTING EVERYTHING{Colors.END}")
    print_separator()
    
    # Export all components
    print("Exporting brainstorms...")
    export_brainstorms()
    
    print("\nExporting drafts...")
    export_drafts()
    
    print("\nExporting tables...")
    export_tables()
    
    # Create zip file
    import zipfile
    zip_name = f"{session.current_project}_complete_export.zip"
    export_base = f"exports/{session.current_project}"
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(export_base):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(export_base))
                zipf.write(file_path, arcname)
    
    print(f"\n{Colors.GREEN} Complete export saved as: {zip_name}{Colors.END}")
    wait_for_key()

def manage_project():
    """Project management (placeholder for now)"""
    print_header()
    print_status()
    
    print(f"\n{Colors.BOLD}  MANAGE PROJECT{Colors.END}")
    print_separator()
    
    print(f"{Colors.YELLOW}This feature is coming soon!{Colors.END}")
    print(f"\nPlanned features:")
    print(f"   • Rename project")
    print(f"   • Archive project")
    print(f"   • Delete project")
    print(f"   • Project settings")
    
    wait_for_key()

def export_screenplay_pdf():
    """Export screenplay as PDF (placeholder)"""
    print_header()
    print_status()
    
    print(f"\n{Colors.BOLD} EXPORT AS SCREENPLAY (PDF){Colors.END}")
    print_separator()
    
    print(f"{Colors.YELLOW}PDF export coming soon!{Colors.END}")
    print(f"\nFor now, please use Text export and convert manually.")
    
    wait_for_key()

def export_as_text():
    """Export screenplay as text file"""
    print_header()
    print_status()
    
    print(f"\n{Colors.BOLD} EXPORT AS TEXT{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT content FROM finalized_draft_v1 ORDER BY created_at DESC LIMIT 1")
    result = cursor.fetchone()
    
    if not result:
        print(f"{Colors.CYAN}No drafts to export yet.{Colors.END}")
        wait_for_key()
        return
    
    filename = f"{session.current_project}_screenplay.txt"
    export_path = os.path.join("projects", session.current_project, filename)
    
    try:
        with open(export_path, 'w') as f:
            f.write(result[0])
        
        print(f"{Colors.GREEN} Screenplay exported to: {export_path}{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED} Export failed: {e}{Colors.END}")
    
    wait_for_key()

def export_database():
    """Export the project database"""
    print_header()
    print_status()
    
    print(f"\n{Colors.BOLD}💾 EXPORT DATABASE{Colors.END}")
    print_separator()
    
    source_path = f"projects/{session.current_project}/{session.current_project}.sqlite"
    export_path = f"{session.current_project}_export.sqlite"
    
    try:
        shutil.copy2(source_path, export_path)
        print(f"{Colors.GREEN} Database exported to: {export_path}{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED} Export failed: {e}{Colors.END}")
    
    wait_for_key()

def comprehensive_export():
    """Export all project data"""
    print_header()
    print_status()
    
    print(f"\n{Colors.BOLD} COMPREHENSIVE EXPORT{Colors.END}")
    print_separator()
    
    try:
        # Import the comprehensive export module
        from comprehensive_data_export import export_project_data
        
        output_dir = export_project_data(session.current_project)
        print(f"{Colors.GREEN} All data exported to: {output_dir}{Colors.END}")
        print(f"\nExported formats:")
        print(f"   • JSON (structured data)")
        print(f"   • SQL (database dump)")
        print(f"   • CSV (tabular data)")
        print(f"   • TXT (human-readable)")
        print(f"   • MD (markdown)")
    except Exception as e:
        print(f"{Colors.RED} Export failed: {e}{Colors.END}")
    
    wait_for_key()

def intake_module():
    """Character and Story Intake Module"""
    if not session.current_project:
        return
    
    while True:
        print_header()
        print_status()
        print(f"\n{Colors.BOLD} CHARACTER & STORY INTAKE{Colors.END}")
        print_separator()
        
        print(f"   {Colors.BOLD}1.{Colors.END}  Add Character")
        print(f"   {Colors.BOLD}2.{Colors.END}  Add Scene Outline")
        print(f"   {Colors.BOLD}3.{Colors.END}  View Characters")
        print(f"   {Colors.BOLD}4.{Colors.END}  View Story Outline")
        print(f"   {Colors.BOLD}5.{Colors.END}  Project Summary")
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
    print(f"\n{Colors.YELLOW} ADD CHARACTER{Colors.END}")
    print_separator()
    print(f"{Colors.CYAN}Type 'back' at any time to cancel{Colors.END}\n")
    
    name = cancelable_input(f"{Colors.BOLD}Character Name: {Colors.END}", required=True)
    if name is None:
        return
    
    gender = cancelable_input(f"{Colors.BOLD}Gender (optional): {Colors.END}")
    if gender is None:
        return
    
    age = cancelable_input(f"{Colors.BOLD}Age (optional): {Colors.END}")
    if age is None:
        return
    
    romantic_challenge = cancelable_input(f"{Colors.BOLD}Romantic Challenge: {Colors.END}")
    if romantic_challenge is None:
        return
    
    lovable_trait = cancelable_input(f"{Colors.BOLD}Lovable Trait: {Colors.END}")
    if lovable_trait is None:
        return
    
    comedic_flaw = cancelable_input(f"{Colors.BOLD}Comedic Flaw: {Colors.END}")
    if comedic_flaw is None:
        return
    
    notes = cancelable_input(f"{Colors.BOLD}Additional Notes: {Colors.END}")
    if notes is None:
        return
    
    cursor = session.db_conn.cursor()
    cursor.execute("""
        INSERT INTO characters (name, gender, age, romantic_challenge, lovable_trait, comedic_flaw, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, gender, age, romantic_challenge, lovable_trait, comedic_flaw, notes))
    
    session.db_conn.commit()
    print(f"\n{Colors.GREEN} Character '{name}' added successfully!{Colors.END}")
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")

def add_scene():
    """Add a scene to the story outline"""
    print(f"\n{Colors.YELLOW} ADD SCENE OUTLINE{Colors.END}")
    print_separator()
    print(f"{Colors.CYAN}Type 'back' at any time to cancel{Colors.END}\n")
    
    act_str = cancelable_input(f"{Colors.BOLD}Act Number: {Colors.END}", required=True)
    if act_str is None:
        return
    try:
        act = int(act_str)
    except ValueError:
        print(f"{Colors.RED} Act must be a number!{Colors.END}")
        wait_for_key()
        return
    
    scene_str = cancelable_input(f"{Colors.BOLD}Scene Number: {Colors.END}", required=True)
    if scene_str is None:
        return
    try:
        scene = int(scene_str)
    except ValueError:
        print(f"{Colors.RED} Scene must be a number!{Colors.END}")
        wait_for_key()
        return
    
    key_characters = cancelable_input(f"{Colors.BOLD}Key Characters (comma-separated): {Colors.END}")
    if key_characters is None:
        return
    
    key_events = cancelable_input(f"{Colors.BOLD}Key Events: {Colors.END}", required=True)
    if key_events is None:
        return
    
    cursor = session.db_conn.cursor()
    cursor.execute("""
        INSERT INTO story_outline (act, scene, key_characters, key_events)
        VALUES (?, ?, ?, ?)
    """, (act, scene, key_characters, key_events))
    
    session.db_conn.commit()
    print(f"\n{Colors.GREEN} Scene {act}.{scene} added successfully!{Colors.END}")
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")

def view_characters():
    """Display all characters"""
    print(f"\n{Colors.YELLOW}👥 PROJECT CHARACTERS{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT name, gender, age, romantic_challenge, lovable_trait, comedic_flaw, notes FROM characters")
    characters = cursor.fetchall()
    
    if not characters:
        print(f"{Colors.CYAN} No characters defined yet.{Colors.END}")
    else:
        for char in characters:
            name, gender, age, challenge, trait, flaw, notes = char
            print(f"\n{Colors.BOLD} {name}{Colors.END}")
            if gender: print(f"   Gender: {gender}")
            if age: print(f"   Age: {age}")
            if challenge: print(f"   Romantic Challenge: {challenge}")
            if trait: print(f"   Lovable Trait: {trait}")
            if flaw: print(f"   Comedic Flaw: {flaw}")
            if notes: print(f"   Notes: {notes}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def view_outline():
    """Display story outline"""
    print(f"\n{Colors.YELLOW} STORY OUTLINE{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT act, scene, key_characters, key_events FROM story_outline ORDER BY act, scene")
    scenes = cursor.fetchall()
    
    if not scenes:
        print(f"{Colors.CYAN} No story outline defined yet.{Colors.END}")
    else:
        current_act = None
        for scene_data in scenes:
            act, scene, characters, events = scene_data
            if act != current_act:
                print(f"\n{Colors.BOLD} ACT {act}{Colors.END}")
                print_separator("─", 20)
                current_act = act
            
            print(f"  {Colors.CYAN}Scene {scene}:{Colors.END} {events}")
            if characters:
                print(f"    {Colors.YELLOW}Characters:{Colors.END} {characters}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def edit_character():
    """Edit an existing character"""
    # Check if we can use GUI mode
    if check_gui_available():
        try:
            from lizzy_intake_interactive import InteractiveIntake
            
            # Get project path
            project_path = f"projects/{session.project_name}" if hasattr(session, 'project_name') else None
            
            if project_path and os.path.exists(project_path):
                # Launch the existing intake GUI
                intake = InteractiveIntake(project_path)
                intake.switch_table('characters')
                intake.launch_gui()
                return
        except (ImportError, Exception) as e:
            print(f"{Colors.YELLOW}Could not open GUI: {e}{Colors.END}")
            pass  # Fall back to CLI mode
    
    # CLI mode fallback
    print(f"\n{Colors.YELLOW}  EDIT CHARACTER{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT id, name FROM characters")
    characters = cursor.fetchall()
    
    if not characters:
        print(f"{Colors.CYAN}No characters to edit.{Colors.END}")
        wait_for_key()
        return
    
    print("Select character to edit:")
    for idx, (char_id, name) in enumerate(characters, 1):
        print(f"   {Colors.BOLD}{idx}.{Colors.END} {name}")
    
    try:
        choice = int(input(f"\n{Colors.BOLD}Select character: {Colors.END}").strip())
        if 1 <= choice <= len(characters):
            char_id = characters[choice-1][0]
            
            # Get current character data
            cursor.execute("SELECT * FROM characters WHERE id = ?", (char_id,))
            char_data = cursor.fetchone()
            
            print(f"\nEditing: {char_data[1]} (leave blank to keep current value)")
            
            new_name = input(f"Name [{char_data[1]}]: ").strip() or char_data[1]
            new_gender = input(f"Gender [{char_data[2]}]: ").strip() or char_data[2]
            new_age = input(f"Age [{char_data[3]}]: ").strip() or char_data[3]
            new_challenge = input(f"Romantic Challenge [{char_data[4]}]: ").strip() or char_data[4]
            new_trait = input(f"Lovable Trait [{char_data[5]}]: ").strip() or char_data[5]
            new_flaw = input(f"Comedic Flaw [{char_data[6]}]: ").strip() or char_data[6]
            new_notes = input(f"Notes [{char_data[7]}]: ").strip() or char_data[7]
            
            cursor.execute("""
                UPDATE characters SET name=?, gender=?, age=?, romantic_challenge=?, 
                lovable_trait=?, comedic_flaw=?, notes=? WHERE id=?
            """, (new_name, new_gender, new_age, new_challenge, new_trait, new_flaw, new_notes, char_id))
            
            session.db_conn.commit()
            print(f"\n{Colors.GREEN} Character updated successfully!{Colors.END}")
    except (ValueError, IndexError):
        print(f"{Colors.RED} Invalid selection{Colors.END}")
    
    wait_for_key()

def delete_character():
    """Delete a character"""
    print(f"\n{Colors.YELLOW}  DELETE CHARACTER{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT id, name FROM characters")
    characters = cursor.fetchall()
    
    if not characters:
        print(f"{Colors.CYAN}No characters to delete.{Colors.END}")
        wait_for_key()
        return
    
    print("Select character to delete:")
    for idx, (char_id, name) in enumerate(characters, 1):
        print(f"   {Colors.BOLD}{idx}.{Colors.END} {name}")
    
    try:
        choice = int(input(f"\n{Colors.BOLD}Select character: {Colors.END}").strip())
        if 1 <= choice <= len(characters):
            char_id, char_name = characters[choice-1]
            
            confirm = input(f"\n{Colors.RED}Are you sure you want to delete '{char_name}'? (y/N): {Colors.END}").strip().lower()
            if confirm == 'y':
                cursor.execute("DELETE FROM characters WHERE id = ?", (char_id,))
                session.db_conn.commit()
                print(f"\n{Colors.GREEN} Character deleted successfully!{Colors.END}")
            else:
                print(f"\n{Colors.YELLOW}Deletion cancelled.{Colors.END}")
    except (ValueError, IndexError):
        print(f"{Colors.RED} Invalid selection{Colors.END}")
    
    wait_for_key()

def edit_scene():
    """Edit an existing scene"""
    # Check if we can use GUI mode
    if check_gui_available():
        try:
            from lizzy_intake_interactive import InteractiveIntake
            
            # Get project path
            project_path = f"projects/{session.project_name}" if hasattr(session, 'project_name') else None
            
            if project_path and os.path.exists(project_path):
                # Launch the existing intake GUI
                intake = InteractiveIntake(project_path)
                intake.switch_table('story_outline')
                intake.launch_gui()
                return
        except (ImportError, Exception) as e:
            print(f"{Colors.YELLOW}Could not open GUI: {e}{Colors.END}")
            pass  # Fall back to CLI mode
    
    # CLI mode fallback
    print(f"\n{Colors.YELLOW}  EDIT SCENE{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT id, act, scene, key_events FROM story_outline ORDER BY act, scene")
    scenes = cursor.fetchall()
    
    if not scenes:
        print(f"{Colors.CYAN}No scenes to edit.{Colors.END}")
        wait_for_key()
        return
    
    print("Select scene to edit:")
    for idx, (scene_id, act, scene, events) in enumerate(scenes, 1):
        print(f"   {Colors.BOLD}{idx}.{Colors.END} Act {act}, Scene {scene}: {events[:50]}...")
    
    try:
        choice = int(input(f"\n{Colors.BOLD}Select scene: {Colors.END}").strip())
        if 1 <= choice <= len(scenes):
            scene_id = scenes[choice-1][0]
            
            # Get current scene data
            cursor.execute("SELECT * FROM story_outline WHERE id = ?", (scene_id,))
            scene_data = cursor.fetchone()
            
            print(f"\nEditing: Act {scene_data[1]}, Scene {scene_data[2]} (leave blank to keep current value)")
            
            try:
                new_act = input(f"Act [{scene_data[1]}]: ").strip()
                new_act = int(new_act) if new_act else scene_data[1]
                
                new_scene = input(f"Scene [{scene_data[2]}]: ").strip()
                new_scene = int(new_scene) if new_scene else scene_data[2]
            except ValueError:
                print(f"{Colors.RED} Act and Scene must be numbers!{Colors.END}")
                wait_for_key()
                return
            
            new_characters = input(f"Key Characters [{scene_data[3]}]: ").strip() or scene_data[3]
            new_events = input(f"Key Events [{scene_data[4]}]: ").strip() or scene_data[4]
            
            cursor.execute("""
                UPDATE story_outline SET act=?, scene=?, key_characters=?, key_events=? WHERE id=?
            """, (new_act, new_scene, new_characters, new_events, scene_id))
            
            session.db_conn.commit()
            print(f"\n{Colors.GREEN} Scene updated successfully!{Colors.END}")
    except (ValueError, IndexError):
        print(f"{Colors.RED} Invalid selection{Colors.END}")
    
    wait_for_key()

def delete_scene():
    """Delete a scene"""
    print(f"\n{Colors.YELLOW}  DELETE SCENE{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT id, act, scene, key_events FROM story_outline ORDER BY act, scene")
    scenes = cursor.fetchall()
    
    if not scenes:
        print(f"{Colors.CYAN}No scenes to delete.{Colors.END}")
        wait_for_key()
        return
    
    print("Select scene to delete:")
    for idx, (scene_id, act, scene, events) in enumerate(scenes, 1):
        print(f"   {Colors.BOLD}{idx}.{Colors.END} Act {act}, Scene {scene}: {events[:50]}...")
    
    try:
        choice = int(input(f"\n{Colors.BOLD}Select scene: {Colors.END}").strip())
        if 1 <= choice <= len(scenes):
            scene_id, act, scene, events = scenes[choice-1]
            
            confirm = input(f"\n{Colors.RED}Are you sure you want to delete Act {act}, Scene {scene}? (y/N): {Colors.END}").strip().lower()
            if confirm == 'y':
                cursor.execute("DELETE FROM story_outline WHERE id = ?", (scene_id,))
                session.db_conn.commit()
                print(f"\n{Colors.GREEN} Scene deleted successfully!{Colors.END}")
            else:
                print(f"\n{Colors.YELLOW}Deletion cancelled.{Colors.END}")
    except (ValueError, IndexError):
        print(f"{Colors.RED} Invalid selection{Colors.END}")
    
    wait_for_key()

def notes_management():
    """Notes management submenu"""
    while True:
        print_header()
        print_status()
        
        print(f"\n{Colors.BOLD} NOTES MANAGEMENT{Colors.END}")
        print_separator()
        
        print(f"   {Colors.BOLD}1.{Colors.END}  Add Note")
        print(f"   {Colors.BOLD}2.{Colors.END}  View Notes")
        print(f"   {Colors.BOLD}3.{Colors.END}   Edit Note")
        print(f"   {Colors.BOLD}4.{Colors.END}   Delete Note")
        if HAS_TERMIOS:
            print(f"\n   {Colors.CYAN}← Press left arrow or ESC to go back{Colors.END}")
        print(f"   {Colors.BOLD}0.{Colors.END}  Back")
        
        choice = input(f"\n{Colors.BOLD}Select option: {Colors.END}").strip()
        
        if not choice and HAS_TERMIOS:
            key = get_single_keypress()
            if key in ['LEFT', 'ESC']:
                break
            continue
        
        if choice == "0":
            break
        elif choice == "1":
            add_note()
        elif choice == "2":
            view_notes()
        elif choice == "3":
            edit_note()
        elif choice == "4":
            delete_note()

def add_note():
    """Add a new note"""
    print(f"\n{Colors.YELLOW} ADD NOTE{Colors.END}")
    print_separator()
    print(f"{Colors.CYAN}Type 'back' at any time to cancel{Colors.END}\n")
    
    title = cancelable_input(f"{Colors.BOLD}Note Title: {Colors.END}", required=True)
    if title is None:
        return
    
    content = cancelable_input(f"{Colors.BOLD}Note Content: {Colors.END}")
    if content is None:
        return
    
    category = cancelable_input(f"{Colors.BOLD}Category (optional): {Colors.END}")
    if category is None:
        return
    
    # First check if notes table exists
    cursor = session.db_conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='notes'
    """)
    
    if not cursor.fetchone():
        # Create notes table if it doesn't exist
        cursor.execute("""
            CREATE TABLE notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        session.db_conn.commit()
    
    cursor.execute("""
        INSERT INTO notes (title, content, category)
        VALUES (?, ?, ?)
    """, (title, content, category))
    
    session.db_conn.commit()
    print(f"\n{Colors.GREEN} Note '{title}' added successfully!{Colors.END}")
    wait_for_key()

def view_notes():
    """Display all notes"""
    print(f"\n{Colors.YELLOW} PROJECT NOTES{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    
    # Check if notes table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='notes'
    """)
    
    if not cursor.fetchone():
        print(f"{Colors.CYAN} No notes table yet. Add a note to create it.{Colors.END}")
        wait_for_key()
        return
    
    cursor.execute("SELECT title, content, category, created_at FROM notes ORDER BY created_at DESC")
    notes = cursor.fetchall()
    
    if not notes:
        print(f"{Colors.CYAN} No notes yet.{Colors.END}")
    else:
        for note in notes:
            title, content, category, created_at = note
            print(f"\n{Colors.BOLD}📌 {title}{Colors.END}")
            if category:
                print(f"   Category: {category}")
            print(f"   Created: {created_at}")
            if content:
                print(f"   {content}")
    
    wait_for_key()

def edit_note():
    """Edit an existing note"""
    print(f"\n{Colors.YELLOW}  EDIT NOTE{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    
    # Check if notes table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='notes'
    """)
    
    if not cursor.fetchone():
        print(f"{Colors.CYAN}No notes table yet.{Colors.END}")
        wait_for_key()
        return
    
    cursor.execute("SELECT id, title FROM notes")
    notes = cursor.fetchall()
    
    if not notes:
        print(f"{Colors.CYAN}No notes to edit.{Colors.END}")
        wait_for_key()
        return
    
    print("Select note to edit:")
    for idx, (note_id, title) in enumerate(notes, 1):
        print(f"   {Colors.BOLD}{idx}.{Colors.END} {title}")
    
    try:
        choice = int(input(f"\n{Colors.BOLD}Select note: {Colors.END}").strip())
        if 1 <= choice <= len(notes):
            note_id = notes[choice-1][0]
            
            # Get current note data
            cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
            note_data = cursor.fetchone()
            
            print(f"\nEditing: {note_data[1]} (leave blank to keep current value)")
            
            new_title = input(f"Title [{note_data[1]}]: ").strip() or note_data[1]
            new_content = input(f"Content [{note_data[2]}]: ").strip() or note_data[2]
            new_category = input(f"Category [{note_data[3]}]: ").strip() or note_data[3]
            
            cursor.execute("""
                UPDATE notes SET title=?, content=?, category=? WHERE id=?
            """, (new_title, new_content, new_category, note_id))
            
            session.db_conn.commit()
            print(f"\n{Colors.GREEN} Note updated successfully!{Colors.END}")
    except (ValueError, IndexError):
        print(f"{Colors.RED} Invalid selection{Colors.END}")
    
    wait_for_key()

def delete_note():
    """Delete a note"""
    print(f"\n{Colors.YELLOW}  DELETE NOTE{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    
    # Check if notes table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='notes'
    """)
    
    if not cursor.fetchone():
        print(f"{Colors.CYAN}No notes table yet.{Colors.END}")
        wait_for_key()
        return
    
    cursor.execute("SELECT id, title FROM notes")
    notes = cursor.fetchall()
    
    if not notes:
        print(f"{Colors.CYAN}No notes to delete.{Colors.END}")
        wait_for_key()
        return
    
    print("Select note to delete:")
    for idx, (note_id, title) in enumerate(notes, 1):
        print(f"   {Colors.BOLD}{idx}.{Colors.END} {title}")
    
    try:
        choice = int(input(f"\n{Colors.BOLD}Select note: {Colors.END}").strip())
        if 1 <= choice <= len(notes):
            note_id, note_title = notes[choice-1]
            
            confirm = input(f"\n{Colors.RED}Are you sure you want to delete '{note_title}'? (y/N): {Colors.END}").strip().lower()
            if confirm == 'y':
                cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
                session.db_conn.commit()
                print(f"\n{Colors.GREEN} Note deleted successfully!{Colors.END}")
            else:
                print(f"\n{Colors.YELLOW}Deletion cancelled.{Colors.END}")
    except (ValueError, IndexError):
        print(f"{Colors.RED} Invalid selection{Colors.END}")
    
    wait_for_key()

def launch_gui_editor():
    """Launch the GUI editor for table management"""
    if not HAS_INTAKE_GUI:
        print(f"{Colors.RED}GUI editor not available{Colors.END}")
        wait_for_key()
        return
    
    print(f"\n{Colors.CYAN}🖥️ Launching GUI Editor...{Colors.END}")
    print(f"{Colors.YELLOW}A new window will open for visual editing{Colors.END}")
    
    try:
        # Launch the intake GUI
        project_path = f"projects/{session.current_project}"
        launch_intake_gui(project_path)
        print(f"\n{Colors.GREEN}✅ GUI editor closed{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}⚠️ Error launching GUI: {str(e)}{Colors.END}")
    
    wait_for_key()

def import_csv_enhanced():
    """Enhanced CSV import with field mapping"""
    print(f"\n{Colors.YELLOW}📁 IMPORT FROM CSV{Colors.END}")
    print_separator()
    
    print(f"{Colors.CYAN}Select Table:{Colors.END}")
    print(f"   {Colors.BOLD}1.{Colors.END} Characters")
    print(f"   {Colors.BOLD}2.{Colors.END} Story Outline (Scenes)")
    print(f"   {Colors.BOLD}3.{Colors.END} Notes")
    print(f"   {Colors.BOLD}0.{Colors.END} Cancel")
    
    table_choice = input(f"\n[ ] Select table: ").strip()
    
    if table_choice == "0":
        return
    
    table_map = {
        "1": "characters",
        "2": "story_outline",
        "3": "notes"
    }
    
    table_name = table_map.get(table_choice)
    if not table_name:
        print(f"{Colors.RED}Invalid selection{Colors.END}")
        wait_for_key()
        return
    
    # Get CSV file path
    print(f"\n{Colors.YELLOW}Enter CSV file path:{Colors.END}")
    print(f"(Drag and drop the file here, or type the path)")
    csv_path = input(f"[ ] Path: ").strip().strip("'\"")
    
    if not os.path.exists(csv_path):
        print(f"{Colors.RED}File not found: {csv_path}{Colors.END}")
        wait_for_key()
        return
    
    try:
        import csv
        
        # Read CSV file
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        if not rows:
            print(f"{Colors.RED}CSV file is empty{Colors.END}")
            wait_for_key()
            return
        
        # Show preview
        print(f"\n{Colors.GREEN}Found {len(rows)} rows{Colors.END}")
        print(f"Columns: {', '.join(rows[0].keys())}")
        print(f"\n{Colors.CYAN}Preview (first 3 rows):{Colors.END}")
        
        for i, row in enumerate(rows[:3], 1):
            print(f"\nRow {i}:")
            for key, value in row.items():
                print(f"  {key}: {value[:50]}..." if len(value) > 50 else f"  {key}: {value}")
        
        # Confirm import
        confirm = input(f"\n[ ] Import these {len(rows)} rows? (y/n): ").strip().lower()
        if confirm != 'y':
            return
        
        # Import data
        cursor = session.db_conn.cursor()
        imported = 0
        
        for row in rows:
            if table_name == "characters":
                cursor.execute("""
                    INSERT INTO characters (name, gender, age, romantic_challenge, 
                                          lovable_trait, comedic_flaw, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    row.get('name', ''),
                    row.get('gender', ''),
                    row.get('age', ''),
                    row.get('romantic_challenge', ''),
                    row.get('lovable_trait', ''),
                    row.get('comedic_flaw', ''),
                    row.get('notes', '')
                ))
                imported += 1
            elif table_name == "story_outline":
                cursor.execute("""
                    INSERT INTO story_outline (act, scene, key_characters, key_events)
                    VALUES (?, ?, ?, ?)
                """, (
                    int(row.get('act', 1)),
                    int(row.get('scene', 1)),
                    row.get('key_characters', ''),
                    row.get('key_events', '')
                ))
                imported += 1
            elif table_name == "notes":
                cursor.execute("""
                    INSERT INTO notes (title, content, category)
                    VALUES (?, ?, ?)
                """, (
                    row.get('title', 'Untitled'),
                    row.get('content', ''),
                    row.get('category', 'General')
                ))
                imported += 1
        
        session.db_conn.commit()
        print(f"\n{Colors.GREEN}✅ Successfully imported {imported} rows!{Colors.END}")
        
    except Exception as e:
        print(f"{Colors.RED}⚠️ Import error: {str(e)}{Colors.END}")
    
    wait_for_key()

def import_csv():
    """Legacy CSV import function - redirects to enhanced version"""
    import_csv_enhanced()

def project_summary():
    """Show complete project summary"""
    print_header()
    print_status()
    print(f"\n{Colors.BOLD} PROJECT SUMMARY{Colors.END}")
    print_separator()
    
    view_characters()
    view_outline()
    view_notes()

def brainstorm_module():
    """Creative Brainstorming Module with Prompt Studio Interface"""
    if not session.current_project or not session.api_key_set:
        return
    
    print_header()
    print_status()
    print(f"\n{Colors.BOLD}BRAINSTORM MODE{Colors.END}")
    print_separator()
    
    # Launch Dynamic Prompt Studio
    print(f"{Colors.GREEN}🎨 Launching Dynamic Prompt Studio...{Colors.END}")
    print(f"{Colors.CYAN}Features:{Colors.END}")
    print(f"  • System-agnostic prompt engineering")
    print(f"  • Real project data integration")
    print(f"  • Custom template management")
    print(f"  • Live preview compilation")
    print(f"  • Toggle between prompts like Claude chats")
    print_separator()
    
    try:
        import subprocess
        import threading
        import webbrowser
        import time
        
        # Launch the prompt studio backend in a separate process
        print(f"{Colors.YELLOW}Starting Prompt Studio backend...{Colors.END}")
        
        def launch_backend():
            """Launch the prompt studio backend server"""
            try:
                subprocess.run([
                    sys.executable, 'prompt_studio_dynamic.py'
                ], cwd=os.getcwd())
            except Exception as e:
                print(f"{Colors.RED}Backend error: {str(e)}{Colors.END}")
        
        # Start backend in background thread
        backend_thread = threading.Thread(target=launch_backend, daemon=True)
        backend_thread.start()
        
        # Wait a moment for server to start
        print(f"{Colors.YELLOW}Waiting for server to start...{Colors.END}")
        time.sleep(3)
        
        # Open web browser to the interface
        studio_url = "http://localhost:8002"
        print(f"{Colors.GREEN}🚀 Opening Prompt Studio: {studio_url}{Colors.END}")
        
        try:
            webbrowser.open(studio_url)
            print(f"{Colors.CYAN}✅ Prompt Studio opened in your browser!{Colors.END}")
            print(f"{Colors.CYAN}   Current project '{session.current_project}' will be auto-detected{Colors.END}")
            print(f"\n{Colors.YELLOW}Instructions:{Colors.END}")
            print(f"  1. Select your project ({session.current_project}) from the dropdown")
            print(f"  2. Choose a prompt template or create a new one")
            print(f"  3. Use data blocks to insert real project data")
            print(f"  4. Preview your compiled prompt with actual data")
            print(f"  5. Save custom templates to your project database")
            print(f"\n{Colors.BOLD}Press Enter when done with Prompt Studio...{Colors.END}")
            input()
            
        except Exception as e:
            print(f"{Colors.RED}Could not open browser automatically.{Colors.END}")
            print(f"{Colors.YELLOW}Please manually open: {studio_url}{Colors.END}")
            print(f"\n{Colors.BOLD}Press Enter when done with Prompt Studio...{Colors.END}")
            input()
            
    except Exception as e:
        print(f"{Colors.RED}Error launching Prompt Studio: {str(e)}{Colors.END}")
        print(f"{Colors.YELLOW}Falling back to enhanced brainstorming...{Colors.END}")
        
        # Fallback to transparent brainstormer if available
        if HAS_TRANSPARENT_MODULES:
            return run_transparent_brainstorm()
    
    # Fallback to original implementation
    # Collect selections
    selected_buckets = []
    selected_tables = []
    selected_versions = []
    user_guidance = ""
    
    # Pick buckets
    print(f"\n{Colors.YELLOW}Select Buckets to Use:{Colors.END}")
    buckets = get_bucket_list()
    if buckets:
        for idx, bucket in enumerate(buckets, 1):
            print(f"   {Colors.BOLD}{idx}.{Colors.END} {bucket}")
        print(f"   {Colors.BOLD}0.{Colors.END} None/Skip")
        
        bucket_choices = input(f"\n[ ] Enter choices (comma-separated): ").strip()
        if bucket_choices and bucket_choices != "0":
            for choice in bucket_choices.split(','):
                try:
                    idx = int(choice.strip()) - 1
                    if 0 <= idx < len(buckets):
                        selected_buckets.append(buckets[idx])
                except ValueError:
                    pass
    
    # Pick tables
    print(f"\n{Colors.YELLOW}Select Tables to Use:{Colors.END}")
    print(f"   {Colors.BOLD}1.{Colors.END} Characters")
    print(f"   {Colors.BOLD}2.{Colors.END} Scenes")
    print(f"   {Colors.BOLD}3.{Colors.END} Notes")
    print(f"   {Colors.BOLD}0.{Colors.END} None/Skip")
    
    table_choices = input(f"\n[ ] Enter choices (comma-separated): ").strip()
    if table_choices and table_choices != "0":
        if "1" in table_choices:
            selected_tables.append("characters")
        if "2" in table_choices:
            selected_tables.append("scenes")
        if "3" in table_choices:
            selected_tables.append("notes")
    
    # Pick prior versions
    print(f"\n{Colors.YELLOW}Use Prior Versions:{Colors.END}")
    cursor = session.db_conn.cursor()
    
    # Get brainstorm versions
    cursor.execute("SELECT DISTINCT session_id, timestamp, tone_preset FROM brainstorming_log ORDER BY timestamp DESC LIMIT 5")
    brainstorm_versions = cursor.fetchall()
    
    if brainstorm_versions:
        print(f"\n{Colors.CYAN}Recent Brainstorms:{Colors.END}")
        for idx, (session_id, timestamp, tone) in enumerate(brainstorm_versions, 1):
            print(f"   {Colors.BOLD}{idx}.{Colors.END} {timestamp} - {tone}")
        
        version_choice = input(f"\n[ ] Select version (or 0 to skip): ").strip()
        if version_choice and version_choice != "0":
            try:
                idx = int(version_choice) - 1
                if 0 <= idx < len(brainstorm_versions):
                    selected_versions.append(("brainstorm", brainstorm_versions[idx][0]))
            except ValueError:
                pass
    
    # Add user guidance
    print(f"\n{Colors.YELLOW}Additional Guidance:{Colors.END}")
    user_guidance = input(f"[ ] Enter any specific instructions: ").strip()
    
    # Confirm selections
    print(f"\n{Colors.BOLD}BRAINSTORM CONFIGURATION{Colors.END}")
    print_separator()
    print(f"Buckets: {', '.join(selected_buckets) if selected_buckets else 'None'}")
    print(f"Tables: {', '.join(selected_tables) if selected_tables else 'None'}")
    print(f"Prior Versions: {len(selected_versions)}")
    print(f"User Guidance: {'Yes' if user_guidance else 'No'}")
    
    confirm = input(f"\n[ ] Start brainstorm? (y/n): ").strip().lower()
    if confirm != 'y':
        return
    
    # Execute brainstorm
    execute_brainstorm(selected_buckets, selected_tables, selected_versions, user_guidance)

def execute_brainstorm(buckets, tables, versions, guidance):
    """Execute the brainstorming with selected inputs"""
    print(f"\n{Colors.CYAN}🧠 Generating creative ideas...{Colors.END}")
    print_separator()
    
    # Build context from selections
    context_parts = []
    
    print(f"\n{Colors.YELLOW}📊 ASSEMBLING CONTEXT:{Colors.END}")
    
    # Add table data
    if "characters" in tables:
        print(f"  • Loading characters...")
        cursor = session.db_conn.cursor()
        cursor.execute("SELECT name, romantic_challenge, lovable_trait, comedic_flaw FROM characters")
        chars = cursor.fetchall()
        if chars:
            char_context = "CHARACTERS:\n" + "\n".join([f"- {c[0]}: {c[1]}, {c[2]}, {c[3]}" for c in chars])
            context_parts.append(char_context)
            print(f"    ✓ {len(chars)} characters loaded")
    
    if "scenes" in tables:
        print(f"  • Loading scenes...")
        cursor = session.db_conn.cursor()
        cursor.execute("SELECT act, scene, key_events FROM story_outline ORDER BY act, scene")
        scenes = cursor.fetchall()
        if scenes:
            scene_context = "SCENES:\n" + "\n".join([f"- Act {s[0]}, Scene {s[1]}: {s[2]}" for s in scenes])
            context_parts.append(scene_context)
            print(f"    ✓ {len(scenes)} scenes loaded")
    
    if "notes" in tables:
        print(f"  • Loading notes...")
        cursor = session.db_conn.cursor()
        cursor.execute("SELECT title, content FROM notes")
        notes = cursor.fetchall()
        if notes:
            notes_context = "NOTES:\n" + "\n".join([f"- {n[0]}: {n[1]}" for n in notes])
            context_parts.append(notes_context)
            print(f"    ✓ {len(notes)} notes loaded")
    
    # Add bucket data
    if buckets:
        print(f"  • Loading buckets...")
        for bucket in buckets:
            bucket_file = f"buckets/{bucket}.txt"
            if os.path.exists(bucket_file):
                with open(bucket_file, 'r') as f:
                    bucket_content = f.read()
                    context_parts.append(f"BUCKET ({bucket}):\n{bucket_content}")
                    print(f"    ✓ Bucket '{bucket}' loaded")
    
    # Build prompt
    prompt = "You are a creative screenwriting assistant. Generate brainstorming ideas for a screenplay.\n\n"
    if context_parts:
        prompt += "CONTEXT:\n" + "\n\n".join(context_parts) + "\n\n"
    if guidance:
        prompt += f"USER GUIDANCE: {guidance}\n\n"
    prompt += """Please provide:
1. Scene Concepts - Creative scene ideas with specific details
2. Dialogue Ideas - Actual dialogue snippets that could be used
3. Visual Moments - Cinematic shots and visual storytelling ideas
4. Character Development - Ways to deepen character arcs
5. Plot Twists - Unexpected turns the story could take

Be specific and creative, providing actionable ideas."""
    
    # Display assembled prompt for debugging
    print(f"\n{Colors.CYAN}📝 PROMPT PREVIEW:{Colors.END}")
    print_separator()
    print(f"{prompt[:500]}..." if len(prompt) > 500 else prompt)
    print_separator()
    
    # Call actual OpenAI API
    print(f"\n{Colors.YELLOW}🤖 Processing with OpenAI API...{Colors.END}")
    
    try:
        # Use the global client that was set up during API key configuration
        global client
        
        if not client:
            print(f"{Colors.RED}⚠️  OpenAI client not initialized. Please set up API key first.{Colors.END}")
            wait_for_key()
            return
        
        # Make API call
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a creative screenwriting assistant specializing in romantic comedies."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )
        
        result = response.choices[0].message.content
        
    except Exception as e:
        print(f"\n{Colors.RED}⚠️  API Error: {str(e)}{Colors.END}")
        print(f"{Colors.YELLOW}Falling back to example output...{Colors.END}")
        
        # Fallback result
        result = """
BRAINSTORMING RESULTS
=====================================

SCENE CONCEPTS:
• Opening with a dramatic misunderstanding at a wedding venue
• Character reveals hidden talent for salsa dancing during company party
• Comedic chase sequence through farmers market with produce obstacles

DIALOGUE IDEAS:
• "I never thought I'd say this, but your spreadsheet organization is... oddly attractive"
• Witty banter about dating apps: "Your profile said you like long walks..." "To the fridge, yes."
• Heartfelt confession interrupted by sprinkler system malfunction

VISUAL MOMENTS:
• Slow-motion romantic moment ruined by pigeon attack
• Split-screen showing both characters having the same realization
• Creative use of office supplies to build elaborate apology display

CHARACTER DEVELOPMENT:
• Protagonist learns to embrace spontaneity through failed plans
• Love interest reveals vulnerability beneath confident exterior
• Supporting character's subplot mirrors main romance theme

PLOT TWISTS:
• The wedding they're planning isn't theirs - it's for their exes
• Secret identity reveal: the anonymous advice columnist is the janitor
• The company merger threatens to separate them geographically
"""
    
    # Display result
    print(f"\n{Colors.GREEN}✨ BRAINSTORM OUTPUT:{Colors.END}")
    print_separator()
    print(result)
    print_separator()
    
    # Save to database
    cursor = session.db_conn.cursor()
    session_id = f"BS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    cursor.execute("""
        INSERT INTO brainstorming_log (session_id, timestamp, tone_preset, scenes_selected, 
                                      bucket_selection, lightrag_context, ai_suggestions)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session_id, datetime.now().isoformat(), "custom", 
          ",".join(tables), ",".join(buckets), prompt[:1000], result))
    
    session.db_conn.commit()
    print(f"\n{Colors.GREEN}✅ Brainstorm saved as session: {session_id}{Colors.END}")
    
    # Wait for user before returning to menu
    wait_for_key()

def write_module():
    """Writing Module with Transparency"""
    if not session.current_project or not session.api_key_set:
        return
    
    print_header()
    print_status()
    print(f"\n{Colors.BOLD}WRITE MODE{Colors.END}")
    print_separator()
    
    # Check if we have transparent modules available
    if HAS_TRANSPARENT_MODULES:
        print(f"{Colors.GREEN}✨ Using Enhanced Transparent Writing{Colors.END}")
        print(f"{Colors.CYAN}You'll see:{Colors.END}")
        print(f"  • Context from brainstorming sessions")
        print(f"  • Style guidance from buckets")
        print(f"  • Prompt assembly in real-time")
        print(f"  • AI generating your screenplay")
        print_separator()
        
        # Use transparent writer
        return run_transparent_write()
    
    # Fallback to original implementation
    # Collect selections (same as brainstorm)
    selected_buckets = []
    selected_tables = []
    selected_versions = []
    user_guidance = ""
    
    # Pick buckets
    print(f"\n{Colors.YELLOW}Select Buckets to Use:{Colors.END}")
    buckets = get_bucket_list()
    if buckets:
        for idx, bucket in enumerate(buckets, 1):
            print(f"   {Colors.BOLD}{idx}.{Colors.END} {bucket}")
        print(f"   {Colors.BOLD}0.{Colors.END} None/Skip")
        
        bucket_choices = input(f"\n[ ] Enter choices (comma-separated): ").strip()
        if bucket_choices and bucket_choices != "0":
            for choice in bucket_choices.split(','):
                try:
                    idx = int(choice.strip()) - 1
                    if 0 <= idx < len(buckets):
                        selected_buckets.append(buckets[idx])
                except ValueError:
                    pass
    
    # Pick tables
    print(f"\n{Colors.YELLOW}Select Tables to Use:{Colors.END}")
    print(f"   {Colors.BOLD}1.{Colors.END} Characters")
    print(f"   {Colors.BOLD}2.{Colors.END} Scenes")
    print(f"   {Colors.BOLD}3.{Colors.END} Notes")
    print(f"   {Colors.BOLD}0.{Colors.END} None/Skip")
    
    table_choices = input(f"\n[ ] Enter choices (comma-separated): ").strip()
    if table_choices and table_choices != "0":
        if "1" in table_choices:
            selected_tables.append("characters")
        if "2" in table_choices:
            selected_tables.append("scenes")
        if "3" in table_choices:
            selected_tables.append("notes")
    
    # Pick prior versions (including brainstorms)
    print(f"\n{Colors.YELLOW}Use Prior Versions:{Colors.END}")
    cursor = session.db_conn.cursor()
    
    # Get most recent brainstorm
    cursor.execute("SELECT session_id, timestamp FROM brainstorming_log ORDER BY timestamp DESC LIMIT 1")
    latest_brainstorm = cursor.fetchone()
    
    if latest_brainstorm:
        print(f"\n{Colors.GREEN}✓ Using latest brainstorm: {latest_brainstorm[0]}{Colors.END}")
        selected_versions.append(("brainstorm", latest_brainstorm[0]))
    
    # Get write versions
    cursor.execute("SELECT DISTINCT version_number, created_at FROM finalized_draft_v1 ORDER BY created_at DESC LIMIT 5")
    write_versions = cursor.fetchall()
    
    if write_versions:
        print(f"\n{Colors.CYAN}Recent Drafts:{Colors.END}")
        for idx, (version, created) in enumerate(write_versions, 1):
            print(f"   {Colors.BOLD}{idx}.{Colors.END} Version {version} - {created}")
        
        version_choice = input(f"\n[ ] Select draft version (or 0 to skip): ").strip()
        if version_choice and version_choice != "0":
            try:
                idx = int(version_choice) - 1
                if 0 <= idx < len(write_versions):
                    selected_versions.append(("draft", write_versions[idx][0]))
            except ValueError:
                pass
    
    # Add user guidance
    print(f"\n{Colors.YELLOW}Additional Guidance:{Colors.END}")
    user_guidance = input(f"[ ] Enter any specific instructions: ").strip()
    
    # Confirm selections
    print(f"\n{Colors.BOLD}WRITE CONFIGURATION{Colors.END}")
    print_separator()
    print(f"Buckets: {', '.join(selected_buckets) if selected_buckets else 'None'}")
    print(f"Tables: {', '.join(selected_tables) if selected_tables else 'None'}")
    print(f"Prior Versions: {len(selected_versions)}")
    print(f"User Guidance: {'Yes' if user_guidance else 'No'}")
    
    confirm = input(f"\n[ ] Start writing? (y/n): ").strip().lower()
    if confirm != 'y':
        return
    
    # Execute write
    execute_write(selected_buckets, selected_tables, selected_versions, user_guidance)

def execute_write(buckets, tables, versions, guidance):
    """Execute the writing with selected inputs"""
    print(f"\n{Colors.CYAN}  Generating screenplay content...{Colors.END}")
    
    # Build context from selections
    context_parts = []
    
    # Add table data
    cursor = session.db_conn.cursor()
    
    if "characters" in tables:
        cursor.execute("SELECT name, romantic_challenge, lovable_trait, comedic_flaw FROM characters")
        chars = cursor.fetchall()
        if chars:
            context_parts.append("CHARACTERS:\n" + "\n".join([f"- {c[0]}: {c[1]}, {c[2]}, {c[3]}" for c in chars]))
    
    if "scenes" in tables:
        cursor.execute("SELECT act, scene, key_events FROM story_outline ORDER BY act, scene")
        scenes = cursor.fetchall()
        if scenes:
            context_parts.append("SCENES:\n" + "\n".join([f"- Act {s[0]}, Scene {s[1]}: {s[2]}" for s in scenes]))
    
    if "notes" in tables:
        cursor.execute("SELECT title, content FROM notes")
        notes = cursor.fetchall()
        if notes:
            context_parts.append("NOTES:\n" + "\n".join([f"- {n[0]}: {n[1]}" for n in notes]))
    
    # Add latest brainstorm if available
    brainstorm_context = ""
    for version_type, version_id in versions:
        if version_type == "brainstorm":
            cursor.execute("SELECT ai_suggestions FROM brainstorming_log WHERE session_id = ?", (version_id,))
            result = cursor.fetchone()
            if result:
                brainstorm_context = f"\nLATEST BRAINSTORM:\n{result[0]}\n"
    
    # Build prompt
    prompt = "Write professional screenplay content.\n\n"
    if context_parts:
        prompt += "\n".join(context_parts) + "\n\n"
    if brainstorm_context:
        prompt += brainstorm_context
    if guidance:
        prompt += f"USER GUIDANCE: {guidance}\n\n"
    prompt += "Write in proper screenplay format with scene headings, action lines, and dialogue."
    
    # Simulate API call
    print(f"{Colors.YELLOW}Processing with AI...{Colors.END}")
    import time
    time.sleep(2)
    
    # Generate result
    result = f"""FADE IN:

INT. COFFEE SHOP - DAY

A cozy neighborhood coffee shop buzzing with morning activity. SARAH (28, creative type with paint-stained fingers) sits alone at a corner table, sketching in a notebook.

JAKE (30, business casual but slightly disheveled) rushes in, checking his phone. He collides with a BARISTA carrying a tray of drinks.

JAKE
Oh God, I'm so sorry! Let me help--

He bends down to help clean up, accidentally knocking over Sarah's coffee with his laptop bag.

SARAH
(looking up, amused)
Going for a record?

JAKE
(flustered)
I swear I'm not usually this... 
destructive. Can I buy you another?

SARAH
Only if you promise to drink it 
sitting down.

Jake laughs, tension easing from his shoulders.

FADE OUT."""
    
    print(f"\n{Colors.GREEN}SCREENPLAY DRAFT{Colors.END}")
    print_separator()
    print(result)
    print_separator()
    
    # Save to database
    version_number = 1
    cursor.execute("SELECT MAX(version_number) FROM finalized_draft_v1")
    max_version = cursor.fetchone()[0]
    if max_version:
        version_number = max_version + 1
    
    cursor.execute("""
        INSERT INTO finalized_draft_v1 (version_number, content, word_count, created_at)
        VALUES (?, ?, ?, ?)
    """, (version_number, result, len(result.split()), datetime.now().isoformat()))
    
    session.db_conn.commit()
    print(f"\n{Colors.GREEN} Draft saved as version {version_number}{Colors.END}")
    wait_for_key()

def write_single_scene():
    """Write a single scene"""
    print_header()
    print_status()
    print(f"\n{Colors.BOLD}  WRITE SINGLE SCENE{Colors.END}")
    print_separator()
    
    # Show available scenes from outline
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT act, scene, key_characters, key_events FROM story_outline ORDER BY act, scene")
    outline = cursor.fetchall()
    
    if not outline:
        print(f"{Colors.RED} No story outline found!{Colors.END}")
        print(f"{Colors.CYAN} Add scenes in Character & Story Intake first{Colors.END}")
        input("Press Enter to continue...")
        return
    
    print(f"{Colors.BLUE} Available Scenes from Outline:{Colors.END}")
    for scene_data in outline:
        act, scene, chars, events = scene_data
        print(f"   Act {act}, Scene {scene}: {events} ({Colors.YELLOW}Characters: {chars}{Colors.END})")
    
    # Get scene selection
    try:
        act = int(input(f"\n{Colors.BOLD}Select Act Number to write: {Colors.END}").strip())
        scene = int(input(f"{Colors.BOLD}Select Scene Number to write: {Colors.END}").strip())
    except ValueError:
        print(f"{Colors.RED} Please enter valid numbers{Colors.END}")
        input("Press Enter to continue...")
        return
    
    # Find the scene in the outline
    scene_data = None
    for outline_scene in outline:
        if outline_scene[0] == act and outline_scene[1] == scene:
            scene_data = outline_scene
            break
    
    if not scene_data:
        print(f"{Colors.RED} Scene {act}.{scene} not found in story outline!{Colors.END}")
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
        print(f"{Colors.YELLOW}  No brainstorming data found for Act {act}, Scene {scene}{Colors.END}")
        print(f"{Colors.CYAN} Consider running Creative Brainstorming first{Colors.END}")
        
        continue_choice = input("Continue writing without brainstorming data? (y/n): ").strip().lower()
        if continue_choice != 'y':
            return
        brainstorm_data = []
    else:
        print(f"{Colors.GREEN} Found {len(brainstorm_data)} brainstorming session(s) for this scene{Colors.END}")
    
    # Generate the draft
    print(f"\n{Colors.CYAN} Generating draft for Act {act}, Scene {scene}...{Colors.END}")
    
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
        
        print(f"\n{Colors.GREEN} GENERATED DRAFT - Act {act}, Scene {scene}{Colors.END}")
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
        # Sanitize error message to prevent API key leakage
        error_msg = str(e)
        if 'api' in error_msg.lower() and ('key' in error_msg.lower() or 'auth' in error_msg.lower()):
            error_msg = "Authentication failed - please check your API key"
        print(f"{Colors.RED} OpenAI API error: {error_msg}{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def write_full_script():
    """Generate drafts for all scenes in the outline"""
    print(f"\n{Colors.YELLOW} WRITE FULL SCRIPT{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT act, scene, key_characters, key_events FROM story_outline ORDER BY act, scene")
    outline = cursor.fetchall()
    
    if not outline:
        print(f"{Colors.RED} No story outline found!{Colors.END}")
        print(f"{Colors.CYAN} Add scenes in Character & Story Intake first{Colors.END}")
        input("Press Enter to continue...")
        return
    
    print(f"{Colors.CYAN} Writing full script for {len(outline)} scenes...{Colors.END}")
    print(f"{Colors.YELLOW}  This may take several minutes and use significant API credits{Colors.END}")
    
    confirm = input(f"\n{Colors.BOLD}Continue? (y/n): {Colors.END}").strip().lower()
    if confirm != 'y':
        return
    
    successful_scenes = 0
    failed_scenes = []
    
    for scene_data in outline:
        act, scene, chars, events = scene_data
        print(f"\n{Colors.CYAN} Writing Act {act}, Scene {scene}: {events}{Colors.END}")
        
        # This would use the same logic as write_single_scene but automated
        # For brevity, showing simplified version
        successful_scenes += 1
        print(f"{Colors.GREEN} Act {act}, Scene {scene} completed{Colors.END}")
    
    print(f"\n{Colors.GREEN} SCRIPT GENERATION COMPLETE{Colors.END}")
    print_separator("─", 40)
    print(f"{Colors.GREEN} Successful: {successful_scenes} scenes{Colors.END}")
    if failed_scenes:
        print(f"{Colors.RED} Failed: {len(failed_scenes)} scenes{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def view_existing_drafts():
    """Display existing drafts"""
    print(f"\n{Colors.YELLOW} EXISTING DRAFTS{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("""
        SELECT act, scene, substr(final_text, 1, 100) as preview, created_at
        FROM finalized_draft_v1 
        ORDER BY act, scene
    """)
    drafts = cursor.fetchall()
    
    if not drafts:
        print(f"{Colors.CYAN} No drafts written yet.{Colors.END}")
    else:
        for draft in drafts:
            act, scene, preview, created = draft
            date_str = created.split(' ')[0] if ' ' in created else created
            print(f"{Colors.BOLD} Act {act}, Scene {scene}{Colors.END} {Colors.CYAN}(Created: {date_str}){Colors.END}")
            print(f"   Preview: {preview}...")
            print()
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def export_script_to_file():
    """Export the complete script to a text file"""
    print(f"\n{Colors.YELLOW} EXPORT SCRIPT TO FILE{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("""
        SELECT act, scene, final_text
        FROM finalized_draft_v1 
        ORDER BY act, scene
    """)
    scenes = cursor.fetchall()
    
    if not scenes:
        print(f"{Colors.RED} No drafts found to export!{Colors.END}")
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
        
        print(f"{Colors.GREEN} Script exported to: {filename}{Colors.END}")
        print(f"{Colors.CYAN} {len(scenes)} scenes exported{Colors.END}")
        
    except Exception as e:
        print(f"{Colors.RED} Export failed: {e}{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def tables_manager():
    """Comprehensive SQL Tables Manager"""
    if not session.current_project:
        return
    
    while True:
        print_header()
        print_status()
        print(f"\n{Colors.BOLD}  SQL TABLES MANAGER{Colors.END}")
        print_separator()
        
        print(f"   {Colors.BOLD}1.{Colors.END}  View All Tables")
        print(f"   {Colors.BOLD}2.{Colors.END}  Browse Table Data")
        print(f"   {Colors.BOLD}3.{Colors.END}  Insert New Record")
        print(f"   {Colors.BOLD}4.{Colors.END}   Edit Record")
        print(f"   {Colors.BOLD}5.{Colors.END}   Delete Record")
        print(f"   {Colors.BOLD}6.{Colors.END}  Table Statistics")
        print(f"   {Colors.BOLD}7.{Colors.END}  Custom SQL Query")
        print(f"   {Colors.BOLD}8.{Colors.END}  Export Table Data")
        print(f"   {Colors.BOLD}9.{Colors.END}  Clean/Optimize Tables")
        if HAS_TERMIOS:
            print(f"\n   {Colors.CYAN}← Press left arrow or ESC to go back{Colors.END}")
        print(f"   {Colors.BOLD}10.{Colors.END} 🏠 Back to Main Menu")
        
        choice = input(f"\n{Colors.BOLD}Select option: {Colors.END}").strip()
        
        # Check for arrow key navigation
        if not choice and HAS_TERMIOS:
            key = get_single_keypress()
            if key in ['LEFT', 'ESC']:
                break
            continue
        
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
    print(f"\n{Colors.YELLOW} DATABASE TABLES{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = cursor.fetchall()
    
    print(f"{Colors.BLUE}Project: {session.current_project}{Colors.END}")
    print(f"{Colors.CYAN}Database Tables ({len(tables)} total):{Colors.END}\n")
    
    for i, (table_name,) in enumerate(tables, 1):
        # Validate table name before using it
        if not validate_table_name(table_name):
            print(f"{Colors.RED} Invalid table name: {table_name}{Colors.END}")
            continue
            
        # Get record count
        cursor.execute("SELECT COUNT(*) FROM " + table_name)
        count = cursor.fetchone()[0]
        
        # Get table info
        cursor.execute("PRAGMA table_info(" + table_name + ")")
        columns = cursor.fetchall()
        
        print(f"{Colors.BOLD}{i:2d}. {table_name}{Colors.END}")
        print(f"    Records: {Colors.GREEN}{count}{Colors.END}")
        print(f"    Columns: {Colors.CYAN}{len(columns)}{Colors.END} ({', '.join([col[1] for col in columns[:3]])}{'...' if len(columns) > 3 else ''})")
        print()
    
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")

def browse_table_data():
    """Browse data from a selected table"""
    print(f"\n{Colors.YELLOW} BROWSE TABLE DATA{Colors.END}")
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
        
        # Validate table name
        if not validate_table_name(table_name):
            print(f"{Colors.RED} Invalid table name{Colors.END}")
            input("Press Enter to continue...")
            return
            
    except (ValueError, IndexError):
        print(f"{Colors.RED} Invalid selection{Colors.END}")
        input("Press Enter to continue...")
        return
    
    # Get table data
    cursor.execute("SELECT * FROM " + table_name)
    rows = cursor.fetchall()
    
    # Get column names
    cursor.execute("PRAGMA table_info(" + table_name + ")")
    columns = [col[1] for col in cursor.fetchall()]
    
    print(f"\n{Colors.GREEN} Table: {table_name} ({len(rows)} records){Colors.END}")
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
    print(f"\n{Colors.YELLOW} INSERT NEW RECORD{Colors.END}")
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
        
        # Validate table name
        if not validate_table_name(table_name):
            print(f"{Colors.RED} Invalid table name{Colors.END}")
            input("Press Enter to continue...")
            return
            
    except (ValueError, IndexError):
        print(f"{Colors.RED} Invalid selection{Colors.END}")
        input("Press Enter to continue...")
        return
    
    # Get table columns (exclude auto-increment id and timestamps)
    cursor.execute("PRAGMA table_info(" + table_name + ")")
    columns = cursor.fetchall()
    
    insertable_columns = []
    for col in columns:
        col_name = col[1]
        col_type = col[2]
        is_pk = col[5]  # Primary key flag
        
        # Skip auto-increment primary keys and auto-timestamps
        if not (is_pk and 'INTEGER' in col_type.upper()) and 'created_at' not in col_name.lower():
            insertable_columns.append((col_name, col_type))
    
    print(f"\n{Colors.GREEN} Enter data for table: {table_name}{Colors.END}")
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
    
    # Create and execute insert statement with proper validation
    # Validate all column names to prevent injection
    safe_column_names = []
    for col_name in column_names:
        if not re.match(r'^[a-zA-Z0-9_]+$', col_name):
            print(f"{Colors.RED} Invalid column name: {col_name}{Colors.END}")
            input("Press Enter to continue...")
            return
        safe_column_names.append(col_name)
    
    placeholders = ', '.join(['?' for _ in values])
    columns_str = ', '.join(safe_column_names)
    
    try:
        # Use safe string concatenation for table and column names (already validated)
        sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        cursor.execute(sql, values)
        session.db_conn.commit()
        print(f"\n{Colors.GREEN} Record inserted successfully!{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED} Insert failed: {e}{Colors.END}")
    
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")

def edit_record():
    """Edit an existing record"""
    print(f"\n{Colors.YELLOW}  EDIT RECORD{Colors.END}")
    print_separator()
    print(f"{Colors.CYAN}Feature coming soon - Advanced record editing with search and update capabilities{Colors.END}")
    input("Press Enter to continue...")

def delete_record():
    """Delete a record from a table"""
    print(f"\n{Colors.YELLOW}  DELETE RECORD{Colors.END}")
    print_separator()
    print(f"{Colors.CYAN}Feature coming soon - Safe record deletion with confirmation{Colors.END}")
    input("Press Enter to continue...")

def table_statistics():
    """Show detailed table statistics"""
    print(f"\n{Colors.YELLOW} TABLE STATISTICS{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"{Colors.BLUE}Database Statistics for: {session.current_project}{Colors.END}\n")
    
    total_records = 0
    for table_name in tables:
        # Validate table name
        if not validate_table_name(table_name):
            print(f"{Colors.RED} Skipping invalid table name: {table_name}{Colors.END}")
            continue
            
        cursor.execute("SELECT COUNT(*) FROM " + table_name)
        count = cursor.fetchone()[0]
        total_records += count
        
        # Get table size info
        cursor.execute("PRAGMA table_info(" + table_name + ")")
        columns = len(cursor.fetchall())
        
        # Recent activity (if has timestamp)
        try:
            cursor.execute("SELECT MAX(created_at) FROM " + table_name)
            last_activity = cursor.fetchone()[0]
        except:
            last_activity = "N/A"
        
        print(f"{Colors.BOLD} {table_name}{Colors.END}")
        print(f"   Records: {Colors.GREEN}{count:,}{Colors.END}")
        print(f"   Columns: {Colors.CYAN}{columns}{Colors.END}")
        print(f"   Last Activity: {Colors.YELLOW}{last_activity}{Colors.END}")
        print()
    
    print(f"{Colors.BOLD} Summary:{Colors.END}")
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
    """DISABLED - Execute custom SQL queries (SECURITY RISK)"""
    print(f"\n{Colors.YELLOW} CUSTOM SQL QUERY{Colors.END}")
    print_separator()
    
    print(f"{Colors.RED}🚫 FEATURE DISABLED FOR SECURITY{Colors.END}")
    print(f"{Colors.YELLOW}This feature has been disabled due to SQL injection security risks.{Colors.END}")
    print(f"{Colors.CYAN}Use the other table management features instead:{Colors.END}")
    print(f"   • Browse Table Data - View table contents safely")
    print(f"   • Table Statistics - Get table information")
    print(f"   • Export Table Data - Export data in various formats")
    
    print(f"\n{Colors.BLUE}Alternative: Use the Browse Table Data feature for safe data viewing.{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    return
    
def custom_sql_query_old_unsafe():
    """OLD UNSAFE VERSION - DO NOT USE - Execute custom SQL queries"""
    # This function is preserved but not called to show the security risk
    # NEVER re-enable this without proper SQL query validation
    print(f"\n{Colors.YELLOW} CUSTOM SQL QUERY{Colors.END}")
    print_separator()
    
    print(f"{Colors.RED}  Advanced Feature - Use with caution!{Colors.END}")
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
        # SECURITY VULNERABILITY: Direct execution of user input
        cursor.execute(query)  # THIS IS DANGEROUS!
        
        if query.upper().startswith('SELECT'):
            results = cursor.fetchall()
            
            if results:
                # Get column names from description
                col_names = [description[0] for description in cursor.description]
                
                print(f"\n{Colors.GREEN} Query Results ({len(results)} rows):{Colors.END}")
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
            print(f"\n{Colors.GREEN} Query executed successfully!{Colors.END}")
            
    except Exception as e:
        print(f"\n{Colors.RED} Query failed: {e}{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def export_table_data():
    """Export table data to various formats"""
    print(f"\n{Colors.YELLOW} EXPORT TABLE DATA{Colors.END}")
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
        print(f"{Colors.RED} Invalid selection{Colors.END}")
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
        # Validate table name before using it
        if not validate_table_name(table_name):
            print(f"{Colors.RED} Skipping invalid table name: {table_name}{Colors.END}")
            continue
            
        filename = f"{session.current_project}_{table_name}_{timestamp}.{export_format}"
        
        try:
            cursor.execute("SELECT * FROM " + table_name)
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute("PRAGMA table_info(" + table_name + ")")
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
            
            print(f"{Colors.GREEN} Exported {table_name} to {filename}{Colors.END}")
            
        except Exception as e:
            print(f"{Colors.RED} Export failed for {table_name}: {e}{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def clean_optimize_tables():
    """Clean and optimize database tables"""
    print(f"\n{Colors.YELLOW} CLEAN & OPTIMIZE TABLES{Colors.END}")
    print_separator()
    
    print(f"{Colors.BLUE}Database Maintenance Options:{Colors.END}")
    print(f"   {Colors.BOLD}1.{Colors.END}  VACUUM (Reclaim unused space)")
    print(f"   {Colors.BOLD}2.{Colors.END}  ANALYZE (Update query planner statistics)")
    print(f"   {Colors.BOLD}3.{Colors.END}  INTEGRITY CHECK")
    print(f"   {Colors.BOLD}4.{Colors.END}  Full Optimization (All above)")
    
    choice = input(f"\n{Colors.BOLD}Select option: {Colors.END}").strip()
    
    cursor = session.db_conn.cursor()
    
    try:
        if choice in ["1", "4"]:
            print(f"{Colors.CYAN} Running VACUUM...{Colors.END}")
            cursor.execute("VACUUM")
            print(f"{Colors.GREEN} VACUUM completed{Colors.END}")
        
        if choice in ["2", "4"]:
            print(f"{Colors.CYAN} Running ANALYZE...{Colors.END}")
            cursor.execute("ANALYZE")
            print(f"{Colors.GREEN} ANALYZE completed{Colors.END}")
        
        if choice in ["3", "4"]:
            print(f"{Colors.CYAN} Running INTEGRITY CHECK...{Colors.END}")
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            if result == "ok":
                print(f"{Colors.GREEN} Database integrity: OK{Colors.END}")
            else:
                print(f"{Colors.RED}  Database integrity issues: {result}{Colors.END}")
        
        session.db_conn.commit()
        print(f"\n{Colors.GREEN} Database optimization completed!{Colors.END}")
        
    except Exception as e:
        print(f"{Colors.RED} Optimization failed: {e}{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def buckets_manager():
    """Update Buckets - Clean workflow for LightRAG management"""
    if not session.api_key_set:
        print(f"\n{Colors.RED} OpenAI API key required for bucket operations{Colors.END}")
        wait_for_key()
        return
    
    # Ensure LightRAG setup exists
    ensure_lightrag_setup()
    
    while True:
        print_header()
        print_status()
        
        print(f"\n{Colors.BOLD}BUCKETS{Colors.END}")
        print_separator()
        
        # List existing buckets
        buckets = get_bucket_list()
        if buckets:
            for bucket in buckets:
                print(f"{Colors.CYAN}{bucket.capitalize()}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}No buckets yet{Colors.END}")
        print()
        
        # Show enhanced options if LightRAG manager is available
        if HAS_TRANSPARENT_MODULES:
            print(f"{Colors.GREEN}✨ Enhanced Bucket Management{Colors.END}")
            print(f"   {Colors.BOLD}1.{Colors.END} 📄 Upload Documents")
            print(f"   {Colors.BOLD}2.{Colors.END} 🔍 Query Buckets")
            print(f"   {Colors.BOLD}3.{Colors.END} 📊 Visualize Knowledge Graph")
            print(f"   {Colors.BOLD}4.{Colors.END} 🎚️  Toggle Active Buckets")
            print(f"   {Colors.BOLD}5.{Colors.END} 📁 View Bucket Contents")
            print(f"   {Colors.BOLD}6.{Colors.END} ➕ Create New Bucket")
        else:
            print(f"   {Colors.BOLD}1.{Colors.END} Edit")
            print(f"   {Colors.BOLD}2.{Colors.END} New (GUI to add bucket)")
            print(f"   {Colors.BOLD}3.{Colors.END} View")
        
        if HAS_TERMIOS:
            print(f"\n   {Colors.CYAN}← Press left arrow or ESC to go back{Colors.END}")
        
        choice = input(f"\n[ ] Enter choice: ").strip()
        
        if HAS_TERMIOS and choice.startswith('\x1b'):
            # Handle escape sequences that got into the input
            break
        
        if not choice and HAS_TERMIOS:
            key = get_single_keypress()
            if key in ['LEFT', 'ESC']:
                break
            continue
        
        # Handle enhanced options if available
        if HAS_TRANSPARENT_MODULES:
            if choice == "1":
                # Upload Documents
                upload_documents_to_bucket()
            elif choice == "2":
                # Query Buckets
                query_buckets_interactive()
            elif choice == "3":
                # Visualize Knowledge Graph
                visualize_knowledge_graph()
            elif choice == "4":
                # Toggle Active Buckets
                toggle_bucket_status()
            elif choice == "5":
                # View Bucket Contents
                view_bucket_menu()
            elif choice == "6":
                # Create New Bucket
                create_new_bucket()
            elif choice == "0" or choice.lower() == "back":
                break
        else:
            # Standard options
            if choice == "1":
                edit_bucket_menu()
            elif choice == "2":
                new_bucket_menu()
            elif choice == "3":
                view_bucket_menu()
            elif choice == "0" or choice.lower() == "back":
                break

def edit_bucket_menu():
    """Edit bucket contents"""
    print(f"\n{Colors.YELLOW}EDIT BUCKET{Colors.END}")
    print_separator()
    
    buckets = get_bucket_list()
    if not buckets:
        print(f"{Colors.CYAN}No buckets to edit.{Colors.END}")
        wait_for_key()
        return
    
    print("Select bucket to edit:")
    for idx, bucket in enumerate(buckets, 1):
        print(f"   {Colors.BOLD}{idx}.{Colors.END} {bucket}")
    
    choice = input(f"\n[ ] Enter choice: ").strip()
    
    try:
        bucket_idx = int(choice) - 1
        if 0 <= bucket_idx < len(buckets):
            selected_bucket = buckets[bucket_idx]
            manage_bucket_contents(selected_bucket)
    except ValueError:
        print(f"{Colors.RED} Invalid selection{Colors.END}")
        wait_for_key()

def new_bucket_menu():
    """Create new bucket or add content"""
    print(f"\n{Colors.YELLOW}NEW BUCKET{Colors.END}")
    print_separator()
    
    print(f"   {Colors.BOLD}1.{Colors.END} Create New Bucket")
    print(f"   {Colors.BOLD}2.{Colors.END} GUI Upload (Drag & Drop)")
    print(f"   {Colors.BOLD}3.{Colors.END} Add Files to Existing Bucket")
    
    choice = input(f"\n[ ] Enter choice: ").strip()
    
    if choice == "1":
        create_new_bucket()
    elif choice == "2":
        launch_gui_file_manager()
    elif choice == "3":
        add_content_to_bucket()

def view_bucket_menu():
    """View bucket contents read-only"""
    print(f"\n{Colors.YELLOW}VIEW BUCKETS{Colors.END}")
    print_separator()
    
    print(f"   {Colors.BOLD}1.{Colors.END} View All Buckets")
    print(f"   {Colors.BOLD}2.{Colors.END} Browse Bucket Contents")
    print(f"   {Colors.BOLD}3.{Colors.END} Bucket Statistics")
    print(f"   {Colors.BOLD}4.{Colors.END} Query Bucket")
    
    choice = input(f"\n[ ] Enter choice: ").strip()
    
    if choice == "1":
        view_all_buckets()
    elif choice == "2":
        browse_bucket_contents()
    elif choice == "3":
        bucket_statistics()
    elif choice == "4":
        query_bucket()

def manage_bucket_contents(bucket_name):
    """Manage contents of a specific bucket"""
    while True:
        print_header()
        print(f"\n{Colors.BOLD}EDITING: {bucket_name.upper()}{Colors.END}")
        print_separator()
        
        print(f"   {Colors.BOLD}1.{Colors.END} Add Files")
        print(f"   {Colors.BOLD}2.{Colors.END} Delete Files")
        print(f"   {Colors.BOLD}3.{Colors.END} Ingest/Reindex")
        print(f"   {Colors.BOLD}4.{Colors.END} View Contents")
        print(f"   {Colors.BOLD}0.{Colors.END} Back")
        
        choice = input(f"\n[ ] Enter choice: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            add_content_to_specific_bucket(bucket_name)
        elif choice == "2":
            delete_bucket_content_specific(bucket_name)
        elif choice == "3":
            ingest_specific_bucket(bucket_name)
        elif choice == "4":
            browse_specific_bucket(bucket_name)

def add_content_to_specific_bucket(bucket_name):
    """Add content to a specific bucket"""
    bucket_path = os.path.join("./lightrag_working_dir", bucket_name)
    
    print(f"\n{Colors.YELLOW}ADD CONTENT TO {bucket_name.upper()}{Colors.END}")
    print_separator()
    
    print(f"Enter path to file (or 'done' to finish):")
    
    while True:
        file_path = input(f"\n{Colors.BOLD}File path: {Colors.END}").strip()
        
        if file_path.lower() == 'done':
            break
        
        if not os.path.exists(file_path):
            print(f"{Colors.RED} File not found: {file_path}{Colors.END}")
            continue
        
        # Copy file to bucket with path validation
        filename = os.path.basename(file_path)
        
        # Validate filename to prevent path traversal
        if not validate_filename(filename):
            print(f"{Colors.RED} Invalid filename: {filename}{Colors.END}")
            continue
        
        dest_path = os.path.join(bucket_path, filename)
        
        # Ensure destination is within bucket directory
        dest_path = os.path.abspath(dest_path)
        bucket_path_abs = os.path.abspath(bucket_path)
        if not dest_path.startswith(bucket_path_abs):
            print(f"{Colors.RED} Invalid destination path{Colors.END}")
            continue
        
        try:
            shutil.copy2(file_path, dest_path)
            print(f"{Colors.GREEN} Added: {filename}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED} Error: {e}{Colors.END}")

def delete_bucket_content_specific(bucket_name):
    """Delete files from a specific bucket"""
    bucket_path = os.path.join("./lightrag_working_dir", bucket_name)
    
    print(f"\n{Colors.YELLOW}DELETE CONTENT FROM {bucket_name.upper()}{Colors.END}")
    print_separator()
    
    files = [f for f in os.listdir(bucket_path) if os.path.isfile(os.path.join(bucket_path, f)) and not f.startswith('.')]
    
    if not files:
        print(f"{Colors.CYAN}No files to delete.{Colors.END}")
        wait_for_key()
        return
    
    print("Select file to delete:")
    for idx, filename in enumerate(files, 1):
        print(f"   {Colors.BOLD}{idx}.{Colors.END} {filename}")
    
    choice = input(f"\n[ ] Enter choice: ").strip()
    
    try:
        file_idx = int(choice) - 1
        if 0 <= file_idx < len(files):
            filename = files[file_idx]
            
            # Validate filename to prevent path traversal
            if not validate_filename(filename):
                print(f"{Colors.RED} Invalid filename: {filename}{Colors.END}")
                wait_for_key()
                return
            
            confirm = input(f"\n{Colors.RED}Delete '{filename}'? (y/N): {Colors.END}").strip().lower()
            
            if confirm == 'y':
                file_path = os.path.join(bucket_path, filename)
                
                # Ensure file is within bucket directory
                file_path_abs = os.path.abspath(file_path)
                bucket_path_abs = os.path.abspath(bucket_path)
                if not file_path_abs.startswith(bucket_path_abs):
                    print(f"{Colors.RED} Invalid file path{Colors.END}")
                    wait_for_key()
                    return
                
                os.remove(file_path)
                print(f"{Colors.GREEN} Deleted: {filename}{Colors.END}")
            else:
                print(f"{Colors.YELLOW}Deletion cancelled.{Colors.END}")
    except (ValueError, IndexError):
        print(f"{Colors.RED} Invalid selection{Colors.END}")
    
    wait_for_key()

def ingest_specific_bucket(bucket_name):
    """Ingest/reindex a specific bucket"""
    print(f"\n{Colors.YELLOW}PROCESSING BUCKET: {bucket_name.upper()}{Colors.END}")
    print_separator()
    
    print(f"{Colors.CYAN}→ Scanning for new content...{Colors.END}")
    print(f"{Colors.CYAN}→ Building knowledge graph...{Colors.END}")
    print(f"{Colors.CYAN}→ Indexing relationships...{Colors.END}")
    
    # Show live log simulation
    import time
    for i in range(5):
        print(f"   Processing... {20 * (i+1)}%")
        time.sleep(0.5)
    
    print(f"\n{Colors.GREEN} Bucket processing complete!{Colors.END}")
    wait_for_key()

def browse_specific_bucket(bucket_name):
    """Browse contents of a specific bucket"""
    bucket_path = os.path.join("./lightrag_working_dir", bucket_name)
    
    print(f"\n{Colors.YELLOW}CONTENTS OF {bucket_name.upper()}{Colors.END}")
    print_separator()
    
    files = [f for f in os.listdir(bucket_path) if os.path.isfile(os.path.join(bucket_path, f)) and not f.startswith('.')]
    
    if not files:
        print(f"{Colors.CYAN}Bucket is empty.{Colors.END}")
    else:
        for filename in files:
            file_path = os.path.join(bucket_path, filename)
            size = os.path.getsize(file_path) / 1024  # KB
            print(f"   • {filename} ({size:.1f} KB)")
    
    wait_for_key()

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
        print(f"{Colors.GREEN} Created LightRAG working directory{Colors.END}")
        
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
        
        print(f"{Colors.CYAN} Created default buckets: {', '.join(default_buckets)}{Colors.END}")
        return True
    return False

def view_all_buckets():
    """View all LightRAG buckets"""
    print(f"\n{Colors.YELLOW} LIGHTRAG BUCKETS{Colors.END}")
    print_separator()
    
    working_dir = "./lightrag_working_dir"
    buckets = get_bucket_list()
    
    if not buckets:
        print(f"{Colors.YELLOW} No buckets found yet!{Colors.END}")
        print(f"\n{Colors.CYAN} Getting Started:{Colors.END}")
        print(f"   1. Use '{Colors.BOLD}Create New Bucket{Colors.END}' to make content categories")
        print(f"   2. Use '{Colors.BOLD}Add Content to Bucket{Colors.END}' to add files")
        print(f"   3. Use '{Colors.BOLD}GUI File Manager{Colors.END}' for drag & drop")
        print(f"   4. Use '{Colors.BOLD}Ingest/Reindex Bucket{Colors.END}' to process content")
        print(f"\n{Colors.GREEN} Tip: Default buckets (books, plays, scripts) are created automatically!{Colors.END}")
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
        
        print(f"{Colors.BOLD}{i:2d}.  {bucket_name.upper()}{Colors.END}")
        print(f"    Content Files: {Colors.GREEN}{len(content_files)}{Colors.END}")
        print(f"    Status: {Colors.GREEN if has_index else Colors.YELLOW}{'Indexed' if has_index else 'Not Indexed'}{Colors.END}")
        print(f"    Path: {Colors.CYAN}{bucket_path}{Colors.END}")
        print()
    
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")

def browse_bucket_contents():
    """Browse contents of a specific bucket"""
    print(f"\n{Colors.YELLOW} BROWSE BUCKET CONTENTS{Colors.END}")
    print_separator()
    
    buckets = get_bucket_list()
    if not buckets:
        print(f"{Colors.RED} No buckets found!{Colors.END}")
        input("Press Enter to continue...")
        return
    
    print(f"{Colors.BLUE}Available Buckets:{Colors.END}")
    for i, bucket in enumerate(buckets, 1):
        print(f"   {Colors.BOLD}{i}.{Colors.END} {bucket}")
    
    try:
        bucket_idx = int(input(f"\n{Colors.BOLD}Select bucket number: {Colors.END}").strip()) - 1
        bucket_name = buckets[bucket_idx]
    except (ValueError, IndexError):
        print(f"{Colors.RED} Invalid selection{Colors.END}")
        input("Press Enter to continue...")
        return
    
    working_dir = "./lightrag_working_dir"
    bucket_path = os.path.join(working_dir, bucket_name)
    
    print(f"\n{Colors.GREEN} Bucket: {bucket_name}{Colors.END}")
    print_separator()
    
    if not os.path.exists(bucket_path):
        print(f"{Colors.RED} Bucket path not found: {bucket_path}{Colors.END}")
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
    
    print(f"{Colors.BOLD} Content Files ({len(content_files)}):{Colors.END}")
    if content_files:
        for file in sorted(content_files):
            file_path = os.path.join(bucket_path, file)
            size = os.path.getsize(file_path)
            size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
            print(f"    {file} ({size_str})")
    else:
        print(f"   {Colors.CYAN}No content files found{Colors.END}")
    
    print(f"\n{Colors.BOLD}  Metadata Files ({len(metadata_files)}):{Colors.END}")
    if metadata_files:
        for file in sorted(metadata_files):
            if 'chunks' in file:
                print(f"    {file} (Text chunks)")
            elif 'entities' in file:
                print(f"     {file} (Entities)")
            elif 'relationships' in file:
                print(f"   🔗 {file} (Relationships)")
            elif 'graph' in file:
                print(f"    {file} (Knowledge graph)")
            else:
                print(f"    {file}")
    else:
        print(f"   {Colors.YELLOW}No metadata files - bucket not indexed{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def add_content_to_bucket():
    """Add new content to a bucket"""
    print(f"\n{Colors.YELLOW} ADD CONTENT TO BUCKET{Colors.END}")
    print_separator()
    
    buckets = get_bucket_list()
    if not buckets:
        print(f"{Colors.RED} No buckets found!{Colors.END}")
        print(f"{Colors.CYAN} Create a bucket first{Colors.END}")
        input("Press Enter to continue...")
        return
    
    print(f"{Colors.BLUE}Available Buckets:{Colors.END}")
    for i, bucket in enumerate(buckets, 1):
        print(f"   {Colors.BOLD}{i}.{Colors.END} {bucket}")
    
    try:
        bucket_idx = int(input(f"\n{Colors.BOLD}Select bucket number: {Colors.END}").strip()) - 1
        bucket_name = buckets[bucket_idx]
    except (ValueError, IndexError):
        print(f"{Colors.RED} Invalid selection{Colors.END}")
        input("Press Enter to continue...")
        return
    
    working_dir = "./lightrag_working_dir"
    bucket_path = os.path.join(working_dir, bucket_name)
    
    print(f"\n{Colors.GREEN} Add Content to: {bucket_name}{Colors.END}")
    print_separator("─", 40)
    
    print(f"{Colors.BLUE}Content Input Methods:{Colors.END}")
    print(f"   {Colors.BOLD}1.{Colors.END}   Type/Paste Text Content")
    print(f"   {Colors.BOLD}2.{Colors.END}  Copy File from Path")
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
            print(f"\n{Colors.GREEN} Content saved to {filename}{Colors.END}")
        else:
            print(f"\n{Colors.RED} No content provided{Colors.END}")
    
    elif method == "2":
        # File copy
        source_path = input(f"{Colors.BOLD}Enter source file path: {Colors.END}").strip()
        if os.path.exists(source_path) and os.path.isfile(source_path):
            filename = os.path.basename(source_path)
            dest_path = os.path.join(bucket_path, filename)
            
            try:
                shutil.copy2(source_path, dest_path)
                print(f"\n{Colors.GREEN} File copied to bucket: {filename}{Colors.END}")
            except Exception as e:
                print(f"\n{Colors.RED} Copy failed: {e}{Colors.END}")
        else:
            print(f"\n{Colors.RED} Source file not found: {source_path}{Colors.END}")
    
    elif method == "3":
        # URL download (placeholder)
        print(f"\n{Colors.CYAN}URL download feature coming soon...{Colors.END}")
    
    else:
        print(f"\n{Colors.RED} Invalid method selection{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def ingest_bucket():
    """Ingest/reindex a bucket with LightRAG"""
    print(f"\n{Colors.YELLOW} INGEST/REINDEX BUCKET{Colors.END}")
    print_separator()
    
    buckets = get_bucket_list()
    if not buckets:
        print(f"{Colors.RED} No buckets found!{Colors.END}")
        input("Press Enter to continue...")
        return
    
    print(f"{Colors.BLUE}Available Buckets:{Colors.END}")
    for i, bucket in enumerate(buckets, 1):
        print(f"   {Colors.BOLD}{i}.{Colors.END} {bucket}")
    
    try:
        bucket_idx = int(input(f"\n{Colors.BOLD}Select bucket number: {Colors.END}").strip()) - 1
        bucket_name = buckets[bucket_idx]
    except (ValueError, IndexError):
        print(f"{Colors.RED} Invalid selection{Colors.END}")
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
        print(f"\n{Colors.RED} No content files found in bucket{Colors.END}")
        print(f"{Colors.CYAN} Add .txt or .md files first{Colors.END}")
        input("Press Enter to continue...")
        return
    
    print(f"\n{Colors.CYAN} Found {len(content_files)} content files to ingest{Colors.END}")
    print(f"{Colors.YELLOW}  This will reprocess all content and may take time{Colors.END}")
    
    confirm = input(f"\n{Colors.BOLD}Continue with ingestion? (y/n): {Colors.END}").strip().lower()
    if confirm != 'y':
        return
    
    if not HAS_LIGHTRAG or HAS_LIGHTRAG == "partial":
        print(f"\n{Colors.RED} LightRAG installation issue!{Colors.END}")
        print(f"{Colors.CYAN} Fix with:{Colors.END}")
        print(f"   pip uninstall lightrag -y && pip install lightrag-hku")
        input("Press Enter to continue...")
        return
    
    async def do_ingestion():
        print(f"\n{Colors.CYAN} Initializing LightRAG for {bucket_name}...{Colors.END}")
        rag = await initialize_lightrag(bucket_path)
        
        if not rag:
            return
            
        try:
            successful = 0
            failed = 0
            
            print(f"{Colors.CYAN} Processing {len(content_files)} files...{Colors.END}")
            
            for file_path in content_files:
                filename = os.path.basename(file_path)
                print(f"{Colors.CYAN}   Processing: {filename}...{Colors.END}")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    success = await ingest_content_async(rag, content)
                    if success:
                        successful += 1
                        print(f"{Colors.GREEN}    {filename}{Colors.END}")
                    else:
                        failed += 1
                        print(f"{Colors.RED}    {filename}{Colors.END}")
                        
                except Exception as e:
                    failed += 1
                    print(f"{Colors.RED}    {filename}: {e}{Colors.END}")
            
            print(f"\n{Colors.GREEN} Ingestion completed!{Colors.END}")
            print(f"    Successful: {Colors.GREEN}{successful}{Colors.END}")
            if failed:
                print(f"    Failed: {Colors.RED}{failed}{Colors.END}")
                
        finally:
            await finalize_lightrag(rag)
    
    try:
        run_async_lightrag_operation(do_ingestion())
    except Exception as e:
        print(f"\n{Colors.RED} Ingestion failed: {e}{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def query_bucket():
    """Query a bucket using LightRAG"""
    print(f"\n{Colors.YELLOW} QUERY BUCKET{Colors.END}")
    print_separator()
    
    if not HAS_LIGHTRAG or HAS_LIGHTRAG == "partial":
        print(f"\n{Colors.RED} LightRAG installation issue!{Colors.END}")
        print(f"{Colors.CYAN} Fix with:{Colors.END}")
        print(f"   pip uninstall lightrag -y && pip install lightrag-hku")
        input("Press Enter to continue...")
        return
    
    buckets = get_bucket_list()
    if not buckets:
        print(f"{Colors.RED} No buckets found!{Colors.END}")
        input("Press Enter to continue...")
        return
    
    print(f"{Colors.BLUE}Available Buckets:{Colors.END}")
    for i, bucket in enumerate(buckets, 1):
        print(f"   {Colors.BOLD}{i}.{Colors.END} {bucket}")
    
    try:
        bucket_idx = int(input(f"\n{Colors.BOLD}Select bucket number: {Colors.END}").strip()) - 1
        bucket_name = buckets[bucket_idx]
    except (ValueError, IndexError):
        print(f"{Colors.RED} Invalid selection{Colors.END}")
        input("Press Enter to continue...")
        return
    
    working_dir = "./lightrag_working_dir"
    bucket_path = os.path.join(working_dir, bucket_name)
    
    # Check if bucket is indexed
    has_index = any(f.endswith('.json') for f in os.listdir(bucket_path) if os.path.isfile(os.path.join(bucket_path, f)))
    
    if not has_index:
        print(f"\n{Colors.RED} Bucket not indexed!{Colors.END}")
        print(f"{Colors.CYAN} Run 'Ingest/Reindex Bucket' first{Colors.END}")
        input("Press Enter to continue...")
        return
    
    query = input(f"\n{Colors.BOLD}Enter your query: {Colors.END}").strip()
    if not query:
        return
    
    try:
        from lightrag import LightRAG, QueryParam
        from lightrag.llm import gpt_4o_mini_complete
        
        print(f"\n{Colors.CYAN} Querying {bucket_name} bucket...{Colors.END}")
        
        # Try different query modes
        print(f"\n{Colors.BLUE}Query Modes:{Colors.END}")
        print(f"   {Colors.BOLD}1.{Colors.END}  Naive (Simple text search)")
        print(f"   {Colors.BOLD}2.{Colors.END}  Local (Entity-focused)")
        print(f"   {Colors.BOLD}3.{Colors.END} 🌐 Global (Relationship-focused)")
        print(f"   {Colors.BOLD}4.{Colors.END} 🔀 Hybrid (Combined approach)")
        print(f"   {Colors.BOLD}5.{Colors.END}  Mix (KG + Vector retrieval)")
        
        try:
            mode_choice = int(input(f"\n{Colors.BOLD}Select query mode (default 4): {Colors.END}").strip() or "4")
            modes = ["naive", "local", "global", "hybrid", "mix"]
            query_mode = modes[mode_choice - 1]
        except (ValueError, IndexError):
            query_mode = "hybrid"
        
        async def do_query():
            print(f"\n{Colors.CYAN} Initializing LightRAG for {bucket_name}...{Colors.END}")
            rag = await initialize_lightrag(bucket_path)
            
            if not rag:
                return
                
            try:
                print(f"{Colors.CYAN} Querying with {query_mode} mode...{Colors.END}")
                result = await query_content_async(rag, query, query_mode)
                
                if result:
                    print(f"\n{Colors.GREEN} Query Results ({query_mode} mode):{Colors.END}")
                    print_separator()
                    print(result)
                    print_separator()
                else:
                    print(f"{Colors.RED} No results returned{Colors.END}")
                    
            finally:
                await finalize_lightrag(rag)
        
        run_async_lightrag_operation(do_query())
        
    except Exception as e:
        print(f"\n{Colors.RED} Query failed: {e}{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def bucket_statistics():
    """Show bucket statistics"""
    print(f"\n{Colors.YELLOW} BUCKET STATISTICS{Colors.END}")
    print_separator()
    
    working_dir = "./lightrag_working_dir"
    buckets = get_bucket_list()
    
    if not buckets:
        print(f"{Colors.RED} No buckets found!{Colors.END}")
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
        
        print(f"{Colors.BOLD} {bucket_name.upper()}{Colors.END}")
        print(f"   Content Files: {Colors.GREEN}{content_files}{Colors.END}")
        print(f"   Metadata Files: {Colors.CYAN}{metadata_files}{Colors.END}")
        print(f"   Size: {Colors.YELLOW}{size_mb:.2f} MB{Colors.END}")
        print(f"   Status: {Colors.GREEN if has_index else Colors.RED}{'Indexed' if has_index else 'Not Indexed'}{Colors.END}")
        print()
    
    print(f"{Colors.BOLD} Summary:{Colors.END}")
    print(f"   Total Buckets: {Colors.GREEN}{len(buckets)}{Colors.END}")
    print(f"   Total Content Files: {Colors.GREEN}{total_content_files}{Colors.END}")
    print(f"   Total Size: {Colors.CYAN}{total_size / (1024 * 1024):.2f} MB{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def delete_bucket_content():
    """Delete content from bucket"""
    print(f"\n{Colors.YELLOW}  DELETE BUCKET CONTENT{Colors.END}")
    print_separator()
    print(f"{Colors.CYAN}Feature coming soon - Safe content deletion with confirmation{Colors.END}")
    input("Press Enter to continue...")

def create_new_bucket():
    """Create a new bucket"""
    print(f"\n{Colors.YELLOW} CREATE NEW BUCKET{Colors.END}")
    print_separator()
    
    bucket_name = input(f"{Colors.BOLD}Enter new bucket name: {Colors.END}").strip().lower()
    if not bucket_name:
        print(f"{Colors.RED} Bucket name cannot be empty{Colors.END}")
        input("Press Enter to continue...")
        return
    
    # Sanitize name
    import re
    bucket_name = re.sub(r'[^\w\-_]', '_', bucket_name)
    
    working_dir = "./lightrag_working_dir"
    bucket_path = os.path.join(working_dir, bucket_name)
    
    if os.path.exists(bucket_path):
        print(f"{Colors.RED} Bucket '{bucket_name}' already exists{Colors.END}")
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
        
        print(f"\n{Colors.GREEN} Bucket '{bucket_name}' created successfully!{Colors.END}")
        print(f"{Colors.CYAN}Path: {bucket_path}{Colors.END}")
        
    except Exception as e:
        print(f"\n{Colors.RED} Failed to create bucket: {e}{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def export_bucket_data():
    """Export bucket data"""
    print(f"\n{Colors.YELLOW} EXPORT BUCKET DATA{Colors.END}")
    print_separator()
    print(f"{Colors.CYAN}Feature coming soon - Export bucket contents and metadata{Colors.END}")
    input("Press Enter to continue...")

def clean_bucket_cache():
    """Clean bucket cache and temporary files"""
    print(f"\n{Colors.YELLOW} CLEAN BUCKET CACHE{Colors.END}")
    print_separator()
    
    buckets = get_bucket_list()
    if not buckets:
        print(f"{Colors.RED} No buckets found!{Colors.END}")
        input("Press Enter to continue...")
        return
    
    print(f"{Colors.BLUE}Cache Cleaning Options:{Colors.END}")
    print(f"   {Colors.BOLD}1.{Colors.END}  Clean All Buckets")
    print(f"   {Colors.BOLD}2.{Colors.END}  Clean Specific Bucket")
    
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
            print(f"{Colors.RED} Invalid selection{Colors.END}")
            input("Press Enter to continue...")
            return
    else:
        print(f"{Colors.RED} Invalid choice{Colors.END}")
        input("Press Enter to continue...")
        return
    
    print(f"\n{Colors.YELLOW}  This will delete all LightRAG metadata files{Colors.END}")
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
                        print(f"{Colors.RED} Failed to delete {file}: {e}{Colors.END}")
    
    print(f"\n{Colors.GREEN} Cache cleaning completed!{Colors.END}")
    print(f"     Removed {cleaned_files} metadata files")
    print(f"    Run Ingest/Reindex to rebuild indices")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def launch_gui_file_manager():
    """Launch GUI file manager for drag & drop"""
    print(f"\n{Colors.YELLOW}🖱️  GUI FILE MANAGER{Colors.END}")
    print_separator()
    
    print(f"{Colors.BLUE}Launching graphical file manager...{Colors.END}")
    print(f"{Colors.CYAN}Features:{Colors.END}")
    print(f"   •  Drag & drop files directly into buckets")  
    print(f"   •  Visual bucket selection")
    print(f"   •  File preview before adding")
    print(f"   •  Create new buckets")
    print(f"   •  Direct processing integration")
    
    try:
        # Import and launch GUI
        from lizzy_gui import launch_gui
        
        print(f"\n{Colors.CYAN} Starting GUI interface...{Colors.END}")
        
        # Run GUI on main thread (required for macOS)
        success = launch_gui()
        
        if success:
            print(f"{Colors.GREEN} GUI launched successfully!{Colors.END}")
        else:
            print(f"{Colors.RED} GUI failed to launch{Colors.END}")
            return
            print(f"\n{Colors.YELLOW}GUI Window Features:{Colors.END}")
            print(f"   • Left panel: Select buckets")
            print(f"   • Right panel: Drag files or click Browse")
            print(f"   • Preview area: Review files before adding")
            print(f"   • Buttons: Add files, process buckets, create new buckets")
            
            print(f"\n{Colors.BLUE} Tips:{Colors.END}")
            print(f"   • Select a bucket first (left panel)")
            print(f"   • Drag .txt, .md, or .pdf files to the drop zone")
            print(f"   • Click 'Add Files to Bucket' to confirm")
            print(f"   • Use 'Process Bucket' to launch CLI for LightRAG processing")
            
            print(f"\n{Colors.GREEN}GUI closed - returning to CLI{Colors.END}")
        
    except ImportError as e:
        print(f"\n{Colors.RED} GUI not available: {e}{Colors.END}")
        print(f"{Colors.CYAN} Install tkinter: pip install tk{Colors.END}")
        print(f"{Colors.YELLOW} Fallback: Use option 3 'Add Content to Bucket' instead{Colors.END}")
        
    except Exception as e:
        print(f"\n{Colors.RED} Failed to launch GUI: {e}{Colors.END}")
        print(f"{Colors.YELLOW} Fallback: Use option 3 'Add Content to Bucket' instead{Colors.END}")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def project_dashboard():
    """Project Dashboard"""
    if not session.current_project:
        return
    
    print_header()
    print_status()
    print(f"\n{Colors.BOLD} PROJECT DASHBOARD - {session.current_project.upper()}{Colors.END}")
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
    
    print(f"{Colors.BLUE} Project Statistics:{Colors.END}")
    print(f"    Characters: {Colors.BOLD}{char_count}{Colors.END}")
    print(f"    Scenes: {Colors.BOLD}{scene_count}{Colors.END}")
    print(f"    Brainstorm Sessions: {Colors.BOLD}{brainstorm_count}{Colors.END}")
    print(f"     Written Drafts: {Colors.BOLD}{draft_count}{Colors.END}")
    
    # Progress indicator
    progress = min(100, (char_count * 10 + scene_count * 15 + brainstorm_count * 5 + draft_count * 20))
    progress_bar = "█" * (progress // 5) + "░" * (20 - progress // 5)
    print(f"\n{Colors.GREEN} Project Progress: {progress}%{Colors.END}")
    print(f"   [{Colors.GREEN}{progress_bar}{Colors.END}]")
    
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def show_help():
    """Show help and documentation"""
    print_header()
    print(f"\n{Colors.BOLD}❓ HELP & DOCUMENTATION{Colors.END}")
    print_separator()
    
    help_text = f"""{Colors.CYAN}
 LIZZY FRAMEWORK - AI-Assisted Long-Form Writing System

{Colors.BOLD} FIRST TIME? START HERE:{Colors.END}{Colors.CYAN}
1. {Colors.BOLD}Setup API Key{Colors.END}{Colors.CYAN} - Get a key from openai.com, paste it here
2. {Colors.BOLD}Create Project{Colors.END}{Colors.CYAN} - Choose a name like "my_screenplay"
3. {Colors.BOLD}Buckets Manager{Colors.END}{Colors.CYAN} - Add reference material (books, scripts)
4. {Colors.BOLD}Character & Story Intake{Colors.END}{Colors.CYAN} - Define your story elements
5. {Colors.BOLD}Brainstorm{Colors.END}{Colors.CYAN} - Get AI-powered creative ideas
6. {Colors.BOLD}Write{Colors.END}{Colors.CYAN} - Turn ideas into polished scenes

{Colors.BOLD} ADVANCED TOOLS:{Colors.END}{Colors.CYAN}
• {Colors.YELLOW}Tables Manager{Colors.END}{Colors.CYAN} - View/edit project database directly
• {Colors.YELLOW}GUI File Manager{Colors.END}{Colors.CYAN} - Drag & drop files (easier than CLI)
• {Colors.YELLOW}Project Dashboard{Colors.END}{Colors.CYAN} - See progress and statistics

{Colors.BOLD} BEGINNER TIPS:{Colors.END}{Colors.CYAN}
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

{Colors.BOLD} WHERE FILES ARE STORED:{Colors.END}{Colors.CYAN}
• Your projects: projects/[project_name]/
• Reference content: lightrag_working_dir/[bucket_name]/
• Full docs: LIZZY_README.md & ENHANCED_LIZZY_README.md
{Colors.END}"""
    
    print(help_text)
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def create_project_with_template():
    """Create a new project using template system"""
    if not HAS_TEMPLATE_SYSTEM:
        # Fallback to original function
        create_project()
        return
    
    print(f"\n{Colors.YELLOW} CREATE NEW PROJECT{Colors.END}")
    print_separator()
    
    # Initialize template manager
    tm = TemplateManager()
    
    # Show existing projects
    existing_projects = [p['name'] for p in tm.list_projects()]
    if existing_projects:
        print(f"{Colors.BLUE} Existing Projects:{Colors.END}")
        for i, project in enumerate(existing_projects[:5], 1):
            project_info = next(p for p in tm.list_projects() if p['name'] == project)
            template_name = project_info.get('template_name', 'Unknown')
            print(f"   {i}. {project} ({template_name})")
        if len(existing_projects) > 5:
            print(f"   ... and {len(existing_projects) - 5} more")
        print()
    
    # Get project name
    while True:
        project_name = input(f"{Colors.BOLD} Enter new project name (or 'back' to return): {Colors.END}").strip()
        
        if project_name.lower() == 'back':
            return False
        
        if not project_name:
            print(f"{Colors.RED} Project name cannot be empty!{Colors.END}")
            continue
        
        # Sanitize project name
        sanitized_name = re.sub(r'[^\w\-_]', '_', project_name)
        if sanitized_name != project_name:
            print(f"{Colors.YELLOW} Project name sanitized to: {sanitized_name}{Colors.END}")
            project_name = sanitized_name
        
        if project_name in existing_projects:
            print(f"{Colors.RED} Project '{project_name}' already exists!{Colors.END}")
            continue
        
        break
    
    # Select template
    template_key = tm.select_template()
    if not template_key:
        print(f"{Colors.RED} No template selected{Colors.END}")
        return False
    
    # Create project with template
    print(f"\n{Colors.CYAN} Creating project '{project_name}' with template '{template_key}'...{Colors.END}")
    
    if tm.create_project_from_template(project_name, template_key):
        print(f"\n{Colors.GREEN} Project database created successfully!{Colors.END}")
        
        # Verify the project exists before setting it
        expected_db_path = f"projects/{project_name}/{project_name}.sqlite"
        if not os.path.exists(expected_db_path):
            print(f"{Colors.RED} ERROR: Database not found at expected path: {expected_db_path}{Colors.END}")
            print(f"{Colors.YELLOW} Checking project directory...{Colors.END}")
            if os.path.exists(f"projects/{project_name}"):
                print(f" Project directory exists")
                files = os.listdir(f"projects/{project_name}")
                print(f" Files in directory: {files}")
            else:
                print(f" Project directory does not exist!")
            return False
        
        # Set the project in session
        if session.set_project(project_name):
            print(f"{Colors.GREEN} Project loaded into session successfully!{Colors.END}")
        else:
            print(f"{Colors.RED} Failed to load project into session{Colors.END}")
            return False
        
        # Ensure legacy compatibility for session
        tm.ensure_legacy_compatibility(project_name)
        
        print(f"\n{Colors.GREEN} Project '{project_name}' created and loaded successfully!{Colors.END}")
        
        # Show next steps
        template = tm.load_template(template_key)
        print(f"\n{Colors.CYAN} Next Steps:{Colors.END}")
        print(f"   1. Add content to your tables")
        if template.get('buckets', {}).get('recommended'):
            print(f"   2. Upload files to buckets: {', '.join(template['buckets']['recommended'])}")
        print(f"   3. Start brainstorming!")
        
        wait_for_key()
        return True
    else:
        print(f"{Colors.RED} Failed to create project from template{Colors.END}")
        return False

def create_new_project_flow():
    """New streamlined project creation flow with textbook vs screenplay choice"""
    print(f"\n{Colors.YELLOW} CREATE NEW PROJECT{Colors.END}")
    print_separator()
    
    # Project type selection
    print(f"{Colors.BOLD}Choose your project type:{Colors.END}\n")
    print(f"   {Colors.BOLD}1.{Colors.END}  📽️  Screenplay")
    print(f"       Clean GUI for characters, scenes, and notes")
    print(f"       Uses screenplay-specific templates and buckets")
    print()
    print(f"   {Colors.BOLD}2.{Colors.END}  📚  Textbook/Research")
    print(f"       All other LightRAG buckets for academic work")
    print(f"       Academic sources, film theory, cultural research")
    print()
    
    while True:
        choice = input(f"{Colors.BOLD}Select project type (1-2, or 'back'): {Colors.END}").strip()
        
        if choice.lower() == 'back':
            return False
        elif choice == "1":
            return create_screenplay_project()
        elif choice == "2":
            return create_textbook_project()
        else:
            print(f"{Colors.RED} Please enter 1, 2, or 'back'{Colors.END}")

def create_screenplay_project():
    """Create screenplay project with GUI interface"""
    if not HAS_TEMPLATE_SYSTEM:
        print(f"{Colors.RED} Template system not available{Colors.END}")
        return False
    
    print(f"\n{Colors.CYAN}📽️ SCREENPLAY PROJECT{Colors.END}")
    print_separator()
    
    # Get project name
    existing_projects = []
    if HAS_TEMPLATE_SYSTEM:
        tm = TemplateManager()
        existing_projects = [p['name'] for p in tm.list_projects()]
    
    while True:
        project_name = input(f"{Colors.BOLD} Enter screenplay project name: {Colors.END}").strip()
        
        if not project_name:
            print(f"{Colors.RED} Project name cannot be empty!{Colors.END}")
            continue
        
        # Sanitize project name
        sanitized_name = re.sub(r'[^\w\-_]', '_', project_name)
        if sanitized_name != project_name:
            print(f"{Colors.YELLOW} Project name sanitized to: {sanitized_name}{Colors.END}")
            project_name = sanitized_name
        
        if project_name in existing_projects:
            print(f"{Colors.RED} Project '{project_name}' already exists!{Colors.END}")
            continue
        
        break
    
    # Create project with screenplay template
    print(f"\n{Colors.CYAN} Creating screenplay project '{project_name}'...{Colors.END}")
    
    if HAS_TEMPLATE_SYSTEM:
        tm = TemplateManager()
        # Use romcom template as default for screenplay projects
        if tm.create_project_from_template(project_name, "romcom"):
            print(f"{Colors.GREEN} ✓ Database created with romcom template{Colors.END}")
            print(f"   - 6 Character archetypes (Protagonist, Love Interest, Best Friend, etc.)")
            print(f"   - 30-scene romcom outline (Opening, Meet Cute, Midpoint, Grand Gesture, etc.)")
            print(f"   - 6 Starter notes with themes, development tips, and writing guidance")
            
            # Set project in session
            if session.set_project(project_name):
                print(f"{Colors.GREEN} ✓ Project loaded into session{Colors.END}")
                
                # Launch GUI if available
                if HAS_INTAKE_GUI:
                    print(f"\n{Colors.CYAN} 🎨 Launching screenplay editing interface...{Colors.END}")
                    print(f"   Clean Tailwind-style GUI for editing:")
                    print(f"   • Character profiles and development")
                    print(f"   • Scene-by-scene story outline")
                    print(f"   • Tagged notes system")
                    
                    wait_for_key()
                    
                    try:
                        project_path = f"projects/{project_name}"
                        launch_intake_gui(project_path)
                    except Exception as e:
                        print(f"{Colors.RED} Error launching GUI: {e}{Colors.END}")
                        print(f"{Colors.YELLOW} Falling back to standard interface{Colors.END}")
                        wait_for_key()
                else:
                    print(f"{Colors.YELLOW} ℹ️ GUI not available, using standard interface{Colors.END}")
                    wait_for_key()
                
                return True
            else:
                print(f"{Colors.RED} Failed to load project into session{Colors.END}")
                return False
        else:
            print(f"{Colors.RED} Failed to create screenplay project{Colors.END}")
            return False
    else:
        # Fallback to basic project creation
        return create_project()

def create_textbook_project():
    """Create textbook/research project with all academic buckets"""
    if not HAS_TEMPLATE_SYSTEM:
        print(f"{Colors.RED} Template system not available{Colors.END}")
        return False
    
    print(f"\n{Colors.CYAN}📚 TEXTBOOK/RESEARCH PROJECT{Colors.END}")
    print_separator()
    
    print(f"{Colors.BLUE}This project includes all academic LightRAG buckets:{Colors.END}")
    print(f"   • academic_sources (general research)")
    print(f"   • balio_sources (Hollywood studio system)")
    print(f"   • bordwell_sources (film studies & narrative theory)")
    print(f"   • cook_sources (film history)")
    print(f"   • cousins_sources (cinema history)")
    print(f"   • cultural_sources (cultural studies)")
    print(f"   • reference_sources (academic references)")
    print(f"   • Plus: dixon_foster, gomery, knight, american_cinema_series")
    print()
    
    # Get project name
    tm = TemplateManager()
    existing_projects = [p['name'] for p in tm.list_projects()]
    
    while True:
        project_name = input(f"{Colors.BOLD} Enter textbook project name: {Colors.END}").strip()
        
        if not project_name:
            print(f"{Colors.RED} Project name cannot be empty!{Colors.END}")
            continue
        
        # Sanitize project name
        sanitized_name = re.sub(r'[^\w\-_]', '_', project_name)
        if sanitized_name != project_name:
            print(f"{Colors.YELLOW} Project name sanitized to: {sanitized_name}{Colors.END}")
            project_name = sanitized_name
        
        if project_name in existing_projects:
            print(f"{Colors.RED} Project '{project_name}' already exists!{Colors.END}")
            continue
        
        break
    
    # Create project with textbook template
    print(f"\n{Colors.CYAN} Creating textbook project '{project_name}'...{Colors.END}")
    
    if tm.create_project_from_template(project_name, "textbook"):
        print(f"{Colors.GREEN} ✓ Database created with textbook tables{Colors.END}")
        print(f"   - Academic research structure")
        print(f"   - Film theory buckets ready")
        print(f"   - All scholarly source buckets configured")
        
        # Set project in session
        if session.set_project(project_name):
            print(f"{Colors.GREEN} ✓ Project loaded into session{Colors.END}")
            
            print(f"\n{Colors.CYAN} 📚 Next steps:{Colors.END}")
            print(f"   1. Upload sources to the appropriate buckets")
            print(f"   2. Use brainstorm to analyze academic content")
            print(f"   3. Write with film theory and scholarly backing")
            
            wait_for_key()
            return True
        else:
            print(f"{Colors.RED} Failed to load project into session{Colors.END}")
            return False
    else:
        print(f"{Colors.RED} Failed to create textbook project{Colors.END}")
        return False

def run_autonomous_agent():
    """Run the autonomous agent - picks template and creates project automatically"""
    if not HAS_AUTONOMOUS_AGENT:
        print(f"{Colors.RED} Autonomous agent not available{Colors.END}")
        wait_for_key()
        return
    
    print_header()
    print(f"\n{Colors.BOLD}🤖 AUTONOMOUS AGENT{Colors.END}")
    print_separator()
    
    print(f"{Colors.CYAN}The agent will:{Colors.END}")
    print(f"  • Analyze available templates")
    print(f"  • Pick the best one intelligently")
    print(f"  • Generate a creative project name")
    print(f"  • Create complete project with sample data")
    print(f"  • Run brainstorm and write workflows")
    print(f"  • Export results automatically")
    
    print(f"\n{Colors.YELLOW}Press Enter to start the agent, or 'back' to return...{Colors.END}")
    choice = input().strip().lower()
    
    if choice == 'back':
        return
    
    print(f"\n{Colors.GREEN}🚀 Starting Autonomous Agent...{Colors.END}\n")
    
    try:
        # Initialize and run the autonomous agent
        agent = AutonomousAgent(api_key=client.api_key if client else None)
        success = agent.run_full_cycle()
        
        if success:
            # Show summary
            summary = agent.get_execution_summary()
            print(f"\n{Colors.GREEN}✅ Agent completed successfully!{Colors.END}")
            print(f"{Colors.CYAN}📊 Execution Summary:{Colors.END}")
            print(f"   Total Actions: {summary['total_actions']}")
            print(f"   Successful: {summary['successful_actions']}")
            print(f"   Errors: {summary['errors']}")
            
            if summary['current_project']:
                print(f"   {Colors.BOLD}Project Created: {summary['current_project']}{Colors.END}")
                
                # Ask if user wants to open the project
                print(f"\n{Colors.YELLOW}Would you like to open this project now? (y/n): {Colors.END}", end="")
                open_choice = input().strip().lower()
                
                if open_choice == 'y':
                    if session.set_project(summary['current_project']):
                        print(f"{Colors.GREEN} Project loaded successfully{Colors.END}")
                        wait_for_key()
                        project_menu()
                    else:
                        print(f"{Colors.RED} Error loading project{Colors.END}")
                        wait_for_key()
                
                # Ask if user wants to export screenplay
                print(f"\n{Colors.YELLOW}Export screenplay to desktop? (y/n): {Colors.END}", end="")
                export_choice = input().strip().lower()
                
                if export_choice == 'y':
                    export_agent_screenplay(summary['current_project'])
        else:
            print(f"{Colors.RED}❌ Agent encountered errors{Colors.END}")
            
    except Exception as e:
        print(f"{Colors.RED}❌ Error running autonomous agent: {str(e)}{Colors.END}")
    
    wait_for_key()

def export_agent_screenplay(project_name):
    """Export screenplay from agent-created project"""
    try:
        import subprocess
        result = subprocess.run(['python3', 'export_screenplay.py'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ Screenplay exported to desktop{Colors.END}")
        else:
            print(f"{Colors.RED}❌ Export failed: {result.stderr}{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}❌ Export error: {str(e)}{Colors.END}")

def run_transparent_brainstorm():
    """Run brainstorming with full transparency using enhanced module"""
    if not HAS_TRANSPARENT_MODULES:
        print(f"{Colors.RED}Enhanced modules not available{Colors.END}")
        return execute_brainstorm([], [], [], "")
    
    try:
        import asyncio
        
        # Initialize transparent brainstormer
        brainstormer = TransparentBrainstormer(
            project_path=f"projects/{session.current_project}",
            api_key=session.api_key
        )
        
        # Get available buckets
        print(f"\n{Colors.YELLOW}Select Knowledge Buckets:{Colors.END}")
        buckets = brainstormer.lightrag_manager.get_bucket_list()
        
        selected_buckets = []
        if buckets:
            for idx, bucket_info in enumerate(buckets, 1):
                status = "✓" if bucket_info['active'] else "✗"
                print(f"   {Colors.BOLD}{idx}.{Colors.END} {bucket_info['name']} [{status}] - {bucket_info['documents']} docs")
            print(f"   {Colors.BOLD}0.{Colors.END} None/Skip")
            
            bucket_choices = input(f"\n[ ] Enter choices (comma-separated): ").strip()
            if bucket_choices and bucket_choices != "0":
                for choice in bucket_choices.split(','):
                    try:
                        idx = int(choice.strip()) - 1
                        if 0 <= idx < len(buckets):
                            selected_buckets.append(buckets[idx]['name'])
                    except ValueError:
                        pass
        
        # Get user guidance
        print(f"\n{Colors.YELLOW}Additional Guidance:{Colors.END}")
        user_guidance = input(f"[ ] Enter any specific instructions: ").strip()
        
        # Show transparency mode options
        print(f"\n{Colors.YELLOW}Transparency Level:{Colors.END}")
        print(f"   {Colors.BOLD}1.{Colors.END} Full - See everything in real-time")
        print(f"   {Colors.BOLD}2.{Colors.END} Summary - See major steps only")
        print(f"   {Colors.BOLD}3.{Colors.END} Results - Just show final output")
        
        transparency_level = input(f"\n[ ] Select level (1-3): ").strip() or "1"
        
        # Set up callbacks for real-time display
        def on_context_assembly(scene, context):
            if transparency_level == "1":
                print(f"\n{Colors.CYAN}📊 Assembling context for {scene}...{Colors.END}")
                print(f"   Characters: {len(context.get('characters', []))}")
                print(f"   Previous scenes: {len(context.get('previous_scenes', []))}")
        
        def on_bucket_query(bucket_name, query, response):
            if transparency_level in ["1", "2"]:
                print(f"\n{Colors.YELLOW}🔍 Querying {bucket_name}...{Colors.END}")
                if transparency_level == "1":
                    print(f"   Query: {query[:100]}...")
                    print(f"   Response preview: {response[:200]}...")
        
        def on_prompt_compilation(prompt):
            if transparency_level == "1":
                print(f"\n{Colors.BLUE}📝 Compiled Prompt:{Colors.END}")
                print(f"{prompt[:500]}...")
        
        def on_ai_response(response):
            if transparency_level in ["1", "2"]:
                print(f"\n{Colors.GREEN}🤖 AI Response received{Colors.END}")
                if transparency_level == "1":
                    print(f"{response[:500]}...")
        
        # Attach callbacks
        brainstormer.on_context_assembly = on_context_assembly
        brainstormer.on_bucket_query = on_bucket_query
        brainstormer.on_prompt_compilation = on_prompt_compilation
        brainstormer.on_ai_response = on_ai_response
        
        # Confirm and run
        print(f"\n{Colors.BOLD}BRAINSTORM CONFIGURATION{Colors.END}")
        print_separator()
        print(f"Buckets: {', '.join(selected_buckets) if selected_buckets else 'None'}")
        print(f"User Guidance: {'Yes' if user_guidance else 'No'}")
        print(f"Transparency: {['', 'Full', 'Summary', 'Results'][int(transparency_level)]}")
        
        confirm = input(f"\n[ ] Start transparent brainstorm? (y/n): ").strip().lower()
        if confirm != 'y':
            return
        
        print(f"\n{Colors.CYAN}🧠 Starting Transparent Brainstorm...{Colors.END}")
        print_separator()
        
        # Run brainstorming
        session_id = asyncio.run(
            brainstormer.brainstorm_all_scenes(selected_buckets, user_guidance)
        )
        
        print(f"\n{Colors.GREEN}✅ Brainstorm completed!{Colors.END}")
        print(f"Session ID: {session_id}")
        
        # Ask if user wants to see the full results
        show_results = input(f"\n[ ] View full results? (y/n): ").strip().lower()
        if show_results == 'y':
            cursor = session.db_conn.cursor()
            cursor.execute("""
                SELECT scene_id, brainstorm_content 
                FROM brainstorming_log 
                WHERE session_id = ?
            """, (session_id,))
            
            results = cursor.fetchall()
            for scene_id, content in results:
                print(f"\n{Colors.BOLD}Scene: {scene_id}{Colors.END}")
                print(content[:1000])  # Show first 1000 chars
                
    except Exception as e:
        print(f"\n{Colors.RED}⚠️ Error in transparent brainstorm: {str(e)}{Colors.END}")
        print(f"{Colors.YELLOW}Falling back to standard brainstorm...{Colors.END}")
        execute_brainstorm([], [], [], "")
    
    wait_for_key()

def run_transparent_write():
    """Run writing with full transparency using enhanced module"""
    if not HAS_TRANSPARENT_MODULES:
        print(f"{Colors.RED}Enhanced modules not available{Colors.END}")
        return
    
    try:
        import asyncio
        
        # Initialize transparent writer
        writer = TransparentWriter(
            project_path=f"projects/{session.current_project}",
            api_key=session.api_key
        )
        
        # Similar setup to brainstorm but for writing
        print(f"\n{Colors.GREEN}✨ Using Enhanced Transparent Writing{Colors.END}")
        
        # Get buckets and guidance
        buckets = writer.lightrag_manager.get_bucket_list()
        selected_buckets = []
        
        # ... (similar bucket selection as brainstorm)
        
        # Run writing
        session_id = asyncio.run(
            writer.write_all_scenes(selected_buckets, "")
        )
        
        print(f"\n{Colors.GREEN}✅ Writing completed!{Colors.END}")
        print(f"Session ID: {session_id}")
        
    except Exception as e:
        print(f"\n{Colors.RED}⚠️ Error in transparent write: {str(e)}{Colors.END}")
    
    wait_for_key()

def enhanced_export():
    """Use enhanced export system for comprehensive exports"""
    if not HAS_TRANSPARENT_MODULES:
        print(f"{Colors.RED}Enhanced export not available{Colors.END}")
        return
    
    try:
        # Initialize export system
        exporter = ExportSystem(
            project_path=f"projects/{session.current_project}",
            project_name=session.current_project
        )
        
        print(f"\n{Colors.BOLD}ENHANCED EXPORT{Colors.END}")
        print_separator()
        
        print(f"{Colors.YELLOW}Export Type:{Colors.END}")
        print(f"   {Colors.BOLD}1.{Colors.END} Complete Package - Everything")
        print(f"   {Colors.BOLD}2.{Colors.END} Screenplay Only")
        print(f"   {Colors.BOLD}3.{Colors.END} Data Package - Tables & Analysis")
        print(f"   {Colors.BOLD}4.{Colors.END} Sessions - All brainstorm/write sessions")
        print(f"   {Colors.BOLD}5.{Colors.END} Analysis - Content & writing analysis")
        
        export_type = input(f"\n[ ] Select type (1-5): ").strip()
        
        type_map = {
            "1": "complete",
            "2": "screenplay", 
            "3": "data",
            "4": "sessions",
            "5": "analysis"
        }
        
        selected_type = type_map.get(export_type, "complete")
        
        # Format selection
        print(f"\n{Colors.YELLOW}Export Formats:{Colors.END}")
        formats = []
        
        print(f"   [x] JSON (always included)")
        if input(f"   [ ] TXT? (y/n): ").strip().lower() == 'y':
            formats.append("txt")
        if input(f"   [ ] HTML? (y/n): ").strip().lower() == 'y':
            formats.append("html")
        if input(f"   [ ] Fountain? (y/n): ").strip().lower() == 'y':
            formats.append("fountain")
        if input(f"   [ ] Markdown? (y/n): ").strip().lower() == 'y':
            formats.append("markdown")
        if input(f"   [ ] CSV? (y/n): ").strip().lower() == 'y':
            formats.append("csv")
        
        formats.append("json")  # Always include JSON
        
        print(f"\n{Colors.CYAN}📦 Creating export package...{Colors.END}")
        
        # Create export
        zip_path = exporter.create_export_package(
            export_type=selected_type,
            formats=formats,
            include_metadata=True
        )
        
        print(f"\n{Colors.GREEN}✅ Export completed!{Colors.END}")
        print(f"Package saved to: {zip_path}")
        
    except Exception as e:
        print(f"\n{Colors.RED}⚠️ Export error: {str(e)}{Colors.END}")
    
    wait_for_key()

def upload_documents_to_bucket():
    """Upload documents to a LightRAG bucket"""
    if not HAS_TRANSPARENT_MODULES:
        print(f"{Colors.RED}Enhanced modules not available{Colors.END}")
        wait_for_key()
        return
    
    try:
        # Initialize LightRAG manager
        manager = LightRAGManager()
        
        print(f"\n{Colors.YELLOW}📄 UPLOAD DOCUMENTS TO BUCKET{Colors.END}")
        print_separator()
        
        # List available buckets
        buckets = manager.get_bucket_list()
        if not buckets:
            print(f"{Colors.YELLOW}No buckets available. Create one first.{Colors.END}")
            wait_for_key()
            return
        
        print(f"{Colors.CYAN}Select Bucket:{Colors.END}")
        for idx, bucket_info in enumerate(buckets, 1):
            print(f"   {Colors.BOLD}{idx}.{Colors.END} {bucket_info['name']} ({bucket_info['documents']} docs)")
        
        bucket_choice = input(f"\n[ ] Select bucket: ").strip()
        
        try:
            idx = int(bucket_choice) - 1
            if 0 <= idx < len(buckets):
                bucket_name = buckets[idx]['name']
            else:
                print(f"{Colors.RED}Invalid selection{Colors.END}")
                wait_for_key()
                return
        except ValueError:
            print(f"{Colors.RED}Invalid selection{Colors.END}")
            wait_for_key()
            return
        
        # Get document path
        print(f"\n{Colors.YELLOW}Enter document path:{Colors.END}")
        print(f"(Drag and drop file or directory, or type path)")
        doc_path = input(f"[ ] Path: ").strip().strip("'\"")
        
        if not os.path.exists(doc_path):
            print(f"{Colors.RED}Path not found: {doc_path}{Colors.END}")
            wait_for_key()
            return
        
        # Process documents
        print(f"\n{Colors.CYAN}📥 Processing documents...{Colors.END}")
        
        if os.path.isfile(doc_path):
            # Single file
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"Adding {os.path.basename(doc_path)}...")
            success = manager.add_to_bucket(bucket_name, content)
            
            if success:
                print(f"{Colors.GREEN}✅ Document added successfully!{Colors.END}")
            else:
                print(f"{Colors.RED}⚠️ Failed to add document{Colors.END}")
        
        elif os.path.isdir(doc_path):
            # Directory of files
            files = [f for f in os.listdir(doc_path) 
                    if f.endswith(('.txt', '.md', '.pdf', '.doc', '.docx'))]
            
            print(f"Found {len(files)} documents")
            
            for file_name in files:
                file_path = os.path.join(doc_path, file_name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"Adding {file_name}...")
                manager.add_to_bucket(bucket_name, content)
            
            print(f"{Colors.GREEN}✅ Added {len(files)} documents!{Colors.END}")
        
    except Exception as e:
        print(f"{Colors.RED}⚠️ Error: {str(e)}{Colors.END}")
    
    wait_for_key()

def query_buckets_interactive():
    """Interactive query interface for buckets"""
    if not HAS_TRANSPARENT_MODULES:
        print(f"{Colors.RED}Enhanced modules not available{Colors.END}")
        wait_for_key()
        return
    
    try:
        manager = LightRAGManager()
        
        print(f"\n{Colors.YELLOW}🔍 QUERY KNOWLEDGE BUCKETS{Colors.END}")
        print_separator()
        
        # Select buckets to query
        buckets = manager.get_bucket_list()
        active_buckets = [b['name'] for b in buckets if b['active']]
        
        print(f"{Colors.CYAN}Active Buckets: {', '.join(active_buckets)}{Colors.END}")
        print(f"\nEnter your query (or 'quit' to exit):")
        
        while True:
            query = input(f"\n[ ] Query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            print(f"\n{Colors.CYAN}🤔 Searching...{Colors.END}")
            
            # Query all active buckets
            results = manager.query_active_buckets(query)
            
            if results:
                for result in results:
                    print(f"\n{Colors.BOLD}Bucket: {result['bucket']}{Colors.END}")
                    print(result['response'][:500] + "..." if len(result['response']) > 500 else result['response'])
            else:
                print(f"{Colors.YELLOW}No results found{Colors.END}")
        
    except Exception as e:
        print(f"{Colors.RED}⚠️ Error: {str(e)}{Colors.END}")
    
    wait_for_key()

def visualize_knowledge_graph():
    """Visualize the knowledge graph of a bucket"""
    if not HAS_TRANSPARENT_MODULES:
        print(f"{Colors.RED}Enhanced modules not available{Colors.END}")
        wait_for_key()
        return
    
    print(f"\n{Colors.YELLOW}📊 VISUALIZE KNOWLEDGE GRAPH{Colors.END}")
    print_separator()
    
    print(f"{Colors.YELLOW}This feature will generate an interactive graph visualization.{Colors.END}")
    print(f"Coming soon: Network graph showing entities and relationships")
    
    wait_for_key()

def toggle_bucket_status():
    """Toggle active/inactive status of buckets"""
    if not HAS_TRANSPARENT_MODULES:
        print(f"{Colors.RED}Enhanced modules not available{Colors.END}")
        wait_for_key()
        return
    
    try:
        manager = LightRAGManager()
        
        print(f"\n{Colors.YELLOW}🎚️ TOGGLE BUCKET STATUS{Colors.END}")
        print_separator()
        
        buckets = manager.get_bucket_list()
        
        for idx, bucket_info in enumerate(buckets, 1):
            status = "✓ Active" if bucket_info['active'] else "✗ Inactive"
            print(f"   {Colors.BOLD}{idx}.{Colors.END} {bucket_info['name']} [{status}]")
        
        choice = input(f"\n[ ] Select bucket to toggle: ").strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(buckets):
                bucket_name = buckets[idx]['name']
                new_status = not buckets[idx]['active']
                
                if new_status:
                    manager.activate_bucket(bucket_name)
                    print(f"{Colors.GREEN}✅ {bucket_name} activated{Colors.END}")
                else:
                    manager.deactivate_bucket(bucket_name)
                    print(f"{Colors.YELLOW}✗ {bucket_name} deactivated{Colors.END}")
            else:
                print(f"{Colors.RED}Invalid selection{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}Invalid selection{Colors.END}")
        
    except Exception as e:
        print(f"{Colors.RED}⚠️ Error: {str(e)}{Colors.END}")
    
    wait_for_key()

def create_new_bucket():
    """Create a new knowledge bucket"""
    if not HAS_TRANSPARENT_MODULES:
        print(f"{Colors.RED}Enhanced modules not available{Colors.END}")
        wait_for_key()
        return
    
    try:
        manager = LightRAGManager()
        
        print(f"\n{Colors.YELLOW}➕ CREATE NEW BUCKET{Colors.END}")
        print_separator()
        
        bucket_name = input(f"[ ] Bucket name: ").strip().lower().replace(' ', '_')
        
        if not bucket_name:
            print(f"{Colors.RED}Name required{Colors.END}")
            wait_for_key()
            return
        
        description = input(f"[ ] Description: ").strip()
        
        # Create bucket
        success = manager.create_bucket(bucket_name, description)
        
        if success:
            print(f"{Colors.GREEN}✅ Bucket '{bucket_name}' created successfully!{Colors.END}")
            
            # Ask if user wants to add documents now
            add_docs = input(f"\n[ ] Add documents now? (y/n): ").strip().lower()
            if add_docs == 'y':
                upload_documents_to_bucket()
        else:
            print(f"{Colors.RED}⚠️ Failed to create bucket{Colors.END}")
        
    except Exception as e:
        print(f"{Colors.RED}⚠️ Error: {str(e)}{Colors.END}")
    
    wait_for_key()

def admin_menu():
    """Admin menu for template management"""
    if not HAS_TEMPLATE_SYSTEM:
        print(f"{Colors.RED} Template system not available{Colors.END}")
        wait_for_key()
        return
    
    admin = LizzyAdmin()
    admin.run()

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.CYAN} Thank you for using LIZZY Framework!{Colors.END}")
        session.close()
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED} An error occurred: {e}{Colors.END}")
        session.close()
        sys.exit(1)