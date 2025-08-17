#!/usr/bin/env python3
"""
Polished Table Editor - Modern, clean GUI with professional styling
Inspired by modern web applications like Notion, Linear, or Supabase
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import sqlite3
import os
from typing import Dict, List, Any, Optional
import json

class PolishedTableEditor:
    """Professional table editor with modern styling"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.project_name = os.path.basename(project_path)
        self.db_path = os.path.join(project_path, f"{self.project_name}.sqlite")
        self.conn = None
        self.root = None
        self.current_table = None
        self.current_data = []
        
        # Connect to database
        self.connect_db()
        
        # Color scheme - modern and refined
        self.colors = {
            'bg_primary': '#f8fafc',       # Slightly cooler white background
            'bg_secondary': '#ffffff',     # Pure white cards
            'bg_tertiary': '#f1f5f9',     # Light blue-gray sections
            'bg_hover': '#f8fafc',         # Hover state
            'border': '#e2e8f0',          # Soft borders
            'border_focus': '#3b82f6',    # Blue focus
            'border_hover': '#cbd5e1',    # Hover border
            'text_primary': '#0f172a',    # Rich dark text
            'text_secondary': '#64748b',  # Cool gray text
            'text_muted': '#94a3b8',     # Lighter muted text
            'accent': '#3b82f6',          # Blue accent
            'accent_hover': '#2563eb',    # Darker blue
            'accent_light': '#dbeafe',    # Light blue background
            'success': '#10b981',         # Green
            'success_light': '#d1fae5',   # Light green
            'danger': '#ef4444',          # Red
            'danger_light': '#fee2e2',    # Light red
            'warning': '#f59e0b',         # Orange
            'shadow_light': '#e2e8f0',    # Light gray for subtle shadow
            'shadow_medium': '#cbd5e1',   # Medium gray for shadow
        }
    
    def connect_db(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
    
    def launch(self):
        """Launch the polished table editor"""
        self.root = tk.Tk()
        self.root.title(f"Table Editor - {self.project_name}")
        self.root.geometry("1600x1000")
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Set minimum window size for better UX
        self.root.minsize(1200, 800)
        
        # Configure modern fonts
        self.setup_fonts()
        
        # Configure modern styles
        self.setup_styles()
        
        # Create layout
        self.create_interface()
        
        # Load data
        self.refresh_tables()
        
        # Center window
        self.center_window()
        
        self.root.mainloop()
    
    def setup_fonts(self):
        """Setup modern font families"""
        self.fonts = {
            'heading_lg': ('SF Pro Display', 28, 'bold'),
            'heading_md': ('SF Pro Display', 20, 'bold'),
            'heading_sm': ('SF Pro Display', 16, 'bold'),
            'body_lg': ('SF Pro Text', 14),
            'body_md': ('SF Pro Text', 12),
            'body_sm': ('SF Pro Text', 11),
            'mono': ('SF Mono', 11),
        }
        
        # Fallback to system fonts if SF Pro not available
        try:
            test_font = font.Font(family='SF Pro Display', size=12)
        except:
            self.fonts = {
                'heading_lg': ('Helvetica Neue', 28, 'bold'),
                'heading_md': ('Helvetica Neue', 20, 'bold'),
                'heading_sm': ('Helvetica Neue', 16, 'bold'),
                'body_lg': ('Helvetica Neue', 14),
                'body_md': ('Helvetica Neue', 12),
                'body_sm': ('Helvetica Neue', 11),
                'mono': ('Monaco', 11),
            }
    
    def setup_styles(self):
        """Setup modern ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure treeview for clean table appearance
        style.configure(
            "Polished.Treeview",
            background=self.colors['bg_secondary'],
            foreground=self.colors['text_primary'],
            fieldbackground=self.colors['bg_secondary'],
            borderwidth=0,
            relief='flat',
            rowheight=44,  # Taller rows for better readability
            font=self.fonts['body_md'],
            highlightthickness=0
        )
        
        style.configure(
            "Polished.Treeview.Heading",
            background=self.colors['bg_tertiary'],
            foreground=self.colors['text_secondary'],
            font=self.fonts['body_md'],
            borderwidth=0,
            relief='flat',
            padding=(20, 16),
            anchor='w'
        )
        
        # Enhanced selection and hover states
        style.map(
            "Polished.Treeview",
            background=[('selected', self.colors['accent_light']), ('!selected', self.colors['bg_secondary'])],
            foreground=[('selected', self.colors['text_primary'])]
        )
        
        # Configure selection style
        style.configure(
            "Polished.Treeview",
            selectbackground=self.colors['accent_light'],
            selectforeground=self.colors['text_primary']
        )
        
        # Modern button styles
        style.configure(
            "Polished.TButton",
            font=self.fonts['body_md'],
            borderwidth=0,
            focuscolor='none',
            padding=(16, 8)
        )
        
        # Entry styles
        style.configure(
            "Polished.TEntry",
            font=self.fonts['body_md'],
            borderwidth=1,
            relief='solid',
            padding=(12, 8)
        )
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"+{x}+{y}")
    
    def create_interface(self):
        """Create the main interface"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Header
        self.create_header(main_container)
        
        # Content area with sidebar and main
        content_area = tk.Frame(main_container, bg=self.colors['bg_primary'])
        content_area.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        self.create_sidebar(content_area)
        
        # Main content
        self.create_main_content(content_area)
        
        # Footer
        self.create_footer(main_container)
    
    def create_header(self, parent):
        """Create polished header"""
        header = tk.Frame(
            parent, 
            bg=self.colors['bg_secondary'],
            height=80
        )
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Add elegant bottom shadow/border
        shadow = tk.Frame(header, bg=self.colors['shadow_light'], height=2)
        shadow.pack(side=tk.BOTTOM, fill=tk.X)
        
        border = tk.Frame(header, bg=self.colors['border'], height=1)
        border.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Header content
        header_content = tk.Frame(header, bg=self.colors['bg_secondary'])
        header_content.pack(fill=tk.BOTH, expand=True, padx=32, pady=20)
        
        # Title and project info
        title_frame = tk.Frame(header_content, bg=self.colors['bg_secondary'])
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        title = tk.Label(
            title_frame,
            text="Database Editor",
            font=self.fonts['heading_md'],
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary']
        )
        title.pack(anchor=tk.W)
        
        subtitle = tk.Label(
            title_frame,
            text=f"Project: {self.project_name}",
            font=self.fonts['body_md'],
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary']
        )
        subtitle.pack(anchor=tk.W)
        
        # Action buttons
        actions_frame = tk.Frame(header_content, bg=self.colors['bg_secondary'])
        actions_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # New table button
        new_table_btn = self.create_button(
            actions_frame,
            "New Table",
            self.show_new_table_dialog,
            style='primary'
        )
        new_table_btn.pack(side=tk.RIGHT, padx=(12, 0))
        
        # Refresh button
        refresh_btn = self.create_button(
            actions_frame,
            "Refresh",
            self.refresh_tables,
            style='secondary'
        )
        refresh_btn.pack(side=tk.RIGHT)
    
    def create_sidebar(self, parent):
        """Create polished sidebar"""
        sidebar = tk.Frame(
            parent,
            bg=self.colors['bg_secondary'],
            width=280
        )
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Elegant sidebar border with shadow
        shadow = tk.Frame(sidebar, bg=self.colors['shadow_light'], width=2)
        shadow.pack(side=tk.RIGHT, fill=tk.Y)
        
        border = tk.Frame(sidebar, bg=self.colors['border'], width=1)
        border.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Sidebar content
        sidebar_content = tk.Frame(sidebar, bg=self.colors['bg_secondary'])
        sidebar_content.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)
        
        # Tables header
        tables_header = tk.Label(
            sidebar_content,
            text="Tables",
            font=self.fonts['heading_sm'],
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary']
        )
        tables_header.pack(anchor=tk.W, pady=(0, 16))
        
        # Tables list frame
        tables_frame = tk.Frame(sidebar_content, bg=self.colors['bg_secondary'])
        tables_frame.pack(fill=tk.BOTH, expand=True)
        
        # Enhanced listbox styling
        self.tables_listbox = tk.Listbox(
            tables_frame,
            font=self.fonts['body_md'],
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            selectbackground=self.colors['accent_light'],
            selectforeground=self.colors['text_primary'],
            borderwidth=0,
            highlightthickness=0,
            activestyle='none',
            cursor='hand2',
            relief='flat'
        )
        self.tables_listbox.pack(fill=tk.BOTH, expand=True)
        self.tables_listbox.bind('<<ListboxSelect>>', self.on_table_select)
        self.tables_listbox.bind('<Button-1>', self.on_table_click)
    
    def create_main_content(self, parent):
        """Create polished main content area"""
        self.main_area = tk.Frame(parent, bg=self.colors['bg_primary'])
        self.main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Welcome screen
        self.create_welcome_screen()
    
    def create_welcome_screen(self):
        """Create welcome screen"""
        welcome_frame = tk.Frame(self.main_area, bg=self.colors['bg_primary'])
        welcome_frame.pack(fill=tk.BOTH, expand=True, padx=48, pady=48)
        
        # Welcome card
        welcome_card = tk.Frame(
            welcome_frame,
            bg=self.colors['bg_secondary'],
            relief='flat',
            bd=0
        )
        welcome_card.pack(expand=True, fill=tk.BOTH)
        
        # Add elegant shadow and border effects
        shadow_frame = tk.Frame(welcome_card, bg=self.colors['shadow_light'], height=2)
        shadow_frame.pack(fill=tk.X)
        
        border_frame = tk.Frame(welcome_card, bg=self.colors['border'], height=1)
        border_frame.pack(fill=tk.X)
        
        # Welcome content
        welcome_content = tk.Frame(welcome_card, bg=self.colors['bg_secondary'])
        welcome_content.pack(expand=True, padx=64, pady=64)
        
        # Icon
        icon_label = tk.Label(
            welcome_content,
            text="🗄️",
            font=('Arial', 48),
            bg=self.colors['bg_secondary']
        )
        icon_label.pack(pady=(0, 24))
        
        # Welcome text
        welcome_title = tk.Label(
            welcome_content,
            text="Select a table to get started",
            font=self.fonts['heading_md'],
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary']
        )
        welcome_title.pack(pady=(0, 12))
        
        welcome_desc = tk.Label(
            welcome_content,
            text="Choose a table from the sidebar to view and edit its data,\nor create a new table to get started.",
            font=self.fonts['body_lg'],
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary'],
            justify=tk.CENTER
        )
        welcome_desc.pack()
        
        self.welcome_frame = welcome_frame
    
    def create_table_view(self, table_name):
        """Create polished table view"""
        # Clear main area
        for widget in self.main_area.winfo_children():
            widget.destroy()
        
        # Table container
        table_container = tk.Frame(self.main_area, bg=self.colors['bg_primary'])
        table_container.pack(fill=tk.BOTH, expand=True, padx=32, pady=32)
        
        # Table header
        table_header = tk.Frame(table_container, bg=self.colors['bg_primary'])
        table_header.pack(fill=tk.X, pady=(0, 24))
        
        # Table title and stats
        title_frame = tk.Frame(table_header, bg=self.colors['bg_primary'])
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        table_title = tk.Label(
            title_frame,
            text=table_name.replace('_', ' ').title(),
            font=self.fonts['heading_md'],
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary']
        )
        table_title.pack(anchor=tk.W)
        
        # Row count
        self.row_count_label = tk.Label(
            title_frame,
            text="",
            font=self.fonts['body_md'],
            bg=self.colors['bg_primary'],
            fg=self.colors['text_secondary']
        )
        self.row_count_label.pack(anchor=tk.W)
        
        # Table actions
        actions_frame = tk.Frame(table_header, bg=self.colors['bg_primary'])
        actions_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Search
        search_frame = tk.Frame(actions_frame, bg=self.colors['bg_primary'])
        search_frame.pack(side=tk.RIGHT, padx=(0, 16))
        
        search_label = tk.Label(
            search_frame,
            text="🔍",
            font=self.fonts['body_lg'],
            bg=self.colors['bg_primary'],
            fg=self.colors['text_secondary']
        )
        search_label.pack(side=tk.LEFT, padx=(0, 8))
        
        self.search_var = tk.StringVar()
        # Enhanced search entry with modern styling
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=self.fonts['body_md'],
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            relief='solid',
            bd=1,
            width=20,
            highlightthickness=2,
            highlightcolor=self.colors['accent'],
            highlightbackground=self.colors['border']
        )
        search_entry.pack(side=tk.LEFT, ipady=8)
        
        # Add subtle rounded corner effect through padding
        search_entry.configure(insertbackground=self.colors['accent'])
        search_entry.bind('<KeyRelease>', lambda e: self.search_table(table_name))
        
        # Action buttons
        delete_table_btn = self.create_button(
            actions_frame,
            "Delete Table",
            lambda: self.delete_table(table_name),
            style='danger'
        )
        delete_table_btn.pack(side=tk.RIGHT, padx=(0, 12))
        
        add_row_btn = self.create_button(
            actions_frame,
            "Add Row",
            lambda: self.show_row_editor(table_name),
            style='primary'
        )
        add_row_btn.pack(side=tk.RIGHT, padx=(0, 12))
        
        # Enhanced table card with shadow
        card_container = tk.Frame(table_container, bg=self.colors['bg_primary'])
        card_container.pack(fill=tk.BOTH, expand=True)
        
        # Shadow layer
        shadow_layer = tk.Frame(
            card_container,
            bg=self.colors['shadow_medium'],
            height=2
        )
        shadow_layer.pack(fill=tk.X, pady=(2, 0))
        
        # Main table card
        table_card = tk.Frame(
            card_container,
            bg=self.colors['bg_secondary'],
            relief='flat',
            bd=0
        )
        table_card.pack(fill=tk.BOTH, expand=True)
        
        # Create polished table
        self.create_polished_table(table_card, table_name)
        
        # Load data
        self.load_table_data(table_name)
    
    def create_polished_table(self, parent, table_name):
        """Create a polished data table"""
        # Table frame with padding
        table_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Treeview
        self.tree = ttk.Treeview(
            table_frame,
            style="Polished.Treeview",
            show='headings'
        )
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events with enhanced interaction
        self.tree.bind('<Double-1>', lambda e: self.edit_selected_row(table_name))
        self.tree.bind('<Button-3>', lambda e: self.show_context_menu(e, table_name))
        self.tree.bind('<Motion>', self.on_tree_motion)
        self.tree.bind('<Leave>', self.on_tree_leave)
    
    def create_button(self, parent, text, command, style='secondary'):
        """Create a polished button"""
        styles = {
            'primary': {
                'bg': self.colors['accent'],
                'fg': 'white',
                'hover_bg': self.colors['accent_hover']
            },
            'secondary': {
                'bg': self.colors['bg_tertiary'],
                'fg': self.colors['text_primary'],
                'hover_bg': self.colors['border']
            },
            'danger': {
                'bg': self.colors['danger'],
                'fg': 'white',
                'hover_bg': '#dc2626'
            },
            'success': {
                'bg': self.colors['success'],
                'fg': 'white',
                'hover_bg': '#059669'
            }
        }
        
        style_config = styles.get(style, styles['secondary'])
        
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=self.fonts['body_md'],
            bg=style_config['bg'],
            fg=style_config['fg'],
            relief='flat',
            bd=0,
            padx=16,
            pady=8,
            cursor='hand2'
        )
        
        # Enhanced hover effects with smooth transitions
        def on_enter(e):
            btn.config(bg=style_config['hover_bg'], relief='flat')
            if style == 'primary':
                btn.config(fg='white')
        
        def on_leave(e):
            btn.config(bg=style_config['bg'], relief='flat')
            if style == 'primary':
                btn.config(fg='white')
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        # Add subtle shadow effect for buttons
        btn.configure(padx=20, pady=10)
        
        return btn
    
    def create_footer(self, parent):
        """Create polished footer"""
        footer = tk.Frame(
            parent,
            bg=self.colors['bg_secondary'],
            height=50
        )
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        # Top border
        border = tk.Frame(footer, bg=self.colors['border'], height=1)
        border.pack(fill=tk.X)
        
        # Footer content
        footer_content = tk.Frame(footer, bg=self.colors['bg_secondary'])
        footer_content.pack(fill=tk.BOTH, expand=True, padx=32, pady=12)
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(
            footer_content,
            textvariable=self.status_var,
            font=self.fonts['body_sm'],
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary']
        )
        status_label.pack(side=tk.LEFT)
        
        # Database info
        db_info = tk.Label(
            footer_content,
            text=f"Database: {os.path.basename(self.db_path)}",
            font=self.fonts['body_sm'],
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_muted']
        )
        db_info.pack(side=tk.RIGHT)
    
    def refresh_tables(self):
        """Refresh table list"""
        self.tables_listbox.delete(0, tk.END)
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        tables = cursor.fetchall()
        
        for table in tables:
            self.tables_listbox.insert(tk.END, table[0])
        
        self.status_var.set(f"Found {len(tables)} tables")
    
    def on_table_click(self, event):
        """Handle table click with visual feedback"""
        # Add visual feedback for table selection
        index = self.tables_listbox.nearest(event.y)
        if index >= 0:
            self.tables_listbox.selection_clear(0, tk.END)
            self.tables_listbox.selection_set(index)
            self.tables_listbox.activate(index)
    
    def on_tree_motion(self, event):
        """Handle mouse motion over tree for hover effects"""
        item = self.tree.identify_row(event.y)
        if item and item != getattr(self, '_last_hovered_item', None):
            # Clear previous hover
            if hasattr(self, '_last_hovered_item') and self._last_hovered_item:
                self.tree.set(self._last_hovered_item, '#0', '')
            self._last_hovered_item = item
    
    def on_tree_leave(self, event):
        """Handle mouse leaving tree"""
        if hasattr(self, '_last_hovered_item') and self._last_hovered_item:
            self.tree.set(self._last_hovered_item, '#0', '')
            self._last_hovered_item = None
    
    def on_table_select(self, event):
        """Handle table selection"""
        selection = self.tables_listbox.curselection()
        if selection:
            table_name = self.tables_listbox.get(selection[0])
            self.current_table = table_name
            self.create_table_view(table_name)
    
    def load_table_data(self, table_name):
        """Load and display table data"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        cursor = self.conn.cursor()
        
        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        col_names = [col[1] for col in columns]
        
        # Configure columns with proper widths
        self.tree['columns'] = col_names
        
        for col_name in col_names:
            display_name = col_name.replace('_', ' ').title()
            self.tree.heading(col_name, text=display_name, anchor='w')
            
            # Set intelligent column widths
            if col_name == 'id':
                width = 80
            elif 'date' in col_name or 'time' in col_name:
                width = 150
            elif col_name in ['name', 'title']:
                width = 200
            elif 'description' in col_name or 'content' in col_name or 'notes' in col_name:
                width = 300
            else:
                width = 150
            
            self.tree.column(col_name, width=width, minwidth=80, anchor='w')
        
        # Load data
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        self.current_data = rows
        
        # Insert data with alternating row colors
        for i, row in enumerate(rows):
            # Format data for display
            display_row = []
            for cell in row:
                if cell is None:
                    display_row.append("")
                elif isinstance(cell, str) and len(cell) > 50:
                    display_row.append(cell[:47] + "...")
                else:
                    display_row.append(str(cell))
            
            tags = ('evenrow',) if i % 2 == 0 else ('oddrow',)
            self.tree.insert('', tk.END, values=display_row, tags=tags)
        
        # Configure enhanced row colors with subtle striping
        self.tree.tag_configure('evenrow', background=self.colors['bg_secondary'])
        self.tree.tag_configure('oddrow', background=self.colors['bg_primary'])
        
        # Add hover effect styling
        self.tree.tag_configure('hover', background=self.colors['bg_hover'])
        
        # Update row count
        self.row_count_label.config(text=f"{len(rows)} rows")
        self.status_var.set(f"Loaded {len(rows)} rows from {table_name}")
    
    def search_table(self, table_name):
        """Search table data"""
        search_term = self.search_var.get().strip().lower()
        
        if not search_term:
            self.load_table_data(table_name)
            return
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filter current data
        filtered_rows = []
        for row in self.current_data:
            row_text = ' '.join(str(cell or '') for cell in row).lower()
            if search_term in row_text:
                filtered_rows.append(row)
        
        # Display filtered data
        for i, row in enumerate(filtered_rows):
            display_row = []
            for cell in row:
                if cell is None:
                    display_row.append("")
                elif isinstance(cell, str) and len(cell) > 50:
                    display_row.append(cell[:47] + "...")
                else:
                    display_row.append(str(cell))
            
            tags = ('evenrow',) if i % 2 == 0 else ('oddrow',)
            self.tree.insert('', tk.END, values=display_row, tags=tags)
        
        self.status_var.set(f"Found {len(filtered_rows)} matching rows")
    
    def show_new_table_dialog(self):
        """Show new table creation dialog"""
        dialog = NewTableDialog(self.root, self.conn, self.colors, self.fonts)
        if dialog.result:
            self.refresh_tables()
            self.status_var.set(f"Created table: {dialog.result}")
    
    def show_row_editor(self, table_name, existing_data=None):
        """Show row editor dialog"""
        dialog = RowEditorDialog(self.root, self.conn, table_name, self.colors, self.fonts, existing_data)
        if dialog.result:
            self.load_table_data(table_name)
            action = "updated" if existing_data else "created"
            self.status_var.set(f"Row {action} successfully")
    
    def edit_selected_row(self, table_name):
        """Edit the selected row"""
        selection = self.tree.selection()
        if not selection:
            return
        
        # Get the row index
        item = self.tree.item(selection[0])
        row_values = item['values']
        
        # Find the actual row data
        for row in self.current_data:
            if str(row[0]) == str(row_values[0]):  # Match by ID
                self.show_row_editor(table_name, row)
                break
    
    def show_context_menu(self, event, table_name):
        """Show context menu for table rows"""
        # Select the item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            # Create context menu
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(
                label="Edit Row",
                command=lambda: self.edit_selected_row(table_name)
            )
            context_menu.add_command(
                label="Delete Row",
                command=lambda: self.delete_selected_row(table_name)
            )
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    
    def delete_selected_row(self, table_name):
        """Delete the selected row"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a row to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this row?"):
            item = self.tree.item(selection[0])
            row_id = item['values'][0]
            
            cursor = self.conn.cursor()
            cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (row_id,))
            self.conn.commit()
            
            self.load_table_data(table_name)
            self.status_var.set("Row deleted successfully")
    
    def delete_table(self, table_name):
        """Delete entire table"""
        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the table '{table_name}'?\n\nThis action cannot be undone."
        ):
            cursor = self.conn.cursor()
            cursor.execute(f"DROP TABLE {table_name}")
            self.conn.commit()
            
            self.refresh_tables()
            
            # Return to welcome screen
            for widget in self.main_area.winfo_children():
                widget.destroy()
            self.create_welcome_screen()
            
            self.status_var.set(f"Table '{table_name}' deleted")


class NewTableDialog:
    """Polished dialog for creating new tables"""
    
    def __init__(self, parent, conn, colors, fonts):
        self.conn = conn
        self.colors = colors
        self.fonts = fonts
        self.result = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Table")
        self.dialog.geometry("700x600")
        self.dialog.configure(bg=colors['bg_primary'])
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.center_dialog(parent)
        
        self.setup_ui()
    
    def center_dialog(self, parent):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup the UI"""
        # Main container
        main_container = tk.Frame(self.dialog, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=32, pady=32)
        
        # Header
        header = tk.Label(
            main_container,
            text="Create New Table",
            font=self.fonts['heading_md'],
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary']
        )
        header.pack(anchor=tk.W, pady=(0, 24))
        
        # Form card
        form_card = tk.Frame(
            main_container,
            bg=self.colors['bg_secondary'],
            relief='solid',
            bd=1
        )
        form_card.pack(fill=tk.BOTH, expand=True)
        
        # Form content
        form_content = tk.Frame(form_card, bg=self.colors['bg_secondary'])
        form_content.pack(fill=tk.BOTH, expand=True, padx=32, pady=32)
        
        # Table name
        name_label = tk.Label(
            form_content,
            text="Table Name",
            font=self.fonts['heading_sm'],
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary']
        )
        name_label.pack(anchor=tk.W, pady=(0, 8))
        
        self.name_var = tk.StringVar()
        name_entry = tk.Entry(
            form_content,
            textvariable=self.name_var,
            font=self.fonts['body_lg'],
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary'],
            relief='solid',
            bd=1,
            highlightthickness=2,
            highlightcolor=self.colors['accent'],
            highlightbackground=self.colors['border'],
            insertbackground=self.colors['accent']
        )
        name_entry.pack(fill=tk.X, pady=(0, 24), ipady=12)
        
        # Columns section
        columns_label = tk.Label(
            form_content,
            text="Columns",
            font=self.fonts['heading_sm'],
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary']
        )
        columns_label.pack(anchor=tk.W, pady=(0, 12))
        
        # Columns container with scrolling
        columns_container = tk.Frame(form_content, bg=self.colors['bg_secondary'])
        columns_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for scrolling
        canvas = tk.Canvas(columns_container, bg=self.colors['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(columns_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Column entries
        self.column_entries = []
        
        # Add default columns
        self.add_column_field("id", "INTEGER PRIMARY KEY AUTOINCREMENT")
        self.add_column_field("name", "TEXT NOT NULL")
        self.add_column_field("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        
        # Add column button
        add_col_frame = tk.Frame(form_content, bg=self.colors['bg_secondary'])
        add_col_frame.pack(fill=tk.X, pady=(16, 24))
        
        add_col_btn = tk.Button(
            add_col_frame,
            text="+ Add Column",
            command=self.add_column_field,
            font=self.fonts['body_md'],
            bg=self.colors['accent'],
            fg='white',
            relief='flat',
            bd=0,
            padx=16,
            pady=8,
            cursor='hand2'
        )
        add_col_btn.pack()
        
        # Actions
        actions_frame = tk.Frame(form_content, bg=self.colors['bg_secondary'])
        actions_frame.pack(fill=tk.X)
        
        cancel_btn = tk.Button(
            actions_frame,
            text="Cancel",
            command=self.dialog.destroy,
            font=self.fonts['body_md'],
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            relief='flat',
            bd=0,
            padx=24,
            pady=10
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(12, 0))
        
        create_btn = tk.Button(
            actions_frame,
            text="Create Table",
            command=self.create_table,
            font=self.fonts['body_md'],
            bg=self.colors['accent'],
            fg='white',
            relief='flat',
            bd=0,
            padx=24,
            pady=10
        )
        create_btn.pack(side=tk.RIGHT)
    
    def add_column_field(self, name="", type_def="TEXT"):
        """Add column input field"""
        row_frame = tk.Frame(self.scrollable_frame, bg=self.colors['bg_primary'])
        row_frame.pack(fill=tk.X, pady=4)
        
        name_entry = tk.Entry(
            row_frame,
            font=self.fonts['body_md'],
            bg=self.colors['bg_secondary'],
            relief='solid',
            bd=1,
            width=20,
            highlightthickness=1,
            highlightcolor=self.colors['accent'],
            highlightbackground=self.colors['border']
        )
        name_entry.pack(side=tk.LEFT, padx=(0, 12), ipady=6)
        name_entry.insert(0, name)
        
        type_entry = tk.Entry(
            row_frame,
            font=self.fonts['body_md'],
            bg=self.colors['bg_secondary'],
            relief='solid',
            bd=1,
            width=30,
            highlightthickness=1,
            highlightcolor=self.colors['accent'],
            highlightbackground=self.colors['border']
        )
        type_entry.pack(side=tk.LEFT, padx=(0, 12), ipady=6)
        type_entry.insert(0, type_def)
        
        remove_btn = tk.Button(
            row_frame,
            text="×",
            command=lambda: self.remove_column_field(row_frame),
            font=self.fonts['body_md'],
            bg=self.colors['danger'],
            fg='white',
            relief='flat',
            bd=0,
            width=3,
            height=1
        )
        remove_btn.pack(side=tk.LEFT)
        
        self.column_entries.append((name_entry, type_entry, row_frame))
    
    def remove_column_field(self, row_frame):
        """Remove column field"""
        row_frame.destroy()
        self.column_entries = [
            entry for entry in self.column_entries 
            if entry[2] != row_frame
        ]
    
    def create_table(self):
        """Create the table"""
        table_name = self.name_var.get().strip()
        
        if not table_name:
            messagebox.showerror("Error", "Please enter a table name")
            return
        
        # Get column definitions
        columns = []
        for name_entry, type_entry, _ in self.column_entries:
            name = name_entry.get().strip()
            type_def = type_entry.get().strip()
            
            if name and type_def:
                columns.append(f"{name} {type_def}")
        
        if not columns:
            messagebox.showerror("Error", "Please define at least one column")
            return
        
        # Create SQL
        columns_sql = ",\n    ".join(columns)
        create_sql = f"CREATE TABLE {table_name} (\n    {columns_sql}\n)"
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(create_sql)
            self.conn.commit()
            
            self.result = table_name
            messagebox.showinfo("Success", f"Table '{table_name}' created successfully!")
            self.dialog.destroy()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))


class RowEditorDialog:
    """Polished dialog for editing rows"""
    
    def __init__(self, parent, conn, table_name, colors, fonts, existing_data=None):
        self.conn = conn
        self.table_name = table_name
        self.colors = colors
        self.fonts = fonts
        self.existing_data = existing_data
        self.result = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{'Edit' if existing_data else 'Add'} Row - {table_name}")
        self.dialog.geometry("600x700")
        self.dialog.configure(bg=colors['bg_primary'])
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.center_dialog(parent)
        
        self.setup_ui()
    
    def center_dialog(self, parent):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup the UI"""
        # Get table schema
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({self.table_name})")
        self.columns = cursor.fetchall()
        
        # Main container
        main_container = tk.Frame(self.dialog, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=32, pady=32)
        
        # Header
        header = tk.Label(
            main_container,
            text=f"{'Edit' if self.existing_data else 'Add'} Row",
            font=self.fonts['heading_md'],
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary']
        )
        header.pack(anchor=tk.W, pady=(0, 24))
        
        # Form card
        form_card = tk.Frame(
            main_container,
            bg=self.colors['bg_secondary'],
            relief='solid',
            bd=1
        )
        form_card.pack(fill=tk.BOTH, expand=True)
        
        # Scrollable form
        canvas = tk.Canvas(form_card, bg=self.colors['bg_secondary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_card, orient="vertical", command=canvas.yview)
        form_frame = tk.Frame(canvas, bg=self.colors['bg_secondary'])
        
        form_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=form_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=32, pady=32)
        scrollbar.pack(side="right", fill="y", pady=32)
        
        # Form fields
        self.entries = {}
        
        for i, col_info in enumerate(self.columns):
            col_name = col_info[1]
            col_type = col_info[2]
            is_pk = col_info[5] == 1
            
            # Skip auto-increment primary keys
            if is_pk and 'AUTOINCREMENT' in col_type.upper():
                continue
            
            # Field container
            field_frame = tk.Frame(form_frame, bg=self.colors['bg_secondary'])
            field_frame.pack(fill=tk.X, pady=12)
            
            # Label
            label = tk.Label(
                field_frame,
                text=col_name.replace('_', ' ').title(),
                font=self.fonts['heading_sm'],
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary']
            )
            label.pack(anchor=tk.W, pady=(0, 8))
            
            # Input field
            if 'TEXT' in col_type.upper() and any(kw in col_name.lower() for kw in ['description', 'content', 'notes']):
                # Text area
                text_widget = tk.Text(
                    field_frame,
                    height=4,
                    font=self.fonts['body_md'],
                    bg=self.colors['bg_primary'],
                    fg=self.colors['text_primary'],
                    relief='solid',
                    bd=1,
                    wrap=tk.WORD,
                    highlightthickness=2,
                    highlightcolor=self.colors['accent'],
                    highlightbackground=self.colors['border'],
                    insertbackground=self.colors['accent']
                )
                text_widget.pack(fill=tk.X, pady=(0, 8))
                
                if self.existing_data and i < len(self.existing_data):
                    value = self.existing_data[i]
                    if value:
                        text_widget.insert(tk.END, str(value))
                
                self.entries[col_name] = text_widget
            else:
                # Entry field
                entry = tk.Entry(
                    field_frame,
                    font=self.fonts['body_md'],
                    bg=self.colors['bg_primary'],
                    fg=self.colors['text_primary'],
                    relief='solid',
                    bd=1,
                    highlightthickness=2,
                    highlightcolor=self.colors['accent'],
                    highlightbackground=self.colors['border'],
                    insertbackground=self.colors['accent']
                )
                entry.pack(fill=tk.X, pady=(0, 8), ipady=10)
                
                if self.existing_data and i < len(self.existing_data):
                    value = self.existing_data[i]
                    if value:
                        entry.insert(0, str(value))
                
                self.entries[col_name] = entry
        
        # Actions
        actions_frame = tk.Frame(main_container, bg=self.colors['bg_primary'])
        actions_frame.pack(fill=tk.X, pady=(24, 0))
        
        cancel_btn = tk.Button(
            actions_frame,
            text="Cancel",
            command=self.dialog.destroy,
            font=self.fonts['body_md'],
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            relief='flat',
            bd=0,
            padx=24,
            pady=10
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(12, 0))
        
        save_btn = tk.Button(
            actions_frame,
            text="Save",
            command=self.save_row,
            font=self.fonts['body_md'],
            bg=self.colors['accent'],
            fg='white',
            relief='flat',
            bd=0,
            padx=24,
            pady=10
        )
        save_btn.pack(side=tk.RIGHT)
    
    def save_row(self):
        """Save the row"""
        # Get values
        values = {}
        for col_name, widget in self.entries.items():
            if isinstance(widget, tk.Text):
                value = widget.get('1.0', tk.END).strip()
            else:
                value = widget.get().strip()
            values[col_name] = value if value else None
        
        cursor = self.conn.cursor()
        
        try:
            if self.existing_data:
                # Update
                set_clauses = [f"{col} = ?" for col in values.keys()]
                sql = f"UPDATE {self.table_name} SET {', '.join(set_clauses)} WHERE id = ?"
                cursor.execute(sql, list(values.values()) + [self.existing_data[0]])
            else:
                # Insert
                columns = list(values.keys())
                placeholders = ['?' for _ in columns]
                sql = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                cursor.execute(sql, list(values.values()))
            
            self.conn.commit()
            self.result = True
            messagebox.showinfo("Success", "Row saved successfully!")
            self.dialog.destroy()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))


def launch_polished_table_editor(project_path: str):
    """Launch the polished table editor"""
    editor = PolishedTableEditor(project_path)
    editor.launch()


if __name__ == "__main__":
    # Test
    import tempfile
    test_dir = os.path.join(tempfile.gettempdir(), "test_project")
    os.makedirs(test_dir, exist_ok=True)
    launch_polished_table_editor(test_dir)