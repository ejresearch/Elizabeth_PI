#!/usr/bin/env python3
"""
Academic Chapter Generator for LIZZY Framework
Adapted from nell_beta_3 academic system to work with LIZZY's textbook template
"""

import os
import sqlite3
from typing import Dict, List, Any
from datetime import datetime
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.rerank import cohere_rerank

class LizzyAcademicChapterGenerator:
    """
    Academic chapter generator adapted for LIZZY Framework:
    - Uses LIZZY's textbook template schema
    - Works with transferred academic buckets
    - Generates structured educational content
    - Saves to LIZZY project database
    """

    # College-level teaching guidelines
    CORE_WRITING_GUIDELINES = """
COLLEGE TEXTBOOK TEACHING GUIDELINES:

EDUCATIONAL DISCOVERY APPROACH:
• Identify the most important people, innovations, and developments from sources
• Explain WHY each topic matters to understanding cinema history
• Teach concepts by building from concrete examples to broader principles
• Help students see patterns and connections across the period

COLLEGE-LEVEL PEDAGOGY:
• Assume intelligent students who need context and explanation, not just facts
• Define technical terms and historical context clearly
• Use engaging examples that illustrate larger concepts
• Balance detail with accessibility - scholarly but not intimidating

TEACHING STRUCTURE:
• Start with concrete examples students can visualize
• Explain the significance and broader implications
• Connect individual innovations to industry-wide changes
• Show cause-and-effect relationships clearly

DISCOVERY PRINCIPLES:
1. FIND THE MOST IMPORTANT FIGURES: Who were the key innovators and decision-makers?
2. IDENTIFY BREAKTHROUGH MOMENTS: What innovations changed everything?
3. EXPLAIN TECHNOLOGICAL EVOLUTION: How did technical capabilities advance?
4. ANALYZE BUSINESS TRANSFORMATION: How did economic models evolve?
5. SHOW CULTURAL IMPACT: How did cinema change American society?

WRITING FOR COLLEGE STUDENTS:
• Use clear, engaging prose that maintains academic rigor
• Include specific dates, names, and technical details as learning anchors
• Explain complex concepts through familiar comparisons when helpful
• Ask implicit questions students might have and answer them
• Build knowledge progressively - each section prepares for the next

AVOID TEXTBOOK PITFALLS:
• Don't just list facts - explain their significance
• Don't assume prior knowledge - build understanding step by step
• Don't oversimplify - maintain intellectual rigor appropriate for college level
• Don't lose the human stories in technical or business details
"""

    # Chapter sections with learning objectives
    CHAPTER_SECTIONS = {
        "I": {
            "title": "The Scientific Dream of Living Pictures",
            "learning_objective": "Students will discover how scientific curiosity about motion became the foundation for a new art form and industry",
            "word_target": 1200,
            "key_questions": [
                "Who were the scientists and inventors experimenting with capturing motion?",
                "What technical breakthroughs made motion pictures possible?",
                "How did scientific experiments attract commercial investment?",
                "Why did Victorian society become fascinated with motion studies?"
            ]
        },
        "II": {
            "title": "The Race to Invent: Competing Visions",
            "learning_objective": "Students will understand how different inventors created competing technologies and business models for exhibiting motion pictures",
            "word_target": 1500,
            "key_questions": [
                "What were the key differences between Edison's and the Lumière brothers' approaches?",
                "How did technical capabilities shape early business models?",
                "Why did projection ultimately triumph over individual viewing devices?",
                "How did international competition drive innovation?"
            ]
        },
        "III": {
            "title": "From Science to Entertainment",
            "learning_objective": "Students will analyze how motion pictures evolved from scientific demonstrations to popular entertainment",
            "word_target": 1100,
            "key_questions": [
                "What types of films did early producers make and why?",
                "How did audience reactions shape content development?",
                "What role did existing entertainment venues play in cinema's growth?",
                "How did early films challenge social norms and values?"
            ]
        },
        "IV": {
            "title": "Edwin S. Porter and the Birth of American Storytelling",
            "learning_objective": "Students will examine how individual innovation created the foundation for narrative cinema",
            "word_target": 1600,
            "key_questions": [
                "Who was Edwin S. Porter and what made him significant?",
                "How did 'The Great Train Robbery' change American filmmaking?",
                "What technical innovations enabled more sophisticated storytelling?",
                "Why did narrative films prove more commercially successful?"
            ]
        },
        "V": {
            "title": "The Nickelodeon Revolution",
            "learning_objective": "Students will explore how technological accessibility and smart business models created America's first mass entertainment medium",
            "word_target": 1800,
            "key_questions": [
                "How did nickelodeons make movies accessible to working-class Americans?",
                "What business innovations made five-cent theaters profitable?",
                "How did immigrant entrepreneurs shape the industry?",
                "What was cinema's impact on urban social life?"
            ]
        }
    }

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.project_path = f"projects/{project_name}"
        self.db_path = f"{self.project_path}/{project_name}.sqlite"
        self.lightrag_path = "./lightrag_working_dir"
        
        # Initialize LightRAG instances for academic buckets
        self.lightrag_instances = {}
        self._init_lightrag_buckets()

    def _init_lightrag_buckets(self):
        """Initialize LightRAG instances for available academic buckets"""
        # Check for API key
        if not os.getenv('OPENAI_API_KEY'):
            print("Warning: OpenAI API key not found. Academic buckets will not be loaded.")
            return
            
        academic_buckets = [
            "bordwell_sources", "cook_sources", "cousins_sources",
            "dixon_foster_sources", "gomery_sources", "knight_sources",
            "balio_sources", "cultural_sources", "reference_sources",
            "american_cinema_series"
        ]
        
        for bucket in academic_buckets:
            bucket_path = os.path.join(self.lightrag_path, bucket)
            if os.path.exists(bucket_path):
                try:
                    # Create custom rerank function with correct model
                    def custom_cohere_rerank(query, documents, **kwargs):
                        from lightrag.rerank import cohere_rerank
                        return cohere_rerank(query, documents, model='rerank-english-v3.0', **kwargs)
                    
                    self.lightrag_instances[bucket] = LightRAG(
                        working_dir=bucket_path,
                        embedding_func=openai_embed,
                        llm_model_func=gpt_4o_mini_complete,
                        rerank_model_func=custom_cohere_rerank,
                    )
                    print(f"Loaded bucket: {bucket}")
                except Exception as e:
                    print(f"Warning: Could not load bucket {bucket}: {e}")

    def validate_project(self):
        """Validate project exists and has textbook template"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Project database not found: {self.db_path}")
        
        # Check if it's a textbook project
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM project_metadata WHERE key='template_type'")
        result = cursor.fetchone()
        conn.close()
        
        if not result or result[0] != 'textbook':
            raise ValueError(f"Project {self.project_name} is not a textbook template project")
        
        print(f"Validated textbook project: {self.project_name}")

    def setup_academic_tables(self):
        """Setup academic-specific tables in LIZZY database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Academic sections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS academic_sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_id INTEGER NOT NULL,
                section_number INTEGER NOT NULL,
                section_title TEXT NOT NULL,
                content TEXT NOT NULL,
                word_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chapter_id) REFERENCES chapters(id)
            )
        """)

        # Academic chapters table (extends the base chapters table)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS academic_chapters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_number INTEGER NOT NULL,
                chapter_title TEXT NOT NULL,
                full_content TEXT NOT NULL,
                total_words INTEGER,
                sections_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
        print("Academic tables setup complete")

    def generate_chapter(self, chapter_num: int = 1) -> Dict[str, Any]:
        """Generate complete academic chapter"""
        self.validate_project()
        self.setup_academic_tables()

        print(f"Generating Chapter {chapter_num}: The Birth of an Industry")
        
        sections_data = []
        total_words = 0

        for roman, section_info in self.CHAPTER_SECTIONS.items():
            print(f"Generating Section {roman}: {section_info['title']}")
            
            try:
                # Generate section content
                content = self._generate_section_content(roman, section_info)
                word_count = len(content.split())
                
                # Save section
                section_data = self._save_section(
                    chapter_num,
                    self._roman_to_number(roman),
                    section_info['title'],
                    content,
                    word_count
                )
                
                sections_data.append(section_data)
                total_words += word_count
                
                print(f"Section {roman} completed ({word_count:,} words)")
                
            except Exception as e:
                print(f"Error generating Section {roman}: {e}")
                continue

        # Assemble complete chapter
        complete_chapter = self._assemble_chapter(chapter_num, sections_data)
        
        # Save complete chapter
        chapter_id = self._save_complete_chapter(chapter_num, complete_chapter, len(sections_data))
        
        print(f"Chapter {chapter_num} completed: {total_words:,} words")
        
        return {
            "status": "success",
            "chapter_number": chapter_num,
            "content": complete_chapter,
            "total_words": total_words,
            "sections_generated": len(sections_data),
            "chapter_id": chapter_id
        }

    def _brainstorm_section_content(self, roman: str, section_info: Dict) -> str:
        """Brainstorm and research content for a section before writing"""
        learning_objective = section_info.get('learning_objective', '')
        key_questions = section_info.get('key_questions', [])
        
        # Build research/brainstorming prompt
        brainstorm_prompt = f"""
ACADEMIC CONTENT DISCOVERY AND RESEARCH PHASE

RESEARCH OBJECTIVE:
Discover and organize source material to support college-level teaching on: {section_info['title']}

LEARNING TARGET: {learning_objective}

DISCOVERY QUESTIONS TO RESEARCH:
{chr(10).join(f"• {q}" for q in key_questions)}

RESEARCH METHODOLOGY:
Your job is to DISCOVER and ORGANIZE the most important information from academic sources. Focus on:

1. KEY FIGURES AND INNOVATORS
   - Who were the most important people in this period?
   - What made them significant to cinema history?
   - What specific contributions did they make?

2. BREAKTHROUGH MOMENTS AND INNOVATIONS  
   - What were the major technological developments?
   - What business model innovations occurred?
   - What artistic/narrative breakthroughs happened?

3. CAUSE-AND-EFFECT RELATIONSHIPS
   - How did technical capabilities enable business opportunities?
   - How did competition drive innovation?
   - How did economic factors influence artistic development?

4. SPECIFIC EXAMPLES AND EVIDENCE
   - Concrete dates, names, and events students can anchor learning to
   - Primary source evidence and contemporary accounts
   - Technical specifications and business details

5. BROADER PATTERNS AND SIGNIFICANCE
   - How do these developments connect to larger industry changes?
   - What patterns would repeat in later periods?
   - Why does this matter for understanding cinema history?

RESEARCH OUTPUT FORMAT:
Organize findings into:
• Key People (with roles and significance)
• Major Innovations (technical, business, artistic)
• Important Events (with dates and context)
• Cause-Effect Relationships
• Primary Source Evidence
• Teaching Examples (concrete cases students can visualize)

ACADEMIC STANDARDS:
- Prioritize scholarly sources and verified historical information
- Include specific dates, names, and technical details
- Balance technical accuracy with accessibility
- Focus on developments that shaped the industry long-term
"""

        # Query academic buckets for research material
        research_responses = []
        primary_buckets = ["bordwell_sources", "cook_sources", "american_cinema_series"]
        
        for bucket_name in primary_buckets:
            if bucket_name in self.lightrag_instances:
                try:
                    response = self.lightrag_instances[bucket_name].query(
                        brainstorm_prompt, param=QueryParam(mode="mix")
                    )
                    research_responses.append(f"[Research from {bucket_name}]\n{response}")
                except Exception as e:
                    print(f"Warning: Error researching {bucket_name}: {e}")
        
        return "\n\n".join(research_responses) if research_responses else "No research data available."

    def _generate_section_content(self, roman: str, section_info: Dict) -> str:
        """Generate content for a specific section using LightRAG"""
        learning_objective = section_info.get('learning_objective', '')
        key_questions = section_info.get('key_questions', [])
        
        # First, brainstorm and research content
        research_material = self._brainstorm_section_content(roman, section_info)
        
        # Build educational prompt
        prompt = f"""
{self.CORE_WRITING_GUIDELINES}

TEACHING OBJECTIVE:
{learning_objective}

SECTION TO TEACH: {section_info['title']}
TARGET LENGTH: {section_info['word_target']} words

KEY QUESTIONS TO EXPLORE AND ANSWER:
{chr(10).join(f"• {q}" for q in key_questions)}

DISCOVERY APPROACH:
Your job is to DISCOVER and TEACH the most important topics from the available document sources. Help students understand:

1. WHO were the key figures and WHY do they matter to cinema history?
2. WHAT were the major innovations and breakthroughs?
3. HOW did technology and business evolve together?
4. WHERE did important developments happen and why?
5. WHEN did crucial changes occur and what caused them?

COLLEGE-LEVEL TEACHING STRATEGY:
• Start with engaging examples that students can visualize
• Explain the broader significance of each innovation or development
• Show cause-and-effect relationships clearly
• Define technical terms and provide historical context
• Use primary source evidence from documents to support your teaching
• Build toward understanding larger patterns and transformations

EDUCATIONAL CONTENT STRUCTURE:
• Begin with the most compelling or important development to grab attention
• Introduce key figures with enough background for students to understand their significance
• Explain technical innovations in accessible but accurate terms
• Show how business decisions shaped artistic and technical development
• Connect individual stories to industry-wide changes
• End by setting up the next phase of development

Remember: You're teaching college students who are intelligent but need guidance to understand the significance of developments in early cinema history. Help them discover why this period matters and how it shaped everything that followed.
"""

        # Query multiple academic buckets and combine results
        all_responses = []
        
        # Use most relevant buckets for cinema history
        primary_buckets = ["bordwell_sources", "cook_sources", "american_cinema_series"]
        
        for bucket_name in primary_buckets:
            if bucket_name in self.lightrag_instances:
                try:
                    response = self.lightrag_instances[bucket_name].query(
                        prompt, param=QueryParam(mode="mix")
                    )
                    all_responses.append(f"[From {bucket_name}]\n{response}")
                except Exception as e:
                    print(f"Warning: Error querying {bucket_name}: {e}")
        
        # Combine and synthesize responses
        if all_responses:
            combined_response = "\n\n".join(all_responses)
            
            # Create synthesis prompt
            synthesis_prompt = f"""
Based on the following research from multiple academic sources, write a cohesive {section_info['word_target']}-word section for college students on "{section_info['title']}".

TEACHING OBJECTIVE: {learning_objective}

RESEARCH SOURCES:
{combined_response}

Requirements:
• Synthesize information from all sources into a coherent narrative
• Maintain academic rigor while being accessible to college students
• Include specific examples, dates, and names as learning anchors
• Explain the significance of developments, not just facts
• Use engaging prose that maintains intellectual rigor
• Target approximately {section_info['word_target']} words

Focus on discovery and teaching - help students understand why this topic matters to cinema history.
"""
            
            # Use the first available bucket for synthesis
            if self.lightrag_instances:
                bucket_name = list(self.lightrag_instances.keys())[0]
                try:
                    final_content = self.lightrag_instances[bucket_name].query(
                        synthesis_prompt, param=QueryParam(mode="mix")
                    )
                    return final_content
                except Exception as e:
                    print(f"Error in synthesis: {e}")
                    return combined_response  # Fallback to combined response
        
        return "Content generation failed - no bucket responses available."

    def _save_section(self, chapter_num: int, section_num: int, title: str,
                     content: str, word_count: int) -> Dict[str, Any]:
        """Save section to LIZZY database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO academic_sections
            (chapter_id, section_number, section_title, content, word_count)
            VALUES (?, ?, ?, ?, ?)
        """, (chapter_num, section_num, title, content, word_count))

        conn.commit()
        conn.close()

        return {
            "section_number": section_num,
            "title": title,
            "word_count": word_count,
            "content": content
        }

    def _assemble_chapter(self, chapter_num: int, sections_data: List[Dict]) -> str:
        """Assemble complete chapter with educational framework"""
        header = f"""# Chapter {chapter_num}: The Birth of an Industry
## American Cinema from Invention to Hollywood's Rise (1890s–1915)

### For Students: What You'll Learn in This Chapter

This chapter tells the story of how motion pictures evolved from scientific experiments to America's dominant entertainment industry in just 25 years. You'll discover the key innovators, breakthrough technologies, and business strategies that created modern cinema.

**Essential Questions to Consider:**
- How did scientific curiosity about motion become a multi-million dollar industry?
- What role did competition and conflict play in shaping early cinema?
- How did technological innovations and business models evolve together?
- Why did Hollywood emerge as the center of American filmmaking?
- What patterns established in this period continue to influence entertainment today?

**Learning Framework:**
This chapter examines five key forces that drove cinema's development:
1. **Scientific Innovation** - How laboratory experiments became entertainment technology
2. **Business Competition** - How rival companies and strategies shaped the industry
3. **Cultural Transformation** - How cinema changed American social life
4. **Geographic Factors** - How location and resources influenced development
5. **Legal and Economic Forces** - How patents, monopolies, and government shaped the market

As you read, look for connections between technological capabilities, business opportunities, and cultural changes. Understanding these relationships will help you see how entertainment industries develop and evolve.

---

"""

        sections_content = []
        for section in sections_data:
            sections_content.append(f"## Section {section['section_number']}: {section['title']}\n\n{section['content']}")

        # Add educational conclusion
        conclusion = """

---

## Chapter Summary: Understanding the Transformation

### What Students Should Take Away

By 1915, American cinema had transformed completely:

**From Scientific Experiment to Mass Entertainment:**
- **1878**: Muybridge's motion studies amazed scientists and the public
- **1915**: Millions of Americans attended movies weekly in thousands of theaters

**From Individual Inventors to Corporate Industry:**
- **1890s**: Lone inventors like Edison and the Lumières experimented with motion pictures
- **1915**: Major studios with hundreds of employees controlled production and distribution

**From Technological Novelty to Cultural Force:**
- **1895**: Motion pictures were curiosities shown between vaudeville acts
- **1915**: Feature films competed with legitimate theater and influenced national culture

**From East Coast Laboratories to Hollywood Studios:**
- **1890s**: Experiments conducted in Edison's New Jersey laboratory
- **1915**: California had become the center of American film production

### Key Patterns That Continue Today

The developments you studied in this chapter established patterns that still influence entertainment:

- **Technology and Business Integration**: Technical innovations and commercial strategies continue to evolve together
- **Competition Drives Innovation**: Rivalry between companies still spurs creative and technical advancement
- **Geographic Concentration**: Entertainment industries still cluster in specific locations
- **Star Power**: Celebrity marketing remains central to entertainment economics
- **Global Reach**: American entertainment continues to dominate international markets

Understanding these foundational patterns helps explain how entertainment industries work today and how they might evolve in the future.

### Questions for Further Thought

1. How do the patterns of innovation and competition you studied compare to developments in today's streaming and digital entertainment?

2. What role did immigrant entrepreneurs play in early cinema, and how does this compare to entrepreneurship in today's tech industry?

3. How did early cinema's relationship with existing entertainment forms (vaudeville, theater) compare to how new media forms emerge today?

4. What can the rise and fall of the Motion Picture Patents Company teach us about monopolies in today's entertainment and technology industries?
"""

        return header + "\n\n".join(sections_content) + conclusion

    def _save_complete_chapter(self, chapter_num: int, content: str, section_count: int) -> str:
        """Save complete chapter to LIZZY database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        total_words = len(content.split())
        chapter_id = f"chapter_{chapter_num}_{int(datetime.now().timestamp())}"

        cursor.execute("""
            INSERT OR REPLACE INTO academic_chapters
            (chapter_number, chapter_title, full_content, total_words, sections_count)
            VALUES (?, ?, ?, ?, ?)
        """, (chapter_num, "The Birth of an Industry", content, total_words, section_count))

        conn.commit()
        conn.close()

        return chapter_id

    def _roman_to_number(self, roman: str) -> int:
        mapping = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8}
        return mapping.get(roman, 1)

def test_academic_generation():
    """Test academic chapter generation"""
    print("Testing LIZZY Academic Chapter Generation")
    
    # You would need a textbook project created first
    project_name = input("Enter textbook project name: ").strip()
    
    try:
        generator = LizzyAcademicChapterGenerator(project_name)
        result = generator.generate_chapter()
        
        if result['status'] == 'success':
            print(f"Generated {result['total_words']:,} words in {result['sections_generated']} sections")
            
            # Save markdown file
            output_path = f"projects/{project_name}/Chapter_1_Academic.md"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result['content'])
            print(f"Saved to: {output_path}")
        
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    test_academic_generation()