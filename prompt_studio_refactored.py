"""
Refactored Prompt Studio using standardized Lizzy API base
Template creation and management interface
"""

import re
from flask import request
from lizzy_api_base import LizzyAPIBase, create_standardized_app
from lizzy_shared import (
    handle_api_errors, validate_request_data, 
    project_manager, response_handler, validator
)

# Create Flask app with standard configuration
app = create_standardized_app(__name__)

# Initialize standardized API
api = LizzyAPIBase(app)

@app.route('/')
def index():
    """Serve the prompt studio interface"""
    try:
        with open('prompt_studio_dynamic.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>Lizzy Prompt Studio</h1>
        <p>Template interface file not found. Please ensure prompt_studio_dynamic.html exists.</p>
        <p><a href="/api/projects">View Available Projects</a></p>
        """

@app.route('/api/compile-prompt', methods=['POST'])
@handle_api_errors
@validate_request_data(['project_name', 'template'])
def compile_prompt():
    """Compile a prompt template with real project data"""
    data = request.validated_data
    project_name = validator.validate_project_name(data['project_name'])
    template = data['template']
    
    compiled = compile_template_with_data(template, project_name)
    
    return response_handler.success({
        'original': template,
        'compiled': compiled,
        'length': len(compiled)
    })

def compile_template_with_data(template: str, project_name: str) -> str:
    """Compile template with real project data"""
    compiled = template
    
    # Replace context variables
    compiled = compiled.replace('{context.project.name}', project_name)
    compiled = compiled.replace('{context.timestamp}', str(datetime.now()))
    
    # Replace SQL table variables with formatted data
    sql_vars = re.findall(r'{sql\.(\w+)}', template)
    for table in sql_vars:
        try:
            data = project_manager.get_table_data(project_name, table, limit=5)
            
            if data['rows']:
                formatted_data = f"=== {table.upper()} DATA ===\n"
                for i, row in enumerate(data['rows']):
                    if table == 'characters' and 'name' in row:
                        formatted_data += f"Character {i+1}: {row.get('name', 'N/A')} - {row.get('romantic_challenge', 'N/A')}\n"
                    elif table == 'story_outline' and 'key_events' in row:
                        formatted_data += f"Scene {i+1}: Act {row.get('act', 'N/A')}, Scene {row.get('scene', 'N/A')} - {row.get('key_events', 'N/A')}\n"
                    else:
                        # Generic display for any table
                        key_fields = [k for k in row.keys() if k not in ['id', 'created_at', 'updated_at']][:2]
                        formatted_data += f"Row {i+1}: " + " | ".join([f"{k}: {row.get(k, 'N/A')}" for k in key_fields]) + "\n"
                
                compiled = compiled.replace(f'{{sql.{table}}}', formatted_data.strip())
            else:
                compiled = compiled.replace(f'{{sql.{table}}}', f"No data in {table} table")
                
        except Exception as e:
            compiled = compiled.replace(f'{{sql.{table}}}', f"Error accessing {table}: {str(e)}")
    
    # Replace LightRAG variables with placeholder
    lightrag_vars = re.findall(r'{lightrag\.(\w+)}', template)
    for bucket in lightrag_vars:
        compiled = compiled.replace(f'{{lightrag.{bucket}}}', f"[LightRAG {bucket} knowledge will be inserted here]")
    
    return compiled

@app.route('/api/project/<project_name>/template-stats', methods=['GET'])
@handle_api_errors
def get_template_stats(project_name):
    """Get template usage statistics"""
    project_name = validator.validate_project_name(project_name)
    
    # Get prompt counts by category
    category_query = """
        SELECT category, COUNT(*) as count 
        FROM custom_prompts 
        GROUP BY category
    """
    categories = project_manager.db_manager.execute_query(project_name, category_query)
    
    # Get most used prompts
    popular_query = """
        SELECT name, use_count 
        FROM custom_prompts 
        WHERE use_count > 0
        ORDER BY use_count DESC 
        LIMIT 5
    """
    popular = project_manager.db_manager.execute_query(project_name, popular_query)
    
    # Get recent prompts
    recent_query = """
        SELECT name, created_at 
        FROM custom_prompts 
        ORDER BY created_at DESC 
        LIMIT 5
    """
    recent = project_manager.db_manager.execute_query(project_name, recent_query)
    
    stats = {
        'categories': categories,
        'popular_prompts': popular,
        'recent_prompts': recent,
        'total_prompts': sum(cat['count'] for cat in categories)
    }
    
    return response_handler.success(stats)

@app.route('/api/project/<project_name>/prompts/<int:prompt_id>/usage', methods=['POST'])
@handle_api_errors
def increment_prompt_usage(project_name, prompt_id):
    """Increment usage count for a prompt"""
    project_name = validator.validate_project_name(project_name)
    
    query = "UPDATE custom_prompts SET use_count = use_count + 1 WHERE id = ?"
    rows_affected = project_manager.db_manager.execute_update(project_name, query, (prompt_id,))
    
    if rows_affected == 0:
        return response_handler.error("Prompt not found", "PROMPT_NOT_FOUND"), 404
    
    return response_handler.success(message="Usage count updated")

if __name__ == '__main__':
    print("📝 Starting Lizzy Prompt Studio...")
    print("🎨 Template creation and management interface")
    print("🔗 http://localhost:8002")
    app.run(host='0.0.0.0', port=8002, debug=True)