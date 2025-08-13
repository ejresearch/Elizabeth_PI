"""
Enhanced Writing Module for Lizzy Framework
Adapted from legacy A7_write.py and B_loopwrite.py
Generates full screenplay for all scenes with continuity and style
"""

import os
import sqlite3
import asyncio
from datetime import datetime
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed

class EnhancedWriteAgent:
    def __init__(self, lightrag_instances=None, base_dir="exports"):
        """Initialize the writing agent with LightRAG instances"""
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
        
        # Use WAL mode for better concurrency
        self.conn = sqlite3.connect(self.db_path, timeout=30)
        self.conn.execute("PRAGMA journal_mode = WAL;")
        print(f"✅ Connected to project: {self.project_name}")
        self.setup_database()
    
    def setup_database(self):
        """Ensure writing tables exist with proper schema"""
        cursor = self.conn.cursor()
        
        # Create table for individual scene drafts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scene_drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                act INTEGER NOT NULL,
                scene INTEGER NOT NULL,
                draft_version INTEGER DEFAULT 1,
                scene_text TEXT NOT NULL,
                word_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(act, scene, draft_version)
            );
        ''')
        
        # Create table for complete script versions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS complete_scripts (
                version_id TEXT PRIMARY KEY,
                total_scenes INTEGER,
                total_words INTEGER,
                buckets_used TEXT,
                user_guidance TEXT,
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
        
        # Get full character details
        cursor.execute("""
            SELECT name, gender, age, romantic_challenge, lovable_trait, comedic_flaw 
            FROM characters
        """)
        all_chars = cursor.fetchall()
        
        context['all_characters'] = {}
        for char in all_chars:
            context['all_characters'][char[0]] = {
                'gender': char[1],
                'age': char[2],
                'romantic_challenge': char[3],
                'lovable_trait': char[4],
                'comedic_flaw': char[5]
            }
        
        # Get scene-specific characters
        context['scene_characters'] = []
        for char_name in context['key_characters'].split(','):
            char_name = char_name.strip()
            if char_name in context['all_characters']:
                context['scene_characters'].append({
                    'name': char_name,
                    **context['all_characters'][char_name]
                })
        
        return context
    
    def fetch_previous_scene_text(self, act, scene):
        """Get the previously written scene for continuity"""
        cursor = self.conn.cursor()
        
        # First try to get from current session
        cursor.execute("""
            SELECT scene_text 
            FROM scene_drafts 
            WHERE (act = ? AND scene = ?) OR (act < ?) OR (act = ? AND scene < ?)
            ORDER BY act DESC, scene DESC 
            LIMIT 1
        """, (act, scene-1, act, act, scene))
        
        result = cursor.fetchone()
        return result[0] if result else None
    
    def fetch_brainstorming_insights(self, act, scene):
        """Get brainstorming insights if they exist"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT bucket_name, response 
            FROM brainstorming_scenes 
            WHERE act = ? AND scene = ?
        """, (act, scene))
        
        results = cursor.fetchall()
        insights = {}
        for bucket, response in results:
            insights[bucket] = response
        
        return insights
    
    async def query_bucket_for_writing(self, bucket_name, context, act, scene, user_guidance=""):
        """Query a bucket for writing suggestions"""
        if bucket_name not in self.lightrag_instances:
            return None
        
        prompt = self._create_writing_prompt(bucket_name, context, act, scene, user_guidance)
        
        try:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.lightrag_instances[bucket_name].query(
                    prompt, 
                    param=QueryParam(mode="hybrid")
                )
            )
            return result
        except Exception as e:
            print(f"  ⚠️ Error querying {bucket_name}: {e}")
            return None
    
    def _create_writing_prompt(self, bucket_name, context, act, scene, user_guidance):
        """Create bucket-specific writing prompts"""
        
        char_details = "\n".join([
            f"- {c['name']} ({c['gender']}, {c['age']}): "
            f"Challenge: {c['romantic_challenge']}, "
            f"Lovable: {c['lovable_trait']}, "
            f"Flaw: {c['comedic_flaw']}"
            for c in context['scene_characters']
        ])
        
        prompts = {
            "scripts": f"""
            As a romantic comedy expert, provide specific dialogue and scene structure for:
            
            Act {act}, Scene {scene}
            Events: {context['key_events']}
            Characters in scene: {char_details}
            
            Focus on:
            - Natural, witty dialogue with subtext
            - Physical comedy moments
            - Romantic tension beats
            - Scene transitions
            
            {f"User guidance: {user_guidance}" if user_guidance else ""}
            """,
            
            "books": f"""
            Using screenwriting theory, suggest narrative structure for:
            
            Act {act}, Scene {scene}
            Events: {context['key_events']}
            Characters: {char_details}
            
            Consider:
            - Story arc progression
            - Character development beats
            - Conflict escalation
            - Theme reinforcement
            
            {f"User guidance: {user_guidance}" if user_guidance else ""}
            """,
            
            "plays": f"""
            From a theatrical perspective, enhance:
            
            Act {act}, Scene {scene}
            Events: {context['key_events']}
            Characters: {char_details}
            
            Emphasize:
            - Dramatic moments and reversals
            - Subtext and unspoken tension
            - Stage-worthy dialogue
            - Emotional authenticity
            
            {f"User guidance: {user_guidance}" if user_guidance else ""}
            """
        }
        
        return prompts.get(bucket_name, prompts["scripts"])
    
    async def generate_scene_text(self, act, scene, context, buckets, user_guidance=""):
        """Generate the actual screenplay text for a scene"""
        
        # Get previous scene for continuity
        previous_scene = self.fetch_previous_scene_text(act, scene)
        
        # Get brainstorming insights if available
        brainstorm_insights = self.fetch_brainstorming_insights(act, scene)
        
        # Query buckets for writing suggestions
        bucket_suggestions = {}
        for bucket in buckets:
            suggestion = await self.query_bucket_for_writing(bucket, context, act, scene, user_guidance)
            if suggestion:
                bucket_suggestions[bucket] = suggestion
        
        # Build the final generation prompt
        final_prompt = await self._build_final_prompt(
            act, scene, context, 
            previous_scene, 
            brainstorm_insights, 
            bucket_suggestions,
            user_guidance
        )
        
        # Generate the scene
        scene_text = await gpt_4o_mini_complete(final_prompt)
        
        return scene_text
    
    async def _build_final_prompt(self, act, scene, context, previous_scene, 
                                  brainstorm_insights, bucket_suggestions, user_guidance):
        """Build the final prompt for scene generation"""
        
        prompt_parts = [
            "You are writing a Hollywood romantic comedy screenplay.",
            "Write in standard screenplay format with proper scene headings, action lines, and dialogue.",
            "",
            f"ACT {act}, SCENE {scene}",
            f"Key Events: {context['key_events']}",
            "",
            "CHARACTERS IN SCENE:",
        ]
        
        # Add character details
        for char in context['scene_characters']:
            prompt_parts.append(
                f"- {char['name'].upper()} ({char['age']}, {char['gender']}): "
                f"{char['romantic_challenge']}. "
                f"Lovable trait: {char['lovable_trait']}. "
                f"Comic flaw: {char['comedic_flaw']}."
            )
        
        # Add continuity from previous scene
        if previous_scene:
            # Extract last 500 chars for context
            continuity = previous_scene[-500:] if len(previous_scene) > 500 else previous_scene
            prompt_parts.extend([
                "",
                "PREVIOUS SCENE ENDING:",
                "..." + continuity if len(previous_scene) > 500 else continuity
            ])
        
        # Add brainstorming insights if available
        if brainstorm_insights:
            prompt_parts.extend(["", "CREATIVE INSIGHTS:"])
            for bucket, insight in brainstorm_insights.items():
                # Use first 200 chars of each insight
                snippet = insight[:200] + "..." if len(insight) > 200 else insight
                prompt_parts.append(f"[{bucket}]: {snippet}")
        
        # Add current bucket suggestions
        if bucket_suggestions:
            prompt_parts.extend(["", "STYLE GUIDANCE:"])
            for bucket, suggestion in bucket_suggestions.items():
                snippet = suggestion[:200] + "..." if len(suggestion) > 200 else suggestion
                prompt_parts.append(f"[{bucket}]: {snippet}")
        
        # Add user guidance
        if user_guidance:
            prompt_parts.extend(["", f"SPECIFIC REQUIREMENTS: {user_guidance}"])
        
        # Final instructions
        prompt_parts.extend([
            "",
            "Write a complete scene that:",
            "- Follows standard screenplay format",
            "- Captures genuine romantic comedy tone (think late 90s/early 2000s classics)",
            "- Features natural, witty dialogue",
            "- Maintains continuity with previous scenes",
            "- Advances both plot and character relationships",
            "- Balances humor with authentic emotion",
            "",
            "WRITE THE SCENE:"
        ])
        
        return "\n".join(prompt_parts)
    
    def save_scene_draft(self, act, scene, scene_text, version=1):
        """Save a scene draft to the database"""
        cursor = self.conn.cursor()
        
        word_count = len(scene_text.split())
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO scene_drafts 
                (act, scene, draft_version, scene_text, word_count)
                VALUES (?, ?, ?, ?, ?)
            """, (act, scene, version, scene_text, word_count))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"  ❌ Error saving scene: {e}")
            return False
    
    async def write_single_scene(self, act, scene, buckets, user_guidance=""):
        """Write a single scene"""
        print(f"\n📝 Writing Act {act}, Scene {scene}")
        
        context = self.fetch_scene_context(act, scene)
        if not context:
            print(f"  ❌ No context found")
            return None
        
        print(f"  Characters: {context['key_characters']}")
        print(f"  Events: {context['key_events'][:80]}...")
        
        # Generate the scene
        scene_text = await self.generate_scene_text(
            act, scene, context, buckets, user_guidance
        )
        
        if scene_text:
            # Save to database
            if self.save_scene_draft(act, scene, scene_text):
                word_count = len(scene_text.split())
                print(f"  ✅ Scene written ({word_count} words)")
                return scene_text
            else:
                print(f"  ⚠️ Scene generated but save failed")
                return scene_text
        else:
            print(f"  ❌ Scene generation failed")
            return None
    
    async def write_full_script(self, buckets, user_guidance="", continue_from=None):
        """Write the complete screenplay for all scenes"""
        version_id = f"SCRIPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"\n{'='*60}")
        print(f"FULL SCREENPLAY GENERATION")
        print(f"Version: {version_id}")
        print(f"{'='*60}")
        
        # Get all scenes
        scenes = self.fetch_all_scenes()
        if not scenes:
            print("❌ No scenes found in story_outline")
            return None
        
        # Filter if continuing from a specific scene
        if continue_from:
            act_from, scene_from = continue_from
            scenes = [(a, s, c, e) for a, s, c, e in scenes 
                     if a > act_from or (a == act_from and s >= scene_from)]
            print(f"📍 Continuing from Act {act_from}, Scene {scene_from}")
        
        print(f"📊 Writing {len(scenes)} scenes")
        print(f"🧠 Using buckets: {', '.join(buckets)}")
        
        if user_guidance:
            print(f"📝 User guidance: {user_guidance}")
        
        print(f"{'-'*60}")
        
        # Track progress
        successful_scenes = []
        failed_scenes = []
        total_words = 0
        
        # Process each scene
        for idx, (act, scene, chars, events) in enumerate(scenes, 1):
            print(f"\n[{idx}/{len(scenes)}] Act {act}, Scene {scene}")
            
            scene_text = await self.write_single_scene(act, scene, buckets, user_guidance)
            
            if scene_text:
                successful_scenes.append((act, scene))
                total_words += len(scene_text.split())
                
                # Show progress
                avg_words = total_words // len(successful_scenes)
                print(f"  📊 Progress: {len(successful_scenes)}/{len(scenes)} scenes, "
                      f"{total_words} total words (avg {avg_words}/scene)")
            else:
                failed_scenes.append((act, scene))
            
            # Small delay to avoid API rate limits
            await asyncio.sleep(1)
        
        # Save script metadata
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO complete_scripts 
            (version_id, total_scenes, total_words, buckets_used, user_guidance)
            VALUES (?, ?, ?, ?, ?)
        """, (
            version_id,
            len(successful_scenes),
            total_words,
            ','.join(buckets),
            user_guidance
        ))
        self.conn.commit()
        
        # Summary
        print(f"\n{'='*60}")
        print(f"SCREENPLAY GENERATION COMPLETE")
        print(f"{'='*60}")
        print(f"✅ Successful: {len(successful_scenes)}/{len(scenes)} scenes")
        print(f"📝 Total words: {total_words}")
        print(f"📊 Average words/scene: {total_words // len(successful_scenes) if successful_scenes else 0}")
        
        if failed_scenes:
            print(f"❌ Failed scenes: {failed_scenes}")
        
        print(f"💾 Version saved as: {version_id}")
        
        return version_id
    
    def export_screenplay(self, version_id=None, format="fountain"):
        """Export the screenplay to a file"""
        cursor = self.conn.cursor()
        
        # Get all scenes
        cursor.execute("""
            SELECT act, scene, scene_text 
            FROM scene_drafts 
            WHERE draft_version = 1
            ORDER BY act, scene
        """)
        scenes = cursor.fetchall()
        
        if not scenes:
            print("No scenes to export")
            return None
        
        # Create export directory
        export_dir = os.path.join(self.base_dir, self.project_name)
        os.makedirs(export_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "fountain":
            filename = os.path.join(export_dir, f"{self.project_name}_{timestamp}.fountain")
            with open(filename, 'w', encoding='utf-8') as f:
                # Fountain header
                f.write(f"Title: {self.project_name.replace('_', ' ').title()}\n")
                f.write(f"Credit: Written by\n")
                f.write(f"Author: Lizzy AI Framework\n")
                f.write(f"Draft date: {datetime.now().strftime('%B %d, %Y')}\n")
                f.write(f"Contact: Generated by Enhanced Lizzy System\n\n")
                
                # Write scenes
                current_act = 0
                for act, scene, text in scenes:
                    if act != current_act:
                        f.write(f"\n# ACT {act}\n\n")
                        current_act = act
                    
                    f.write(f"## Scene {scene}\n\n")
                    f.write(text)
                    f.write("\n\n")
        
        elif format == "pdf":
            # Would require additional library like reportlab
            filename = os.path.join(export_dir, f"{self.project_name}_{timestamp}.txt")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"SCREENPLAY: {self.project_name.upper()}\n")
                f.write(f"{'='*60}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*60}\n\n")
                
                for act, scene, text in scenes:
                    f.write(f"\nACT {act}, SCENE {scene}\n")
                    f.write(f"{'-'*40}\n\n")
                    f.write(text)
                    f.write("\n\n")
        
        else:  # Default text format
            filename = os.path.join(export_dir, f"{self.project_name}_{timestamp}.txt")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"SCREENPLAY: {self.project_name.upper()}\n")
                f.write(f"{'='*60}\n\n")
                
                for act, scene, text in scenes:
                    f.write(f"ACT {act}, SCENE {scene}\n")
                    f.write(f"{'-'*40}\n\n")
                    f.write(text)
                    f.write("\n\n" + "="*60 + "\n\n")
        
        print(f"✅ Screenplay exported to: {filename}")
        return filename
    
    def get_scene_statistics(self):
        """Get statistics about the written scenes"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_scenes,
                SUM(word_count) as total_words,
                AVG(word_count) as avg_words,
                MIN(word_count) as min_words,
                MAX(word_count) as max_words
            FROM scene_drafts
            WHERE draft_version = 1
        """)
        
        stats = cursor.fetchone()
        
        if stats and stats[0] > 0:
            return {
                'total_scenes': stats[0],
                'total_words': stats[1] or 0,
                'avg_words': int(stats[2]) if stats[2] else 0,
                'min_words': stats[3] or 0,
                'max_words': stats[4] or 0
            }
        
        return None
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Async wrapper for the main writing function
async def run_enhanced_write_async(project_path, selected_buckets, user_guidance="", continue_from=None):
    """
    Async function to run enhanced writing
    """
    agent = EnhancedWriteAgent()
    
    try:
        # Setup
        agent.connect_to_project(project_path)
        agent.setup_lightrag_buckets(selected_buckets)
        
        # Run writing
        version_id = await agent.write_full_script(
            buckets=selected_buckets,
            user_guidance=user_guidance,
            continue_from=continue_from
        )
        
        # Export screenplay
        if version_id:
            agent.export_screenplay(version_id)
            
            # Show statistics
            stats = agent.get_scene_statistics()
            if stats:
                print(f"\n📊 SCREENPLAY STATISTICS:")
                print(f"  Total scenes: {stats['total_scenes']}")
                print(f"  Total words: {stats['total_words']}")
                print(f"  Average words/scene: {stats['avg_words']}")
                print(f"  Shortest scene: {stats['min_words']} words")
                print(f"  Longest scene: {stats['max_words']} words")
        
        return version_id
        
    finally:
        agent.close()


# Synchronous wrapper for integration with existing Lizzy system
def run_enhanced_write(project_path, selected_buckets, user_guidance="", continue_from=None):
    """
    Run enhanced writing for a Lizzy project (synchronous wrapper)
    
    Args:
        project_path: Path to the project directory
        selected_buckets: List of bucket names to use
        user_guidance: Optional user guidance text
        continue_from: Optional tuple (act, scene) to continue from
    
    Returns:
        version_id: The script version ID
    """
    return asyncio.run(run_enhanced_write_async(
        project_path, selected_buckets, user_guidance, continue_from
    ))


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python enhanced_write.py <project_path> <bucket1,bucket2,...> [guidance] [continue_act,scene]")
        sys.exit(1)
    
    project_path = sys.argv[1]
    buckets = sys.argv[2].split(',')
    guidance = sys.argv[3] if len(sys.argv) > 3 else ""
    
    continue_from = None
    if len(sys.argv) > 4:
        parts = sys.argv[4].split(',')
        if len(parts) == 2:
            continue_from = (int(parts[0]), int(parts[1]))
    
    version_id = run_enhanced_write(project_path, buckets, guidance, continue_from)
    print(f"\n✨ Screenplay complete! Version: {version_id}")