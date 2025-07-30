# LIZZY Framework

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
║              🎬 AI-ASSISTED SCREENWRITING SYSTEM 🎬                          ║
║                     ~ Structure • Intelligence • Craft ~                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**From Story Idea to Professional Screenplay in Minutes, Not Months**

</div>

---

## 🎯 What LIZZY Does

LIZZY guides you through the complete screenwriting process using a proven workflow:

**Your Input** → **AI Enhancement** → **Professional Output**

- **🧠 Story Development**: Build rich characters and compelling scene outlines
- **📚 Knowledge Integration**: Access curated screenwriting wisdom and techniques  
- **🤖 AI Brainstorming**: Generate creative ideas contextual to YOUR specific story
- **✍️ Screenplay Writing**: Produce properly formatted scenes with authentic dialogue
- **📈 Version Management**: Track every iteration with complete revision history
- **📤 Professional Export**: Output industry-standard formats ready for production

---

## 🚀 Quick Start for Screenwriters

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
python lizzy.py
```

On first run, LIZZY will ask for your OpenAI API key and create your workspace.

---

## 🎬 How Screenwriters Use LIZZY

### The LIZZY Workflow

```
Create Project → Build Story Foundation → AI Brainstorm → Write Scenes → Polish & Export
```

### Step 1: Project Setup
```
LIZZY
-----
1. New Project ← Start here
2. Existing Project
3. Getting Started
```

Create your screenplay project. Each project gets its own isolated database, so you can work on multiple scripts simultaneously without any mixing of characters or story elements.

### Step 2: Build Your Story Foundation
```
PROJECT: My Romantic Comedy
---------------------------
1. Update Tables ← Add your story elements
2. Update Buckets
3. Brainstorm
4. Write
5. Version History
6. Export Options
```

**Update Tables** lets you define:
- **Characters**: Names, personality traits, flaws, romantic challenges
- **Scenes**: Act/scene structure, key events, character arcs
- **Notes**: Random ideas, themes, visual concepts

*Example Character Entry:*
```
Name: Sarah Chen
Age: 28
Lovable Trait: Finds humor in disasters
Comedic Flaw: Terrible at reading social cues
Romantic Challenge: Fears vulnerability after bad breakup
```

### Step 3: Feed the Knowledge Base
```
BUCKETS
-------
Books    ← Screenwriting guides, character development
Scripts  ← Professional screenplay examples  
Plays    ← Dialogue techniques, theatrical timing
```

**Update Buckets** lets you add reference materials:
- Upload `.txt`, `.pdf`, or `.md` files with writing advice
- Add example scripts you admire
- Include character archetypes, dialogue samples, story structures

LIZZY uses these as contextual knowledge when generating ideas.

### Step 4: AI-Powered Brainstorming
```
BRAINSTORM MODE
---------------
- Pick buckets: [books, scripts] ✓
- Pick tables: [characters, scenes] ✓  
- Add guidance: "Focus on meet-cute scenarios"

[ ] Start brainstorm?
```

The AI analyzes YOUR specific characters and story, combines it with screenwriting knowledge from your buckets, and generates:
- **Scene concepts** tailored to your characters
- **Dialogue ideas** that match their voices
- **Visual moments** that advance your specific plot
- **Character development** opportunities

*Sample Brainstorm Output:*
```
SCENE CONCEPTS:
• Sarah's social awkwardness leads to coffee shop misunderstanding
• Use her humor-in-disasters trait when she accidentally crashes wedding
• Vulnerability moment: Sarah admits fear through self-deprecating joke

DIALOGUE IDEAS:  
• "I have a gift for turning meet-cutes into meet-disasters"
• "That's either the worst pickup line or refreshingly honest"
```

### Step 5: Write Professional Scenes
```
WRITE MODE
----------
- Uses latest brainstorm automatically ✓
- Pick additional context
- Add specific direction: "Write opening scene"

[ ] Start writing?
```

LIZZY transforms brainstorm ideas into properly formatted screenplay scenes:

```
FADE IN:

INT. DOWNTOWN COFFEE SHOP - MORNING

SARAH CHEN (28, paint-stained apron, sketchbook clutched 
protectively) navigates through the morning rush crowd. 
Her eyes dart between faces, looking for an escape route.

She spots an empty corner table. Perfect.

Sarah makes a beeline for it, focused on her destination. 
She doesn't see JAKE (30, rumpled business casual, 
juggling phone and laptop bag) coming from the opposite 
direction.

COLLISION. 

Coffee erupts in all directions. Sarah's sketchbook flies 
open, pages fluttering.

                    SARAH
          (surveying the disaster)
     I have a gift for turning simple 
     tasks into abstract art.

                    JAKE
          (kneeling to help gather pages)
     Is that what this is? Because I 
     was thinking more... Jackson Pollock 
     meets morning caffeine crisis.

Sarah looks up. Their eyes meet over a coffee-stained 
sketch of a couple sharing an umbrella.

                    SARAH
     That's either the worst pickup line 
     or refreshingly honest.

                    JAKE
     Why not both?

FADE OUT.
```

### Step 6: Track & Refine
```
VERSIONS
--------
BRAINSTORM VERSIONS:
1. BS_20250130_143022 - Initial meet-cute ideas
2. BS_20250130_150415 - Character voice development

WRITE VERSIONS:  
1. Version 1 - Opening scene (347 words)
2. Version 2 - Revised with more conflict (412 words)
```

Every brainstorm and draft is saved with full metadata. Compare versions, reuse old ideas, track your creative evolution.

### Step 7: Professional Export
```
EXPORT
------
1. Export brainstorms     ← Save all creative sessions
2. Export final drafts    ← Properly formatted screenplays
3. Export tables         ← Character/scene databases  
4. Export everything     ← Complete project archive
```

Get your screenplay in multiple formats ready for producers, directors, or contest submissions.

---

## 🧠 The AI Advantage

### Context-Aware Intelligence
Unlike generic AI writing tools, LIZZY knows YOUR story:
- Remembers your characters' specific traits and flaws
- Builds on your established story structure  
- Maintains consistency across scenes and drafts
- Incorporates your preferred writing techniques and references

### Iterative Creativity
Each session builds on the last:
```
Draft 1: Basic scene structure
↓ (brainstorm feedback: "needs more conflict")
Draft 2: Added character tension  
↓ (brainstorm feedback: "strengthen dialogue")
Draft 3: Sharper, more authentic voices
```

---

## 💡 For Professional Screenwriters

### Time Efficiency
- **Research Phase**: Upload reference scripts → instant knowledge base
- **Development**: Character creation → scene outline → first draft in hours
- **Revision**: AI suggestions based on your specific story problems
- **Formatting**: Industry-standard output, no manual formatting needed

### Creative Enhancement
- **Writer's Block**: AI generates story-specific ideas, not generic prompts
- **Character Voice**: Maintain consistency across 120-page scripts
- **Scene Beats**: Ensure every scene advances YOUR particular plot
- **Dialogue Polish**: AI suggestions match each character's established voice

### Project Management
- **Multiple Projects**: Each screenplay completely isolated
- **Version Control**: Never lose a good idea or draft
- **Collaboration Ready**: Export complete project archives
- **Portfolio Building**: Track creative evolution across projects

---

## 🛠️ Technical Architecture

### Project Isolation
```
projects/
├── romantic_comedy_draft/
│   └── romantic_comedy_draft.sqlite    # Isolated story data
├── thriller_spec/
│   └── thriller_spec.sqlite            # Completely separate
└── family_drama/
    └── family_drama.sqlite
```

### Shared Knowledge Base
```
lightrag_working_dir/
├── books/          # Screenwriting guides, character development
├── scripts/        # Professional screenplay examples
└── plays/          # Dialogue techniques, theatrical timing
```

### AI Integration
- **OpenAI GPT-4o Mini**: Creative text generation optimized for cost/quality
- **LightRAG**: Semantic knowledge retrieval (~200ms response time)
- **Context Assembly**: Your story + writing knowledge = personalized output

---

## 📚 Templates & Expansion

LIZZY currently specializes in **screenwriting** with a romantic comedy foundation, but the architecture supports unlimited story types.

**🚧 Coming Soon:**
- **Genre Templates**: Thriller, Drama, Sci-Fi, Horror, Documentary
- **Format Templates**: TV Episodes, Web Series, Short Films
- **Style Templates**: Indie, Studio, International markets
- **Specialized Workflows**: Adaptation, Rewrite, Polish passes

The modular design means new templates plug directly into the existing workflow—same tools, different creative focus.

---

## 🎭 Example: From Idea to Script

**Start**: "I want to write a romantic comedy about two people who keep having terrible first dates"

**30 minutes later**: Complete opening scene with:
- Fully developed characters (Sarah: disaster-magnet artist, Jake: over-planner consultant)  
- Authentic dialogue matching their personalities
- Visual comedy that sets up the story's central theme
- Professional screenplay formatting
- Ideas for 5 more scenes generated and saved

**The difference**: Instead of staring at a blank page wondering "what would these characters say?", you have AI that knows Sarah uses humor to deflect vulnerability and Jake over-explains when nervous.

---

## 🚀 Get Started Now

```bash
git clone https://github.com/ejresearch/Elizabeth_PI.git
cd Elizabeth_PI
pip install openai lightrag-hku tiktoken numpy
python lizzy.py
```

**Your first screenplay starts with a single command.**

---

## 📞 Support & Community

- **Issues**: [GitHub Issues](https://github.com/ejresearch/Elizabeth_PI/issues)
- **Documentation**: Built-in help system (Help & Documentation in main menu)
- **Examples**: Includes "The Last Coffee Shop" sample project

---

<div align="center">

**LIZZY Framework** - *Professional screenwriting, intelligent assistance*

*Transform your story ideas into compelling screenplays with AI that understands your unique creative vision.*

</div>