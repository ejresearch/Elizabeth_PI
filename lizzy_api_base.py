"""
Standardized API Base for Lizzy System
Provides consistent endpoints and error handling across all services
"""

from flask import Flask, jsonify, request
from lizzy_shared import (
    handle_api_errors, validate_request_data, 
    project_manager, response_handler, validator
)

class LizzyAPIBase:
    """Base class for Lizzy API services with standardized endpoints"""
    
    def __init__(self, app: Flask, url_prefix: str = '/api'):
        self.app = app
        self.url_prefix = url_prefix
        self.register_common_routes()
    
    def register_common_routes(self):
        """Register common endpoints that all services need"""
        
        @self.app.route(f'{self.url_prefix}/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify(response_handler.success({"status": "healthy", "service": "lizzy"}))
        
        @self.app.route(f'{self.url_prefix}/projects', methods=['GET'])
        @handle_api_errors
        def list_projects():
            """List all available projects"""
            projects = project_manager.db_manager.get_projects_list()
            return jsonify(response_handler.success({"projects": projects}))
        
        @self.app.route(f'{self.url_prefix}/project/<project_name>/info', methods=['GET'])
        @handle_api_errors
        def get_project_info(project_name):
            """Get project information and statistics"""
            info = project_manager.get_project_info(project_name)
            return jsonify(response_handler.success(info))
        
        @self.app.route(f'{self.url_prefix}/project/<project_name>/tables', methods=['GET'])
        @handle_api_errors
        def list_project_tables(project_name):
            """List all tables in a project"""
            project_name = validator.validate_project_name(project_name)
            
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            tables = project_manager.db_manager.execute_query(project_name, query)
            
            return jsonify(response_handler.success({"tables": [t['name'] for t in tables]}))
        
        @self.app.route(f'{self.url_prefix}/project/<project_name>/table/<table_name>', methods=['GET'])
        @handle_api_errors
        def get_table_data(project_name, table_name):
            """Get table data with pagination"""
            limit = request.args.get('limit', 100, type=int)
            limit = min(limit, 1000)  # Cap at 1000 rows
            
            data = project_manager.get_table_data(project_name, table_name, limit)
            return jsonify(response_handler.success(data))
        
        @self.app.route(f'{self.url_prefix}/project/<project_name>/table/<table_name>/update', methods=['POST'])
        @handle_api_errors
        @validate_request_data(['row_id', 'column', 'value'])
        def update_table_cell(project_name, table_name):
            """Update a single table cell"""
            data = request.validated_data
            project_name = validator.validate_project_name(project_name)
            
            # Validate table and column names
            if not table_name.replace('_', '').isalnum():
                raise ValidationError("Invalid table name")
            if not data['column'].replace('_', '').isalnum():
                raise ValidationError("Invalid column name")
            
            query = f"UPDATE {table_name} SET {data['column']} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            rows_affected = project_manager.db_manager.execute_update(
                project_name, query, (data['value'], data['row_id'])
            )
            
            if rows_affected == 0:
                return jsonify(response_handler.error("Row not found", "ROW_NOT_FOUND")), 404
            
            return jsonify(response_handler.success(message="Cell updated successfully"))
        
        @self.app.route(f'{self.url_prefix}/project/<project_name>/prompts', methods=['GET'])
        @handle_api_errors
        def list_prompts(project_name):
            """List all custom prompts for a project"""
            project_name = validator.validate_project_name(project_name)
            
            query = """
                SELECT id, name, description, category, is_system, use_count, 
                       created_at, updated_at
                FROM custom_prompts 
                ORDER BY is_system DESC, name ASC
            """
            prompts = project_manager.db_manager.execute_query(project_name, query)
            
            return jsonify(response_handler.success({"prompts": prompts}))
        
        @self.app.route(f'{self.url_prefix}/project/<project_name>/prompts', methods=['POST'])
        @handle_api_errors
        @validate_request_data(['name', 'template'], ['description', 'category'])
        def create_prompt(project_name):
            """Create a new custom prompt"""
            data = validator.validate_template_data(request.validated_data)
            project_name = validator.validate_project_name(project_name)
            
            # Check for duplicate names
            check_query = "SELECT COUNT(*) as count FROM custom_prompts WHERE name = ?"
            result = project_manager.db_manager.execute_query(project_name, check_query, (data['name'],))
            if result[0]['count'] > 0:
                return jsonify(response_handler.error("Prompt name already exists", "DUPLICATE_NAME")), 409
            
            # Insert new prompt
            insert_query = """
                INSERT INTO custom_prompts (name, template, description, category)
                VALUES (?, ?, ?, ?)
            """
            project_manager.db_manager.execute_update(
                project_name, insert_query, 
                (data['name'], data['template'], data['description'], data['category'])
            )
            
            return jsonify(response_handler.success(message="Prompt created successfully"))
        
        @self.app.route(f'{self.url_prefix}/project/<project_name>/prompts/<int:prompt_id>', methods=['GET'])
        @handle_api_errors
        def get_prompt(project_name, prompt_id):
            """Get a specific prompt"""
            project_name = validator.validate_project_name(project_name)
            
            query = "SELECT * FROM custom_prompts WHERE id = ?"
            prompts = project_manager.db_manager.execute_query(project_name, query, (prompt_id,))
            
            if not prompts:
                return jsonify(response_handler.error("Prompt not found", "PROMPT_NOT_FOUND")), 404
            
            return jsonify(response_handler.success(prompts[0]))
        
        @self.app.route(f'{self.url_prefix}/project/<project_name>/prompts/<int:prompt_id>', methods=['PUT'])
        @handle_api_errors
        @validate_request_data(['name', 'template'], ['description', 'category'])
        def update_prompt(project_name, prompt_id):
            """Update an existing prompt"""
            data = validator.validate_template_data(request.validated_data)
            project_name = validator.validate_project_name(project_name)
            
            # Check if prompt exists
            check_query = "SELECT COUNT(*) as count FROM custom_prompts WHERE id = ?"
            result = project_manager.db_manager.execute_query(project_name, check_query, (prompt_id,))
            if result[0]['count'] == 0:
                return jsonify(response_handler.error("Prompt not found", "PROMPT_NOT_FOUND")), 404
            
            # Check for duplicate names (excluding current prompt)
            dup_query = "SELECT COUNT(*) as count FROM custom_prompts WHERE name = ? AND id != ?"
            result = project_manager.db_manager.execute_query(project_name, dup_query, (data['name'], prompt_id))
            if result[0]['count'] > 0:
                return jsonify(response_handler.error("Prompt name already exists", "DUPLICATE_NAME")), 409
            
            # Update prompt
            update_query = """
                UPDATE custom_prompts 
                SET name = ?, template = ?, description = ?, category = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            project_manager.db_manager.execute_update(
                project_name, update_query,
                (data['name'], data['template'], data['description'], data['category'], prompt_id)
            )
            
            return jsonify(response_handler.success(message="Prompt updated successfully"))
        
        @self.app.route(f'{self.url_prefix}/project/<project_name>/prompts/<int:prompt_id>', methods=['DELETE'])
        @handle_api_errors
        def delete_prompt(project_name, prompt_id):
            """Delete a prompt"""
            project_name = validator.validate_project_name(project_name)
            
            # Don't allow deletion of system prompts
            check_query = "SELECT is_system FROM custom_prompts WHERE id = ?"
            result = project_manager.db_manager.execute_query(project_name, check_query, (prompt_id,))
            if not result:
                return jsonify(response_handler.error("Prompt not found", "PROMPT_NOT_FOUND")), 404
            
            if result[0]['is_system']:
                return jsonify(response_handler.error("Cannot delete system prompts", "SYSTEM_PROMPT")), 403
            
            # Delete prompt
            delete_query = "DELETE FROM custom_prompts WHERE id = ?"
            rows_affected = project_manager.db_manager.execute_update(project_name, delete_query, (prompt_id,))
            
            if rows_affected == 0:
                return jsonify(response_handler.error("Prompt not found", "PROMPT_NOT_FOUND")), 404
            
            return jsonify(response_handler.success(message="Prompt deleted successfully"))
        
        @self.app.route(f'{self.url_prefix}/project/<project_name>/conversations', methods=['GET'])
        @handle_api_errors
        def list_conversations(project_name):
            """List conversations for a project"""
            project_name = validator.validate_project_name(project_name)
            limit = request.args.get('limit', 50, type=int)
            
            query = """
                SELECT id, title, template_name, created_at, updated_at, message_count, starred
                FROM conversations
                ORDER BY updated_at DESC
                LIMIT ?
            """
            conversations = project_manager.db_manager.execute_query(project_name, query, (limit,))
            
            return jsonify(response_handler.success({"conversations": conversations}))
        
        @self.app.route(f'{self.url_prefix}/project/<project_name>/conversations', methods=['POST'])
        @handle_api_errors
        @validate_request_data(['title', 'messages'], ['template_id', 'template_name'])
        def create_conversation(project_name):
            """Create a new conversation"""
            data = validator.validate_conversation_data(request.validated_data)
            project_name = validator.validate_project_name(project_name)
            
            # Insert conversation
            conv_query = """
                INSERT INTO conversations (title, template_id, template_name, message_count)
                VALUES (?, ?, ?, ?)
            """
            project_manager.db_manager.execute_update(
                project_name, conv_query,
                (data['title'], data.get('template_id'), data.get('template_name'), len(data['messages']))
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
            for msg in data['messages']:
                project_manager.db_manager.execute_update(
                    project_name, msg_query,
                    (conversation_id, msg['role'], msg['content'])
                )
            
            return jsonify(response_handler.success(
                {"conversation_id": conversation_id}, 
                "Conversation saved successfully"
            ))

def create_standardized_app(name: str, **kwargs) -> Flask:
    """Create Flask app with standardized configuration"""
    app = Flask(name, **kwargs)
    
    # CORS headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify(response_handler.error("Endpoint not found", "NOT_FOUND")), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify(response_handler.error("Method not allowed", "METHOD_NOT_ALLOWED")), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify(response_handler.error("Internal server error", "INTERNAL_ERROR")), 500
    
    return app