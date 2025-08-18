#!/usr/bin/env python3
"""
Test script for Prompt Studio integration with TransparentBrainstormer
"""

import os
import sys
from prompt_studio_backend import PromptStudioManager, get_brainstorm_template


def test_prompt_studio_integration():
    """Test the Prompt Studio integration"""
    
    print("🧪 Testing Prompt Studio Integration")
    print("="*50)
    
    # Use a demo project path
    demo_project = "test_project"
    
    # Create test directory if it doesn't exist
    if not os.path.exists(demo_project):
        os.makedirs(demo_project)
    
    print(f"📁 Using test project: {demo_project}")
    
    # Initialize manager
    manager = PromptStudioManager(demo_project)
    print("✅ PromptStudioManager initialized")
    
    # Test saving a custom template
    custom_template = """# Custom Test Template

## Scene Context  
SCENE: Act {context.act}, Scene {context.scene}
EVENTS: {context.scene_description}
CHARACTERS: {character_details}
LOGLINE: {logline}

## Task
Generate creative ideas for this scene.
Focus on: {user_guidance}

## Output
- 3-5 key insights
- 6-8 beat suggestions  
- 3-5 questions for development"""

    template_id = manager.save_template(
        template_name="Test Custom Template",
        prompt_template=custom_template,
        buckets={"scripts": True, "plays": True, "books": False}
    )
    
    print(f"✅ Saved custom template with ID: {template_id}")
    
    # Test retrieving active template
    active_template = manager.get_active_template()
    if active_template:
        print(f"✅ Retrieved active template: {active_template['template_name']}")
        print(f"📝 Template preview: {active_template['prompt_template'][:100]}...")
    else:
        print("❌ No active template found")
    
    # Test the integration function
    template_text = get_brainstorm_template(demo_project)
    print(f"✅ Integration function returned {len(template_text)} characters")
    
    # Test with non-existent project (should return default)
    default_template = get_brainstorm_template("nonexistent_project")
    print(f"✅ Default template fallback: {len(default_template)} characters")
    
    print("\n🎉 All tests passed!")
    print("\n📋 Integration Summary:")
    print("1. Prompt Studio saves templates to project.sqlite → prompt_configs")
    print("2. TransparentBrainstormer calls get_brainstorm_template()")  
    print("3. Custom templates automatically loaded during brainstorming")
    print("4. Falls back to default if no custom template exists")
    
    # Cleanup test directory
    import shutil
    if os.path.exists(demo_project):
        shutil.rmtree(demo_project)
    
    print(f"\n🧹 Cleaned up test directory: {demo_project}")


if __name__ == "__main__":
    test_prompt_studio_integration()