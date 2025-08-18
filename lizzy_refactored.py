#!/usr/bin/env python3
"""
LIZZY FRAMEWORK - Unified Entry Point with Service Launcher
AI-Assisted Long-Form Writing System with Template Support
"""

import os
import sys
import subprocess
import webbrowser
from datetime import datetime
from typing import Dict, List

# Import shared components
from lizzy_shared import db_manager, project_manager, logger

class LizzyServiceManager:
    """Manages all Lizzy services and provides unified entry point"""
    
    def __init__(self):
        self.services = {
            'web': {
                'name': 'Web Project Editor',
                'script': 'web_server.py',
                'port': 8080,
                'description': 'Main project data curation interface'
            },
            'prompt': {
                'name': 'Prompt Studio',
                'script': 'prompt_studio_dynamic.py', 
                'port': 8002,
                'description': 'Template creation and management'
            },
            'brainstorm': {
                'name': 'Brainstorm Studio',
                'script': 'brainstorm_backend_enhanced.py',
                'port': 5001,
                'description': 'AI brainstorming with templates'
            }
        }
        self.running_processes = {}
    
    def list_projects(self) -> List[str]:
        """List available projects"""
        return db_manager.get_projects_list()
    
    def show_menu(self):
        """Show main menu"""
        print("\n" + "="*60)
        print("🦎 LIZZY - AI Writing Framework")
        print("="*60)
        
        projects = self.list_projects()
        if projects:
            print(f"\n📁 Available Projects ({len(projects)}):")
            for i, project in enumerate(projects, 1):
                print(f"  {i}. {project}")
        else:
            print("\n📁 No projects found in exports/ directory")
            print("   Create a project first using the web interface")
        
        print(f"\n🚀 Available Services:")
        for key, service in self.services.items():
            status = "✅ Running" if key in self.running_processes else "⚪ Stopped"
            print(f"  {key}: {service['name']} - {service['description']} ({status})")
        
        print(f"\n📋 Commands:")
        print(f"  start <service>  - Start a service (web, prompt, brainstorm)")
        print(f"  stop <service>   - Stop a service")
        print(f"  launch <service> - Start service and open browser")
        print(f"  status          - Show service status")
        print(f"  projects        - List projects")
        print(f"  help            - Show this menu")
        print(f"  quit            - Exit Lizzy")
        print("="*60)
    
    def start_service(self, service_key: str, open_browser: bool = False) -> bool:
        """Start a service"""
        if service_key not in self.services:
            print(f"❌ Unknown service: {service_key}")
            return False
        
        if service_key in self.running_processes:
            print(f"⚠️  Service '{service_key}' is already running")
            return False
        
        service = self.services[service_key]
        script_path = os.path.join(os.path.dirname(__file__), service['script'])
        
        if not os.path.exists(script_path):
            print(f"❌ Service script not found: {service['script']}")
            return False
        
        try:
            print(f"🚀 Starting {service['name']}...")
            process = subprocess.Popen([
                sys.executable, script_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.running_processes[service_key] = process
            
            # Give it a moment to start
            import time
            time.sleep(2)
            
            if process.poll() is None:  # Still running
                url = f"http://localhost:{service['port']}"
                print(f"✅ {service['name']} started at {url}")
                
                if open_browser:
                    print(f"🌐 Opening browser...")
                    webbrowser.open(url)
                
                return True
            else:
                # Process died
                stdout, stderr = process.communicate()
                print(f"❌ Failed to start {service['name']}")
                if stderr:
                    print(f"Error: {stderr.decode()}")
                del self.running_processes[service_key]
                return False
                
        except Exception as e:
            print(f"❌ Error starting service: {e}")
            return False
    
    def stop_service(self, service_key: str) -> bool:
        """Stop a service"""
        if service_key not in self.running_processes:
            print(f"⚠️  Service '{service_key}' is not running")
            return False
        
        try:
            process = self.running_processes[service_key]
            process.terminate()
            
            # Wait for graceful shutdown
            import time
            time.sleep(1)
            
            if process.poll() is None:
                # Force kill if still running
                process.kill()
            
            del self.running_processes[service_key]
            service_name = self.services[service_key]['name']
            print(f"🛑 {service_name} stopped")
            return True
            
        except Exception as e:
            print(f"❌ Error stopping service: {e}")
            return False
    
    def show_status(self):
        """Show status of all services"""
        print(f"\n📊 Service Status:")
        for key, service in self.services.items():
            if key in self.running_processes:
                process = self.running_processes[key]
                if process.poll() is None:
                    print(f"  ✅ {service['name']} - Running (PID: {process.pid})")
                else:
                    print(f"  ❌ {service['name']} - Dead process")
                    del self.running_processes[key]
            else:
                print(f"  ⚪ {service['name']} - Stopped")
    
    def stop_all_services(self):
        """Stop all running services"""
        for service_key in list(self.running_processes.keys()):
            self.stop_service(service_key)
    
    def launch_service(self, service_key: str) -> bool:
        """Start service and open browser"""
        return self.start_service(service_key, open_browser=True)
    
    def run(self):
        """Main interactive loop"""
        print("🦎 Lizzy Framework Starting...")
        
        try:
            while True:
                self.show_menu()
                
                try:
                    cmd = input("\n🦎 lizzy> ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    print("\n\n👋 Goodbye!")
                    break
                
                if not cmd:
                    continue
                
                parts = cmd.split()
                command = parts[0]
                
                if command == 'quit' or command == 'exit':
                    print("\n🛑 Stopping all services...")
                    self.stop_all_services()
                    print("👋 Goodbye!")
                    break
                
                elif command == 'help':
                    continue  # Menu will show again
                
                elif command == 'status':
                    self.show_status()
                
                elif command == 'projects':
                    projects = self.list_projects()
                    if projects:
                        print(f"\n📁 Available Projects:")
                        for project in projects:
                            try:
                                info = project_manager.get_project_info(project)
                                print(f"  • {project} ({info['total_records']} records)")
                            except Exception:
                                print(f"  • {project}")
                    else:
                        print("\n📁 No projects found")
                
                elif command == 'start':
                    if len(parts) < 2:
                        print("❌ Usage: start <service>")
                        print("   Available services: " + ", ".join(self.services.keys()))
                    else:
                        self.start_service(parts[1])
                
                elif command == 'stop':
                    if len(parts) < 2:
                        print("❌ Usage: stop <service>")
                        print("   Available services: " + ", ".join(self.services.keys()))
                    else:
                        self.stop_service(parts[1])
                
                elif command == 'launch':
                    if len(parts) < 2:
                        print("❌ Usage: launch <service>")
                        print("   Available services: " + ", ".join(self.services.keys()))
                    else:
                        self.launch_service(parts[1])
                
                else:
                    print(f"❌ Unknown command: {command}")
                    print("   Type 'help' for available commands")
        
        except KeyboardInterrupt:
            print("\n\n🛑 Interrupted - stopping all services...")
            self.stop_all_services()
            print("👋 Goodbye!")
        
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            self.stop_all_services()

def main():
    """Main entry point"""
    
    # Quick service launch shortcuts
    if len(sys.argv) > 1:
        service_manager = LizzyServiceManager()
        
        if sys.argv[1] == '--web':
            print("🚀 Quick launching Web Project Editor...")
            service_manager.launch_service('web')
            return
        
        elif sys.argv[1] == '--prompt':
            print("🚀 Quick launching Prompt Studio...")
            service_manager.launch_service('prompt')
            return
        
        elif sys.argv[1] == '--brainstorm':
            print("🚀 Quick launching Brainstorm Studio...")
            service_manager.launch_service('brainstorm')
            return
        
        elif sys.argv[1] == '--help':
            print("""
🦎 Lizzy Framework - Usage:

  python lizzy.py                 Interactive mode with service menu
  python lizzy.py --web           Quick launch Web Project Editor
  python lizzy.py --prompt        Quick launch Prompt Studio  
  python lizzy.py --brainstorm    Quick launch Brainstorm Studio
  python lizzy.py --help          Show this help

Workflow:
  1. Use --web to create/edit project data
  2. Use --prompt to create templates
  3. Use --brainstorm to generate content
            """)
            return
    
    # Interactive mode
    service_manager = LizzyServiceManager()
    service_manager.run()

if __name__ == "__main__":
    main()