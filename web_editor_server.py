"""
Simplified Web Server for Project Editor
Main project data curation interface
"""

from flask import Flask, render_template_string, jsonify, request
import os
import sqlite3
import json

# Create Flask app
app = Flask(__name__)

@app.route('/')
def index():
    """Serve the main web project editor"""
    try:
        with open('web_editor.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>Lizzy Screenplay Writer Studio</h1>
        <p>Main interface file not found. Please ensure web_editor.html exists.</p>
        """

# Get current project from environment variable (passed by lizzy.py)
current_project = os.environ.get('CURRENT_PROJECT', 'gamma')  # Fallback to gamma if not set

@app.route('/api/projects')
def get_projects():
    """Get list of available projects"""
    try:
        projects_dir = "projects"
        if not os.path.exists(projects_dir):
            return jsonify([])
        
        projects = []
        for entry in os.scandir(projects_dir):
            if entry.is_dir():
                db_path = os.path.join(entry.path, f"{entry.name}.sqlite")
                if os.path.exists(db_path):
                    projects.append(entry.name)
        
        return jsonify(projects)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_db_connection():
    """Get database connection"""
    db_path = f"projects/{current_project}/{current_project}.sqlite"
    if not os.path.exists(db_path):
        raise FileNotFoundError("Project database not found")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/tables/<table_name>')
def get_table_data(table_name):
    """Get data from specified table"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # Convert to list of dicts
        data = [dict(row) for row in rows]
        
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/characters')
def get_characters():
    """Get characters data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM characters")
        rows = cursor.fetchall()
        
        # Convert to list of dicts with proper field mapping
        data = []
        for row in rows:
            data.append({
                'id': row['id'],
                'name': row['name'] if 'name' in row.keys() else '',
                'archetype': row['archetype'] if 'archetype' in row.keys() else '',
                'gender': row['gender'] if 'gender' in row.keys() else '', 
                'age': row['age'] if 'age' in row.keys() else '',
                'challenge': row['romantic_challenge'] if 'romantic_challenge' in row.keys() else '',
                'trait': row['lovable_trait'] if 'lovable_trait' in row.keys() else '',
                'flaw': row['comedic_flaw'] if 'comedic_flaw' in row.keys() else '',
                'notes': row['notes'] if 'notes' in row.keys() else ''
            })
        
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/outline')
def get_outline():
    """Get story outline data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Use story_outline_extended table
        cursor.execute("SELECT * FROM story_outline_extended ORDER BY act_number, scene_number")
        rows = cursor.fetchall()
        
        # Convert to list of dicts with proper field mapping
        data = []
        for row in rows:
            data.append({
                'id': row['id'],
                'act': row['act'] if 'act' in row.keys() else row.get('act_number', 1),
                'scene': row['scene_number'] if 'scene_number' in row.keys() else 1,
                'beat': row['beat'] if 'beat' in row.keys() else '',
                'description': row['description'] if 'description' in row.keys() else '',
                'status': row['status'] if 'status' in row.keys() else 'pending',
                'key_characters': row['key_characters'] if 'key_characters' in row.keys() else '',
                'key_events': row['key_events'] if 'key_events' in row.keys() else ''
            })
        
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notes')
def get_notes():
    """Get notes data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if notes table exists, create if not
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notes'")
        if not cursor.fetchone():
            cursor.execute("""CREATE TABLE notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
            conn.commit()
        
        cursor.execute("SELECT * FROM notes ORDER BY created_at DESC")
        rows = cursor.fetchall()
        
        # Convert to list of dicts
        data = []
        for row in rows:
            data.append({
                'id': row['id'],
                'title': row['title'] if 'title' in row.keys() else '',
                'category': row['category'] if 'category' in row.keys() else '',
                'content': row['content'] if 'content' in row.keys() else ''
            })
        
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/brainstorm/sessions')
def get_brainstorm_sessions():
    """Get brainstorm sessions data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM brainstorming_log ORDER BY created_at DESC")
        rows = cursor.fetchall()
        
        # Group by session_id and aggregate
        sessions = {}
        for row in rows:
            session_id = row['session_id']
            if session_id not in sessions:
                sessions[session_id] = {
                    'session_id': session_id,
                    'status': 'completed',
                    'total_scenes': 0,
                    'buckets_used': row['bucket_selection'] or 'Various buckets',
                    'user_guidance': row['tone_preset']
                }
            sessions[session_id]['total_scenes'] += 1
        
        conn.close()
        return jsonify(list(sessions.values()))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/written-scenes')
def get_written_scenes():
    """Get written scenes data - placeholder for now"""
    try:
        # For now return empty array since we don't have a written scenes table
        return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/project/info')
def get_project_info():
    """Get project info and stats"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get counts from various tables
        cursor.execute("SELECT COUNT(*) as count FROM characters")
        characters_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM story_outline_extended")
        scenes_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM notes")
        notes_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(DISTINCT session_id) as count FROM brainstorming_log")
        brainstorm_count = cursor.fetchone()['count']
        
        project_info = {
            'name': current_project,
            'stats': {
                'characters': characters_count,
                'scenes': scenes_count,
                'notes': notes_count,
                'brainstorm_sessions': brainstorm_count,
                'written_scenes': 0  # Placeholder
            }
        }
        
        conn.close()
        return jsonify(project_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tables/<table_name>', methods=['POST'])
def add_table_row(table_name):
    """Add a new row to specified table"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build INSERT query based on data
        columns = list(data.keys())
        placeholders = ', '.join(['?' for _ in columns])
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        cursor.execute(query, list(data.values()))
        conn.commit()
        
        new_id = cursor.lastrowid
        conn.close()
        
        return jsonify({"id": new_id, "success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/<table_type>/<int:item_id>', methods=['PUT'])
def update_item(table_type, item_id):
    """Update an item in the database"""
    try:
        data = request.get_json()
        field = data.get('field')
        value = data.get('value')
        
        if not field or value is None:
            return jsonify({"error": "Missing field or value"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Map table types to actual table names and field mappings
        table_mappings = {
            'characters': {
                'table': 'characters',
                'fields': {
                    'name': 'name',
                    'archetype': 'archetype', 
                    'gender': 'gender',
                    'age': 'age',
                    'challenge': 'romantic_challenge',
                    'trait': 'lovable_trait'
                }
            },
            'outline': {
                'table': 'story_outline_extended',
                'fields': {
                    'act': 'act',
                    'scene': 'scene_number',
                    'beat': 'beat',
                    'description': 'description',
                    'status': 'status',
                    'key_characters': 'key_characters',
                    'key_events': 'key_events'
                }
            },
            'notes': {
                'table': 'notes',
                'fields': {
                    'title': 'title',
                    'category': 'category',
                    'content': 'content'
                }
            }
        }
        
        if table_type not in table_mappings:
            return jsonify({"error": "Invalid table type"}), 400
        
        mapping = table_mappings[table_type]
        table_name = mapping['table']
        db_field = mapping['fields'].get(field, field)
        
        # Update the database
        query = f"UPDATE {table_name} SET {db_field} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        cursor.execute(query, (value, item_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Item not found"}), 404
        
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Lizzy Web Editor Server on port 8080...")
    print(f"📁 Current project: {current_project}")
    print("📋 Available endpoints:")
    print("  GET /api/characters - Get characters")
    print("  GET /api/outline - Get story outline")
    print("  GET /api/notes - Get notes")
    print("  GET /api/brainstorm/sessions - Get brainstorm sessions")
    print("  GET /api/written-scenes - Get written scenes")
    print("  GET /api/project/info - Get project info and stats")
    print("  PUT /api/<type>/<id> - Update item")
    app.run(host='localhost', port=8080, debug=True)