"""
Prompt Editor Backend for Lizzy Brainstorm Module
Provides API for prompt template management and testing
"""

import os
import json
import sqlite3
import asyncio
import webview
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from lizzy_templates import TemplateManager, PromptInspector
from lizzy_transparent_brainstorm import TransparentBrainstormer, BrainstormContext


@dataclass
class PromptConfig:
    """Configuration for a prompt template"""
    template_name: str
    prompt_template: str
    buckets: Dict[str, bool]
    output_format: Dict[str, Dict]
    version: str = "1.0"
    created_at: datetime = None
    modified_at: datetime = None
    performance_metrics: Dict = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.modified_at is None:
            self.modified_at = datetime.now()
        if self.performance_metrics is None:
            self.performance_metrics = {}


class PromptEditorAPI:
    """API for prompt editor interactions"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.project_name = os.path.basename(project_path)
        self.db_path = os.path.join(project_path, f"{self.project_name}.sqlite")
        
        # Initialize components
        self.template_manager = TemplateManager()
        self.brainstormer = TransparentBrainstormer(project_path)
        self.prompt_inspector = PromptInspector(self.template_manager)
        
        # Setup database tables
        self.setup_database()
        
        # Current configuration
        self.current_config = None
        self.test_results = []
        
    def setup_database(self):
        """Setup database tables for prompt configurations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Prompt configurations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompt_configs (
                config_id TEXT PRIMARY KEY,
                template_name TEXT,
                prompt_template TEXT,
                buckets TEXT,
                output_format TEXT,
                version TEXT,
                created_at TIMESTAMP,
                modified_at TIMESTAMP,
                performance_metrics TEXT,
                is_active BOOLEAN DEFAULT 0
            )
        ''')
        
        # Prompt test results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompt_tests (
                test_id TEXT PRIMARY KEY,
                config_id TEXT,
                act INTEGER,
                scene INTEGER,
                test_timestamp TIMESTAMP,
                response_time REAL,
                output_compliance REAL,
                creative_quality REAL,
                test_output TEXT,
                FOREIGN KEY (config_id) REFERENCES prompt_configs (config_id)
            )
        ''')
        
        # Version history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompt_versions (
                version_id TEXT PRIMARY KEY,
                config_id TEXT,
                version_number TEXT,
                prompt_template TEXT,
                created_at TIMESTAMP,
                change_description TEXT,
                FOREIGN KEY (config_id) REFERENCES prompt_configs (config_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_scene_context(self, act: int, scene: int) -> Dict:
        """Get context for a specific scene"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get scene info
        cursor.execute('''
            SELECT key_characters, key_events 
            FROM story_outline 
            WHERE act = ? AND scene = ?
        ''', (act, scene))
        scene_data = cursor.fetchone()
        
        if not scene_data:
            return {"error": f"Scene not found: Act {act}, Scene {scene}"}
        
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
        
        # Get previous scene
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
        
        # Get project logline
        cursor.execute("SELECT value FROM project_info WHERE key = 'description'")
        result = cursor.fetchone()
        logline = result[0] if result else "A romantic comedy about unexpected love"
        
        conn.close()
        
        return {
            "act": act,
            "scene": scene,
            "scene_description": f"Characters: {scene_data[0]}\nEvents: {scene_data[1]}",
            "character_details": character_details,
            "previous_scene": previous_scene,
            "logline": logline,
            "key_characters": scene_data[0],
            "key_events": scene_data[1]
        }
    
    def get_all_scenes(self) -> List[Dict]:
        """Get all scenes from the story outline"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT act, scene, key_characters, key_events 
            FROM story_outline 
            ORDER BY act, scene
        ''')
        scenes = cursor.fetchall()
        
        conn.close()
        
        return [
            {
                "act": act,
                "scene": scene,
                "label": f"Act {act}, Scene {scene}",
                "characters": chars,
                "events": events
            }
            for act, scene, chars, events in scenes
        ]
    
    def save_prompt_config(self, config_data: Dict) -> str:
        """Save a prompt configuration"""
        config_id = f"PC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        config = PromptConfig(
            template_name=config_data.get('templateName', 'Untitled'),
            prompt_template=config_data.get('promptTemplate', ''),
            buckets=config_data.get('buckets', {}),
            output_format=config_data.get('outputFormat', {})
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Deactivate previous configs
        cursor.execute("UPDATE prompt_configs SET is_active = 0")
        
        # Save new config
        cursor.execute('''
            INSERT INTO prompt_configs 
            (config_id, template_name, prompt_template, buckets, output_format, 
             version, created_at, modified_at, performance_metrics, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            config_id,
            config.template_name,
            config.prompt_template,
            json.dumps(config.buckets),
            json.dumps(config.output_format),
            config.version,
            config.created_at,
            config.modified_at,
            json.dumps(config.performance_metrics),
            True
        ))
        
        conn.commit()
        conn.close()
        
        self.current_config = config
        return config_id
    
    def load_active_config(self) -> Optional[Dict]:
        """Load the active prompt configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT config_id, template_name, prompt_template, buckets, output_format,
                   version, created_at, modified_at, performance_metrics
            FROM prompt_configs 
            WHERE is_active = 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "config_id": result[0],
                "template_name": result[1],
                "prompt_template": result[2],
                "buckets": json.loads(result[3]),
                "output_format": json.loads(result[4]),
                "version": result[5],
                "created_at": result[6],
                "modified_at": result[7],
                "performance_metrics": json.loads(result[8]) if result[8] else {}
            }
        
        return None
    
    async def test_prompt(self, prompt_template: str, scene_selector: str) -> Dict:
        """Test a prompt template on a specific scene"""
        # Parse scene selector (e.g., "Act 2, Scene 3 - Coffee Shop")
        parts = scene_selector.split(',')
        act = int(parts[0].split()[-1])
        scene = int(parts[1].split()[1])
        
        test_id = f"TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Get scene context
        context_data = self.get_scene_context(act, scene)
        
        # Compile prompt with actual data
        compiled_prompt = self.compile_prompt(prompt_template, context_data)
        
        # Run test with brainstormer
        start_time = datetime.now()
        
        try:
            # Create mock context for testing
            context = BrainstormContext(
                act=act,
                scene=scene,
                scene_description=context_data['scene_description'],
                character_details=context_data['character_details'],
                previous_scene=context_data['previous_scene'],
                user_guidance="Test run from prompt editor",
                active_buckets=["scripts", "plays", "books"]
            )
            
            # Execute test query
            result = await self.brainstormer.execute_queries(
                {"test": {"compiled_prompt": compiled_prompt}},
                context
            )
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Analyze output compliance
            output_compliance = self.analyze_output_compliance(result.get("test", {}))
            creative_quality = self.estimate_creative_quality(result.get("test", {}))
            
            # Save test result
            if self.current_config:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO prompt_tests
                    (test_id, config_id, act, scene, test_timestamp, 
                     response_time, output_compliance, creative_quality, test_output)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    test_id,
                    self.current_config.get('config_id', 'unknown'),
                    act,
                    scene,
                    datetime.now(),
                    response_time,
                    output_compliance,
                    creative_quality,
                    json.dumps(result)
                ))
                
                conn.commit()
                conn.close()
            
            return {
                "success": True,
                "test_id": test_id,
                "response_time": response_time,
                "output_compliance": output_compliance,
                "creative_quality": creative_quality,
                "output": result.get("test", {})
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "test_id": test_id
            }
    
    def compile_prompt(self, template: str, context_data: Dict) -> str:
        """Compile a prompt template with actual scene data"""
        compiled = template
        
        # Format character details
        char_details = []
        for char in context_data.get('character_details', []):
            char_details.append(
                f"{char['name'].upper()} ({char['age']}, {char['gender']}): "
                f"Romantic challenge: {char['romantic_challenge']}. "
                f"Lovable trait: {char['lovable_trait']}. "
                f"Comic flaw: {char['comedic_flaw']}."
            )
        
        # Replace variables
        replacements = {
            '{context.act}': str(context_data.get('act', '')),
            '{context.scene}': str(context_data.get('scene', '')),
            '{context.scene_description}': context_data.get('scene_description', ''),
            '{character_details}': '\n'.join(char_details),
            '{logline}': context_data.get('logline', ''),
            '{previous_scene}': context_data.get('previous_scene', ''),
            '{user_guidance}': 'Focus on character dynamics and humor'
        }
        
        for key, value in replacements.items():
            compiled = compiled.replace(key, value)
        
        return compiled
    
    def analyze_output_compliance(self, output: Dict) -> float:
        """Analyze how well the output complies with the expected format"""
        if not output or 'response' not in output:
            return 0.0
        
        response = output.get('response', '')
        
        # Check for expected sections
        expected_sections = [
            'SQL Snapshot',
            'Bucket Notes',
            'Unified Strategy',
            'Beat Sketch',
            'Opportunities & Risks',
            'Open Questions'
        ]
        
        found_sections = sum(1 for section in expected_sections if section in response)
        compliance = (found_sections / len(expected_sections)) * 100
        
        return min(compliance, 100.0)
    
    def estimate_creative_quality(self, output: Dict) -> float:
        """Estimate the creative quality of the output"""
        if not output or 'response' not in output:
            return 0.0
        
        response = output.get('response', '')
        
        # Simple heuristics for creative quality
        quality_indicators = {
            'specific_examples': len([1 for word in ['example', 'instance', 'such as', 'like'] if word in response.lower()]),
            'emotional_beats': len([1 for word in ['feeling', 'emotion', 'heart', 'tension'] if word in response.lower()]),
            'humor_elements': len([1 for word in ['funny', 'comedy', 'laugh', 'joke'] if word in response.lower()]),
            'structural_elements': len([1 for word in ['setup', 'payoff', 'reversal', 'twist'] if word in response.lower()])
        }
        
        # Calculate weighted score
        total_score = sum(quality_indicators.values())
        max_score = 20  # Arbitrary maximum
        
        quality = min((total_score / max_score) * 100, 100.0)
        return quality
    
    def get_version_history(self, config_id: str) -> List[Dict]:
        """Get version history for a configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT version_id, version_number, created_at, change_description
            FROM prompt_versions
            WHERE config_id = ?
            ORDER BY created_at DESC
        ''', (config_id,))
        
        versions = cursor.fetchall()
        conn.close()
        
        return [
            {
                "version_id": v[0],
                "version_number": v[1],
                "created_at": v[2],
                "change_description": v[3]
            }
            for v in versions
        ]
    
    def create_version(self, config_id: str, change_description: str) -> str:
        """Create a new version of a configuration"""
        version_id = f"V_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current config
        cursor.execute('''
            SELECT prompt_template, version FROM prompt_configs
            WHERE config_id = ?
        ''', (config_id,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return None
        
        current_template, current_version = result
        
        # Calculate new version number
        version_parts = current_version.split('.')
        new_version = f"{version_parts[0]}.{int(version_parts[1]) + 1}"
        
        # Save version
        cursor.execute('''
            INSERT INTO prompt_versions
            (version_id, config_id, version_number, prompt_template, created_at, change_description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            version_id,
            config_id,
            new_version,
            current_template,
            datetime.now(),
            change_description
        ))
        
        # Update config version
        cursor.execute('''
            UPDATE prompt_configs
            SET version = ?, modified_at = ?
            WHERE config_id = ?
        ''', (new_version, datetime.now(), config_id))
        
        conn.commit()
        conn.close()
        
        return version_id
    
    def get_performance_metrics(self, config_id: str) -> Dict:
        """Get aggregated performance metrics for a configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                AVG(response_time) as avg_response_time,
                AVG(output_compliance) as avg_compliance,
                AVG(creative_quality) as avg_quality,
                COUNT(*) as total_tests
            FROM prompt_tests
            WHERE config_id = ?
        ''', (config_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "avg_response_time": result[0] or 0,
                "avg_compliance": result[1] or 0,
                "avg_quality": result[2] or 0,
                "total_tests": result[3] or 0
            }
        
        return {
            "avg_response_time": 0,
            "avg_compliance": 0,
            "avg_quality": 0,
            "total_tests": 0
        }


class PromptEditorWindow:
    """Window manager for the prompt editor"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.api = PromptEditorAPI(project_path)
        self.window = None
    
    def start(self):
        """Start the prompt editor window"""
        # Create window
        self.window = webview.create_window(
            'Lizzy Prompt Studio - Brainstorm Configuration',
            'prompt_editor.html',
            width=1400,
            height=900,
            resizable=True,
            js_api=self.api
        )
        
        # Start GUI
        webview.start()
    
    def return_to_brainstorm(self):
        """Close editor and return to brainstorm"""
        if self.window:
            self.window.destroy()


def launch_prompt_editor(project_path: str):
    """Launch the prompt editor for a project"""
    editor = PromptEditorWindow(project_path)
    editor.start()


if __name__ == "__main__":
    # Demo launch
    demo_project = "exports/the_wrong_wedding_20250813_1253"
    if os.path.exists(demo_project):
        launch_prompt_editor(demo_project)
    else:
        print(f"Demo project not found: {demo_project}")