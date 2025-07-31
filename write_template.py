#!/usr/bin/env python3
"""
Template-aware writing module for LIZZY Framework
Supports both Romantic Comedy and Academic Textbook templates
"""

import os
import sqlite3
from lightrag import LightRAG, QueryParam
from lightrag.llm import gpt_4o_mini_complete

BUCKETS_DIR = "./lightrag_working_dir"

# Template-specific writing configurations
TEMPLATE_CONFIGS = {
    "romcom": {
        "source_tables": ["story_outline", "characters", "brainstorming_log_v*"],
        "output_prefix": "draft",
        "tone_prompts": {
            "screenplay": "Write in proper screenplay format with INT/EXT sluglines, character names in caps, and concise action lines.",
            "novel": "Write in narrative prose with rich descriptions, internal thoughts, and flowing dialogue.",
            "treatment": "Write as a film treatment with present tense, visual descriptions, and story beats."
        },
        "default_guidance": "Focus on character chemistry, comedic timing, and emotional authenticity."
    },
    "textbook": {
        "source_tables": ["chapters", "learning_objectives", "content_sections", "brainstorming_log_v*"],
        "output_prefix": "manuscript",
        "tone_prompts": {
            "academic": "Write in formal academic style with clear topic sentences, evidence-based arguments, and proper citations.",
            "accessible": "Write in an engaging, accessible style that maintains academic rigor while being student-friendly.",
            "reference": "Write in reference format with clear definitions, bullet points, and quick-access information."
        },
        "default_guidance": "Ensure content aligns with learning objectives and builds on previous concepts."
    }
}

class TemplateWriter:
    def __init__(self, base_dir="projects"):
        self.base_dir = base_dir
        self.project_name = None
        self.conn = None
        self.template_type = None
        self.lightrag = None
        self.selected_buckets = []
        self.bucket_guidance = {}
        self.writing_style = ""
        self.goal = ""
        self.additional_context = ""
        self.output_table = None
        self.source_table = None
        self.source_columns = []

    def get_project_template(self):
        """Detect the template type from project metadata"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM project_metadata WHERE key='template_type'")
        result = cursor.fetchone()
        return result[0] if result else 'romcom'

    def start(self):
        """Main workflow"""
        self.select_project()
        self.select_buckets()
        self.select_source_table()
        self.select_writing_style()
        self.goal = input(f"\n What should this {self.template_type} writing accomplish?: ").strip()
        self.additional_context = input("\n Additional context or requirements: ").strip()
        self.create_output_table()
        self.run()

    def select_project(self):
        """Select project and detect template"""
        print("\n Available Projects:")
        projects = [p for p in os.listdir(self.base_dir) if os.path.isdir(os.path.join(self.base_dir, p))]
        for p in projects:
            print(f"- {p}")
        
        while True:
            name = input("\nSelect a project: ").strip()
            db_path = os.path.join(self.base_dir, name, f"{name}.sqlite")
            if os.path.exists(db_path):
                self.project_name = name
                self.conn = sqlite3.connect(db_path)
                self.template_type = self.get_project_template()
                print(f" Loaded {self.template_type.upper()} project: {name}")
                break
            print(" Project not found.")

    def select_buckets(self):
        """Select appropriate buckets based on template"""
        print("\n Available Buckets:")
        all_buckets = [b for b in os.listdir(BUCKETS_DIR) if os.path.isdir(os.path.join(BUCKETS_DIR, b))]
        
        # Filter recommended buckets based on template
        if self.template_type == "romcom":
            recommended = ["books", "scripts", "plays"]
        else:  # textbook
            recommended = ["pedagogical", "academic_sources", "examples"]
        
        available_recommended = [b for b in recommended if b in all_buckets]
        other_buckets = [b for b in all_buckets if b not in recommended]
        
        print("\n Recommended for your template:")
        for i, b in enumerate(available_recommended, 1):
            print(f"{i}. {b}")
        
        if other_buckets:
            print("\n Other available:")
            for i, b in enumerate(other_buckets, len(available_recommended) + 1):
                print(f"{i}. {b}")
        
        choices = input("\nEnter bucket numbers (comma-separated, or 'all' for recommended): ").strip()
        
        if choices.lower() == "all":
            self.selected_buckets = available_recommended
        else:
            indices = [int(c.strip()) - 1 for c in choices.split(",") if c.strip().isdigit()]
            all_available = available_recommended + other_buckets
            self.selected_buckets = [all_available[i] for i in indices if 0 <= i < len(all_available)]
        
        # Get guidance for each bucket
        for b in self.selected_buckets:
            if self.template_type == "romcom":
                prompt = f"\n How should '{b}' inform the screenplay/story?: "
            else:
                prompt = f"\n How should '{b}' inform the educational content?: "
            self.bucket_guidance[b] = input(prompt).strip()
        
        # Initialize LightRAG
        self.lightrag = LightRAG(BUCKETS_DIR, llm_model_func=gpt_4o_mini_complete)

    def select_source_table(self):
        """Select source table based on template"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        all_tables = [row[0] for row in cursor.fetchall()]
        
        # Get template-specific tables
        template_config = TEMPLATE_CONFIGS[self.template_type]
        recommended_tables = []
        
        for pattern in template_config["source_tables"]:
            if "*" in pattern:
                # Handle wildcard patterns
                prefix = pattern.replace("*", "")
                matching = [t for t in all_tables if t.startswith(prefix)]
                recommended_tables.extend(matching)
            elif pattern in all_tables:
                recommended_tables.append(pattern)
        
        print(f"\n Available source tables for {self.template_type}:")
        for i, t in enumerate(recommended_tables, 1):
            print(f"{i}. {t}")
        
        table_idx = int(input("Select table number: ").strip()) - 1
        self.source_table = recommended_tables[table_idx]
        
        # Get columns
        cursor.execute(f"PRAGMA table_info({self.source_table})")
        self.source_columns = [row[1] for row in cursor.fetchall()]
        print("\n Using columns:")
        for col in self.source_columns:
            print(f"- {col}")

    def select_writing_style(self):
        """Select writing style based on template"""
        template_config = TEMPLATE_CONFIGS[self.template_type]
        tone_prompts = template_config["tone_prompts"]
        
        print(f"\n Choose writing style for {self.template_type}:")
        style_keys = list(tone_prompts.keys())
        for i, key in enumerate(style_keys, 1):
            print(f"{i}. {key.title()}")
        
        choice = int(input(f"Enter 1-{len(style_keys)}: ").strip()) - 1
        style_key = style_keys[choice]
        self.writing_style = tone_prompts[style_key]

    def create_output_table(self):
        """Create versioned output table"""
        cursor = self.conn.cursor()
        prefix = TEMPLATE_CONFIGS[self.template_type]["output_prefix"]
        
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '{prefix}_v%'")
        existing = cursor.fetchall()
        versions = []
        for t in existing:
            try:
                version = int(t[0].split("_v")[-1])
                versions.append(version)
            except:
                pass
        
        version = max(versions) + 1 if versions else 1
        self.output_table = f"{prefix}_v{version}"
        
        # Create table with template-appropriate schema
        if self.template_type == "romcom":
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.output_table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_table TEXT,
                    source_id INTEGER,
                    act INTEGER,
                    scene INTEGER,
                    content TEXT,
                    word_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
        else:  # textbook
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.output_table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_table TEXT,
                    source_id INTEGER,
                    chapter_id INTEGER,
                    section_title TEXT,
                    content TEXT,
                    word_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
        
        self.conn.commit()
        print(f" Created output table: {self.output_table}")

    def build_prompt(self, context_dict):
        """Build template-appropriate prompt"""
        context_str = "\n".join([f"{k}: {v}" for k, v in context_dict.items() if v])
        guidance_sections = "\n\n".join([f"[{b.upper()} Context]\n{self.bucket_guidance[b]}" for b in self.selected_buckets])
        
        template_guidance = TEMPLATE_CONFIGS[self.template_type]["default_guidance"]
        
        parts = [
            f"Writing Style: {self.writing_style}",
            f"Goal: {self.goal}",
            f"Template Guidance: {template_guidance}",
            f"\n---CONTEXT---\n{context_str}\n---",
            guidance_sections
        ]
        
        if self.additional_context:
            parts.append(f"\nAdditional Requirements: {self.additional_context}")
        
        return "\n\n".join(parts)

    def run(self):
        """Execute writing based on template"""
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT rowid, * FROM {self.source_table}")
        rows = cursor.fetchall()
        
        cursor.execute(f"PRAGMA table_info({self.source_table})")
        columns = [row[1] for row in cursor.fetchall()]
        
        for row in rows:
            row_dict = dict(zip(["rowid"] + columns, row))
            row_id = row_dict["rowid"]
            
            # Filter relevant content
            context_data = {col: row_dict.get(col, "") for col in self.source_columns if row_dict.get(col, "")}
            if not context_data:
                print(f" Skipping row {row_id} — no content.")
                continue
            
            # Format prefix based on template
            if self.template_type == "romcom":
                act = row_dict.get("act")
                scene = row_dict.get("scene")
                prefix = f"Act {act}, Scene {scene}" if act and scene else f"Row {row_id}"
            else:  # textbook
                chapter = row_dict.get("chapter_title") or row_dict.get("chapter_id")
                section = row_dict.get("section_title")
                prefix = f"Chapter: {chapter}" + (f", Section: {section}" if section else "")
            
            print(f"\n Writing: {prefix}")
            
            prompt = self.build_prompt(context_data)
            
            try:
                print(f"\n PROMPT:\n{prompt}\n")
                result = self.lightrag.query(prompt, param=QueryParam(mode="mix", buckets=self.selected_buckets))
                word_count = len(result.split())
                print(f" RESPONSE ({word_count} words):\n{result}\n{'-'*60}")
                
                # Save based on template
                if self.template_type == "romcom":
                    cursor.execute(
                        f"""INSERT INTO {self.output_table} 
                        (source_table, source_id, act, scene, content, word_count) 
                        VALUES (?, ?, ?, ?, ?, ?)""",
                        (self.source_table, row_id, row_dict.get("act"), row_dict.get("scene"), result, word_count)
                    )
                else:  # textbook
                    cursor.execute(
                        f"""INSERT INTO {self.output_table} 
                        (source_table, source_id, chapter_id, section_title, content, word_count) 
                        VALUES (?, ?, ?, ?, ?, ?)""",
                        (self.source_table, row_id, row_dict.get("chapter_id"), row_dict.get("section_title"), result, word_count)
                    )
                
                self.conn.commit()
                
            except Exception as e:
                print(f" Error processing {prefix}: {e}")
        
        print(f"\n Writing complete! Output saved to table: {self.output_table}")

if __name__ == "__main__":
    writer = TemplateWriter()
    writer.start()