"""
Transparent Brainstorming Module for Lizzy
Provides real-time visibility into every step of the brainstorming process
"""

import os
import json
import sqlite3
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from lizzy_templates import TemplateManager, PromptInspector
from lizzy_lightrag_manager import LightRAGManager


@dataclass
class BrainstormStep:
    """Represents a single step in the brainstorming process"""
    step_id: str
    step_type: str  # "context", "prompt", "query", "response"
    timestamp: datetime
    bucket: str
    content: Any
    metadata: Dict = None


@dataclass
class BrainstormContext:
    """Context for a brainstorming session"""
    act: int
    scene: int
    scene_description: str
    character_details: List[Dict]
    previous_scene: str
    user_guidance: str
    active_buckets: List[str]


class TransparentBrainstormer:
    """Transparent brainstorming engine with real-time visibility"""
    
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
            'step_started': [],
            'step_completed': [],
            'context_assembled': [],
            'prompt_compiled': [],
            'query_sent': [],
            'response_received': [],
            'session_completed': []
        }
    
    def setup_tracking_tables(self):
        """Setup tables for tracking brainstorming sessions"""
        cursor = self.conn.cursor()
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brainstorm_sessions (
                session_id TEXT PRIMARY KEY,
                project_name TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                total_scenes INTEGER,
                buckets_used TEXT,
                user_guidance TEXT,
                status TEXT DEFAULT 'running'
            )
        ''')
        
        # Steps table for detailed tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brainstorm_steps (
                step_id TEXT PRIMARY KEY,
                session_id TEXT,
                step_type TEXT,
                timestamp TIMESTAMP,
                act INTEGER,
                scene INTEGER,
                bucket TEXT,
                content TEXT,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES brainstorm_sessions (session_id)
            )
        ''')
        
        # Outputs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brainstorm_outputs (
                output_id TEXT PRIMARY KEY,
                session_id TEXT,
                act INTEGER,
                scene INTEGER,
                bucket TEXT,
                prompt_used TEXT,
                response TEXT,
                timestamp TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES brainstorm_sessions (session_id)
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
        """Start a new brainstorming session"""
        session_id = f"BS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = {
            "session_id": session_id,
            "start_time": datetime.now(),
            "buckets": buckets,
            "user_guidance": user_guidance,
            "scenes": [],
            "status": "running"
        }
        
        # Save session to database
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO brainstorm_sessions 
            (session_id, project_name, start_time, buckets_used, user_guidance)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, self.project_name, datetime.now(), 
              ','.join(buckets), user_guidance))
        self.conn.commit()
        
        self.steps_log = []
        print(f"🧠 Started brainstorming session: {session_id}")
        return session_id
    
    def log_step(self, step: BrainstormStep):
        """Log a brainstorming step"""
        self.steps_log.append(step)
        
        # Save to database
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO brainstorm_steps 
            (step_id, session_id, step_type, timestamp, act, scene, bucket, content, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            step.step_id,
            self.current_session["session_id"],
            step.step_type,
            step.timestamp,
            getattr(step, 'act', None),
            getattr(step, 'scene', None),
            step.bucket,
            json.dumps(step.content) if not isinstance(step.content, str) else step.content,
            json.dumps(step.metadata or {})
        ))
        self.conn.commit()
    
    def assemble_context(self, act: int, scene: int) -> BrainstormContext:
        """Assemble context for a specific scene"""
        step_id = f"context_{act}_{scene}_{datetime.now().strftime('%H%M%S')}"
        
        self.trigger_callback('step_started', {
            'step': 'context_assembly',
            'act': act,
            'scene': scene
        })
        
        cursor = self.conn.cursor()
        
        # Get scene info
        cursor.execute('''
            SELECT key_characters, key_events 
            FROM story_outline 
            WHERE act = ? AND scene = ?
        ''', (act, scene))
        scene_data = cursor.fetchone()
        
        if not scene_data:
            raise ValueError(f"Scene not found: Act {act}, Scene {scene}")
        
        scene_description = f"Characters: {scene_data[0]}\nEvents: {scene_data[1]}"
        
        # Get character details
        cursor.execute('''
            SELECT name, gender, age, romantic_challenge, lovable_trait, comedic_flaw 
            FROM characters
        ''')
        all_chars = cursor.fetchall()
        
        character_details = []
        scene_chars = scene_data[0].split(',') if scene_data[0] else []
        
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
        
        # Get previous scene for continuity
        previous_scene = ""
        if scene > 1:
            cursor.execute('''
                SELECT key_events 
                FROM story_outline 
                WHERE act = ? AND scene = ?
            ''', (act, scene - 1))
            prev_data = cursor.fetchone()
            if prev_data:
                previous_scene = prev_data[0]
        
        context = BrainstormContext(
            act=act,
            scene=scene,
            scene_description=scene_description,
            character_details=character_details,
            previous_scene=previous_scene,
            user_guidance=self.current_session.get("user_guidance", ""),
            active_buckets=self.current_session["buckets"]
        )
        
        # Log context assembly
        step = BrainstormStep(
            step_id=step_id,
            step_type="context",
            timestamp=datetime.now(),
            bucket="system",
            content=context.__dict__,
            metadata={"act": act, "scene": scene}
        )
        self.log_step(step)
        
        self.trigger_callback('context_assembled', {
            'context': context,
            'step_id': step_id
        })
        
        return context
    
    def compile_prompts(self, context: BrainstormContext) -> Dict[str, Dict]:
        """Compile prompts for each active bucket"""
        step_id = f"prompts_{context.act}_{context.scene}_{datetime.now().strftime('%H%M%S')}"
        
        self.trigger_callback('step_started', {
            'step': 'prompt_compilation',
            'buckets': context.active_buckets
        })
        
        compiled_prompts = {}
        
        for bucket in context.active_buckets:
            # Format character details for prompt
            char_context = "\n".join([
                f"- {char['name']} ({char['gender']}, {char['age']}): "
                f"Challenge: {char['romantic_challenge']}, "
                f"Lovable: {char['lovable_trait']}, "
                f"Comedic Flaw: {char['comedic_flaw']}"
                for char in context.character_details
            ])
            
            # Build context dict for template
            template_context = {
                "act": context.act,
                "scene": context.scene,
                "scene_context": context.scene_description,
                "character_details": char_context,
                "previous_scene": context.previous_scene,
                "user_guidance": context.user_guidance
            }
            
            # Use prompt inspector for transparency
            inspection = self.prompt_inspector.inspect_prompt(
                "brainstorm", bucket, template_context
            )
            
            compiled_prompts[bucket] = {
                "template_used": self.template_manager.get_template("brainstorm", bucket),
                "context": template_context,
                "compiled_prompt": inspection["compiled_prompt"],
                "inspection": inspection
            }
        
        # Log prompt compilation
        step = BrainstormStep(
            step_id=step_id,
            step_type="prompt",
            timestamp=datetime.now(),
            bucket="all",
            content=compiled_prompts,
            metadata={"act": context.act, "scene": context.scene}
        )
        self.log_step(step)
        
        self.trigger_callback('prompt_compiled', {
            'prompts': compiled_prompts,
            'step_id': step_id
        })
        
        return compiled_prompts
    
    async def execute_queries(self, compiled_prompts: Dict[str, Dict], 
                             context: BrainstormContext) -> Dict[str, Dict]:
        """Execute queries against LightRAG buckets"""
        responses = {}
        
        for bucket, prompt_data in compiled_prompts.items():
            step_id = f"query_{bucket}_{context.act}_{context.scene}_{datetime.now().strftime('%H%M%S')}"
            
            self.trigger_callback('query_sent', {
                'bucket': bucket,
                'prompt': prompt_data["compiled_prompt"][:200] + "...",
                'step_id': step_id
            })
            
            # Log query start
            query_step = BrainstormStep(
                step_id=step_id,
                step_type="query",
                timestamp=datetime.now(),
                bucket=bucket,
                content=prompt_data["compiled_prompt"],
                metadata={"act": context.act, "scene": context.scene, "status": "sent"}
            )
            self.log_step(query_step)
            
            # Execute query
            try:
                result = self.lightrag_manager.query_bucket(
                    bucket, 
                    prompt_data["compiled_prompt"]
                )
                
                response_data = {
                    "bucket": bucket,
                    "query": prompt_data["compiled_prompt"],
                    "response": result.get("response", "No response"),
                    "timestamp": datetime.now(),
                    "success": "error" not in result
                }
                
                responses[bucket] = response_data
                
                # Log successful response
                response_step = BrainstormStep(
                    step_id=f"response_{step_id}",
                    step_type="response",
                    timestamp=datetime.now(),
                    bucket=bucket,
                    content=result.get("response", "No response"),
                    metadata={"act": context.act, "scene": context.scene, "success": True}
                )
                self.log_step(response_step)
                
                # Save to outputs table
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT INTO brainstorm_outputs
                    (output_id, session_id, act, scene, bucket, prompt_used, response, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    f"out_{step_id}",
                    self.current_session["session_id"],
                    context.act,
                    context.scene,
                    bucket,
                    prompt_data["compiled_prompt"],
                    result.get("response", ""),
                    datetime.now()
                ))
                self.conn.commit()
                
                self.trigger_callback('response_received', {
                    'bucket': bucket,
                    'response': result.get("response", "")[:200] + "...",
                    'step_id': step_id,
                    'success': True
                })
                
            except Exception as e:
                error_response = {
                    "bucket": bucket,
                    "query": prompt_data["compiled_prompt"],
                    "response": f"Error: {str(e)}",
                    "timestamp": datetime.now(),
                    "success": False
                }
                
                responses[bucket] = error_response
                
                # Log error
                error_step = BrainstormStep(
                    step_id=f"error_{step_id}",
                    step_type="response",
                    timestamp=datetime.now(),
                    bucket=bucket,
                    content=f"Error: {str(e)}",
                    metadata={"act": context.act, "scene": context.scene, "success": False}
                )
                self.log_step(error_step)
                
                self.trigger_callback('response_received', {
                    'bucket': bucket,
                    'error': str(e),
                    'step_id': step_id,
                    'success': False
                })
            
            # Small delay between queries
            await asyncio.sleep(0.5)
        
        return responses
    
    async def brainstorm_scene(self, act: int, scene: int) -> Dict:
        """Brainstorm a single scene with full transparency"""
        print(f"\n🎬 Brainstorming Act {act}, Scene {scene}")
        
        try:
            # 1. Assemble context
            print("  📊 Assembling context...")
            context = self.assemble_context(act, scene)
            
            # 2. Compile prompts
            print("  📝 Compiling prompts...")
            prompts = self.compile_prompts(context)
            
            # 3. Execute queries
            print("  🔍 Executing queries...")
            responses = await self.execute_queries(prompts, context)
            
            # 4. Compile results
            scene_result = {
                "act": act,
                "scene": scene,
                "context": context,
                "prompts": prompts,
                "responses": responses,
                "timestamp": datetime.now(),
                "success": all(r["success"] for r in responses.values())
            }
            
            print(f"  ✅ Scene {scene} brainstorming complete")
            return scene_result
            
        except Exception as e:
            print(f"  ❌ Error brainstorming scene: {e}")
            return {
                "act": act,
                "scene": scene,
                "error": str(e),
                "timestamp": datetime.now(),
                "success": False
            }
    
    async def brainstorm_all_scenes(self, buckets: List[str], user_guidance: str = "") -> str:
        """Brainstorm all scenes with full session tracking"""
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
        
        print(f"🧠 Brainstorming {len(scenes)} scenes")
        print(f"📚 Using buckets: {', '.join(buckets)}")
        
        scene_results = []
        successful_scenes = 0
        
        for act, scene in scenes:
            result = await self.brainstorm_scene(act, scene)
            scene_results.append(result)
            
            if result.get("success", False):
                successful_scenes += 1
        
        # Complete session
        self.current_session["end_time"] = datetime.now()
        self.current_session["status"] = "completed"
        
        cursor.execute('''
            UPDATE brainstorm_sessions 
            SET end_time = ?, total_scenes = ?, status = ?
            WHERE session_id = ?
        ''', (datetime.now(), successful_scenes, "completed", session_id))
        self.conn.commit()
        
        print(f"\n✅ Brainstorming session complete!")
        print(f"📊 Successfully processed: {successful_scenes}/{len(scenes)} scenes")
        
        self.trigger_callback('session_completed', {
            'session_id': session_id,
            'total_scenes': len(scenes),
            'successful_scenes': successful_scenes,
            'results': scene_results
        })
        
        return session_id
    
    def get_session_summary(self, session_id: str) -> Dict:
        """Get comprehensive summary of a brainstorming session"""
        cursor = self.conn.cursor()
        
        # Get session info
        cursor.execute('''
            SELECT * FROM brainstorm_sessions 
            WHERE session_id = ?
        ''', (session_id,))
        session_data = cursor.fetchone()
        
        if not session_data:
            return {"error": "Session not found"}
        
        # Get all outputs
        cursor.execute('''
            SELECT act, scene, bucket, response, timestamp
            FROM brainstorm_outputs 
            WHERE session_id = ?
            ORDER BY act, scene, bucket
        ''', (session_id,))
        outputs = cursor.fetchall()
        
        # Get step counts
        cursor.execute('''
            SELECT step_type, COUNT(*) 
            FROM brainstorm_steps 
            WHERE session_id = ?
            GROUP BY step_type
        ''', (session_id,))
        step_counts = dict(cursor.fetchall())
        
        return {
            "session_id": session_id,
            "session_data": session_data,
            "total_outputs": len(outputs),
            "outputs_by_scene": self._group_outputs_by_scene(outputs),
            "step_counts": step_counts,
            "buckets_used": session_data[4].split(',') if session_data[4] else []
        }
    
    def _group_outputs_by_scene(self, outputs: List) -> Dict:
        """Group outputs by scene"""
        grouped = {}
        for act, scene, bucket, response, timestamp in outputs:
            scene_key = f"Act {act}, Scene {scene}"
            if scene_key not in grouped:
                grouped[scene_key] = {}
            grouped[scene_key][bucket] = {
                "response": response,
                "timestamp": timestamp
            }
        return grouped
    
    def export_session_report(self, session_id: str) -> str:
        """Export detailed session report"""
        summary = self.get_session_summary(session_id)
        
        if "error" in summary:
            return None
        
        # Create report
        report_lines = [
            f"BRAINSTORMING SESSION REPORT",
            f"{'='*60}",
            f"Session ID: {session_id}",
            f"Project: {self.project_name}",
            f"Buckets Used: {', '.join(summary['buckets_used'])}",
            f"Total Outputs: {summary['total_outputs']}",
            f"Step Counts: {summary['step_counts']}",
            f"",
            f"SCENE-BY-SCENE RESULTS:",
            f"{'-'*60}"
        ]
        
        for scene, buckets in summary["outputs_by_scene"].items():
            report_lines.append(f"\n{scene}")
            report_lines.append(f"{'-'*30}")
            
            for bucket, data in buckets.items():
                report_lines.append(f"\n[{bucket.upper()}]")
                response = data["response"]
                preview = response[:300] + "..." if len(response) > 300 else response
                report_lines.append(preview)
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.project_path, f"brainstorm_report_{session_id}_{timestamp}.txt")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"📄 Report exported: {report_file}")
        return report_file


# Real-time console interface for transparency
class BrainstormConsole:
    """Console interface showing real-time brainstorming progress"""
    
    def __init__(self, brainstormer: TransparentBrainstormer):
        self.brainstormer = brainstormer
        self.setup_callbacks()
    
    def setup_callbacks(self):
        """Setup real-time callbacks"""
        self.brainstormer.register_callback('step_started', self.on_step_started)
        self.brainstormer.register_callback('context_assembled', self.on_context_assembled)
        self.brainstormer.register_callback('prompt_compiled', self.on_prompt_compiled)
        self.brainstormer.register_callback('query_sent', self.on_query_sent)
        self.brainstormer.register_callback('response_received', self.on_response_received)
        self.brainstormer.register_callback('session_completed', self.on_session_completed)
    
    def on_step_started(self, data):
        step = data.get('step', 'unknown')
        print(f"  🔄 Starting: {step}")
    
    def on_context_assembled(self, data):
        context = data['context']
        print(f"  📊 Context assembled for Act {context.act}, Scene {context.scene}")
        print(f"    Characters: {len(context.character_details)}")
        print(f"    Active buckets: {len(context.active_buckets)}")
    
    def on_prompt_compiled(self, data):
        prompts = data['prompts']
        print(f"  📝 Compiled {len(prompts)} prompts")
        for bucket, prompt_data in prompts.items():
            prompt_length = len(prompt_data['compiled_prompt'])
            print(f"    {bucket}: {prompt_length} characters")
    
    def on_query_sent(self, data):
        bucket = data['bucket']
        print(f"  🔍 Querying {bucket}...")
    
    def on_response_received(self, data):
        bucket = data['bucket']
        success = data.get('success', False)
        status = "✅" if success else "❌"
        print(f"  {status} Response from {bucket}")
        
        if success:
            response_preview = data.get('response', '')[:100] + "..."
            print(f"    Preview: {response_preview}")
        else:
            error = data.get('error', 'Unknown error')
            print(f"    Error: {error}")
    
    def on_session_completed(self, data):
        total = data['total_scenes']
        successful = data['successful_scenes']
        session_id = data['session_id']
        
        print(f"\n🎉 Session completed: {session_id}")
        print(f"📊 Results: {successful}/{total} scenes successful")


async def demo_transparent_brainstorm():
    """Demonstrate transparent brainstorming"""
    project_path = "exports/the_wrong_wedding_20250813_1253"
    
    if not os.path.exists(project_path):
        print(f"Project not found: {project_path}")
        return
    
    # Initialize components
    brainstormer = TransparentBrainstormer(project_path)
    console = BrainstormConsole(brainstormer)
    
    print("\n" + "="*60)
    print("TRANSPARENT BRAINSTORMING DEMO")
    print("="*60)
    
    # Run brainstorming with transparency
    session_id = await brainstormer.brainstorm_all_scenes(
        buckets=["scripts", "books"],
        user_guidance="Focus on witty dialogue and romantic tension"
    )
    
    # Export report
    brainstormer.export_session_report(session_id)
    
    print("\n✨ Transparent brainstorming complete!")


if __name__ == "__main__":
    asyncio.run(demo_transparent_brainstorm())