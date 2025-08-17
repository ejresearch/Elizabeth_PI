#!/usr/bin/env python3
"""
Populate ALL 30 scenes in the gamma project with complete romcom descriptions
"""

import requests
import json

BASE_URL = "http://localhost:8080/api"

# Complete 30-scene romcom structure
all_scenes_data = [
    # ACT 1 - Setup (Scenes 1-10)
    {"id": 1, "description": "Emma's scathing review of 'Rosa's Kitchen' goes viral, destroying Jake's restaurant opening night"},
    {"id": 2, "description": "Jake confronts Emma at her favorite coffee shop, heated argument reveals mutual attraction"},
    {"id": 3, "description": "Maya pushes Emma to give the restaurant a fair second chance, guilt sets in"},
    {"id": 4, "description": "Emma goes undercover with fake name to Jake's restaurant for honest review"},
    {"id": 5, "description": "Jake catches Emma's deception but they end up cooking together in kitchen"},
    {"id": 6, "description": "Emma discovers Jake's passion and family history behind the restaurant"},
    {"id": 7, "description": "Jake learns about Emma's food blog origins and her own culinary dreams"},
    {"id": 8, "description": "Victoria offers Emma promotion to destroy competitors like Jake's restaurant"},
    {"id": 9, "description": "Emma and Jake's first real conversation about food, culture, and authenticity"},
    {"id": 10, "description": "Farmer's market date - Jake shows Emma where he sources ingredients, chemistry builds"},
    
    # ACT 2A - Rising Action (Scenes 11-15)
    {"id": 11, "description": "Emma writes positive review but Victoria kills it, demanding harsher criticism"},
    {"id": 12, "description": "Jake invites Emma to family dinner with Abuela Rosa and Carlos"},
    {"id": 13, "description": "Abuela Rosa teaches Emma family recipes, cultural significance of food"},
    {"id": 14, "description": "Emma and Jake's first kiss during late-night cooking session"},
    {"id": 15, "description": "Victoria discovers Emma's relationship, threatens job unless she destroys Jake"},
    
    # ACT 2B - Complications (Scenes 16-20)
    {"id": 16, "description": "Emma struggles between career ambitions and growing feelings for Jake"},
    {"id": 17, "description": "Jake plans surprise birthday dinner for Emma using her favorite flavors"},
    {"id": 18, "description": "Carlos warns Jake about getting too involved with food critic"},
    {"id": 19, "description": "Emma and Jake have first major fight about honesty and trust"},
    {"id": 20, "description": "Victoria gives Emma ultimatum: destroy Jake's restaurant or lose everything"},
    
    # ACT 2C - Crisis (Scenes 21-25)
    {"id": 21, "description": "Emma chooses career, writes devastating follow-up review of Rosa's Kitchen"},
    {"id": 22, "description": "Jake discovers Emma's betrayal, feels completely used and heartbroken"},
    {"id": 23, "description": "Restaurant faces closure, family recipes at risk of being lost forever"},
    {"id": 24, "description": "Maya confronts Emma about throwing away real love for fake success"},
    {"id": 25, "description": "Emma realizes Victoria manipulated her, but damage seems irreversible"},
    
    # ACT 3 - Resolution (Scenes 26-30)
    {"id": 26, "description": "Emma quits magazine, decides to fight for Jake and the restaurant"},
    {"id": 27, "description": "Emma organizes food blogger campaign to save Rosa's Kitchen"},
    {"id": 28, "description": "Jake initially rejects Emma's help, too hurt to trust again"},
    {"id": 29, "description": "Abuela Rosa convinces Jake that love requires forgiveness and second chances"},
    {"id": 30, "description": "Grand reopening with Emma's help, public apology, and passionate reconciliation"}
]

def update_scene_description(scene_id, description):
    """Update a scene description"""
    try:
        response = requests.put(f"{BASE_URL}/outline/{scene_id}",
                              json={"field": "description", "value": description})
        return response.json().get("success", False)
    except:
        return False

def populate_all_scenes():
    """Populate all 30 scene descriptions"""
    print("📖 Populating ALL 30 scenes with complete romcom structure...")
    print("🎬 Story: Food blogger vs Chef - Complete 3-Act Structure")
    print("=" * 60)
    
    success_count = 0
    failed_scenes = []
    
    for scene in all_scenes_data:
        scene_id = scene["id"]
        description = scene["description"]
        
        if update_scene_description(scene_id, description):
            success_count += 1
            act = "Act 1" if scene_id <= 10 else "Act 2" if scene_id <= 25 else "Act 3"
            print(f"  ✅ Scene {scene_id:2d} ({act}): {description[:60]}...")
        else:
            failed_scenes.append(scene_id)
            print(f"  ❌ Failed to update scene {scene_id}")
    
    print("=" * 60)
    print(f"🎭 Completed: {success_count}/30 scenes successfully populated")
    
    if failed_scenes:
        print(f"⚠️  Failed scenes: {failed_scenes}")
    else:
        print("✨ ALL scenes populated successfully!")
        print()
        print("📚 Complete Story Structure:")
        print("   • Act 1 (Scenes 1-10): Setup & Meet-Cute")
        print("   • Act 2A (Scenes 11-15): Rising Romance") 
        print("   • Act 2B (Scenes 16-20): Complications")
        print("   • Act 2C (Scenes 21-25): Crisis & Breakup")
        print("   • Act 3 (Scenes 26-30): Resolution & Love Wins")

def main():
    """Main population function"""
    try:
        # Test server connection
        response = requests.get(f"{BASE_URL}/project/info")
        if response.status_code != 200:
            print("❌ Cannot connect to web server. Make sure it's running on localhost:8080")
            return
        
        print("✅ Connected to web server")
        print()
        
        populate_all_scenes()
        
        print()
        print("🎉 All 30 scenes now have complete descriptions!")
        print("🌐 Refresh your browser to see the full story outline")
        print("📝 Ready for brainstorming and scene writing!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()