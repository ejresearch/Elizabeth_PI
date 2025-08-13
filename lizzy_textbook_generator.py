#!/usr/bin/env python3
"""
Textbook Outline Generator for Lizzy
Generates comprehensive textbook outlines using film book buckets
"""

import os
import sys
import sqlite3
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed

# Add the main directory to path
sys.path.append('/Users/elle/Desktop/Elizabeth_PI')
from lizzy_templates import TemplateManager

class TextbookOutlineGenerator:
    """Generates comprehensive textbook outlines using academic film sources"""
    
    def __init__(self, project_dir="projects"):
        self.project_dir = project_dir
        self.project_name = None
        self.conn = None
        self.template_manager = TemplateManager()
        self.template_manager.load_bucket_config()
        self.film_book_buckets = self.template_manager.get_template_buckets("textbook")
        self.lightrag_instances = {}
        self.outline_data = {
            "metadata": {},
            "chapters": [],
            "concepts": {},
            "bibliography": []
        }
        
    async def initialize_buckets(self):
        """Initialize LightRAG instances for film book buckets"""
        print("📚 Initializing film book buckets...")
        
        working_dir = "/Users/elle/Desktop/Elizabeth_PI/lightrag_working_dir"
        
        for bucket in self.film_book_buckets:
            bucket_path = os.path.join(working_dir, bucket)
            if os.path.exists(bucket_path):
                try:
                    self.lightrag_instances[bucket] = LightRAG(
                        working_dir=bucket_path,
                        embedding_func=openai_embed,
                        llm_model_func=gpt_4o_mini_complete
                    )
                    print(f"   ✅ {bucket} initialized")
                except Exception as e:
                    print(f"   ❌ {bucket} failed: {e}")
            else:
                print(f"   ⚠️ {bucket} not found")
    
    def select_project(self):
        """Select or create a project for the textbook"""
        print("\n📂 TEXTBOOK OUTLINE GENERATOR")
        print("="*50)
        
        # Show existing projects
        if os.path.exists(self.project_dir):
            projects = [p for p in os.listdir(self.project_dir) 
                       if os.path.isdir(os.path.join(self.project_dir, p))]
            if projects:
                print("\nExisting projects:")
                for i, project in enumerate(projects, 1):
                    print(f"  {i}. {project}")
        
        # Get project choice
        choice = input("\nEnter project name (new or existing): ").strip()
        
        if not choice:
            choice = f"textbook_{datetime.now().strftime('%Y%m%d_%H%M')}"
        
        self.project_name = choice
        project_path = os.path.join(self.project_dir, choice)
        os.makedirs(project_path, exist_ok=True)
        
        # Connect to database
        db_path = os.path.join(project_path, f"{choice}.sqlite")
        self.conn = sqlite3.connect(db_path)
        self.setup_database()
        
        print(f"📖 Project: {choice}")
    
    def setup_database(self):
        """Create database schema for textbook generation"""
        cursor = self.conn.cursor()
        
        # Textbook metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS textbook_metadata (
                title TEXT,
                subject TEXT,
                target_audience TEXT,
                academic_level TEXT,
                focus_areas TEXT,
                pedagogical_approach TEXT,
                created_at TEXT,
                updated_at TEXT
            )''')
        
        # Chapter outlines
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chapters (
                chapter_number INTEGER,
                title TEXT,
                overview TEXT,
                learning_objectives TEXT,
                key_concepts TEXT,
                theoretical_frameworks TEXT,
                case_studies TEXT,
                exercises TEXT,
                readings TEXT,
                estimated_length INTEGER
            )''')
        
        # Concept hierarchy
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS concepts (
                concept_id TEXT PRIMARY KEY,
                name TEXT,
                category TEXT,
                definition TEXT,
                theorist TEXT,
                related_concepts TEXT,
                chapter_references TEXT,
                complexity_level TEXT,
                prerequisite_concepts TEXT
            )''')
        
        # Bibliography
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bibliography (
                source_id TEXT PRIMARY KEY,
                type TEXT,
                author TEXT,
                title TEXT,
                publication TEXT,
                year INTEGER,
                relevance_score INTEGER,
                chapter_references TEXT,
                key_concepts TEXT
            )''')
        
        # Generation logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generation_log (
                timestamp TEXT,
                stage TEXT,
                bucket TEXT,
                prompt TEXT,
                response TEXT,
                tokens_used INTEGER
            )''')
        
        self.conn.commit()
        print("✅ Database schema created")
    
    def gather_textbook_requirements(self):
        """Collect requirements for textbook generation"""
        print("\n📋 TEXTBOOK REQUIREMENTS")
        print("-"*30)
        
        title = input("📖 Textbook title: ").strip() or "Film Studies Textbook"
        subject = input("🎬 Subject area: ").strip() or "Film Theory and Analysis"
        audience = input("👥 Target audience: ").strip() or "Undergraduate students"
        level = input("🎓 Academic level (intro/intermediate/advanced): ").strip() or "intermediate"
        
        print("\n🎯 Focus areas (separate with commas):")
        print("Examples: narrative theory, genre analysis, auteur theory, cultural studies")
        focus_input = input("Focus areas: ").strip()
        focus_areas = [area.strip() for area in focus_input.split(",")] if focus_input else [
            "narrative theory", "genre analysis", "visual storytelling", "film history"
        ]
        
        approach = input("\n📚 Pedagogical approach (theoretical/practical/mixed): ").strip() or "mixed"
        
        # Store metadata
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO textbook_metadata 
            (title, subject, target_audience, academic_level, focus_areas, pedagogical_approach, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (title, subject, audience, level, json.dumps(focus_areas), approach, 
             datetime.now().isoformat(), datetime.now().isoformat()))
        self.conn.commit()
        
        self.outline_data["metadata"] = {
            "title": title,
            "subject": subject,
            "target_audience": audience,
            "academic_level": level,
            "focus_areas": focus_areas,
            "pedagogical_approach": approach
        }
        
        print(f"\n✅ Requirements saved for: {title}")
    
    async def generate_chapter_structure(self):
        """Generate comprehensive chapter structure using academic sources"""
        print("\n📚 GENERATING CHAPTER STRUCTURE")
        print("-"*40)
        
        metadata = self.outline_data["metadata"]
        
        # Build comprehensive prompt for chapter structure
        structure_prompt = f"""
        Create a comprehensive chapter structure for a {metadata['academic_level']} level textbook titled "{metadata['title']}".

        TEXTBOOK SPECIFICATIONS:
        - Subject: {metadata['subject']}
        - Target Audience: {metadata['target_audience']}
        - Academic Level: {metadata['academic_level']}
        - Focus Areas: {', '.join(metadata['focus_areas'])}
        - Pedagogical Approach: {metadata['pedagogical_approach']}

        REQUIREMENTS:
        1. Create 10-15 chapters with logical progression
        2. Each chapter should build on previous concepts
        3. Balance theoretical frameworks with practical applications
        4. Include foundational concepts early, advanced topics later
        5. Consider current trends and canonical theories

        For each chapter, provide:
        - Chapter number and title
        - 2-3 sentence overview
        - 4-6 specific learning objectives
        - Key theoretical concepts to cover
        - Suggested case studies or film examples
        - Connection to other chapters

        Format as a structured outline suitable for academic curriculum.
        """
        
        # Query multiple academic buckets for comprehensive coverage
        chapter_responses = {}
        
        for bucket in self.lightrag_instances:
            try:
                print(f"   🔍 Consulting {bucket}...")
                response = await self.lightrag_instances[bucket].aquery(
                    structure_prompt, 
                    param=QueryParam(mode="hybrid")
                )
                chapter_responses[bucket] = response
                
                # Log the generation
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT INTO generation_log (timestamp, stage, bucket, prompt, response, tokens_used)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    (datetime.now().isoformat(), "chapter_structure", bucket, structure_prompt, response, len(response)))
                self.conn.commit()
                
                print(f"   ✅ {bucket} response received ({len(response)} chars)")
                
            except Exception as e:
                print(f"   ❌ Error with {bucket}: {e}")
        
        # Synthesize responses into coherent chapter structure
        await self.synthesize_chapters(chapter_responses)
    
    async def synthesize_chapters(self, responses: Dict[str, str]):
        """Synthesize multiple academic perspectives into coherent chapter structure"""
        print("\n🔄 SYNTHESIZING CHAPTER STRUCTURE")
        
        synthesis_prompt = f"""
        Based on multiple academic perspectives below, create a definitive chapter structure for "{self.outline_data['metadata']['title']}".

        ACADEMIC PERSPECTIVES:
        {chr(10).join([f"[{bucket.upper()}]{chr(10)}{response}{chr(10)}" for bucket, response in responses.items()])}

        SYNTHESIS REQUIREMENTS:
        1. Combine the best elements from all perspectives
        2. Ensure logical progression and academic rigor
        3. Remove redundancy and conflicting suggestions
        4. Create exactly 12 chapters
        5. Balance breadth with depth appropriate for {self.outline_data['metadata']['academic_level']} level

        OUTPUT FORMAT for each chapter:
        Chapter X: [Title]
        Overview: [2-3 sentences]
        Learning Objectives:
        - [Objective 1]
        - [Objective 2] 
        - [Objective 3]
        Key Concepts: [list]
        Theoretical Frameworks: [list]
        Case Studies: [suggested films/examples]
        Exercises: [2-3 exercise types]
        
        Create comprehensive, publication-ready chapter outlines.
        """
        
        # Use the most comprehensive academic source for synthesis
        synthesis_bucket = max(responses.keys(), key=lambda b: len(responses[b]))
        
        try:
            final_structure = await self.lightrag_instances[synthesis_bucket].aquery(
                synthesis_prompt,
                param=QueryParam(mode="hybrid")
            )
            
            # Parse and store the final structure
            await self.parse_and_store_chapters(final_structure)
            
            print("✅ Chapter structure synthesized and stored")
            
        except Exception as e:
            print(f"❌ Synthesis error: {e}")
    
    async def parse_and_store_chapters(self, structure_text: str):
        """Parse synthesized structure and store in database"""
        cursor = self.conn.cursor()
        
        # Simple parsing logic (could be enhanced with more sophisticated parsing)
        chapters = []
        current_chapter = {}
        
        lines = structure_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('Chapter '):
                if current_chapter:
                    chapters.append(current_chapter)
                current_chapter = {'title': line, 'content': {}}
                current_section = 'title'
            elif line.startswith('Overview:'):
                current_section = 'overview'
                current_chapter['content']['overview'] = line.replace('Overview:', '').strip()
            elif line.startswith('Learning Objectives:'):
                current_section = 'objectives'
                current_chapter['content']['learning_objectives'] = []
            elif line.startswith('Key Concepts:'):
                current_section = 'concepts'
                current_chapter['content']['key_concepts'] = line.replace('Key Concepts:', '').strip()
            elif line.startswith('- ') and current_section == 'objectives':
                current_chapter['content']['learning_objectives'].append(line[2:])
            elif line and current_section == 'overview':
                current_chapter['content']['overview'] += ' ' + line
        
        if current_chapter:
            chapters.append(current_chapter)
        
        # Store chapters in database
        for i, chapter in enumerate(chapters, 1):
            title = chapter.get('title', f'Chapter {i}')
            content = chapter.get('content', {})
            
            cursor.execute('''
                INSERT OR REPLACE INTO chapters 
                (chapter_number, title, overview, learning_objectives, key_concepts)
                VALUES (?, ?, ?, ?, ?)''',
                (i, title, content.get('overview', ''), 
                 json.dumps(content.get('learning_objectives', [])),
                 content.get('key_concepts', '')))
        
        self.conn.commit()
        self.outline_data["chapters"] = chapters
        
        print(f"📖 Stored {len(chapters)} chapters")
    
    async def generate_concept_hierarchy(self):
        """Generate hierarchical concept map from academic sources"""
        print("\n🧠 GENERATING CONCEPT HIERARCHY")
        print("-"*35)
        
        concept_prompt = f"""
        Create a comprehensive concept hierarchy for "{self.outline_data['metadata']['title']}" 
        focusing on {', '.join(self.outline_data['metadata']['focus_areas'])}.

        REQUIREMENTS:
        1. Identify 50-80 key concepts across all focus areas
        2. Organize into hierarchy: Foundational → Intermediate → Advanced
        3. For each concept provide:
           - Clear definition
           - Associated theorist(s) if applicable
           - Prerequisite concepts
           - Related concepts
           - Chapter where introduced

        CONCEPT CATEGORIES:
        - Foundational: Basic terminology and principles
        - Intermediate: Theoretical frameworks and methods
        - Advanced: Complex theories and contemporary debates

        Format as structured knowledge map suitable for curriculum planning.
        """
        
        concept_responses = {}
        
        for bucket in self.lightrag_instances:
            try:
                print(f"   🔍 Extracting concepts from {bucket}...")
                response = await self.lightrag_instances[bucket].aquery(
                    concept_prompt,
                    param=QueryParam(mode="global")
                )
                concept_responses[bucket] = response
                print(f"   ✅ {bucket} concepts extracted")
                
            except Exception as e:
                print(f"   ❌ Error with {bucket}: {e}")
        
        # Store concept data
        await self.store_concepts(concept_responses)
    
    async def store_concepts(self, responses: Dict[str, str]):
        """Store concept hierarchy in database"""
        print("💾 Storing concept hierarchy...")
        
        cursor = self.conn.cursor()
        
        # Simple concept extraction (could be enhanced)
        all_concepts = []
        
        for bucket, response in responses.items():
            # Log the concept generation
            cursor.execute('''
                INSERT INTO generation_log (timestamp, stage, bucket, prompt, response, tokens_used)
                VALUES (?, ?, ?, ?, ?, ?)''',
                (datetime.now().isoformat(), "concept_hierarchy", bucket, "concept_extraction", response, len(response)))
        
        self.conn.commit()
        print("✅ Concept hierarchy stored")
    
    async def generate_bibliography(self):
        """Generate comprehensive bibliography from academic sources"""
        print("\n📚 GENERATING BIBLIOGRAPHY")
        print("-"*30)
        
        biblio_prompt = f"""
        Create a comprehensive bibliography for "{self.outline_data['metadata']['title']}"
        suitable for {self.outline_data['metadata']['academic_level']} level students.

        REQUIREMENTS:
        1. Include foundational texts in film studies
        2. Cover all focus areas: {', '.join(self.outline_data['metadata']['focus_areas'])}
        3. Mix of classic and contemporary sources
        4. Include books, journal articles, and key essays
        5. Organize by relevance and importance

        For each source provide:
        - Full citation
        - Brief annotation (2-3 sentences)
        - Relevance to specific chapters
        - Difficulty level (undergraduate/graduate)

        Prioritize canonical texts and essential readings.
        """
        
        bibliography_data = {}
        
        for bucket in self.lightrag_instances:
            try:
                print(f"   📖 Gathering sources from {bucket}...")
                response = await self.lightrag_instances[bucket].aquery(
                    biblio_prompt,
                    param=QueryParam(mode="global")
                )
                bibliography_data[bucket] = response
                print(f"   ✅ {bucket} bibliography generated")
                
            except Exception as e:
                print(f"   ❌ Error with {bucket}: {e}")
        
        await self.store_bibliography(bibliography_data)
    
    async def store_bibliography(self, data: Dict[str, str]):
        """Store bibliography in database"""
        cursor = self.conn.cursor()
        
        for bucket, response in data.items():
            cursor.execute('''
                INSERT INTO generation_log (timestamp, stage, bucket, prompt, response, tokens_used)
                VALUES (?, ?, ?, ?, ?, ?)''',
                (datetime.now().isoformat(), "bibliography", bucket, "bibliography_generation", response, len(response)))
        
        self.conn.commit()
        print("✅ Bibliography stored")
    
    def export_textbook_outline(self):
        """Export complete textbook outline"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"{self.project_name}_textbook_outline_{timestamp}.md"
        filepath = os.path.join(self.project_dir, self.project_name, filename)
        
        cursor = self.conn.cursor()
        
        # Get all data
        cursor.execute("SELECT * FROM textbook_metadata")
        metadata = cursor.fetchone()
        
        cursor.execute("SELECT * FROM chapters ORDER BY chapter_number")
        chapters = cursor.fetchall()
        
        # Generate markdown outline
        outline = []
        outline.append(f"# {metadata[0] if metadata else 'Film Studies Textbook'}")
        outline.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
        
        if metadata:
            outline.append("## Textbook Specifications")
            outline.append(f"- **Subject:** {metadata[1]}")
            outline.append(f"- **Target Audience:** {metadata[2]}")
            outline.append(f"- **Academic Level:** {metadata[3]}")
            outline.append(f"- **Focus Areas:** {metadata[4]}")
            outline.append(f"- **Pedagogical Approach:** {metadata[5]}\n")
        
        outline.append("## Chapter Structure\n")
        
        for chapter in chapters:
            outline.append(f"### {chapter[1]}")
            if chapter[2]:  # overview
                outline.append(f"{chapter[2]}\n")
            
            if chapter[3]:  # learning objectives
                objectives = json.loads(chapter[3]) if chapter[3].startswith('[') else [chapter[3]]
                outline.append("**Learning Objectives:**")
                for obj in objectives:
                    outline.append(f"- {obj}")
                outline.append("")
            
            if chapter[4]:  # key concepts
                outline.append(f"**Key Concepts:** {chapter[4]}\n")
        
        # Write to file
        with open(filepath, 'w') as f:
            f.write('\n'.join(outline))
        
        print(f"📄 Textbook outline exported: {filename}")
        return filepath
    
    async def run(self):
        """Main execution flow"""
        print("🎓 LIZZY TEXTBOOK OUTLINE GENERATOR")
        print("="*50)
        
        # Initialize system
        await self.initialize_buckets()
        self.select_project()
        self.gather_textbook_requirements()
        
        # Generate components
        await self.generate_chapter_structure()
        await self.generate_concept_hierarchy()
        await self.generate_bibliography()
        
        # Export final outline
        outline_file = self.export_textbook_outline()
        
        print(f"\n✅ TEXTBOOK OUTLINE COMPLETE!")
        print(f"📁 Project: {self.project_name}")
        print(f"📄 Outline: {outline_file}")
        print(f"💾 Database: {os.path.join(self.project_dir, self.project_name, f'{self.project_name}.sqlite')}")
        
        print(f"\n🎯 NEXT STEPS:")
        print("1. Review the generated outline")
        print("2. Refine chapter content using the detailed database")
        print("3. Generate specific chapter content using Lizzy's write modules")
        print("4. Create exercises and assessments")

async def main():
    """Run the textbook outline generator"""
    generator = TextbookOutlineGenerator()
    await generator.run()

if __name__ == "__main__":
    asyncio.run(main())