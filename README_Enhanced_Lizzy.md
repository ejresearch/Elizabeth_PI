# Enhanced Lizzy Framework - Transparent AI Screenwriting System

## Overview

The Enhanced Lizzy Framework is a comprehensive, transparent AI-assisted screenwriting system that provides full visibility into every step of the creative process. Unlike traditional black-box AI systems, Lizzy shows you exactly what data is being used, how prompts are compiled, and why specific outputs are generated.

## Key Features

### 🔍 **Complete Transparency**
- Real-time visibility into every processing step
- Prompt compilation and inspection tools
- Data provenance tracking
- Step-by-step workflow monitoring

### 🧠 **LightRAG Knowledge Management**
- Visual knowledge graph exploration
- Dynamic bucket activation/deactivation
- Document ingestion with metadata
- Relationship mapping and analysis

### 📝 **Template-Driven Prompts**
- Configurable prompt templates
- Bucket-specific specializations
- Version control and comparison
- Real-time preview capabilities

### 🎬 **Scene-by-Scene Processing**
- Individual scene brainstorming and writing
- Continuity tracking between scenes
- Character development integration
- Progress monitoring and statistics

### 📊 **Comprehensive Export System**
- Multiple format support (Fountain, HTML, JSON, etc.)
- Complete session history and metadata
- Analysis reports and statistics
- Version comparison tools

## Architecture

```
┌─────────────────────┐
│  Main Orchestrator  │ ← Entry point and GUI
└─────────┬───────────┘
          │
    ┌─────┴─────────────────────────────────┐
    │                                       │
┌───▼────┐  ┌─────────────┐  ┌──────────────▼──┐
│Template│  │  LightRAG   │  │  Interactive     │
│Manager │  │  Manager    │  │  Intake          │
└───┬────┘  └─────┬───────┘  └──────────────┬──┘
    │             │                         │
    │       ┌─────▼─────────────────────────▼──┐
    │       │                                  │
┌───▼───────▼─┐                    ┌───────────▼──┐
│Transparent  │                    │Transparent   │
│Brainstormer │                    │Writer        │
└─────┬───────┘                    └───────┬──────┘
      │                                    │
      └────────────┬───────────────────────┘
                   │
            ┌──────▼─────┐
            │  Export    │
            │  System    │
            └────────────┘
```

## Module Breakdown

### 1. **lizzy_templates.py** - Template Management System
- **Purpose**: Manages all prompts and templates with full configurability
- **Key Features**:
  - Bucket-specific prompt templates
  - Real-time template compilation
  - Template comparison and versioning
  - Prompt inspection and debugging

### 2. **lizzy_lightrag_manager.py** - Knowledge Management Layer
- **Purpose**: Handles LightRAG knowledge graphs and bucket management
- **Key Features**:
  - Visual knowledge graph creation
  - Dynamic bucket activation
  - Document ingestion and metadata
  - Query interface and comparison

### 3. **lizzy_intake_interactive.py** - Interactive Data Intake
- **Purpose**: GUI-based data entry and management
- **Key Features**:
  - Table-based data editing
  - CSV import/export
  - Document upload interface
  - Data relationship visualization

### 4. **lizzy_transparent_brainstorm.py** - Transparent Brainstorming
- **Purpose**: Scene-by-scene brainstorming with full visibility
- **Key Features**:
  - Real-time step tracking
  - Context assembly monitoring
  - Bucket-specific insights
  - Session recording and replay

### 5. **lizzy_transparent_write.py** - Transparent Writing
- **Purpose**: Screenplay generation with complete process visibility
- **Key Features**:
  - Step-by-step scene generation
  - Continuity tracking
  - Word count and progress monitoring
  - Quality metrics and analysis

### 6. **lizzy_export_system.py** - Comprehensive Export System
- **Purpose**: Multi-format export with metadata and analysis
- **Key Features**:
  - Multiple export formats
  - Complete session archives
  - Statistical analysis
  - Version comparison reports

### 7. **lizzy_main_orchestrator.py** - Main Application Framework
- **Purpose**: Unified interface and workflow coordination
- **Key Features**:
  - Tabbed GUI interface
  - Workflow automation
  - Real-time monitoring
  - Session management

## Installation and Setup

### Prerequisites
```bash
pip install tkinter pandas matplotlib networkx sqlite3 asyncio lightrag openai
```

### Basic Setup
1. Ensure you have a valid OpenAI API key set in your environment
2. Create or open a Lizzy project directory
3. Run the main orchestrator

## Usage Examples

### Command Line Interface
```bash
# Launch GUI interface
python lizzy_main_orchestrator.py --gui

# Open specific project
python lizzy_main_orchestrator.py --project /path/to/project

# Run demonstration
python lizzy_main_orchestrator.py --demo
```

### Programmatic Usage
```python
from lizzy_main_orchestrator import LizzyOrchestrator

# Initialize with project
orchestrator = LizzyOrchestrator("path/to/project")

# Launch GUI
orchestrator.launch_gui()

# Or run workflows programmatically
await orchestrator.launch_brainstorm_workflow()
await orchestrator.launch_write_workflow()
```

### Individual Module Usage
```python
# Template management
from lizzy_templates import TemplateManager
tm = TemplateManager()
prompt = tm.compile_prompt("brainstorm", "scripts", context)

# LightRAG management
from lizzy_lightrag_manager import LightRAGManager
lm = LightRAGManager()
lm.create_bucket("new_bucket", "Description")

# Transparent brainstorming
from lizzy_transparent_brainstorm import TransparentBrainstormer
brainstormer = TransparentBrainstormer("project_path")
session_id = await brainstormer.brainstorm_all_scenes(["scripts", "books"])

# Transparent writing
from lizzy_transparent_write import TransparentWriter
writer = TransparentWriter("project_path")
session_id = await writer.write_all_scenes(["scripts", "books"], "user guidance")

# Export system
from lizzy_export_system import LizzyExporter
exporter = LizzyExporter("project_path")
zip_path = exporter.create_export_package("complete", ["json", "html", "txt"])
```

## Workflow Examples

### Complete Screenplay Workflow
1. **Setup Project**: Create or open project directory
2. **Data Intake**: Use interactive intake to add characters and scenes
3. **Bucket Management**: Upload documents to LightRAG buckets
4. **Template Configuration**: Customize prompts for your style
5. **Brainstorming**: Run transparent brainstorming across all scenes
6. **Writing**: Generate screenplay with full continuity tracking
7. **Export**: Create multi-format export packages

### Real-Time Monitoring Example
```python
# Set up real-time callbacks
def on_scene_started(data):
    print(f"Starting scene: Act {data['act']}, Scene {data['scene']}")

def on_prompt_compiled(data):
    print(f"Prompt compiled: {data['prompt_length']} characters")

# Register callbacks
writer.register_callback('scene_started', on_scene_started)
writer.register_callback('prompt_compiled', on_prompt_compiled)

# Run with monitoring
await writer.write_all_scenes(["scripts"], "Make it funny")
```

## Data Transparency Features

### Prompt Inspection
- **Template Loading**: See which templates are used
- **Context Assembly**: View all data being compiled
- **Variable Substitution**: Track how variables are filled
- **Final Prompt**: Preview exact prompt sent to AI

### Process Tracking
- **Step-by-Step Logging**: Every operation is recorded
- **Timing Analysis**: See how long each step takes
- **Success/Failure Tracking**: Monitor what works and what doesn't
- **Session Comparison**: Compare different approaches

### Data Provenance
- **Source Tracking**: Know which data influenced which output
- **Version History**: Track changes and iterations
- **Metadata Recording**: Comprehensive context preservation
- **Audit Trail**: Complete record of all operations

## Export Formats

### Screenplay Formats
- **Fountain**: Industry-standard plaintext format
- **HTML**: Web-viewable with styling
- **Text**: Simple text format
- **JSON**: Structured data format

### Analysis Formats
- **Statistics Reports**: Word counts, scene analysis
- **Session Comparisons**: Performance metrics
- **Data Quality Reports**: Completeness analysis
- **Relationship Maps**: Character and scene connections

## Customization

### Template Customization
```python
# Create custom template
tm.create_custom_template("brainstorm", "my_style", {
    "name": "My Custom Style",
    "system_prompt": "You are my custom brainstorming assistant...",
    "context_template": "Custom context: {scene_context}",
    "focus_areas": ["Custom area 1", "Custom area 2"]
})
```

### Bucket Configuration
```python
# Create specialized bucket
lm.create_bucket("character_arcs", "Character development resources")
lm.add_document_to_bucket("character_arcs", document_text, metadata)
```

### Workflow Customization
```python
# Custom workflow
async def my_custom_workflow():
    # Custom brainstorming
    brainstorm_session = await brainstormer.brainstorm_all_scenes(["custom_bucket"])
    
    # Custom writing with specific guidance
    write_session = await writer.write_all_scenes(
        ["scripts"], 
        "Focus on visual storytelling and minimal dialogue"
    )
    
    # Custom export
    exporter.create_export_package("analysis", ["json", "html"])
```

## Best Practices

### Template Design
- Keep templates focused and specific
- Use clear variable names
- Include helpful context in prompts
- Test templates with preview mode

### Bucket Management
- Organize documents by type and purpose
- Use descriptive bucket names
- Regular knowledge graph visualization
- Monitor bucket performance

### Workflow Optimization
- Start with smaller test runs
- Monitor real-time feedback
- Use session comparison for improvement
- Keep detailed session notes

### Quality Control
- Review generated content regularly
- Use statistics to identify patterns
- Compare different prompt approaches
- Maintain version history

## Troubleshooting

### Common Issues
- **API Key Errors**: Ensure OpenAI API key is properly set
- **Database Locks**: Close other connections to SQLite database
- **Memory Issues**: Process large projects in smaller batches
- **GUI Issues**: Check tkinter installation and display settings

### Performance Optimization
- Use specific buckets rather than all buckets
- Optimize template length
- Monitor API usage and costs
- Use background processing for large workflows

### Debugging Tools
- Enable verbose logging
- Use prompt inspection tools
- Check session logs
- Review export metadata

## Contributing

The Enhanced Lizzy Framework is designed to be modular and extensible. Each component can be developed and tested independently, making it easy to add new features or modify existing functionality.

### Module Independence
- Templates can be modified without affecting other components
- New bucket types can be added easily
- Export formats can be extended
- GUI components are modular

### Extension Points
- Custom template types
- New export formats
- Additional analysis tools
- Workflow automation scripts

## Future Enhancements

### Planned Features
- **Web Interface**: Browser-based GUI
- **Collaboration Tools**: Multi-user project support
- **Advanced Analytics**: ML-based content analysis
- **Plugin System**: Third-party extensions

### Research Directions
- **Prompt Optimization**: Automated prompt improvement
- **Content Quality Metrics**: Objective quality assessment
- **Workflow Intelligence**: Adaptive workflow recommendations
- **Cross-Project Learning**: Knowledge transfer between projects

---

The Enhanced Lizzy Framework represents a new approach to AI-assisted creative work, where transparency and user control are paramount. By providing complete visibility into the AI process, it empowers writers to understand, control, and improve their creative workflows.