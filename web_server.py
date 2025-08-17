"""
Web Server for Lizzy Project Editor
Serves the modern web interface and provides REST API for database operations
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Global variables
current_project_path = None
current_project_name = None

class WebProjectManager:
    """Manages web interface database operations"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.project_name = os.path.basename(project_path)
        self.db_path = os.path.join(project_path, f"{self.project_name}.sqlite")
        
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_characters(self) -> List[Dict]:
        """Get all characters"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, archetype, gender, age, 
                   romantic_challenge, lovable_trait, comedic_flaw, notes
            FROM characters ORDER BY id
        """)
        
        characters = []
        for row in cursor.fetchall():
            characters.append({
                'id': row['id'],
                'name': row['name'] or '[Character Name]',
                'archetype': row['archetype'] or '',
                'gender': row['gender'] or '',
                'age': row['age'] or '',
                'challenge': row['romantic_challenge'] or '',
                'trait': row['lovable_trait'] or '',
                'flaw': row['comedic_flaw'] or '',
                'notes': row['notes'] or ''
            })
        
        conn.close()
        return characters
    
    def update_character(self, char_id: int, field: str, value: str) -> bool:
        """Update a character field"""
        field_map = {
            'name': 'name',
            'archetype': 'archetype',
            'gender': 'gender', 
            'age': 'age',
            'challenge': 'romantic_challenge',
            'trait': 'lovable_trait',
            'flaw': 'comedic_flaw',
            'notes': 'notes'
        }
        
        db_field = field_map.get(field)
        if not db_field:
            return False
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"UPDATE characters SET {db_field} = ? WHERE id = ?", (value, char_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating character: {e}")
            return False
    
    def get_story_outline(self) -> List[Dict]:
        """Get story outline"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Try extended table first
        try:
            cursor.execute("""
                SELECT id, act, beat, scene_number, description, 
                       status, characters, location, notes
                FROM story_outline_extended ORDER BY scene_number
            """)
            
            scenes = []
            for row in cursor.fetchall():
                scenes.append({
                    'id': row['id'],
                    'act': row['act'] or '',
                    'beat': row['beat'] or '',
                    'scene': row['scene_number'] or 0,
                    'description': row['description'] or '',
                    'status': row['status'] or 'placeholder',
                    'characters': row['characters'] or '',
                    'location': row['location'] or '',
                    'notes': row['notes'] or ''
                })
        
        except sqlite3.OperationalError:
            # Fallback to simple table
            cursor.execute("""
                SELECT id, act, scene, key_characters, key_events
                FROM story_outline ORDER BY act, scene
            """)
            
            scenes = []
            for row in cursor.fetchall():
                scenes.append({
                    'id': row['id'],
                    'act': f"Act {row['act']}",
                    'beat': 'Scene',
                    'scene': row['scene'] or 0,
                    'description': row['key_events'] or '',
                    'status': 'placeholder',
                    'characters': row['key_characters'] or '',
                    'location': '',
                    'notes': ''
                })
        
        conn.close()
        return scenes
    
    def update_scene(self, scene_id: int, field: str, value: str) -> bool:
        """Update a scene field"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Try extended table first
            try:
                field_map = {
                    'act': 'act',
                    'beat': 'beat',
                    'scene': 'scene_number',
                    'description': 'description',
                    'status': 'status',
                    'characters': 'characters',
                    'location': 'location'
                }
                
                db_field = field_map.get(field)
                if db_field:
                    if db_field == 'scene_number':
                        value = int(value)
                    cursor.execute(f"UPDATE story_outline_extended SET {db_field} = ? WHERE id = ?", (value, scene_id))
            
            except sqlite3.OperationalError:
                # Fallback to simple table
                field_map = {
                    'act': 'act',
                    'scene': 'scene',
                    'characters': 'key_characters',
                    'description': 'key_events'
                }
                
                db_field = field_map.get(field)
                if db_field:
                    if db_field in ['act', 'scene']:
                        value = int(value)
                    cursor.execute(f"UPDATE story_outline SET {db_field} = ? WHERE id = ?", (value, scene_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error updating scene: {e}")
            return False
    
    def get_notes(self) -> List[Dict]:
        """Get all notes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, category, content, created_at
            FROM notes ORDER BY created_at DESC
        """)
        
        notes = []
        for row in cursor.fetchall():
            # Format created date
            created = row['created_at']
            if created:
                try:
                    dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    created = dt.strftime('%Y-%m-%d')
                except:
                    created = created[:10]
            
            notes.append({
                'id': row['id'],
                'title': row['title'] or '',
                'category': row['category'] or '',
                'content': row['content'] or '',
                'created': created or ''
            })
        
        conn.close()
        return notes
    
    def update_note(self, note_id: int, field: str, value: str) -> bool:
        """Update a note field"""
        field_map = {
            'title': 'title',
            'category': 'category',
            'content': 'content'
        }
        
        db_field = field_map.get(field)
        if not db_field:
            return False
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"UPDATE notes SET {db_field} = ? WHERE id = ?", (value, note_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating note: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get project statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Count characters
        cursor.execute("SELECT COUNT(*) FROM characters")
        char_count = cursor.fetchone()[0]
        
        # Count scenes
        try:
            cursor.execute("SELECT COUNT(*) FROM story_outline_extended")
            scene_count = cursor.fetchone()[0]
        except:
            cursor.execute("SELECT COUNT(*) FROM story_outline")
            scene_count = cursor.fetchone()[0]
        
        # Count notes
        cursor.execute("SELECT COUNT(*) FROM notes")
        notes_count = cursor.fetchone()[0]
        
        # Count brainstorm sessions
        brainstorm_count = 0
        try:
            cursor.execute("SELECT COUNT(*) FROM brainstorm_sessions")
            brainstorm_count = cursor.fetchone()[0]
        except:
            pass
        
        # Count written scenes
        written_scenes = 0
        try:
            cursor.execute("SELECT COUNT(*) FROM written_scenes")
            written_scenes = cursor.fetchone()[0]
        except:
            pass
        
        conn.close()
        
        return {
            'characters': char_count,
            'scenes': scene_count,
            'notes': notes_count,
            'brainstorm_sessions': brainstorm_count,
            'written_scenes': written_scenes
        }
    
    def get_brainstorm_sessions(self) -> List[Dict]:
        """Get all brainstorm sessions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        sessions = []
        try:
            cursor.execute("""
                SELECT session_id, start_time, end_time, total_scenes, 
                       buckets_used, user_guidance, status
                FROM brainstorm_sessions 
                ORDER BY start_time DESC
            """)
            
            for row in cursor.fetchall():
                sessions.append({
                    'session_id': row[0],
                    'start_time': row[1],
                    'end_time': row[2],
                    'total_scenes': row[3] or 0,
                    'buckets_used': row[4] or '',
                    'user_guidance': row[5] or '',
                    'status': row[6] or 'unknown'
                })
        except Exception as e:
            print(f"Error getting brainstorm sessions: {e}")
        
        conn.close()
        return sessions
    
    def get_brainstorm_outputs(self, session_id: str) -> List[Dict]:
        """Get outputs for a specific brainstorm session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        outputs = []
        try:
            cursor.execute("""
                SELECT act, scene, bucket, response, timestamp
                FROM brainstorm_outputs 
                WHERE session_id = ?
                ORDER BY act, scene, bucket
            """, (session_id,))
            
            for row in cursor.fetchall():
                outputs.append({
                    'act': row[0],
                    'scene': row[1],
                    'bucket': row[2],
                    'response': row[3],
                    'timestamp': row[4]
                })
        except Exception as e:
            print(f"Error getting brainstorm outputs: {e}")
        
        conn.close()
        return outputs
    
    def get_written_scenes(self) -> List[Dict]:
        """Get all written scenes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        scenes = []
        try:
            cursor.execute("""
                SELECT id, act, scene, title, content, status, created_at, updated_at
                FROM written_scenes 
                ORDER BY act, scene
            """)
            
            for row in cursor.fetchall():
                scenes.append({
                    'id': row[0],
                    'act': row[1],
                    'scene': row[2],
                    'title': row[3] or '',
                    'content': row[4] or '',
                    'status': row[5] or 'draft',
                    'created_at': row[6],
                    'updated_at': row[7]
                })
        except Exception as e:
            print(f"Error getting written scenes: {e}")
        
        conn.close()
        return scenes
    
    def update_written_scene(self, scene_id: int, field: str, value: str) -> bool:
        """Update a written scene field"""
        field_map = {
            'title': 'title',
            'content': 'content',
            'status': 'status'
        }
        
        db_field = field_map.get(field)
        if not db_field:
            return False
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"UPDATE written_scenes SET {db_field} = ?, updated_at = datetime('now') WHERE id = ?", (value, scene_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating written scene: {e}")
            return False

# Initialize project manager
project_manager = None

def set_project(project_path: str):
    """Set the current project"""
    global project_manager, current_project_path, current_project_name
    current_project_path = project_path
    current_project_name = os.path.basename(project_path)
    project_manager = WebProjectManager(project_path)

# Routes
@app.route('/')
def index():
    """Serve the main web interface"""
    return send_from_directory('.', 'web_project_editor.html')

@app.route('/api/project/info')
def get_project_info():
    """Get current project information"""
    if not project_manager:
        return jsonify({'error': 'No project loaded'}), 400
    
    return jsonify({
        'name': current_project_name,
        'path': current_project_path,
        'stats': project_manager.get_stats()
    })

@app.route('/api/characters')
def get_characters():
    """Get all characters"""
    if not project_manager:
        return jsonify({'error': 'No project loaded'}), 400
    
    return jsonify(project_manager.get_characters())

@app.route('/api/characters/<int:char_id>', methods=['PUT'])
def update_character(char_id):
    """Update a character field"""
    if not project_manager:
        return jsonify({'error': 'No project loaded'}), 400
    
    data = request.get_json()
    field = data.get('field')
    value = data.get('value', '')
    
    if project_manager.update_character(char_id, field, value):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to update character'}), 500

@app.route('/api/outline')
def get_outline():
    """Get story outline"""
    if not project_manager:
        return jsonify({'error': 'No project loaded'}), 400
    
    return jsonify(project_manager.get_story_outline())

@app.route('/api/outline/<int:scene_id>', methods=['PUT'])
def update_scene(scene_id):
    """Update a scene field"""
    if not project_manager:
        return jsonify({'error': 'No project loaded'}), 400
    
    data = request.get_json()
    field = data.get('field')
    value = data.get('value', '')
    
    if project_manager.update_scene(scene_id, field, value):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to update scene'}), 500

@app.route('/api/notes')
def get_notes():
    """Get all notes"""
    if not project_manager:
        return jsonify({'error': 'No project loaded'}), 400
    
    return jsonify(project_manager.get_notes())

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update a note field"""
    if not project_manager:
        return jsonify({'error': 'No project loaded'}), 400
    
    data = request.get_json()
    field = data.get('field')
    value = data.get('value', '')
    
    if project_manager.update_note(note_id, field, value):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to update note'}), 500

@app.route('/api/brainstorm/sessions')
def get_brainstorm_sessions():
    """Get all brainstorm sessions"""
    if not project_manager:
        return jsonify({'error': 'No project loaded'}), 400
    
    return jsonify(project_manager.get_brainstorm_sessions())

@app.route('/api/brainstorm/sessions/<session_id>/outputs')
def get_brainstorm_outputs(session_id):
    """Get outputs for a specific brainstorm session"""
    if not project_manager:
        return jsonify({'error': 'No project loaded'}), 400
    
    return jsonify(project_manager.get_brainstorm_outputs(session_id))

@app.route('/api/written-scenes')
def get_written_scenes():
    """Get all written scenes"""
    if not project_manager:
        return jsonify({'error': 'No project loaded'}), 400
    
    return jsonify(project_manager.get_written_scenes())

@app.route('/api/written-scenes/<int:scene_id>', methods=['PUT'])
def update_written_scene(scene_id):
    """Update a written scene field"""
    if not project_manager:
        return jsonify({'error': 'No project loaded'}), 400
    
    data = request.get_json()
    field = data.get('field')
    value = data.get('value', '')
    
    if project_manager.update_written_scene(scene_id, field, value):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to update written scene'}), 500

@app.route('/api/save-all', methods=['POST'])
def save_all():
    """Save all changes (placeholder)"""
    return jsonify({'success': True, 'message': 'All changes saved'})

def launch_web_editor(project_path: str, port: int = 5000, auto_open: bool = True):
    """Launch the web-based project editor"""
    import webbrowser
    import threading
    import time
    
    set_project(project_path)
    
    url = f"http://localhost:{port}"
    
    print(f"🌐 Starting web server for project: {current_project_name}")
    print(f"🚀 Open your browser to: {url}")
    print(f"📝 Project database: {project_manager.db_path}")
    print()
    print("✨ Modern Web Interface Features:")
    print("   • Responsive design with mobile support")
    print("   • Dark/light mode toggle")  
    print("   • Inline cell editing")
    print("   • Real-time database sync")
    print("   • Professional Tailwind styling")
    print()
    
    if auto_open:
        def open_browser():
            time.sleep(1.5)  # Wait for server to start
            try:
                webbrowser.open(url)
                print(f"🌍 Opened browser to {url}")
            except Exception as e:
                print(f"⚠️  Could not auto-open browser: {e}")
                print(f"📖 Please manually open: {url}")
        
        threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use!")
            print(f"💡 Trying port {port + 1}...")
            launch_web_editor(project_path, port + 1, auto_open)

if __name__ == '__main__':
    # Test with gamma project
    project_path = 'projects/gamma'
    if os.path.exists(project_path):
        launch_web_editor(project_path)
    else:
        print("❌ Gamma project not found. Please create it first.")