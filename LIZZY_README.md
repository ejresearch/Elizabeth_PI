#  LIZZY FRAMEWORK
## AI-Assisted Long-Form Writing System

A modular command-line framework for AI-assisted creative writing, featuring structured memory, dynamic document retrieval, and iterative refinement.

##  Quick Start

1. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY=your_key_here
   ```

2. **Install dependencies:**
   ```bash
   pip install openai lightrag
   ```

3. **Create a new project:**
   ```bash
   python start.py
   ```

4. **Follow the workflow:**
   ```bash
   python intake.py project_name    # Define characters & scenes
   python brainstorm.py project_name # Generate creative ideas  
   python write.py project_name     # Create polished drafts
   ```

##  Module Overview

###  Start Module (`start.py`)
- **Purpose:** Initialize new writing projects
- **Features:** Creates isolated SQLite databases with structured tables
- **Usage:** `python start.py`

###  Intake Module (`intake.py`) 
- **Purpose:** Capture story elements and foundational metadata
- **Features:** Interactive forms for characters, scenes, and story outline
- **Usage:** `python intake.py <project_name>`

###  Brainstorm Module (`brainstorm.py`)
- **Purpose:** Generate creative ideas using AI and source material
- **Features:** 
  - 5 tone presets (Cheesy Romcom, Romantic Dramedy, Shakespearean Comedy, etc.)
  - LightRAG integration for contextual content retrieval
  - Dynamic querying of thematic buckets (books, plays, scripts)
- **Usage:** `python brainstorm.py <project_name>`

###  Write Module (`write.py`)
- **Purpose:** Synthesize brainstorming into polished drafts
- **Features:**
  - Single scene or full script generation
  - Proper screenplay formatting
  - Export to text files
  - Versioned draft storage
- **Usage:** `python write.py <project_name>`

###  Content Buckets (`setup_buckets.py`)
- **Purpose:** Manage LightRAG thematic content buckets
- **Features:**
  - Organize source material (books, plays, scripts)
  - Ingest content for retrieval during brainstorming
  - Bucket management and content listing
- **Usage:** `python setup_buckets.py`

##  Project Structure

```
projects/
├── project_name/
│   └── project_name.sqlite          # Isolated project database
│
lightrag_working_dir/
├── books/                           # Screenwriting guides, craft books
├── plays/                           # Theatrical works, dialogue examples
└── scripts/                         # Professional screenplays, samples
```

## 💾 Database Schema

Each project has dedicated tables:
- **characters:** Character profiles with traits and challenges
- **story_outline:** Act/scene structure with key events  
- **brainstorming_log:** AI-generated creative ideas with context
- **finalized_draft_v1:** Polished scene drafts
- **project_metadata:** Project settings and versioning

##  Tone Presets

1. **Cheesy Romcom** - Light-hearted with obvious romantic tropes
2. **Romantic Dramedy** - Balance of romance and realistic drama
3. **Shakespearean Comedy** - Witty wordplay and elaborate schemes
4. **Modern Indie** - Quirky, authentic, unconventional storytelling
5. **Classic Hollywood** - Sophisticated dialogue, timeless romance

##  Advanced Features

### LightRAG Integration
- **Graph-based retrieval:** Semantic content discovery
- **Contextual querying:** Finds relevant material based on scene context
- **Multi-bucket support:** Different content types for varied inspiration

### Iterative Refinement
- **Versioned drafts:** Track changes and improvements
- **Context preservation:** Maintains character and story continuity
- **Feedback loops:** Each module builds on previous outputs

### Modular Architecture
- **Independent modules:** Run any stage separately
- **Data encapsulation:** Isolated project databases
- **Workflow flexibility:** Adapt to different creative processes

##  Example Workflow

```bash
# 1. Initialize project
python start.py
# > Enter: "romantic_comedy_pilot"

# 2. Define story elements  
python intake.py romantic_comedy_pilot
# > Add characters: Emma (workaholic), Jake (free spirit)
# > Add scenes: Act 1 Scene 1 - Coffee shop meet-cute

# 3. Generate creative ideas
python brainstorm.py romantic_comedy_pilot  
# > Select: Romantic Dramedy tone
# > Query: scripts bucket for inspiration
# > Result: Detailed brainstorming output with dialogue ideas

# 4. Write the scene
python write.py romantic_comedy_pilot
# > Generate: Act 1, Scene 1
# > Result: Properly formatted screenplay scene
# > Export: romantic_comedy_pilot_script_20250729.txt
```

##  Key Benefits

- **Enhanced Coherence:** Structured memory maintains narrative consistency
- **Authentic Content:** Dynamic retrieval creates contextually rich outputs  
- **User Control:** Interactive workflow with iterative refinement
- **Professional Quality:** Proper formatting and industry standards
- **Scalable:** Adapts to projects of any length or complexity

## 🔮 Future Enhancements

- Multi-genre support beyond screenwriting
- Real-time collaboration features
- Advanced quality assurance checks
- Custom prompt templates
- Integration with professional writing tools

---

**Built for writers, by writers. Powered by AI, guided by creativity.**