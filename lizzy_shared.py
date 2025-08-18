"""
Shared Components and Common Functionality for Lizzy System
Extracts reusable code to reduce duplication and improve maintainability
"""

import os
import json
import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from functools import wraps
from flask import jsonify, request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LizzyError(Exception):
    """Base exception for Lizzy system"""
    pass

class ProjectNotFoundError(LizzyError):
    """Raised when project is not found"""
    pass

class DatabaseError(LizzyError):
    """Raised when database operations fail"""
    pass

class ValidationError(LizzyError):
    """Raised when validation fails"""
    pass

class DatabaseManager:
    """Centralized database operations for all Lizzy components"""
    
    def __init__(self, projects_dir='exports'):
        self.projects_dir = projects_dir
        
    def get_project_db_path(self, project_name: str) -> str:
        """Get the database path for a project"""
        return os.path.join(self.projects_dir, project_name, f"{project_name}.sqlite")
    
    def validate_project_exists(self, project_name: str) -> bool:
        """Validate that a project exists"""
        db_path = self.get_project_db_path(project_name)
        return os.path.exists(db_path)
    
    def get_connection(self, project_name: str) -> sqlite3.Connection:
        """Get database connection with error handling"""
        if not self.validate_project_exists(project_name):
            raise ProjectNotFoundError(f"Project '{project_name}' not found")
        
        try:
            db_path = self.get_project_db_path(project_name)
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error for {project_name}: {e}")
            raise DatabaseError(f"Failed to connect to project database: {e}")
    
    def execute_query(self, project_name: str, query: str, params: tuple = None) -> List[Dict]:
        """Execute query with error handling and logging"""
        try:
            with self.get_connection(project_name) as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except sqlite3.Error as e:
            logger.error(f"Query execution error: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise DatabaseError(f"Query execution failed: {e}")
    
    def execute_update(self, project_name: str, query: str, params: tuple = None) -> int:
        """Execute update/insert/delete with error handling"""
        try:
            with self.get_connection(project_name) as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                conn.commit()
                return cursor.rowcount
                
        except sqlite3.Error as e:
            logger.error(f"Update execution error: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise DatabaseError(f"Update execution failed: {e}")
    
    def get_projects_list(self) -> List[str]:
        """Get list of available projects"""
        try:
            projects = []
            if os.path.exists(self.projects_dir):
                for item in os.listdir(self.projects_dir):
                    project_path = os.path.join(self.projects_dir, item)
                    if os.path.isdir(project_path):
                        db_path = os.path.join(project_path, f"{item}.sqlite")
                        if os.path.exists(db_path):
                            projects.append(item)
            return sorted(projects)
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return []

class SchemaManager:
    """Manages database schema setup and migrations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def setup_core_tables(self, project_name: str):
        """Setup core tables needed by all components"""
        queries = [
            # Project info table
            '''CREATE TABLE IF NOT EXISTS project_info (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            
            # Custom prompts table (standardized)
            '''CREATE TABLE IF NOT EXISTS custom_prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                template TEXT NOT NULL,
                description TEXT,
                category TEXT DEFAULT 'custom',
                is_system BOOLEAN DEFAULT 0,
                use_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            
            # Conversations table
            '''CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                template_id INTEGER,
                template_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                starred BOOLEAN DEFAULT 0
            )''',
            
            # Conversation messages table
            '''CREATE TABLE IF NOT EXISTS conversation_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
            )'''
        ]
        
        for query in queries:
            try:
                self.db_manager.execute_update(project_name, query)
            except DatabaseError as e:
                logger.warning(f"Schema setup warning for {project_name}: {e}")

class DataValidator:
    """Centralized data validation"""
    
    @staticmethod
    def validate_project_name(project_name: str) -> str:
        """Validate and sanitize project name"""
        if not project_name:
            raise ValidationError("Project name is required")
        
        # Remove potentially dangerous characters
        safe_name = ''.join(c for c in project_name if c.isalnum() or c in '_-.')
        
        if not safe_name:
            raise ValidationError("Project name contains no valid characters")
        
        if len(safe_name) > 100:
            raise ValidationError("Project name too long (max 100 characters)")
        
        return safe_name
    
    @staticmethod
    def validate_template_data(data: Dict) -> Dict:
        """Validate template creation/update data"""
        required_fields = ['name', 'template']
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f"Field '{field}' is required")
        
        if len(data['name']) > 200:
            raise ValidationError("Template name too long (max 200 characters)")
        
        if len(data['template']) > 50000:
            raise ValidationError("Template content too long (max 50,000 characters)")
        
        # Sanitize data
        clean_data = {
            'name': data['name'].strip(),
            'template': data['template'].strip(),
            'description': data.get('description', '').strip()[:500],  # Max 500 chars
            'category': data.get('category', 'custom').strip()[:50]
        }
        
        return clean_data
    
    @staticmethod
    def validate_conversation_data(data: Dict) -> Dict:
        """Validate conversation save data"""
        if not data.get('title'):
            raise ValidationError("Conversation title is required")
        
        if not data.get('messages') or not isinstance(data['messages'], list):
            raise ValidationError("Conversation must have messages")
        
        clean_data = {
            'title': data['title'].strip()[:200],
            'messages': data['messages'][:1000],  # Max 1000 messages
            'template_id': data.get('template_id'),
            'template_name': data.get('template_name', '').strip()[:200]
        }
        
        return clean_data

class APIResponseHandler:
    """Standardized API response handling"""
    
    @staticmethod
    def success(data: Any = None, message: str = None) -> Dict:
        """Create success response"""
        response = {"success": True}
        if data is not None:
            response["data"] = data
        if message:
            response["message"] = message
        return response
    
    @staticmethod
    def error(message: str, code: str = None, details: Any = None) -> Dict:
        """Create error response"""
        response = {
            "success": False,
            "error": message
        }
        if code:
            response["error_code"] = code
        if details:
            response["details"] = details
        return response
    
    @staticmethod
    def paginated(data: List, total: int, page: int = 1, per_page: int = 50) -> Dict:
        """Create paginated response"""
        return {
            "success": True,
            "data": data,
            "pagination": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page
            }
        }

def handle_api_errors(f):
    """Decorator for consistent API error handling"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error in {f.__name__}: {e}")
            return jsonify(APIResponseHandler.error(str(e), "VALIDATION_ERROR")), 400
        except ProjectNotFoundError as e:
            logger.warning(f"Project not found in {f.__name__}: {e}")
            return jsonify(APIResponseHandler.error(str(e), "PROJECT_NOT_FOUND")), 404
        except DatabaseError as e:
            logger.error(f"Database error in {f.__name__}: {e}")
            return jsonify(APIResponseHandler.error("Database operation failed", "DATABASE_ERROR")), 500
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {e}")
            return jsonify(APIResponseHandler.error("Internal server error", "INTERNAL_ERROR")), 500
    
    return decorated_function

def validate_request_data(required_fields: List[str] = None, optional_fields: List[str] = None):
    """Decorator for request data validation"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json() if request.is_json else {}
            
            # Check required fields
            if required_fields:
                missing_fields = [field for field in required_fields if not data.get(field)]
                if missing_fields:
                    return jsonify(APIResponseHandler.error(
                        f"Missing required fields: {', '.join(missing_fields)}",
                        "MISSING_FIELDS"
                    )), 400
            
            # Filter allowed fields
            if required_fields or optional_fields:
                allowed_fields = (required_fields or []) + (optional_fields or [])
                filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
                request.validated_data = filtered_data
            else:
                request.validated_data = data
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

class ProjectManager:
    """High-level project operations"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.schema_manager = SchemaManager(self.db_manager)
        
    def get_project_info(self, project_name: str) -> Dict:
        """Get comprehensive project information"""
        project_name = DataValidator.validate_project_name(project_name)
        
        # Get basic project info
        info_query = "SELECT key, value FROM project_info"
        info_rows = self.db_manager.execute_query(project_name, info_query)
        project_info = {row['key']: row['value'] for row in info_rows}
        
        # Get table statistics
        tables_query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        tables = self.db_manager.execute_query(project_name, tables_query)
        
        table_stats = {}
        for table in tables:
            table_name = table['name']
            count_query = f"SELECT COUNT(*) as count FROM {table_name}"
            count_result = self.db_manager.execute_query(project_name, count_query)
            table_stats[table_name] = count_result[0]['count'] if count_result else 0
        
        return {
            'name': project_name,
            'info': project_info,
            'tables': table_stats,
            'total_records': sum(table_stats.values())
        }
    
    def get_table_data(self, project_name: str, table_name: str, limit: int = 100) -> Dict:
        """Get table data with pagination"""
        project_name = DataValidator.validate_project_name(project_name)
        
        # Validate table name (basic SQL injection protection)
        if not table_name.replace('_', '').isalnum():
            raise ValidationError("Invalid table name")
        
        # Get data
        query = f"SELECT * FROM {table_name} LIMIT ?"
        rows = self.db_manager.execute_query(project_name, query, (limit,))
        
        # Get total count
        count_query = f"SELECT COUNT(*) as count FROM {table_name}"
        count_result = self.db_manager.execute_query(project_name, count_query)
        total = count_result[0]['count'] if count_result else 0
        
        return {
            'table_name': table_name,
            'rows': rows,
            'total_rows': total,
            'returned_rows': len(rows)
        }

# Initialize shared instances
db_manager = DatabaseManager()
schema_manager = SchemaManager(db_manager)
project_manager = ProjectManager()
validator = DataValidator()
response_handler = APIResponseHandler()

# Export commonly used functions
__all__ = [
    'DatabaseManager', 'SchemaManager', 'DataValidator', 'APIResponseHandler',
    'ProjectManager', 'LizzyError', 'ProjectNotFoundError', 'DatabaseError',
    'ValidationError', 'handle_api_errors', 'validate_request_data',
    'db_manager', 'schema_manager', 'project_manager', 'validator', 'response_handler'
]