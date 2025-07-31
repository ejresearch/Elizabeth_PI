#!/usr/bin/env python3
"""
Lizzy Framework - Content Bucket Setup
Helps users populate LightRAG thematic buckets with source material
"""

import os
import sys
import shutil

def create_bucket_structure():
    """Create the basic bucket structure"""
    working_dir = "./lightrag_working_dir"
    buckets = ["books", "plays", "scripts"]
    
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
        print(f" Created LightRAG working directory: {working_dir}")
    
    for bucket in buckets:
        bucket_path = os.path.join(working_dir, bucket)
        if not os.path.exists(bucket_path):
            os.makedirs(bucket_path)
            print(f" Created bucket: {bucket}")
        
        # Create a README file for each bucket
        readme_path = os.path.join(bucket_path, "README.txt")
        if not os.path.exists(readme_path):
            readme_content = f"""
LIZZY FRAMEWORK - {bucket.upper()} BUCKET
{'=' * 50}

This bucket is for storing {bucket}-related source material.

SUPPORTED FILE TYPES:
- .txt files (plain text)  
- .md files (markdown)
- .pdf files (will be processed)

RECOMMENDATIONS FOR {bucket.upper()}:
"""
            
            if bucket == "books":
                readme_content += """
- Screenwriting guides (Syd Field, Robert McKee, etc.)
- Writing craft books (Stephen King's "On Writing", etc.)
- Character development resources
- Story structure guides
- Genre-specific writing advice
"""
            elif bucket == "plays":
                readme_content += """
- Classical plays (Shakespeare, Tennessee Williams, etc.)
- Contemporary plays and theatrical works
- Dialogue-focused dramatic works
- Character study pieces
- Theatrical formatting examples
"""
            elif bucket == "scripts":
                readme_content += """
- Professional screenplays
- Sample scripts in your target genre
- Award-winning screenplays
- Contemporary film scripts
- TV pilot scripts and episodes
"""
            
            readme_content += f"""
TO ADD CONTENT:
1. Copy your source files to this directory
2. Run: python setup_buckets.py --ingest {bucket}
3. The content will be indexed for retrieval during brainstorming

CURRENT CONTENT:
- Check this directory for .txt, .md, or .pdf files
"""
            
            with open(readme_path, 'w') as f:
                f.write(readme_content)
            
            print(f" Created README for {bucket} bucket")

def list_bucket_content():
    """List content in all buckets"""
    working_dir = "./lightrag_working_dir"
    buckets = ["books", "plays", "scripts"]
    
    print("\n CURRENT BUCKET CONTENT")
    print("=" * 50)
    
    for bucket in buckets:
        bucket_path = os.path.join(working_dir, bucket)
        if not os.path.exists(bucket_path):
            print(f" {bucket.upper()}: Bucket not found")
            continue
        
        files = []
        for file in os.listdir(bucket_path):
            file_path = os.path.join(bucket_path, file)
            if os.path.isfile(file_path) and not file.startswith('.') and file != "README.txt":
                # Skip LightRAG metadata files
                if not file.endswith(('.json', '.graphml')):
                    files.append(file)
        
        print(f"\n {bucket.upper()} ({len(files)} files):")
        if files:
            for file in sorted(files):
                print(f"   - {file}")
        else:
            print("   (empty - add .txt, .md, or .pdf files)")

def ingest_bucket_content(bucket_name):
    """Ingest content into a specific bucket using LightRAG"""
    try:
        from lightrag import LightRAG
        from lightrag.llm import gpt_4o_mini_complete
    except ImportError:
        print(" LightRAG not installed!")
        print(" Install with: pip install lightrag")
        return False
    
    working_dir = "./lightrag_working_dir"
    bucket_path = os.path.join(working_dir, bucket_name)
    
    if not os.path.exists(bucket_path):
        print(f" Bucket '{bucket_name}' not found!")
        return False
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print(" OpenAI API key not found!")
        print(" Set your API key: export OPENAI_API_KEY=your_key_here")
        return False
    
    # Initialize LightRAG for this bucket
    print(f" Initializing LightRAG for {bucket_name} bucket...")
    rag = LightRAG(
        working_dir=bucket_path,
        llm_model_func=gpt_4o_mini_complete
    )
    
    # Find content files to ingest
    content_files = []
    for file in os.listdir(bucket_path):
        if file.endswith(('.txt', '.md')) and file != "README.txt":
            content_files.append(os.path.join(bucket_path, file))
    
    if not content_files:
        print(f"  No content files found in {bucket_name} bucket")
        print(" Add .txt or .md files to the bucket directory")
        return False
    
    print(f" Found {len(content_files)} content files to ingest...")
    
    # Ingest each file
    for file_path in content_files:
        filename = os.path.basename(file_path)
        print(f"   Processing: {filename}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Insert content into LightRAG
            rag.insert(content)
            print(f"    Ingested: {filename}")
            
        except Exception as e:
            print(f"    Failed to ingest {filename}: {e}")
    
    print(f"🎉 Bucket '{bucket_name}' ingestion complete!")
    return True

def main():
    """Main function for bucket setup"""
    print(" LIZZY FRAMEWORK - CONTENT BUCKET SETUP")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--ingest" and len(sys.argv) == 3:
            bucket_name = sys.argv[2]
            if bucket_name in ["books", "plays", "scripts"]:
                ingest_bucket_content(bucket_name)
            else:
                print(" Invalid bucket name. Use: books, plays, or scripts")
            return
        elif sys.argv[1] == "--list":
            list_bucket_content()
            return
    
    # Interactive mode
    while True:
        print("\nOptions:")
        print("1. Create/Setup Bucket Structure")
        print("2. List Current Content")
        print("3. Ingest Content into Bucket")
        print("4. Usage Instructions")
        print("0. Exit")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            create_bucket_structure()
        elif choice == "2":
            list_bucket_content()
        elif choice == "3":
            print("\nAvailable buckets: books, plays, scripts")
            bucket = input("Enter bucket name to ingest: ").strip().lower()
            if bucket in ["books", "plays", "scripts"]:
                ingest_bucket_content(bucket)
            else:
                print(" Invalid bucket name")
        elif choice == "4":
            print("""
 USAGE INSTRUCTIONS
==================

1. SETUP BUCKETS:
   - Run option 1 to create the bucket structure
   - This creates folders: books/, plays/, scripts/

2. ADD CONTENT:
   - Copy your source files (.txt, .md) into the appropriate bucket folder
   - Books: Screenwriting guides, craft books
   - Plays: Theatrical works, dialogue examples  
   - Scripts: Professional screenplays, samples

3. INGEST CONTENT:
   - Run option 3 to process files with LightRAG
   - This indexes content for retrieval during brainstorming
   - Requires OpenAI API key

4. USE IN WORKFLOW:
   - Run python brainstorm.py <project> to use indexed content
   - Content will be dynamically retrieved based on scene context
   - Different buckets provide different types of inspiration

COMMAND LINE USAGE:
   python setup_buckets.py --list           # List all content
   python setup_buckets.py --ingest books   # Ingest books bucket
            """)
        elif choice == "0":
            print(" Setup complete!")
            break
        else:
            print(" Invalid choice")

if __name__ == "__main__":
    main()