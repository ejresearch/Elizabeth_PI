"""
Interactive Intake Module for Lizzy
Provides GUI components for data entry and management
"""

import os
import csv
import json
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd


class InteractiveIntake:
    """Main intake interface with GUI components"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.project_name = os.path.basename(project_path)
        self.db_path = os.path.join(project_path, f"{self.project_name}.sqlite")
        self.conn = None
        self.root = None
        self.current_table = None
        self.connect_db()
    
    def connect_db(self):
        """Connect to project database"""
        if os.path.exists(self.db_path):
            self.conn = sqlite3.connect(self.db_path)
        else:
            raise FileNotFoundError(f"Database not found: {self.db_path}")
    
    def launch_gui(self):
        """Launch the main GUI interface"""
        self.root = tk.Tk()
        self.root.title(f"Lizzy Intake - {self.project_name}")
        self.root.geometry("1200x800")
        
        # Create menu bar
        self.create_menu()
        
        # Create main layout
        self.create_main_layout()
        
        # Load initial data
        self.refresh_data()
        
        self.root.mainloop()
    
    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import CSV", command=self.import_csv)
        file_menu.add_command(label="Export CSV", command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Import Documents", command=self.import_documents)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Add Row", command=self.add_row)
        edit_menu.add_command(label="Edit Selected", command=self.edit_row)
        edit_menu.add_command(label="Delete Selected", command=self.delete_row)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Characters", command=lambda: self.switch_table("characters"))
        view_menu.add_command(label="Scenes", command=lambda: self.switch_table("story_outline"))
        view_menu.add_command(label="Notes", command=lambda: self.switch_table("notes"))
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Chat with Data", command=self.launch_chat)
        tools_menu.add_command(label="Visualize Relationships", command=self.visualize_data)
    
    def create_main_layout(self):
        """Create the main application layout"""
        # Top frame for controls
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Table selector
        ttk.Label(control_frame, text="Table:").grid(row=0, column=0, padx=5)
        self.table_var = tk.StringVar(value="characters")
        table_combo = ttk.Combobox(control_frame, textvariable=self.table_var, 
                                   values=["characters", "story_outline", "notes"])
        table_combo.grid(row=0, column=1, padx=5)
        table_combo.bind('<<ComboboxSelected>>', lambda e: self.switch_table(self.table_var.get()))
        
        # Search box
        ttk.Label(control_frame, text="Search:").grid(row=0, column=2, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=3, padx=5)
        search_entry.bind('<KeyRelease>', lambda e: self.search_data())
        
        # Buttons
        ttk.Button(control_frame, text="Add New", command=self.add_row).grid(row=0, column=4, padx=5)
        ttk.Button(control_frame, text="Edit", command=self.edit_row).grid(row=0, column=5, padx=5)
        ttk.Button(control_frame, text="Delete", command=self.delete_row).grid(row=0, column=6, padx=5)
        ttk.Button(control_frame, text="Refresh", command=self.refresh_data).grid(row=0, column=7, padx=5)
        
        # Main data frame with treeview
        data_frame = ttk.Frame(self.root, padding="10")
        data_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)
        
        # Create treeview with scrollbars
        tree_scroll_y = ttk.Scrollbar(data_frame)
        tree_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        tree_scroll_x = ttk.Scrollbar(data_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.tree = ttk.Treeview(data_frame, 
                                 yscrollcommand=tree_scroll_y.set,
                                 xscrollcommand=tree_scroll_x.set)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E))
    
    def switch_table(self, table_name: str):
        """Switch to viewing a different table"""
        self.current_table = table_name
        self.table_var.set(table_name)
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh the data display"""
        if not self.current_table:
            self.current_table = "characters"
        
        # Clear existing data
        self.tree.delete(*self.tree.get_children())
        
        # Get column info
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({self.current_table})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Configure treeview columns
        self.tree["columns"] = columns
        self.tree["show"] = "headings"
        
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=150)
        
        # Load data
        cursor.execute(f"SELECT * FROM {self.current_table}")
        rows = cursor.fetchall()
        
        for row in rows:
            self.tree.insert("", tk.END, values=row)
        
        self.status_var.set(f"Loaded {len(rows)} rows from {self.current_table}")
    
    def search_data(self):
        """Search and filter displayed data"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            self.refresh_data()
            return
        
        # Clear existing data
        self.tree.delete(*self.tree.get_children())
        
        # Search in database
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({self.current_table})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Build search query
        where_clauses = [f"{col} LIKE '%{search_term}%'" for col in columns if col != 'id']
        where_clause = " OR ".join(where_clauses)
        
        query = f"SELECT * FROM {self.current_table} WHERE {where_clause}"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        for row in rows:
            self.tree.insert("", tk.END, values=row)
        
        self.status_var.set(f"Found {len(rows)} matching rows")
    
    def add_row(self):
        """Add a new row to the current table"""
        dialog = DataEntryDialog(self.root, self.conn, self.current_table)
        if dialog.result:
            self.refresh_data()
            self.status_var.set("New row added successfully")
    
    def edit_row(self):
        """Edit selected row"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a row to edit")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        dialog = DataEntryDialog(self.root, self.conn, self.current_table, values)
        if dialog.result:
            self.refresh_data()
            self.status_var.set("Row updated successfully")
    
    def delete_row(self):
        """Delete selected row"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a row to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this row?"):
            item = self.tree.item(selection[0])
            values = item['values']
            
            cursor = self.conn.cursor()
            
            # Get primary key column (assume first column)
            cursor.execute(f"PRAGMA table_info({self.current_table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Delete row
            cursor.execute(f"DELETE FROM {self.current_table} WHERE {columns[0]} = ?", (values[0],))
            self.conn.commit()
            
            self.refresh_data()
            self.status_var.set("Row deleted successfully")
    
    def import_csv(self):
        """Import data from CSV file"""
        filename = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                df = pd.read_csv(filename)
                df.to_sql(self.current_table, self.conn, if_exists='append', index=False)
                self.conn.commit()
                self.refresh_data()
                self.status_var.set(f"Imported {len(df)} rows from CSV")
            except Exception as e:
                messagebox.showerror("Import Error", str(e))
    
    def export_csv(self):
        """Export current table to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                df = pd.read_sql_query(f"SELECT * FROM {self.current_table}", self.conn)
                df.to_csv(filename, index=False)
                self.status_var.set(f"Exported {len(df)} rows to CSV")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))
    
    def import_documents(self):
        """Import documents for LightRAG buckets"""
        dialog = DocumentImportDialog(self.root, self.project_path)
        if dialog.result:
            self.status_var.set("Documents imported successfully")
    
    def launch_chat(self):
        """Launch chat interface for data"""
        ChatInterface(self.root, self.conn, self.current_table)
    
    def visualize_data(self):
        """Visualize data relationships"""
        DataVisualizer(self.root, self.conn)


class DataEntryDialog:
    """Dialog for adding/editing data rows"""
    
    def __init__(self, parent, conn, table_name, existing_data=None):
        self.conn = conn
        self.table_name = table_name
        self.existing_data = existing_data
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Row" if existing_data else "Add New Row")
        self.dialog.geometry("500x400")
        
        # Get table schema
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        self.columns = cursor.fetchall()
        
        # Create form fields
        self.entries = {}
        row = 0
        
        for col_info in self.columns:
            col_name = col_info[1]
            col_type = col_info[2]
            
            # Skip auto-increment fields
            if col_info[5] == 1:  # Primary key
                continue
            
            ttk.Label(self.dialog, text=col_name.replace("_", " ").title() + ":").grid(
                row=row, column=0, padx=10, pady=5, sticky=tk.W
            )
            
            if col_type == "TEXT" and "description" in col_name.lower():
                # Use text widget for long text fields
                text_widget = scrolledtext.ScrolledText(self.dialog, height=4, width=40)
                text_widget.grid(row=row, column=1, padx=10, pady=5)
                
                if existing_data:
                    col_idx = [c[1] for c in self.columns].index(col_name)
                    text_widget.insert(tk.END, existing_data[col_idx] or "")
                
                self.entries[col_name] = text_widget
            else:
                # Use entry widget for other fields
                entry = ttk.Entry(self.dialog, width=40)
                entry.grid(row=row, column=1, padx=10, pady=5)
                
                if existing_data:
                    col_idx = [c[1] for c in self.columns].index(col_name)
                    entry.insert(0, existing_data[col_idx] or "")
                
                self.entries[col_name] = entry
            
            row += 1
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        parent.wait_window(self.dialog)
    
    def save_data(self):
        """Save the entered data"""
        cursor = self.conn.cursor()
        
        # Collect values
        values = []
        columns = []
        
        for col_name, widget in self.entries.items():
            columns.append(col_name)
            if isinstance(widget, scrolledtext.ScrolledText):
                values.append(widget.get(1.0, tk.END).strip())
            else:
                values.append(widget.get())
        
        try:
            if self.existing_data:
                # Update existing row
                set_clause = ", ".join([f"{col} = ?" for col in columns])
                primary_key = [c[1] for c in self.columns if c[5] == 1][0]
                primary_value = self.existing_data[0]
                
                query = f"UPDATE {self.table_name} SET {set_clause} WHERE {primary_key} = ?"
                cursor.execute(query, values + [primary_value])
            else:
                # Insert new row
                placeholders = ", ".join(["?" for _ in columns])
                query = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                cursor.execute(query, values)
            
            self.conn.commit()
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Database Error", str(e))


class DocumentImportDialog:
    """Dialog for importing documents to LightRAG buckets"""
    
    def __init__(self, parent, project_path):
        self.project_path = project_path
        self.result = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Import Documents")
        self.dialog.geometry("600x500")
        
        # Bucket selection
        ttk.Label(self.dialog, text="Select Bucket:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        
        self.bucket_var = tk.StringVar()
        bucket_combo = ttk.Combobox(self.dialog, textvariable=self.bucket_var,
                                    values=["scripts", "books", "plays", "examples", "reference"])
        bucket_combo.grid(row=0, column=1, padx=10, pady=10)
        bucket_combo.set("scripts")
        
        # Document input
        ttk.Label(self.dialog, text="Document Content:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.NW)
        
        self.text_widget = scrolledtext.ScrolledText(self.dialog, height=20, width=60)
        self.text_widget.grid(row=1, column=1, padx=10, pady=5)
        
        # Metadata
        ttk.Label(self.dialog, text="Title:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.title_entry = ttk.Entry(self.dialog, width=50)
        self.title_entry.grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(self.dialog, text="Tags:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        self.tags_entry = ttk.Entry(self.dialog, width=50)
        self.tags_entry.grid(row=3, column=1, padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Import File", command=self.import_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save", command=self.save_document).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def import_file(self):
        """Import content from file"""
        filename = filedialog.askopenfilename(
            title="Select document",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                self.text_widget.delete(1.0, tk.END)
                self.text_widget.insert(tk.END, content)
                
                # Set title from filename
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(0, os.path.basename(filename))
    
    def save_document(self):
        """Save document to LightRAG bucket"""
        bucket = self.bucket_var.get()
        content = self.text_widget.get(1.0, tk.END).strip()
        title = self.title_entry.get()
        tags = self.tags_entry.get()
        
        if not content:
            messagebox.showwarning("No Content", "Please enter document content")
            return
        
        # Here you would integrate with LightRAGManager to add the document
        # For now, we'll save it to a file
        doc_dir = os.path.join(self.project_path, "documents", bucket)
        os.makedirs(doc_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(doc_dir, f"{title or 'doc'}_{timestamp}.txt")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Save metadata
        metadata = {
            "title": title,
            "tags": tags,
            "bucket": bucket,
            "timestamp": timestamp,
            "file": filename
        }
        
        meta_file = os.path.join(doc_dir, f"metadata_{timestamp}.json")
        with open(meta_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.result = True
        messagebox.showinfo("Success", f"Document saved to {bucket} bucket")
        self.dialog.destroy()


class ChatInterface:
    """Chat interface for interacting with data"""
    
    def __init__(self, parent, conn, table_name):
        self.conn = conn
        self.table_name = table_name
        
        # Create chat window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Chat with {table_name}")
        self.window.geometry("600x500")
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(self.window, height=25, width=70)
        self.chat_display.grid(row=0, column=0, padx=10, pady=10)
        self.chat_display.config(state=tk.DISABLED)
        
        # Input frame
        input_frame = ttk.Frame(self.window)
        input_frame.grid(row=1, column=0, padx=10, pady=5, sticky=(tk.W, tk.E))
        
        self.input_entry = ttk.Entry(input_frame, width=50)
        self.input_entry.grid(row=0, column=0, padx=5)
        self.input_entry.bind('<Return>', lambda e: self.send_message())
        
        ttk.Button(input_frame, text="Send", command=self.send_message).grid(row=0, column=1, padx=5)
        
        # Initial message
        self.add_message("System", f"Chat interface for {table_name} table. Ask questions about your data!")
    
    def add_message(self, sender: str, message: str):
        """Add message to chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"\n{sender}: {message}\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def send_message(self):
        """Process user message"""
        message = self.input_entry.get().strip()
        if not message:
            return
        
        self.add_message("You", message)
        self.input_entry.delete(0, tk.END)
        
        # Process query
        response = self.process_query(message)
        self.add_message("Assistant", response)
    
    def process_query(self, query: str) -> str:
        """Process natural language query"""
        query_lower = query.lower()
        cursor = self.conn.cursor()
        
        try:
            # Simple query processing
            if "how many" in query_lower or "count" in query_lower:
                cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
                count = cursor.fetchone()[0]
                return f"There are {count} rows in {self.table_name}"
            
            elif "show" in query_lower or "list" in query_lower:
                cursor.execute(f"SELECT * FROM {self.table_name} LIMIT 5")
                rows = cursor.fetchall()
                if rows:
                    result = f"Here are the first {len(rows)} rows:\n"
                    for row in rows:
                        result += f"  {row}\n"
                    return result
                return "No data found"
            
            elif "describe" in query_lower or "schema" in query_lower:
                cursor.execute(f"PRAGMA table_info({self.table_name})")
                columns = cursor.fetchall()
                result = f"Table {self.table_name} has these columns:\n"
                for col in columns:
                    result += f"  - {col[1]} ({col[2]})\n"
                return result
            
            else:
                return "I can help you explore your data. Try asking:\n" \
                       "- How many rows are there?\n" \
                       "- Show me some data\n" \
                       "- Describe the table structure"
                       
        except Exception as e:
            return f"Error processing query: {str(e)}"


class DataVisualizer:
    """Visualize data relationships"""
    
    def __init__(self, parent, conn):
        self.conn = conn
        
        # Create visualization window
        self.window = tk.Toplevel(parent)
        self.window.title("Data Relationships")
        self.window.geometry("800x600")
        
        # Canvas for visualization
        self.canvas = tk.Canvas(self.window, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw relationships
        self.visualize_relationships()
    
    def visualize_relationships(self):
        """Create visual representation of data relationships"""
        # Get character and scene data
        cursor = self.conn.cursor()
        
        # Get characters
        cursor.execute("SELECT name FROM characters")
        characters = [row[0] for row in cursor.fetchall()]
        
        # Get scenes
        cursor.execute("SELECT act, scene, key_characters FROM story_outline")
        scenes = cursor.fetchall()
        
        # Draw characters as nodes
        char_positions = {}
        y = 50
        for i, char in enumerate(characters):
            x = 100 + (i * 150)
            self.canvas.create_oval(x-30, y-30, x+30, y+30, fill="lightblue")
            self.canvas.create_text(x, y, text=char)
            char_positions[char] = (x, y)
        
        # Draw scenes and connections
        scene_y = 200
        for act, scene, chars in scenes:
            scene_x = 100 + ((act-1) * 200) + (scene * 50)
            
            # Draw scene box
            self.canvas.create_rectangle(scene_x-40, scene_y-20, scene_x+40, scene_y+20, fill="lightgreen")
            self.canvas.create_text(scene_x, scene_y, text=f"A{act}S{scene}")
            
            # Draw connections to characters
            if chars:
                for char_name in chars.split(','):
                    char_name = char_name.strip()
                    if char_name in char_positions:
                        char_x, char_y = char_positions[char_name]
                        self.canvas.create_line(char_x, char_y+30, scene_x, scene_y-20, 
                                               fill="gray", dash=(2, 2))


def launch_intake_gui(project_path: str):
    """Launch the intake GUI for a project"""
    intake = InteractiveIntake(project_path)
    intake.launch_gui()


if __name__ == "__main__":
    # Demo usage
    import sys
    
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "exports/the_wrong_wedding_20250813_1253"
    
    if os.path.exists(project_path):
        launch_intake_gui(project_path)
    else:
        print(f"Project not found: {project_path}")