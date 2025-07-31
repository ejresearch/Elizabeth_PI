#!/usr/bin/env python3
"""
Template Manager for LIZZY Framework
Handles template loading, project creation, and schema management
"""

import os
import json
import sqlite3
from datetime import datetime

class TemplateManager:
    def __init__(self, templates_dir="templates", projects_dir="projects"):
        self.templates_dir = templates_dir
        self.projects_dir = projects_dir
        self.custom_dir = os.path.join(templates_dir, "custom")
        
        # Create directories if they don't exist
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.custom_dir, exist_ok=True)
        os.makedirs(self.projects_dir, exist_ok=True)
    
    def get_available_templates(self):
        """Get list of all available templates"""
        templates = {}
        
        # Load default templates
        for file in os.listdir(self.templates_dir):
            if file.endswith('.json') and os.path.isfile(os.path.join(self.templates_dir, file)):
                template_key = file[:-5]  # Remove .json
                template = self.load_template(template_key)
                if template:
                    templates[template_key] = {
                        'name': template['name'],
                        'description': template.get('description', ''),
                        'version': template.get('version', '1.0'),
                        'is_custom': False
                    }
        
        # Load custom templates
        if os.path.exists(self.custom_dir):
            for file in os.listdir(self.custom_dir):
                if file.endswith('.json'):
                    template_key = file[:-5]
                    template = self.load_template(template_key)
                    if template:
                        templates[template_key] = {
                            'name': template['name'],
                            'description': template.get('description', ''),
                            'version': template.get('version', '1.0'),
                            'is_custom': True
                        }
        
        return templates
    
    def load_template(self, template_key):
        """Load a template by key"""
        # Check custom first
        custom_path = os.path.join(self.custom_dir, f"{template_key}.json")
        default_path = os.path.join(self.templates_dir, f"{template_key}.json")
        
        if os.path.exists(custom_path):
            path = custom_path
        elif os.path.exists(default_path):
            path = default_path
        else:
            return None
        
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f" Error loading template {template_key}: {e}")
            return None
    
    def select_template(self):
        """Interactive template selection"""
        templates = self.get_available_templates()
        
        if not templates:
            print(" No templates found. Please check your templates directory.")
            return None
        
        print("\n Available Templates:")
        print("-" * 50)
        
        template_keys = list(templates.keys())
        for i, key in enumerate(template_keys, 1):
            template_info = templates[key]
            custom_mark = " " if template_info['is_custom'] else ""
            print(f"{i}. {template_info['name']}{custom_mark}")
            print(f"   {template_info['description']}")
            print(f"   Version: {template_info['version']}")
            print()
        
        while True:
            try:
                choice = int(input(f"Select template (1-{len(template_keys)}): ")) - 1
                if 0 <= choice < len(template_keys):
                    return template_keys[choice]
                else:
                    print(f" Please enter a number between 1 and {len(template_keys)}")
            except ValueError:
                print(" Please enter a valid number")
    
    def create_project_from_template(self, project_name, template_key):
        """Create a new project using the specified template"""
        template = self.load_template(template_key)
        if not template:
            print(f" Template '{template_key}' not found")
            return False
        
        # Create project directory
        project_dir = os.path.join(self.projects_dir, project_name)
        if os.path.exists(project_dir):
            print(f" Project '{project_name}' already exists")
            return False
        
        os.makedirs(project_dir)
        
        # Create database
        db_path = os.path.join(project_dir, f"{project_name}.sqlite")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Create all tables from template
            for table_name, table_info in template['tables'].items():
                fields = []
                for field_name, field_type in table_info['fields'].items():
                    if field_name == "FOREIGN KEY":
                        # Handle foreign key constraints
                        cursor.execute(f"PRAGMA foreign_keys = ON")
                        continue
                    fields.append(f"{field_name} {field_type}")
                
                fields_sql = ", ".join(fields)
                create_sql = f"CREATE TABLE {table_name} ({fields_sql})"
                cursor.execute(create_sql)
            
            # Create project metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Store template information
            cursor.execute("""
                INSERT INTO project_metadata (key, value) VALUES 
                ('template_type', ?),
                ('template_version', ?),
                ('template_name', ?),
                ('created_date', ?)
            """, (
                template_key,
                template.get('version', '1.0'),
                template['name'],
                datetime.now().isoformat()
            ))
            
            # Store template snapshot for future reference
            cursor.execute("""
                INSERT INTO project_metadata (key, value) VALUES 
                ('template_snapshot', ?)
            """, (json.dumps(template),))
            
            conn.commit()
            conn.close()
            
            print(f" Project '{project_name}' created using template '{template['name']}'")
            print(f" Location: {project_dir}")
            
            # Show template info
            print(f"\n Template Details:")
            print(f"   Tables: {', '.join(template['tables'].keys())}")
            if template.get('buckets', {}).get('recommended'):
                print(f"   Recommended buckets: {', '.join(template['buckets']['recommended'])}")
            
            return True
            
        except Exception as e:
            print(f" Error creating project: {e}")
            # Clean up on failure
            conn.close()
            shutil.rmtree(project_dir, ignore_errors=True)
            return False
    
    def get_project_template(self, project_name):
        """Get the template type for an existing project"""
        db_path = os.path.join(self.projects_dir, project_name, f"{project_name}.sqlite")
        if not os.path.exists(db_path):
            return None
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM project_metadata WHERE key='template_type'")
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else 'romcom'  # Default fallback
        except:
            return 'romcom'  # Default fallback
    
    def get_project_info(self, project_name):
        """Get detailed project information"""
        db_path = os.path.join(self.projects_dir, project_name, f"{project_name}.sqlite")
        if not os.path.exists(db_path):
            return None
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all metadata
            cursor.execute("SELECT key, value FROM project_metadata")
            metadata = dict(cursor.fetchall())
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                'template_type': metadata.get('template_type', 'unknown'),
                'template_name': metadata.get('template_name', 'Unknown'),
                'template_version': metadata.get('template_version', '1.0'),
                'created_date': metadata.get('created_date', 'Unknown'),
                'tables': tables,
                'metadata': metadata
            }
        except Exception as e:
            print(f" Error reading project info: {e}")
            return None
    
    def list_projects(self):
        """List all available projects with their template info"""
        if not os.path.exists(self.projects_dir):
            return []
        
        projects = []
        for item in os.listdir(self.projects_dir):
            project_path = os.path.join(self.projects_dir, item)
            if os.path.isdir(project_path):
                info = self.get_project_info(item)
                if info:
                    projects.append({
                        'name': item,
                        'template_type': info['template_type'],
                        'template_name': info['template_name'],
                        'created_date': info['created_date']
                    })
        
        return projects
    
    def ensure_legacy_compatibility(self, project_name):
        """Ensure legacy projects have template metadata"""
        db_path = os.path.join(self.projects_dir, project_name, f"{project_name}.sqlite")
        if not os.path.exists(db_path):
            return False
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if project_metadata table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='project_metadata'
            """)
            
            if not cursor.fetchone():
                # Create metadata table
                cursor.execute("""
                    CREATE TABLE project_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key TEXT UNIQUE NOT NULL,
                        value TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Add default template type (assume romcom for legacy)
                cursor.execute("""
                    INSERT INTO project_metadata (key, value) VALUES 
                    ('template_type', 'romcom'),
                    ('template_name', 'Romantic Comedy (Legacy)'),
                    ('template_version', '1.0'),
                    ('migrated_legacy', 'true')
                """)
                
                conn.commit()
                print(f" Migrated legacy project '{project_name}' to template system")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f" Error migrating legacy project: {e}")
            return False

if __name__ == "__main__":
    # Test the template manager
    tm = TemplateManager()
    templates = tm.get_available_templates()
    print("Available templates:")
    for key, info in templates.items():
        print(f"- {key}: {info['name']}")