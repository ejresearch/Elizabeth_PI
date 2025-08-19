#!/usr/bin/env python3
import requests
import json
import os

def upload_document(bucket_name, content, filename):
    """Upload a document to the LightRAG bucket"""
    url = f"http://localhost:8001/api/buckets/{bucket_name}/documents"
    
    # Clean content of problematic characters
    clean_content = content.replace('\r', '').replace('\t', ' ')
    
    data = {
        "content": clean_content,
        "filename": filename
    }
    
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def upload_scifi_collection():
    """Upload our sci-fi collection in manageable chunks"""
    
    # Upload H.G. Wells content
    print("Uploading H.G. Wells - The Time Machine...")
    with open('time_machine.txt', 'r', encoding='utf-8') as f:
        content = f.read()[:20000]  # First 20k characters
    result = upload_document('scifi_screenplays', content, 'time_machine_excerpt.txt')
    print(f"Result: {result}")
    
    print("\nUploading H.G. Wells - War of the Worlds...")
    with open('war_of_worlds.txt', 'r', encoding='utf-8') as f:
        content = f.read()[:20000]
    result = upload_document('scifi_screenplays', content, 'war_of_worlds_excerpt.txt')
    print(f"Result: {result}")
    
    print("\nUploading H.G. Wells - The Invisible Man...")
    with open('invisible_man.txt', 'r', encoding='utf-8') as f:
        content = f.read()[:20000]
    result = upload_document('scifi_screenplays', content, 'invisible_man_excerpt.txt')
    print(f"Result: {result}")
    
    print("\nUploading Jules Verne - Twenty Thousand Leagues...")
    with open('twenty_thousand_leagues.txt', 'r', encoding='utf-8') as f:
        content = f.read()[:20000]
    result = upload_document('scifi_screenplays', content, 'twenty_thousand_leagues_excerpt.txt')
    print(f"Result: {result}")
    
    print("\nUploading Blade Runner 2049 inspired scenes...")
    with open('blade_runner_2049_scenes.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    result = upload_document('scifi_screenplays', content, 'blade_runner_2049_scenes.txt')
    print(f"Result: {result}")
    
    print("\nUploading Matrix inspired scenes...")
    with open('matrix_inspired_scenes.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    result = upload_document('scifi_screenplays', content, 'matrix_inspired_scenes.txt')
    print(f"Result: {result}")
    
    print("\nUploading Alien inspired scenes...")
    with open('alien_inspired_scenes.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    result = upload_document('scifi_screenplays', content, 'alien_inspired_scenes.txt')
    print(f"Result: {result}")

if __name__ == "__main__":
    upload_scifi_collection()