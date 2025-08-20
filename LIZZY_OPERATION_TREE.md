# 🌟 LIZZY.PY - Complete Operation Tree & Routing Guide

## 📊 **How Lizzy Works - System Architecture**

```
🚀 LIZZY.PY (Main Entry Point)
│
├── 🔧 INITIALIZATION
│   ├── Import Core Modules
│   │   ├── core_templates.py (Template System)
│   │   ├── core_brainstorm.py (AI Brainstorming)
│   │   ├── core_write.py (Writing Engine)
│   │   ├── core_export.py (Export System)
│   │   ├── core_knowledge.py (LightRAG Manager)
│   │   ├── core_editor.py (GUI Editor)
│   │   └── core_outline.py (Outline Manager)
│   │
│   ├── Session Management
│   │   ├── API Key Setup (util_apikey.py)
│   │   ├── Project Database (SQLite)
│   │   └── User Preferences
│   │
│   └── Environment Setup
│       ├── Load .env file
│       ├── Initialize directories
│       └── Check dependencies
│
├── 🎯 MAIN MENU SYSTEM
│   │
│   ├── 1. 🆕 Create New Romcom Project
│   │   ├── → create_project()
│   │   ├── → Initialize SQLite database
│   │   ├── → Set up project structure
│   │   └── → project_menu()
│   │
│   ├── 2. 📂 Open Existing Project  
│   │   ├── → select_project()
│   │   ├── → Load project database
│   │   └── → project_menu()
│   │
│   ├── 3. ❓ Help & Getting Started
│   │   └── → Show documentation
│   │
│   ├── 4. 🔧 Settings & Configuration
│   │   ├── → API Key Management
│   │   ├── → Template Configuration
│   │   └── → System Preferences
│   │
│   └── 5. 🔬 Advanced Tools & Analytics
│       ├── → bucket_manager_menu()
│       ├── → Analytics Dashboard
│       └── → System Administration
│
├── 📝 PROJECT MENU (When project is loaded)
│   │
│   ├── 1. 🎭 Character Development
│   │   ├── → Launch character editor GUI
│   │   ├── → Use romcom templates
│   │   └── → Store in characters table
│   │
│   ├── 2. 🧠 Story Brainstorming  
│   │   ├── → core_brainstorm.TransparentBrainstormer
│   │   ├── → AI-assisted ideation
│   │   ├── → Scene generation
│   │   └── → Store in brainstorming_log
│   │
│   ├── 3. 📋 Scene Outline
│   │   ├── → core_outline.RomcomOutlineGUI
│   │   ├── → 30-scene structure
│   │   ├── → Template-based outline
│   │   └── → Store in scenes table
│   │
│   ├── 4. ✍️ Write Screenplay
│   │   ├── → core_write.TransparentWriter
│   │   ├── → Scene-by-scene writing
│   │   ├── → AI assistance
│   │   └── → Store in screenplay_content
│   │
│   ├── 5. 📚 Knowledge Base
│   │   ├── → bucket_manager_menu()
│   │   ├── → LightRAG integration
│   │   ├── → Reference management
│   │   └── → Research tools
│   │
│   ├── 6. 📊 Export & Share
│   │   ├── → core_export.LizzyExporter
│   │   ├── → PDF generation
│   │   ├── → HTML export
│   │   └── → Final Draft format
│   │
│   └── 7. 🔧 Project Settings
│       ├── → Edit database tables
│       ├── → Project metadata
│       └── → Backup/restore
│
└── 🧠 KNOWLEDGE BASE SYSTEM
    │
    ├── bucket_manager_menu()
    │   ├── → LightRAG bucket management
    │   ├── → Document processing
    │   ├── → Query interface
    │   └── → Analytics dashboard
    │
    ├── Web Interfaces (Separate Servers)
    │   ├── bucket_alt/web_lightrag_server.py (Port 8001)
    │   │   ├── Enhanced Analytics Dashboard
    │   │   ├── Real-time Performance Monitoring  
    │   │   ├── Bucket Comparison Tools
    │   │   └── Professional UX Interface
    │   │
    │   ├── bucket_manager_server.py (Port 8002)
    │   │   ├── Basic Bucket Manager
    │   │   ├── File Upload Interface
    │   │   └── Simple Management Tools
    │   │
    │   ├── web_brainstorm_server.py (Port 8003)
    │   │   ├── AI Brainstorming Interface
    │   │   └── Creative Writing Tools
    │   │
    │   └── web_editor_server.py (Port 8004)
    │       ├── Character Editor GUI
    │       └── Interactive Forms
    │
    └── CLI Tools
        ├── analytics_report_generator.py
        ├── util_admin.py
        └── util_agent.py
```

---

## 🎯 **How to Use Lizzy - Quick Start Guide**

### **Method 1: CLI Interface (Recommended for Writing)**
```bash
python lizzy.py
```

**Navigation Flow:**
1. **First Time:** Set up OpenAI API key
2. **Create Project:** Choose "Create New Romcom Project"
3. **Follow Workflow:** Character → Brainstorm → Outline → Write → Export
4. **Access Tools:** Use menu options for specific features

### **Method 2: Web Analytics Dashboard**
```bash
python bucket_alt/web_lightrag_server.py
# Then open: http://localhost:8001
```

**Features:**
- 📊 **Analytics Tab** - Real-time metrics and performance
- 📈 **System Monitoring** - CPU, memory, disk usage
- 🔍 **Bucket Comparison** - Side-by-side analysis
- 📄 **Export Tools** - Multiple report formats

### **Method 3: Basic Bucket Manager**
```bash
python bucket_manager_server.py  
# Then open: http://localhost:8002
```

**Features:**
- 📁 Simple bucket management
- 📤 File upload interface
- 🔧 Basic processing tools

---

## 🗂️ **Project Structure & Data Flow**

### **Project Database (SQLite)**
Each project creates its own `.sqlite` file containing:

```
📊 PROJECT DATABASE
├── characters (Character profiles & archetypes)
├── scenes (30-scene outline structure)  
├── screenplay_content (Written scenes & drafts)
├── brainstorming_log (AI brainstorming sessions)
├── finalized_draft_v1 (Completed drafts)
└── project_metadata (Settings & info)
```

### **LightRAG Knowledge Base**
Separate knowledge management system:

```
🧠 LIGHTRAG SYSTEM
├── lightrag_working_dir/
│   ├── bucket1/ (Knowledge graphs)
│   ├── bucket2/ (Reference materials)
│   └── _statistics/ (Performance data)
├── _reports/ (Analytics exports)
└── bucket_config.json (System config)
```

---

## 🚀 **Recommended Workflow**

### **For Screenplay Writing:**
1. **Start:** `python lizzy.py`
2. **Create:** New romcom project
3. **Develop:** Characters using templates
4. **Brainstorm:** Story ideas with AI
5. **Outline:** 30-scene structure
6. **Write:** Scene-by-scene with AI assistance
7. **Export:** Professional screenplay format

### **For Analytics & Monitoring:**
1. **Start:** `python bucket_alt/web_lightrag_server.py`
2. **Open:** http://localhost:8001
3. **Click:** 📊 Analytics tab
4. **Monitor:** System performance and usage
5. **Export:** Reports as needed

### **For Knowledge Management:**
1. **Access:** Through lizzy.py → Knowledge Base menu
2. **Or Web:** http://localhost:8001 or http://localhost:8002
3. **Upload:** Documents and references
4. **Query:** Using LightRAG AI search
5. **Analyze:** Using analytics dashboard

---

## 💡 **Key Differences Between Interfaces**

| Interface | Port | Purpose | Best For |
|-----------|------|---------|----------|
| **lizzy.py** | CLI | Complete writing workflow | Screenplay creation |
| **web_lightrag_server.py** | 8001 | Enhanced analytics | Performance monitoring |
| **bucket_manager_server.py** | 8002 | Basic management | Simple file uploads |
| **web_brainstorm_server.py** | 8003 | AI brainstorming | Creative ideation |
| **web_editor_server.py** | 8004 | Character editor | Character development |

---

## 🔧 **Configuration & Setup**

### **Environment Variables (.env)**
```
OPENAI_API_KEY=sk-...
PROJECT_DIR=/path/to/projects
LIGHTRAG_DIR=/path/to/knowledge
```

### **First-Time Setup**
1. Install dependencies: `pip install -r requirements.txt`
2. Set OpenAI API key: Use lizzy.py setup or .env file
3. Run lizzy.py: Follow interactive setup
4. Create first project: Use guided workflow

### **Advanced Features**
- **Templates:** Romcom character archetypes & scene structures
- **AI Integration:** OpenAI GPT for writing assistance
- **Knowledge Graphs:** LightRAG for research management
- **Analytics:** Real-time performance monitoring
- **Export:** Multiple professional formats

---

**🎯 Start with `python lizzy.py` for the complete guided experience!**