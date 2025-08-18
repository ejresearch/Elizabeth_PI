# 🎬 Lizzy Framework - GUI Quick Start Guide

## ✅ All HTML GUIs Are Already Updated to Latest Versions

Your system is fully configured with the latest interfaces. Here's how to test and use each one:

## 🚀 How to Launch Each Interface

### 1. 🧠 Brainstorm Seamless Interface
**Latest Version**: `brainstorm_seamless.html` (35KB)
```bash
# Start the backend
python3 brainstorm_backend_refactored.py

# Access in browser
open http://localhost:5001
```

**Features:**
- AI chat with project data integration
- Template-based brainstorming
- Real-time conversation management
- Auto-save functionality
- Export to markdown

---

### 2. 🛠️ Prompt Studio Dynamic Interface  
**Latest Version**: `prompt_studio_dynamic.html` (60KB)
```bash
# Start the backend
python3 prompt_studio_dynamic.py

# Access in browser
open http://localhost:8002
```

**Features:**
- Prompt builder with live preview
- AI chat mode with custom prompts
- Data block integration (SQL + LightRAG)
- Template management
- Real project data compilation

---

### 3. 🌐 Web Project Editor Interface
**Latest Version**: `web_project_editor.html` (65KB)
```bash
# Start the backend
python3 web_server_refactored.py

# Access in browser
open http://localhost:8080
```

**Features:**
- Project management dashboard
- Database editing interface
- Character/scene management
- Data visualization
- Table editing capabilities

---

### 4. 📝 Intake Interactive GUI
**Latest Version**: `lizzy_intake_interactive.py` (tkinter-based)
```bash
# Launch for specific project
python3 -c "from lizzy_intake_interactive import launch_intake_gui; launch_intake_gui('projects/Alpha')"

# Or use the main Lizzy interface
python3 lizzy.py
# Then select intake option
```

**Features:**
- Modern tkinter desktop GUI
- Direct database editing
- Character/scene forms
- CSV import/export
- Real-time validation

---

## 🎮 Complete Demo Script

**Run the automated demo:**
```bash
python3 demo_all_guis.py
```

This script will:
1. ✅ Check all projects and HTML files
2. 🚀 Launch all servers automatically
3. 🌐 Open interfaces in your browser
4. ⚙️ Provide interactive menu

---

## 📊 Current System Status

### ✅ Verified Configurations:
- `brainstorm_backend_refactored.py` → `brainstorm_seamless.html`
- `prompt_studio_refactored.py` → `prompt_studio_dynamic.html`
- `web_server_refactored.py` → `web_project_editor.html`
- `lizzy_intake_interactive.py` → Modern tkinter GUI

### 📁 Test Projects Available:
- **Alpha** - 53,248 bytes
- **Beta** - 36,864 bytes  
- **gamma** - 61,440 bytes

---

## 🔧 Quick Individual Tests

### Test Brainstorm API:
```bash
curl http://localhost:5001/api/projects
```

### Test Prompt Studio API:
```bash
curl http://localhost:8002/api/projects
```

### Test Web Editor API:
```bash
curl http://localhost:8080/api/projects
```

---

## 🌟 Key Features of Latest GUIs

### Brainstorm Seamless:
- **Seamless chat interface** with AI integration
- **Template system** for structured brainstorming
- **Real-time data** from your projects
- **Conversation history** and export

### Prompt Studio Dynamic:
- **Dual mode**: Builder + Chat
- **Live preview** of compiled prompts
- **Data blocks** from SQL tables and LightRAG
- **OpenAI integration** for testing

### Web Project Editor:
- **Full project management** dashboard
- **Interactive table editing**
- **Character and scene management**
- **Modern responsive design**

### Intake Interactive:
- **Native desktop GUI** (tkinter)
- **Form-based data entry**
- **CSV import/export**
- **Real-time database updates**

---

## 🎯 Next Steps

1. **Choose your workflow:**
   - Creative brainstorming → Use Brainstorm Seamless
   - Prompt engineering → Use Prompt Studio Dynamic  
   - Data management → Use Web Project Editor
   - Quick data entry → Use Intake Interactive

2. **Run the demo:** `python3 demo_all_guis.py`

3. **Pick a project:** Alpha, Beta, or gamma

4. **Start creating!** All interfaces are ready to go.

---

**🎉 All GUIs are up-to-date and ready to use!**