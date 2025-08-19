"""
Transparent Writing Module for Lizzy
Provides step-by-step visibility into screenplay generation process
"""

import os
import json
import sqlite3
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from core_templates import TemplateManager, PromptInspector
from core_knowledge import LightRAGManager
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed


@dataclass
class WriteStep:
    """Represents a single step in the writing process"""
    step_id: str
    step_type: str  # "context", "brainstorm_fetch", "bucket_query", "prompt_compile", "generation", "scene_complete"
    timestamp: datetime
    act: int
    scene: int
    content: Any
    metadata: Dict = None


@dataclass
class WriteContext:
    """Context for writing a scene"""
    act: int
    scene: int
    scene_description: str
    key_events: str
    character_details: List[Dict]
    previous_scene_text: str
    brainstorm_insights: Dict[str, str]
    user_guidance: str
    active_buckets: List[str]


class TransparentWriter:
    """Transparent screenplay writing engine with full visibility"""
    
    def __init__(self, project_path: str, template_manager: TemplateManager = None, 
                 lightrag_manager: LightRAGManager = None):
        self.project_path = project_path
        self.project_name = os.path.basename(project_path)
        self.db_path = os.path.join(project_path, f"{self.project_name}.sqlite")
        
        # Initialize managers
        self.template_manager = template_manager or TemplateManager()
        self.lightrag_manager = lightrag_manager or LightRAGManager()
        self.prompt_inspector = PromptInspector(self.template_manager)
        
        # Connect to database
        self.conn = sqlite3.connect(self.db_path)
        self.setup_tracking_tables()
        
        # Session tracking
        self.current_session = None
        self.steps_log = []
        self.callbacks = {
            'session_started': [],
            'scene_started': [],
            'context_assembled': [],
            'brainstorm_fetched': [],
            'bucket_queried': [],
            'prompt_compiled': [],
            'generation_started': [],
            'scene_generated': [],
            'scene_saved': [],
            'session_completed': [],
            'step_completed': []
        }
    
    def setup_tracking_tables(self):
        """Setup tables for tracking writing sessions"""
        cursor = self.conn.cursor()
        
        # Writing sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS write_sessions (
                session_id TEXT PRIMARY KEY,
                project_name TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                total_scenes INTEGER,
                successful_scenes INTEGER,
                buckets_used TEXT,
                user_guidance TEXT,
                status TEXT DEFAULT 'running'
            )
        ''')
        
        # Writing steps table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS write_steps (
                step_id TEXT PRIMARY KEY,
                session_id TEXT,
                step_type TEXT,
                timestamp TIMESTAMP,
                act INTEGER,
                scene INTEGER,
                content TEXT,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES write_sessions (session_id)
            )
        ''')
        
        # Scene generations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scene_generations (
                generation_id TEXT PRIMARY KEY,
                session_id TEXT,
                act INTEGER,
                scene INTEGER,
                context_used TEXT,
                prompt_used TEXT,
                generated_text TEXT,
                word_count INTEGER,
                timestamp TIMESTAMP,
                success BOOLEAN,
                FOREIGN KEY (session_id) REFERENCES write_sessions (session_id)
            )
        ''')
        
        # Final scenes table (enhanced)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS final_scenes (
                scene_id TEXT PRIMARY KEY,
                session_id TEXT,
                act INTEGER,
                scene INTEGER,
                scene_text TEXT,
                word_count INTEGER,
                character_count INTEGER,
                timestamp TIMESTAMP,
                version INTEGER DEFAULT 1,
                FOREIGN KEY (session_id) REFERENCES write_sessions (session_id)
            )
        ''')
        
        self.conn.commit()
    
    def register_callback(self, event: str, callback: Callable):
        """Register a callback for specific events"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def trigger_callback(self, event: str, data: Any):
        """Trigger all callbacks for an event"""
        for callback in self.callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                print(f"Callback error: {e}")
    
    def start_session(self, buckets: List[str], user_guidance: str = "") -> str:
        """Start a new writing session"""
        session_id = f"WS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = {
            "session_id": session_id,
            "start_time": datetime.now(),
            "buckets": buckets,
            "user_guidance": user_guidance,
            "scenes_written": 0,
            "total_words": 0,
            "status": "running"
        }
        
        # Save session to database
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO write_sessions 
            (session_id, project_name, start_time, buckets_used, user_guidance)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, self.project_name, datetime.now(), 
              ','.join(buckets), user_guidance))
        self.conn.commit()
        
        self.steps_log = []
        
        self.trigger_callback('session_started', {
            'session_id': session_id,
            'buckets': buckets,
            'user_guidance': user_guidance
        })
        
        return session_id
    
    def log_step(self, step: WriteStep):
        """Log a writing step"""
        self.steps_log.append(step)
        
        # Save to database
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO write_steps 
            (step_id, session_id, step_type, timestamp, act, scene, content, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            step.step_id,
            self.current_session["session_id"],
            step.step_type,
            step.timestamp,
            step.act,
            step.scene,
            json.dumps(step.content) if not isinstance(step.content, str) else step.content,
            json.dumps(step.metadata or {})
        ))
        self.conn.commit()
        
        self.trigger_callback('step_completed', {
            'step': step,
            'total_steps': len(self.steps_log)
        })
    
    def assemble_write_context(self, act: int, scene: int) -> WriteContext:
        """Assemble comprehensive context for writing a scene"""
        step_id = f"context_{act}_{scene}_{datetime.now().strftime('%H%M%S')}"
        
        cursor = self.conn.cursor()
        
        # Get scene outline
        cursor.execute('''
            SELECT key_characters, key_events 
            FROM story_outline 
            WHERE act = ? AND scene = ?
        ''', (act, scene))
        scene_data = cursor.fetchone()
        
        if not scene_data:
            raise ValueError(f"Scene not found: Act {act}, Scene {scene}")
        
        key_characters, key_events = scene_data
        scene_description = f"Characters: {key_characters}\nEvents: {key_events}"
        
        # Get character details
        cursor.execute('''
            SELECT name, gender, age, romantic_challenge, lovable_trait, comedic_flaw 
            FROM characters
        ''')
        all_chars = cursor.fetchall()
        
        character_details = []
        scene_chars = key_characters.split(',') if key_characters else []
        
        for char_data in all_chars:
            if any(char_data[0].strip() == sc.strip() for sc in scene_chars):
                character_details.append({
                    'name': char_data[0],
                    'gender': char_data[1],
                    'age': char_data[2],
                    'romantic_challenge': char_data[3],
                    'lovable_trait': char_data[4],
                    'comedic_flaw': char_data[5]
                })
        
        # Get previous scene text for continuity
        previous_scene_text = self.get_previous_scene_text(act, scene)
        
        # Get brainstorming insights if available
        brainstorm_insights = self.fetch_brainstorm_insights(act, scene)
        
        context = WriteContext(
            act=act,
            scene=scene,
            scene_description=scene_description,
            key_events=key_events,
            character_details=character_details,
            previous_scene_text=previous_scene_text,
            brainstorm_insights=brainstorm_insights,
            user_guidance=self.current_session.get("user_guidance", ""),
            active_buckets=self.current_session["buckets"]
        )
        
        # Log context assembly
        step = WriteStep(
            step_id=step_id,
            step_type="context",
            timestamp=datetime.now(),
            act=act,
            scene=scene,
            content=context.__dict__,
            metadata={"characters_count": len(character_details)}
        )
        self.log_step(step)
        
        self.trigger_callback('context_assembled', {
            'context': context,
            'step_id': step_id
        })
        
        return context
    
    def get_previous_scene_text(self, act: int, scene: int) -> str:
        """Get the text of the previous scene for continuity"""
        cursor = self.conn.cursor()
        
        # Try to get from current session first
        cursor.execute('''
            SELECT scene_text 
            FROM final_scenes 
            WHERE session_id = ? AND ((act = ? AND scene < ?) OR act < ?)
            ORDER BY act DESC, scene DESC 
            LIMIT 1
        ''', (self.current_session["session_id"], act, scene, act))
        
        result = cursor.fetchone()
        if result:
            return result[0]
        
        # Fallback to any previous scene
        cursor.execute('''
            SELECT scene_text 
            FROM final_scenes 
            WHERE (act = ? AND scene < ?) OR act < ?
            ORDER BY act DESC, scene DESC 
            LIMIT 1
        ''', (act, scene, act))
        
        result = cursor.fetchone()
        return result[0] if result else ""
    
    def fetch_brainstorm_insights(self, act: int, scene: int) -> Dict[str, str]:
        """Fetch brainstorming insights for this scene"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT bucket, response 
            FROM brainstorm_outputs 
            WHERE act = ? AND scene = ?
            ORDER BY timestamp DESC
        ''', (act, scene))
        
        insights = {}
        for bucket, response in cursor.fetchall():
            insights[bucket] = response
        
        if insights:
            step_id = f"brainstorm_fetch_{act}_{scene}_{datetime.now().strftime('%H%M%S')}"
            step = WriteStep(
                step_id=step_id,
                step_type="brainstorm_fetch",
                timestamp=datetime.now(),
                act=act,
                scene=scene,
                content=insights,
                metadata={"buckets_found": len(insights)}
            )
            self.log_step(step)
            
            self.trigger_callback('brainstorm_fetched', {
                'insights': insights,
                'buckets_found': len(insights),
                'step_id': step_id
            })
        
        return insights
    
    async def query_buckets_for_writing(self, context: WriteContext) -> Dict[str, str]:
        """Query LightRAG buckets for writing-specific suggestions"""
        suggestions = {}
        
        for bucket in context.active_buckets:
            step_id = f"bucket_query_{bucket}_{context.act}_{context.scene}_{datetime.now().strftime('%H%M%S')}"
            
            # Create writing-specific prompt
            query_prompt = self.create_writing_query_prompt(bucket, context)
            
            self.trigger_callback('bucket_queried', {
                'bucket': bucket,
                'query_prompt': query_prompt[:200] + "...",
                'step_id': step_id
            })
            
            try:
                result = self.lightrag_manager.query_bucket(bucket, query_prompt)
                
                if "error" not in result:
                    suggestions[bucket] = result.get("response", "")
                    
                    # Log successful query
                    step = WriteStep(
                        step_id=step_id,
                        step_type="bucket_query",
                        timestamp=datetime.now(),
                        act=context.act,
                        scene=context.scene,
                        content=result.get("response", ""),
                        metadata={"bucket": bucket, "success": True}
                    )
                    self.log_step(step)
                else:
                    # Log failed query
                    step = WriteStep(
                        step_id=step_id,
                        step_type="bucket_query",
                        timestamp=datetime.now(),
                        act=context.act,
                        scene=context.scene,
                        content=f"Error: {result.get('error', 'Unknown error')}",
                        metadata={"bucket": bucket, "success": False}
                    )
                    self.log_step(step)
            
            except Exception as e:
                step = WriteStep(
                    step_id=step_id,
                    step_type="bucket_query",
                    timestamp=datetime.now(),
                    act=context.act,
                    scene=context.scene,
                    content=f"Exception: {str(e)}",
                    metadata={"bucket": bucket, "success": False}
                )
                self.log_step(step)
            
            # Small delay between queries
            await asyncio.sleep(0.3)
        
        return suggestions
    
    def create_writing_query_prompt(self, bucket: str, context: WriteContext) -> str:
        """Create bucket-specific writing query"""
        char_list = ", ".join([char['name'] for char in context.character_details])
        
        prompts = {
            "scripts": f"""
            Provide specific writing guidance for a romantic comedy scene:
            
            Scene: Act {context.act}, Scene {context.scene}
            Events: {context.key_events}
            Characters: {char_list}
            
            Focus on:
            - Dialogue techniques and comedic timing
            - Physical comedy opportunities
            - Romantic tension building
            - Scene pacing and structure
            """,
            
            "books": f"""
            Apply screenwriting theory to guide this scene:
            
            Scene: Act {context.act}, Scene {context.scene}
            Events: {context.key_events}
            Characters: {char_list}
            
            Consider:
            - Three-act structure positioning
            - Character arc development
            - Conflict escalation
            - Theme reinforcement
            """,
            
            "plays": f"""
            Enhance this scene with theatrical techniques:
            
            Scene: Act {context.act}, Scene {context.scene}
            Events: {context.key_events}
            Characters: {char_list}
            
            Emphasize:
            - Dramatic moments and reversals
            - Subtext and tension
            - Visual storytelling
            - Emotional authenticity
            """
        }
        
        return prompts.get(bucket, prompts["scripts"])
    
    def compile_final_prompt(self, context: WriteContext, bucket_suggestions: Dict[str, str]) -> str:
        """Compile the enhanced Write Tab prompt with full Lizzy specification"""
        step_id = f"prompt_compile_{context.act}_{context.scene}_{datetime.now().strftime('%H%M%S')}"
        
        # Format character details  
        char_details = []
        for char in context.character_details:
            char_details.append(
                f"{char['name'].upper()} ({char['age']}, {char['gender']}): "
                f"Romantic challenge: {char['romantic_challenge']}. "
                f"Lovable trait: {char['lovable_trait']}. "
                f"Comic flaw: {char['comedic_flaw']}."
            )
        
        # Format previous scene continuity
        prev_scene_text = ""
        if context.previous_scene_text:
            continuity_excerpt = context.previous_scene_text[-400:] if len(context.previous_scene_text) > 400 else context.previous_scene_text
            prev_scene_text = "..." + continuity_excerpt if len(context.previous_scene_text) > 400 else continuity_excerpt
        
        # Format brainstorming insights
        brainstorming_results = ""
        if context.brainstorm_insights:
            brainstorm_parts = []
            for bucket, insight in context.brainstorm_insights.items():
                snippet = insight[:250] + "..." if len(insight) > 250 else insight
                brainstorm_parts.append(f"[{bucket}]: {snippet}")
            brainstorming_results = "\n".join(brainstorm_parts)
        
        # Format reference insights (bucket suggestions)
        reference_insights = ""
        if bucket_suggestions:
            insight_parts = []
            for bucket, suggestion in bucket_suggestions.items():
                bucket_tag = f"[{bucket.title()}]"
                snippet = suggestion[:250] + "..." if len(suggestion) > 250 else suggestion
                insight_parts.append(f"{bucket_tag} {snippet}")
            reference_insights = "\n".join(insight_parts)
        
        # Enhanced Lizzy prompt with full specification
        final_prompt = f"""# Writing a Screenplay with Lizzy

## General Instructions
You are **Lizzy**, an expert screenwriter specializing in romantic comedies. Your mission: revitalize the lost art of the rom-com — creating scripts that feel magnetic, romantic, and warm; timeless, witty, and emotionally resonant — while steering clear of formulaic, overproduced content.

Romantic comedies flourished in the 1990s and early 2000s, blending sharp writing, authentic chemistry, and high-stakes emotional arcs. We will return to that craft, balancing humor, sincerity, and romantic tension.

## Dataset Access
- **Pinnacle Romantic Comedies** – tone & pacing
- **The Complete Works of William Shakespeare** – plot frameworks & thematic depth  
- **Essential Screenwriting Craft Guides** – structure & dialogue mastery

## Data Sources & Authority (Read Carefully)
- **SQL is the source of truth** for plot, characters, locations, and continuity. If LightRAG ideas conflict with SQL, **follow SQL**.
- If SQL lacks a detail that is necessary to write the scene, state a single brief **ASSUMPTION:** line in action (max 10 words) and keep it consistent thereafter.
- Do **not** add new named characters unless the outline requires it. If unavoidable, label as **NEW CHARACTER** with minimal footprint.

## Scene Context
SCENE TO WRITE:
Act {context.act}, Scene {context.scene}

REQUIRED EVENTS:
{context.key_events}

CHARACTERS IN SCENE:
{chr(10).join(char_details)}

CONTINUITY FROM PREVIOUS SCENE:
{prev_scene_text}

BRAINSTORMING INSIGHTS:
{brainstorming_results}

WRITING GUIDANCE (from LightRAG Reference Insights):
{reference_insights}

SPECIFIC REQUIREMENTS (from user):
{context.user_guidance}

## Writing Requirements
- Standard Hollywood screenplay format (scene headings, action, dialogue).
- Natural, witty dialogue with subtext; show, don't explain.
- Visual storytelling and purposeful character action.
- Balance humor with genuine emotion.
- Maintain continuity with prior scenes and character positioning.
- Advance both plot and relationships.
- Avoid clichés, corporate formulas, and flat exposition.

## Writing Style Guidelines
- Clarity & brevity; active voice; concrete detail.
- No stock phrases, overused words, or filler meta-speech.
- Keep action lines lean; dialogue feels unscripted.
- Use subtext over exposition; preserve distinct character voices.

## Conflict Resolution Rules
- If **RAG** contradicts **SQL** → follow **SQL**.
- If **user guidance** contradicts RAG or style presets → follow **user guidance** unless it breaks SQL continuity.

WRITE THE COMPLETE SCENE NOW:"""
        
        # Log prompt compilation
        step = WriteStep(
            step_id=step_id,
            step_type="prompt_compile",
            timestamp=datetime.now(),
            act=context.act,
            scene=context.scene,
            content=final_prompt,
            metadata={
                "prompt_length": len(final_prompt),
                "has_continuity": bool(context.previous_scene_text),
                "has_brainstorm": bool(context.brainstorm_insights),
                "has_suggestions": bool(bucket_suggestions)
            }
        )
        self.log_step(step)
        
        self.trigger_callback('prompt_compiled', {
            'prompt': final_prompt,
            'prompt_length': len(final_prompt),
            'components': {
                'continuity': bool(context.previous_scene_text),
                'brainstorm': bool(context.brainstorm_insights),
                'suggestions': bool(bucket_suggestions)
            },
            'step_id': step_id
        })
        
        return final_prompt
    
    async def generate_scene(self, final_prompt: str, context: WriteContext) -> str:
        """Generate the actual scene text"""
        step_id = f"generation_{context.act}_{context.scene}_{datetime.now().strftime('%H%M%S')}"
        
        self.trigger_callback('generation_started', {
            'act': context.act,
            'scene': context.scene,
            'prompt_length': len(final_prompt),
            'step_id': step_id
        })
        
        try:
            # Generate scene text
            scene_text = await gpt_4o_mini_complete(final_prompt)
            
            # Calculate metrics
            word_count = len(scene_text.split())
            char_count = len(scene_text)
            
            # Log generation
            step = WriteStep(
                step_id=step_id,
                step_type="generation",
                timestamp=datetime.now(),
                act=context.act,
                scene=context.scene,
                content=scene_text,
                metadata={
                    "word_count": word_count,
                    "char_count": char_count,
                    "success": True
                }
            )
            self.log_step(step)
            
            # Save generation record
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO scene_generations
                (generation_id, session_id, act, scene, context_used, prompt_used, 
                 generated_text, word_count, timestamp, success)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                step_id,
                self.current_session["session_id"],
                context.act,
                context.scene,
                json.dumps(context.__dict__, default=str),
                final_prompt,
                scene_text,
                word_count,
                datetime.now(),
                True
            ))
            self.conn.commit()
            
            self.trigger_callback('scene_generated', {
                'act': context.act,
                'scene': context.scene,
                'scene_text': scene_text,
                'word_count': word_count,
                'success': True,
                'step_id': step_id
            })
            
            return scene_text
            
        except Exception as e:
            # Log failed generation
            step = WriteStep(
                step_id=step_id,
                step_type="generation",
                timestamp=datetime.now(),
                act=context.act,
                scene=context.scene,
                content=f"Error: {str(e)}",
                metadata={"success": False, "error": str(e)}
            )
            self.log_step(step)
            
            # Save failed generation record
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO scene_generations
                (generation_id, session_id, act, scene, context_used, prompt_used, 
                 generated_text, word_count, timestamp, success)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                step_id,
                self.current_session["session_id"],
                context.act,
                context.scene,
                json.dumps(context.__dict__, default=str),
                final_prompt,
                f"Generation failed: {str(e)}",
                0,
                datetime.now(),
                False
            ))
            self.conn.commit()
            
            self.trigger_callback('scene_generated', {
                'act': context.act,
                'scene': context.scene,
                'error': str(e),
                'success': False,
                'step_id': step_id
            })
            
            raise e
    
    def save_scene(self, scene_text: str, context: WriteContext) -> bool:
        """Save the generated scene"""
        step_id = f"save_{context.act}_{context.scene}_{datetime.now().strftime('%H%M%S')}"
        
        try:
            cursor = self.conn.cursor()
            
            word_count = len(scene_text.split())
            char_count = len(scene_text)
            
            cursor.execute('''
                INSERT INTO final_scenes
                (scene_id, session_id, act, scene, scene_text, word_count, 
                 character_count, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                step_id,
                self.current_session["session_id"],
                context.act,
                context.scene,
                scene_text,
                word_count,
                char_count,
                datetime.now()
            ))
            
            self.conn.commit()
            
            # Update session stats
            self.current_session["scenes_written"] += 1
            self.current_session["total_words"] += word_count
            
            # Log save
            step = WriteStep(
                step_id=step_id,
                step_type="scene_complete",
                timestamp=datetime.now(),
                act=context.act,
                scene=context.scene,
                content="Scene saved successfully",
                metadata={
                    "word_count": word_count,
                    "char_count": char_count,
                    "total_scenes": self.current_session["scenes_written"]
                }
            )
            self.log_step(step)
            
            self.trigger_callback('scene_saved', {
                'act': context.act,
                'scene': context.scene,
                'word_count': word_count,
                'total_scenes': self.current_session["scenes_written"],
                'total_words': self.current_session["total_words"],
                'step_id': step_id
            })
            
            return True
            
        except Exception as e:
            print(f"Error saving scene: {e}")
            return False
    
    async def write_scene(self, act: int, scene: int) -> bool:
        """Write a complete scene with full transparency"""
        self.trigger_callback('scene_started', {
            'act': act,
            'scene': scene
        })
        
        try:
            # 1. Assemble context
            context = self.assemble_write_context(act, scene)
            
            # 2. Query buckets for writing suggestions
            bucket_suggestions = await self.query_buckets_for_writing(context)
            
            # 3. Compile final prompt
            final_prompt = self.compile_final_prompt(context, bucket_suggestions)
            
            # 4. Generate scene
            scene_text = await self.generate_scene(final_prompt, context)
            
            # 5. Save scene
            success = self.save_scene(scene_text, context)
            
            return success
            
        except Exception as e:
            print(f"❌ Error writing scene {act}-{scene}: {e}")
            return False
    
    async def write_all_scenes(self, buckets: List[str], user_guidance: str = "") -> str:
        """Write all scenes with full transparency"""
        session_id = self.start_session(buckets, user_guidance)
        
        # Get all scenes
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT act, scene 
            FROM story_outline 
            ORDER BY act, scene
        ''')
        scenes = cursor.fetchall()
        
        if not scenes:
            print("❌ No scenes found in story outline")
            return session_id
        
        print(f"📝 Writing {len(scenes)} scenes")
        print(f"🧠 Using buckets: {', '.join(buckets)}")
        
        successful_scenes = 0
        
        for act, scene in scenes:
            print(f"\n🎬 Writing Act {act}, Scene {scene}")
            
            success = await self.write_scene(act, scene)
            
            if success:
                successful_scenes += 1
                print(f"  ✅ Scene completed")
            else:
                print(f"  ❌ Scene failed")
            
            # Brief pause between scenes
            await asyncio.sleep(1)
        
        # Complete session
        self.current_session["end_time"] = datetime.now()
        self.current_session["status"] = "completed"
        
        cursor.execute('''
            UPDATE write_sessions 
            SET end_time = ?, total_scenes = ?, successful_scenes = ?, status = ?
            WHERE session_id = ?
        ''', (
            datetime.now(), 
            len(scenes), 
            successful_scenes, 
            "completed", 
            session_id
        ))
        self.conn.commit()
        
        self.trigger_callback('session_completed', {
            'session_id': session_id,
            'total_scenes': len(scenes),
            'successful_scenes': successful_scenes,
            'total_words': self.current_session["total_words"]
        })
        
        return session_id
    
    def get_session_summary(self, session_id: str) -> Dict:
        """Get comprehensive summary of a writing session"""
        cursor = self.conn.cursor()
        
        # Get session info
        cursor.execute('''
            SELECT * FROM write_sessions 
            WHERE session_id = ?
        ''', (session_id,))
        session_data = cursor.fetchone()
        
        if not session_data:
            return {"error": "Session not found"}
        
        # Get scene statistics
        cursor.execute('''
            SELECT act, scene, word_count, timestamp
            FROM final_scenes 
            WHERE session_id = ?
            ORDER BY act, scene
        ''', (session_id,))
        scenes = cursor.fetchall()
        
        # Get step counts
        cursor.execute('''
            SELECT step_type, COUNT(*) 
            FROM write_steps 
            WHERE session_id = ?
            GROUP BY step_type
        ''', (session_id,))
        step_counts = dict(cursor.fetchall())
        
        total_words = sum(scene[2] for scene in scenes)
        avg_words = total_words // len(scenes) if scenes else 0
        
        return {
            "session_id": session_id,
            "session_data": session_data,
            "scenes_written": len(scenes),
            "total_words": total_words,
            "average_words_per_scene": avg_words,
            "step_counts": step_counts,
            "scenes_detail": scenes
        }
    
    def export_screenplay(self, session_id: str) -> str:
        """Export the complete screenplay"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT act, scene, scene_text, word_count
            FROM final_scenes 
            WHERE session_id = ?
            ORDER BY act, scene
        ''', (session_id,))
        scenes = cursor.fetchall()
        
        if not scenes:
            print("No scenes to export")
            return None
        
        # Create export
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.project_path, f"screenplay_{session_id}_{timestamp}.txt")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"SCREENPLAY: {self.project_name.upper()}\n")
            f.write(f"{'='*60}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Session: {session_id}\n")
            f.write(f"Total Scenes: {len(scenes)}\n")
            f.write(f"Total Words: {sum(scene[3] for scene in scenes)}\n")
            f.write(f"{'='*60}\n\n")
            
            for act, scene, text, word_count in scenes:
                f.write(f"ACT {act}, SCENE {scene}\n")
                f.write(f"({word_count} words)\n")
                f.write(f"{'-'*40}\n\n")
                f.write(text)
                f.write(f"\n\n{'='*60}\n\n")
        
        print(f"✅ Screenplay exported: {filename}")
        return filename


# Real-time console interface for writing transparency
class WriteConsole:
    """Console interface showing real-time writing progress"""
    
    def __init__(self, writer: TransparentWriter):
        self.writer = writer
        self.setup_callbacks()
    
    def setup_callbacks(self):
        """Setup real-time callbacks"""
        self.writer.register_callback('session_started', self.on_session_started)
        self.writer.register_callback('scene_started', self.on_scene_started)
        self.writer.register_callback('context_assembled', self.on_context_assembled)
        self.writer.register_callback('brainstorm_fetched', self.on_brainstorm_fetched)
        self.writer.register_callback('bucket_queried', self.on_bucket_queried)
        self.writer.register_callback('prompt_compiled', self.on_prompt_compiled)
        self.writer.register_callback('generation_started', self.on_generation_started)
        self.writer.register_callback('scene_generated', self.on_scene_generated)
        self.writer.register_callback('scene_saved', self.on_scene_saved)
        self.writer.register_callback('session_completed', self.on_session_completed)
    
    def on_session_started(self, data):
        session_id = data['session_id']
        buckets = data['buckets']
        print(f"📝 Writing session started: {session_id}")
        print(f"🧠 Using buckets: {', '.join(buckets)}")
    
    def on_scene_started(self, data):
        act, scene = data['act'], data['scene']
        print(f"\n🎬 Starting Act {act}, Scene {scene}")
    
    def on_context_assembled(self, data):
        context = data['context']
        print(f"  📊 Context assembled")
        print(f"    Characters: {len(context.character_details)}")
        print(f"    Has continuity: {'Yes' if context.previous_scene_text else 'No'}")
        print(f"    Has brainstorm: {'Yes' if context.brainstorm_insights else 'No'}")
    
    def on_brainstorm_fetched(self, data):
        buckets_found = data['buckets_found']
        print(f"  🧠 Brainstorm insights: {buckets_found} buckets")
    
    def on_bucket_queried(self, data):
        bucket = data['bucket']
        print(f"  🔍 Querying {bucket} for writing guidance...")
    
    def on_prompt_compiled(self, data):
        length = data['prompt_length']
        components = data['components']
        print(f"  📝 Prompt compiled ({length} chars)")
        print(f"    Components: continuity={components['continuity']}, "
              f"brainstorm={components['brainstorm']}, suggestions={components['suggestions']}")
    
    def on_generation_started(self, data):
        act, scene = data['act'], data['scene']
        print(f"  ⚡ Generating scene text...")
    
    def on_scene_generated(self, data):
        if data['success']:
            word_count = data['word_count']
            print(f"  ✅ Scene generated ({word_count} words)")
        else:
            error = data['error']
            print(f"  ❌ Generation failed: {error}")
    
    def on_scene_saved(self, data):
        word_count = data['word_count']
        total_scenes = data['total_scenes']
        total_words = data['total_words']
        print(f"  💾 Scene saved ({word_count} words)")
        print(f"    Session progress: {total_scenes} scenes, {total_words} total words")
    
    def on_session_completed(self, data):
        session_id = data['session_id']
        successful = data['successful_scenes']
        total = data['total_scenes']
        total_words = data['total_words']
        
        print(f"\n🎉 Writing session completed: {session_id}")
        print(f"📊 Results: {successful}/{total} scenes successful")
        print(f"📝 Total words: {total_words}")


async def demo_transparent_write():
    """Demonstrate transparent writing"""
    project_path = "exports/the_wrong_wedding_20250813_1253"
    
    if not os.path.exists(project_path):
        print(f"Project not found: {project_path}")
        return
    
    # Initialize components
    writer = TransparentWriter(project_path)
    console = WriteConsole(writer)
    
    print("\n" + "="*60)
    print("TRANSPARENT WRITING DEMO")
    print("="*60)
    
    # Run writing with full transparency
    session_id = await writer.write_all_scenes(
        buckets=["scripts", "books"],
        user_guidance="Focus on witty dialogue and authentic emotion"
    )
    
    # Export screenplay
    writer.export_screenplay(session_id)
    
    # Show summary
    summary = writer.get_session_summary(session_id)
    print(f"\n📊 FINAL SUMMARY:")
    print(f"  Scenes written: {summary['scenes_written']}")
    print(f"  Total words: {summary['total_words']}")
    print(f"  Average words/scene: {summary['average_words_per_scene']}")
    
    print("\n✨ Transparent writing complete!")


if __name__ == "__main__":
    asyncio.run(demo_transparent_write())