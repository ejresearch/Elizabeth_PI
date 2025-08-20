# 🗂️ Bucket Library System - Setup Complete!

## ✅ What's Now Available

Your bucket library system is fully integrated and running! Here's what you can access:

### 🌐 **Bucket Manager** (Port 8002)
```bash
http://localhost:8002
```
**Features:**
- View all buckets (Local, Library, Legacy)
- Create buckets (Library or Local scope)
- Import buckets from library
- Export buckets
- Migrate existing buckets

### 📝 **Brainstorm Builder** (Port 8003) 
```bash
http://localhost:8003
```
**New Features:**
- **LightRAG Data Blocks** now include ALL bucket types:
  - 📁 **Local Buckets** - Project-specific buckets
  - 🌐 **Library Buckets** - Already imported from library
  - 📥 **Available Buckets** - **New!** One-click import from library

**How to Use:**
1. Open Brainstorm Builder
2. Navigate to "Data Blocks" section
3. See "📚 LightRAG Buckets" 
4. Click **Available Buckets** (dashed border) to instantly import & use
5. Use imported buckets normally in your prompts

## 🚀 **How to Start Servers**

### Start Bucket Manager:
```bash
python bucket_manager_server.py
# Access at http://localhost:8002
```

### Start Brainstorm Builder:  
```bash
python web_brainstorm_server.py
# Access at http://localhost:8003
```

## 📁 **Bucket Organization Structure**

```
~/lightrag_library/              # Global library (shared across all projects)
├── buckets/                     # All library buckets stored here
│   ├── bucket_id_abc123/        # Each bucket has unique ID
│   └── bucket_id_def456/
├── projects/                    # Project associations
│   ├── ProjectA.json            # Which buckets ProjectA uses
│   └── ProjectB.json
└── library_config.json         # Global library config

YourProject/
├── lightrag_working_dir/        # Project-specific LightRAG
│   ├── imported/               # Symlinks to library buckets
│   ├── local/                  # Project-only buckets
│   └── project_lightrag.json   # Project config
```

## 🎯 **Key New Features**

### **One-Click Import in Brainstorm**
- See available library buckets with dashed borders
- Click to automatically import to your project
- Immediately usable in prompts
- Real-time status updates

### **Bucket Scopes**
- **Library Buckets**: Shared across projects, centrally managed
- **Local Buckets**: Project-specific, can be promoted to library
- **Legacy Buckets**: Your existing buckets (backward compatible)

### **Import/Export**
- Import any library bucket to any project
- Export buckets for sharing
- Share buckets between projects
- Promote local buckets to library

## 🔧 **API Endpoints**

### Bucket Manager API (Port 8002):
```bash
GET    /api/buckets              # List all buckets  
POST   /api/buckets              # Create bucket
GET    /api/library/buckets      # List library buckets
POST   /api/library/import/{id}  # Import bucket
POST   /api/library/promote/{name} # Promote to library
GET    /api/library/stats        # Library statistics
POST   /api/migrate              # Migrate existing buckets
```

### Brainstorm API (Port 8003):
```bash
GET    /api/project/{name}/schema # Get project schema + buckets
```

## ✨ **Everything is Backward Compatible**

- Your existing buckets still work exactly as before
- Old bucket manager functionality preserved
- Existing workflows unchanged
- Migration is optional (but recommended)

---

## 🎉 **You're Ready!**

1. **Access Bucket Manager**: http://localhost:8002 
2. **Access Brainstorm Builder**: http://localhost:8003
3. **Create library buckets** for sharing across projects
4. **Import buckets** with one click in brainstorm builder
5. **Enjoy centralized bucket management!**