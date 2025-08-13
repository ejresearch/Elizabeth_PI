#!/usr/bin/env python3
"""
Debug template compilation
"""

import sys
import os
sys.path.append('/Users/elle/Desktop/Elizabeth_PI')

from lizzy_templates import TemplateManager

def debug_templates():
    """Debug template compilation"""
    
    tm = TemplateManager()
    tm.load_bucket_config()
    
    print("Available templates:")
    for category, templates in tm.templates.items():
        print(f"  {category}: {list(templates.keys()) if isinstance(templates, dict) else 'Not a dict'}")
    
    # Test get_template
    romcom_template = tm.get_template("romcom", "romcom")
    print(f"\nRomcom template: {romcom_template}")
    
    textbook_template = tm.get_template("textbook", "textbook")
    print(f"\nTextbook template: {textbook_template}")
    
    # Test context
    context = {
        "act": 1,
        "scene": 3,
        "scene_context": "Coffee shop meet-cute",
        "character_details": "Sarah (28): Commitment-phobic\nJake (30): Workaholic", 
        "previous_scene": "Sarah's morning routine"
    }
    
    if romcom_template:
        prompt = tm.compile_prompt("romcom", "romcom", context)
        print(f"\nRomcom prompt length: {len(prompt)}")
        print(f"Romcom prompt preview: {prompt[:200]}...")

if __name__ == "__main__":
    debug_templates()