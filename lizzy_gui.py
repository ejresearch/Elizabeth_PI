#!/usr/bin/env python3
"""
LIZZY Framework - GUI File Drop Interface
Drag-and-drop interface for adding content to LightRAG buckets
"""

import os
import sys
import re
import shutil
import threading
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    from tkinter.scrolledtext import ScrolledText
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

def validate_filename(filename):
    """Validate filename to prevent path traversal"""
    if not filename or not isinstance(filename, str):
        return False
    # Prevent path traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        return False
    # Allow only safe characters
    if not re.match(r'^[a-zA-Z0-9._-]+$', filename):
        return False
    return True

class LizzyFileDropGUI:
    def __init__(self):
        if not GUI_AVAILABLE:
            print(" GUI not available - tkinter not installed")
            return
            
        self.root = tk.Tk()
        self.setup_window()
        self.setup_widgets()
        self.setup_drag_drop()
        self.load_buckets()
        
    def setup_window(self):
        """Setup main window"""
        self.root.title("LIZZY - Content File Manager")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a2e')
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"800x600+{x}+{y}")
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Dark theme colors
        self.style.configure('Title.TLabel', 
                           background='#1a1a2e', 
                           foreground='#00d4aa',
                           font=('Arial', 16, 'bold'))
        
        self.style.configure('Subtitle.TLabel',
                           background='#1a1a2e',
                           foreground='#ffffff',
                           font=('Arial', 12))
        
        self.style.configure('Drop.TFrame',
                           background='#16213e',
                           relief='ridge',
                           borderwidth=2)
        
        self.style.configure('Bucket.TFrame',
                           background='#0f3460',
                           relief='raised',
                           borderwidth=1)
        
    def setup_widgets(self):
        """Setup GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text=" LIZZY Content Manager", style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Drag & drop files to add content to LightRAG buckets", style='Subtitle.TLabel')
        subtitle_label.pack(pady=(0, 20))
        
        # Create paned window for buckets and drop area
        self.paned_window = ttk.PanedWindow(main_frame, orient='horizontal')
        self.paned_window.pack(fill='both', expand=True)
        
        # Buckets panel
        self.setup_buckets_panel()
        
        # Drop area panel
        self.setup_drop_panel()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Select a bucket and drag files")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, style='Subtitle.TLabel')
        status_label.pack(pady=(10, 0))
        
    def setup_buckets_panel(self):
        """Setup buckets selection panel"""
        buckets_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(buckets_frame, weight=1)
        
        # Buckets title
        buckets_title = ttk.Label(buckets_frame, text=" Content Buckets", style='Subtitle.TLabel')
        buckets_title.pack(pady=(0, 10))
        
        # Buckets listbox with scrollbar
        listbox_frame = ttk.Frame(buckets_frame)
        listbox_frame.pack(fill='both', expand=True, padx=(0, 10))
        
        self.buckets_listbox = tk.Listbox(listbox_frame, 
                                         selectmode='single',
                                         bg='#16213e',
                                         fg='#ffffff',
                                         selectbackground='#00d4aa',
                                         selectforeground='#1a1a2e',
                                         font=('Arial', 11),
                                         activestyle='none')
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient='vertical', command=self.buckets_listbox.yview)
        self.buckets_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.buckets_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.buckets_listbox.bind('<<ListboxSelect>>', self.on_bucket_select)
        
        # Bucket management buttons
        buttons_frame = ttk.Frame(buckets_frame)
        buttons_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(buttons_frame, text=" New Bucket", command=self.create_bucket).pack(side='left', padx=(0, 5))
        ttk.Button(buttons_frame, text=" Refresh", command=self.load_buckets).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text=" Browse", command=self.browse_files).pack(side='left', padx=5)
        
    def setup_drop_panel(self):
        """Setup file drop panel"""
        drop_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(drop_frame, weight=2)
        
        # Drop area title
        drop_title = ttk.Label(drop_frame, text=" Drop Zone", style='Subtitle.TLabel')
        drop_title.pack(pady=(0, 10))
        
        # Main drop area
        self.drop_area = tk.Frame(drop_frame, 
                                 bg='#16213e',
                                 relief='ridge',
                                 bd=3,
                                 highlightthickness=2,
                                 highlightcolor='#00d4aa',
                                 highlightbackground='#16213e')
        self.drop_area.pack(fill='both', expand=True, padx=10)
        
        # Drop instructions
        self.drop_label = tk.Label(self.drop_area,
                                  text=" Drag files here\n\nSupported formats:\n• .txt files\n• .md files\n• .pdf files\n\nOr click 'Browse' to select files",
                                  bg='#16213e',
                                  fg='#00d4aa',
                                  font=('Arial', 14),
                                  justify='center')
        self.drop_label.pack(expand=True)
        
        # Files preview area
        preview_frame = ttk.Frame(drop_frame)
        preview_frame.pack(fill='x', padx=10, pady=(10, 0))
        
        preview_label = ttk.Label(preview_frame, text=" Files to Add:", style='Subtitle.TLabel')
        preview_label.pack(anchor='w')
        
        self.files_text = ScrolledText(preview_frame, height=6, 
                                      bg='#0f3460', fg='#ffffff',
                                      font=('Consolas', 10),
                                      wrap='word')
        self.files_text.pack(fill='x', pady=(5, 0))
        
        # Action buttons
        action_frame = ttk.Frame(drop_frame)
        action_frame.pack(fill='x', padx=10, pady=(10, 0))
        
        ttk.Button(action_frame, text=" Add Files to Bucket", command=self.add_files_to_bucket).pack(side='left')
        ttk.Button(action_frame, text=" Clear List", command=self.clear_files).pack(side='left', padx=(10, 0))
        ttk.Button(action_frame, text=" Process Bucket", command=self.process_bucket).pack(side='right')
        
        self.selected_bucket = None
        self.pending_files = []
        
    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        # Enable drop on the drop area
        self.drop_area.bind('<Button-1>', self.on_drop_click)
        self.drop_label.bind('<Button-1>', self.on_drop_click)
        
        # Try to enable drag and drop (platform dependent)
        try:
            self.root.tk.call('package', 'require', 'tkdnd')
            self.drop_area.drop_target_register('DND_Files')
            self.drop_area.dnd_bind('<<Drop>>', self.on_drop)
            self.drop_area.dnd_bind('<<DragEnter>>', self.on_drag_enter)
            self.drop_area.dnd_bind('<<DragLeave>>', self.on_drag_leave)
        except:
            # Fallback: click to browse
            pass
            
    def load_buckets(self):
        """Load available buckets"""
        self.buckets_listbox.delete(0, 'end')
        
        working_dir = "./lightrag_working_dir"
        if not os.path.exists(working_dir):
            os.makedirs(working_dir)
            
        buckets = []
        for entry in os.scandir(working_dir):
            if entry.is_dir() and not entry.name.startswith('.'):
                buckets.append(entry.name)
        
        for bucket in sorted(buckets):
            bucket_path = os.path.join(working_dir, bucket)
            # Count files
            content_count = 0
            if os.path.exists(bucket_path):
                for file in os.listdir(bucket_path):
                    if file.endswith(('.txt', '.md', '.pdf')):
                        content_count += 1
            
            # Check if indexed
            has_index = any(f.endswith('.json') for f in os.listdir(bucket_path) 
                          if os.path.isfile(os.path.join(bucket_path, f)))
            
            status = "" if has_index else ""
            display_text = f"{status} {bucket} ({content_count} files)"
            self.buckets_listbox.insert('end', display_text)
            
        if not buckets:
            self.buckets_listbox.insert('end', "No buckets found - Create one first")
            
    def on_bucket_select(self, event):
        """Handle bucket selection"""
        selection = self.buckets_listbox.curselection()
        if selection:
            text = self.buckets_listbox.get(selection[0])
            # Extract bucket name (remove status and count)
            if "No buckets found" in text:
                self.selected_bucket = None
                return
            
            # Parse bucket name from display text
            parts = text.split(' ')
            if len(parts) >= 2:
                self.selected_bucket = parts[1]  # Skip status emoji
                self.status_var.set(f"Selected bucket: {self.selected_bucket}")
                self.update_drop_area()
            
    def update_drop_area(self):
        """Update drop area based on selected bucket"""
        if self.selected_bucket:
            self.drop_label.config(
                text=f" Drop files for bucket: {self.selected_bucket}\n\nSupported formats:\n• .txt files\n• .md files\n• .pdf files\n\nFiles will be added to:\nlightrag_working_dir/{self.selected_bucket}/",
                fg='#00d4aa'
            )
            self.drop_area.config(highlightcolor='#00d4aa')
        else:
            self.drop_label.config(
                text=" Select a bucket first\n\nThen drag files here or click Browse",
                fg='#ff6b6b'
            )
            self.drop_area.config(highlightcolor='#ff6b6b')
            
    def on_drop_click(self, event):
        """Handle click on drop area"""
        if not self.selected_bucket:
            messagebox.showwarning("No Bucket Selected", "Please select a bucket first!")
            return
        self.browse_files()
        
    def on_drag_enter(self, event):
        """Handle drag enter"""
        self.drop_area.config(bg='#00d4aa', highlightbackground='#00d4aa')
        self.drop_label.config(bg='#00d4aa', fg='#1a1a2e')
        
    def on_drag_leave(self, event):
        """Handle drag leave"""
        self.drop_area.config(bg='#16213e', highlightbackground='#16213e')
        self.drop_label.config(bg='#16213e', fg='#00d4aa')
        
    def on_drop(self, event):
        """Handle file drop"""
        self.on_drag_leave(None)  # Reset colors
        
        if not self.selected_bucket:
            messagebox.showwarning("No Bucket Selected", "Please select a bucket first!")
            return
            
        files = self.root.tk.splitlist(event.data)
        self.add_files_to_preview(files)
        
    def browse_files(self):
        """Browse for files"""
        if not self.selected_bucket:
            messagebox.showwarning("No Bucket Selected", "Please select a bucket first!")
            return
            
        files = filedialog.askopenfilenames(
            title="Select files to add to bucket",
            filetypes=[
                ("Text files", "*.txt"),
                ("Markdown files", "*.md"), 
                ("PDF files", "*.pdf"),
                ("All supported", "*.txt;*.md;*.pdf"),
                ("All files", "*.*")
            ]
        )
        
        if files:
            self.add_files_to_preview(files)
            
    def add_files_to_preview(self, files):
        """Add files to preview list"""
        valid_extensions = {'.txt', '.md', '.pdf'}
        
        for file_path in files:
            file_path = os.path.normpath(file_path)
            if os.path.isfile(file_path):
                ext = Path(file_path).suffix.lower()
                if ext in valid_extensions:
                    if file_path not in self.pending_files:
                        self.pending_files.append(file_path)
                else:
                    messagebox.showwarning("Unsupported File", 
                                         f"File type {ext} not supported: {os.path.basename(file_path)}")
        
        self.update_files_preview()
        
    def update_files_preview(self):
        """Update the files preview area"""
        self.files_text.delete(1.0, 'end')
        
        if self.pending_files:
            self.files_text.insert('end', f" {len(self.pending_files)} files ready to add:\n\n")
            
            for i, file_path in enumerate(self.pending_files, 1):
                filename = os.path.basename(file_path)
                size = os.path.getsize(file_path)
                size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
                
                self.files_text.insert('end', f"{i:2d}. {filename} ({size_str})\n")
                self.files_text.insert('end', f"    {file_path}\n\n")
                
            self.status_var.set(f"{len(self.pending_files)} files ready - Click 'Add Files to Bucket'")
        else:
            self.files_text.insert('end', "No files selected yet.\nDrag files here or click Browse.")
            self.status_var.set("Ready - Select files to add")
            
    def clear_files(self):
        """Clear pending files list"""
        self.pending_files = []
        self.update_files_preview()
        
    def add_files_to_bucket(self):
        """Add pending files to selected bucket"""
        if not self.selected_bucket:
            messagebox.showwarning("No Bucket Selected", "Please select a bucket first!")
            return
            
        if not self.pending_files:
            messagebox.showwarning("No Files", "No files to add!")
            return
            
        working_dir = "./lightrag_working_dir"
        bucket_path = os.path.join(working_dir, self.selected_bucket)
        
        if not os.path.exists(bucket_path):
            os.makedirs(bucket_path)
            
        success_count = 0
        error_files = []
        
        for file_path in self.pending_files:
            try:
                filename = os.path.basename(file_path)
                
                # Validate filename to prevent path traversal
                if not validate_filename(filename):
                    error_files.append(f"{filename}: Invalid filename")
                    continue
                
                dest_path = os.path.join(bucket_path, filename)
                
                # Handle duplicates
                counter = 1
                original_name = filename
                while os.path.exists(dest_path):
                    name, ext = os.path.splitext(original_name)
                    filename = f"{name}_{counter}{ext}"
                    
                    # Validate new filename as well
                    if not validate_filename(filename):
                        error_files.append(f"{original_name}: Unable to create safe filename")
                        break
                    
                    dest_path = os.path.join(bucket_path, filename)
                    counter += 1
                else:
                    # Ensure destination is within bucket directory
                    dest_path_abs = os.path.abspath(dest_path)
                    bucket_path_abs = os.path.abspath(bucket_path)
                    if not dest_path_abs.startswith(bucket_path_abs):
                        error_files.append(f"{filename}: Invalid destination path")
                        continue
                    
                    shutil.copy2(file_path, dest_path)
                    success_count += 1
                
            except Exception as e:
                error_files.append(f"{os.path.basename(file_path)}: {str(e)}")
                
        # Show results
        if success_count > 0:
            messagebox.showinfo("Success", 
                              f" Added {success_count} files to bucket '{self.selected_bucket}'")
            
        if error_files:
            error_msg = " Failed to add some files:\n\n" + "\n".join(error_files)
            messagebox.showerror("Errors", error_msg)
            
        # Clear pending files and refresh
        self.clear_files()
        self.load_buckets()
        self.status_var.set(f"Added {success_count} files to {self.selected_bucket}")
        
    def process_bucket(self):
        """Process bucket with LightRAG (launch CLI)"""
        if not self.selected_bucket:
            messagebox.showwarning("No Bucket Selected", "Please select a bucket first!")
            return
            
        # Show info about processing
        result = messagebox.askyesno("Process Bucket", 
                                   f"This will launch the command-line interface to process the '{self.selected_bucket}' bucket with LightRAG.\n\nThis requires an OpenAI API key and may take time.\n\nContinue?")
        
        if result:
            self.status_var.set(f"Launching CLI to process {self.selected_bucket}...")
            self.root.update()
            
            # Launch CLI in a separate process
            import subprocess
            try:
                subprocess.Popen([sys.executable, "lizzy.py"], 
                               cwd=os.path.dirname(os.path.abspath(__file__)))
                messagebox.showinfo("CLI Launched", 
                                  f"Command-line interface launched!\n\nUse 'Buckets Manager (LightRAG)' → 'Ingest/Reindex Bucket' → '{self.selected_bucket}' to process the files.")
            except Exception as e:
                messagebox.showerror("Launch Error", f"Failed to launch CLI: {e}")
                
    def create_bucket(self):
        """Create a new bucket"""
        from tkinter.simpledialog import askstring
        
        bucket_name = askstring("New Bucket", "Enter bucket name:")
        if bucket_name:
            # Sanitize name
            import re
            bucket_name = re.sub(r'[^\w\-_]', '_', bucket_name.lower())
            
            working_dir = "./lightrag_working_dir"
            bucket_path = os.path.join(working_dir, bucket_name)
            
            if os.path.exists(bucket_path):
                messagebox.showerror("Error", f"Bucket '{bucket_name}' already exists!")
                return
                
            try:
                os.makedirs(bucket_path)
                
                # Create README
                readme_content = f"""# {bucket_name.upper()} BUCKET

This bucket is for storing {bucket_name}-related source material.

## Supported File Types
- .txt files (plain text)  
- .md files (markdown)
- .pdf files (will be processed)

## Usage
1. Add your source files to this directory
2. Run Ingest/Reindex Bucket to process with LightRAG
3. Query the bucket for contextual content retrieval

Created via LIZZY GUI File Manager
"""
                
                with open(os.path.join(bucket_path, "README.md"), 'w') as f:
                    f.write(readme_content)
                
                messagebox.showinfo("Success", f" Bucket '{bucket_name}' created successfully!")
                self.load_buckets()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create bucket: {e}")
                
    def run(self):
        """Run the GUI"""
        if not GUI_AVAILABLE:
            print(" GUI not available - install tkinter")
            return
            
        self.root.mainloop()

def launch_gui():
    """Launch the GUI interface"""
    if not GUI_AVAILABLE:
        print(" GUI requires tkinter - install with: pip install tk")
        return False
    
    # Ensure GUI runs on main thread (required for macOS)
    if threading.current_thread() != threading.main_thread():
        print(" GUI must be launched from main thread")
        return False
        
    try:
        gui = LizzyFileDropGUI()
        gui.run()
        return True
    except Exception as e:
        print(f" GUI error: {e}")
        return False

if __name__ == "__main__":
    launch_gui()