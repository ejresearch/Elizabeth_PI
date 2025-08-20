# Lizzy Framework User Manual

## Table of Contents
1. [Getting Started](#getting-started)
2. [Project Management](#project-management)
3. [Table Editor](#table-editor)
4. [Workflow Steps](#workflow-steps)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Features](#advanced-features)

---

## Getting Started

### System Requirements
- Python 3.8 or higher
- OpenAI API key
- Modern web browser (Chrome, Firefox, Safari, Edge)
- 4GB RAM minimum
- Internet connection for AI features

### Installation & First Run

1. **Clone or download the Lizzy Framework**
   ```bash
   git clone [repository-url]
   cd Elizabeth_PI
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your OpenAI API key**
   
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY="sk-your-api-key-here"
   ```

4. **Run Lizzy**
   ```bash
   python lizzy.py
   ```

### First-Time Setup Flow

When you first run Lizzy:

1. **API Key Verification**
   - Automatically loads from `.env` file
   - Tests connection with OpenAI
   - Shows "✅ Existing API key is working!" when successful

2. **Main Menu Display**
   ```
   LIZZY - Romantic Comedy Screenplay Generator
   ════════════════════════════════════════════════════════════════════════════════
   Get started in 30 seconds with a complete romcom template:
   📝 6 character archetypes + 30-scene outline + writing guides

      1. 🆕 Create New Romcom Project
      2. 📂 Open Existing Project
      3. ❓ Help & Getting Started
      4. 🚪 Exit
   ```

---

## Project Management

### Creating a New Project

1. **From Main Menu**: Select option `1` - Create New Romcom Project
2. **Name Your Project**: Enter a descriptive name (special characters auto-sanitized)
3. **Automatic Setup**: The system creates:
   - Project directory: `projects/[your_project_name]/`
   - SQLite database with all required tables
   - Pre-populated romcom template including:
     - 6 character archetypes ready to customize
     - 30-scene three-act structure
     - Professional writing guidance notes

### Loading an Existing Project

1. **From Main Menu**: Select option `2` - Open Existing Project
2. **Project List**: View numbered list with creation dates:
   ```
   Available Projects:
    1. romantic_comedy_2024 (created: 2024-01-15)
    2. love_story_draft (created: 2024-01-10)
    3. wedding_chaos (created: 2024-01-05)
   ```
3. **Select Project**: Enter the number to load
4. **Auto-Navigation**: Proceeds to Project Workflow Menu

### Project Status Display

Once loaded, the status bar shows:
```
API Key: ✓ Connected │ Current Project: romantic_comedy_2024
────────────────────────────────────────────────────────────────────────────────
```

---

## Table Editor

### Launching the Editor

From the Project Workflow Menu, select option `1` - 🎨 Edit Tables

The system will:
1. Start a local web server on port 8080
2. Open your default browser automatically
3. Display the full-featured project editor

### Web Editor Features

#### Main Interface
- **Navigation Bar**: Switch between Characters, Scenes, and Notes
- **Data Grid**: Interactive table with sorting and filtering
- **Action Buttons**: Add, Edit, Delete, Import/Export

#### Character Management
Edit character profiles with these fields:
- **Name**: Character's full name
- **Gender**: Character gender
- **Age**: Age or age range
- **Romantic Challenge**: Main obstacle to love
- **Lovable Trait**: Endearing quality
- **Comedic Flaw**: Source of humor
- **Notes**: Additional details

#### Scene Outline
Manage your 30-scene structure:
- **Act**: Act number (1, 2, or 3)
- **Scene**: Scene number within the act
- **Key Characters**: Characters involved
- **Key Events**: What happens in the scene

#### Notes Section
Store writing guidance and references:
- **Title**: Note heading
- **Content**: Full text content
- **Category**: Organization tag

### Editor Operations

#### Adding Data
1. Click "Add New" button
2. Fill in the form fields
3. Click "Save" to commit

#### Editing Data
1. Click the edit icon (✏️) on any row
2. Modify fields in the popup form
3. Click "Update" to save changes

#### Deleting Data
1. Click the delete icon (🗑️) on any row
2. Confirm deletion in the popup
3. Data is permanently removed

#### Bulk Import (CSV)
1. Click "Import CSV" button
2. Select your CSV file
3. Map columns to database fields
4. Review and confirm import

#### Export Options
- **Export All**: Complete database backup
- **Export Table**: Current table as CSV
- **Export Selection**: Selected rows only

### Auto-Save Feature
- All changes save immediately to the database
- No manual save required
- Timestamp tracking for all modifications

### Closing the Editor
1. Make all desired changes
2. Close the browser tab
3. Press Enter in the terminal to return to menu
4. Server stops automatically

---

## Workflow Steps

After loading a project, follow the 5-step creative process:

### Step 1: Edit Tables (🎨)
- Define your characters
- Structure your scenes
- Add writing notes
- Import reference materials

### Step 2: Knowledge Explorer (🕸️)
**Bucket Manager** - Launches at `http://localhost:8002`
- Upload reference scripts
- Add writing guides
- Build knowledge graphs
- Organize by category

Features:
- Drag & drop file upload
- Real-time processing stats
- LightRAG integration
- Search and filter capabilities

### Step 3: Brainstorm (💭)
**Creative Studio** - Interactive AI brainstorming
- Dynamic prompt editor
- AI chat interface
- Context from your tables
- Session history tracking

Process:
1. Select scenes to brainstorm
2. Choose knowledge buckets for context
3. Set tone and style preferences
4. Generate AI suggestions
5. Save promising ideas

### Step 4: Write (✍️)
**AI-Assisted Writing**
- Scene-by-scene generation
- Character voice consistency
- Professional formatting
- Multiple draft versions

### Step 5: Export (📤)
**Export Options**:
1. **Complete Package**: Everything including database, sessions, exports
2. **Screenplay Only**: Formatted screenplay document
3. **Data & Analysis**: Characters, outline, and notes
4. **All Sessions**: Brainstorming history and generated content

Export formats:
- JSON (structured data)
- TXT (readable text)
- ZIP (packaged archive)

---

## Troubleshooting

### Common Issues & Solutions

#### API Key Not Loading
**Problem**: "No API key found" error
**Solution**:
1. Check `.env` file exists in project root
2. Verify format: `OPENAI_API_KEY="sk-..."`
3. Restart Lizzy after adding key

#### Table Editor Won't Open
**Problem**: Browser doesn't launch
**Solution**:
1. Check port 8080 is free: `lsof -i :8080`
2. Kill blocking process: `kill -9 [PID]`
3. Manually open: `http://localhost:8080`

#### Project Won't Load
**Problem**: "Failed to load project" error
**Solution**:
1. Verify `.sqlite` file exists in project folder
2. Check file permissions
3. Try creating a new project and importing data

#### Database Errors
**Problem**: Missing tables or data corruption
**Solution**:
1. Export any recoverable data
2. Create new project
3. Import exported data
4. Lizzy auto-creates missing tables on load

#### Server Won't Stop
**Problem**: Terminal stuck after closing browser
**Solution**:
1. Press Enter in terminal
2. Use Ctrl+C if needed
3. Force kill: `lsof -ti:8080 | xargs kill -9`

---

## Advanced Features

### Direct Database Access
Query or modify the SQLite database directly:
```bash
sqlite3 projects/your_project/your_project.sqlite

# Example queries
.tables
SELECT * FROM characters;
SELECT act, scene, key_events FROM story_outline WHERE act = 1;
```

### Project Structure
```
projects/
├── your_project_name/
│   ├── your_project_name.sqlite    # Main database
│   ├── exports/                    # Export packages
│   │   └── export_20240115_143022.zip
│   ├── sessions/                   # Brainstorm sessions
│   │   └── session_abc123.json
│   └── buckets/                    # Knowledge bases
│       ├── scripts/
│       └── guides/
```

### Database Schema

#### characters table
```sql
id INTEGER PRIMARY KEY
name TEXT NOT NULL
gender TEXT
age TEXT
romantic_challenge TEXT
lovable_trait TEXT
comedic_flaw TEXT
notes TEXT
created_at TIMESTAMP
```

#### story_outline table
```sql
id INTEGER PRIMARY KEY
act INTEGER NOT NULL
scene INTEGER NOT NULL
key_characters TEXT
key_events TEXT
created_at TIMESTAMP
```

#### brainstorming_log table
```sql
id INTEGER PRIMARY KEY
session_id TEXT NOT NULL
timestamp TEXT NOT NULL
tone_preset TEXT
scenes_selected TEXT
bucket_selection TEXT
lightrag_context TEXT
ai_suggestions TEXT
created_at TIMESTAMP
```

### Backup & Recovery

#### Manual Backup
```bash
# Backup entire project
cp -r projects/your_project ~/backups/

# Backup database only
cp projects/your_project/*.sqlite ~/backups/
```

#### Restore from Backup
```bash
# Restore entire project
cp -r ~/backups/your_project projects/

# Restore database only
cp ~/backups/*.sqlite projects/your_project/
```

### Keyboard Shortcuts

#### In Terminal
- `Ctrl+C`: Force quit
- `Enter`: Confirm/Continue
- Number keys: Menu selection

#### In Web Editor
- `Ctrl+S`: Not needed (auto-save)
- `Esc`: Close popup forms
- `Tab`: Navigate fields

### Performance Tips

1. **Large Projects**
   - Export completed acts to reduce database size
   - Archive old brainstorming sessions
   - Limit knowledge buckets to relevant materials

2. **Faster Loading**
   - Keep project names short
   - Regular database cleanup
   - Close unused browser tabs

3. **API Usage**
   - Monitor token usage in brainstorming
   - Use focused prompts
   - Cache frequently used responses

---

## Best Practices

### Project Organization
1. **Naming Convention**: Use descriptive names without spaces
   - ✅ `romantic_comedy_2024`
   - ✅ `wedding_story_draft3`
   - ❌ `My Project!!!`
   - ❌ `test (copy) (2)`

2. **Regular Exports**: Export after each major milestone
   - After character creation
   - After outline completion
   - After each act is written

3. **Version Control**: Keep previous exports for rollback

### Writing Workflow
1. **Start with Characters**: Fully develop before outlining
2. **Complete Outline**: All 30 scenes before writing
3. **Brainstorm in Batches**: 5-10 scenes at a time
4. **Write Sequentially**: Follow story order
5. **Export Frequently**: Save progress regularly

### Collaboration
- Export project as ZIP for sharing
- Import colleague's CSV data
- Merge brainstorming sessions
- Track changes via exports

---

## Quick Reference

### File Locations
- **Main Script**: `lizzy.py`
- **Projects**: `projects/`
- **API Config**: `api_config.json`
- **Environment**: `.env`
- **Exports**: `projects/[name]/exports/`

### Port Usage
- **Table Editor**: 8080
- **Bucket Manager**: 8002
- **Brainstorm Studio**: 8002 (shared)

### Required Files
- `lizzy.py` - Main application
- `web_editor_server.py` - Table editor backend
- `web_brainstorm_server.py` - Brainstorm backend
- `bucket_manager_server.py` - Bucket manager backend
- `util_apikey.py` - API key management
- `load_env.py` - Environment loader

### Support Resources
- **Issues**: Report at GitHub repository
- **Documentation**: This user manual
- **Templates**: Pre-configured in new projects
- **Examples**: Sample projects in `examples/`

---

## Summary

The Lizzy Framework provides a complete romantic comedy screenplay writing system with:

✅ **One-click project creation** with professional templates
✅ **Web-based table editor** for characters and scenes  
✅ **AI-powered brainstorming** with knowledge graph context
✅ **Structured 5-step workflow** from concept to screenplay
✅ **Multiple export formats** for sharing and backup
✅ **Auto-save everything** with no data loss
✅ **Clean CLI interface** with visual web tools

Follow the workflow: **Edit → Explore → Brainstorm → Write → Export** for best results.

Happy writing! 🎬