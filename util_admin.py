#!/usr/bin/env python3
"""
LIZZY Admin Module - Template and Schema Management
Allows customization of templates without breaking existing projects
"""

import os
import json
import sqlite3
import shutil
from datetime import datetime

class LizzyAdmin:
    def __init__(self, templates_dir="templates", projects_dir="projects"):
        self.templates_dir = templates_dir
        self.projects_dir = projects_dir
        self.custom_dir = os.path.join(templates_dir, "custom")
        
        # Create directories if they don't exist
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.custom_dir, exist_ok=True)
    
    def run(self):
        """Main admin menu"""
        while True:
            print("\n" + "="*60)
            print("  LIZZY ADMIN - Template & Schema Management")
            print("="*60)
            print("\n1. View Available Templates")
            print("2. Edit Template Schema")
            print("3. Edit Template Prompts")
            print("4. Create Custom Template")
            print("5. Export Template")
            print("6. Import Template")
            print("7. View Template Usage")
            print("8. Back to Main Menu")
            
            choice = input("\nSelect option (1-8): ").strip()
            
            if choice == "1":
                self.view_templates()
            elif choice == "2":
                self.edit_schema()
            elif choice == "3":
                self.edit_prompts()
            elif choice == "4":
                self.create_template()
            elif choice == "5":
                self.export_template()
            elif choice == "6":
                self.import_template()
            elif choice == "7":
                self.view_usage()
            elif choice == "8":
                break
            else:
                print(" Invalid option")
    
    def load_template(self, template_name):
        """Load a template JSON file"""
        # Check custom templates first
        custom_path = os.path.join(self.custom_dir, f"{template_name}.json")
        default_path = os.path.join(self.templates_dir, f"{template_name}.json")
        
        if os.path.exists(custom_path):
            path = custom_path
        elif os.path.exists(default_path):
            path = default_path
        else:
            return None
        
        with open(path, 'r') as f:
            return json.load(f)
    
    def save_template(self, template_name, template_data, is_custom=True):
        """Save a template JSON file"""
        if is_custom:
            path = os.path.join(self.custom_dir, f"{template_name}.json")
        else:
            path = os.path.join(self.templates_dir, f"{template_name}.json")
        
        # Update version and timestamp
        template_data["version"] = template_data.get("version", "1.0")
        template_data["last_modified"] = datetime.now().isoformat()
        
        with open(path, 'w') as f:
            json.dump(template_data, f, indent=2)
        
        print(f" Template saved: {path}")
    
    def view_templates(self):
        """View all available templates"""
        print("\n Available Templates:")
        print("-" * 40)
        
        # Default templates
        print("\n  Default Templates:")
        for file in os.listdir(self.templates_dir):
            if file.endswith('.json') and file != 'custom':
                template = self.load_template(file[:-5])
                if template:
                    print(f"  - {template['name']} (v{template.get('version', '1.0')})")
                    print(f"    {template.get('description', 'No description')}")
        
        # Custom templates
        if os.path.exists(self.custom_dir):
            custom_files = [f for f in os.listdir(self.custom_dir) if f.endswith('.json')]
            if custom_files:
                print("\n Custom Templates:")
                for file in custom_files:
                    template = self.load_template(file[:-5])
                    if template:
                        print(f"  - {template['name']} (v{template.get('version', '1.0')})")
                        print(f"    {template.get('description', 'No description')}")
    
    def edit_schema(self):
        """Edit template schema (tables and fields)"""
        template_name = input("\nEnter template name to edit: ").strip().lower()
        template = self.load_template(template_name)
        
        if not template:
            print(" Template not found")
            return
        
        print(f"\n Editing Schema for: {template['name']}")
        
        while True:
            print("\n1. View Tables")
            print("2. Add Table")
            print("3. Edit Table")
            print("4. Remove Table")
            print("5. Save & Exit")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == "1":
                self.view_tables(template)
            elif choice == "2":
                self.add_table(template)
            elif choice == "3":
                self.edit_table(template)
            elif choice == "4":
                self.remove_table(template)
            elif choice == "5":
                # Save as custom template
                custom_name = input("\nSave as (leave blank for same name): ").strip() or template_name
                self.save_template(custom_name, template, is_custom=True)
                break
    
    def view_tables(self, template):
        """View all tables in a template"""
        print("\n Tables in template:")
        for table_name, table_info in template["tables"].items():
            print(f"\n  {table_info.get('display_name', table_name)}:")
            print(f"   {table_info.get('description', 'No description')}")
            print("   Fields:")
            for field, field_type in table_info["fields"].items():
                req = " (required)" if field in table_info.get("required", []) else ""
                print(f"     - {field}: {field_type}{req}")
    
    def add_table(self, template):
        """Add a new table to template"""
        table_name = input("\nTable name (lowercase, no spaces): ").strip().lower()
        display_name = input("Display name: ").strip()
        description = input("Description: ").strip()
        
        fields = {"id": "INTEGER PRIMARY KEY AUTOINCREMENT"}
        required_fields = []
        
        print("\nAdd fields (type 'done' when finished):")
        while True:
            field_name = input("\nField name (or 'done'): ").strip().lower()
            if field_name == 'done':
                break
            
            print("Field types: TEXT, INTEGER, REAL, TIMESTAMP")
            field_type = input("Field type: ").strip().upper()
            
            is_required = input("Required? (y/n): ").strip().lower() == 'y'
            
            if is_required:
                field_type += " NOT NULL"
                required_fields.append(field_name)
            
            fields[field_name] = field_type
        
        # Add timestamps
        fields["created_at"] = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        
        template["tables"][table_name] = {
            "fields": fields,
            "required": required_fields,
            "display_name": display_name,
            "description": description
        }
        
        print(f" Table '{table_name}' added")
    
    def edit_table(self, template):
        """Edit existing table"""
        table_name = input("\nTable name to edit: ").strip().lower()
        
        if table_name not in template["tables"]:
            print(" Table not found")
            return
        
        table = template["tables"][table_name]
        
        while True:
            print(f"\n Editing table: {table_name}")
            print("1. Add field")
            print("2. Remove field")
            print("3. Edit description")
            print("4. Done")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == "1":
                field_name = input("\nNew field name: ").strip().lower()
                field_type = input("Field type (TEXT/INTEGER/REAL): ").strip().upper()
                is_required = input("Required? (y/n): ").strip().lower() == 'y'
                
                if is_required:
                    field_type += " NOT NULL"
                    if "required" not in table:
                        table["required"] = []
                    table["required"].append(field_name)
                
                table["fields"][field_name] = field_type
                print(f" Field '{field_name}' added")
                
            elif choice == "2":
                field_name = input("\nField to remove: ").strip().lower()
                if field_name in table["fields"] and field_name not in ["id", "created_at"]:
                    del table["fields"][field_name]
                    if "required" in table and field_name in table["required"]:
                        table["required"].remove(field_name)
                    print(f" Field '{field_name}' removed")
                else:
                    print(" Cannot remove system fields or field not found")
                    
            elif choice == "3":
                table["description"] = input("\nNew description: ").strip()
                
            elif choice == "4":
                break
    
    def remove_table(self, template):
        """Remove a table from template"""
        table_name = input("\nTable name to remove: ").strip().lower()
        
        if table_name in template["tables"]:
            confirm = input(f"  Remove table '{table_name}'? (y/n): ").strip().lower()
            if confirm == 'y':
                del template["tables"][table_name]
                print(f" Table '{table_name}' removed")
        else:
            print(" Table not found")
    
    def edit_prompts(self):
        """Edit template prompts"""
        template_name = input("\nEnter template name to edit: ").strip().lower()
        template = self.load_template(template_name)
        
        if not template:
            print(" Template not found")
            return
        
        print(f"\n✏️  Editing Prompts for: {template['name']}")
        
        while True:
            print("\n1. Edit Brainstorm Tones")
            print("2. Edit Brainstorm Bucket Guidance")
            print("3. Edit Write Styles")
            print("4. Edit Default Guidance")
            print("5. Save & Exit")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == "1":
                self.edit_tones(template)
            elif choice == "2":
                self.edit_bucket_guidance(template)
            elif choice == "3":
                self.edit_write_styles(template)
            elif choice == "4":
                template["prompts"]["write"]["default_guidance"] = input("\nNew default guidance: ").strip()
            elif choice == "5":
                custom_name = input("\nSave as (leave blank for same name): ").strip() or template_name
                self.save_template(custom_name, template, is_custom=True)
                break
    
    def edit_tones(self, template):
        """Edit brainstorm tones"""
        tones = template["prompts"]["brainstorm"]["tones"]
        
        print("\n Current Tones:")
        for key, value in tones.items():
            print(f"\n{key}:")
            print(f"  {value[:100]}...")
        
        action = input("\n(a)dd, (e)dit, (r)emove tone? ").strip().lower()
        
        if action == 'a':
            key = input("Tone key (no spaces): ").strip().lower()
            value = input("Tone prompt: ").strip()
            tones[key] = value
        elif action == 'e':
            key = input("Tone key to edit: ").strip().lower()
            if key in tones:
                tones[key] = input("New prompt: ").strip()
        elif action == 'r':
            key = input("Tone key to remove: ").strip().lower()
            if key in tones:
                del tones[key]
    
    def edit_bucket_guidance(self, template):
        """Edit bucket guidance"""
        guidance = template["prompts"]["brainstorm"]["bucket_guidance"]
        
        print("\n Current Bucket Guidance:")
        for bucket, text in guidance.items():
            print(f"\n{bucket}:")
            print(f"  {text[:100]}...")
        
        bucket = input("\nBucket to edit (or 'new' for new bucket): ").strip().lower()
        
        if bucket == 'new':
            bucket = input("New bucket name: ").strip().lower()
        
        if bucket:
            guidance[bucket] = input(f"\nGuidance for {bucket}:\n").strip()
    
    def edit_write_styles(self, template):
        """Edit writing styles"""
        styles = template["prompts"]["write"]["styles"]
        
        print("\n  Current Writing Styles:")
        for key, value in styles.items():
            print(f"\n{key}:")
            print(f"  {value}")
        
        action = input("\n(a)dd, (e)dit, (r)emove style? ").strip().lower()
        
        if action == 'a':
            key = input("Style key: ").strip().lower()
            value = input("Style description: ").strip()
            styles[key] = value
        elif action == 'e':
            key = input("Style to edit: ").strip().lower()
            if key in styles:
                styles[key] = input("New description: ").strip()
        elif action == 'r':
            key = input("Style to remove: ").strip().lower()
            if key in styles:
                del styles[key]
    
    def create_template(self):
        """Create a new custom template"""
        print("\n Create Custom Template")
        
        name = input("Template name: ").strip()
        description = input("Description: ").strip()
        base_on = input("Base on existing template? (romcom/textbook/none): ").strip().lower()
        
        if base_on in ['romcom', 'textbook']:
            template = self.load_template(base_on)
            template["name"] = name
            template["description"] = description
        else:
            template = {
                "name": name,
                "version": "1.0",
                "description": description,
                "tables": {},
                "buckets": {
                    "recommended": [],
                    "descriptions": {}
                },
                "prompts": {
                    "brainstorm": {
                        "tones": {},
                        "bucket_guidance": {}
                    },
                    "write": {
                        "styles": {},
                        "default_guidance": ""
                    }
                }
            }
        
        file_name = name.lower().replace(" ", "_")
        self.save_template(file_name, template, is_custom=True)
        
        print(f"\n Template '{name}' created!")
        print("Use the Edit options to customize it further.")
    
    def export_template(self):
        """Export a template for sharing"""
        template_name = input("\nTemplate to export: ").strip().lower()
        template = self.load_template(template_name)
        
        if not template:
            print(" Template not found")
            return
        
        export_name = f"{template_name}_export_{datetime.now().strftime('%Y%m%d')}.json"
        export_path = os.path.join(os.getcwd(), export_name)
        
        with open(export_path, 'w') as f:
            json.dump(template, f, indent=2)
        
        print(f" Template exported to: {export_path}")
    
    def import_template(self):
        """Import a template file"""
        file_path = input("\nPath to template JSON file: ").strip()
        
        if not os.path.exists(file_path):
            print(" File not found")
            return
        
        try:
            with open(file_path, 'r') as f:
                template = json.load(f)
            
            name = template.get("name", "Imported Template")
            file_name = name.lower().replace(" ", "_")
            
            self.save_template(file_name, template, is_custom=True)
            print(f" Template '{name}' imported successfully!")
            
        except Exception as e:
            print(f" Error importing template: {e}")
    
    def view_usage(self):
        """View which projects use which templates"""
        print("\n Template Usage:")
        print("-" * 40)
        
        template_usage = {}
        
        for project in os.listdir(self.projects_dir):
            project_path = os.path.join(self.projects_dir, project)
            if os.path.isdir(project_path):
                db_path = os.path.join(project_path, f"{project}.sqlite")
                if os.path.exists(db_path):
                    try:
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute("SELECT value FROM project_metadata WHERE key='template_type'")
                        result = cursor.fetchone()
                        conn.close()
                        
                        template_type = result[0] if result else "unknown"
                        if template_type not in template_usage:
                            template_usage[template_type] = []
                        template_usage[template_type].append(project)
                    except:
                        pass
        
        for template, projects in template_usage.items():
            print(f"\n  {template.upper()}:")
            for project in projects:
                print(f"  - {project}")

if __name__ == "__main__":
    admin = LizzyAdmin()
    admin.run()