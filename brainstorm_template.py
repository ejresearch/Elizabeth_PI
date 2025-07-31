#!/usr/bin/env python3
"""
Template-aware brainstorming module for LIZZY Framework
Supports both Romantic Comedy and Academic Textbook templates
"""

import os
import sqlite3
from lightrag import LightRAG, QueryParam

# Template-specific prompt configurations
TEMPLATE_PROMPTS = {
    "romcom": {
        "tones": {
            "cheesy-romcom": "Write this scene as if it's from a bubbly, cliché-filled romantic comedy full of silly misunderstandings and charm.",
            "romantic-dramedy": "Write this scene like it's a grounded romantic dramedy—funny but heartfelt, with honest emotional tension and subtle humor.",
            "shakespearean-romance": "Craft this scene in the style of a Shakespearean romantic comedy—rich in language, irony, and poetic flare."
        },
        "bucket_guidance": {
            "books": """
You are an expert on screenwriting theory, drawing from acclaimed screenwriting books.
Provide insights on **structure, pacing, and character arcs**.
Explain **scene progression within a three-act structure** based on established principles.
""",
            "scripts": """
You are an expert in romantic comedy screenplays, knowledgeable of the top 100 romcom scripts.
Compare this scene to **moments from successful romcoms**.
Suggest effective use of **romcom tropes** with a focus on dialogue, humor, and pacing.
""",
            "plays": """
You are an expert in Shakespearean drama and comedy, deeply familiar with Shakespeare's complete works.
Analyze the scene through a **Shakespearean lens**, focusing on **character dynamics, irony, heightened language, and themes**.
"""
        }
    },
    "textbook": {
        "tones": {
            "academic-formal": "Write in clear, formal academic prose suitable for university students, with proper terminology and scholarly tone.",
            "conversational-teaching": "Write as if explaining to students in an engaging classroom setting, balancing accessibility with academic rigor.",
            "simplified-introductory": "Write for beginners with simple language, clear definitions, and many relatable examples."
        },
        "bucket_guidance": {
            "pedagogical": """
You are an expert in educational theory and instructional design.
Focus on **learning objectives, cognitive load, and scaffolding concepts**.
Ensure content aligns with **Bloom's taxonomy** and promotes active learning.
""",
            "academic_sources": """
You are an expert in academic research and scholarly writing.
Emphasize **evidence-based content, proper citations, and academic integrity**.
Connect concepts to **current research and established theories** in the field.
""",
            "examples": """
You are an expert at making abstract concepts concrete through examples.
Provide **real-world applications, case studies, and practical scenarios**.
Use **analogies and comparisons** to enhance understanding.
"""
        }
    }
}

class TemplateBrainstormingAgent:
    def __init__(self, lightrag_instances, base_dir="projects"):
        self.lightrag = lightrag_instances
        self.base_dir = base_dir
        self.project_name = None
        self.conn = None
        self.template_type = None
        self.prompt_style = None
        self.easter_egg = ""
        self.table_name = None

    def get_project_template(self):
        """Detect the template type from project metadata"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM project_metadata WHERE key='template_type'")
        result = cursor.fetchone()
        return result[0] if result else 'romcom'  # default to romcom

    def setup_project(self):
        """Select project and detect its template type"""
        print(" Available Projects:")
        for name in os.listdir(self.base_dir):
            if os.path.isdir(os.path.join(self.base_dir, name)):
                print(f"- {name}")

        while True:
            project = input("\nEnter project name: ").strip()
            path = os.path.join(self.base_dir, project, f"{project}.sqlite")
            if os.path.exists(path):
                self.project_name = project
                self.conn = sqlite3.connect(path)
                self.template_type = self.get_project_template()
                print(f" Loaded {self.template_type.upper()} project: {project}")
                break
            print(" Not found. Try again.")

    def select_prompt_style(self):
        """Choose template-appropriate prompt tone"""
        template_tones = TEMPLATE_PROMPTS[self.template_type]["tones"]
        print(f"\n Choose a prompt tone for {self.template_type}:")
        
        tone_keys = list(template_tones.keys())
        for i, key in enumerate(tone_keys, 1):
            print(f"{i}. {key.replace('-', ' ').title()}")
        
        choice = input(f"Enter 1–{len(tone_keys)}: ").strip()
        self.prompt_style = tone_keys[int(choice) - 1]

    def input_easter_egg(self):
        """Optional creative twist"""
        if self.template_type == "romcom":
            idea = input("\n Add an optional easter egg or twist (or leave blank): ").strip()
        else:  # textbook
            idea = input("\n Add specific focus or emphasis (or leave blank): ").strip()
        self.easter_egg = idea

    def get_next_table_name(self):
        """Get versioned table name"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'brainstorming_log_v%'")
        tables = cursor.fetchall()
        versions = [int(name[0].split("_v")[-1]) for name in tables if "_v" in name[0]]
        next_version = max(versions) + 1 if versions else 1
        return f"brainstorming_log_v{next_version}"

    def setup_table(self):
        """Create brainstorming output table"""
        self.table_name = self.get_next_table_name()
        cursor = self.conn.cursor()
        
        if self.template_type == "romcom":
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    act INTEGER NOT NULL,
                    scene INTEGER NOT NULL,
                    scene_description TEXT NOT NULL,
                    bucket_name TEXT NOT NULL,
                    response TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:  # textbook
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chapter_id INTEGER NOT NULL,
                    section_title TEXT,
                    content_description TEXT NOT NULL,
                    bucket_name TEXT NOT NULL,
                    response TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        self.conn.commit()
        print(f" Created table: {self.table_name}")

    def fetch_content_items(self):
        """Fetch items to brainstorm based on template"""
        cursor = self.conn.cursor()
        
        if self.template_type == "romcom":
            cursor.execute("""
                SELECT act, scene, key_events 
                FROM story_outline 
                WHERE key_events IS NOT NULL AND key_events != ''
                ORDER BY act, scene
            """)
            return cursor.fetchall()
        else:  # textbook
            cursor.execute("""
                SELECT c.id, c.chapter_title, cs.section_title, cs.section_content
                FROM chapters c
                LEFT JOIN content_sections cs ON c.id = cs.chapter_id
                WHERE cs.section_content IS NOT NULL AND cs.section_content != ''
                ORDER BY c.chapter_number, cs.sequence_order
            """)
            return cursor.fetchall()

    def create_prompt(self, bucket_name, content_description):
        """Generate template-appropriate prompt"""
        template_config = TEMPLATE_PROMPTS[self.template_type]
        tone_prompt = template_config["tones"][self.prompt_style]
        bucket_guidance = template_config["bucket_guidance"].get(bucket_name, "")
        
        if self.easter_egg:
            if self.template_type == "romcom":
                tone_prompt += f"\n\n Writer twist: {self.easter_egg}"
            else:
                tone_prompt += f"\n\n Focus area: {self.easter_egg}"
        
        return f"""
{tone_prompt}

### Content:
{content_description}

### Task:
{bucket_guidance.strip()}
"""

    def query_bucket(self, bucket, prompt):
        """Query LightRAG bucket"""
        try:
            print(f" Querying {bucket} bucket...")
            return self.lightrag[bucket].query(prompt, param=QueryParam(mode="mix"))
        except Exception as e:
            print(f" Error querying {bucket}: {e}")
            return "No output."

    def save_response(self, *args):
        """Save brainstorming response based on template"""
        cursor = self.conn.cursor()
        
        if self.template_type == "romcom":
            act, scene, desc, bucket, response = args
            cursor.execute(
                f"""INSERT INTO {self.table_name}
                (act, scene, scene_description, bucket_name, response)
                VALUES (?, ?, ?, ?, ?)""",
                (act, scene, desc, bucket, response)
            )
        else:  # textbook
            chapter_id, section_title, desc, bucket, response = args
            cursor.execute(
                f"""INSERT INTO {self.table_name}
                (chapter_id, section_title, content_description, bucket_name, response)
                VALUES (?, ?, ?, ?, ?)""",
                (chapter_id, section_title, desc, bucket, response)
            )
        
        self.conn.commit()

    def run(self):
        """Execute brainstorming based on template"""
        items = self.fetch_content_items()
        if not items:
            print(" No content found to brainstorm.")
            return

        # Select appropriate buckets based on template
        if self.template_type == "romcom":
            active_buckets = ["books", "scripts", "plays"]
        else:  # textbook
            active_buckets = ["pedagogical", "academic_sources", "examples"]
        
        # Filter to only use buckets that exist
        active_buckets = [b for b in active_buckets if b in self.lightrag]
        
        if self.template_type == "romcom":
            for act, scene, summary in items:
                print(f"\n Act {act}, Scene {scene}")
                for bucket in active_buckets:
                    prompt = self.create_prompt(bucket, summary)
                    result = self.query_bucket(bucket, prompt)
                    self.save_response(act, scene, summary, bucket, result)
                    print(f"\n Brainstorm ({bucket.capitalize()}):\n{result}\n{'-'*60}")
        else:  # textbook
            for chapter_id, chapter_title, section_title, content in items:
                print(f"\n Chapter: {chapter_title}")
                if section_title:
                    print(f"   Section: {section_title}")
                
                for bucket in active_buckets:
                    prompt = self.create_prompt(bucket, content)
                    result = self.query_bucket(bucket, prompt)
                    self.save_response(chapter_id, section_title or chapter_title, content, bucket, result)
                    print(f"\n Brainstorm ({bucket.capitalize()}):\n{result}\n{'-'*60}")

if __name__ == "__main__":
    # Initialize LightRAG instances for available buckets
    lightrag_instances = {}
    
    # RomCom buckets
    if os.path.exists("./lightrag_working_dir/books"):
        lightrag_instances["books"] = LightRAG(working_dir="./lightrag_working_dir/books")
    if os.path.exists("./lightrag_working_dir/scripts"):
        lightrag_instances["scripts"] = LightRAG(working_dir="./lightrag_working_dir/scripts")
    if os.path.exists("./lightrag_working_dir/plays"):
        lightrag_instances["plays"] = LightRAG(working_dir="./lightrag_working_dir/plays")
    
    # Textbook buckets
    if os.path.exists("./lightrag_working_dir/pedagogical"):
        lightrag_instances["pedagogical"] = LightRAG(working_dir="./lightrag_working_dir/pedagogical")
    if os.path.exists("./lightrag_working_dir/academic_sources"):
        lightrag_instances["academic_sources"] = LightRAG(working_dir="./lightrag_working_dir/academic_sources")
    if os.path.exists("./lightrag_working_dir/examples"):
        lightrag_instances["examples"] = LightRAG(working_dir="./lightrag_working_dir/examples")
    
    # Run the agent
    agent = TemplateBrainstormingAgent(lightrag_instances)
    agent.setup_project()
    agent.select_prompt_style()
    agent.input_easter_egg()
    agent.setup_table()
    agent.run()
    agent.conn.close()
    print("\n Brainstorming complete!")