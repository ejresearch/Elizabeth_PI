"""
Main Orchestrator for the Enhanced Lizzy System
Ties together all modules and provides the unified interface
"""

import os
import sys
import asyncio
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import all Lizzy modules
from lizzy_templates import TemplateManager, PromptInspector
from lizzy_lightrag_manager import LightRAGManager, BucketInterface
from lizzy_intake_interactive import launch_intake_gui
from lizzy_transparent_brainstorm import TransparentBrainstormer, BrainstormConsole
from lizzy_transparent_write import TransparentWriter, WriteConsole
from lizzy_export_system import LizzyExporter


class LizzyOrchestrator:
    """Main orchestrator that coordinates all Lizzy components"""
    
    def __init__(self, project_path: str = None):
        self.project_path = project_path
        self.project_name = os.path.basename(project_path) if project_path else None
        
        # Initialize all managers
        self.template_manager = None
        self.lightrag_manager = None
        self.brainstormer = None
        self.writer = None
        self.exporter = None
        
        # GUI components
        self.root = None
        self.status_var = None
        self.progress_var = None
        
        # Session tracking
        self.current_session = None
        self.session_log = []
        
        if project_path:
            self.initialize_project(project_path)
    
    def initialize_project(self, project_path: str):
        """Initialize all components for a project"""
        self.project_path = project_path
        self.project_name = os.path.basename(project_path)
        
        print(f"🚀 Initializing Lizzy for project: {self.project_name}")
        
        # Initialize core managers
        self.template_manager = TemplateManager()
        self.lightrag_manager = LightRAGManager()
        self.exporter = LizzyExporter(project_path)
        
        # Initialize processing engines
        self.brainstormer = TransparentBrainstormer(
            project_path, 
            self.template_manager, 
            self.lightrag_manager
        )
        
        self.writer = TransparentWriter(
            project_path, 
            self.template_manager, 
            self.lightrag_manager
        )
        
        print("✅ All components initialized")
    
    def launch_gui(self):
        """Launch the main GUI interface"""
        self.root = tk.Tk()
        self.root.title(f"Lizzy Framework - {self.project_name or 'No Project'}")
        self.root.geometry("1400x900")
        
        # Set up the interface
        self.create_menu()
        self.create_main_interface()
        
        # Start the GUI loop
        self.root.mainloop()
    
    def create_menu(self):
        """Create the main menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Project", command=self.open_project)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_separator()
        file_menu.add_command(label="Export Complete", command=lambda: self.export_project("complete"))
        file_menu.add_command(label="Export Screenplay", command=lambda: self.export_project("screenplay"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Data Intake", command=self.launch_intake)
        tools_menu.add_command(label="Template Editor", command=self.launch_template_editor)
        tools_menu.add_command(label="Bucket Manager", command=self.launch_bucket_manager)
        
        # Workflow menu
        workflow_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Workflow", menu=workflow_menu)
        workflow_menu.add_command(label="Brainstorm All Scenes", command=self.launch_brainstorm_workflow)
        workflow_menu.add_command(label="Write All Scenes", command=self.launch_write_workflow)
        workflow_menu.add_command(label="Full Workflow", command=self.launch_full_workflow)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Session Log", command=self.show_session_log)
        view_menu.add_command(label="Project Overview", command=self.show_project_overview)
        view_menu.add_command(label="Statistics", command=self.show_statistics)
    
    def create_main_interface(self):
        """Create the main interface layout"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Dashboard tab
        self.create_dashboard_tab(notebook)
        
        # Templates tab
        self.create_templates_tab(notebook)
        
        # Buckets tab
        self.create_buckets_tab(notebook)
        
        # Sessions tab
        self.create_sessions_tab(notebook)
        
        # Export tab
        self.create_export_tab(notebook)
        
        # Status bar
        self.create_status_bar()
    
    def create_dashboard_tab(self, notebook):
        """Create the main dashboard tab"""
        dashboard_frame = ttk.Frame(notebook)
        notebook.add(dashboard_frame, text="Dashboard")
        
        # Project info section
        info_frame = ttk.LabelFrame(dashboard_frame, text="Project Information", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        if self.project_name:
            ttk.Label(info_frame, text=f"Project: {self.project_name}").pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"Path: {self.project_path}").pack(anchor=tk.W)
        else:
            ttk.Label(info_frame, text="No project loaded").pack(anchor=tk.W)
            ttk.Button(info_frame, text="Open Project", command=self.open_project).pack(pady=5)
        
        # Quick actions section
        actions_frame = ttk.LabelFrame(dashboard_frame, text="Quick Actions", padding="10")
        actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        button_frame = ttk.Frame(actions_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Data Intake", 
                  command=self.launch_intake).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Brainstorm", 
                  command=self.launch_brainstorm_workflow).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Write", 
                  command=self.launch_write_workflow).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export", 
                  command=lambda: self.export_project("complete")).pack(side=tk.LEFT, padx=5)\n        \n        # Status section\n        status_frame = ttk.LabelFrame(dashboard_frame, text=\"System Status\", padding=\"10\")\n        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)\n        \n        self.status_text = tk.Text(status_frame, height=15, width=80)\n        scrollbar = ttk.Scrollbar(status_frame, command=self.status_text.yview)\n        self.status_text.config(yscrollcommand=scrollbar.set)\n        \n        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)\n        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)\n        \n        self.log_message(\"Lizzy Framework initialized\")\n        if self.project_name:\n            self.log_message(f\"Project loaded: {self.project_name}\")\n    \n    def create_templates_tab(self, notebook):\n        \"\"\"Create the templates management tab\"\"\"\n        templates_frame = ttk.Frame(notebook)\n        notebook.add(templates_frame, text=\"Templates\")\n        \n        # Template list\n        list_frame = ttk.LabelFrame(templates_frame, text=\"Available Templates\", padding=\"10\")\n        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)\n        \n        # Template tree\n        self.template_tree = ttk.Treeview(list_frame)\n        self.template_tree[\"columns\"] = (\"Type\", \"Active\", \"Description\")\n        self.template_tree.heading(\"#0\", text=\"Name\")\n        self.template_tree.heading(\"Type\", text=\"Type\")\n        self.template_tree.heading(\"Active\", text=\"Active\")\n        self.template_tree.heading(\"Description\", text=\"Description\")\n        \n        self.template_tree.pack(fill=tk.BOTH, expand=True)\n        \n        # Template controls\n        controls_frame = ttk.Frame(templates_frame)\n        controls_frame.pack(fill=tk.X, padx=10, pady=5)\n        \n        ttk.Button(controls_frame, text=\"Refresh\", \n                  command=self.refresh_templates).pack(side=tk.LEFT, padx=5)\n        ttk.Button(controls_frame, text=\"Edit Template\", \n                  command=self.edit_template).pack(side=tk.LEFT, padx=5)\n        ttk.Button(controls_frame, text=\"Preview\", \n                  command=self.preview_template).pack(side=tk.LEFT, padx=5)\n        \n        self.refresh_templates()\n    \n    def create_buckets_tab(self, notebook):\n        \"\"\"Create the buckets management tab\"\"\"\n        buckets_frame = ttk.Frame(notebook)\n        notebook.add(buckets_frame, text=\"Knowledge Buckets\")\n        \n        # Bucket list\n        list_frame = ttk.LabelFrame(buckets_frame, text=\"Knowledge Buckets\", padding=\"10\")\n        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)\n        \n        # Bucket tree\n        self.bucket_tree = ttk.Treeview(list_frame)\n        self.bucket_tree[\"columns\"] = (\"Active\", \"Documents\", \"Entities\", \"Relations\")\n        self.bucket_tree.heading(\"#0\", text=\"Bucket\")\n        self.bucket_tree.heading(\"Active\", text=\"Active\")\n        self.bucket_tree.heading(\"Documents\", text=\"Docs\")\n        self.bucket_tree.heading(\"Entities\", text=\"Entities\")\n        self.bucket_tree.heading(\"Relations\", text=\"Relations\")\n        \n        self.bucket_tree.pack(fill=tk.BOTH, expand=True)\n        \n        # Bucket controls\n        controls_frame = ttk.Frame(buckets_frame)\n        controls_frame.pack(fill=tk.X, padx=10, pady=5)\n        \n        ttk.Button(controls_frame, text=\"Refresh\", \n                  command=self.refresh_buckets).pack(side=tk.LEFT, padx=5)\n        ttk.Button(controls_frame, text=\"Toggle Active\", \n                  command=self.toggle_bucket).pack(side=tk.LEFT, padx=5)\n        ttk.Button(controls_frame, text=\"Add Document\", \n                  command=self.add_document_to_bucket).pack(side=tk.LEFT, padx=5)\n        ttk.Button(controls_frame, text=\"Visualize\", \n                  command=self.visualize_bucket).pack(side=tk.LEFT, padx=5)\n        \n        self.refresh_buckets()\n    \n    def create_sessions_tab(self, notebook):\n        \"\"\"Create the sessions tracking tab\"\"\"\n        sessions_frame = ttk.Frame(notebook)\n        notebook.add(sessions_frame, text=\"Sessions\")\n        \n        # Session list\n        list_frame = ttk.LabelFrame(sessions_frame, text=\"Recent Sessions\", padding=\"10\")\n        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)\n        \n        # Session tree\n        self.session_tree = ttk.Treeview(list_frame)\n        self.session_tree[\"columns\"] = (\"Type\", \"Status\", \"Scenes\", \"Time\")\n        self.session_tree.heading(\"#0\", text=\"Session ID\")\n        self.session_tree.heading(\"Type\", text=\"Type\")\n        self.session_tree.heading(\"Status\", text=\"Status\")\n        self.session_tree.heading(\"Scenes\", text=\"Scenes\")\n        self.session_tree.heading(\"Time\", text=\"Time\")\n        \n        self.session_tree.pack(fill=tk.BOTH, expand=True)\n        \n        # Session controls\n        controls_frame = ttk.Frame(sessions_frame)\n        controls_frame.pack(fill=tk.X, padx=10, pady=5)\n        \n        ttk.Button(controls_frame, text=\"Refresh\", \n                  command=self.refresh_sessions).pack(side=tk.LEFT, padx=5)\n        ttk.Button(controls_frame, text=\"View Details\", \n                  command=self.view_session_details).pack(side=tk.LEFT, padx=5)\n        ttk.Button(controls_frame, text=\"Export Session\", \n                  command=self.export_session).pack(side=tk.LEFT, padx=5)\n        \n        self.refresh_sessions()\n    \n    def create_export_tab(self, notebook):\n        \"\"\"Create the export management tab\"\"\"\n        export_frame = ttk.Frame(notebook)\n        notebook.add(export_frame, text=\"Export\")\n        \n        # Export options\n        options_frame = ttk.LabelFrame(export_frame, text=\"Export Options\", padding=\"10\")\n        options_frame.pack(fill=tk.X, padx=10, pady=5)\n        \n        # Export type\n        ttk.Label(options_frame, text=\"Export Type:\").grid(row=0, column=0, sticky=tk.W, padx=5)\n        self.export_type_var = tk.StringVar(value=\"complete\")\n        export_combo = ttk.Combobox(options_frame, textvariable=self.export_type_var,\n                                   values=[\"complete\", \"screenplay\", \"data\", \"sessions\", \"analysis\"])\n        export_combo.grid(row=0, column=1, padx=5, sticky=tk.W)\n        \n        # Export formats\n        ttk.Label(options_frame, text=\"Formats:\").grid(row=1, column=0, sticky=tk.W, padx=5)\n        \n        formats_frame = ttk.Frame(options_frame)\n        formats_frame.grid(row=1, column=1, sticky=tk.W, padx=5)\n        \n        self.format_vars = {\n            \"json\": tk.BooleanVar(value=True),\n            \"txt\": tk.BooleanVar(value=True),\n            \"html\": tk.BooleanVar(value=True),\n            \"fountain\": tk.BooleanVar(value=False),\n            \"csv\": tk.BooleanVar(value=False),\n            \"markdown\": tk.BooleanVar(value=False)\n        }\n        \n        for i, (format_name, var) in enumerate(self.format_vars.items()):\n            ttk.Checkbutton(formats_frame, text=format_name, variable=var).grid(\n                row=i//3, column=i%3, sticky=tk.W, padx=5\n            )\n        \n        # Export button\n        ttk.Button(options_frame, text=\"Create Export Package\", \n                  command=self.create_export_package).grid(row=2, column=0, columnspan=2, pady=10)\n        \n        # Export history\n        history_frame = ttk.LabelFrame(export_frame, text=\"Export History\", padding=\"10\")\n        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)\n        \n        self.export_tree = ttk.Treeview(history_frame)\n        self.export_tree[\"columns\"] = (\"Type\", \"Size\", \"Created\")\n        self.export_tree.heading(\"#0\", text=\"Export\")\n        self.export_tree.heading(\"Type\", text=\"Type\")\n        self.export_tree.heading(\"Size\", text=\"Size\")\n        self.export_tree.heading(\"Created\", text=\"Created\")\n        \n        self.export_tree.pack(fill=tk.BOTH, expand=True)\n    \n    def create_status_bar(self):\n        \"\"\"Create the status bar\"\"\"\n        status_frame = ttk.Frame(self.root)\n        status_frame.pack(fill=tk.X, side=tk.BOTTOM)\n        \n        self.status_var = tk.StringVar(value=\"Ready\")\n        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=5)\n        \n        self.progress_var = tk.IntVar()\n        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var)\n        self.progress_bar.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)\n    \n    # Menu action methods\n    def open_project(self):\n        \"\"\"Open an existing project\"\"\"\n        from tkinter import filedialog\n        \n        project_dir = filedialog.askdirectory(title=\"Select Project Directory\")\n        if project_dir:\n            self.initialize_project(project_dir)\n            self.log_message(f\"Opened project: {self.project_name}\")\n            self.refresh_all_tabs()\n    \n    def new_project(self):\n        \"\"\"Create a new project\"\"\"\n        # This would create a new project structure\n        messagebox.showinfo(\"New Project\", \"New project creation not yet implemented\")\n    \n    def launch_intake(self):\n        \"\"\"Launch the data intake interface\"\"\"\n        if not self.project_path:\n            messagebox.showwarning(\"No Project\", \"Please open a project first\")\n            return\n        \n        self.log_message(\"Launching data intake interface...\")\n        # This would launch the intake GUI in a separate window\n        try:\n            launch_intake_gui(self.project_path)\n        except Exception as e:\n            messagebox.showerror(\"Error\", f\"Failed to launch intake: {e}\")\n    \n    def launch_template_editor(self):\n        \"\"\"Launch the template editor\"\"\"\n        # This would open a template editing interface\n        messagebox.showinfo(\"Template Editor\", \"Template editor not yet implemented\")\n    \n    def launch_bucket_manager(self):\n        \"\"\"Launch the bucket manager\"\"\"\n        if not self.lightrag_manager:\n            messagebox.showwarning(\"No Project\", \"Please open a project first\")\n            return\n        \n        # This would launch the bucket management interface\n        interface = BucketInterface(self.lightrag_manager)\n        interface.manage_buckets_menu()\n    \n    async def launch_brainstorm_workflow(self):\n        \"\"\"Launch the brainstorming workflow\"\"\"\n        if not self.brainstormer:\n            messagebox.showwarning(\"No Project\", \"Please open a project first\")\n            return\n        \n        # Get user preferences\n        dialog = WorkflowDialog(self.root, \"Brainstorm Configuration\")\n        if not dialog.result:\n            return\n        \n        buckets = dialog.selected_buckets\n        guidance = dialog.user_guidance\n        \n        self.log_message(f\"Starting brainstorm workflow with buckets: {', '.join(buckets)}\")\n        \n        try:\n            # Set up console for real-time feedback\n            console = BrainstormConsole(self.brainstormer)\n            \n            # Run brainstorming\n            session_id = await self.brainstormer.brainstorm_all_scenes(buckets, guidance)\n            \n            self.log_message(f\"Brainstorm workflow completed: {session_id}\")\n            self.refresh_sessions()\n            \n        except Exception as e:\n            self.log_message(f\"Brainstorm workflow failed: {e}\")\n            messagebox.showerror(\"Error\", f\"Brainstorming failed: {e}\")\n    \n    async def launch_write_workflow(self):\n        \"\"\"Launch the writing workflow\"\"\"\n        if not self.writer:\n            messagebox.showwarning(\"No Project\", \"Please open a project first\")\n            return\n        \n        # Get user preferences\n        dialog = WorkflowDialog(self.root, \"Write Configuration\")\n        if not dialog.result:\n            return\n        \n        buckets = dialog.selected_buckets\n        guidance = dialog.user_guidance\n        \n        self.log_message(f\"Starting write workflow with buckets: {', '.join(buckets)}\")\n        \n        try:\n            # Set up console for real-time feedback\n            console = WriteConsole(self.writer)\n            \n            # Run writing\n            session_id = await self.writer.write_all_scenes(buckets, guidance)\n            \n            self.log_message(f\"Write workflow completed: {session_id}\")\n            self.refresh_sessions()\n            \n        except Exception as e:\n            self.log_message(f\"Write workflow failed: {e}\")\n            messagebox.showerror(\"Error\", f\"Writing failed: {e}\")\n    \n    async def launch_full_workflow(self):\n        \"\"\"Launch the complete brainstorm + write workflow\"\"\"\n        if not self.brainstormer or not self.writer:\n            messagebox.showwarning(\"No Project\", \"Please open a project first\")\n            return\n        \n        # Get user preferences\n        dialog = WorkflowDialog(self.root, \"Full Workflow Configuration\")\n        if not dialog.result:\n            return\n        \n        buckets = dialog.selected_buckets\n        guidance = dialog.user_guidance\n        \n        self.log_message(\"Starting full workflow: brainstorm + write\")\n        \n        try:\n            # First brainstorm\n            await self.launch_brainstorm_workflow()\n            \n            # Then write\n            await self.launch_write_workflow()\n            \n            self.log_message(\"Full workflow completed successfully\")\n            \n        except Exception as e:\n            self.log_message(f\"Full workflow failed: {e}\")\n            messagebox.showerror(\"Error\", f\"Full workflow failed: {e}\")\n    \n    def export_project(self, export_type: str):\n        \"\"\"Export the project\"\"\"\n        if not self.exporter:\n            messagebox.showwarning(\"No Project\", \"Please open a project first\")\n            return\n        \n        self.log_message(f\"Creating {export_type} export package...\")\n        \n        try:\n            zip_path = self.exporter.create_export_package(\n                export_type=export_type,\n                formats=[\"json\", \"txt\", \"html\"],\n                include_metadata=True\n            )\n            \n            self.log_message(f\"Export created: {zip_path}\")\n            messagebox.showinfo(\"Export Complete\", f\"Export saved to:\\n{zip_path}\")\n            \n        except Exception as e:\n            self.log_message(f\"Export failed: {e}\")\n            messagebox.showerror(\"Error\", f\"Export failed: {e}\")\n    \n    # Helper methods\n    def log_message(self, message: str):\n        \"\"\"Log a message to the status display\"\"\"\n        timestamp = datetime.now().strftime(\"%H:%M:%S\")\n        log_entry = f\"[{timestamp}] {message}\\n\"\n        \n        if hasattr(self, 'status_text'):\n            self.status_text.insert(tk.END, log_entry)\n            self.status_text.see(tk.END)\n        \n        # Also log to console\n        print(log_entry.strip())\n    \n    def refresh_all_tabs(self):\n        \"\"\"Refresh all tab contents\"\"\"\n        self.refresh_templates()\n        self.refresh_buckets()\n        self.refresh_sessions()\n    \n    def refresh_templates(self):\n        \"\"\"Refresh the templates display\"\"\"\n        if not hasattr(self, 'template_tree') or not self.template_manager:\n            return\n        \n        # Clear existing items\n        for item in self.template_tree.get_children():\n            self.template_tree.delete(item)\n        \n        # Add templates\n        for category, templates in self.template_manager.templates.items():\n            category_item = self.template_tree.insert(\"\", tk.END, text=category.title(), \n                                                     values=(\"\", \"\", \"\"))\n            \n            for name, template in templates.items():\n                active = \"✓\" if template.get(\"active\", False) else \"✗\"\n                description = template.get(\"name\", \"\")\n                self.template_tree.insert(category_item, tk.END, text=name,\n                                         values=(category, active, description))\n    \n    def refresh_buckets(self):\n        \"\"\"Refresh the buckets display\"\"\"\n        if not hasattr(self, 'bucket_tree') or not self.lightrag_manager:\n            return\n        \n        # Clear existing items\n        for item in self.bucket_tree.get_children():\n            self.bucket_tree.delete(item)\n        \n        # Add buckets\n        buckets = self.lightrag_manager.get_bucket_list()\n        for bucket in buckets:\n            active = \"✓\" if bucket[\"active\"] else \"✗\"\n            self.bucket_tree.insert(\"\", tk.END, text=bucket[\"name\"],\n                                   values=(active, bucket[\"documents\"], \n                                          bucket[\"entities\"], bucket[\"relationships\"]))\n    \n    def refresh_sessions(self):\n        \"\"\"Refresh the sessions display\"\"\"\n        if not hasattr(self, 'session_tree'):\n            return\n        \n        # Clear existing items\n        for item in self.session_tree.get_children():\n            self.session_tree.delete(item)\n        \n        # Add sessions (this would get real session data)\n        # Placeholder for now\n        pass\n    \n    def edit_template(self):\n        \"\"\"Edit selected template\"\"\"\n        messagebox.showinfo(\"Template Editor\", \"Template editing not yet implemented\")\n    \n    def preview_template(self):\n        \"\"\"Preview selected template\"\"\"\n        messagebox.showinfo(\"Template Preview\", \"Template preview not yet implemented\")\n    \n    def toggle_bucket(self):\n        \"\"\"Toggle selected bucket active state\"\"\"\n        selection = self.bucket_tree.selection()\n        if not selection:\n            messagebox.showwarning(\"No Selection\", \"Please select a bucket\")\n            return\n        \n        item = self.bucket_tree.item(selection[0])\n        bucket_name = item['text']\n        \n        # Toggle bucket\n        current_state = item['values'][0] == \"✓\"\n        new_state = not current_state\n        \n        if self.lightrag_manager.toggle_bucket(bucket_name, new_state):\n            self.refresh_buckets()\n            self.log_message(f\"Toggled bucket {bucket_name}: {'ON' if new_state else 'OFF'}\")\n    \n    def add_document_to_bucket(self):\n        \"\"\"Add document to selected bucket\"\"\"\n        messagebox.showinfo(\"Add Document\", \"Document addition not yet implemented\")\n    \n    def visualize_bucket(self):\n        \"\"\"Visualize selected bucket's knowledge graph\"\"\"\n        selection = self.bucket_tree.selection()\n        if not selection:\n            messagebox.showwarning(\"No Selection\", \"Please select a bucket\")\n            return\n        \n        item = self.bucket_tree.item(selection[0])\n        bucket_name = item['text']\n        \n        try:\n            viz_file = self.lightrag_manager.visualize_knowledge_graph(bucket_name)\n            if viz_file:\n                self.log_message(f\"Knowledge graph visualization saved: {viz_file}\")\n                messagebox.showinfo(\"Visualization\", f\"Graph saved to: {viz_file}\")\n            else:\n                messagebox.showinfo(\"No Data\", \"No graph data available for visualization\")\n        except Exception as e:\n            messagebox.showerror(\"Error\", f\"Visualization failed: {e}\")\n    \n    def view_session_details(self):\n        \"\"\"View details of selected session\"\"\"\n        messagebox.showinfo(\"Session Details\", \"Session details not yet implemented\")\n    \n    def export_session(self):\n        \"\"\"Export selected session\"\"\"\n        messagebox.showinfo(\"Export Session\", \"Session export not yet implemented\")\n    \n    def create_export_package(self):\n        \"\"\"Create export package with selected options\"\"\"\n        export_type = self.export_type_var.get()\n        formats = [name for name, var in self.format_vars.items() if var.get()]\n        \n        if not formats:\n            messagebox.showwarning(\"No Formats\", \"Please select at least one export format\")\n            return\n        \n        self.export_project(export_type)\n    \n    def show_session_log(self):\n        \"\"\"Show the session log\"\"\"\n        messagebox.showinfo(\"Session Log\", \"Session log viewer not yet implemented\")\n    \n    def show_project_overview(self):\n        \"\"\"Show project overview\"\"\"\n        if not self.exporter:\n            messagebox.showwarning(\"No Project\", \"Please open a project first\")\n            return\n        \n        overview = self.exporter.generate_project_overview()\n        \n        # Create overview window\n        overview_window = tk.Toplevel(self.root)\n        overview_window.title(\"Project Overview\")\n        overview_window.geometry(\"600x500\")\n        \n        text_widget = tk.Text(overview_window, wrap=tk.WORD)\n        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)\n        \n        # Format overview\n        overview_text = f\"Project: {overview.get('project_name', 'Unknown')}\\n\\n\"\n        overview_text += f\"Generated: {overview.get('generated_at', 'Unknown')}\\n\\n\"\n        \n        if 'content_summary' in overview:\n            overview_text += \"Content Summary:\\n\"\n            content = overview['content_summary']\n            if 'characters' in content:\n                overview_text += f\"  Characters: {len(content['characters'])}\\n\"\n            if 'structure' in content:\n                structure = content['structure']\n                overview_text += f\"  Acts: {structure.get('acts', 0)}\\n\"\n                overview_text += f\"  Scenes: {structure.get('scenes', 0)}\\n\"\n        \n        if 'statistics' in overview:\n            overview_text += \"\\nStatistics:\\n\"\n            stats = overview['statistics']\n            overview_text += f\"  Total Words: {stats.get('total_words', 0)}\\n\"\n            overview_text += f\"  Avg Words/Scene: {stats.get('average_words_per_scene', 0)}\\n\"\n        \n        text_widget.insert(tk.END, overview_text)\n        text_widget.config(state=tk.DISABLED)\n    \n    def show_statistics(self):\n        \"\"\"Show project statistics\"\"\"\n        messagebox.showinfo(\"Statistics\", \"Statistics viewer not yet implemented\")\n\n\nclass WorkflowDialog:\n    \"\"\"Dialog for configuring workflow parameters\"\"\"\n    \n    def __init__(self, parent, title):\n        self.result = None\n        self.selected_buckets = []\n        self.user_guidance = \"\"\n        \n        # Create dialog\n        self.dialog = tk.Toplevel(parent)\n        self.dialog.title(title)\n        self.dialog.geometry(\"400x300\")\n        \n        # Bucket selection\n        bucket_frame = ttk.LabelFrame(self.dialog, text=\"Select Buckets\", padding=\"10\")\n        bucket_frame.pack(fill=tk.X, padx=10, pady=5)\n        \n        self.bucket_vars = {\n            \"scripts\": tk.BooleanVar(value=True),\n            \"books\": tk.BooleanVar(value=True),\n            \"plays\": tk.BooleanVar(value=False),\n            \"examples\": tk.BooleanVar(value=False),\n            \"reference\": tk.BooleanVar(value=False)\n        }\n        \n        for bucket, var in self.bucket_vars.items():\n            ttk.Checkbutton(bucket_frame, text=bucket.title(), variable=var).pack(anchor=tk.W)\n        \n        # User guidance\n        guidance_frame = ttk.LabelFrame(self.dialog, text=\"User Guidance\", padding=\"10\")\n        guidance_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)\n        \n        self.guidance_text = tk.Text(guidance_frame, height=5)\n        self.guidance_text.pack(fill=tk.BOTH, expand=True)\n        self.guidance_text.insert(tk.END, \"Focus on witty dialogue and authentic emotion\")\n        \n        # Buttons\n        button_frame = ttk.Frame(self.dialog)\n        button_frame.pack(fill=tk.X, padx=10, pady=10)\n        \n        ttk.Button(button_frame, text=\"Start\", command=self.ok_clicked).pack(side=tk.RIGHT, padx=5)\n        ttk.Button(button_frame, text=\"Cancel\", command=self.cancel_clicked).pack(side=tk.RIGHT)\n        \n        # Make modal\n        self.dialog.transient(parent)\n        self.dialog.grab_set()\n        parent.wait_window(self.dialog)\n    \n    def ok_clicked(self):\n        \"\"\"Handle OK button click\"\"\"\n        self.selected_buckets = [bucket for bucket, var in self.bucket_vars.items() if var.get()]\n        self.user_guidance = self.guidance_text.get(1.0, tk.END).strip()\n        \n        if not self.selected_buckets:\n            messagebox.showwarning(\"No Buckets\", \"Please select at least one bucket\")\n            return\n        \n        self.result = True\n        self.dialog.destroy()\n    \n    def cancel_clicked(self):\n        \"\"\"Handle Cancel button click\"\"\"\n        self.result = False\n        self.dialog.destroy()\n\n\ndef main():\n    \"\"\"Main entry point\"\"\"\n    import argparse\n    \n    parser = argparse.ArgumentParser(description=\"Lizzy Framework - AI-Assisted Screenwriting\")\n    parser.add_argument(\"--project\", \"-p\", help=\"Project directory path\")\n    parser.add_argument(\"--gui\", action=\"store_true\", help=\"Launch GUI interface\")\n    parser.add_argument(\"--demo\", action=\"store_true\", help=\"Run demonstration mode\")\n    \n    args = parser.parse_args()\n    \n    if args.demo:\n        # Run demonstration\n        demo_project = \"exports/the_wrong_wedding_20250813_1253\"\n        if os.path.exists(demo_project):\n            orchestrator = LizzyOrchestrator(demo_project)\n            orchestrator.launch_gui()\n        else:\n            print(f\"Demo project not found: {demo_project}\")\n            print(\"Please create a project first.\")\n    \n    elif args.gui or args.project:\n        # Launch GUI\n        orchestrator = LizzyOrchestrator(args.project)\n        orchestrator.launch_gui()\n    \n    else:\n        # Show help\n        parser.print_help()\n        print(\"\\nExamples:\")\n        print(\"  python lizzy_main_orchestrator.py --gui\")\n        print(\"  python lizzy_main_orchestrator.py --project /path/to/project\")\n        print(\"  python lizzy_main_orchestrator.py --demo\")\n\n\nif __name__ == \"__main__\":\n    main()