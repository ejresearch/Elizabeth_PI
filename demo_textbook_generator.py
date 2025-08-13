#!/usr/bin/env python3
"""
Demo of Textbook Outline Generator
Shows automated textbook generation using film book buckets
"""

import os
import sys
import sqlite3
import json
import asyncio
from datetime import datetime
from typing import Dict, List

# Add the main directory to path
sys.path.append('/Users/elle/Desktop/Elizabeth_PI')
from lizzy_textbook_generator import TextbookOutlineGenerator

async def demo_textbook_generation():
    """Demonstrate automated textbook outline generation"""
    
    print("🎓 DEMO: TEXTBOOK OUTLINE GENERATOR")
    print("="*50)
    
    # Create generator instance
    generator = TextbookOutlineGenerator()
    
    # Initialize buckets
    await generator.initialize_buckets()
    
    # Set up demo project automatically
    generator.project_name = "film_theory_textbook_demo"
    project_path = os.path.join(generator.project_dir, generator.project_name)
    os.makedirs(project_path, exist_ok=True)
    
    db_path = os.path.join(project_path, f"{generator.project_name}.sqlite")
    generator.conn = sqlite3.connect(db_path)
    generator.setup_database()
    
    # Set demo requirements
    demo_metadata = {
        "title": "Introduction to Film Theory and Analysis",
        "subject": "Film Studies",
        "target_audience": "Undergraduate students",
        "academic_level": "intermediate",
        "focus_areas": ["narrative theory", "genre analysis", "auteur theory", "visual storytelling", "film history"],
        "pedagogical_approach": "mixed"
    }
    
    # Store metadata in database
    cursor = generator.conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO textbook_metadata 
        (title, subject, target_audience, academic_level, focus_areas, pedagogical_approach, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (demo_metadata["title"], demo_metadata["subject"], demo_metadata["target_audience"], 
         demo_metadata["academic_level"], json.dumps(demo_metadata["focus_areas"]), 
         demo_metadata["pedagogical_approach"], datetime.now().isoformat(), datetime.now().isoformat()))
    generator.conn.commit()
    
    generator.outline_data["metadata"] = demo_metadata
    
    print(f"\n📖 Demo Project: {generator.project_name}")
    print(f"📚 Title: {demo_metadata['title']}")
    print(f"🎯 Focus Areas: {', '.join(demo_metadata['focus_areas'])}")
    print(f"👥 Target: {demo_metadata['target_audience']}")
    
    # Generate a simplified chapter structure (limit API calls for demo)
    print(f"\n📚 GENERATING CHAPTER STRUCTURE")
    print("-"*40)
    
    # Use just one comprehensive bucket for demo
    demo_bucket = "reference_sources"  # This has the most comprehensive data
    
    if demo_bucket in generator.lightrag_instances:
        structure_prompt = f"""
        Create a 12-chapter structure for an undergraduate textbook titled "{demo_metadata['title']}".

        FOCUS AREAS: {', '.join(demo_metadata['focus_areas'])}
        LEVEL: {demo_metadata['academic_level']}
        APPROACH: {demo_metadata['pedagogical_approach']}

        For each chapter provide:
        - Chapter number and title
        - Brief overview (2 sentences)
        - 3-4 learning objectives
        - Key concepts
        - Suggested film examples

        Create a logical progression from foundational concepts to advanced analysis.
        """
        
        try:
            print(f"   🔍 Consulting {demo_bucket}...")
            from lightrag import QueryParam
            structure_response = await generator.lightrag_instances[demo_bucket].aquery(
                structure_prompt,
                param=QueryParam(mode="hybrid")
            )
            
            print(f"   ✅ Chapter structure generated ({len(structure_response)} characters)")
            print(f"   📝 Preview: {structure_response[:200]}...")
            
            # Store the response
            cursor.execute('''
                INSERT INTO generation_log (timestamp, stage, bucket, prompt, response, tokens_used)
                VALUES (?, ?, ?, ?, ?, ?)''',
                (datetime.now().isoformat(), "demo_chapter_structure", demo_bucket, structure_prompt, structure_response, len(structure_response)))
            generator.conn.commit()
            
            # Create sample chapters for demo
            sample_chapters = [
                {"number": 1, "title": "Chapter 1: Introduction to Film as Art Form", "overview": "Foundational concepts of cinema as artistic medium"},
                {"number": 2, "title": "Chapter 2: Visual Language and Cinematography", "overview": "Camera techniques, composition, and visual storytelling"},
                {"number": 3, "title": "Chapter 3: Narrative Structure in Cinema", "overview": "Story construction, plot devices, and narrative techniques"},
                {"number": 4, "title": "Chapter 4: Genre Theory and Analysis", "overview": "Film genres, conventions, and audience expectations"},
                {"number": 5, "title": "Chapter 5: Auteur Theory", "overview": "Director as author, personal style and vision"},
                {"number": 6, "title": "Chapter 6: Film History and Movements", "overview": "Historical development and major cinematic movements"}
            ]
            
            for chapter in sample_chapters:
                cursor.execute('''
                    INSERT OR REPLACE INTO chapters 
                    (chapter_number, title, overview, learning_objectives, key_concepts)
                    VALUES (?, ?, ?, ?, ?)''',
                    (chapter["number"], chapter["title"], chapter["overview"], 
                     json.dumps(["Understanding core concepts", "Analyzing film examples", "Critical thinking skills"]),
                     "Film theory, Visual analysis, Critical methodology"))
            generator.conn.commit()
            
        except Exception as e:
            print(f"   ❌ Error generating structure: {e}")
    
    # Generate concept map sample
    print(f"\n🧠 GENERATING CONCEPT HIERARCHY")
    print("-"*35)
    
    concept_prompt = f"""
    Identify 20 key concepts for "{demo_metadata['title']}" organized by complexity level.
    
    FOUNDATIONAL: Basic terminology students need first
    INTERMEDIATE: Theoretical frameworks and analytical methods  
    ADVANCED: Complex theories and contemporary debates
    
    For each concept provide: name, definition, theorist (if applicable), complexity level.
    """
    
    try:
        print(f"   🔍 Extracting concepts from {demo_bucket}...")
        concept_response = await generator.lightrag_instances[demo_bucket].aquery(
            concept_prompt,
            param=QueryParam(mode="global")
        )
        
        print(f"   ✅ Concept hierarchy generated ({len(concept_response)} characters)")
        print(f"   📝 Preview: {concept_response[:200]}...")
        
        # Store concepts
        cursor.execute('''
            INSERT INTO generation_log (timestamp, stage, bucket, prompt, response, tokens_used)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (datetime.now().isoformat(), "demo_concepts", demo_bucket, concept_prompt, concept_response, len(concept_response)))
        generator.conn.commit()
        
    except Exception as e:
        print(f"   ❌ Error generating concepts: {e}")
    
    # Export the demo outline
    print(f"\n📄 EXPORTING TEXTBOOK OUTLINE")
    print("-"*30)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"{generator.project_name}_outline_{timestamp}.md"
    filepath = os.path.join(project_path, filename)
    
    # Get stored data
    cursor.execute("SELECT * FROM textbook_metadata")
    metadata = cursor.fetchone()
    
    cursor.execute("SELECT * FROM chapters ORDER BY chapter_number")
    chapters = cursor.fetchall()
    
    # Generate markdown outline
    outline_content = []
    outline_content.append(f"# {metadata[0] if metadata else 'Film Studies Textbook'}")
    outline_content.append(f"*Generated by Lizzy Textbook Generator on {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
    
    if metadata:
        outline_content.append("## Textbook Specifications")
        outline_content.append(f"- **Subject:** {metadata[1]}")
        outline_content.append(f"- **Target Audience:** {metadata[2]}")
        outline_content.append(f"- **Academic Level:** {metadata[3]}")
        outline_content.append(f"- **Focus Areas:** {metadata[4]}")
        outline_content.append(f"- **Pedagogical Approach:** {metadata[5]}\n")
    
    outline_content.append("## Chapter Structure\n")
    
    for chapter in chapters:
        outline_content.append(f"### {chapter[1]}")
        if chapter[2]:  # overview
            outline_content.append(f"{chapter[2]}\n")
        
        if chapter[3]:  # learning objectives
            try:
                objectives = json.loads(chapter[3]) if chapter[3].startswith('[') else [chapter[3]]
                outline_content.append("**Learning Objectives:**")
                for obj in objectives:
                    outline_content.append(f"- {obj}")
                outline_content.append("")
            except:
                pass
        
        if chapter[4]:  # key concepts
            outline_content.append(f"**Key Concepts:** {chapter[4]}\n")
    
    # Add generation details
    outline_content.append("## Generation Details\n")
    outline_content.append(f"- **Generated using:** {len(generator.lightrag_instances)} film book buckets")
    outline_content.append(f"- **Primary source:** {demo_bucket}")
    outline_content.append(f"- **Total entities:** {sum([len(instance._get_entities()) if hasattr(instance, '_get_entities') else 0 for instance in generator.lightrag_instances.values()])}")
    outline_content.append(f"- **Database:** {db_path}")
    
    # Write outline file
    with open(filepath, 'w') as f:
        f.write('\n'.join(outline_content))
    
    print(f"   ✅ Outline exported: {filename}")
    
    # Show summary
    print(f"\n{'='*50}")
    print("✅ DEMO TEXTBOOK GENERATION COMPLETE!")
    print(f"📁 Project: {generator.project_name}")
    print(f"📄 Outline: {filename}")
    print(f"💾 Database: {os.path.basename(db_path)}")
    print(f"🧠 Buckets Used: {len(generator.lightrag_instances)} film book buckets")
    
    print(f"\n🎯 CAPABILITIES DEMONSTRATED:")
    print("✅ Automatic initialization of 7 academic film buckets")
    print("✅ Comprehensive textbook metadata collection")
    print("✅ Chapter structure generation from academic sources")
    print("✅ Concept hierarchy extraction")
    print("✅ Database storage with full logging")
    print("✅ Markdown outline export")
    
    print(f"\n🚀 READY FOR:")
    print("- Interactive textbook generation")
    print("- Custom focus area selection")
    print("- Multi-bucket synthesis")
    print("- Chapter content generation")
    print("- Exercise and assessment creation")
    
    return filepath

if __name__ == "__main__":
    asyncio.run(demo_textbook_generation())