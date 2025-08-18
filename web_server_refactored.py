"""
Refactored Web Server using standardized Lizzy API base
Main project data curation interface
"""

from flask import render_template_string, jsonify
from lizzy_api_base import LizzyAPIBase, create_standardized_app
from lizzy_shared import handle_api_errors, project_manager, response_handler

# Create Flask app with standard configuration
app = create_standardized_app(__name__)

# Initialize standardized API
api = LizzyAPIBase(app)

@app.route('/')
def index():
    """Serve the main web project editor"""
    try:
        with open('web_project_editor.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>Lizzy Screenplay Writer Studio</h1>
        <p>Main interface file not found. Please ensure web_project_editor.html exists.</p>
        <p><a href="/api/projects">View Available Projects</a></p>
        """

# Get current project from session or use default
current_project = 'gamma'  # Default project - should be managed via session in production

# Direct table endpoints for web_project_editor.html
@app.route('/api/characters', methods=['GET'])
@handle_api_errors
def get_characters():
    """Get characters data"""
    query = "SELECT * FROM characters"
    characters = project_manager.db_manager.execute_query(current_project, query)
    
    # Map database fields to expected UI fields
    for char in characters:
        char['challenge'] = char.get('romantic_challenge', '')
        char['trait'] = char.get('lovable_trait', '')
    
    return jsonify(characters)

@app.route('/api/outline', methods=['GET'])
@handle_api_errors  
def get_outline():
    """Get story outline data"""
    query = "SELECT * FROM story_outline_extended"
    outline = project_manager.db_manager.execute_query(current_project, query)
    
    # Map database fields to expected UI fields
    for scene in outline:
        scene['scene'] = scene.get('scene_number', '')
    
    return jsonify(outline)

@app.route('/api/notes', methods=['GET'])
@handle_api_errors
def get_notes():
    """Get project notes"""
    query = "SELECT * FROM notes"
    notes = project_manager.db_manager.execute_query(current_project, query)
    return jsonify(notes)

@app.route('/api/brainstorm/sessions', methods=['GET'])
@handle_api_errors
def get_brainstorm_sessions():
    """Get brainstorm sessions"""
    query = "SELECT * FROM brainstorming_log ORDER BY created_at DESC"
    sessions = project_manager.db_manager.execute_query(current_project, query)
    return jsonify(sessions)

@app.route('/api/written-scenes', methods=['GET'])
@handle_api_errors
def get_written_scenes():
    """Get written scenes"""
    query = "SELECT * FROM finalized_draft_v1"
    scenes = project_manager.db_manager.execute_query(current_project, query)
    return jsonify(scenes)

@app.route('/api/project/info', methods=['GET'])
@handle_api_errors
def get_current_project_info():
    """Get current project info and stats"""
    # Get table statistics directly
    tables_query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    tables = project_manager.db_manager.execute_query(current_project, tables_query)
    
    table_stats = {}
    for table in tables:
        table_name = table['name']
        count_query = f"SELECT COUNT(*) as count FROM {table_name}"
        count_result = project_manager.db_manager.execute_query(current_project, count_query)
        table_stats[table_name] = count_result[0]['count'] if count_result else 0
    
    # Build stats from table data
    stats = {
        'characters': table_stats.get('characters', 0),
        'scenes': table_stats.get('story_outline_extended', 0),
        'notes': table_stats.get('notes', 0),
        'brainstorm_sessions': table_stats.get('brainstorming_log', 0),
        'written_scenes': table_stats.get('finalized_draft_v1', 0)
    }
    
    return jsonify({'project_name': current_project, 'stats': stats})

# Additional project-specific endpoints
@app.route('/api/project/<project_name>/schema', methods=['GET'])
@handle_api_errors
def get_project_schema(project_name):
    """Get project schema for dynamic UI generation"""
    info = project_manager.get_project_info(project_name)
    
    # Build schema information
    schema = {
        'project_name': project_name,
        'tables': {},
        'data_blocks': {'sql': [], 'lightrag': [], 'context': []}
    }
    
    # Get table details
    for table_name, row_count in info['tables'].items():
        if table_name.startswith('sqlite_'):
            continue
            
        # Get column info
        query = f"PRAGMA table_info({table_name})"
        columns = project_manager.db_manager.execute_query(project_name, query)
        
        schema['tables'][table_name] = {
            'row_count': row_count,
            'columns': [col['name'] for col in columns]
        }
        
        # Create data blocks for SQL tables
        schema['data_blocks']['sql'].append({
            'key': f'sql.{table_name}',
            'label': table_name.replace('_', ' ').title(),
            'description': f'{row_count} rows from {table_name} table',
            'sample': f'Recent {table_name} data...'
        })
    
    # Add context blocks
    schema['data_blocks']['context'].extend([
        {
            'key': 'context.project.name',
            'label': 'Project Name',
            'description': 'Current project name',
            'sample': project_name
        },
        {
            'key': 'context.timestamp',
            'label': 'Current Time',
            'description': 'Current timestamp',
            'sample': 'Current date and time'
        }
    ])
    
    return response_handler.success(schema)

if __name__ == '__main__':
    print("✍️ Starting Lizzy Screenplay Writer Studio...")
    print("🎬 Professional screenplay writing and scene development")
    print("🔗 http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)