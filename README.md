# LIZZY Framework - Complete User Manual

## AI-Assisted Screenwriting System

LIZZY is an intelligent screenwriting CLI that transforms your creative ideas into professional screenplays through a structured, AI-powered workflow. Think of it as your personal writing studio that combines your unique story vision with the craft knowledge of master screenwriters.

<div align="center">

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    ██╗     ██╗███████╗███████╗██╗   ██╗                     ║
║                    ██║     ██║╚══███╔╝╚══███╔╝╚██╗ ██╔╝                     ║
║                    ██║     ██║  ███╔╝   ███╔╝  ╚████╔╝                      ║
║                    ██║     ██║ ███╔╝   ███╔╝    ╚██╔╝                       ║
║                    ███████╗██║███████╗███████╗   ██║                        ║
║                    ╚══════╝╚═╝╚══════╝╚══════╝   ╚═╝                        ║
║                                                                              ║
║               AI-ASSISTED SCREENWRITING SYSTEM                           ║
║                     ~ Structure • Intelligence • Craft ~                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**From Story Idea to Professional Screenplay in Minutes, Not Months**

</div>

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [System Overview](#system-overview)
3. [Main Interface Guide](#main-interface-guide)
4. [🤖 Autonomous Agent](#autonomous-agent)
5. [Project Management](#project-management)
6. [Template System](#template-system)
7. [Knowledge Base (Buckets)](#knowledge-base-buckets)
8. [AI Workflows](#ai-workflows)
9. [Export System](#export-system)
10. [Admin Features](#admin-features)
11. [Advanced Usage](#advanced-usage)
12. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites
- **Python 3.8+** (check with `python3 --version`)
- **OpenAI API key** ([get one here](https://platform.openai.com/api-keys))
- **5 minutes** to set up your first screenplay

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/ejresearch/Elizabeth_PI.git
cd Elizabeth_PI

# 2. Install dependencies
pip install openai lightrag-hku tiktoken numpy

# 3. Launch LIZZY
python3 lizzy.py
```

### First Time Setup
1. Run `python3 lizzy.py`
2. Enter your OpenAI API key when prompted
3. Choose option 3 (🤖 Auto Agent) for instant screenplay generation
4. Or choose option 1 (New Project) for manual project creation

---

## System Overview

### What LIZZY Does

LIZZY guides you through the complete screenwriting process using a proven workflow:

**Your Input** → **AI Enhancement** → **Professional Output**

- **🎭 Story Development**: Build rich characters and compelling scene outlines
- **📚 Knowledge Integration**: Access curated screenwriting wisdom and techniques  
- **🧠 AI Brainstorming**: Generate creative ideas contextual to YOUR specific story
- **✍️ Screenplay Writing**: Produce properly formatted scenes with authentic dialogue
- **📋 Version Management**: Track every iteration with complete revision history
- **📤 Professional Export**: Output industry-standard formats ready for production
- **🤖 Autonomous Agent**: One-click project creation from template to screenplay

### Core Architecture

```
LIZZY Framework
├── Main Interface (lizzy.py)
├── 🤖 Autonomous Agent (autonomous_agent.py)
├── Template System (template_manager.py)
├── Project Database (SQLite per project)
├── Knowledge Base (LightRAG + buckets)
├── AI Workflows (brainstorm.py, write.py)
└── Export System (export_screenplay.py)
```

---

## Main Interface Guide

Launch LIZZY with `python3 lizzy.py` to access the main menu:

```
LIZZY
════════════════════════════════════════════════════════════════════════════════
   1.  New Project
   2.  Existing Project
   3.  🤖 Auto Agent (Pick Template & Go)
   4.  Getting Started
   5.   Admin
   6.  Exit
```

### Option 1: New Project

**Manual Project Creation**

1. **Select Template**: Choose from available templates (romcom, textbook, custom)
2. **Name Project**: Enter a unique project name
3. **Database Creation**: LIZZY creates isolated SQLite database
4. **Template Setup**: Tables and schema configured automatically

**Template Selection Process:**
```
Available Templates:
──────────────────────────────────────────────────────────────
1. Romantic Comedy 
   A template for character-driven romantic comedies
   Version: 1.0

2. Academic Textbook 
   Template for educational textbooks with structured learning
   Version: 1.0

Select template (1-2): 1
```

**Project Naming:**
- Use descriptive names: `my_romantic_comedy`, `thriller_script_v2`
- Avoid spaces (use underscores)
- Names become folder and database names

### Option 2: Existing Project

**Load Previous Work**

Displays all existing projects with creation dates:
```
SELECT PROJECT
════════════════════════════════════════════════════════════════════════════════
Available Projects:
   1. the_wrong_wedding_20250731_1328 (created: 2025-07-31)
   2. coffee_shop_romance_20250731_1326 (created: 2025-07-31)
   3. my_thriller_screenplay (created: 2025-07-30)

Select project number (or 'back' to return): 1
```

**Project Information Displayed:**
- Project name and creation date
- Template type used
- Last modification time
- Database status

### Option 3: 🤖 Auto Agent (Pick Template & Go)

**Fully Automated Project Creation**

The autonomous agent eliminates manual setup:

```
🤖 AUTONOMOUS AGENT
════════════════════════════════════════════════════════════════════════════════
The agent will:
  • Analyze available templates
  • Pick the best one intelligently
  • Generate a creative project name
  • Create complete project with sample data
  • Run brainstorm and write workflows
  • Export results automatically

Press Enter to start the agent, or 'back' to return...
```

**Agent Execution Process:**
1. **Template Analysis**: Scores templates based on stability, descriptions, randomness
2. **Intelligent Selection**: Picks optimal template automatically
3. **Name Generation**: Creates unique, timestamp-based project names
4. **Project Creation**: Full database setup with proper schema
5. **Data Population**: Template-appropriate sample characters and story elements
6. **Workflow Execution**: Runs brainstorm and write sessions
7. **Results Export**: Automatic export with execution log

**Post-Completion Options:**
- Open created project immediately
- Export screenplay to desktop
- View execution summary

### Option 4: Getting Started

**Documentation and Help**

Displays the complete README content within the interface, including:
- Installation instructions
- Basic usage examples
- Workflow explanations
- Feature overviews

### Option 5: Admin

**Template and System Management**

Access to advanced configuration:
- Template editing and creation
- System settings
- Database management
- Bucket configuration

### Option 6: Exit

**Clean System Shutdown**

Properly closes all database connections and exits the system.

---

## 🤖 Autonomous Agent

The autonomous agent is LIZZY's flagship feature for instant screenplay generation.

### How It Works

**Intelligent Template Selection:**
```python
# Agent scoring algorithm:
score = 0
if not template['is_custom']: score += 10  # Prefer stable templates
if template['description']: score += 5     # Prefer documented templates
score += random.randint(1, 5)             # Add variety
```

**Creative Name Generation:**
- Template-specific patterns:
  - Romcom: `coffee_shop_romance`, `midnight_in_brooklyn`, `the_wrong_wedding`
  - Textbook: `modern_studies`, `comprehensive_guide`, `essential_concepts`
- Timestamp suffix for uniqueness: `_20250731_1328`

**Sample Data Population:**

For Romantic Comedy:
```
Characters Created:
- Maya Chen (28, Female): Finds humor in disasters, terrible at social cues
- Jake Morrison (30, Male): Genuinely cares about everyone, explains jokes

Story Outline:
- Act 1, Scene 1: Meet-cute at coffee shop disaster
- Act 1, Scene 2: Awkward second encounter at bookstore
- Act 2, Scene 1: Forced together by circumstances
- Act 2, Scene 2: Growing chemistry despite mishaps
- Act 3, Scene 1: Resolution and romantic climax
```

### Agent Execution Log

The agent maintains detailed logs:
```json
{
  "timestamp": "2025-07-31T13:28:51",
  "action": "Selected template: romcom",
  "details": "Score: 20",
  "status": "success"
}
```

### Using Agent Results

**Immediate Options After Completion:**
1. **Open Project**: Load into full LIZZY interface for editing
2. **Export Screenplay**: Generate formatted screenplay files
3. **View Summary**: Review execution statistics

**Generated Files:**
- `projects/[project_name]/[project_name].sqlite` - Complete project database
- `exports/[project_name]/execution_log.json` - Agent activity log
- `exports/[project_name]/[project_name]_screenplay.txt` - Formatted screenplay
- `exports/[project_name]/[project_name]_characters.txt` - Character development sheet

---

## Project Management

Once a project is loaded, you enter the project-specific interface:

```
PROJECT: my_romantic_comedy
Current Template: Romantic Comedy (romcom)
Database: ✓ Connected | Tables: 3 | Records: 8
════════════════════════════════════════════════════════════════════════════════
   1.  Update Tables
   2.  Update Buckets
   3.  Brainstorm
   4.  Write
   5.  Version History
   6.  Export Options
   7.  Back to Main Menu
```

### Option 1: Update Tables

**Character Development Interface**

Access your story's core elements:

**Characters Table:**
```
CHARACTER EDITOR
════════════════════════════════════════════════════════════════════════════════
Current Characters:
1. Maya Chen (Female, 28)
   • Lovable Trait: Finds humor in disasters
   • Comedic Flaw: Terrible at reading social cues
   • Romantic Challenge: Fears vulnerability after bad breakup

2. Jake Morrison (Male, 30)
   • Lovable Trait: Genuinely cares about everyone
   • Comedic Flaw: Explains jokes after telling them
   • Romantic Challenge: Overanalyzes everything

Options:
   1. Add New Character
   2. Edit Existing Character
   3. Delete Character
   4. View All Characters
   5. Back to Project Menu
```

**Adding a New Character:**
```
ADD NEW CHARACTER
────────────────────────────────────────────────────────────────────────────────
Name: Sarah Williams
Gender: Female  
Age: 26
Romantic Challenge: Workaholic who forgot how to have fun
Lovable Trait: Incredibly organized and reliable
Comedic Flaw: Takes everything literally
Notes: Maya's best friend and voice of reason

Character added successfully!
```

**Story Outline Table:**
```
STORY OUTLINE EDITOR
════════════════════════════════════════════════════════════════════════════════
Three-Act Structure:

ACT 1:
   Scene 1.1: Maya, Jake | Meet-cute at coffee shop disaster
   Scene 1.2: Maya, Jake | Awkward second encounter at bookstore

ACT 2:
   Scene 2.1: Maya, Jake | Forced together by circumstances
   Scene 2.2: Maya, Jake | Growing chemistry despite mishaps

ACT 3:
   Scene 3.1: Maya, Jake | Resolution and romantic climax

Options:
   1. Add New Scene
   2. Edit Existing Scene
   3. Delete Scene
   4. Reorganize Act Structure
   5. Back to Project Menu
```

**Notes Table:**
```
NOTES MANAGER
════════════════════════════════════════════════════════════════════════════════
Categories: story_ideas (3), dialogue_snippets (2), visual_concepts (1)

Recent Notes:
1. [story_ideas] Coffee shop disaster - Maya spills on important documents
2. [dialogue_snippets] "I have a gift for turning simple tasks into disasters"
3. [visual_concepts] Papers flying in slow motion during collision scene

Options:
   1. Add New Note
   2. Search Notes
   3. Edit Note
   4. Delete Note
   5. Export Notes
   6. Back to Project Menu
```

### Option 2: Update Buckets

**Knowledge Base Management**

Buckets store reference materials that inform AI generation:

```
BUCKET MANAGER
════════════════════════════════════════════════════════════════════════════════
Recommended for Romantic Comedy:
   ✓ books (3 files) - Screenwriting theory and romantic comedy guides
   ✓ scripts (45 files) - Professional romantic comedy screenplays
   ✓ plays (12 files) - Theatrical works with romantic themes

Additional Buckets:
   ○ cultural_sources (0 files) - Cultural context and references
   ○ reference_sources (8 files) - General academic references

Options:
   1. Upload Files to Bucket
   2. View Bucket Contents
   3. Remove Files from Bucket
   4. Create New Bucket
   5. Back to Project Menu
```

**Uploading to Buckets:**
```
UPLOAD TO BUCKET: books
────────────────────────────────────────────────────────────────────────────────
Supported formats: .txt, .pdf, .md

Drag and drop files here, or enter file paths:
> /Users/username/Documents/Save_The_Cat_Writes_A_Novel.pdf
> /Users/username/Documents/Romantic_Comedy_Structure.txt

Processing files...
✓ Save_The_Cat_Writes_A_Novel.pdf processed (45 pages)
✓ Romantic_Comedy_Structure.txt processed (12 pages)

Files successfully added to books bucket!
Knowledge base updated for AI generation.
```

### Option 3: Brainstorm

**AI-Powered Creative Session**

Generate ideas specific to your project:

```
BRAINSTORM SESSION
════════════════════════════════════════════════════════════════════════════════
Select Knowledge Sources:
   ☑ books - Screenwriting theory and romantic comedy guides
   ☑ scripts - Professional romantic comedy screenplays
   ☐ plays - Theatrical works with romantic themes
   ☐ cultural_sources - Cultural context and references

Select Project Elements:
   ☑ characters - Your story's characters and their traits
   ☑ story_outline - Three-act structure and scene breakdown
   ☑ notes - Your creative notes and ideas

Additional Guidance (optional):
> Focus on meet-cute scenarios that showcase character flaws

Starting brainstorm session...
```

**Brainstorm Output Example:**
```
BRAINSTORM RESULTS - Session #3
Generated: 2025-07-31 at 1:45 PM
Duration: 2 minutes 34 seconds
════════════════════════════════════════════════════════════════════════════════

CHARACTER DYNAMICS:
• Maya's disaster-prone nature creates perfect setup for Jake's over-caring response
• Jake's joke-explaining flaw could interrupt romantic moments, creating comedic beats
• Their challenges (vulnerability vs. over-analysis) create perfect conflict resolution arc

SCENE CONCEPTS:
• Coffee shop disaster: Maya's social awkwardness leads to misunderstanding about Jake's intentions
• Bookstore encounter: Jake over-explains a book recommendation, Maya misreads his literary analysis as romantic interest
• Forced collaboration: Wedding planning disaster brings them together professionally

DIALOGUE IDEAS:
• Maya: "I have a gift for turning meet-cutes into meet-disasters"
• Jake: "That joke was funnier in my head. Let me explain why..."
• Maya: "Do you always narrate your own emotional journey?"

VISUAL MOMENTS:
• Papers flying in slow motion during coffee collision
• Jake's elaborate hand gestures while explaining simple concepts
• Maya's visible internal monologue during social confusion

STORY DEVELOPMENT:
• Act 1 Focus: Establish their flaws through meet-cute disasters
• Act 2 Complications: Professional collaboration forces them to work together
• Act 3 Resolution: They help each other overcome their respective challenges

Results saved to: brainstorm_results_20250731_134500.txt
```

### Option 4: Write

**AI Screenplay Generation**

Transform brainstorm ideas into formatted scenes:

```
WRITE SESSION
════════════════════════════════════════════════════════════════════════════════
Available Brainstorm Sessions:
   1. Session #3 (2025-07-31 1:45 PM) - Meet-cute scenarios
   2. Session #2 (2025-07-31 1:20 PM) - Character development
   3. Session #1 (2025-07-31 1:00 PM) - Initial story concepts

Select brainstorm to use: 1

Writing Style:
   1. Screenplay (Industry standard format)
   2. Treatment (Narrative prose)
   3. Novel excerpt (Literary style)

Select style: 1

Specific Direction (optional):
> Write the opening coffee shop scene with focus on physical comedy

Generating screenplay content...
```

**Generated Screenplay Example:**
```
FADE IN:

INT. DOWNTOWN COFFEE SHOP - MORNING

The morning rush is in full swing. MAYA CHEN (28, paint-stained 
apron, sketchbook clutched protectively) navigates through the 
crowd like she's defusing a bomb.

She spots an empty corner table. Her eyes light up.

                    MAYA
                    (whispered)
          Perfect. Just don't mess this up.

Maya makes a beeline for the table, focused entirely on her 
destination. She doesn't see JAKE MORRISON (30, rumpled business 
casual, juggling phone and laptop bag) approaching from the 
opposite direction.

COLLISION.

Coffee erupts in all directions. Maya's sketchbook flies open, 
pages fluttering like confetti. Jake's laptop bag spills its 
contents across the floor.

Beat. They both stare at the disaster zone.

                    MAYA
                    (surveying the carnage)
          I have a gift for turning simple 
          tasks into abstract art.

JAKE kneels to help gather the scattered pages, his phone still 
pressed to his ear.

                    JAKE
                    (into phone)
          Let me call you back. I'm in the 
          middle of what appears to be a 
          Jackson Pollock meets morning 
          caffeine crisis situation.

He hangs up and looks at Maya, who's holding a coffee-stained 
sketch of two people sharing an umbrella.

                    JAKE (CONT'D)
          Is that... us?

                    MAYA
          It's a couple. Generic couple. 
          Definitely not prophetic or anything.

                    JAKE
          I was about to say it's either the 
          worst meet-cute in cinematic history 
          or refreshingly honest.

Maya looks up. Their eyes meet over the ruined sketch.

                    MAYA
          Why not both?

FADE OUT.

Scene saved as: coffee_shop_opening_20250731_150000.txt
Word count: 347 words | Format: Screenplay | Duration: ~2.5 minutes
```

### Option 5: Version History

**Complete Revision Tracking**

View and manage all project iterations:

```
VERSION HISTORY
════════════════════════════════════════════════════════════════════════════════
BRAINSTORM SESSIONS:
   BS_20250731_145000 - Meet-cute scenarios (347 words)
   BS_20250731_132000 - Character development (289 words)  
   BS_20250731_130000 - Initial story concepts (156 words)

WRITE SESSIONS:
   WS_20250731_150000 - Coffee shop opening scene (347 words)
   WS_20250731_140000 - Character introduction draft (412 words)

OPTIONS:
   1. View Specific Version
   2. Compare Versions
   3. Restore Previous Version
   4. Export Version History
   5. Delete Old Versions
   6. Back to Project Menu
```

**Version Comparison:**
```
COMPARING VERSIONS
────────────────────────────────────────────────────────────────────────────────
Version A: WS_20250731_140000 (Character introduction draft)
Version B: WS_20250731_150000 (Coffee shop opening scene)

DIFFERENCES:
+ Added physical comedy elements
+ Enhanced dialogue with character-specific quirks
+ Improved scene description and pacing
+ Added visual metaphor (Jackson Pollock reference)

STATISTICS:
Version A: 412 words, 3.2 min runtime
Version B: 347 words, 2.5 min runtime
Change: -65 words (-15.8%), -0.7 min runtime

Recommendation: Version B is more focused and comedically stronger.
```

### Option 6: Export Options

**Professional Output Generation**

Multiple export formats for different needs:

```
EXPORT OPTIONS
════════════════════════════════════════════════════════════════════════════════
   1. Export Brainstorm Sessions
   2. Export Write Sessions  
   3. Export Complete Project
   4. Export Character Development
   5. Export Story Outline
   6. Export Everything (Archive)
   7. Quick Export to Desktop
   8. Back to Project Menu
```

**Export Destinations:**
- `exports/[project_name]/` - Organized by project
- Desktop (for quick access)
- Custom directory (user specified)

**Export Formats:**
- `.txt` - Universal text format
- `.md` - Markdown with formatting
- `.json` - Structured data export
- `.pdf` - Professional presentation format

---

## Template System

Templates define project structure and AI behavior patterns.

### Available Templates

**1. Romantic Comedy (romcom)**
```json
{
  "name": "Romantic Comedy",
  "version": "1.0",
  "description": "Template for romantic comedy screenplays with character-driven humor",
  "tables": {
    "characters": {
      "fields": {
        "name": "TEXT NOT NULL",
        "gender": "TEXT",
        "age": "TEXT", 
        "romantic_challenge": "TEXT",
        "lovable_trait": "TEXT",
        "comedic_flaw": "TEXT"
      }
    },
    "story_outline": {
      "fields": {
        "act": "INTEGER NOT NULL",
        "scene": "INTEGER NOT NULL",
        "key_characters": "TEXT",
        "key_events": "TEXT"
      }
    }
  }
}
```

**2. Academic Textbook (textbook)**
```json
{
  "name": "Academic Textbook", 
  "version": "1.0",
  "description": "Template for educational textbooks with structured learning objectives",
  "tables": {
    "chapters": {
      "fields": {
        "chapter_number": "INTEGER NOT NULL",
        "chapter_title": "TEXT NOT NULL",
        "introduction_text": "TEXT"
      }
    },
    "learning_objectives": {
      "fields": {
        "chapter_id": "INTEGER NOT NULL",
        "objective_text": "TEXT NOT NULL",
        "bloom_level": "TEXT"
      }
    }
  }
}
```

### Template Components

**Database Schema:**
- Defines table structure for project data
- Specifies required fields and data types
- Establishes relationships between tables

**AI Prompts:**
- Brainstorm guidance for different tones and styles
- Bucket-specific instructions for knowledge integration
- Writing style templates for output formatting

**Recommended Buckets:**
- Suggests knowledge sources relevant to template type
- Provides descriptions for each bucket's purpose
- Guides users toward effective knowledge curation

### Creating Custom Templates

Custom templates go in `templates/custom/`:

```json
{
  "name": "My Custom Template",
  "version": "1.0", 
  "description": "Description of your template",
  "tables": {
    "your_table": {
      "fields": {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "your_field": "TEXT NOT NULL"
      },
      "required": ["your_field"],
      "display_name": "Your Table",
      "description": "What this table stores"
    }
  },
  "buckets": {
    "recommended": ["bucket1", "bucket2"],
    "descriptions": {
      "bucket1": "Purpose of this bucket"
    }
  }
}
```

---

## Knowledge Base (Buckets)

Buckets store reference materials that inform AI generation.

### Available Buckets

**Core Buckets:**
- `books/` - Screenwriting guides, writing theory
- `scripts/` - Professional screenplay examples  
- `plays/` - Theatrical works, dialogue examples

**Specialized Buckets:**
- `bordwell_sources/` - Film theory and analysis
- `cook_sources/` - Film history perspectives
- `cultural_sources/` - Cultural context and references
- `reference_sources/` - General academic materials

### Bucket Management

**Adding Files:**
1. Navigate to "Update Buckets" in project menu
2. Select target bucket
3. Upload files (.txt, .pdf, .md formats supported)
4. Files are processed and indexed automatically

**File Processing:**
- Text extraction from PDFs
- Chunking for AI consumption
- Semantic indexing with LightRAG
- Metadata storage for retrieval

**Usage in AI Generation:**
- Brainstorm sessions draw relevant knowledge
- Write sessions incorporate stylistic patterns
- Context-aware suggestions based on uploaded content

---

## AI Workflows

### Brainstorm Workflow

**Input Processing:**
1. Selected project elements (characters, outline, notes)
2. Chosen knowledge buckets (books, scripts, etc.)
3. User guidance and specific directions
4. Template-specific prompt engineering

**AI Generation Process:**
```python
# Simplified workflow
context = assemble_project_context(characters, outline, notes)
knowledge = retrieve_relevant_knowledge(selected_buckets, context)
prompt = build_brainstorm_prompt(template, guidance, context, knowledge)
result = ai_generate(prompt)
formatted_output = format_brainstorm_results(result)
```

**Output Structure:**
- Character dynamics and development ideas
- Scene concepts and story beats
- Dialogue suggestions and voice patterns
- Visual moments and cinematography ideas
- Story development recommendations

### Write Workflow

**Input Processing:**
1. Selected brainstorm session results
2. Writing style preferences (screenplay, treatment, novel)
3. Specific scene or content directions
4. Template formatting guidelines

**Generation Process:**
```python
# Simplified workflow  
brainstorm_context = load_brainstorm_session(selected_session)
style_guide = get_style_template(selected_style)  
scene_direction = parse_user_guidance(user_input)
prompt = build_write_prompt(brainstorm_context, style_guide, scene_direction)
content = ai_generate(prompt)
formatted_scene = apply_formatting(content, style_guide)
```

**Output Formatting:**
- **Screenplay**: Industry-standard format with proper sluglines
- **Treatment**: Narrative prose with visual descriptions  
- **Novel**: Literary style with internal thoughts and rich description

---

## Export System

### Automatic Export (Autonomous Agent)

The agent automatically exports:
- `execution_log.json` - Complete activity log
- `[project]_screenplay.txt` - Formatted screenplay
- `[project]_characters.txt` - Character development sheet

### Manual Export Options

**Individual Exports:**
1. **Brainstorm Sessions** - All creative session results
2. **Write Sessions** - All generated content
3. **Character Development** - Character sheets and analysis
4. **Story Outline** - Three-act structure breakdown
5. **Complete Project** - Everything in organized format

**Export Formats:**

**Screenplay Format:**
```
THE WRONG WEDDING

A Romantic Comedy

Created by LIZZY Framework
Generated on July 31, 2025

FADE IN:

INT. COFFEE SHOP - MORNING

MAYA CHEN enters the bustling coffee shop...
```

**Character Development:**
```
CHARACTER DEVELOPMENT SHEET
════════════════════════════════════════════════════════════════════════════════

CHARACTER 1: MAYA CHEN
────────────────────────────────────────────────────────────────────────────────
Basic Info:
  • Name: Maya Chen
  • Gender: Female  
  • Age: 28

Character Arc:
  • Lovable Trait: Finds humor in disasters
  • Comedic Flaw: Terrible at reading social cues
  • Romantic Challenge: Fears vulnerability after bad breakup
```

### Quick Export to Desktop

For immediate access, use "Quick Export to Desktop":
- Copies key files directly to desktop
- Names files clearly for easy identification
- Includes screenplay, characters, and execution log

---

## Admin Features

Access advanced system management through the Admin menu:

```
LIZZY ADMIN - Template & Schema Management
════════════════════════════════════════════════════════════════════════════════
1. View Available Templates
2. Edit Template Schema  
3. Edit Template Prompts
4. Create Custom Template
5. Export Template
6. Import Template
7. View Template Usage
8. Back to Main Menu
```

### Template Management

**View Available Templates:**
- Lists all templates with metadata
- Shows usage statistics
- Displays template health status

**Edit Template Schema:**
- Modify table structures
- Add/remove fields
- Update relationships and constraints

**Edit Template Prompts:**
- Customize AI generation behavior
- Modify tone and style options
- Update bucket guidance instructions

**Create Custom Template:**
- Step-by-step template builder
- Field-by-field table definition
- Prompt customization interface

### System Maintenance

**Database Management:**
- Project database health checks
- Orphaned file cleanup
- Performance optimization

**Bucket Administration:**
- Bulk file operations
- Index rebuilding
- Storage management

**Usage Analytics:**
- Project creation statistics
- Template popularity metrics
- AI generation usage patterns

---

## Advanced Usage

### Batch Processing

Create multiple projects programmatically:

```python
from autonomous_agent import AutonomousAgent

# Create 5 projects with different templates
for i in range(5):
    agent = AutonomousAgent()
    agent.run_full_cycle()
```

### Custom AI Prompts

Modify AI behavior by editing template prompts:

```json
{
  "brainstorm": {
    "tones": {
      "custom-tone": "Your custom AI instruction here"
    }
  }
}
```

### API Integration

Integrate LIZZY with external tools:

```python
import subprocess

# Run LIZZY agent from external script
result = subprocess.run(['python3', 'autonomous_agent.py'], 
                       capture_output=True, text=True)

if result.returncode == 0:
    print("Project created successfully")
```

### Collaboration Workflows

**Project Sharing:**
1. Export complete project archive
2. Share `exports/project_name/` folder
3. Recipient imports template and data
4. Collaborative editing through version history

**Version Control Integration:**
- Commit project exports to git
- Track changes through version history
- Merge collaborative edits

---

## Troubleshooting

### Common Issues

**1. OpenAI API Key Problems**
```
Error: "OpenAI API key required to continue"

Solutions:
- Set environment variable: export OPENAI_API_KEY="your-key"
- Enter key when prompted in LIZZY interface
- Verify key has sufficient credits and permissions
```

**2. Template System Not Available**
```
Error: "Template system not available"

Solutions:
- Ensure template_manager.py is in project directory
- Check that templates/ folder exists
- Verify template JSON files are valid
```

**3. Database Connection Issues**
```
Error: "Database connection failed"

Solutions:
- Check project folder permissions
- Verify SQLite installation
- Ensure sufficient disk space
- Try creating new project to test
```

**4. LightRAG Import Errors**
```
Error: "LightRAG not available"

Solutions:
- Install: pip install lightrag-hku
- Verify Python version compatibility (3.8+)
- Check for conflicting packages
```

**5. Export Failures**
```
Error: "Export failed"

Solutions:  
- Check destination folder permissions
- Verify sufficient disk space
- Ensure project database is not corrupted
- Try exporting individual components
```

### Performance Optimization

**Large Projects:**
- Regularly export and archive old versions
- Clean up unused brainstorm sessions
- Optimize bucket file sizes

**AI Generation Speed:**
- Use smaller knowledge buckets for faster processing
- Limit brainstorm session scope
- Choose appropriate AI model settings

**Database Performance:**
- Regular database maintenance through Admin
- Monitor project file sizes
- Archive completed projects

### Getting Help

**Built-in Help:**
- Use "Getting Started" menu option
- Check template documentation in Admin
- Review version history for examples

**Community Support:**
- GitHub Issues: Report bugs and request features
- Documentation: Complete user manual (this document)
- Examples: Sample projects in `projects/` folder

### Backup and Recovery

**Regular Backups:**
```bash
# Backup entire LIZZY workspace
cp -r Elizabeth_PI Elizabeth_PI_backup_$(date +%Y%m%d)
```

**Project Recovery:**
- Projects stored in `projects/[name]/[name].sqlite`
- Export data regularly through Export Options
- Version history provides point-in-time recovery

**System Recovery:**
```bash
# Reset to clean state (preserves projects)
git clean -fd
git reset --hard HEAD

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Appendix

### File Structure
```
Elizabeth_PI/
├── lizzy.py                    # Main interface
├── autonomous_agent.py         # Autonomous agent system
├── template_manager.py         # Template system
├── export_screenplay.py        # Export utilities
├── brainstorm.py              # AI brainstorm workflow
├── write.py                   # AI write workflow
├── admin.py                   # Admin interface
├── templates/                 # Template definitions
│   ├── romcom.json
│   ├── textbook.json
│   └── custom/                # User templates
├── projects/                  # Project databases  
│   └── [project_name]/
│       └── [project_name].sqlite
├── exports/                   # Exported content
│   └── [project_name]/
│       ├── execution_log.json
│       ├── [project]_screenplay.txt
│       └── [project]_characters.txt
└── lightrag_working_dir/      # Knowledge base
    ├── books/
    ├── scripts/
    └── plays/
```

### Keyboard Shortcuts
- `Ctrl+C` - Cancel current operation
- `Enter` - Confirm selection
- `back` - Return to previous menu (when available)
- `exit` - Quick exit from most menus

### Default Settings
- AI Model: GPT-4o Mini (cost-optimized)
- Export Format: UTF-8 text files
- Project Isolation: Complete (separate databases)
- Version History: Unlimited retention
- Auto-save: All operations auto-saved

---

**LIZZY Framework** - *Professional screenwriting with intelligent assistance*

*Transform your story ideas into compelling screenplays with AI that understands your unique creative vision.*

Last Updated: July 31, 2025 | Version: 2.0 with Autonomous Agent