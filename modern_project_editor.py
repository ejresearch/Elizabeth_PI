"""
Modern Project Editor GUI for Lizzy
Clean, contemporary interface for editing characters, story outline, and notes
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


class ModernProjectEditor:
    """Modern, clean GUI for editing all project tables"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.project_name = os.path.basename(project_path)
        self.db_path = os.path.join(project_path, f"{self.project_name}.sqlite")
        self.conn = None
        self.root = None
        
        # Tailwind-inspired design tokens with better contrast
        self.colors = {
            'bg_primary': '#ffffff',      # white
            'bg_secondary': '#f9fafb',    # gray-50
            'bg_tertiary': '#f3f4f6',     # gray-100
            'bg_hover': '#f3f4f6',        # gray-100
            'bg_input': '#ffffff',        # white with border
            'border': '#d1d5db',          # gray-300
            'border_light': '#e5e7eb',    # gray-200
            'border_active': '#3b82f6',   # blue-500
            'text_primary': '#111827',    # gray-900
            'text_secondary': '#6b7280',  # gray-500
            'text_muted': '#9ca3af',      # gray-400
            'accent': '#3b82f6',          # blue-500
            'accent_hover': '#2563eb',    # blue-600
            'accent_light': '#eff6ff',    # blue-50
            'success': '#059669',         # emerald-600
            'success_hover': '#047857',   # emerald-700
            'success_light': '#ecfdf5',   # emerald-50
            'warning': '#d97706',         # amber-600
            'warning_light': '#fffbeb',   # amber-50
            'danger': '#dc2626',          # red-600
            'danger_hover': '#b91c1c',    # red-700
            'danger_light': '#fef2f2',    # red-50
            'purple': '#7c3aed',          # violet-600
            'purple_light': '#f5f3ff'     # violet-50
        }
        
        # Tailwind-inspired typography
        self.fonts = {
            'title': ('SF Pro Display', 24, 'bold'),      # text-2xl font-bold
            'heading': ('SF Pro Display', 18, 'bold'),    # text-lg font-bold
            'subheading': ('SF Pro Display', 16, 'bold'), # text-base font-bold
            'body': ('SF Pro Text', 14),                  # text-sm
            'body_medium': ('SF Pro Text', 14, 'bold'),   # text-sm font-medium
            'caption': ('SF Pro Text', 12),               # text-xs
            'monospace': ('SF Mono', 13)                  # text-xs font-mono
        }
        
        self.connect_db()
    
    def connect_db(self):
        """Connect to project database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not connect to database: {e}")
    
    def launch(self):
        """Launch the modern editor GUI"""
        self.root = tk.Tk()
        self.root.title(f"Lizzy Project Editor - {self.project_name}")
        self.root.geometry("1400x900")
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Set up modern styling
        self.setup_styles()
        
        # Create main interface
        self.create_header()
        self.create_main_content()
        self.create_status_bar()
        
        # Load initial data
        self.refresh_all_tables()
        
        self.root.mainloop()
    
    def setup_styles(self):
        """Configure Tailwind-inspired ttk styles"""
        style = ttk.Style()
        
        # Configure Tailwind-style button
        style.configure('Tailwind.TButton',
                       padding=(16, 10),
                       font=self.fonts['body_medium'],
                       relief='flat',
                       borderwidth=1)
        
        # Configure Tailwind-style frame
        style.configure('Tailwind.TFrame',
                       background=self.colors['bg_primary'],
                       relief='flat',
                       borderwidth=0)
        
        # Configure Tailwind-style labels
        style.configure('Body.TLabel',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       font=self.fonts['body'])
        
        style.configure('Heading.TLabel',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       font=self.fonts['heading'])
        
        style.configure('Title.TLabel',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       font=self.fonts['title'])
        
        style.configure('Secondary.TLabel',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_secondary'],
                       font=self.fonts['body'])
        
        style.configure('Caption.TLabel',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_muted'],
                       font=self.fonts['caption'])
        
        # Configure Tailwind-style treeview
        style.configure('Tailwind.Treeview',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['bg_primary'],
                       font=self.fonts['body'],
                       rowheight=40,
                       borderwidth=1,
                       relief='solid')
        
        style.configure('Tailwind.Treeview.Heading',
                       background=self.colors['bg_tertiary'],
                       foreground=self.colors['text_primary'],
                       font=self.fonts['body_medium'],
                       relief='flat',
                       borderwidth=1)
        
        # Configure Tailwind-style notebook
        style.configure('Tailwind.TNotebook',
                       background=self.colors['bg_primary'],
                       borderwidth=0)
        
        style.configure('Tailwind.TNotebook.Tab',
                       padding=(24, 16),
                       font=self.fonts['body_medium'],
                       borderwidth=0,
                       focuscolor='none')
        
        # Configure map for selected/active states
        style.map('Tailwind.TNotebook.Tab',
                 background=[('selected', self.colors['bg_primary']),
                           ('!selected', self.colors['bg_secondary'])],
                 foreground=[('selected', self.colors['accent']),
                           ('!selected', self.colors['text_secondary'])])
    
    def create_header(self):
        """Create Tailwind-style header section"""
        # Header container with proper padding
        header_frame = tk.Frame(self.root, bg=self.colors['bg_primary'], height=88)
        header_frame.pack(fill='x', padx=24, pady=(24, 0))
        header_frame.pack_propagate(False)
        
        # Left side - Project title
        left_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        left_frame.pack(side='left', fill='y')
        
        title_label = ttk.Label(left_frame, 
                               text=f"📝 {self.project_name}",
                               style='Title.TLabel')
        title_label.pack(anchor='w', pady=(16, 0))
        
        subtitle_label = ttk.Label(left_frame,
                                  text="Romantic Comedy Project Editor",
                                  style='Secondary.TLabel')
        subtitle_label.pack(anchor='w', pady=(4, 0))
        
        # Right side - Action buttons with Tailwind spacing
        button_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        button_frame.pack(side='right', fill='y', pady=16)
        
        # Tailwind-style buttons with proper spacing (space-x-3)
        self.create_tailwind_button(button_frame, "📤 Export", self.colors['purple'], 
                                   self.colors['purple_light'], self.export_project).pack(side='right')
        
        self.create_tailwind_button(button_frame, "💾 Save All", self.colors['success'], 
                                   self.colors['success_light'], self.save_all_changes).pack(side='right', padx=(0, 12))
        
        self.create_tailwind_button(button_frame, "🔄 Refresh", self.colors['bg_tertiary'], 
                                   self.colors['bg_hover'], self.refresh_all_tables, 
                                   text_color=self.colors['text_primary']).pack(side='right', padx=(0, 12))
        
        # Tailwind-style separator (border-b border-gray-200)
        separator = tk.Frame(self.root, bg=self.colors['border_light'], height=1)
        separator.pack(fill='x', padx=24, pady=(16, 24))
    
    def create_tailwind_button(self, parent, text, bg_color, hover_color, command, text_color='white'):
        """Create a Tailwind-style button with hover effects"""
        btn = tk.Button(parent,
                       text=text,
                       bg=bg_color,
                       fg=text_color,
                       font=self.fonts['body_medium'],
                       relief='flat',
                       bd=0,
                       padx=20,
                       pady=10,
                       cursor='hand2',
                       command=command)
        
        # Add hover effects
        def on_enter(e):
            btn.configure(bg=hover_color if text_color == 'white' else self.colors['bg_hover'])
        
        def on_leave(e):
            btn.configure(bg=bg_color)
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def create_main_content(self):
        """Create Tailwind-style main tabbed content area"""
        # Main container with proper padding (px-6)
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=24, pady=(0, 24))
        
        # Create Tailwind-style notebook for tabs
        self.notebook = ttk.Notebook(main_frame, style='Tailwind.TNotebook')
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs with better styling
        self.create_characters_tab()
        self.create_outline_tab()
        self.create_notes_tab()
    
    def create_characters_tab(self):
        """Create Tailwind-style characters editing tab"""
        characters_frame = tk.Frame(self.notebook, bg=self.colors['bg_secondary'])
        self.notebook.add(characters_frame, text="👥 Characters")
        
        # Tab content container with proper padding
        content_frame = tk.Frame(characters_frame, bg=self.colors['bg_secondary'])
        content_frame.pack(fill='both', expand=True, padx=24, pady=24)
        
        # Header section with better spacing
        header = tk.Frame(content_frame, bg=self.colors['bg_secondary'])
        header.pack(fill='x', pady=(0, 20))
        
        # Title and description
        title_frame = tk.Frame(header, bg=self.colors['bg_secondary'])
        title_frame.pack(side='left', fill='y')
        
        ttk.Label(title_frame, text="Character Development", style='Heading.TLabel').pack(anchor='w')
        ttk.Label(title_frame, text="Customize your 6 romantic comedy archetypes", 
                 style='Secondary.TLabel').pack(anchor='w', pady=(4, 0))
        
        # Action buttons with proper Tailwind spacing
        char_actions = tk.Frame(header, bg=self.colors['bg_secondary'])
        char_actions.pack(side='right', fill='y', pady=8)
        
        self.create_tailwind_button(char_actions, "➕ Add Character", self.colors['success'], 
                                   self.colors['success_hover'], self.add_character).pack(side='right')
        
        self.create_tailwind_button(char_actions, "✏️ Edit", self.colors['accent'], 
                                   self.colors['accent_hover'], self.edit_character).pack(side='right', padx=(0, 12))
        
        self.create_tailwind_button(char_actions, "🗑️ Delete", self.colors['danger'], 
                                   self.colors['danger_hover'], self.delete_character).pack(side='right', padx=(0, 12))
        
        # Tailwind-style table container with border and rounded corners
        table_container = tk.Frame(content_frame, bg=self.colors['bg_primary'], relief='solid', bd=1)
        table_container.pack(fill='both', expand=True)
        
        # Table frame with proper padding
        table_frame = tk.Frame(table_container, bg=self.colors['bg_primary'])
        table_frame.pack(fill='both', expand=True, padx=1, pady=1)
        
        # Create Tailwind-style treeview
        columns = ('Name', 'Archetype', 'Gender', 'Age', 'Challenge', 'Trait', 'Flaw')
        self.characters_tree = ttk.Treeview(table_frame, 
                                          columns=columns, 
                                          show='tree headings',
                                          style='Tailwind.Treeview')
        
        # Configure columns with better widths
        self.characters_tree.heading('#0', text='')
        self.characters_tree.column('#0', width=0, minwidth=0, stretch=False)  # Hide ID column
        
        column_config = {
            'Name': 140,
            'Archetype': 180,
            'Gender': 80,
            'Age': 60,
            'Challenge': 200,
            'Trait': 200,
            'Flaw': 200
        }
        
        for col in columns:
            self.characters_tree.heading(col, text=col, anchor='w')
            width = column_config.get(col, 120)
            self.characters_tree.column(col, width=width, minwidth=80, anchor='w')
        
        # Tailwind-style scrollbars
        char_v_scroll = ttk.Scrollbar(table_frame, orient='vertical', 
                                     command=self.characters_tree.yview)
        char_h_scroll = ttk.Scrollbar(table_frame, orient='horizontal', 
                                     command=self.characters_tree.xview)
        
        self.characters_tree.configure(yscrollcommand=char_v_scroll.set,
                                      xscrollcommand=char_h_scroll.set)
        
        # Grid layout with proper weights
        self.characters_tree.grid(row=0, column=0, sticky='nsew')
        char_v_scroll.grid(row=0, column=1, sticky='ns')
        char_h_scroll.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click for inline editing
        self.characters_tree.bind('<Double-1>', self.on_character_cell_double_click)
        
        # Store current editing state
        self.editing_item = None
        self.editing_column = None
        self.edit_entry = None
    
    def create_outline_tab(self):
        """Create the story outline editing tab"""
        outline_frame = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
        self.notebook.add(outline_frame, text="📖 Story Outline")
        
        # Header section
        header = tk.Frame(outline_frame, bg=self.colors['bg_primary'])
        header.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(header, text="Story Structure", style='Subheading.TLabel').pack(side='left')
        
        # Action buttons
        outline_actions = tk.Frame(header, bg=self.colors['bg_primary'])
        outline_actions.pack(side='right')
        
        tk.Button(outline_actions, text="➕ Add Scene",
                 bg=self.colors['success'], fg='white',
                 font=self.fonts['body'], relief='flat',
                 padx=12, pady=6, cursor='hand2',
                 command=self.add_scene).pack(side='left', padx=(0, 8))
        
        tk.Button(outline_actions, text="✏️ Edit",
                 bg=self.colors['accent'], fg='white',
                 font=self.fonts['body'], relief='flat',
                 padx=12, pady=6, cursor='hand2',
                 command=self.edit_scene).pack(side='left', padx=(0, 8))
        
        tk.Button(outline_actions, text="🗑️ Delete",
                 bg=self.colors['danger'], fg='white',
                 font=self.fonts['body'], relief='flat',
                 padx=12, pady=6, cursor='hand2',
                 command=self.delete_scene).pack(side='left')
        
        # Outline table
        table_frame = tk.Frame(outline_frame, bg=self.colors['bg_primary'])
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Create treeview
        columns = ('Act', 'Beat', 'Scene #', 'Description', 'Status', 'Characters', 'Location')
        self.outline_tree = ttk.Treeview(table_frame, 
                                        columns=columns, 
                                        show='tree headings',
                                        style='Modern.Treeview')
        
        # Configure columns
        self.outline_tree.heading('#0', text='ID')
        self.outline_tree.column('#0', width=50, minwidth=50)
        
        column_widths = {
            'Act': 80, 'Beat': 180, 'Scene #': 80, 'Description': 300,
            'Status': 100, 'Characters': 150, 'Location': 120
        }
        
        for col in columns:
            self.outline_tree.heading(col, text=col)
            width = column_widths.get(col, 120)
            self.outline_tree.column(col, width=width, minwidth=80)
        
        # Scrollbars
        outline_v_scroll = ttk.Scrollbar(table_frame, orient='vertical', 
                                        command=self.outline_tree.yview)
        outline_h_scroll = ttk.Scrollbar(table_frame, orient='horizontal', 
                                        command=self.outline_tree.xview)
        
        self.outline_tree.configure(yscrollcommand=outline_v_scroll.set,
                                   xscrollcommand=outline_h_scroll.set)
        
        # Grid layout
        self.outline_tree.grid(row=0, column=0, sticky='nsew')
        outline_v_scroll.grid(row=0, column=1, sticky='ns')
        outline_h_scroll.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click for inline editing
        self.outline_tree.bind('<Double-1>', self.on_outline_cell_double_click)
    
    def create_notes_tab(self):
        """Create the notes editing tab"""
        notes_frame = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
        self.notebook.add(notes_frame, text="📝 Notes")
        
        # Header section
        header = tk.Frame(notes_frame, bg=self.colors['bg_primary'])
        header.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(header, text="Development Notes", style='Subheading.TLabel').pack(side='left')
        
        # Action buttons
        notes_actions = tk.Frame(header, bg=self.colors['bg_primary'])
        notes_actions.pack(side='right')
        
        tk.Button(notes_actions, text="➕ Add Note",
                 bg=self.colors['success'], fg='white',
                 font=self.fonts['body'], relief='flat',
                 padx=12, pady=6, cursor='hand2',
                 command=self.add_note).pack(side='left', padx=(0, 8))
        
        tk.Button(notes_actions, text="✏️ Edit",
                 bg=self.colors['accent'], fg='white',
                 font=self.fonts['body'], relief='flat',
                 padx=12, pady=6, cursor='hand2',
                 command=self.edit_note).pack(side='left', padx=(0, 8))
        
        tk.Button(notes_actions, text="🗑️ Delete",
                 bg=self.colors['danger'], fg='white',
                 font=self.fonts['body'], relief='flat',
                 padx=12, pady=6, cursor='hand2',
                 command=self.delete_note).pack(side='left')
        
        # Notes table
        table_frame = tk.Frame(notes_frame, bg=self.colors['bg_primary'])
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Create treeview
        columns = ('Title', 'Category', 'Content Preview', 'Created')
        self.notes_tree = ttk.Treeview(table_frame, 
                                      columns=columns, 
                                      show='tree headings',
                                      style='Modern.Treeview')
        
        # Configure columns
        self.notes_tree.heading('#0', text='ID')
        self.notes_tree.column('#0', width=50, minwidth=50)
        
        column_widths = {
            'Title': 200, 'Category': 120, 'Content Preview': 400, 'Created': 120
        }
        
        for col in columns:
            self.notes_tree.heading(col, text=col)
            width = column_widths.get(col, 120)
            self.notes_tree.column(col, width=width, minwidth=80)
        
        # Scrollbars
        notes_v_scroll = ttk.Scrollbar(table_frame, orient='vertical', 
                                      command=self.notes_tree.yview)
        notes_h_scroll = ttk.Scrollbar(table_frame, orient='horizontal', 
                                      command=self.notes_tree.xview)
        
        self.notes_tree.configure(yscrollcommand=notes_v_scroll.set,
                                 xscrollcommand=notes_h_scroll.set)
        
        # Grid layout
        self.notes_tree.grid(row=0, column=0, sticky='nsew')
        notes_v_scroll.grid(row=0, column=1, sticky='ns')
        notes_h_scroll.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click for inline editing
        self.notes_tree.bind('<Double-1>', self.on_notes_cell_double_click)
    
    def create_status_bar(self):
        """Create Tailwind-style status bar"""
        # Status bar with border-t and proper height
        status_frame = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=48)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        # Add top border
        border = tk.Frame(status_frame, bg=self.colors['border_light'], height=1)
        border.pack(fill='x')
        
        # Content frame with proper padding
        content_frame = tk.Frame(status_frame, bg=self.colors['bg_secondary'])
        content_frame.pack(fill='both', expand=True, padx=24, pady=12)
        
        # Status message on left
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(content_frame, 
                               textvariable=self.status_var,
                               bg=self.colors['bg_secondary'],
                               fg=self.colors['text_secondary'],
                               font=self.fonts['caption'],
                               anchor='w')
        status_label.pack(side='left')
        
        # Project stats on right
        self.stats_var = tk.StringVar()
        stats_label = tk.Label(content_frame,
                              textvariable=self.stats_var,
                              bg=self.colors['bg_secondary'],
                              fg=self.colors['text_muted'],
                              font=self.fonts['caption'],
                              anchor='e')
        stats_label.pack(side='right')
    
    # Data loading methods
    def refresh_all_tables(self):
        """Refresh all table data"""
        self.load_characters()
        self.load_outline()
        self.load_notes()
        self.update_stats()
        self.status_var.set("Data refreshed")
    
    def load_characters(self):
        """Load characters data into the table"""
        # Clear existing data
        for item in self.characters_tree.get_children():
            self.characters_tree.delete(item)
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, name, archetype, gender, age, 
                       romantic_challenge, lovable_trait, comedic_flaw
                FROM characters ORDER BY id
            """)
            
            for row in cursor.fetchall():
                values = (
                    row['name'] or '',
                    row['archetype'] or '',
                    row['gender'] or '',
                    row['age'] or '',
                    (row['romantic_challenge'] or '')[:50] + '...' if len(row['romantic_challenge'] or '') > 50 else (row['romantic_challenge'] or ''),
                    (row['lovable_trait'] or '')[:50] + '...' if len(row['lovable_trait'] or '') > 50 else (row['lovable_trait'] or ''),
                    (row['comedic_flaw'] or '')[:50] + '...' if len(row['comedic_flaw'] or '') > 50 else (row['comedic_flaw'] or '')
                )
                self.characters_tree.insert('', 'end', text=str(row['id']), values=values)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load characters: {e}")
    
    def load_outline(self):
        """Load story outline data into the table"""
        # Clear existing data
        for item in self.outline_tree.get_children():
            self.outline_tree.delete(item)
        
        try:
            cursor = self.conn.cursor()
            
            # Try extended outline table first
            try:
                cursor.execute("""
                    SELECT id, act, beat, scene_number, description, 
                           status, characters, location
                    FROM story_outline_extended ORDER BY scene_number
                """)
                rows = cursor.fetchall()
                
                for row in rows:
                    values = (
                        row['act'] or '',
                        row['beat'] or '',
                        str(row['scene_number']) or '',
                        (row['description'] or '')[:100] + '...' if len(row['description'] or '') > 100 else (row['description'] or ''),
                        row['status'] or '',
                        row['characters'] or '',
                        row['location'] or ''
                    )
                    self.outline_tree.insert('', 'end', text=str(row['id']), values=values)
            
            except sqlite3.OperationalError:
                # Fallback to simple outline table
                cursor.execute("""
                    SELECT id, act, scene, key_characters, key_events
                    FROM story_outline ORDER BY act, scene
                """)
                rows = cursor.fetchall()
                
                for row in rows:
                    values = (
                        f"Act {row['act']}",
                        'Scene',
                        str(row['scene']),
                        (row['key_events'] or '')[:100] + '...' if len(row['key_events'] or '') > 100 else (row['key_events'] or ''),
                        'placeholder',
                        row['key_characters'] or '',
                        ''
                    )
                    self.outline_tree.insert('', 'end', text=str(row['id']), values=values)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load outline: {e}")
    
    def load_notes(self):
        """Load notes data into the table"""
        # Clear existing data
        for item in self.notes_tree.get_children():
            self.notes_tree.delete(item)
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, title, category, content, created_at
                FROM notes ORDER BY created_at DESC
            """)
            
            for row in cursor.fetchall():
                # Format date
                created = row['created_at']
                if created:
                    try:
                        dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                        created = dt.strftime('%Y-%m-%d')
                    except:
                        created = created[:10]  # Take first 10 chars
                
                # Preview content
                content_preview = (row['content'] or '')[:100] + '...' if len(row['content'] or '') > 100 else (row['content'] or '')
                
                values = (
                    row['title'] or '',
                    row['category'] or '',
                    content_preview,
                    created or ''
                )
                self.notes_tree.insert('', 'end', text=str(row['id']), values=values)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load notes: {e}")
    
    def update_stats(self):
        """Update the statistics display"""
        try:
            cursor = self.conn.cursor()
            
            # Count characters
            cursor.execute("SELECT COUNT(*) FROM characters")
            char_count = cursor.fetchone()[0]
            
            # Count scenes
            try:
                cursor.execute("SELECT COUNT(*) FROM story_outline_extended")
                scene_count = cursor.fetchone()[0]
            except:
                cursor.execute("SELECT COUNT(*) FROM story_outline")
                scene_count = cursor.fetchone()[0]
            
            # Count notes
            cursor.execute("SELECT COUNT(*) FROM notes")
            notes_count = cursor.fetchone()[0]
            
            self.stats_var.set(f"Characters: {char_count} | Scenes: {scene_count} | Notes: {notes_count}")
        
        except Exception as e:
            self.stats_var.set("Stats unavailable")
    
    # Inline editing methods
    def on_character_cell_double_click(self, event):
        """Handle double-click on character cell for inline editing"""
        item = self.characters_tree.selection()[0] if self.characters_tree.selection() else None
        if not item:
            return
        
        # Get the column that was clicked
        column = self.characters_tree.identify_column(event.x)
        if column == '#0':  # Skip ID column
            return
        
        # Convert column number to column name
        columns = ['Name', 'Archetype', 'Gender', 'Age', 'Challenge', 'Trait', 'Flaw']
        col_index = int(column.replace('#', '')) - 1
        if col_index < 0 or col_index >= len(columns):
            return
        
        column_name = columns[col_index]
        self.start_inline_edit(self.characters_tree, item, column, column_name, 'characters')
    
    def on_outline_cell_double_click(self, event):
        """Handle double-click on outline cell for inline editing"""
        item = self.outline_tree.selection()[0] if self.outline_tree.selection() else None
        if not item:
            return
        
        # Get the column that was clicked
        column = self.outline_tree.identify_column(event.x)
        if column == '#0':  # Skip ID column
            return
        
        # Convert column number to column name
        columns = ['Act', 'Beat', 'Scene #', 'Description', 'Status', 'Characters', 'Location']
        col_index = int(column.replace('#', '')) - 1
        if col_index < 0 or col_index >= len(columns):
            return
        
        column_name = columns[col_index]
        table_name = 'story_outline_extended'  # Default to extended, will handle simple in save method
        self.start_inline_edit(self.outline_tree, item, column, column_name, table_name)
    
    def on_notes_cell_double_click(self, event):
        """Handle double-click on notes cell for inline editing"""
        item = self.notes_tree.selection()[0] if self.notes_tree.selection() else None
        if not item:
            return
        
        # Get the column that was clicked
        column = self.notes_tree.identify_column(event.x)
        if column == '#0':  # Skip ID column
            return
        
        # Convert column number to column name
        columns = ['Title', 'Category', 'Content Preview', 'Created']
        col_index = int(column.replace('#', '')) - 1
        if col_index < 0 or col_index >= len(columns):
            return
        
        column_name = columns[col_index]
        if column_name == 'Created':  # Don't allow editing created date
            return
        
        self.start_inline_edit(self.notes_tree, item, column, column_name, 'notes')
    
    def start_inline_edit(self, tree, item, column, column_name, table_name):
        """Start inline editing for a cell"""
        # Close any existing edit
        self.finish_inline_edit()
        
        # Get the bounding box of the cell
        bbox = tree.bbox(item, column)
        if not bbox:
            return
        
        # Get current value
        current_value = tree.set(item, column_name)
        
        # Create entry widget for editing
        self.edit_entry = tk.Entry(tree, 
                                  font=self.fonts['body'],
                                  bg=self.colors['bg_input'],
                                  fg=self.colors['text_primary'],
                                  relief='solid',
                                  bd=1)
        self.edit_entry.insert(0, current_value)
        self.edit_entry.select_range(0, tk.END)
        
        # Position the entry widget over the cell
        self.edit_entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        self.edit_entry.focus()
        
        # Store editing state
        self.editing_item = item
        self.editing_column = column_name
        self.editing_tree = tree
        self.editing_table = table_name
        
        # Bind events to finish editing
        self.edit_entry.bind('<Return>', self.finish_inline_edit)
        self.edit_entry.bind('<Escape>', self.cancel_inline_edit)
        self.edit_entry.bind('<FocusOut>', self.finish_inline_edit)
    
    def finish_inline_edit(self, event=None):
        """Finish inline editing and save changes"""
        if not self.edit_entry or not self.editing_item:
            return
        
        # Get new value
        new_value = self.edit_entry.get()
        
        # Update the tree display
        self.editing_tree.set(self.editing_item, self.editing_column, new_value)
        
        # Save to database
        self.save_inline_edit(new_value)
        
        # Clean up
        self.cleanup_inline_edit()
    
    def cancel_inline_edit(self, event=None):
        """Cancel inline editing without saving"""
        self.cleanup_inline_edit()
    
    def cleanup_inline_edit(self):
        """Clean up inline editing widgets and state"""
        if self.edit_entry:
            self.edit_entry.destroy()
            self.edit_entry = None
        
        self.editing_item = None
        self.editing_column = None
        self.editing_tree = None
        self.editing_table = None
    
    def save_inline_edit(self, new_value):
        """Save inline edit to database"""
        if not self.editing_item or not self.editing_column or not self.editing_table:
            return
        
        try:
            # Get the record ID from the row index since we hid the ID column
            children = self.editing_tree.get_children()
            row_index = children.index(self.editing_item)
            
            cursor = self.conn.cursor()
            
            if self.editing_table == 'characters':
                # Get the actual ID for this row
                cursor.execute("SELECT id FROM characters ORDER BY id LIMIT 1 OFFSET ?", (row_index,))
                result = cursor.fetchone()
                if not result:
                    return
                item_id = result[0]
                
                # Map column names to database fields
                field_map = {
                    'Name': 'name',
                    'Archetype': 'archetype', 
                    'Gender': 'gender',
                    'Age': 'age',
                    'Challenge': 'romantic_challenge',
                    'Trait': 'lovable_trait',
                    'Flaw': 'comedic_flaw'
                }
                
                db_field = field_map.get(self.editing_column)
                if db_field:
                    cursor.execute(f"UPDATE characters SET {db_field} = ? WHERE id = ?", 
                                 (new_value, item_id))
            
            elif self.editing_table == 'story_outline_extended':
                # Get the actual ID for this row
                try:
                    cursor.execute("SELECT id FROM story_outline_extended ORDER BY scene_number LIMIT 1 OFFSET ?", (row_index,))
                    result = cursor.fetchone()
                    if not result:
                        return
                    item_id = result[0]
                    
                    # Map column names to database fields
                    field_map = {
                        'Act': 'act',
                        'Beat': 'beat',
                        'Scene #': 'scene_number',
                        'Description': 'description',
                        'Status': 'status',
                        'Characters': 'characters',
                        'Location': 'location'
                    }
                    
                    db_field = field_map.get(self.editing_column)
                    if db_field:
                        # Handle scene number as integer
                        if db_field == 'scene_number':
                            try:
                                new_value = int(new_value)
                            except ValueError:
                                self.status_var.set("❌ Scene number must be a number")
                                return
                        
                        cursor.execute(f"UPDATE story_outline_extended SET {db_field} = ? WHERE id = ?", 
                                     (new_value, item_id))
                
                except sqlite3.OperationalError:
                    # Fallback to simple story_outline table
                    cursor.execute("SELECT id FROM story_outline ORDER BY act, scene LIMIT 1 OFFSET ?", (row_index,))
                    result = cursor.fetchone()
                    if not result:
                        return
                    item_id = result[0]
                    
                    # Simple outline field mapping
                    field_map = {
                        'Act': 'act',
                        'Scene #': 'scene',
                        'Characters': 'key_characters',
                        'Description': 'key_events'
                    }
                    
                    db_field = field_map.get(self.editing_column)
                    if db_field:
                        if db_field in ['act', 'scene']:
                            try:
                                new_value = int(new_value)
                            except ValueError:
                                self.status_var.set("❌ Act/Scene must be a number")
                                return
                        
                        cursor.execute(f"UPDATE story_outline SET {db_field} = ? WHERE id = ?", 
                                     (new_value, item_id))
            
            elif self.editing_table == 'notes':
                # Get the actual ID for this row
                cursor.execute("SELECT id FROM notes ORDER BY created_at DESC LIMIT 1 OFFSET ?", (row_index,))
                result = cursor.fetchone()
                if not result:
                    return
                item_id = result[0]
                
                # Map column names to database fields
                field_map = {
                    'Title': 'title',
                    'Category': 'category',
                    'Content Preview': 'content'
                }
                
                db_field = field_map.get(self.editing_column)
                if db_field:
                    cursor.execute(f"UPDATE notes SET {db_field} = ? WHERE id = ?", 
                                 (new_value, item_id))
            
            self.conn.commit()
            self.status_var.set(f"✅ Updated {self.editing_column}")
            
        except Exception as e:
            self.status_var.set(f"❌ Error saving: {e}")
    
    # Character management methods
    def add_character(self):
        """Add a new character"""
        self.edit_character_dialog()
    
    def edit_character(self):
        """Edit selected character"""
        selection = self.characters_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a character to edit")
            return
        
        char_id = self.characters_tree.item(selection[0])['text']
        self.edit_character_dialog(char_id)
    
    def delete_character(self):
        """Delete selected character"""
        selection = self.characters_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a character to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this character?"):
            char_id = self.characters_tree.item(selection[0])['text']
            try:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM characters WHERE id = ?", (char_id,))
                self.conn.commit()
                self.load_characters()
                self.update_stats()
                self.status_var.set("Character deleted")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete character: {e}")
    
    def edit_character_dialog(self, char_id=None):
        """Show character editing dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Character" if char_id else "Add Character")
        dialog.geometry("600x700")
        dialog.configure(bg=self.colors['bg_primary'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (700 // 2)
        dialog.geometry(f"600x700+{x}+{y}")
        
        # Load existing data if editing
        character_data = {}
        if char_id:
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT * FROM characters WHERE id = ?", (char_id,))
                row = cursor.fetchone()
                if row:
                    character_data = dict(row)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load character: {e}")
                dialog.destroy()
                return
        
        # Dialog content
        main_frame = tk.Frame(dialog, bg=self.colors['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title
        ttk.Label(main_frame, 
                 text="Character Details",
                 style='Heading.TLabel').pack(anchor='w', pady=(0, 20))
        
        # Form fields
        fields = {}
        
        # Name field
        tk.Label(main_frame, text="Name *", 
                bg=self.colors['bg_primary'],
                fg=self.colors['text_primary'],
                font=self.fonts['body_bold']).pack(anchor='w', pady=(0, 5))
        
        fields['name'] = tk.Entry(main_frame, font=self.fonts['body'],
                                 bg=self.colors['bg_secondary'],
                                 relief='flat', bd=1)
        fields['name'].pack(fill='x', pady=(0, 15), ipady=8)
        fields['name'].insert(0, character_data.get('name', ''))
        
        # Archetype field
        tk.Label(main_frame, text="Archetype", 
                bg=self.colors['bg_primary'],
                fg=self.colors['text_primary'],
                font=self.fonts['body_bold']).pack(anchor='w', pady=(0, 5))
        
        fields['archetype'] = tk.Entry(main_frame, font=self.fonts['body'],
                                      bg=self.colors['bg_secondary'],
                                      relief='flat', bd=1)
        fields['archetype'].pack(fill='x', pady=(0, 15), ipady=8)
        fields['archetype'].insert(0, character_data.get('archetype', ''))
        
        # Row for Gender and Age
        row_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        row_frame.pack(fill='x', pady=(0, 15))
        
        # Gender
        gender_frame = tk.Frame(row_frame, bg=self.colors['bg_primary'])
        gender_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        tk.Label(gender_frame, text="Gender", 
                bg=self.colors['bg_primary'],
                fg=self.colors['text_primary'],
                font=self.fonts['body_bold']).pack(anchor='w', pady=(0, 5))
        
        fields['gender'] = tk.Entry(gender_frame, font=self.fonts['body'],
                                   bg=self.colors['bg_secondary'],
                                   relief='flat', bd=1)
        fields['gender'].pack(fill='x', ipady=8)
        fields['gender'].insert(0, character_data.get('gender', ''))
        
        # Age
        age_frame = tk.Frame(row_frame, bg=self.colors['bg_primary'])
        age_frame.pack(side='left', fill='x', expand=True)
        
        tk.Label(age_frame, text="Age", 
                bg=self.colors['bg_primary'],
                fg=self.colors['text_primary'],
                font=self.fonts['body_bold']).pack(anchor='w', pady=(0, 5))
        
        fields['age'] = tk.Entry(age_frame, font=self.fonts['body'],
                                bg=self.colors['bg_secondary'],
                                relief='flat', bd=1)
        fields['age'].pack(fill='x', ipady=8)
        fields['age'].insert(0, character_data.get('age', ''))
        
        # Text area fields
        text_fields = [
            ('romantic_challenge', 'Romantic Challenge'),
            ('lovable_trait', 'Lovable Trait'),
            ('comedic_flaw', 'Comedic Flaw'),
            ('notes', 'Additional Notes')
        ]
        
        for field_name, label in text_fields:
            tk.Label(main_frame, text=label, 
                    bg=self.colors['bg_primary'],
                    fg=self.colors['text_primary'],
                    font=self.fonts['body_bold']).pack(anchor='w', pady=(0, 5))
            
            text_widget = tk.Text(main_frame, height=3, 
                                 font=self.fonts['body'],
                                 bg=self.colors['bg_secondary'],
                                 relief='flat', bd=1,
                                 wrap='word')
            text_widget.pack(fill='x', pady=(0, 15))
            text_widget.insert('1.0', character_data.get(field_name, ''))
            fields[field_name] = text_widget
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        button_frame.pack(fill='x', pady=(20, 0))
        
        def save_character():
            # Validate required fields
            if not fields['name'].get().strip():
                messagebox.showerror("Validation Error", "Name is required")
                return
            
            try:
                cursor = self.conn.cursor()
                
                # Collect data
                data = {
                    'name': fields['name'].get().strip(),
                    'archetype': fields['archetype'].get().strip(),
                    'gender': fields['gender'].get().strip(),
                    'age': fields['age'].get().strip(),
                    'romantic_challenge': fields['romantic_challenge'].get('1.0', 'end-1c').strip(),
                    'lovable_trait': fields['lovable_trait'].get('1.0', 'end-1c').strip(),
                    'comedic_flaw': fields['comedic_flaw'].get('1.0', 'end-1c').strip(),
                    'notes': fields['notes'].get('1.0', 'end-1c').strip()
                }
                
                if char_id:
                    # Update existing character
                    cursor.execute("""
                        UPDATE characters SET 
                        name=?, archetype=?, gender=?, age=?,
                        romantic_challenge=?, lovable_trait=?, comedic_flaw=?, notes=?
                        WHERE id=?
                    """, (*data.values(), char_id))
                    action = "updated"
                else:
                    # Insert new character
                    cursor.execute("""
                        INSERT INTO characters 
                        (name, archetype, gender, age, romantic_challenge, 
                         lovable_trait, comedic_flaw, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, tuple(data.values()))
                    action = "added"
                
                self.conn.commit()
                self.load_characters()
                self.update_stats()
                self.status_var.set(f"Character {action}")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save character: {e}")
        
        tk.Button(button_frame, text="Cancel",
                 bg=self.colors['bg_tertiary'],
                 fg=self.colors['text_primary'],
                 font=self.fonts['body'],
                 relief='flat', padx=20, pady=8,
                 command=dialog.destroy).pack(side='right', padx=(8, 0))
        
        tk.Button(button_frame, text="Save Character",
                 bg=self.colors['success'],
                 fg='white',
                 font=self.fonts['body_bold'],
                 relief='flat', padx=20, pady=8,
                 command=save_character).pack(side='right')
    
    # Scene management methods (similar structure to characters)
    def add_scene(self):
        """Add a new scene"""
        self.edit_scene_dialog()
    
    def edit_scene(self):
        """Edit selected scene"""
        selection = self.outline_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a scene to edit")
            return
        
        scene_id = self.outline_tree.item(selection[0])['text']
        self.edit_scene_dialog(scene_id)
    
    def delete_scene(self):
        """Delete selected scene"""
        selection = self.outline_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a scene to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this scene?"):
            scene_id = self.outline_tree.item(selection[0])['text']
            try:
                cursor = self.conn.cursor()
                # Try extended table first
                try:
                    cursor.execute("DELETE FROM story_outline_extended WHERE id = ?", (scene_id,))
                except:
                    cursor.execute("DELETE FROM story_outline WHERE id = ?", (scene_id,))
                
                self.conn.commit()
                self.load_outline()
                self.update_stats()
                self.status_var.set("Scene deleted")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete scene: {e}")
    
    def edit_scene_dialog(self, scene_id=None):
        """Show scene editing dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Scene" if scene_id else "Add Scene")
        dialog.geometry("800x700")
        dialog.configure(bg=self.colors['bg_primary'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (dialog.winfo_screenheight() // 2) - (700 // 2)
        dialog.geometry(f"800x700+{x}+{y}")
        
        # Determine which table we're working with
        is_extended = True
        scene_data = {}
        
        if scene_id:
            try:
                cursor = self.conn.cursor()
                # Try extended table first
                try:
                    cursor.execute("SELECT * FROM story_outline_extended WHERE id = ?", (scene_id,))
                    row = cursor.fetchone()
                    if row:
                        scene_data = dict(row)
                    else:
                        is_extended = False
                except sqlite3.OperationalError:
                    is_extended = False
                
                # Fallback to simple table
                if not is_extended:
                    cursor.execute("SELECT * FROM story_outline WHERE id = ?", (scene_id,))
                    row = cursor.fetchone()
                    if row:
                        scene_data = dict(row)
                        
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load scene: {e}")
                dialog.destroy()
                return
        else:
            # Check if extended table exists for new scenes
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='story_outline_extended'")
                is_extended = cursor.fetchone() is not None
            except:
                is_extended = False
        
        # Dialog content
        main_frame = tk.Frame(dialog, bg=self.colors['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title
        ttk.Label(main_frame, 
                 text="Scene Details",
                 style='Heading.TLabel').pack(anchor='w', pady=(0, 20))
        
        fields = {}
        
        if is_extended:
            # Extended scene form
            # Act field
            tk.Label(main_frame, text="Act *", 
                    bg=self.colors['bg_primary'],
                    fg=self.colors['text_primary'],
                    font=self.fonts['body_bold']).pack(anchor='w', pady=(0, 5))
            
            fields['act'] = tk.Entry(main_frame, font=self.fonts['body'],
                                    bg=self.colors['bg_secondary'],
                                    relief='flat', bd=1)
            fields['act'].pack(fill='x', pady=(0, 15), ipady=8)
            fields['act'].insert(0, scene_data.get('act', 'Act I'))
            
            # Beat field
            tk.Label(main_frame, text="Beat *", 
                    bg=self.colors['bg_primary'],
                    fg=self.colors['text_primary'],
                    font=self.fonts['body_bold']).pack(anchor='w', pady=(0, 5))
            
            fields['beat'] = tk.Entry(main_frame, font=self.fonts['body'],
                                     bg=self.colors['bg_secondary'],
                                     relief='flat', bd=1)
            fields['beat'].pack(fill='x', pady=(0, 15), ipady=8)
            fields['beat'].insert(0, scene_data.get('beat', ''))
            
            # Scene Number and Status row
            row_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
            row_frame.pack(fill='x', pady=(0, 15))
            
            # Scene Number
            scene_frame = tk.Frame(row_frame, bg=self.colors['bg_primary'])
            scene_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
            
            tk.Label(scene_frame, text="Scene Number *", 
                    bg=self.colors['bg_primary'],
                    fg=self.colors['text_primary'],
                    font=self.fonts['body_bold']).pack(anchor='w', pady=(0, 5))
            
            fields['scene_number'] = tk.Entry(scene_frame, font=self.fonts['body'],
                                             bg=self.colors['bg_secondary'],
                                             relief='flat', bd=1)
            fields['scene_number'].pack(fill='x', ipady=8)
            fields['scene_number'].insert(0, str(scene_data.get('scene_number', '')))
            
            # Status
            status_frame = tk.Frame(row_frame, bg=self.colors['bg_primary'])
            status_frame.pack(side='left', fill='x', expand=True)
            
            tk.Label(status_frame, text="Status", 
                    bg=self.colors['bg_primary'],
                    fg=self.colors['text_primary'],
                    font=self.fonts['body_bold']).pack(anchor='w', pady=(0, 5))
            
            fields['status'] = ttk.Combobox(status_frame, font=self.fonts['body'],
                                           values=['placeholder', 'drafted', 'completed'])
            fields['status'].pack(fill='x', ipady=4)
            fields['status'].set(scene_data.get('status', 'placeholder'))
            
            # Characters and Location row
            row_frame2 = tk.Frame(main_frame, bg=self.colors['bg_primary'])
            row_frame2.pack(fill='x', pady=(0, 15))
            
            # Characters
            char_frame = tk.Frame(row_frame2, bg=self.colors['bg_primary'])
            char_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
            
            tk.Label(char_frame, text="Characters", 
                    bg=self.colors['bg_primary'],
                    fg=self.colors['text_primary'],
                    font=self.fonts['body_bold']).pack(anchor='w', pady=(0, 5))
            
            fields['characters'] = tk.Entry(char_frame, font=self.fonts['body'],
                                           bg=self.colors['bg_secondary'],
                                           relief='flat', bd=1)
            fields['characters'].pack(fill='x', ipady=8)
            fields['characters'].insert(0, scene_data.get('characters', ''))
            
            # Location
            location_frame = tk.Frame(row_frame2, bg=self.colors['bg_primary'])
            location_frame.pack(side='left', fill='x', expand=True)
            
            tk.Label(location_frame, text="Location", 
                    bg=self.colors['bg_primary'],
                    fg=self.colors['text_primary'],
                    font=self.fonts['body_bold']).pack(anchor='w', pady=(0, 5))
            
            fields['location'] = tk.Entry(location_frame, font=self.fonts['body'],
                                         bg=self.colors['bg_secondary'],
                                         relief='flat', bd=1)
            fields['location'].pack(fill='x', ipady=8)
            fields['location'].insert(0, scene_data.get('location', ''))
            
            # Description field
            tk.Label(main_frame, text="Description", 
                    bg=self.colors['bg_primary'],
                    fg=self.colors['text_primary'],
                    font=self.fonts['body_bold']).pack(anchor='w', pady=(0, 5))
            
            fields['description'] = tk.Text(main_frame, height=4, 
                                          font=self.fonts['body'],
                                          bg=self.colors['bg_secondary'],
                                          relief='flat', bd=1, wrap='word')
            fields['description'].pack(fill='x', pady=(0, 15))
            fields['description'].insert('1.0', scene_data.get('description', ''))
            
            # Notes field
            tk.Label(main_frame, text="Notes", 
                    bg=self.colors['bg_primary'],
                    fg=self.colors['text_primary'],
                    font=self.fonts['body_bold']).pack(anchor='w', pady=(0, 5))
            
            fields['notes'] = tk.Text(main_frame, height=4, 
                                    font=self.fonts['body'],
                                    bg=self.colors['bg_secondary'],
                                    relief='flat', bd=1, wrap='word')
            fields['notes'].pack(fill='x', pady=(0, 20))
            fields['notes'].insert('1.0', scene_data.get('notes', ''))
            
        else:
            # Simple scene form
            # Act and Scene row
            row_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
            row_frame.pack(fill='x', pady=(0, 15))
            
            # Act
            act_frame = tk.Frame(row_frame, bg=self.colors['bg_primary'])
            act_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
            
            tk.Label(act_frame, text="Act *", 
                    bg=self.colors['bg_primary'],
                    fg=self.colors['text_primary'],
                    font=self.fonts['body_bold']).pack(anchor='w', pady=(0, 5))
            
            fields['act'] = tk.Entry(act_frame, font=self.fonts['body'],
                                    bg=self.colors['bg_secondary'],
                                    relief='flat', bd=1)
            fields['act'].pack(fill='x', ipady=8)
            fields['act'].insert(0, str(scene_data.get('act', '1')))
            
            # Scene
            scene_frame = tk.Frame(row_frame, bg=self.colors['bg_primary'])
            scene_frame.pack(side='left', fill='x', expand=True)
            
            tk.Label(scene_frame, text="Scene *", 
                    bg=self.colors['bg_primary'],
                    fg=self.colors['text_primary'],
                    font=self.fonts['body_bold']).pack(anchor='w', pady=(0, 5))
            
            fields['scene'] = tk.Entry(scene_frame, font=self.fonts['body'],
                                      bg=self.colors['bg_secondary'],
                                      relief='flat', bd=1)
            fields['scene'].pack(fill='x', ipady=8)
            fields['scene'].insert(0, str(scene_data.get('scene', '')))
            
            # Key Characters field
            tk.Label(main_frame, text="Key Characters", 
                    bg=self.colors['bg_primary'],
                    fg=self.colors['text_primary'],
                    font=self.fonts['body_bold']).pack(anchor='w', pady=(0, 5))
            
            fields['key_characters'] = tk.Entry(main_frame, font=self.fonts['body'],
                                               bg=self.colors['bg_secondary'],
                                               relief='flat', bd=1)
            fields['key_characters'].pack(fill='x', pady=(0, 15), ipady=8)
            fields['key_characters'].insert(0, scene_data.get('key_characters', ''))
            
            # Key Events field
            tk.Label(main_frame, text="Key Events", 
                    bg=self.colors['bg_primary'],
                    fg=self.colors['text_primary'],
                    font=self.fonts['body_bold']).pack(anchor='w', pady=(0, 5))
            
            fields['key_events'] = tk.Text(main_frame, height=8, 
                                         font=self.fonts['body'],
                                         bg=self.colors['bg_secondary'],
                                         relief='flat', bd=1, wrap='word')
            fields['key_events'].pack(fill='x', expand=True, pady=(0, 20))
            fields['key_events'].insert('1.0', scene_data.get('key_events', ''))
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        button_frame.pack(fill='x')
        
        def save_scene():
            try:
                cursor = self.conn.cursor()
                
                if is_extended:
                    # Validate required fields
                    if not fields['act'].get().strip() or not fields['beat'].get().strip():
                        messagebox.showerror("Validation Error", "Act and Beat are required")
                        return
                    
                    # Get scene number
                    try:
                        scene_number = int(fields['scene_number'].get().strip()) if fields['scene_number'].get().strip() else None
                    except ValueError:
                        messagebox.showerror("Validation Error", "Scene number must be a number")
                        return
                    
                    if scene_number is None:
                        # Auto-assign scene number
                        cursor.execute("SELECT MAX(scene_number) FROM story_outline_extended")
                        max_scene = cursor.fetchone()[0] or 0
                        scene_number = max_scene + 1
                    
                    data = {
                        'act': fields['act'].get().strip(),
                        'act_number': int(fields['act'].get().strip().split()[-1]) if 'act' in fields['act'].get().lower() else 1,
                        'beat': fields['beat'].get().strip(),
                        'scene_number': scene_number,
                        'description': fields['description'].get('1.0', 'end-1c').strip(),
                        'status': fields['status'].get(),
                        'characters': fields['characters'].get().strip(),
                        'location': fields['location'].get().strip(),
                        'notes': fields['notes'].get('1.0', 'end-1c').strip()
                    }
                    
                    if scene_id:
                        cursor.execute("""
                            UPDATE story_outline_extended SET 
                            act=?, act_number=?, beat=?, scene_number=?, description=?,
                            status=?, characters=?, location=?, notes=?
                            WHERE id=?
                        """, (*data.values(), scene_id))
                        action = "updated"
                    else:
                        cursor.execute("""
                            INSERT INTO story_outline_extended 
                            (act, act_number, beat, scene_number, description, status, characters, location, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, tuple(data.values()))
                        action = "added"
                        
                else:
                    # Simple table
                    # Validate required fields
                    if not fields['act'].get().strip() or not fields['scene'].get().strip():
                        messagebox.showerror("Validation Error", "Act and Scene are required")
                        return
                    
                    try:
                        act = int(fields['act'].get().strip())
                        scene = int(fields['scene'].get().strip())
                    except ValueError:
                        messagebox.showerror("Validation Error", "Act and Scene must be numbers")
                        return
                    
                    data = {
                        'act': act,
                        'scene': scene,
                        'key_characters': fields['key_characters'].get().strip(),
                        'key_events': fields['key_events'].get('1.0', 'end-1c').strip()
                    }
                    
                    if scene_id:
                        cursor.execute("""
                            UPDATE story_outline SET 
                            act=?, scene=?, key_characters=?, key_events=?
                            WHERE id=?
                        """, (*data.values(), scene_id))
                        action = "updated"
                    else:
                        cursor.execute("""
                            INSERT INTO story_outline (act, scene, key_characters, key_events)
                            VALUES (?, ?, ?, ?)
                        """, tuple(data.values()))
                        action = "added"
                
                self.conn.commit()
                self.load_outline()
                self.update_stats()
                self.status_var.set(f"Scene {action}")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save scene: {e}")
        
        tk.Button(button_frame, text="Cancel",
                 bg=self.colors['bg_tertiary'],
                 fg=self.colors['text_primary'],
                 font=self.fonts['body'],
                 relief='flat', padx=20, pady=8,
                 command=dialog.destroy).pack(side='right', padx=(8, 0))
        
        tk.Button(button_frame, text="Save Scene",
                 bg=self.colors['success'],
                 fg='white',
                 font=self.fonts['body_bold'],
                 relief='flat', padx=20, pady=8,
                 command=save_scene).pack(side='right')
    
    # Notes management methods (similar structure)
    def add_note(self):
        """Add a new note"""
        self.edit_note_dialog()
    
    def edit_note(self):
        """Edit selected note"""
        selection = self.notes_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a note to edit")
            return
        
        note_id = self.notes_tree.item(selection[0])['text']
        self.edit_note_dialog(note_id)
    
    def delete_note(self):
        """Delete selected note"""
        selection = self.notes_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a note to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this note?"):
            note_id = self.notes_tree.item(selection[0])['text']
            try:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
                self.conn.commit()
                self.load_notes()
                self.update_stats()
                self.status_var.set("Note deleted")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete note: {e}")
    
    def edit_note_dialog(self, note_id=None):
        """Show note editing dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Note" if note_id else "Add Note")
        dialog.geometry("700x600")
        dialog.configure(bg=self.colors['bg_primary'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"700x600+{x}+{y}")
        
        # Load existing data if editing
        note_data = {}
        if note_id:
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
                row = cursor.fetchone()
                if row:
                    note_data = dict(row)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load note: {e}")
                dialog.destroy()
                return
        
        # Dialog content
        main_frame = tk.Frame(dialog, bg=self.colors['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title
        ttk.Label(main_frame, 
                 text="Note Details",
                 style='Heading.TLabel').pack(anchor='w', pady=(0, 20))
        
        # Title field
        tk.Label(main_frame, text="Title *", 
                bg=self.colors['bg_primary'],
                fg=self.colors['text_primary'],
                font=self.fonts['body_bold']).pack(anchor='w', pady=(0, 5))
        
        title_entry = tk.Entry(main_frame, font=self.fonts['body'],
                              bg=self.colors['bg_secondary'],
                              relief='flat', bd=1)
        title_entry.pack(fill='x', pady=(0, 15), ipady=8)
        title_entry.insert(0, note_data.get('title', ''))
        
        # Category field
        tk.Label(main_frame, text="Category", 
                bg=self.colors['bg_primary'],
                fg=self.colors['text_primary'],
                font=self.fonts['body_bold']).pack(anchor='w', pady=(0, 5))
        
        category_entry = tk.Entry(main_frame, font=self.fonts['body'],
                                 bg=self.colors['bg_secondary'],
                                 relief='flat', bd=1)
        category_entry.pack(fill='x', pady=(0, 15), ipady=8)
        category_entry.insert(0, note_data.get('category', ''))
        
        # Content field
        tk.Label(main_frame, text="Content", 
                bg=self.colors['bg_primary'],
                fg=self.colors['text_primary'],
                font=self.fonts['body_bold']).pack(anchor='w', pady=(0, 5))
        
        content_text = scrolledtext.ScrolledText(main_frame, 
                                               height=15,
                                               font=self.fonts['body'],
                                               bg=self.colors['bg_secondary'],
                                               relief='flat', bd=1,
                                               wrap='word')
        content_text.pack(fill='both', expand=True, pady=(0, 20))
        content_text.insert('1.0', note_data.get('content', ''))
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        button_frame.pack(fill='x')
        
        def save_note():
            if not title_entry.get().strip():
                messagebox.showerror("Validation Error", "Title is required")
                return
            
            try:
                cursor = self.conn.cursor()
                
                data = {
                    'title': title_entry.get().strip(),
                    'category': category_entry.get().strip(),
                    'content': content_text.get('1.0', 'end-1c').strip()
                }
                
                if note_id:
                    cursor.execute("""
                        UPDATE notes SET title=?, category=?, content=?
                        WHERE id=?
                    """, (*data.values(), note_id))
                    action = "updated"
                else:
                    cursor.execute("""
                        INSERT INTO notes (title, category, content)
                        VALUES (?, ?, ?)
                    """, tuple(data.values()))
                    action = "added"
                
                self.conn.commit()
                self.load_notes()
                self.update_stats()
                self.status_var.set(f"Note {action}")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save note: {e}")
        
        tk.Button(button_frame, text="Cancel",
                 bg=self.colors['bg_tertiary'],
                 fg=self.colors['text_primary'],
                 font=self.fonts['body'],
                 relief='flat', padx=20, pady=8,
                 command=dialog.destroy).pack(side='right', padx=(8, 0))
        
        tk.Button(button_frame, text="Save Note",
                 bg=self.colors['success'],
                 fg='white',
                 font=self.fonts['body_bold'],
                 relief='flat', padx=20, pady=8,
                 command=save_note).pack(side='right')
    
    # Utility methods
    def save_all_changes(self):
        """Save all pending changes"""
        try:
            self.conn.commit()
            self.status_var.set("All changes saved")
            messagebox.showinfo("Success", "All changes have been saved to the database")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {e}")
    
    def export_project(self):
        """Export project data"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"{self.project_name}_export.json"
        )
        
        if filename:
            try:
                import json
                
                # Export all data
                export_data = {
                    'project_name': self.project_name,
                    'exported_at': datetime.now().isoformat(),
                    'characters': [],
                    'outline': [],
                    'notes': []
                }
                
                cursor = self.conn.cursor()
                
                # Export characters
                cursor.execute("SELECT * FROM characters")
                export_data['characters'] = [dict(row) for row in cursor.fetchall()]
                
                # Export outline
                try:
                    cursor.execute("SELECT * FROM story_outline_extended")
                    export_data['outline'] = [dict(row) for row in cursor.fetchall()]
                except:
                    cursor.execute("SELECT * FROM story_outline")
                    export_data['outline'] = [dict(row) for row in cursor.fetchall()]
                
                # Export notes
                cursor.execute("SELECT * FROM notes")
                export_data['notes'] = [dict(row) for row in cursor.fetchall()]
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                self.status_var.set(f"Exported to {filename}")
                messagebox.showinfo("Success", f"Project exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export project: {e}")


def launch_modern_editor(project_path: str):
    """Launch the modern project editor"""
    if not os.path.exists(project_path):
        messagebox.showerror("Error", f"Project path does not exist: {project_path}")
        return
    
    editor = ModernProjectEditor(project_path)
    editor.launch()


def launch_for_current_project():
    """Launch the editor for the current session project"""
    # This function can be called from lizzy.py
    try:
        # Import here to avoid circular imports
        from lizzy import session
        
        if not session.current_project:
            messagebox.showwarning("No Project", "No project is currently loaded")
            return
            
        project_path = f"projects/{session.current_project}"
        launch_modern_editor(project_path)
        
    except ImportError:
        messagebox.showerror("Error", "Could not access session information")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch editor: {e}")


if __name__ == "__main__":
    # Demo with a test project
    import tempfile
    import sqlite3
    
    # Create a temporary test project
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = os.path.join(tmpdir, "demo_project")
        os.makedirs(project_path)
        
        # Create test database
        db_path = os.path.join(project_path, "demo_project.sqlite")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create test tables
        cursor.execute("""
            CREATE TABLE characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                archetype TEXT,
                gender TEXT,
                age TEXT,
                romantic_challenge TEXT,
                lovable_trait TEXT,
                comedic_flaw TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert test data
        cursor.execute("""
            INSERT INTO characters (name, archetype, gender, age)
            VALUES ('Emma', 'Protagonist', 'Female', '28')
        """)
        
        cursor.execute("""
            INSERT INTO notes (title, content, category)
            VALUES ('Plot Idea', 'What if they meet at a coffee shop?', 'Ideas')
        """)
        
        conn.commit()
        conn.close()
        
        # Launch editor
        launch_modern_editor(project_path)