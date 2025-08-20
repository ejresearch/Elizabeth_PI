# Loading Projects in Lizzy Framework

## Overview
The Lizzy Framework provides a streamlined workflow for loading and managing screenplay projects. This guide covers how to create, load, and work with projects efficiently.

## Quick Start

### Running Lizzy
```bash
python lizzy.py
```

### First-Time Setup
When you first run Lizzy, it will:
1. Display the Lizzy ASCII art header
2. Check for your OpenAI API key
3. Test the API key connection
4. Present the main menu

## Main Menu Options

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

## Creating a New Project

### Option 1: From Main Menu
1. Select option `1` - Create New Romcom Project
2. Enter a project name (special characters will be sanitized)
3. The system will:
   - Create a project directory in `projects/[project_name]/`
   - Initialize a SQLite database with all required tables
   - Load the romcom template with:
     - 6 pre-configured character archetypes
     - 30-scene story outline
     - Writing guidance notes
   - Automatically load the project for immediate use

### What Gets Created
```
projects/
└── your_project_name/
    └── your_project_name.sqlite
```

The database includes these tables:
- `characters` - Character profiles with romantic challenges, traits, and flaws
- `story_outline` - Act/scene structure with key events
- `brainstorming_log` - AI-generated ideas and suggestions
- `finalized_draft_v1` - Completed screenplay content
- `project_metadata` - Project settings and timestamps

## Loading an Existing Project

### Option 2: From Main Menu
1. Select option `2` - Open Existing Project
2. You'll see a numbered list of available projects with creation dates:
   ```
   Available Projects:
    1. romantic_comedy_2024 (created: 2024-01-15)
    2. love_story_draft (created: 2024-01-10)
    3. wedding_chaos (created: 2024-01-05)
   ```
3. Enter the number of the project you want to load
4. The project loads and takes you to the Project Workflow Menu

### Project Status Indicator
Once loaded, you'll see the project status at the top of menus:
```
API Key: ✓ Connected │ Current Project: romantic_comedy_2024
────────────────────────────────────────────────────────────────────────────────
```

## Project Workflow Menu

After loading a project, you enter the 5-step workflow:

```
LIZZY WORKFLOW
════════════════════════════════════════════════════════════════════════════════
📝 Complete your romantic comedy in 5 simple steps:

   1. 🎨 Edit Tables (Characters, Scenes, Notes)
   2. 🕸️  Knowledge Explorer (Interactive LightRAG Graphs)
   3. 💭 Brainstorm (Generate ideas for scenes)
   4. ✍️  Write (Create screenplay scenes)
   5. 📤 Export (Final screenplay output)

   0. 🏠 Back to Main Menu
```

## Working with Projects

### Edit Tables (Option 1)
- Launches a web-based editor at `http://localhost:8080`
- Full CRUD operations on all project tables
- Visual interface for managing characters, scenes, and notes
- Auto-saves all changes to the project database

### Knowledge Explorer (Option 2)
- Opens the Bucket Manager at `http://localhost:8002`
- Upload reference materials (scripts, books, guides)
- Build a knowledge graph for AI context
- Organize materials by category

### Brainstorm (Option 3)
- Interactive AI brainstorming interface
- Uses your character profiles and scene outline
- Generates creative suggestions based on your knowledge buckets
- Saves all brainstorming sessions to the database

### Write (Option 4)
- AI-assisted screenplay writing
- Pulls context from characters, outline, and brainstorming
- Professional screenplay formatting
- Version tracking for drafts

### Export (Option 5)
- Multiple export formats available:
  - Complete package (everything)
  - Screenplay only
  - Data & analysis
  - All sessions
- Creates timestamped export packages

## Project File Structure

```
projects/
├── romantic_comedy_2024/
│   ├── romantic_comedy_2024.sqlite    # Main project database
│   ├── exports/                       # Export packages
│   └── sessions/                      # Brainstorming sessions
├── love_story_draft/
│   └── love_story_draft.sqlite
└── wedding_chaos/
    └── wedding_chaos.sqlite
```

## API Key Management

### Initial Setup
The API key loads once at startup:
1. Checks environment variable `OPENAI_API_KEY`
2. Checks `.env` file in project directory
3. Tests the key with OpenAI API
4. Displays connection status

### Key Storage Locations
- Environment variable: `OPENAI_API_KEY`
- `.env` file in project root
- `api_config.json` for persistent storage

## Tips for Efficient Project Management

### Best Practices
1. **Naming Projects**: Use descriptive names without spaces
   - Good: `romantic_comedy_2024`, `wedding_story_v2`
   - Avoid: `My Project!!!`, `Test (1)`

2. **Regular Exports**: Export your work regularly to prevent data loss

3. **Template Usage**: New projects automatically include the romcom template - customize it rather than starting from scratch

4. **Session Management**: Each work session is tracked - you can always return to where you left off

### Switching Between Projects
1. Return to main menu (option `0` from Project Workflow)
2. Select "Open Existing Project"
3. Choose your project
4. Continue where you left off

### Project Backups
To backup a project:
1. Navigate to `projects/[project_name]/`
2. Copy the entire folder to your backup location
3. The `.sqlite` file contains all project data

## Troubleshooting

### Project Won't Load
- Check that the `.sqlite` file exists in the project folder
- Ensure the project name hasn't been manually changed
- Verify file permissions

### API Key Issues
- The key loads once at startup
- If you see connection errors, restart Lizzy
- Check your `.env` file format: `OPENAI_API_KEY="sk-..."`

### Database Errors
- Lizzy automatically creates missing tables when loading projects
- If tables are corrupted, export your data and create a new project

## Advanced Features

### Direct Database Access
Advanced users can query the SQLite database directly:
```bash
sqlite3 projects/your_project/your_project.sqlite
```

### Custom Templates
While Lizzy uses the romcom template by default, the system supports custom templates through the `TemplateManager` class.

### Multi-Project Workflows
You can work on multiple projects by:
1. Opening one project
2. Exporting necessary data
3. Switching to another project
4. Importing reference materials

## Summary

The Lizzy project loading system provides:
- ✅ One-time API key loading at startup
- ✅ Automatic project creation with templates
- ✅ Easy project switching
- ✅ Persistent project state
- ✅ Web-based editing interfaces
- ✅ Comprehensive export options

Follow the 5-step workflow (Edit → Explore → Brainstorm → Write → Export) for best results in creating your romantic comedy screenplay.