"""
Enhanced Brainstorm Backend with Conversation Saving and SQL Editor
"""

import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from typing import Dict, List, Any, Optional

app = Flask(__name__)
CORS(app)

class BrainstormManager:
    """Manages brainstorm conversations and templates"""
    
    def __init__(self, projects_dir='exports'):
        self.projects_dir = projects_dir
    
    def setup_conversation_tables(self, cursor):
        """Create tables for storing conversations"""
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                template_id INTEGER,
                template_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                tags TEXT,
                starred BOOLEAN DEFAULT 0
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tokens INTEGER DEFAULT 0,
                metadata TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
            )
        ''')
        
        # Template categories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS template_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                color TEXT,
                icon TEXT
            )
        ''')
        
        # Enhanced prompts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_prompts_enhanced (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                template TEXT NOT NULL,
                description TEXT,
                category_id INTEGER,
                category TEXT DEFAULT 'custom',
                owner TEXT DEFAULT 'user',
                is_system BOOLEAN DEFAULT 0,
                is_shared BOOLEAN DEFAULT 0,
                use_count INTEGER DEFAULT 0,
                word_count INTEGER DEFAULT 0,
                variables TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES template_categories (id)
            )
        ''')
        
        # SQL query history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sql_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                result_count INTEGER,
                execution_time INTEGER,
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Saved SQL queries
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                query TEXT NOT NULL,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def save_conversation(self, project_name: str, conversation_data: Dict) -> int:
        """Save a conversation to the database"""
        db_path = os.path.join(self.projects_dir, project_name, f"{project_name}.sqlite")
        
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Project database not found: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        self.setup_conversation_tables(cursor)
        
        # Insert conversation
        cursor.execute('''
            INSERT INTO conversations (title, template_id, template_name, message_count, tags)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            conversation_data.get('title', f'Chat {datetime.now().strftime("%Y-%m-%d %H:%M")}'),
            conversation_data.get('template_id'),
            conversation_data.get('template_name'),
            len(conversation_data.get('messages', [])),
            json.dumps(conversation_data.get('tags', []))
        ))
        
        conversation_id = cursor.lastrowid
        
        # Insert messages
        for message in conversation_data.get('messages', []):
            cursor.execute('''
                INSERT INTO conversation_messages (conversation_id, role, content, tokens)
                VALUES (?, ?, ?, ?)
            ''', (
                conversation_id,
                message['role'],
                message['content'],
                len(message['content']) // 4  # Rough token estimate
            ))
        
        conn.commit()
        conn.close()
        
        return conversation_id
    
    def get_conversations(self, project_name: str, limit: int = 50) -> List[Dict]:
        """Get conversation history"""
        db_path = os.path.join(self.projects_dir, project_name, f"{project_name}.sqlite")
        
        if not os.path.exists(db_path):
            return []
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        self.setup_conversation_tables(cursor)
        
        # Get conversations
        cursor.execute('''
            SELECT id, title, template_name, created_at, message_count, starred
            FROM conversations
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        conversations = []
        for row in cursor.fetchall():
            conv_id = row[0]
            
            # Get messages
            cursor.execute('''
                SELECT role, content, timestamp
                FROM conversation_messages
                WHERE conversation_id = ?
                ORDER BY timestamp
            ''', (conv_id,))
            
            messages = [
                {'role': msg[0], 'content': msg[1], 'timestamp': msg[2]}
                for msg in cursor.fetchall()
            ]
            
            conversations.append({
                'id': conv_id,
                'title': row[1],
                'template_name': row[2],
                'created_at': row[3],
                'message_count': row[4],
                'starred': row[5],
                'messages': messages
            })
        
        conn.close()
        return conversations
    
    def get_conversation(self, project_name: str, conversation_id: int) -> Optional[Dict]:
        """Get a specific conversation"""
        db_path = os.path.join(self.projects_dir, project_name, f"{project_name}.sqlite")
        
        if not os.path.exists(db_path):
            return None
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, template_name, created_at, message_count, starred, tags
            FROM conversations
            WHERE id = ?
        ''', (conversation_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        # Get messages
        cursor.execute('''
            SELECT role, content, timestamp, tokens
            FROM conversation_messages
            WHERE conversation_id = ?
            ORDER BY timestamp
        ''', (conversation_id,))
        
        messages = [
            {
                'role': msg[0],
                'content': msg[1],
                'timestamp': msg[2],
                'tokens': msg[3]
            }
            for msg in cursor.fetchall()
        ]
        
        conversation = {
            'id': row[0],
            'title': row[1],
            'template_name': row[2],
            'created_at': row[3],
            'message_count': row[4],
            'starred': row[5],
            'tags': json.loads(row[6]) if row[6] else [],
            'messages': messages
        }
        
        conn.close()
        return conversation
    
    def delete_conversation(self, project_name: str, conversation_id: int) -> bool:
        """Delete a conversation"""
        db_path = os.path.join(self.projects_dir, project_name, f"{project_name}.sqlite")
        
        if not os.path.exists(db_path):
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def execute_sql(self, project_name: str, query: str) -> Dict:
        """Execute SQL query on project database"""
        db_path = os.path.join(self.projects_dir, project_name, f"{project_name}.sqlite")
        
        if not os.path.exists(db_path):
            return {'error': 'Project database not found'}
        
        # Security: Only allow SELECT queries
        if not query.strip().upper().startswith('SELECT'):
            return {'error': 'Only SELECT queries are allowed'}
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        start_time = datetime.now()
        
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Convert to dict
            results = [dict(row) for row in rows]
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Save to history
            cursor.execute('''
                INSERT INTO sql_history (query, result_count, execution_time)
                VALUES (?, ?, ?)
            ''', (query, len(results), int(execution_time)))
            
            conn.commit()
            conn.close()
            
            return {
                'results': results,
                'count': len(results),
                'execution_time': execution_time
            }
            
        except Exception as e:
            conn.close()
            return {'error': str(e)}
    
    def save_sql_query(self, project_name: str, query_data: Dict) -> int:
        """Save a SQL query for later use"""
        db_path = os.path.join(self.projects_dir, project_name, f"{project_name}.sqlite")
        
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Project database not found")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        self.setup_conversation_tables(cursor)
        
        cursor.execute('''
            INSERT INTO saved_queries (name, description, query, tags)
            VALUES (?, ?, ?, ?)
        ''', (
            query_data.get('name'),
            query_data.get('description', ''),
            query_data.get('query'),
            json.dumps(query_data.get('tags', []))
        ))
        
        query_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return query_id
    
    def get_saved_queries(self, project_name: str) -> List[Dict]:
        """Get saved SQL queries"""
        db_path = os.path.join(self.projects_dir, project_name, f"{project_name}.sqlite")
        
        if not os.path.exists(db_path):
            return []
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        self.setup_conversation_tables(cursor)
        
        cursor.execute('''
            SELECT id, name, description, query, tags, created_at
            FROM saved_queries
            ORDER BY created_at DESC
        ''')
        
        queries = []
        for row in cursor.fetchall():
            queries.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'query': row[3],
                'tags': json.loads(row[4]) if row[4] else [],
                'created_at': row[5]
            })
        
        conn.close()
        return queries


# Initialize manager
manager = BrainstormManager()

# API Routes
@app.route('/api/project/<project_name>/conversations', methods=['GET'])
def get_conversations(project_name):
    """Get conversation history"""
    try:
        conversations = manager.get_conversations(project_name)
        return jsonify({'conversations': conversations})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/project/<project_name>/conversations', methods=['POST'])
def save_conversation(project_name):
    """Save a new conversation"""
    try:
        data = request.json
        conversation_id = manager.save_conversation(project_name, data)
        return jsonify({'id': conversation_id, 'message': 'Conversation saved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/project/<project_name>/conversations/<int:conversation_id>', methods=['GET'])
def get_conversation(project_name, conversation_id):
    """Get a specific conversation"""
    try:
        conversation = manager.get_conversation(project_name, conversation_id)
        if conversation:
            return jsonify(conversation)
        else:
            return jsonify({'error': 'Conversation not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/project/<project_name>/conversations/<int:conversation_id>', methods=['DELETE'])
def delete_conversation(project_name, conversation_id):
    """Delete a conversation"""
    try:
        success = manager.delete_conversation(project_name, conversation_id)
        if success:
            return jsonify({'message': 'Conversation deleted'})
        else:
            return jsonify({'error': 'Conversation not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sql/execute', methods=['POST'])
def execute_sql():
    """Execute SQL query"""
    try:
        data = request.json
        project_name = data.get('project_name')
        query = data.get('query')
        
        if not project_name or not query:
            return jsonify({'error': 'Missing project_name or query'}), 400
        
        result = manager.execute_sql(project_name, query)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sql/save', methods=['POST'])
def save_sql_query():
    """Save SQL query"""
    try:
        data = request.json
        project_name = data.get('project_name')
        
        if not project_name:
            return jsonify({'error': 'Missing project_name'}), 400
        
        query_id = manager.save_sql_query(project_name, data)
        return jsonify({'id': query_id, 'message': 'Query saved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sql/saved', methods=['GET'])
def get_saved_queries():
    """Get saved SQL queries"""
    try:
        project_name = request.args.get('project_name')
        
        if not project_name:
            return jsonify({'error': 'Missing project_name'}), 400
        
        queries = manager.get_saved_queries(project_name)
        return jsonify({'queries': queries})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Enhanced Chat Endpoint with Structured Output
@app.route('/api/chat', methods=['POST'])
def enhanced_chat():
    """Enhanced chat with structured markdown output"""
    data = request.json
    project_name = data.get('project_name')
    template_id = data.get('template_id')
    user_message = data.get('user_message')
    conversation_id = data.get('conversation_id')
    format_type = data.get('format', 'markdown_lists')
    
    if not project_name or not user_message:
        return jsonify({"error": "Missing project_name or user_message"}), 400
    
    try:
        # Get API key from environment or request
        import os
        api_key = data.get('api_key') or os.getenv('OPENAI_API_KEY')
        if not api_key:
            return jsonify({"error": "OpenAI API key not configured"}), 500
        
        # Initialize OpenAI client
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Build conversation with enhanced formatting instructions
        messages = []
        
        # Add system prompt with formatting instructions
        if template_id:
            db_path = os.path.join(manager.projects_dir, project_name, f"{project_name}.sqlite")
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get template
                cursor.execute('SELECT template FROM custom_prompts WHERE id = ?', (template_id,))
                result = cursor.fetchone()
                
                if result:
                    template = result[0]
                    
                    # Compile template with real project data
                    compiled_template = compile_template_with_data(template, project_name, conn)
                    
                    # Add formatting instructions
                    if format_type == 'markdown_lists':
                        compiled_template += "\n\nIMPORTANT: Structure your response using markdown formatting with clear headings and bullet points. Use:\n- ## for main sections\n- ### for subsections\n- * or - for bullet points\n- 1. 2. 3. for numbered lists\n- **bold** for emphasis\n\nOrganize ideas into clear, scannable lists rather than long paragraphs."
                    
                    messages.append({
                        "role": "system",
                        "content": compiled_template
                    })
                
                conn.close()
        
        # Add user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Call OpenAI
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
        
        return jsonify({
            "response": ai_response,
            "conversation_id": conversation_id
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def compile_template_with_data(template, project_name, conn):
    """Compile template with real project data"""
    compiled = template
    
    # Replace context variables
    compiled = compiled.replace('{context.project.name}', project_name)
    
    # Replace SQL table variables with formatted data
    import re
    sql_vars = re.findall(r'{sql\.(\w+)}', template)
    for table in sql_vars:
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table} LIMIT 5")
            rows = cursor.fetchall()
            
            if rows:
                # Get column names
                column_names = [description[0] for description in cursor.description]
                
                # Format as readable text
                formatted_data = f"=== {table.upper()} DATA ===\n"
                for i, row in enumerate(rows):
                    if table == 'characters':
                        formatted_data += f"Character {i+1}: {dict(zip(column_names, row))}\n"
                    elif table == 'story_outline':
                        formatted_data += f"Scene {i+1}: {dict(zip(column_names, row))}\n"
                    else:
                        formatted_data += f"Row {i+1}: {dict(zip(column_names, row))}\n"
                
                compiled = compiled.replace(f'{{sql.{table}}}', formatted_data.strip())
            else:
                compiled = compiled.replace(f'{{sql.{table}}}', f"No data in {table} table")
                
        except Exception as e:
            compiled = compiled.replace(f'{{sql.{table}}}', f"Error accessing {table}: {str(e)}")
    
    return compiled

def save_message_to_conversation(project_name, conversation_id, user_message, ai_response):
    """Save messages to existing conversation"""
    db_path = os.path.join(manager.projects_dir, project_name, f"{project_name}.sqlite")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add user message
    cursor.execute('''
        INSERT INTO conversation_messages (conversation_id, role, content)
        VALUES (?, ?, ?)
    ''', (conversation_id, 'user', user_message))
    
    # Add AI response
    cursor.execute('''
        INSERT INTO conversation_messages (conversation_id, role, content)
        VALUES (?, ?, ?)
    ''', (conversation_id, 'assistant', ai_response))
    
    # Update conversation message count
    cursor.execute('''
        UPDATE conversations 
        SET message_count = (
            SELECT COUNT(*) FROM conversation_messages 
            WHERE conversation_id = ?
        ), updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (conversation_id, conversation_id))
    
    conn.commit()
    conn.close()

# Auto-save endpoint
@app.route('/api/conversation/autosave', methods=['POST'])
def autosave_conversation():
    """Auto-save conversation in progress"""
    data = request.json
    project_name = data.get('project_name')
    conversation_id = data.get('conversation_id')
    messages = data.get('messages', [])
    template_id = data.get('template_id')
    
    if not project_name:
        return jsonify({"error": "Missing project_name"}), 400
    
    try:
        # If no conversation_id, create new conversation
        if not conversation_id:
            conversation_data = {
                'title': f'Auto-saved {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                'messages': messages,
                'template_id': template_id,
                'template_name': 'Auto-saved'
            }
            conversation_id = manager.save_conversation(project_name, conversation_data)
        else:
            # Update existing conversation
            save_message_to_conversation(project_name, conversation_id, 
                                       messages[-2]['content'] if len(messages) >= 2 else '',
                                       messages[-1]['content'] if messages else '')
        
        return jsonify({"conversation_id": conversation_id})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Table update endpoint
@app.route('/api/table/update', methods=['POST'])
def update_table_cell():
    """Update a table cell"""
    data = request.json
    project_name = data.get('project_name')
    table = data.get('table')
    row_id = data.get('row_id')
    column = data.get('column')
    value = data.get('value')
    
    if not all([project_name, table, column]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    try:
        db_path = os.path.join(manager.projects_dir, project_name, f"{project_name}.sqlite")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Update the cell
        cursor.execute(f'''
            UPDATE {table} 
            SET {column} = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (value, row_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Cell updated successfully"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get table data endpoint
@app.route('/api/project/<project_name>/table/<table_name>', methods=['GET'])
def get_table_data(project_name, table_name):
    """Get table data for editing"""
    try:
        db_path = os.path.join(manager.projects_dir, project_name, f"{project_name}.sqlite")
        
        if not os.path.exists(db_path):
            return jsonify({"error": "Project not found"}), 404
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 100")
        rows = cursor.fetchall()
        
        # Convert to dict
        table_data = {
            'table': table_name,
            'rows': [dict(row) for row in rows]
        }
        
        conn.close()
        return jsonify(table_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/brainstorm-enhanced')
def brainstorm_enhanced():
    """Serve the enhanced brainstorm interface"""
    return render_template('brainstorm_enhanced.html')

@app.route('/brainstorm-seamless')
def brainstorm_seamless():
    """Serve the seamless brainstorm interface"""
    with open('brainstorm_seamless.html', 'r') as f:
        return f.read()

if __name__ == '__main__':
    app.run(debug=True, port=5001)