# LIZZY Framework

## AI-Assisted Long-Form Writing System

LIZZY is a modular, AI-powered screenwriting framework that combines structured database management with advanced language models to assist writers in developing professional screenplays from concept to final draft.

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
║              🎬 AI-ASSISTED LONG-FORM WRITING SYSTEM 🎬                      ║
║                     ~ Modular • Iterative • Intelligent ~                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

</div>

## 🎯 Overview

LIZZY Framework is a comprehensive screenwriting assistant that guides writers through every stage of screenplay development:

- **Character Development**: Create deep, psychologically complex characters with full backstories
- **Story Structure**: Build scene-by-scene outlines with dramatic beats and emotional arcs
- **AI Brainstorming**: Generate creative ideas using contextual source material and multiple tone presets
- **Professional Formatting**: Output industry-standard screenplay format
- **Knowledge Integration**: Leverage curated writing resources through semantic search

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- 2GB free disk space

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ejresearch/Elizabeth_PI.git
cd Elizabeth_PI
```

2. Install dependencies:
```bash
pip install openai lightrag-hku tiktoken numpy
```

3. Launch LIZZY:
```bash
python lizzy.py
```

4. Enter your OpenAI API key when prompted

## 🏗️ Architecture

### Core Components

- **SQLite Database**: Project isolation with 5 core tables
- **LightRAG Integration**: Knowledge graphs for semantic content retrieval
- **OpenAI GPT-4o Mini**: Creative text generation
- **CLI Interface**: Retro-styled command line with intuitive navigation
- **GUI Extension**: Drag-and-drop file management for source materials

### Database Schema

```sql
project_metadata    -- Core project settings
characters          -- Character profiles with psychological depth
story_outline       -- Scene-by-scene structure
brainstorming_log   -- AI-powered creative sessions
finalized_draft_v1  -- Professional screenplay content
```

## 📚 Features

### 1. Four Core Modules

- **START**: Project initialization and configuration
- **INTAKE**: Character and story development
- **BRAINSTORM**: AI-assisted creative exploration
- **WRITE**: Scene generation and formatting

### 2. Knowledge Management

- **Demo Books**: Writing theory and craft resources
- **Demo Scripts**: Professional screenplay analysis
- **Demo Plays**: Theatrical dialogue techniques

### 3. Advanced Tools

- **Tables Manager**: Direct SQL database access
- **Buckets Manager**: LightRAG content organization
- **Export System**: JSON, SQL, CSV, TXT, Markdown formats
- **GUI File Manager**: Visual drag-and-drop interface

## 🎨 Usage Example

### Creating Your First Project

1. **Launch LIZZY**:
```bash
python lizzy.py
```

2. **Create New Project**:
   - Select "Create New Project" from main menu
   - Enter project name, genre, and logline
   - Define theme and target length

3. **Develop Characters**:
   - Navigate to "Character & Story Intake"
   - Create 3-5 main characters
   - Add personality traits, backstory, goals, and conflicts

4. **Outline Your Story**:
   - Build scene-by-scene structure
   - Define locations, time of day, and key events
   - Track emotional beats and character arcs

5. **Brainstorm with AI**:
   - Select scenes to develop
   - Choose tone presets (Modern Indie, Romantic Dramedy, etc.)
   - Review AI suggestions enhanced by source material

6. **Write Your Screenplay**:
   - Generate professional formatted scenes
   - Edit and refine content
   - Export complete screenplay

## 🛠️ Configuration

### API Key Setup

LIZZY stores your OpenAI API key securely in:
- macOS/Linux: `~/.lizzy/config.json`
- Windows: `%USERPROFILE%\.lizzy\config.json`

### Custom Knowledge Bases

Add your own reference materials:

1. Launch Buckets Manager from main menu
2. Select "GUI File Manager"
3. Drag `.txt`, `.md`, or `.pdf` files into buckets
4. System automatically indexes for AI retrieval

## 📊 Sample Project

LIZZY includes "The Last Coffee Shop" - a complete demonstration project featuring:

- 3 fully developed characters
- 3-scene short film structure
- Professional screenplay (1,399 words)
- Complete brainstorming sessions
- Export examples in all formats

## 🤖 AI Integration

### LightRAG Knowledge Graphs

- **31,593 entities** across knowledge bases
- **23,506 relationships** for semantic connections
- **~200ms query response** time
- **Contextual retrieval** for brainstorming

### GPT-4o Mini Features

- Creative text generation
- Multiple tone presets
- Character voice consistency
- Thematic integration

## 📤 Export Capabilities

- **JSON**: Complete structured data with metadata
- **SQL**: Full database dump with schema
- **CSV**: Tabular data for analysis
- **TXT**: Human-readable formatted content
- **Markdown**: Documentation with formatting

## 🔧 Troubleshooting

### Common Issues

1. **LightRAG Import Error**:
```bash
pip uninstall lightrag -y
pip install lightrag-hku
```

2. **API Key Not Saving**:
- Check permissions on `~/.lizzy/` directory
- Manually create `config.json` if needed

3. **Database Errors**:
- Run `python init_db.py` to reinitialize tables
- Check `projects/` directory permissions

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4o Mini API
- HKU NLP Lab for LightRAG
- The screenwriting community for inspiration

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ejresearch/Elizabeth_PI/issues)
- **Documentation**: Built-in help system (`Help & Documentation` in main menu)

---

<div align="center">

**LIZZY Framework v1.0** - *Write better stories, faster*

</div>