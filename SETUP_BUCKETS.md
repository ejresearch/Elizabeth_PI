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
