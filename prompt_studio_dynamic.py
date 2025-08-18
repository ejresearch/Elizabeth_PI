"""
Dynamic Prompt Studio Backend - System Agnostic
Automatically discovers project schemas and builds data blocks from real data
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class ProjectDiscovery:
    """Dynamically discover and analyze project structure"""
    
    def __init__(self, projects_dir="projects"):
        self.projects_dir = projects_dir
        self.lightrag_dir = "lightrag_working_dir"
        
    def discover_projects(self) -> List[str]:
        """Find all available projects"""
        projects = []
        if os.path.exists(self.projects_dir):
            for item in os.listdir(self.projects_dir):
                project_path = os.path.join(self.projects_dir, item)
                if os.path.isdir(project_path):
                    # Check for SQLite database
                    db_path = os.path.join(project_path, f"{item}.sqlite")
                    if os.path.exists(db_path):
                        projects.append(item)
        return projects
    
    def analyze_project_schema(self, project_name: str) -> Dict:
        """Analyze a project's database schema and discover available data"""
        project_path = os.path.join(self.projects_dir, project_name)
        db_path = os.path.join(project_path, f"{project_name}.sqlite")
        
        if not os.path.exists(db_path):
            return {"error": "Project database not found"}
        
        schema_info = {
            "project_name": project_name,
            "tables": {},
            "data_blocks": {},
            "sample_data": {},
            "custom_prompts": []
        }
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Setup custom prompts table if not exists
            self._setup_prompts_table(cursor)
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Analyze each table
            for table in tables:
                schema_info["tables"][table] = self._analyze_table(cursor, table)
                schema_info["sample_data"][table] = self._get_sample_data(cursor, table)
                
            # Generate data blocks based on discovered schema
            schema_info["data_blocks"] = self._generate_data_blocks(schema_info["tables"], schema_info["sample_data"])
            
            # Load custom prompts
            schema_info["custom_prompts"] = self._load_custom_prompts(cursor)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            schema_info["error"] = str(e)
            
        return schema_info
    
    def _analyze_table(self, cursor, table_name: str) -> Dict:
        """Analyze a table's structure"""
        try:
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            
            return {
                "columns": [{"name": col[1], "type": col[2]} for col in columns],
                "row_count": row_count
            }
        except:
            return {"columns": [], "row_count": 0}
    
    def _get_sample_data(self, cursor, table_name: str, limit: int = 3) -> List[Dict]:
        """Get sample data from a table"""
        try:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Convert to list of dicts
            sample_data = []
            for row in rows:
                sample_data.append(dict(zip(columns, row)))
                
            return sample_data
        except:
            return []
    
    def _generate_data_blocks(self, tables: Dict, sample_data: Dict) -> Dict:
        """Generate data blocks based on discovered schema"""
        blocks = {
            "sql": [],
            "lightrag": [],
            "context": []
        }
        
        # SQL blocks - full tables only
        for table_name, table_info in tables.items():
            if table_info["row_count"] > 0:
                # Skip system tables
                if table_name in ['sqlite_sequence']:
                    continue
                    
                # Create one block per table (full table)
                sample_rows = sample_data.get(table_name, [])
                row_count = table_info["row_count"]
                
                block = {
                    "key": f"sql.{table_name}",
                    "label": self._humanize_table_name(table_name),
                    "description": f"Complete {table_name} table ({row_count} rows)",
                    "table": table_name,
                    "row_count": row_count,
                    "sample": f"{len(sample_rows)} sample rows available"
                }
                blocks["sql"].append(block)
        
        # Add core LightRAG buckets only
        blocks["lightrag"] = self._discover_core_lightrag_blocks()
        
        # Add minimal context blocks
        blocks["context"] = [
            {"key": "context.project.name", "label": "Project Name", "description": "Current project identifier"}
        ]
        
        return blocks
    
    def _discover_core_lightrag_blocks(self) -> List[Dict]:
        """Discover only the core LightRAG buckets (scripts, plays, books)"""
        blocks = []
        
        # Only these three buckets
        core_buckets = {
            "romcom_scripts": "Scripts",
            "shakespeare_plays": "Plays", 
            "screenwriting_books": "Books"
        }
        
        try:
            bucket_config_path = os.path.join(self.lightrag_dir, "bucket_config.json")
            if os.path.exists(bucket_config_path):
                with open(bucket_config_path, 'r') as f:
                    config = json.load(f)
                
                # Create blocks for core buckets only
                for bucket_name, display_name in core_buckets.items():
                    if bucket_name in config.get("metadata", {}):
                        metadata = config["metadata"][bucket_name]
                        blocks.append({
                            "key": f"lightrag.{bucket_name}",
                            "label": display_name,
                            "description": metadata.get("description", f"{display_name} knowledge base"),
                            "bucket": bucket_name,
                            "doc_count": metadata.get("document_count", 0)
                        })
                    
        except Exception as e:
            print(f"Error discovering core LightRAG blocks: {e}")
        
        return blocks
    
    def _setup_prompts_table(self, cursor):
        """Setup custom prompts table"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                template TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default System Brainstorm if it doesn't exist
        cursor.execute('SELECT COUNT(*) FROM custom_prompts WHERE name = ?', ('System Brainstorm',))
        if cursor.fetchone()[0] == 0:
            default_template = '''# Brainstorm with Lizzy

## Objectives
Bring the **SQL outline** to life with concrete, high-signal ideas grounded by **LightRAG** references. Treat this like a writers' room: explore, compare, and curate options so the Write phase has a strong, organized mission.

## Authority & Role Separation
- **SQL is canonical** for plot, characters, and continuity. We may explore variations here, but do not contradict SQL facts.
- **Brainstorm may quote** from LightRAG sources and name works/characters *for analysis only* (the Write phase will paraphrase and never copy).
- If an essential detail is missing from SQL, propose **ASSUMPTIONS (DRAFT)** as bullets; keep each to ≤ 10 words.

## Inputs (from SQL)
**Project:** {context.project.name}

**Character Data:**
{sql.characters}

**Story Structure:**
{sql.story_outline_extended}

**Project Notes:**
{sql.notes}

## LightRAG Retrieval Policy (Discovery Mode)
**Two‑Pass strategy required**

**Pass 1 — Sequential, purpose-built queries**
1) **Scripts (tone & pacing):** {lightrag.romcom_scripts} — pull comedic rhythm, cinematic flow, dialogue tactics. Quotes **allowed** with titles.
2) **Plays (plot mechanics):** {lightrag.shakespeare_plays} — pull reversals, dramatic irony, archetypes, thematic frames. Quotes **allowed** with titles.
3) **Books (craft rules):** {lightrag.screenwriting_books} — pull structural principles, beat taxonomies, dialogue techniques. Short quotes **allowed** with titles/pages if available.
- Mode: `mix` for each.
- From each bucket, select **3–5 references**. Include short quotes (≤ 40 words each) *only if they illuminate a tactic*.

**Pass 2 — Cross-bucket synthesis**
- Resolve conflicts; cluster tactics into a **coherent scene strategy**.
- Output a **Unified Strategy** blurb **≤ 50 words** describing beat logic and tone.

## Output Specification (sections & caps)
1) **SQL Snapshot (Ground Truth)** — 3–5 bullets reiterating must-hit facts from SQL.
2) **Bucket Notes — Scripts** — 3–5 items; may include short quotes with titles.
3) **Bucket Notes — Plays** — 3–5 items; may include short quotes with titles.
4) **Bucket Notes — Books** — 3–5 items; may include short quotes with titles/pages.
5) **Unified Strategy (≤ 50 words)** — one paragraph merging the above.
6) **Beat Sketch (6–10 beats)** — numbered list mapping from opening image to button; tag beats with [Tone], [Plot], or [Craft].
7) **Opportunities & Risks (max 6 bullets)** — list potential payoffs and pitfalls.
8) **ASSUMPTIONS (DRAFT)** — optional bullets for missing-but-necessary details (≤ 10 words each).
9) **Open Questions (max 5)** — crisp questions to resolve before writing.

## Formatting Rules
- Use clear bullets and numbered lists; no walls of text.
- Always cite LightRAG items with **[Bucket] Title (Author, Year)** where known.
- Quotes ≤ 40 words; attribute them.
- Avoid importing proper nouns into the final **Unified Strategy**; keep it abstracted to tactics.

Now perform Pass 1 and Pass 2, then produce the output sections in order.'''
            
            cursor.execute('''
                INSERT INTO custom_prompts (name, template, description)
                VALUES (?, ?, ?)
            ''', ('System Brainstorm', default_template, "Lizzy's official brainstorming template"))
    
    def _load_custom_prompts(self, cursor):
        """Load all custom prompts"""
        cursor.execute('''
            SELECT id, name, template, description, created_at, updated_at
            FROM custom_prompts
            ORDER BY updated_at DESC
        ''')
        
        prompts = []
        for row in cursor.fetchall():
            prompts.append({
                'id': row[0],
                'name': row[1],
                'template': row[2],
                'description': row[3],
                'created_at': row[4],
                'updated_at': row[5]
            })
        return prompts
    
    def _humanize_table_name(self, table_name: str) -> str:
        """Convert table names to human-readable labels"""
        table_map = {
            "characters": "Characters",
            "story_outline": "Story Outline", 
            "story_outline_extended": "Extended Outline",
            "notes": "Project Notes",
            "project_metadata": "Project Metadata",
            "brainstorming_log": "Brainstorm History",
            "finalized_draft_v1": "Finalized Draft",
            "outline_metadata": "Outline Metadata"
        }
        
        return table_map.get(table_name, table_name.replace('_', ' ').title())
    
    def _discover_lightrag_blocks(self) -> List[Dict]:
        """Discover available LightRAG buckets"""
        blocks = []
        
        try:
            # Load bucket configuration
            bucket_config_path = os.path.join(self.lightrag_dir, "bucket_config.json")
            if os.path.exists(bucket_config_path):
                with open(bucket_config_path, 'r') as f:
                    config = json.load(f)
                
                # Create blocks for each bucket
                for bucket_name, metadata in config.get("metadata", {}).items():
                    blocks.append({
                        "key": f"lightrag.{bucket_name}.query",
                        "label": self._humanize_bucket_name(bucket_name),
                        "description": metadata.get("description", f"Query {bucket_name} knowledge"),
                        "bucket": bucket_name,
                        "collection": metadata.get("collection", "unknown"),
                        "doc_count": metadata.get("document_count", 0)
                    })
                
                # Add generic query types
                query_types = [
                    ("dialogue", "Dialogue samples and conversation patterns"),
                    ("structure", "Story structure and beat patterns"),
                    ("character", "Character archetypes and development"),
                    ("themes", "Thematic elements and motifs")
                ]
                
                for query_type, description in query_types:
                    blocks.append({
                        "key": f"lightrag.query.{query_type}",
                        "label": f"Query: {query_type.title()}",
                        "description": description,
                        "query_type": query_type
                    })
                    
        except Exception as e:
            print(f"Error discovering LightRAG blocks: {e}")
        
        return blocks
    
    def _humanize_label(self, table_name: str, col_name: str) -> str:
        """Convert table.column names to human-readable labels"""
        # Special cases for common patterns
        label_map = {
            "characters.romantic_challenge": "Character Challenges",
            "characters.lovable_trait": "Character Traits", 
            "characters.comedic_flaw": "Character Flaws",
            "characters.name": "Character Names",
            "story_outline.key_events": "Scene Events",
            "story_outline.key_characters": "Scene Characters",
            "story_outline.act": "Act Number",
            "story_outline.scene": "Scene Number",
            "story_outline_extended.location": "Scene Location",
            "story_outline_extended.description": "Scene Description",
            "project_metadata.value": "Project Metadata",
            "notes.content": "Project Notes"
        }
        
        key = f"{table_name}.{col_name}"
        if key in label_map:
            return label_map[key]
        
        # Generic humanization
        words = col_name.replace('_', ' ').split()
        return ' '.join(word.capitalize() for word in words)
    
    def _humanize_bucket_name(self, bucket_name: str) -> str:
        """Convert bucket names to human-readable labels"""
        return bucket_name.replace('_', ' ').title()
    
    def _get_column_sample(self, rows: List[Dict], col_name: str) -> str:
        """Get a sample value from a column"""
        for row in rows:
            value = row.get(col_name)
            if value and str(value).strip():
                return str(value)[:100] + ("..." if len(str(value)) > 100 else "")
        return "No data"
    
    def get_project_data(self, project_name: str, table: str = None, column: str = None) -> Any:
        """Get actual data from a project"""
        db_path = os.path.join(self.projects_dir, project_name, f"{project_name}.sqlite")
        
        if not os.path.exists(db_path):
            return None
            
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            if table and column:
                # Get specific column data
                cursor.execute(f"SELECT {column} FROM {table} WHERE {column} IS NOT NULL AND {column} != '' LIMIT 10;")
                results = [row[0] for row in cursor.fetchall() if row[0]]
                conn.close()
                return results
            elif table:
                # Get all data from table
                cursor.execute(f"SELECT * FROM {table};")
                rows = cursor.fetchall()
                
                # Get column names
                cursor.execute(f"PRAGMA table_info({table});")
                columns = [col[1] for col in cursor.fetchall()]
                
                conn.close()
                return [dict(zip(columns, row)) for row in rows]
            
            conn.close()
            return None
            
        except Exception as e:
            return f"Error: {str(e)}"

# Initialize discovery system
discovery = ProjectDiscovery()

@app.route('/api/projects')
def get_projects():
    """Get list of available projects"""
    projects = discovery.discover_projects()
    return jsonify({"projects": projects})

@app.route('/api/project/<project_name>/schema')
def get_project_schema(project_name):
    """Get project schema and data blocks"""
    schema = discovery.analyze_project_schema(project_name)
    return jsonify(schema)

@app.route('/api/project/<project_name>/data/<table>')
def get_table_data(project_name, table):
    """Get data from a specific table"""
    data = discovery.get_project_data(project_name, table)
    return jsonify({"table": table, "data": data})

@app.route('/api/project/<project_name>/column/<table>/<column>')
def get_column_data(project_name, table, column):
    """Get data from a specific column"""
    data = discovery.get_project_data(project_name, table, column)
    return jsonify({"table": table, "column": column, "data": data})

@app.route('/api/compile-prompt', methods=['POST'])
def compile_prompt():
    """Compile a prompt template with real project data"""
    data = request.json
    project_name = data.get('project_name')
    template = data.get('template')
    
    if not project_name or not template:
        return jsonify({"error": "Missing project_name or template"}), 400
    
    compiled = template
    
    # Replace context variables
    compiled = compiled.replace('{context.project.name}', project_name)
    
    # Replace SQL table variables with formatted table data
    import re
    sql_vars = re.findall(r'{sql\.(\w+)}', template)
    for table in sql_vars:
        table_data = discovery.get_project_data(project_name, table)
        if table_data and isinstance(table_data, list):
            # Format table data nicely
            formatted_data = f"TABLE: {table.upper()}\n"
            for i, row in enumerate(table_data[:5]):  # Show first 5 rows
                formatted_data += f"Row {i+1}: "
                # Show key fields for each table type
                if table == 'characters' and 'name' in row:
                    formatted_data += f"{row.get('name', 'N/A')} - {row.get('romantic_challenge', 'N/A')} - {row.get('lovable_trait', 'N/A')} - {row.get('comedic_flaw', 'N/A')}\n"
                elif table == 'story_outline_extended' and 'description' in row:
                    formatted_data += f"Act {row.get('act_number', 'N/A')}, Scene {row.get('scene_number', 'N/A')}: {row.get('description', 'N/A')}\n"
                elif table == 'notes' and 'title' in row:
                    formatted_data += f"{row.get('title', 'N/A')}: {row.get('content', 'N/A')[:100]}...\n"
                else:
                    # Generic row display
                    key_fields = [k for k in row.keys() if k not in ['id', 'created_at', 'updated_at']][:3]
                    formatted_data += " | ".join([f"{k}: {row.get(k, 'N/A')}" for k in key_fields]) + "\n"
            
            if len(table_data) > 5:
                formatted_data += f"... and {len(table_data) - 5} more rows\n"
            
            compiled = compiled.replace(f'{{sql.{table}}}', formatted_data.strip())
        else:
            compiled = compiled.replace(f'{{sql.{table}}}', f"No data available for {table} table")
    
    # Replace LightRAG variables
    lightrag_vars = re.findall(r'{lightrag\.(\w+)}', template)
    for bucket in lightrag_vars:
        compiled = compiled.replace(f'{{lightrag.{bucket}}}', f"[Query {bucket} knowledge base for relevant insights]")
    
    return jsonify({"compiled": compiled})

@app.route('/api/project/<project_name>/prompts', methods=['GET'])
def get_project_prompts(project_name):
    """Get all custom prompts for a project"""
    db_path = os.path.join(discovery.projects_dir, project_name, f"{project_name}.sqlite")
    
    if not os.path.exists(db_path):
        return jsonify({"error": "Project not found"}), 404
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        discovery._setup_prompts_table(cursor)
        prompts = discovery._load_custom_prompts(cursor)
        
        conn.close()
        return jsonify({"prompts": prompts})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/project/<project_name>/prompts', methods=['POST'])
def save_project_prompt(project_name):
    """Save a new custom prompt"""
    data = request.json
    name = data.get('name')
    template = data.get('template') 
    description = data.get('description', '')
    
    if not name or not template:
        return jsonify({"error": "Name and template are required"}), 400
    
    db_path = os.path.join(discovery.projects_dir, project_name, f"{project_name}.sqlite")
    
    if not os.path.exists(db_path):
        return jsonify({"error": "Project not found"}), 404
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        discovery._setup_prompts_table(cursor)
        
        # Check if name already exists
        cursor.execute('SELECT COUNT(*) FROM custom_prompts WHERE name = ?', (name,))
        if cursor.fetchone()[0] > 0:
            return jsonify({"error": "Prompt name already exists"}), 400
        
        # Insert new prompt
        cursor.execute('''
            INSERT INTO custom_prompts (name, template, description, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (name, template, description, datetime.now()))
        
        prompt_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({"id": prompt_id, "message": "Prompt saved successfully"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/project/<project_name>/prompts/<int:prompt_id>', methods=['PUT'])
def update_project_prompt(project_name, prompt_id):
    """Update an existing prompt"""
    data = request.json
    name = data.get('name')
    template = data.get('template')
    description = data.get('description', '')
    
    if not name or not template:
        return jsonify({"error": "Name and template are required"}), 400
    
    db_path = os.path.join(discovery.projects_dir, project_name, f"{project_name}.sqlite")
    
    if not os.path.exists(db_path):
        return jsonify({"error": "Project not found"}), 404
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if prompt exists
        cursor.execute('SELECT COUNT(*) FROM custom_prompts WHERE id = ?', (prompt_id,))
        if cursor.fetchone()[0] == 0:
            return jsonify({"error": "Prompt not found"}), 404
        
        # Check if name conflicts with another prompt
        cursor.execute('SELECT COUNT(*) FROM custom_prompts WHERE name = ? AND id != ?', (name, prompt_id))
        if cursor.fetchone()[0] > 0:
            return jsonify({"error": "Prompt name already exists"}), 400
        
        # Update prompt
        cursor.execute('''
            UPDATE custom_prompts 
            SET name = ?, template = ?, description = ?, updated_at = ?
            WHERE id = ?
        ''', (name, template, description, datetime.now(), prompt_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Prompt updated successfully"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/project/<project_name>/prompts/<int:prompt_id>', methods=['DELETE'])
def delete_project_prompt(project_name, prompt_id):
    """Delete a custom prompt"""
    db_path = os.path.join(discovery.projects_dir, project_name, f"{project_name}.sqlite")
    
    if not os.path.exists(db_path):
        return jsonify({"error": "Project not found"}), 404
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if prompt exists and get its name
        cursor.execute('SELECT name FROM custom_prompts WHERE id = ?', (prompt_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Prompt not found"}), 404
        
        # Don't allow deleting the default System Brainstorm
        if result[0] == 'System Brainstorm':
            return jsonify({"error": "Cannot delete the default System Brainstorm template"}), 400
        
        # Delete prompt
        cursor.execute('DELETE FROM custom_prompts WHERE id = ?', (prompt_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Prompt deleted successfully"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def serve_interface():
    """Serve the main interface"""
    return send_from_directory('.', 'prompt_studio_dynamic.html')

if __name__ == '__main__':
    print("🚀 Starting Dynamic Prompt Studio...")
    print("📊 Discovering projects...")
    projects = discovery.discover_projects()
    print(f"✅ Found {len(projects)} projects: {', '.join(projects)}")
    
    app.run(host='0.0.0.0', port=8002, debug=True)