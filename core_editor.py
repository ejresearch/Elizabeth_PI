"""
Interactive Intake Module for Lizzy - Polished Version
Provides modern GUI components for data entry and management
"""

import os
import csv
import json
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, font
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd


class InteractiveIntake:
    """Polished intake interface with modern GUI components"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.project_name = os.path.basename(project_path)
        self.db_path = os.path.join(project_path, f"{self.project_name}.sqlite")
        self.conn = None
        self.root = None
        self.current_table = "characters"
        self.current_data = []
        self.connect_db()
        
        # Modern color scheme
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
        """Connect to project database"""
        if os.path.exists(self.db_path):
            self.conn = sqlite3.connect(self.db_path)
        else:
            raise FileNotFoundError(f"Database not found: {self.db_path}")
    
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
            rowheight=44,
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
    
    def launch_gui(self):
        """Launch the polished GUI interface"""
        self.root = tk.Tk()
        self.root.title(f"Lizzy Intake - {self.project_name}")
        self.root.geometry("1600x1000")
        self.root.configure(bg=self.colors['bg_primary'])
        self.root.minsize(1200, 800)
        
        # Configure modern fonts and styles
        self.setup_fonts()
        self.setup_styles()
        
        # Create menu bar
        self.create_menu()
        
        # Create modern interface
        self.create_interface()
        
        # Load initial data
        self.refresh_data()
        
        # Center window
        self.center_window()
        
        self.root.mainloop()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"+{x}+{y}")
    
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
    
    def create_interface(self):
        """Create the modern interface"""
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
            text="Lizzy Intake",
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
        
        # Action buttons in header
        actions_frame = tk.Frame(header_content, bg=self.colors['bg_secondary'])
        actions_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add new button
        add_btn = self.create_button(
            actions_frame,
            "Add Row",
            self.add_row,
            style='primary'
        )
        add_btn.pack(side=tk.RIGHT, padx=(12, 0))
        
        # Refresh button
        refresh_btn = self.create_button(
            actions_frame,
            "Refresh",
            self.refresh_data,
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
        
        # Table buttons
        tables_frame = tk.Frame(sidebar_content, bg=self.colors['bg_secondary'])
        tables_frame.pack(fill=tk.X, pady=(0, 24))
        
        tables = [
            ("characters", "Characters"),
            ("story_outline", "Story Outline"),
            ("notes", "Notes")
        ]
        
        for table_name, display_name in tables:
            btn = self.create_table_button(
                tables_frame,
                display_name,
                lambda t=table_name: self.switch_table(t)
            )
            btn.pack(fill=tk.X, pady=2)
        
        # Search section
        search_header = tk.Label(
            sidebar_content,
            text="Search",
            font=self.fonts['heading_sm'],
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary']
        )
        search_header.pack(anchor=tk.W, pady=(16, 8))
        
        # Search entry
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            sidebar_content,
            textvariable=self.search_var,
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
        search_entry.pack(fill=tk.X, pady=(0, 8), ipady=8)
        search_entry.bind('<KeyRelease>', lambda e: self.search_data())
    
    def create_main_content(self, parent):
        """Create main content area"""
        self.main_area = tk.Frame(parent, bg=self.colors['bg_primary'])
        self.main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Will be populated with table view
        self.create_table_view()
    
    def create_table_view(self):
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
            text=self.current_table.replace('_', ' ').title(),
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
        
        # Action buttons
        delete_btn = self.create_button(
            actions_frame,
            "Delete Row",
            self.delete_row,
            style='danger'
        )
        delete_btn.pack(side=tk.RIGHT, padx=(0, 12))
        
        edit_btn = self.create_button(
            actions_frame,
            "Edit Row",
            self.edit_row,
            style='secondary'
        )
        edit_btn.pack(side=tk.RIGHT, padx=(0, 12))
        
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
        self.create_polished_table(table_card)
    
    def create_polished_table(self, parent):
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
        
        # Bind events
        self.tree.bind('<Double-1>', lambda e: self.edit_row())
        self.tree.bind('<Button-3>', lambda e: self.show_context_menu(e))
    
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
            padx=20,
            pady=10,
            cursor='hand2'
        )
        
        # Enhanced hover effects
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
        
        return btn
    
    def create_table_button(self, parent, text, command):
        """Create a table selection button"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=self.fonts['body_md'],
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            relief='flat',
            bd=0,
            padx=16,
            pady=8,
            cursor='hand2',
            anchor='w'
        )
        
        def on_enter(e):
            btn.config(bg=self.colors['bg_tertiary'])
        
        def on_leave(e):
            btn.config(bg=self.colors['bg_secondary'])
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
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
    
    def show_context_menu(self, event):
        """Show context menu for table rows"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            # Create context menu
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(
                label="Edit Row",
                command=self.edit_row
            )
            context_menu.add_command(
                label="Delete Row",
                command=self.delete_row
            )
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    
    def switch_table(self, table_name: str):
        """Switch to viewing a different table"""
        self.current_table = table_name
        self.create_table_view()
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh the data display"""
        if not self.current_table:
            self.current_table = "characters"
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        cursor = self.conn.cursor()
        
        # Get column info
        cursor.execute(f"PRAGMA table_info({self.current_table})")
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
        cursor.execute(f"SELECT * FROM {self.current_table}")
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
        
        # Update row count
        if hasattr(self, 'row_count_label'):
            self.row_count_label.config(text=f"{len(rows)} rows")
        
        self.status_var.set(f"Loaded {len(rows)} rows from {self.current_table}")
    
    def search_data(self):
        """Search and filter displayed data"""
        search_term = self.search_var.get().strip().lower()
        
        if not search_term:
            self.refresh_data()
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
    
    def add_row(self):
        """Add a new row to the current table"""
        dialog = DataEntryDialog(self.root, self.conn, self.current_table, self.colors, self.fonts)
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
        row_values = item['values']
        
        # Find the actual row data
        for row in self.current_data:
            if str(row[0]) == str(row_values[0]):  # Match by ID
                dialog = DataEntryDialog(self.root, self.conn, self.current_table, self.colors, self.fonts, row)
                if dialog.result:
                    self.refresh_data()
                    self.status_var.set("Row updated successfully")
                break
    
    def delete_row(self):
        """Delete selected row"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a row to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this row?"):
            item = self.tree.item(selection[0])
            row_id = item['values'][0]
            
            cursor = self.conn.cursor()
            cursor.execute(f"DELETE FROM {self.current_table} WHERE id = ?", (row_id,))
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
        dialog = DocumentImportDialog(self.root, self.project_path, self.colors, self.fonts)
        if dialog.result:
            self.status_var.set("Documents imported successfully")
    
    def launch_chat(self):
        """Launch chat interface for data"""
        ChatInterface(self.root, self.conn, self.current_table, self.colors, self.fonts)
    
    def visualize_data(self):
        """Visualize data relationships"""
        DataVisualizer(self.root, self.conn, self.colors, self.fonts)


class DataEntryDialog:
    """Polished dialog for adding/editing data rows"""
    
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
            command=self.save_data,
            font=self.fonts['body_md'],
            bg=self.colors['accent'],
            fg='white',
            relief='flat',
            bd=0,
            padx=24,
            pady=10
        )
        save_btn.pack(side=tk.RIGHT)
    
    def save_data(self):
        """Save the entered data"""
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


class DocumentImportDialog:
    """Polished dialog for importing documents to LightRAG buckets"""
    
    def __init__(self, parent, project_path, colors, fonts):
        self.project_path = project_path
        self.colors = colors
        self.fonts = fonts
        self.result = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Import Documents")
        self.dialog.geometry("700x600")
        self.dialog.configure(bg=colors['bg_primary'])
        
        # Create UI elements using modern styling
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI with modern styling"""
        # Main container
        main_container = tk.Frame(self.dialog, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=32, pady=32)
        
        # Header
        header = tk.Label(
            main_container,
            text="Import Documents",
            font=self.fonts['heading_md'],
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary']
        )
        header.pack(anchor=tk.W, pady=(0, 24))
        
        # Form fields
        # Bucket selection
        bucket_label = tk.Label(
            main_container,
            text="Select Bucket:",
            font=self.fonts['heading_sm'],
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary']
        )
        bucket_label.pack(anchor=tk.W, pady=(0, 8))
        
        self.bucket_var = tk.StringVar()
        bucket_combo = ttk.Combobox(main_container, textvariable=self.bucket_var,
                                    values=["scripts", "books", "plays", "examples", "reference"])
        bucket_combo.pack(fill=tk.X, pady=(0, 24))
        bucket_combo.set("scripts")
        
        # Document content
        content_label = tk.Label(
            main_container,
            text="Document Content:",
            font=self.fonts['heading_sm'],
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary']
        )
        content_label.pack(anchor=tk.W, pady=(0, 8))
        
        self.text_widget = tk.Text(
            main_container,
            height=15,
            font=self.fonts['body_md'],
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            relief='solid',
            bd=1,
            wrap=tk.WORD
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 16))
        
        # Metadata fields
        meta_frame = tk.Frame(main_container, bg=self.colors['bg_primary'])
        meta_frame.pack(fill=tk.X, pady=(0, 24))
        
        # Title
        title_label = tk.Label(meta_frame, text="Title:", font=self.fonts['body_md'],
                              bg=self.colors['bg_primary'], fg=self.colors['text_primary'])
        title_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 12))
        
        self.title_entry = tk.Entry(meta_frame, font=self.fonts['body_md'],
                                   bg=self.colors['bg_secondary'], width=30)
        self.title_entry.grid(row=0, column=1, sticky=tk.W)
        
        # Tags
        tags_label = tk.Label(meta_frame, text="Tags:", font=self.fonts['body_md'],
                             bg=self.colors['bg_primary'], fg=self.colors['text_primary'])
        tags_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 12), pady=(8, 0))
        
        self.tags_entry = tk.Entry(meta_frame, font=self.fonts['body_md'],
                                  bg=self.colors['bg_secondary'], width=30)
        self.tags_entry.grid(row=1, column=1, sticky=tk.W, pady=(8, 0))
        
        # Buttons
        button_frame = tk.Frame(main_container, bg=self.colors['bg_primary'])
        button_frame.pack(fill=tk.X)
        
        # Import file button
        import_btn = tk.Button(
            button_frame,
            text="Import File",
            command=self.import_file,
            font=self.fonts['body_md'],
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            relief='flat',
            bd=0,
            padx=16,
            pady=8
        )
        import_btn.pack(side=tk.LEFT)
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy,
            font=self.fonts['body_md'],
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            relief='flat',
            bd=0,
            padx=16,
            pady=8
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(12, 0))
        
        # Save button
        save_btn = tk.Button(
            button_frame,
            text="Save Document",
            command=self.save_document,
            font=self.fonts['body_md'],
            bg=self.colors['accent'],
            fg='white',
            relief='flat',
            bd=0,
            padx=16,
            pady=8
        )
        save_btn.pack(side=tk.RIGHT)
    
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
        
        # Save document
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
    """Polished chat interface for interacting with data"""
    
    def __init__(self, parent, conn, table_name, colors, fonts):
        self.conn = conn
        self.table_name = table_name
        self.colors = colors
        self.fonts = fonts
        
        # Create chat window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Chat with {table_name}")
        self.window.geometry("700x600")
        self.window.configure(bg=colors['bg_primary'])
        
        self.setup_ui()
        
        # Initial message
        self.add_message("System", f"Chat interface for {table_name} table. Ask questions about your data!")
    
    def setup_ui(self):
        """Setup the UI with modern styling"""
        # Main container
        main_container = tk.Frame(self.window, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)
        
        # Chat display
        self.chat_display = tk.Text(
            main_container,
            height=25,
            font=self.fonts['body_md'],
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            relief='solid',
            bd=1,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 16))
        
        # Input frame
        input_frame = tk.Frame(main_container, bg=self.colors['bg_primary'])
        input_frame.pack(fill=tk.X)
        
        self.input_entry = tk.Entry(
            input_frame,
            font=self.fonts['body_md'],
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            relief='solid',
            bd=1
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12), ipady=8)
        self.input_entry.bind('<Return>', lambda e: self.send_message())
        
        send_btn = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            font=self.fonts['body_md'],
            bg=self.colors['accent'],
            fg='white',
            relief='flat',
            bd=0,
            padx=16,
            pady=8
        )
        send_btn.pack(side=tk.RIGHT)
    
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
    """Polished visualizer for data relationships"""
    
    def __init__(self, parent, conn, colors, fonts):
        self.conn = conn
        self.colors = colors
        self.fonts = fonts
        
        # Create visualization window
        self.window = tk.Toplevel(parent)
        self.window.title("Data Relationships")
        self.window.geometry("900x700")
        self.window.configure(bg=colors['bg_primary'])
        
        # Canvas for visualization
        canvas_frame = tk.Frame(self.window, bg=colors['bg_secondary'], relief='solid', bd=1)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)
        
        self.canvas = tk.Canvas(canvas_frame, bg=colors['bg_secondary'])
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Draw relationships
        self.visualize_relationships()
    
    def visualize_relationships(self):
        """Create visual representation of data relationships"""
        # Get character and scene data
        cursor = self.conn.cursor()
        
        try:
            # Get characters
            cursor.execute("SELECT name FROM characters")
            characters = [row[0] for row in cursor.fetchall()]
            
            # Get scenes
            cursor.execute("SELECT act, scene, key_characters FROM story_outline")
            scenes = cursor.fetchall()
            
            # Draw characters as nodes
            char_positions = {}
            y = 80
            for i, char in enumerate(characters):
                x = 120 + (i * 180)
                self.canvas.create_oval(x-35, y-35, x+35, y+35, fill=self.colors['accent_light'], outline=self.colors['accent'])
                self.canvas.create_text(x, y, text=char, font=self.fonts['body_md'], fill=self.colors['text_primary'])
                char_positions[char] = (x, y)
            
            # Draw scenes and connections
            scene_y = 250
            for act, scene, chars in scenes:
                scene_x = 120 + ((act-1) * 220) + (scene * 60)
                
                # Draw scene box
                self.canvas.create_rectangle(scene_x-45, scene_y-25, scene_x+45, scene_y+25, 
                                           fill=self.colors['success_light'], outline=self.colors['success'])
                self.canvas.create_text(scene_x, scene_y, text=f"A{act}S{scene}", 
                                      font=self.fonts['body_md'], fill=self.colors['text_primary'])
                
                # Draw connections to characters
                if chars:
                    for char_name in chars.split(','):
                        char_name = char_name.strip()
                        if char_name in char_positions:
                            char_x, char_y = char_positions[char_name]
                            self.canvas.create_line(char_x, char_y+35, scene_x, scene_y-25, 
                                                   fill=self.colors['text_muted'], width=2)
        
        except sqlite3.Error:
            # If tables don't exist, show message
            self.canvas.create_text(400, 300, text="No relationship data available", 
                                  font=self.fonts['heading_sm'], fill=self.colors['text_secondary'])


def launch_intake_gui(project_path: str):
    """Launch the polished intake GUI for a project"""
    intake = InteractiveIntake(project_path)
    intake.launch_gui()


if __name__ == "__main__":
    # Demo usage
    import sys
    
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "projects/Alpha"
    
    if os.path.exists(project_path):
        launch_intake_gui(project_path)
    else:
        print(f"Project not found: {project_path}")