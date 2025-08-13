"""
Enhanced Brainstorming Module for Lizzy Framework
Adapted from legacy A5_brainstorm.py to work with current system
Processes each scene individually with bucket-specific insights
"""

import os
import sqlite3
from datetime import datetime
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed

class EnhancedBrainstormAgent:
    def __init__(self, lightrag_instances=None, base_dir="exports"):
        """Initialize the brainstorming agent with LightRAG instances"""
        self.lightrag_instances = lightrag_instances or {}
        self.base_dir = base_dir
        self.project_name = None
        self.db_path = None
        self.conn = None
        
    def setup_lightrag_buckets(self, bucket_names):
        """Initialize LightRAG instances for selected buckets"""
        for bucket in bucket_names:
            if bucket not in self.lightrag_instances:
                working_dir = f"./lightrag_working_dir/{bucket}"
                os.makedirs(working_dir, exist_ok=True)
                self.lightrag_instances[bucket] = LightRAG(
                    working_dir=working_dir,
                    embedding_func=openai_embed,
                    llm_model_func=gpt_4o_mini_complete
                )
        print(f"✅ Initialized {len(bucket_names)} LightRAG buckets")
    
    def connect_to_project(self, project_path):
        """Connect to an existing project database"""
        self.project_name = os.path.basename(project_path)
        self.db_path = os.path.join(project_path, f"{self.project_name}.sqlite")
        
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        
        self.conn = sqlite3.connect(self.db_path)
        print(f"✅ Connected to project: {self.project_name}")
        self.setup_database()
    
    def setup_database(self):
        """Ensure brainstorming tables exist with proper schema"""
        cursor = self.conn.cursor()
        
        # Create enhanced brainstorming log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brainstorming_scenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                act INTEGER NOT NULL,
                scene INTEGER NOT NULL,
                scene_description TEXT NOT NULL,
                bucket_name TEXT NOT NULL,
                prompt_used TEXT NOT NULL,
                response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(act, scene, bucket_name)
            );
        ''')
        
        # Create summary table for full brainstorm sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brainstorming_sessions (
                session_id TEXT PRIMARY KEY,
                buckets_used TEXT NOT NULL,
                tables_used TEXT NOT NULL,
                user_guidance TEXT,
                total_scenes INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        self.conn.commit()
    
    def fetch_all_scenes(self):
        """Fetch all scenes from story_outline table"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT act, scene, key_characters, key_events 
            FROM story_outline 
            ORDER BY act, scene
        """)
        return cursor.fetchall()
    
    def fetch_scene_context(self, act, scene):
        """Build comprehensive context for a specific scene"""
        cursor = self.conn.cursor()
        context = {}
        
        # Get scene details
        cursor.execute("""
            SELECT key_characters, key_events 
            FROM story_outline 
            WHERE act = ? AND scene = ?
        """, (act, scene))
        result = cursor.fetchone()
        
        if not result:
            return None
        
        context['key_characters'] = result[0]
        context['key_events'] = result[1]
        
        # Get character details for those in this scene
        cursor.execute("""
            SELECT name, gender, age, romantic_challenge, lovable_trait, comedic_flaw 
            FROM characters
        """)
        all_chars = cursor.fetchall()
        
        # Filter to just characters in this scene
        scene_chars = []
        for char in all_chars:
            if char[0] in context['key_characters']:
                scene_chars.append({
                    'name': char[0],
                    'gender': char[1],
                    'age': char[2],
                    'romantic_challenge': char[3],
                    'lovable_trait': char[4],
                    'comedic_flaw': char[5]
                })
        
        context['characters'] = scene_chars
        
        # Get previous scene for continuity
        if scene > 1:
            cursor.execute("""
                SELECT key_events 
                FROM story_outline 
                WHERE act = ? AND scene = ?
            """, (act, scene - 1))
            prev = cursor.fetchone()
            context['previous_scene'] = prev[0] if prev else None
        
        return context
    
    def create_bucket_prompt(self, bucket_name, scene_context, act, scene, user_guidance=""):
        """Create specialized prompts for each bucket type"""
        
        base_context = f"""
        Act {act}, Scene {scene}
        
        Key Characters: {scene_context['key_characters']}
        Key Events: {scene_context['key_events']}
        
        Character Details:
        {self._format_characters(scene_context['characters'])}
        """
        
        if scene_context.get('previous_scene'):
            base_context += f"\n\nPrevious Scene: {scene_context['previous_scene']}"
        
        if user_guidance:
            base_context += f"\n\nUser Guidance: {user_guidance}"
        
        prompts = {
            "books": f"""
            You are an expert on screenwriting theory and structure.
            
            ### Scene Context:
            {base_context}
            
            ### Task:
            Analyze this scene through the lens of classic three-act structure and screenwriting principles.
            Provide insights on:
            - How this scene should advance the overall narrative arc
            - Character development opportunities
            - Pacing and tension building
            - Thematic resonance
            - Setup and payoff opportunities
            
            Focus on craft and technique from established screenwriting methodology.
            """,
            
            "scripts": f"""
            You are an expert in romantic comedy screenplays.
            
            ### Scene Context:
            {base_context}
            
            ### Task:
            Compare this scene to similar moments in successful romantic comedies.
            Provide insights on:
            - Effective romantic comedy tropes that could enhance this scene
            - Dialogue techniques that balance humor and heart
            - Physical comedy opportunities
            - Romantic tension building
            - Comedic timing and rhythm
            
            Reference specific examples from successful romcom scripts where applicable.
            """,
            
            "plays": f"""
            You are an expert in dramatic structure and theatrical storytelling.
            
            ### Scene Context:
            {base_context}
            
            ### Task:
            Analyze this scene through a theatrical/dramatic lens.
            Provide insights on:
            - Character dynamics and power shifts
            - Subtext and dramatic irony opportunities
            - Heightened language and memorable exchanges
            - Theatrical moments and visual storytelling
            - Emotional truth and authenticity
            
            Draw from classical and contemporary theatrical techniques.
            """,
            
            # Add more bucket types as needed
            "examples": f"""
            You are an expert in analyzing successful screenplay examples.
            
            ### Scene Context:
            {base_context}
            
            ### Task:
            Provide specific examples of how similar scenes have been executed successfully.
            Include:
            - Concrete scene structures that work
            - Dialogue patterns and techniques
            - Visual storytelling methods
            - Transition techniques
            - Memorable moments and why they work
            """
        }
        
        return prompts.get(bucket_name, prompts["scripts"])  # Default to scripts
    
    def _format_characters(self, characters):
        """Format character details for prompt"""
        if not characters:
            return "No character details available"
        
        formatted = []
        for char in characters:
            formatted.append(
                f"- {char['name']} ({char['gender']}, {char['age']}): "
                f"Challenge: {char['romantic_challenge']}, "
                f"Lovable: {char['lovable_trait']}, "
                f"Flaw: {char['comedic_flaw']}"
            )
        return "\n".join(formatted)
    
    def query_bucket(self, bucket_name, prompt):
        """Query a specific LightRAG bucket"""
        if bucket_name not in self.lightrag_instances:
            print(f"⚠️ Bucket '{bucket_name}' not initialized")
            return "Bucket not available"
        
        try:
            rag = self.lightrag_instances[bucket_name]
            response = rag.query(prompt, param=QueryParam(mode="hybrid"))
            return response
        except Exception as e:
            print(f"❌ Error querying {bucket_name}: {e}")
            return f"Error: {str(e)}"
    
    def save_scene_brainstorm(self, act, scene, scene_desc, bucket_name, prompt, response):
        """Save brainstorming output for a specific scene and bucket"""
        cursor = self.conn.cursor()
        
        # Use INSERT OR REPLACE to handle duplicates
        cursor.execute("""
            INSERT OR REPLACE INTO brainstorming_scenes 
            (act, scene, scene_description, bucket_name, prompt_used, response, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (act, scene, scene_desc, bucket_name, prompt, response, datetime.now()))
        
        self.conn.commit()
    
    def brainstorm_single_scene(self, act, scene, buckets, user_guidance=""):
        """Brainstorm a single scene with all selected buckets"""
        print(f"\n🎬 Brainstorming Act {act}, Scene {scene}")
        
        context = self.fetch_scene_context(act, scene)
        if not context:
            print(f"❌ No context found for Act {act}, Scene {scene}")
            return None
        
        scene_desc = f"Characters: {context['key_characters']}\nEvents: {context['key_events']}"
        results = {}
        
        for bucket in buckets:
            print(f"  🔍 Querying {bucket} bucket...")
            prompt = self.create_bucket_prompt(bucket, context, act, scene, user_guidance)
            response = self.query_bucket(bucket, prompt)
            
            if response and response != "Bucket not available":
                self.save_scene_brainstorm(act, scene, scene_desc, bucket, prompt, response)
                results[bucket] = response
                print(f"    ✓ {bucket} insights saved")
            else:
                print(f"    ✗ {bucket} query failed")
        
        return results
    
    def brainstorm_all_scenes(self, buckets, tables=None, user_guidance=""):
        """Run comprehensive brainstorming for all scenes"""
        session_id = f"BS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"\n{'='*60}")
        print(f"COMPREHENSIVE SCENE BRAINSTORMING")
        print(f"Session ID: {session_id}")
        print(f"{'='*60}")
        
        # Get all scenes
        scenes = self.fetch_all_scenes()
        if not scenes:
            print("❌ No scenes found in story_outline")
            return
        
        print(f"📊 Found {len(scenes)} scenes to brainstorm")
        print(f"🧠 Using buckets: {', '.join(buckets)}")
        
        if user_guidance:
            print(f"📝 User guidance: {user_guidance}")
        
        print(f"{'-'*60}")
        
        # Save session info
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO brainstorming_sessions 
            (session_id, buckets_used, tables_used, user_guidance, total_scenes)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session_id, 
            ','.join(buckets),
            ','.join(tables) if tables else '',
            user_guidance,
            len(scenes)
        ))
        self.conn.commit()
        
        # Process each scene
        successful_scenes = 0
        failed_scenes = []
        
        for act, scene, chars, events in scenes:
            print(f"\n{'─'*40}")
            print(f"Processing Act {act}, Scene {scene}")
            print(f"  Characters: {chars}")
            print(f"  Events: {events[:100]}..." if len(events) > 100 else f"  Events: {events}")
            
            results = self.brainstorm_single_scene(act, scene, buckets, user_guidance)
            
            if results:
                successful_scenes += 1
                print(f"✅ Scene brainstorming complete")
            else:
                failed_scenes.append((act, scene))
                print(f"❌ Scene brainstorming failed")
        
        # Summary
        print(f"\n{'='*60}")
        print(f"BRAINSTORMING COMPLETE")
        print(f"{'='*60}")
        print(f"✅ Successful: {successful_scenes}/{len(scenes)} scenes")
        if failed_scenes:
            print(f"❌ Failed scenes: {failed_scenes}")
        print(f"📁 Session saved as: {session_id}")
        
        return session_id
    
    def get_brainstorm_insights(self, act, scene):
        """Retrieve all brainstorming insights for a specific scene"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT bucket_name, response 
            FROM brainstorming_scenes 
            WHERE act = ? AND scene = ?
            ORDER BY created_at DESC
        """, (act, scene))
        
        results = cursor.fetchall()
        insights = {}
        for bucket, response in results:
            insights[bucket] = response
        
        return insights
    
    def export_brainstorming_report(self, session_id=None):
        """Export brainstorming results to a formatted report"""
        cursor = self.conn.cursor()
        
        # Get latest session if not specified
        if not session_id:
            cursor.execute("""
                SELECT session_id FROM brainstorming_sessions 
                ORDER BY created_at DESC LIMIT 1
            """)
            result = cursor.fetchone()
            if result:
                session_id = result[0]
            else:
                print("No brainstorming sessions found")
                return
        
        # Create export directory
        export_dir = os.path.join(self.base_dir, self.project_name, "brainstorms")
        os.makedirs(export_dir, exist_ok=True)
        
        filename = os.path.join(export_dir, f"{session_id}_report.txt")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"BRAINSTORMING REPORT\n")
            f.write(f"{'='*60}\n")
            f.write(f"Project: {self.project_name}\n")
            f.write(f"Session: {session_id}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n\n")
            
            # Get all scenes with brainstorming
            cursor.execute("""
                SELECT DISTINCT act, scene, scene_description 
                FROM brainstorming_scenes 
                ORDER BY act, scene
            """)
            scenes = cursor.fetchall()
            
            for act, scene, desc in scenes:
                f.write(f"\nACT {act}, SCENE {scene}\n")
                f.write(f"{'-'*40}\n")
                f.write(f"{desc}\n\n")
                
                # Get all bucket insights for this scene
                insights = self.get_brainstorm_insights(act, scene)
                for bucket, response in insights.items():
                    f.write(f"[{bucket.upper()} INSIGHTS]\n")
                    f.write(f"{response}\n\n")
        
        print(f"✅ Report exported to: {filename}")
        return filename
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Standalone function for integration with existing Lizzy system
def run_enhanced_brainstorm(project_path, selected_buckets, user_guidance=""):
    """
    Run enhanced brainstorming for a Lizzy project
    
    Args:
        project_path: Path to the project directory
        selected_buckets: List of bucket names to use
        user_guidance: Optional user guidance text
    
    Returns:
        session_id: The brainstorming session ID
    """
    agent = EnhancedBrainstormAgent()
    
    try:
        # Setup
        agent.connect_to_project(project_path)
        agent.setup_lightrag_buckets(selected_buckets)
        
        # Run brainstorming
        session_id = agent.brainstorm_all_scenes(
            buckets=selected_buckets,
            user_guidance=user_guidance
        )
        
        # Export report
        agent.export_brainstorming_report(session_id)
        
        return session_id
        
    finally:
        agent.close()


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python enhanced_brainstorm.py <project_path> <bucket1,bucket2,...>")
        sys.exit(1)
    
    project_path = sys.argv[1]
    buckets = sys.argv[2].split(',')
    guidance = sys.argv[3] if len(sys.argv) > 3 else ""
    
    session_id = run_enhanced_brainstorm(project_path, buckets, guidance)
    print(f"\n✨ Brainstorming complete! Session: {session_id}")