#!/bin/bash

echo "🚀 Setting up LIZZY Framework repository..."

# Remove any existing git history
rm -rf .git

# Initialize fresh git repo
git init

# Remove large files before adding to git
echo "🧹 Cleaning up large files..."
rm -rf lightrag_working_dir/
rm -f *_export_*.json
rm -f *_summary_*.md

# Create a sample bucket structure file for users
cat > SETUP_BUCKETS.md << 'EOF'
# Setting Up Knowledge Buckets

After cloning this repository, you'll need to create the LightRAG buckets:

1. Create the directory structure:
```bash
mkdir -p lightrag_working_dir/books
mkdir -p lightrag_working_dir/scripts  
mkdir -p lightrag_working_dir/plays
```

2. Add your reference materials:
   - Place `.txt` or `.md` files in each bucket
   - Or use the GUI: `python lizzy.py` → Buckets Manager → GUI File Manager

3. The system will automatically index your content when you first query it.

## Demo Content

For demonstration purposes, you can create sample files:
- `books/`: Writing theory, character development guides
- `scripts/`: Screenplay analyses, structure examples
- `plays/`: Dialogue techniques, theatrical writing

The system works best with 3-5 reference documents per bucket.
EOF

echo "✅ Created SETUP_BUCKETS.md"

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: LIZZY Framework - AI-Assisted Screenwriting System

- Complete CLI/GUI screenwriting framework
- SQLite database architecture  
- OpenAI GPT-4o Mini integration
- Modular design with 4 core components
- Sample project included

Note: LightRAG data excluded due to size. See SETUP_BUCKETS.md for setup instructions."

echo "✅ Repository initialized!"
echo ""
echo "Now run these commands to push to GitHub:"
echo ""
echo "git remote add origin https://github.com/ejresearch/Elizabeth_PI.git"
echo "git push -u origin main"
echo ""
echo "If 'main' doesn't work, try: git push -u origin master"