"""
Refactored Web Server using standardized Lizzy API base
Main project data curation interface
"""

from flask import render_template_string
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
        <h1>Lizzy Web Project Editor</h1>
        <p>Main interface file not found. Please ensure web_project_editor.html exists.</p>
        <p><a href="/api/projects">View Available Projects</a></p>
        """

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
    print("🌐 Starting Lizzy Web Project Editor...")
    print("📊 Data curation and project management interface")
    print("🔗 http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)