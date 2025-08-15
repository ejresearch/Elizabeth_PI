"""
Romcom Outline Module for Lizzy
Handles Template vs DIY story outlining with SQL storage
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext


@dataclass
class SceneOutline:
    """Represents a single scene in the outline"""
    act: int
    beat: str
    scene_number: int
    description: str
    status: str = "placeholder"  # placeholder, drafted, completed
    
    
@dataclass 
class RomcomOutlineTemplate:
    """Default romcom three-act structure template"""
    acts = {
        "Act I": {
            "beats": [
                {
                    "name": "Opening Image / Chemical Equation",
                    "scenes": 2,
                    "description": "Establish the world and protagonist's starting point"
                },
                {
                    "name": "Meet Cute", 
                    "scenes": 2,
                    "description": "The moment when romantic leads first encounter each other"
                },
                {
                    "name": "Reaction",
                    "scenes": 2,
                    "description": "How the characters react to their first meeting"
                },
                {
                    "name": "Romantic Complication",
                    "scenes": 2,
                    "description": "The obstacle that prevents easy romance"
                },
                {
                    "name": "Raise Stakes",
                    "scenes": 2,
                    "description": "Why this relationship matters to the characters"
                },
                {
                    "name": "Break-Into-Act II",
                    "scenes": 2,
                    "description": "Commitment to pursue the relationship despite obstacles"
                }
            ]
        },
        "Act II": {
            "beats": [
                {
                    "name": "Fun & Games / Falling In",
                    "scenes": 2,
                    "description": "The promise of the premise - romance develops"
                },
                {
                    "name": "Midpoint Hook",
                    "scenes": 2,
                    "description": "Major revelation or event that changes everything"
                },
                {
                    "name": "External/Internal Tensions Rise",
                    "scenes": 2,
                    "description": "Conflicts intensify both outside and within"
                },
                {
                    "name": "Lose Beat",
                    "scenes": 2,
                    "description": "All seems lost - the relationship appears doomed"
                },
                {
                    "name": "Self-Revelation",
                    "scenes": 2,
                    "description": "Characters realize what they must change"
                }
            ]
        },
        "Act III": {
            "beats": [
                {
                    "name": "Grand Gesture",
                    "scenes": 2,
                    "description": "Big romantic action to win back love"
                },
                {
                    "name": "Reunion",
                    "scenes": 2,
                    "description": "Coming back together after growth"
                },
                {
                    "name": "Happy Ending",
                    "scenes": 2,
                    "description": "Resolution of all conflicts"
                },
                {
                    "name": "Final Image",
                    "scenes": 2,
                    "description": "Mirror of opening showing transformation"
                }
            ]
        }
    }


class RomcomOutlineManager:
    """Manages romcom story outlines with Template/DIY options"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.project_name = os.path.basename(project_path)
        self.db_path = os.path.join(project_path, f"{self.project_name}.sqlite")
        self.conn = sqlite3.connect(self.db_path)
        self.setup_database()
        self.outline_mode = None  # "template" or "diy"
        
    def setup_database(self):
        """Create tables for storing outline data"""
        cursor = self.conn.cursor()
        
        # Main outline table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS story_outline_extended (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                act TEXT NOT NULL,
                act_number INTEGER NOT NULL,
                beat TEXT NOT NULL,
                scene_number INTEGER NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'placeholder',
                characters TEXT,
                location TEXT,
                key_events TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Outline metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outline_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                outline_mode TEXT NOT NULL,
                template_used TEXT,
                total_scenes INTEGER,
                acts_structure TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        
    def initialize_template_outline(self):
        """Initialize the database with the default romcom template"""
        cursor = self.conn.cursor()
        
        # Clear existing outline
        cursor.execute("DELETE FROM story_outline_extended")
        
        scene_counter = 1
        act_number = 1
        
        for act_name, act_data in RomcomOutlineTemplate.acts.items():
            for beat in act_data["beats"]:
                for scene_idx in range(1, beat["scenes"] + 1):
                    cursor.execute('''
                        INSERT INTO story_outline_extended 
                        (act, act_number, beat, scene_number, description, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        act_name,
                        act_number,
                        beat["name"],
                        scene_counter,
                        f"[{beat['description']}]",
                        "placeholder"
                    ))
                    scene_counter += 1
            act_number += 1
            
        # Save metadata
        cursor.execute('''
            INSERT INTO outline_metadata (outline_mode, template_used, total_scenes, acts_structure)
            VALUES (?, ?, ?, ?)
        ''', (
            "template",
            "romcom_default",
            scene_counter - 1,
            json.dumps({"acts": 3, "structure": "romcom"})
        ))
        
        self.conn.commit()
        return scene_counter - 1
        
    def initialize_diy_outline(self):
        """Initialize an empty DIY outline structure"""
        cursor = self.conn.cursor()
        
        # Clear existing outline
        cursor.execute("DELETE FROM story_outline_extended")
        
        # Create basic three-act structure with empty beats
        acts = ["Act I", "Act II", "Act III"]
        
        for idx, act in enumerate(acts, 1):
            # Add a single placeholder scene per act
            cursor.execute('''
                INSERT INTO story_outline_extended 
                (act, act_number, beat, scene_number, description, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                act,
                idx,
                "Custom Beat",
                idx,
                "[Add your own beat description]",
                "placeholder"
            ))
            
        # Save metadata
        cursor.execute('''
            INSERT INTO outline_metadata (outline_mode, template_used, total_scenes, acts_structure)
            VALUES (?, ?, ?, ?)
        ''', (
            "diy",
            None,
            3,
            json.dumps({"acts": 3, "structure": "custom"})
        ))
        
        self.conn.commit()
        return 3
        
    def get_outline(self) -> List[Dict]:
        """Retrieve the current outline from database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, act, act_number, beat, scene_number, description, 
                   status, characters, location, key_events, notes
            FROM story_outline_extended
            ORDER BY act_number, scene_number
        ''')
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        return [dict(zip(columns, row)) for row in rows]
        
    def update_scene(self, scene_id: int, updates: Dict):
        """Update a specific scene in the outline"""
        cursor = self.conn.cursor()
        
        # Build update query
        set_clauses = []
        values = []
        for key, value in updates.items():
            if key not in ['id', 'created_at']:
                set_clauses.append(f"{key} = ?")
                values.append(value)
                
        if set_clauses:
            values.append(datetime.now().isoformat())
            values.append(scene_id)
            
            query = f'''
                UPDATE story_outline_extended 
                SET {', '.join(set_clauses)}, updated_at = ?
                WHERE id = ?
            '''
            cursor.execute(query, values)
            self.conn.commit()
            
    def add_scene(self, act: str, beat: str, after_scene: Optional[int] = None):
        """Add a new scene to the outline"""
        cursor = self.conn.cursor()
        
        # Get act number
        act_number = int(act.split()[-1]) if "Act" in act else 1
        
        # Determine scene number
        if after_scene:
            # Insert after specific scene
            cursor.execute('''
                UPDATE story_outline_extended 
                SET scene_number = scene_number + 1
                WHERE scene_number > ?
            ''', (after_scene,))
            new_scene_number = after_scene + 1
        else:
            # Add at the end
            cursor.execute('SELECT MAX(scene_number) FROM story_outline_extended')
            max_scene = cursor.fetchone()[0] or 0
            new_scene_number = max_scene + 1
            
        # Insert new scene
        cursor.execute('''
            INSERT INTO story_outline_extended 
            (act, act_number, beat, scene_number, description, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            act,
            act_number,
            beat,
            new_scene_number,
            "[New scene - add description]",
            "placeholder"
        ))
        
        self.conn.commit()
        return cursor.lastrowid
        
    def delete_scene(self, scene_id: int):
        """Delete a scene from the outline"""
        cursor = self.conn.cursor()
        
        # Get scene number for reordering
        cursor.execute('SELECT scene_number FROM story_outline_extended WHERE id = ?', (scene_id,))
        scene_num = cursor.fetchone()
        
        if scene_num:
            # Delete the scene
            cursor.execute('DELETE FROM story_outline_extended WHERE id = ?', (scene_id,))
            
            # Reorder remaining scenes
            cursor.execute('''
                UPDATE story_outline_extended 
                SET scene_number = scene_number - 1
                WHERE scene_number > ?
            ''', (scene_num[0],))
            
            self.conn.commit()
            
    def export_outline_markdown(self) -> str:
        """Export outline as markdown format"""
        outline = self.get_outline()
        
        if not outline:
            return "# Empty Outline\n\nNo scenes defined yet."
            
        markdown = f"# {self.project_name} - Story Outline\n\n"
        markdown += f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
        
        current_act = None
        current_beat = None
        
        for scene in outline:
            # Act header (level 1)
            if scene['act'] != current_act:
                current_act = scene['act']
                markdown += f"\n# {current_act}\n\n"
                current_beat = None
                
            # Beat header (level 2)
            if scene['beat'] != current_beat:
                current_beat = scene['beat']
                markdown += f"\n## {current_beat}\n\n"
                
            # Scene (level 3)
            status_emoji = {
                "placeholder": "⚪",
                "drafted": "🟡", 
                "completed": "🟢"
            }.get(scene['status'], "⚪")
            
            markdown += f"### Scene {scene['scene_number']} {status_emoji}\n\n"
            
            # Scene details
            if scene['description'] and scene['description'] != "[Add your own beat description]":
                markdown += f"{scene['description']}\n\n"
                
            if scene['characters']:
                markdown += f"**Characters:** {scene['characters']}\n\n"
                
            if scene['location']:
                markdown += f"**Location:** {scene['location']}\n\n"
                
            if scene['key_events']:
                markdown += f"**Key Events:**\n{scene['key_events']}\n\n"
                
            if scene['notes']:
                markdown += f"**Notes:**\n{scene['notes']}\n\n"
                
            markdown += "---\n"
            
        return markdown
        
    def get_outline_statistics(self) -> Dict:
        """Get statistics about the current outline"""
        cursor = self.conn.cursor()
        
        # Total scenes
        cursor.execute('SELECT COUNT(*) FROM story_outline_extended')
        total_scenes = cursor.fetchone()[0]
        
        # Scenes by status
        cursor.execute('''
            SELECT status, COUNT(*) 
            FROM story_outline_extended 
            GROUP BY status
        ''')
        status_counts = dict(cursor.fetchall())
        
        # Scenes by act
        cursor.execute('''
            SELECT act, COUNT(*) 
            FROM story_outline_extended 
            GROUP BY act
        ''')
        act_counts = dict(cursor.fetchall())
        
        return {
            "total_scenes": total_scenes,
            "status_breakdown": status_counts,
            "acts_breakdown": act_counts,
            "completion_percentage": (
                status_counts.get("completed", 0) / total_scenes * 100 
                if total_scenes > 0 else 0
            )
        }


class RomcomOutlineGUI:
    """GUI for managing romcom outlines"""
    
    def __init__(self, project_path: str):
        self.manager = RomcomOutlineManager(project_path)
        self.root = None
        self.tree = None
        self.selected_mode = None
        
    def launch(self):
        """Launch the outline GUI"""
        self.root = tk.Tk()
        self.root.title(f"Romcom Outline - {self.manager.project_name}")
        self.root.geometry("1400x900")
        
        # Check if outline exists
        outline = self.manager.get_outline()
        
        if not outline:
            # Show mode selection dialog
            self.show_mode_selection()
        else:
            # Load existing outline
            self.create_main_interface()
            
        self.root.mainloop()
        
    def show_mode_selection(self):
        """Show Template vs DIY selection dialog"""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Center frame
        frame = ttk.Frame(self.root, padding="50")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        title = ttk.Label(frame, text="Choose Your Outline Mode", 
                         font=("Arial", 24, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Description
        desc = ttk.Label(frame, text="How would you like to structure your romantic comedy?",
                        font=("Arial", 12))
        desc.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Template option
        template_frame = ttk.LabelFrame(frame, text="📝 Template", padding="20")
        template_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        
        template_desc = tk.Text(template_frame, width=40, height=15, wrap="word")
        template_desc.insert("1.0", 
            "Use the proven romcom structure:\n\n"
            "ACT I (12 scenes)\n"
            "• Opening Image\n"
            "• Meet Cute\n"
            "• Reaction\n"
            "• Romantic Complication\n"
            "• Raise Stakes\n"
            "• Break into Act II\n\n"
            "ACT II (10 scenes)\n"
            "• Fun & Games\n"
            "• Midpoint Hook\n"
            "• Tensions Rise\n"
            "• Self-Revelation\n\n"
            "ACT III (8 scenes)\n"
            "• Grand Gesture\n"
            "• Reunion\n"
            "• Happy Ending"
        )
        template_desc.config(state="disabled", bg="#f0f0f0")
        template_desc.grid(row=0, column=0)
        
        ttk.Button(template_frame, text="Use Template", 
                  command=lambda: self.select_mode("template")).grid(row=1, column=0, pady=10)
        
        # DIY option
        diy_frame = ttk.LabelFrame(frame, text="🎨 DIY", padding="20")
        diy_frame.grid(row=2, column=1, padx=20, pady=20, sticky="nsew")
        
        diy_desc = tk.Text(diy_frame, width=40, height=15, wrap="word")
        diy_desc.insert("1.0",
            "Create your own structure:\n\n"
            "• Start with a blank outline\n"
            "• Add your own acts and beats\n"
            "• Define custom scene structure\n"
            "• Complete creative freedom\n\n"
            "Perfect for:\n"
            "• Experimental structures\n"
            "• Non-traditional romcoms\n"
            "• Adapted works\n"
            "• Personal storytelling style\n\n"
            "You can add, remove, and reorganize\n"
            "scenes however you like!"
        )
        diy_desc.config(state="disabled", bg="#f0f0f0")
        diy_desc.grid(row=0, column=0)
        
        ttk.Button(diy_frame, text="Start DIY", 
                  command=lambda: self.select_mode("diy")).grid(row=1, column=0, pady=10)
                  
    def select_mode(self, mode: str):
        """Handle mode selection"""
        self.selected_mode = mode
        
        if mode == "template":
            total_scenes = self.manager.initialize_template_outline()
            messagebox.showinfo("Template Loaded", 
                              f"Romcom template loaded with {total_scenes} scenes!")
        else:
            total_scenes = self.manager.initialize_diy_outline()
            messagebox.showinfo("DIY Mode", 
                              "Starting with blank outline. Add your own structure!")
            
        self.create_main_interface()
        
    def create_main_interface(self):
        """Create the main outline management interface"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export as Markdown", command=self.export_markdown)
        file_menu.add_command(label="Print Outline", command=self.print_outline)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Add Scene", command=self.add_scene_dialog)
        edit_menu.add_command(label="Edit Scene", command=self.edit_scene)
        edit_menu.add_command(label="Delete Scene", command=self.delete_scene)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Statistics", command=self.show_statistics)
        view_menu.add_command(label="Refresh", command=self.refresh_outline)
        
        # Top toolbar
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side="top", fill="x", padx=5, pady=5)
        
        ttk.Button(toolbar, text="➕ Add Scene", command=self.add_scene_dialog).pack(side="left", padx=2)
        ttk.Button(toolbar, text="✏️ Edit", command=self.edit_scene).pack(side="left", padx=2)
        ttk.Button(toolbar, text="🗑️ Delete", command=self.delete_scene).pack(side="left", padx=2)
        ttk.Button(toolbar, text="📊 Stats", command=self.show_statistics).pack(side="left", padx=2)
        ttk.Button(toolbar, text="🔄 Refresh", command=self.refresh_outline).pack(side="left", padx=2)
        
        # Main content area
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create treeview for outline
        columns = ("Beat", "Description", "Status", "Characters", "Location")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="tree headings", height=25)
        
        # Define headings
        self.tree.heading("#0", text="Scene")
        self.tree.heading("Beat", text="Beat")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Characters", text="Characters")
        self.tree.heading("Location", text="Location")
        
        # Column widths
        self.tree.column("#0", width=100)
        self.tree.column("Beat", width=200)
        self.tree.column("Description", width=400)
        self.tree.column("Status", width=100)
        self.tree.column("Characters", width=200)
        self.tree.column("Location", width=150)
        
        # Scrollbars
        vsb = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(main_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click to edit
        self.tree.bind("<Double-Button-1>", lambda e: self.edit_scene())
        
        # Status bar
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken")
        status_bar.pack(side="bottom", fill="x")
        
        # Load outline
        self.refresh_outline()
        
    def refresh_outline(self):
        """Refresh the outline display"""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Load outline
        outline = self.manager.get_outline()
        
        current_act = None
        current_beat = None
        act_item = None
        beat_item = None
        
        for scene in outline:
            # Create act node if needed
            if scene['act'] != current_act:
                current_act = scene['act']
                act_item = self.tree.insert("", "end", text=current_act, open=True,
                                           tags=("act",))
                current_beat = None
                
            # Create beat node if needed  
            if scene['beat'] != current_beat:
                current_beat = scene['beat']
                beat_item = self.tree.insert(act_item, "end", text="", open=True,
                                            values=(current_beat, "", "", "", ""),
                                            tags=("beat",))
                
            # Add scene
            status_emoji = {
                "placeholder": "⚪",
                "drafted": "🟡",
                "completed": "🟢"
            }.get(scene['status'], "⚪")
            
            self.tree.insert(beat_item, "end", 
                           text=f"Scene {scene['scene_number']} {status_emoji}",
                           values=("", 
                                  scene['description'] or "",
                                  scene['status'],
                                  scene['characters'] or "",
                                  scene['location'] or ""),
                           tags=("scene", scene['status'], f"scene_{scene['id']}"))
                           
        # Configure tags for styling
        self.tree.tag_configure("act", font=("Arial", 12, "bold"))
        self.tree.tag_configure("beat", font=("Arial", 11, "italic"))
        self.tree.tag_configure("placeholder", foreground="gray")
        self.tree.tag_configure("drafted", foreground="orange")
        self.tree.tag_configure("completed", foreground="green")
        
        # Update status
        stats = self.manager.get_outline_statistics()
        self.status_var.set(
            f"Total Scenes: {stats['total_scenes']} | "
            f"Completed: {stats['status_breakdown'].get('completed', 0)} | "
            f"Progress: {stats['completion_percentage']:.1f}%"
        )
        
    def add_scene_dialog(self):
        """Show dialog to add a new scene"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Scene")
        dialog.geometry("400x300")
        
        # Act selection
        ttk.Label(dialog, text="Act:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        act_var = tk.StringVar(value="Act I")
        act_combo = ttk.Combobox(dialog, textvariable=act_var,
                                values=["Act I", "Act II", "Act III"])
        act_combo.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # Beat name
        ttk.Label(dialog, text="Beat:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        beat_entry = ttk.Entry(dialog, width=30)
        beat_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        # After scene
        ttk.Label(dialog, text="After Scene #:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        after_var = tk.StringVar()
        after_entry = ttk.Entry(dialog, textvariable=after_var, width=10)
        after_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        def add_scene():
            act = act_var.get()
            beat = beat_entry.get() or "Custom Beat"
            after = int(after_var.get()) if after_var.get() else None
            
            self.manager.add_scene(act, beat, after)
            self.refresh_outline()
            dialog.destroy()
            
        ttk.Button(button_frame, text="Add", command=add_scene).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)
        
        dialog.columnconfigure(1, weight=1)
        
    def edit_scene(self):
        """Edit the selected scene"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a scene to edit")
            return
            
        # Get scene ID from tags
        item = selection[0]
        tags = self.tree.item(item)["tags"]
        
        scene_id = None
        for tag in tags:
            if tag.startswith("scene_"):
                scene_id = int(tag.split("_")[1])
                break
                
        if not scene_id:
            messagebox.showwarning("Invalid Selection", "Please select a scene (not an act or beat)")
            return
            
        # Get scene data
        outline = self.manager.get_outline()
        scene = next((s for s in outline if s['id'] == scene_id), None)
        
        if not scene:
            return
            
        # Create edit dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Scene {scene['scene_number']}")
        dialog.geometry("600x500")
        
        # Create fields
        fields = {}
        
        row = 0
        for field_name, field_label in [
            ("description", "Description"),
            ("characters", "Characters"),
            ("location", "Location"),
            ("key_events", "Key Events"),
            ("notes", "Notes")
        ]:
            ttk.Label(dialog, text=f"{field_label}:").grid(row=row, column=0, padx=10, pady=5, sticky="nw")
            
            if field_name in ["key_events", "notes", "description"]:
                # Use text widget for longer content
                text_widget = scrolledtext.ScrolledText(dialog, width=50, height=5, wrap="word")
                text_widget.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
                text_widget.insert("1.0", scene[field_name] or "")
                fields[field_name] = text_widget
            else:
                # Use entry for shorter content
                entry = ttk.Entry(dialog, width=50)
                entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
                entry.insert(0, scene[field_name] or "")
                fields[field_name] = entry
                
            row += 1
            
        # Status selection
        ttk.Label(dialog, text="Status:").grid(row=row, column=0, padx=10, pady=5, sticky="w")
        status_var = tk.StringVar(value=scene['status'])
        status_combo = ttk.Combobox(dialog, textvariable=status_var,
                                   values=["placeholder", "drafted", "completed"])
        status_combo.grid(row=row, column=1, padx=10, pady=5, sticky="w")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=row+1, column=0, columnspan=2, pady=20)
        
        def save_changes():
            updates = {
                "status": status_var.get()
            }
            
            for field_name, widget in fields.items():
                if isinstance(widget, scrolledtext.ScrolledText):
                    updates[field_name] = widget.get("1.0", "end-1c")
                else:
                    updates[field_name] = widget.get()
                    
            self.manager.update_scene(scene_id, updates)
            self.refresh_outline()
            dialog.destroy()
            
        ttk.Button(button_frame, text="Save", command=save_changes).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)
        
        dialog.columnconfigure(1, weight=1)
        
    def delete_scene(self):
        """Delete the selected scene"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a scene to delete")
            return
            
        # Get scene ID from tags
        item = selection[0]
        tags = self.tree.item(item)["tags"]
        
        scene_id = None
        for tag in tags:
            if tag.startswith("scene_"):
                scene_id = int(tag.split("_")[1])
                break
                
        if not scene_id:
            messagebox.showwarning("Invalid Selection", "Please select a scene (not an act or beat)")
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this scene?"):
            self.manager.delete_scene(scene_id)
            self.refresh_outline()
            
    def export_markdown(self):
        """Export outline as markdown"""
        markdown = self.manager.export_outline_markdown()
        
        # Save dialog
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")],
            initialfile=f"{self.manager.project_name}_outline.md"
        )
        
        if filename:
            with open(filename, 'w') as f:
                f.write(markdown)
            messagebox.showinfo("Export Complete", f"Outline exported to {filename}")
            
    def print_outline(self):
        """Display printable version of outline"""
        markdown = self.manager.export_outline_markdown()
        
        # Create preview window
        preview = tk.Toplevel(self.root)
        preview.title("Outline Preview")
        preview.geometry("800x600")
        
        text = scrolledtext.ScrolledText(preview, wrap="word", width=80, height=30)
        text.pack(fill="both", expand=True, padx=10, pady=10)
        text.insert("1.0", markdown)
        text.config(state="disabled")
        
    def show_statistics(self):
        """Show outline statistics"""
        stats = self.manager.get_outline_statistics()
        
        msg = f"""Outline Statistics:

Total Scenes: {stats['total_scenes']}

Status Breakdown:
• Placeholder: {stats['status_breakdown'].get('placeholder', 0)}
• Drafted: {stats['status_breakdown'].get('drafted', 0)}
• Completed: {stats['status_breakdown'].get('completed', 0)}

Acts Breakdown:
• Act I: {stats['acts_breakdown'].get('Act I', 0)} scenes
• Act II: {stats['acts_breakdown'].get('Act II', 0)} scenes
• Act III: {stats['acts_breakdown'].get('Act III', 0)} scenes

Completion: {stats['completion_percentage']:.1f}%"""
        
        messagebox.showinfo("Outline Statistics", msg)


def main():
    """Demo the outline system"""
    import tempfile
    
    # Create test project
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = os.path.join(tmpdir, "test_romcom")
        os.makedirs(project_path)
        
        # Launch GUI
        gui = RomcomOutlineGUI(project_path)
        gui.launch()


if __name__ == "__main__":
    main()