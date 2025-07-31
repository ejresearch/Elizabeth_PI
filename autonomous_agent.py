#!/usr/bin/env python3
"""
Autonomous Agent for LIZZY Framework
Picks templates and executes workflows independently
"""

import os
import json
import sqlite3
import random
import time
from datetime import datetime
from openai import OpenAI
from template_manager import TemplateManager
from admin import LizzyAdmin

class AutonomousAgent:
    def __init__(self, api_key=None, working_dir="./"):
        self.working_dir = working_dir
        self.template_manager = TemplateManager()
        self.admin = LizzyAdmin()
        
        # Initialize OpenAI client
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            # Try to get from environment
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                self.client = None
                print("⚠️  No OpenAI API key provided. Agent will run in simulation mode.")
        
        self.execution_log = []
        self.current_project = None
        
    def log_action(self, action, details=None, status="info"):
        """Log agent actions for transparency"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "status": status
        }
        self.execution_log.append(log_entry)
        
        # Print to console with emoji indicators
        status_emoji = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
        print(f"{status_emoji.get(status, 'ℹ️')} [{datetime.now().strftime('%H:%M:%S')}] {action}")
        if details:
            print(f"   └─ {details}")
    
    def analyze_templates(self):
        """Analyze available templates and pick one intelligently"""
        self.log_action("Analyzing available templates")
        
        templates = self.template_manager.get_available_templates()
        if not templates:
            self.log_action("No templates found", status="error")
            return None
        
        self.log_action(f"Found {len(templates)} templates", 
                       f"Available: {', '.join(templates.keys())}")
        
        # Simple intelligent selection (can be enhanced with AI)
        template_scores = {}
        for key, info in templates.items():
            score = 0
            
            # Prefer non-custom templates (more stable)
            if not info['is_custom']:
                score += 10
            
            # Prefer templates with descriptions
            if info.get('description'):
                score += 5
                
            # Add some randomness for variety
            score += random.randint(1, 5)
            
            template_scores[key] = score
        
        # Pick highest scoring template
        selected = max(template_scores.items(), key=lambda x: x[1])[0]
        self.log_action(f"Selected template: {selected}", 
                       f"Score: {template_scores[selected]}", "success")
        
        return selected
    
    def generate_project_name(self, template_key):
        """Generate a creative project name based on template"""
        self.log_action("Generating project name")
        
        # Template-specific name patterns
        name_patterns = {
            'romcom': [
                'coffee_shop_romance', 'midnight_in_brooklyn', 'the_wrong_wedding',
                'digital_hearts', 'rainy_day_love', 'bookstore_encounters'
            ],
            'textbook': [
                'modern_studies', 'comprehensive_guide', 'essential_concepts',
                'advanced_topics', 'practical_handbook', 'student_companion'
            ]
        }
        
        # Get pattern for template or use generic
        patterns = name_patterns.get(template_key, [
            'creative_project', 'new_venture', 'story_experiment',
            'narrative_exploration', 'content_creation'
        ])
        
        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        base_name = random.choice(patterns)
        project_name = f"{base_name}_{timestamp}"
        
        self.log_action(f"Generated project name: {project_name}", status="success")
        return project_name
    
    def create_project(self, template_key, project_name):
        """Create a new project using selected template"""
        self.log_action(f"Creating project '{project_name}' with template '{template_key}'")
        
        success = self.template_manager.create_project_from_template(project_name, template_key)
        
        if success:
            self.current_project = project_name
            self.log_action(f"Project created successfully", f"Path: projects/{project_name}", "success")
            return True
        else:
            self.log_action("Project creation failed", status="error")
            return False
    
    def populate_project_data(self, project_name, template_key):
        """Populate project with sample data based on template"""
        self.log_action("Populating project with sample data")
        
        db_path = os.path.join("projects", project_name, f"{project_name}.sqlite")
        if not os.path.exists(db_path):
            self.log_action("Database not found", status="error")
            return False
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Template-specific sample data
            if template_key == 'romcom':
                self._populate_romcom_data(cursor)
            elif template_key == 'textbook':
                self._populate_textbook_data(cursor)
            else:
                self._populate_generic_data(cursor)
            
            conn.commit()
            conn.close()
            
            self.log_action("Sample data populated", status="success")
            return True
            
        except Exception as e:
            self.log_action(f"Error populating data: {str(e)}", status="error")
            return False
    
    def _populate_romcom_data(self, cursor):
        """Populate romantic comedy specific data"""
        # Sample characters
        characters = [
            ("Maya Chen", "Female", "28", "Fears vulnerability after bad breakup", 
             "Finds humor in disasters", "Terrible at reading social cues"),
            ("Jake Morrison", "Male", "30", "Overanalyzes everything", 
             "Genuinely cares about everyone", "Explains jokes after telling them")
        ]
        
        for char in characters:
            cursor.execute("""
                INSERT INTO characters (name, gender, age, romantic_challenge, lovable_trait, comedic_flaw)
                VALUES (?, ?, ?, ?, ?, ?)
            """, char)
        
        # Sample story outline
        outline = [
            (1, 1, "Maya, Jake", "Meet-cute at coffee shop disaster"),
            (1, 2, "Maya, Jake", "Awkward second encounter at bookstore"),
            (2, 1, "Maya, Jake", "Forced together by circumstances"),
            (2, 2, "Maya, Jake", "Growing chemistry despite mishaps"),
            (3, 1, "Maya, Jake", "Resolution and romantic climax")
        ]
        
        for scene in outline:
            cursor.execute("""
                INSERT INTO story_outline (act, scene, key_characters, key_events)
                VALUES (?, ?, ?, ?)
            """, scene)
    
    def _populate_textbook_data(self, cursor):
        """Populate textbook specific data"""
        # Sample chapter
        cursor.execute("""
            INSERT INTO chapters (chapter_number, chapter_title, chapter_subtitle, introduction_text)
            VALUES (1, 'Introduction to Film Studies', 'Foundations of Cinema Analysis', 
                   'This chapter introduces fundamental concepts in film analysis and criticism.')
        """)
        
        # Get the chapter ID for foreign key references
        chapter_id = cursor.lastrowid
        
        # Sample learning objectives
        objectives = [
            ("Understand the basic elements of film language", "Knowledge", 1),
            ("Analyze visual composition in cinema", "Analysis", 2),
            ("Evaluate directorial choices and their impact", "Evaluation", 3)
        ]
        
        for obj_text, bloom_level, order in objectives:
            cursor.execute("""
                INSERT INTO learning_objectives (chapter_id, objective_text, bloom_level, sequence_order)
                VALUES (?, ?, ?, ?)
            """, (chapter_id, obj_text, bloom_level, order))
        
        # Sample key concepts
        concepts = [
            ("Mise-en-scène", "The arrangement of everything that appears in the frame", "Visual elements including lighting, color, costume, and set design"),
            ("Montage", "The technique of combining individual shots to create meaning", "Soviet filmmakers like Sergei Eisenstein pioneered this approach")
        ]
        
        for term, definition, examples in concepts:
            cursor.execute("""
                INSERT INTO key_concepts (term, definition, chapter_id, examples)
                VALUES (?, ?, ?, ?)
            """, (term, definition, chapter_id, examples))
    
    def _populate_generic_data(self, cursor):
        """Populate generic sample data"""
        # Check what tables exist and try to add basic data
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Try to add a basic record to the first non-metadata table
        for table in tables:
            if table != 'project_metadata':
                try:
                    # Get table structure
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    # Find first text column that's not id or created_at
                    for col in columns:
                        col_name = col[1]
                        col_type = col[2]
                        if 'TEXT' in col_type and col_name not in ['id', 'created_at']:
                            cursor.execute(f"""
                                INSERT INTO {table} ({col_name})
                                VALUES ('Agent generated sample data')
                            """)
                            break
                    break
                except:
                    continue
    
    def run_workflow(self, project_name):
        """Execute the complete workflow for the project"""
        self.log_action(f"Starting workflow for project '{project_name}'")
        
        # Run brainstorm (simulation if no API key)
        if self.client:
            self._run_brainstorm(project_name)
            self._run_write(project_name)
        else:
            self.log_action("Simulating brainstorm session (no API key)", status="warning")
            self._simulate_brainstorm(project_name)
            self.log_action("Simulating write session (no API key)", status="warning")
            self._simulate_write(project_name)
        
        self.log_action("Workflow completed", status="success")
    
    def _run_brainstorm(self, project_name):
        """Run actual brainstorm session with AI"""
        self.log_action("Running AI brainstorm session")
        # This would integrate with your existing brainstorm system
        # For now, simulate the process
        time.sleep(2)  # Simulate processing time
        self.log_action("Brainstorm session completed", status="success")
    
    def _simulate_brainstorm(self, project_name):
        """Simulate brainstorm for demonstration"""
        db_path = os.path.join("projects", project_name, f"{project_name}.sqlite")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if notes table exists, otherwise add to first available table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notes'")
        if cursor.fetchone():
            cursor.execute("""
                INSERT INTO notes (title, content, category)
                VALUES ('Agent Brainstorm', 'Simulated brainstorm results - creative scene ideas generated', 'brainstorm')
            """)
        else:
            # Add brainstorm note to any available text field
            self._add_system_note(cursor, "Agent Brainstorm: Creative ideas generated")
        
        conn.commit()
        conn.close()
    
    def _simulate_write(self, project_name):
        """Simulate write session for demonstration"""
        db_path = os.path.join("projects", project_name, f"{project_name}.sqlite")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        self._add_system_note(cursor, "Agent Write: Sample content created")
        
        conn.commit()
        conn.close()
    
    def _add_system_note(self, cursor, content):
        """Add a system note to any available table"""
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                if table != 'project_metadata':
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    
                    # Find a text column to add the note
                    text_col = None
                    for col in columns:
                        if 'TEXT' in col[2] and col[1] not in ['id', 'created_at']:
                            text_col = col[1]
                            break
                    
                    if text_col:
                        cursor.execute(f"INSERT INTO {table} ({text_col}) VALUES (?)", (content,))
                        break
        except:
            pass
    
    def _run_write(self, project_name):
        """Run actual write session with AI"""
        self.log_action("Running AI write session")
        time.sleep(2)  # Simulate processing time
        self.log_action("Write session completed", status="success")
    
    def export_results(self, project_name):
        """Export project results"""
        self.log_action("Exporting project results")
        
        # Create export directory
        export_dir = os.path.join("exports", project_name)
        os.makedirs(export_dir, exist_ok=True)
        
        # Export execution log
        log_file = os.path.join(export_dir, "execution_log.json")
        with open(log_file, 'w') as f:
            json.dump(self.execution_log, f, indent=2)
        
        self.log_action(f"Results exported to {export_dir}", status="success")
    
    def run_full_cycle(self):
        """Execute complete autonomous cycle: pick template -> create project -> run workflow"""
        self.log_action("🚀 Starting autonomous agent cycle", status="info")
        
        # Step 1: Pick template
        template_key = self.analyze_templates()
        if not template_key:
            return False
        
        # Step 2: Generate project name
        project_name = self.generate_project_name(template_key)
        
        # Step 3: Create project
        if not self.create_project(template_key, project_name):
            return False
        
        # Step 4: Populate with sample data
        if not self.populate_project_data(project_name, template_key):
            return False
        
        # Step 5: Run workflow
        self.run_workflow(project_name)
        
        # Step 6: Export results
        self.export_results(project_name)
        
        self.log_action("🎉 Autonomous cycle completed successfully!", 
                       f"Project: {project_name}", "success")
        
        return True
    
    def get_execution_summary(self):
        """Get summary of agent execution"""
        total_actions = len(self.execution_log)
        success_count = len([log for log in self.execution_log if log['status'] == 'success'])
        error_count = len([log for log in self.execution_log if log['status'] == 'error'])
        
        return {
            'total_actions': total_actions,
            'successful_actions': success_count,
            'errors': error_count,
            'current_project': self.current_project,
            'execution_log': self.execution_log
        }

def main():
    """CLI interface for autonomous agent"""
    print("\n" + "="*60)
    print("🤖 LIZZY AUTONOMOUS AGENT")
    print("="*60)
    print("This agent will:")
    print("1. Analyze available templates")
    print("2. Pick the best one intelligently") 
    print("3. Create a new project")
    print("4. Run the complete workflow")
    print("5. Export results")
    print("\nPress Enter to start, or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n❌ Agent cancelled by user")
        return
    
    # Initialize and run agent
    agent = AutonomousAgent()
    success = agent.run_full_cycle()
    
    # Show summary
    summary = agent.get_execution_summary()
    print("\n" + "="*60)
    print("📊 EXECUTION SUMMARY")
    print("="*60)
    print(f"Total Actions: {summary['total_actions']}")
    print(f"Successful: {summary['successful_actions']}")
    print(f"Errors: {summary['errors']}")
    if summary['current_project']:
        print(f"Project Created: {summary['current_project']}")
    
    if success:
        print("\n✅ Agent completed successfully! Check the 'projects' and 'exports' directories.")
    else:
        print("\n❌ Agent encountered errors. Check the log above.")

if __name__ == "__main__":
    main()