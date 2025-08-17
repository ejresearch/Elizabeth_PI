#!/usr/bin/env python3
"""
Populate the gamma project with sample romcom data
"""

import requests
import json

BASE_URL = "http://localhost:8080/api"

# Character data for a romcom about a food blogger and a chef
characters_data = [
    {
        "id": 1,
        "name": "Emma Chen",
        "gender": "Female", 
        "age": "28",
        "challenge": "Trust issues from past betrayal",
        "trait": "Witty food blogger with sharp tongue",
        "flaw": "Judges people too quickly",
        "notes": "Food blogger who gave bad review to Jake's restaurant"
    },
    {
        "id": 2,
        "name": "Jake Rodriguez", 
        "gender": "Male",
        "age": "32",
        "challenge": "Fear of putting himself out there again",
        "trait": "Passionate about authentic cooking",
        "flaw": "Stubborn and proud",
        "notes": "Chef trying to save his family restaurant"
    },
    {
        "id": 3,
        "name": "Maya Patel",
        "gender": "Female", 
        "age": "26",
        "challenge": "People-pleasing tendencies",
        "trait": "Eternally optimistic best friend",
        "flaw": "Gives unsolicited advice",
        "notes": "Emma's roommate and social media manager"
    },
    {
        "id": 4,
        "name": "Carlos Rodriguez",
        "gender": "Male",
        "age": "35", 
        "challenge": "Workaholic tendencies",
        "trait": "Dry humor and wisdom",
        "flaw": "Meddles in Jake's love life",
        "notes": "Jake's older brother and business partner"
    },
    {
        "id": 5,
        "name": "Victoria Sterling",
        "gender": "Female",
        "age": "35",
        "challenge": "Obsessed with social status",
        "trait": "Sharp business acumen",
        "flaw": "Manipulative and condescending", 
        "notes": "Food magazine editor competing for Emma's restaurant reviews"
    },
    {
        "id": 6,
        "name": "Abuela Rosa",
        "gender": "Female",
        "age": "72",
        "challenge": "Watching family legacy fade",
        "trait": "Warm heart and killer cooking",
        "flaw": "Overly protective of traditions",
        "notes": "Jake's grandmother who started the restaurant"
    }
]

# Sample story outline updates
outline_updates = [
    {"id": 1, "description": "Emma's harsh review destroys Jake's restaurant opening night"},
    {"id": 2, "description": "Jake confronts Emma at coffee shop, sparks fly"},
    {"id": 3, "description": "Maya pushes Emma to give restaurant a second chance"},
    {"id": 4, "description": "Emma goes undercover to Jake's restaurant"},
    {"id": 5, "description": "Jake catches Emma but they end up cooking together"},
    {"id": 10, "description": "Emma and Jake's first real date at the farmer's market"},
    {"id": 15, "description": "Victoria offers Emma dream job to destroy Jake's restaurant"},
    {"id": 20, "description": "Emma must choose between career and love"},
    {"id": 25, "description": "Jake's restaurant faces closure, Emma feels guilty"},
    {"id": 30, "description": "Grand reopening with Emma's help, love wins"}
]

# Sample notes updates
notes_updates = [
    {
        "id": 1,
        "title": "Emma's Character Arc",
        "category": "Character Development", 
        "content": "Emma starts as cynical food critic who judges quickly. Through Jake, she learns to see beyond surface, discovering her own capacity for vulnerability and trust. Her arc is about opening her heart."
    },
    {
        "id": 2,
        "title": "Jake's Growth Journey",
        "category": "Character Development",
        "content": "Jake begins prideful and closed off after business failures. Meeting Emma forces him to confront his fears of vulnerability. He learns that true strength comes from openness and asking for help."
    },
    {
        "id": 3,
        "title": "Food as Love Language",
        "category": "Theme",
        "content": "Central theme: food represents love, culture, and connection. Jake's cooking is his way of expressing care. Emma's reviews become less about criticism and more about celebration of culinary artistry."
    }
]

def update_character_field(char_id, field, value):
    """Update a character field"""
    try:
        response = requests.put(f"{BASE_URL}/characters/{char_id}", 
                              json={"field": field, "value": value})
        return response.json().get("success", False)
    except:
        return False

def update_outline_field(scene_id, field, value):
    """Update an outline field"""
    try:
        response = requests.put(f"{BASE_URL}/outline/{scene_id}",
                              json={"field": field, "value": value})
        return response.json().get("success", False)
    except:
        return False

def update_note_field(note_id, field, value):
    """Update a note field"""
    try:
        response = requests.put(f"{BASE_URL}/notes/{note_id}",
                              json={"field": field, "value": value})
        return response.json().get("success", False)
    except:
        return False

def populate_characters():
    """Populate all character data"""
    print("🧑‍🤝‍🧑 Populating characters...")
    success_count = 0
    
    for char in characters_data:
        char_id = char["id"]
        fields = ["name", "gender", "age", "challenge", "trait", "flaw", "notes"]
        
        for field in fields:
            if char.get(field):
                if update_character_field(char_id, field, char[field]):
                    success_count += 1
                    print(f"  ✅ Updated {char['name']} - {field}")
                else:
                    print(f"  ❌ Failed to update {char['name']} - {field}")
    
    print(f"🎭 Characters: {success_count} field updates completed")

def populate_outline():
    """Populate story outline descriptions"""
    print("\n📖 Populating story outline...")
    success_count = 0
    
    for update in outline_updates:
        if update_outline_field(update["id"], "description", update["description"]):
            success_count += 1
            print(f"  ✅ Updated scene {update['id']}")
        else:
            print(f"  ❌ Failed to update scene {update['id']}")
    
    print(f"🎬 Outline: {success_count} scenes updated")

def populate_notes():
    """Populate development notes"""
    print("\n📝 Populating notes...")
    success_count = 0
    
    for note in notes_updates:
        note_id = note["id"]
        fields = ["title", "category", "content"]
        
        for field in fields:
            if note.get(field):
                if update_note_field(note_id, field, note[field]):
                    success_count += 1
                    print(f"  ✅ Updated note {note['title']} - {field}")
                else:
                    print(f"  ❌ Failed to update note {note['title']} - {field}")
    
    print(f"📋 Notes: {success_count} field updates completed")

def main():
    """Main population function"""
    print("🚀 Populating Gamma Project with Romcom Data")
    print("=" * 50)
    print("📚 Story: Food blogger vs Chef romantic comedy")
    print()
    
    try:
        # Test server connection
        response = requests.get(f"{BASE_URL}/project/info")
        if response.status_code != 200:
            print("❌ Cannot connect to web server. Make sure it's running on localhost:8080")
            return
        
        print("✅ Connected to web server")
        print()
        
        # Populate all data
        populate_characters()
        populate_outline() 
        populate_notes()
        
        print()
        print("🎉 Population complete!")
        print("🌐 Refresh your browser to see the updated data")
        print("💫 Your romcom project is ready for brainstorming and writing!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()