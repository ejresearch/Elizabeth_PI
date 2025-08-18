"""
Refactored Brainstorm Backend using standardized Lizzy API base
AI brainstorming interface with conversation management
"""

import os
import re
from datetime import datetime
from flask import request
from lizzy_api_base import LizzyAPIBase, create_standardized_app
from lizzy_shared import (
    handle_api_errors, validate_request_data, 
    project_manager, response_handler, validator, ValidationError
)

# Create Flask app with standard configuration
app = create_standardized_app(__name__)

# Initialize standardized API
api = LizzyAPIBase(app)

@app.route('/')
def index():
    """Serve the brainstorm interface"""
    try:
        with open('brainstorm_seamless.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>Lizzy Creative Brainstorm Studio</h1>
        <p>Brainstorm interface file not found. Please ensure brainstorm_seamless.html exists.</p>
        <p><a href="/api/projects">View Available Projects</a></p>
        """

@app.route('/api/chat', methods=['POST'])
@handle_api_errors
@validate_request_data(
    ['project_name', 'user_message'], 
    ['template_id', 'conversation_id', 'format', 'api_key']
)
def enhanced_chat():
    """Enhanced chat with structured markdown output"""
    data = request.validated_data
    project_name = validator.validate_project_name(data['project_name'])
    user_message = data['user_message'].strip()
    template_id = data.get('template_id')
    conversation_id = data.get('conversation_id')
    format_type = data.get('format', 'markdown_lists')
    
    if not user_message:
        raise ValidationError("Message cannot be empty")
    
    # Get API key from environment or request
    api_key = data.get('api_key') or os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValidationError("OpenAI API key not configured")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
    except ImportError:
        raise ValidationError("OpenAI library not installed")
    
    # Build conversation with enhanced formatting instructions
    messages = []
    
    # Add system prompt with formatting instructions
    if template_id:
        template_query = "SELECT template FROM custom_prompts WHERE id = ?"
        templates = project_manager.db_manager.execute_query(project_name, template_query, (template_id,))
        
        if templates:
            template = templates[0]['template']
            compiled_template = compile_template_with_data(template, project_name)
            
            # Add formatting instructions for structured output
            if format_type == 'markdown_lists':
                compiled_template += "\n\nIMPORTANT: Structure your response using clear markdown formatting:\n- Use ## for main sections\n- Use ### for subsections\n- Use bullet points (*) for lists\n- Use numbered lists (1. 2. 3.) for sequences\n- Use **bold** for emphasis\n- Organize ideas into scannable lists rather than long paragraphs"
            
            messages.append({
                "role": "system",
                "content": compiled_template
            })
    
    # Add user message
    messages.append({
        "role": "user",
        "content": user_message
    })
    
    # Call OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        ai_response = response.choices[0].message.content
        
        # Save to conversation if conversation_id provided
        if conversation_id:
            save_message_to_conversation(project_name, conversation_id, user_message, ai_response)
        
        # Increment template usage count
        if template_id:
            usage_query = "UPDATE custom_prompts SET use_count = use_count + 1 WHERE id = ?"
            project_manager.db_manager.execute_update(project_name, usage_query, (template_id,))
        
        return response_handler.success({
            "response": ai_response,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        raise ValidationError(f"AI service error: {str(e)}")

def compile_template_with_data(template: str, project_name: str) -> str:
    """Compile template with real project data"""
    compiled = template
    
    # Replace context variables
    compiled = compiled.replace('{context.project.name}', project_name)
    compiled = compiled.replace('{context.timestamp}', datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    # Replace SQL table variables with formatted data
    sql_vars = re.findall(r'{sql\.(\w+)}', template)
    for table in sql_vars:
        try:
            data = project_manager.get_table_data(project_name, table, limit=5)
            
            if data['rows']:
                formatted_data = f"=== {table.upper()} DATA ===\n"
                for i, row in enumerate(data['rows']):
                    if table == 'characters':
                        char_info = []
                        if 'name' in row: char_info.append(f"Name: {row['name']}")
                        if 'romantic_challenge' in row: char_info.append(f"Challenge: {row['romantic_challenge']}")
                        if 'lovable_trait' in row: char_info.append(f"Trait: {row['lovable_trait']}")
                        formatted_data += f"Character {i+1}: {' | '.join(char_info)}\n"
                    elif table == 'story_outline':
                        scene_info = []
                        if 'act' in row: scene_info.append(f"Act {row['act']}")
                        if 'scene' in row: scene_info.append(f"Scene {row['scene']}")
                        if 'key_events' in row: scene_info.append(row['key_events'])
                        formatted_data += f"Scene {i+1}: {' - '.join(scene_info)}\n"
                    else:
                        # Generic display for any table
                        key_fields = [k for k in row.keys() if k not in ['id', 'created_at', 'updated_at']][:3]
                        formatted_data += f"Row {i+1}: " + " | ".join([f"{k}: {row.get(k, 'N/A')}" for k in key_fields]) + "\n"
                
                compiled = compiled.replace(f'{{sql.{table}}}', formatted_data.strip())
            else:
                compiled = compiled.replace(f'{{sql.{table}}}', f"No data in {table} table")
                
        except Exception as e:
            compiled = compiled.replace(f'{{sql.{table}}}', f"Error accessing {table}: {str(e)}")
    
    return compiled

def save_message_to_conversation(project_name: str, conversation_id: int, user_message: str, ai_response: str):
    """Save messages to existing conversation"""
    # Add user message
    user_query = """
        INSERT INTO conversation_messages (conversation_id, role, content)
        VALUES (?, ?, ?)
    """
    project_manager.db_manager.execute_update(project_name, user_query, (conversation_id, 'user', user_message))
    
    # Add AI response
    ai_query = """
        INSERT INTO conversation_messages (conversation_id, role, content)
        VALUES (?, ?, ?)
    """
    project_manager.db_manager.execute_update(project_name, ai_query, (conversation_id, 'assistant', ai_response))
    
    # Update conversation metadata
    update_query = """
        UPDATE conversations 
        SET message_count = (
            SELECT COUNT(*) FROM conversation_messages 
            WHERE conversation_id = ?
        ), updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """
    project_manager.db_manager.execute_update(project_name, update_query, (conversation_id, conversation_id))

@app.route('/api/conversation/autosave', methods=['POST'])
@handle_api_errors
@validate_request_data(['project_name'], ['conversation_id', 'messages', 'template_id'])
def autosave_conversation():
    """Auto-save conversation in progress"""
    data = request.validated_data
    project_name = validator.validate_project_name(data['project_name'])
    conversation_id = data.get('conversation_id')
    messages = data.get('messages', [])
    template_id = data.get('template_id')
    
    # If no conversation_id, create new conversation
    if not conversation_id and messages:
        conversation_data = {
            'title': f'Auto-saved {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            'messages': messages,
            'template_id': template_id,
            'template_name': 'Auto-saved'
        }
        
        # Use the standardized conversation creation
        validated_data = validator.validate_conversation_data(conversation_data)
        
        conv_query = """
            INSERT INTO conversations (title, template_id, template_name, message_count)
            VALUES (?, ?, ?, ?)
        """
        project_manager.db_manager.execute_update(
            project_name, conv_query,
            (validated_data['title'], validated_data.get('template_id'), 
             validated_data.get('template_name'), len(validated_data['messages']))
        )
        
        # Get the conversation ID
        conv_id_query = "SELECT last_insert_rowid() as id"
        result = project_manager.db_manager.execute_query(project_name, conv_id_query)
        conversation_id = result[0]['id']
        
        # Insert messages
        msg_query = """
            INSERT INTO conversation_messages (conversation_id, role, content)
            VALUES (?, ?, ?)
        """
        for msg in validated_data['messages']:
            project_manager.db_manager.execute_update(
                project_name, msg_query,
                (conversation_id, msg['role'], msg['content'])
            )
    
    return response_handler.success({"conversation_id": conversation_id})

@app.route('/api/project/<project_name>/conversations/<int:conversation_id>/messages', methods=['GET'])
@handle_api_errors
def get_conversation_messages(project_name, conversation_id):
    """Get messages for a specific conversation"""
    project_name = validator.validate_project_name(project_name)
    
    query = """
        SELECT role, content, timestamp
        FROM conversation_messages
        WHERE conversation_id = ?
        ORDER BY timestamp ASC
    """
    messages = project_manager.db_manager.execute_query(project_name, query, (conversation_id,))
    
    return response_handler.success({"messages": messages})

if __name__ == '__main__':
    print("🧠 Starting Lizzy Creative Brainstorm Studio...")
    print("💭 AI-powered creative brainstorming for screenplay scenes")
    print("🔗 http://localhost:5001")
    app.run(debug=True, port=5001)