#!/usr/bin/env python3
"""
Lizzy Framework - Complete GUI Demo Script
Shows you how to access all the latest HTML interfaces and test them
"""

import os
import sys
import time
import subprocess
import webbrowser
import threading
from datetime import datetime

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title):
    print(f"\n{Colors.CYAN}{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def check_projects():
    """Check available projects"""
    print_header("Checking Available Projects")
    
    projects_dir = 'projects'
    if not os.path.exists(projects_dir):
        print_error("No projects directory found!")
        return []
    
    projects = []
    for item in os.listdir(projects_dir):
        project_path = os.path.join(projects_dir, item)
        if os.path.isdir(project_path):
            db_path = os.path.join(project_path, f"{item}.sqlite")
            if os.path.exists(db_path):
                size = os.path.getsize(db_path)
                projects.append(item)
                print_success(f"Project '{item}' - Database: {size:,} bytes")
            else:
                print_warning(f"Project '{item}' - No database found")
    
    if projects:
        print_info(f"Found {len(projects)} projects ready for testing")
    
    return projects

def check_html_files():
    """Verify all HTML GUI files exist"""
    print_header("Verifying HTML GUI Files")
    
    html_files = {
        'brainstorm_seamless.html': 'Brainstorm Interface',
        'prompt_studio_dynamic.html': 'Prompt Studio Interface', 
        'web_project_editor.html': 'Web Project Editor',
        'prompt_editor_polished.html': 'Prompt Editor'
    }
    
    all_present = True
    for filename, description in html_files.items():
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print_success(f"{description}: {filename} ({size:,} bytes)")
        else:
            print_error(f"{description}: {filename} - MISSING!")
            all_present = False
    
    return all_present

def launch_server(script_name, port, name, delay=3):
    """Launch a server in background"""
    print_info(f"Starting {name}...")
    
    try:
        process = subprocess.Popen([
            sys.executable, script_name
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give server time to start
        time.sleep(delay)
        
        # Check if process is still running (didn't crash)
        if process.poll() is None:
            print_success(f"{name} started successfully on port {port}")
            return process
        else:
            stdout, stderr = process.communicate()
            print_error(f"{name} failed to start: {stderr.decode()}")
            return None
            
    except Exception as e:
        print_error(f"Failed to launch {name}: {e}")
        return None

def test_gui_interfaces():
    """Test all GUI interfaces"""
    print_header("Testing All GUI Interfaces")
    
    servers = []
    
    # 1. Brainstorm Seamless Interface
    print_info("1. Testing Brainstorm Seamless Interface")
    if os.path.exists('brainstorm_backend_refactored.py'):
        process = launch_server('brainstorm_backend_refactored.py', 5001, 'Brainstorm Backend')
        if process:
            servers.append(('Brainstorm Studio', 'http://localhost:5001', process))
    else:
        print_warning("brainstorm_backend_refactored.py not found")
    
    # 2. Prompt Studio Dynamic Interface  
    print_info("2. Testing Prompt Studio Dynamic Interface")
    if os.path.exists('prompt_studio_dynamic.py'):
        process = launch_server('prompt_studio_dynamic.py', 8002, 'Prompt Studio')
        if process:
            servers.append(('Prompt Studio', 'http://localhost:8002', process))
    else:
        print_warning("prompt_studio_dynamic.py not found")
    
    # 3. Web Project Editor Interface
    print_info("3. Testing Web Project Editor Interface")
    if os.path.exists('web_server_refactored.py'):
        process = launch_server('web_server_refactored.py', 8080, 'Web Project Editor')
        if process:
            servers.append(('Project Editor', 'http://localhost:8080', process))
    else:
        print_warning("web_server_refactored.py not found")
    
    return servers

def show_access_guide(servers):
    """Show how to access each interface"""
    print_header("🌐 GUI Access Guide")
    
    if not servers:
        print_error("No servers are running!")
        return
    
    print(f"{Colors.BOLD}All interfaces are now running. Access them via:{Colors.END}")
    print()
    
    for name, url, process in servers:
        print(f"{Colors.GREEN}🔗 {name}{Colors.END}")
        print(f"   URL: {Colors.CYAN}{url}{Colors.END}")
        print(f"   Status: {'✅ Running' if process.poll() is None else '❌ Stopped'}")
        print()
    
    # Special note about intake GUI
    print(f"{Colors.YELLOW}📝 Intake Interactive GUI{Colors.END}")
    print(f"   Type: tkinter-based desktop GUI")
    print(f"   Launch: python3 -c \"from lizzy_intake_interactive import launch_intake_gui; launch_intake_gui('projects/Alpha')\"")
    print()

def interactive_demo():
    """Interactive demonstration"""
    print_header("🎮 Interactive Demo")
    
    servers = test_gui_interfaces()
    
    if not servers:
        print_error("No servers could be started!")
        return
    
    show_access_guide(servers)
    
    print(f"{Colors.BOLD}Choose an action:{Colors.END}")
    print("1. Open all GUIs in browser")
    print("2. Open specific GUI")
    print("3. Show status")
    print("4. Exit and stop all servers")
    
    while True:
        try:
            choice = input(f"\n{Colors.CYAN}Enter choice (1-4): {Colors.END}")
            
            if choice == '1':
                print_info("Opening all GUIs in browser...")
                for name, url, process in servers:
                    if process.poll() is None:
                        print_info(f"Opening {name}: {url}")
                        webbrowser.open(url)
                        time.sleep(1)
                
            elif choice == '2':
                print("\nAvailable GUIs:")
                for i, (name, url, process) in enumerate(servers, 1):
                    status = "✅ Running" if process.poll() is None else "❌ Stopped"
                    print(f"  {i}. {name} - {status}")
                
                try:
                    gui_choice = int(input("Select GUI number: ")) - 1
                    if 0 <= gui_choice < len(servers):
                        name, url, process = servers[gui_choice]
                        if process.poll() is None:
                            print_info(f"Opening {name}: {url}")
                            webbrowser.open(url)
                        else:
                            print_error(f"{name} is not running!")
                    else:
                        print_error("Invalid selection!")
                except ValueError:
                    print_error("Please enter a valid number!")
                    
            elif choice == '3':
                print_info("Server Status:")
                for name, url, process in servers:
                    status = "✅ Running" if process.poll() is None else "❌ Stopped"
                    print(f"  {name}: {status}")
                    
            elif choice == '4':
                print_info("Stopping all servers...")
                for name, url, process in servers:
                    if process.poll() is None:
                        process.terminate()
                        print_success(f"Stopped {name}")
                print_success("All servers stopped. Goodbye!")
                break
                
            else:
                print_error("Invalid choice! Please enter 1-4.")
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Interrupted by user{Colors.END}")
            break
        except Exception as e:
            print_error(f"Error: {e}")

def main():
    """Main demo function"""
    print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    🎬 LIZZY FRAMEWORK GUI DEMO                              ║ 
║                      Complete Interface Testing                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}
""")
    
    print_info(f"Demo started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check prerequisites
    projects = check_projects()
    html_files_ok = check_html_files()
    
    if not projects:
        print_error("No projects found! Create some projects first.")
        return
    
    if not html_files_ok:
        print_error("Some HTML files are missing!")
        return
    
    print_success("All prerequisites met!")
    
    # Run interactive demo
    interactive_demo()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Demo interrupted by user. Cleaning up...{Colors.END}")
    except Exception as e:
        print_error(f"Demo failed: {e}")
        sys.exit(1)