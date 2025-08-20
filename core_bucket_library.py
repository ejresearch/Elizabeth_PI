"""
Bucket Library Management System
Enables centralized bucket storage with project-based organization and import/export
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
import hashlib

class BucketLibrary:
    """Manages a centralized library of LightRAG buckets"""
    
    def __init__(self, library_path: str = None):
        """Initialize the bucket library"""
        if library_path is None:
            library_path = os.path.expanduser("~/lightrag_library")
        
        self.library_path = Path(library_path)
        self.buckets_dir = self.library_path / "buckets"
        self.projects_dir = self.library_path / "projects"
        self.config_file = self.library_path / "library_config.json"
        
        self._initialize_library()
        self.config = self._load_config()
        
    def _initialize_library(self):
        """Create library directory structure"""
        self.library_path.mkdir(exist_ok=True)
        self.buckets_dir.mkdir(exist_ok=True)
        self.projects_dir.mkdir(exist_ok=True)
        
        if not self.config_file.exists():
            default_config = {
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "bucket_count": 0,
                "project_count": 0,
                "metadata": {}
            }
            self._save_config(default_config)
    
    def _load_config(self) -> Dict:
        """Load library configuration"""
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def _save_config(self, config: Dict):
        """Save library configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def create_bucket(self, bucket_name: str, project_name: str, description: str = "") -> Dict:
        """Create a new bucket in the library and assign it to a project"""
        bucket_id = self._generate_bucket_id(bucket_name, project_name)
        bucket_path = self.buckets_dir / bucket_id
        
        if bucket_path.exists():
            return {"success": False, "error": f"Bucket {bucket_id} already exists"}
        
        bucket_path.mkdir(exist_ok=True)
        
        # Create bucket metadata
        metadata = {
            "id": bucket_id,
            "name": bucket_name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "created_by_project": project_name,
            "projects": [project_name],
            "stats": {
                "document_count": 0,
                "entity_count": 0,
                "relationship_count": 0
            }
        }
        
        metadata_file = bucket_path / "bucket_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Update project configuration
        self._add_bucket_to_project(project_name, bucket_id)
        
        # Update library config
        self.config["bucket_count"] += 1
        self._save_config(self.config)
        
        return {"success": True, "bucket_id": bucket_id, "path": str(bucket_path)}
    
    def _generate_bucket_id(self, bucket_name: str, project_name: str) -> str:
        """Generate a unique bucket ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_input = f"{bucket_name}_{project_name}_{timestamp}"
        hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"{bucket_name}_{hash_suffix}"
    
    def _add_bucket_to_project(self, project_name: str, bucket_id: str):
        """Add a bucket to a project's configuration"""
        project_file = self.projects_dir / f"{project_name}.json"
        
        if project_file.exists():
            with open(project_file, 'r') as f:
                project_config = json.load(f)
        else:
            project_config = {
                "name": project_name,
                "created_at": datetime.now().isoformat(),
                "buckets": [],
                "settings": {}
            }
            self.config["project_count"] += 1
            self._save_config(self.config)
        
        if bucket_id not in project_config["buckets"]:
            project_config["buckets"].append(bucket_id)
            project_config["last_modified"] = datetime.now().isoformat()
        
        with open(project_file, 'w') as f:
            json.dump(project_config, f, indent=2)
    
    def import_bucket_to_project(self, bucket_id: str, project_name: str, 
                                 project_dir: str) -> Dict:
        """Import a bucket from the library to a project"""
        bucket_path = self.buckets_dir / bucket_id
        
        if not bucket_path.exists():
            return {"success": False, "error": f"Bucket {bucket_id} not found"}
        
        # Create project lightrag directory structure
        project_lightrag = Path(project_dir) / "lightrag_working_dir"
        imported_dir = project_lightrag / "imported"
        imported_dir.mkdir(parents=True, exist_ok=True)
        
        # Create symlink to library bucket
        symlink_path = imported_dir / bucket_id
        if symlink_path.exists():
            if symlink_path.is_symlink():
                symlink_path.unlink()
            else:
                return {"success": False, "error": f"Path {symlink_path} already exists and is not a symlink"}
        
        try:
            symlink_path.symlink_to(bucket_path)
        except OSError as e:
            # Fallback to copying if symlinks aren't supported
            shutil.copytree(bucket_path, symlink_path)
        
        # Update bucket metadata to include this project
        metadata_file = bucket_path / "bucket_metadata.json"
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        if project_name not in metadata["projects"]:
            metadata["projects"].append(project_name)
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        # Update project configuration
        self._add_bucket_to_project(project_name, bucket_id)
        
        # Create/update project-specific configuration
        project_config_file = project_lightrag / "project_lightrag.json"
        if project_config_file.exists():
            with open(project_config_file, 'r') as f:
                project_config = json.load(f)
        else:
            project_config = {
                "project_name": project_name,
                "created_at": datetime.now().isoformat(),
                "imported_buckets": [],
                "local_buckets": []
            }
        
        if bucket_id not in project_config["imported_buckets"]:
            project_config["imported_buckets"].append(bucket_id)
        
        with open(project_config_file, 'w') as f:
            json.dump(project_config, f, indent=2)
        
        return {"success": True, "message": f"Bucket {bucket_id} imported to {project_name}"}
    
    def list_library_buckets(self) -> List[Dict]:
        """List all buckets in the library"""
        buckets = []
        
        for bucket_dir in self.buckets_dir.iterdir():
            if bucket_dir.is_dir():
                metadata_file = bucket_dir / "bucket_metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        buckets.append(metadata)
        
        return buckets
    
    def list_project_buckets(self, project_name: str) -> List[Dict]:
        """List all buckets associated with a project"""
        project_file = self.projects_dir / f"{project_name}.json"
        
        if not project_file.exists():
            return []
        
        with open(project_file, 'r') as f:
            project_config = json.load(f)
        
        buckets = []
        for bucket_id in project_config.get("buckets", []):
            bucket_path = self.buckets_dir / bucket_id
            metadata_file = bucket_path / "bucket_metadata.json"
            
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    buckets.append(json.load(f))
        
        return buckets
    
    def export_bucket(self, bucket_id: str, export_path: str) -> Dict:
        """Export a bucket from the library to an external location"""
        bucket_path = self.buckets_dir / bucket_id
        
        if not bucket_path.exists():
            return {"success": False, "error": f"Bucket {bucket_id} not found"}
        
        export_dest = Path(export_path) / bucket_id
        
        try:
            shutil.copytree(bucket_path, export_dest)
            return {"success": True, "exported_to": str(export_dest)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def share_bucket_between_projects(self, bucket_id: str, from_project: str, 
                                     to_project: str) -> Dict:
        """Share a bucket from one project to another"""
        bucket_path = self.buckets_dir / bucket_id
        
        if not bucket_path.exists():
            return {"success": False, "error": f"Bucket {bucket_id} not found"}
        
        # Update bucket metadata
        metadata_file = bucket_path / "bucket_metadata.json"
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        if to_project not in metadata["projects"]:
            metadata["projects"].append(to_project)
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        # Add to target project
        self._add_bucket_to_project(to_project, bucket_id)
        
        return {"success": True, "message": f"Bucket {bucket_id} shared from {from_project} to {to_project}"}
    
    def get_bucket_info(self, bucket_id: str) -> Optional[Dict]:
        """Get detailed information about a bucket"""
        bucket_path = self.buckets_dir / bucket_id
        metadata_file = bucket_path / "bucket_metadata.json"
        
        if not metadata_file.exists():
            return None
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Add storage information
        metadata["storage"] = {
            "path": str(bucket_path),
            "size_mb": self._get_directory_size(bucket_path) / (1024 * 1024)
        }
        
        return metadata
    
    def _get_directory_size(self, path: Path) -> int:
        """Calculate total size of a directory in bytes"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size
    
    def search_buckets(self, query: str) -> List[Dict]:
        """Search buckets by name or description"""
        results = []
        query_lower = query.lower()
        
        for bucket in self.list_library_buckets():
            if (query_lower in bucket["name"].lower() or 
                query_lower in bucket.get("description", "").lower()):
                results.append(bucket)
        
        return results
    
    def get_library_stats(self) -> Dict:
        """Get statistics about the bucket library"""
        buckets = self.list_library_buckets()
        projects = list(self.projects_dir.glob("*.json"))
        
        total_size = self._get_directory_size(self.library_path)
        
        return {
            "total_buckets": len(buckets),
            "total_projects": len(projects),
            "total_size_mb": total_size / (1024 * 1024),
            "average_bucket_size_mb": (total_size / len(buckets) / (1024 * 1024)) if buckets else 0,
            "most_shared_buckets": self._get_most_shared_buckets(buckets),
            "library_path": str(self.library_path)
        }
    
    def _get_most_shared_buckets(self, buckets: List[Dict]) -> List[Dict]:
        """Find buckets shared across the most projects"""
        sorted_buckets = sorted(buckets, 
                               key=lambda x: len(x.get("projects", [])), 
                               reverse=True)
        return sorted_buckets[:5]


class ProjectLightRAGManager:
    """Manages LightRAG instances for a specific project"""
    
    def __init__(self, project_dir: str, project_name: str, library: BucketLibrary = None):
        """Initialize project-specific LightRAG manager"""
        self.project_dir = Path(project_dir)
        self.project_name = project_name
        self.lightrag_dir = self.project_dir / "lightrag_working_dir"
        self.imported_dir = self.lightrag_dir / "imported"
        self.local_dir = self.lightrag_dir / "local"
        self.config_file = self.lightrag_dir / "project_lightrag.json"
        
        # Use provided library or create default
        self.library = library if library else BucketLibrary()
        
        self._initialize_project_structure()
        self.config = self._load_config()
        
    def _initialize_project_structure(self):
        """Create project directory structure"""
        self.lightrag_dir.mkdir(parents=True, exist_ok=True)
        self.imported_dir.mkdir(parents=True, exist_ok=True)
        self.local_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.config_file.exists():
            default_config = {
                "project_name": self.project_name,
                "created_at": datetime.now().isoformat(),
                "imported_buckets": [],
                "local_buckets": [],
                "active_buckets": []
            }
            self._save_config(default_config)
    
    def _load_config(self) -> Dict:
        """Load project configuration"""
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def _save_config(self, config: Dict):
        """Save project configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def create_local_bucket(self, bucket_name: str, description: str = "") -> Dict:
        """Create a project-specific local bucket"""
        bucket_path = self.local_dir / bucket_name
        
        if bucket_path.exists():
            return {"success": False, "error": f"Local bucket {bucket_name} already exists"}
        
        bucket_path.mkdir(exist_ok=True)
        
        # Create bucket metadata
        metadata = {
            "name": bucket_name,
            "description": description,
            "type": "local",
            "created_at": datetime.now().isoformat(),
            "project": self.project_name
        }
        
        metadata_file = bucket_path / "bucket_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Update project config
        if bucket_name not in self.config["local_buckets"]:
            self.config["local_buckets"].append(bucket_name)
            self._save_config(self.config)
        
        return {"success": True, "path": str(bucket_path)}
    
    def import_from_library(self, bucket_id: str) -> Dict:
        """Import a bucket from the library"""
        return self.library.import_bucket_to_project(
            bucket_id, 
            self.project_name, 
            str(self.project_dir)
        )
    
    def promote_to_library(self, local_bucket_name: str, description: str = "") -> Dict:
        """Promote a local bucket to the library"""
        local_bucket_path = self.local_dir / local_bucket_name
        
        if not local_bucket_path.exists():
            return {"success": False, "error": f"Local bucket {local_bucket_name} not found"}
        
        # Create bucket in library
        result = self.library.create_bucket(local_bucket_name, self.project_name, description)
        
        if result["success"]:
            bucket_id = result["bucket_id"]
            library_bucket_path = Path(result["path"])
            
            # Copy local bucket content to library
            for item in local_bucket_path.iterdir():
                if item.name != "bucket_metadata.json":
                    if item.is_dir():
                        shutil.copytree(item, library_bucket_path / item.name)
                    else:
                        shutil.copy2(item, library_bucket_path / item.name)
            
            # Remove local bucket and create symlink
            shutil.rmtree(local_bucket_path)
            self.import_from_library(bucket_id)
            
            # Update project config
            self.config["local_buckets"].remove(local_bucket_name)
            if bucket_id not in self.config["imported_buckets"]:
                self.config["imported_buckets"].append(bucket_id)
            self._save_config(self.config)
            
            return {"success": True, "bucket_id": bucket_id, "message": f"Local bucket promoted to library as {bucket_id}"}
        
        return result
    
    def list_all_buckets(self) -> Dict:
        """List all buckets available to this project"""
        imported_buckets = []
        for bucket_id in self.config.get("imported_buckets", []):
            info = self.library.get_bucket_info(bucket_id)
            if info:
                info["type"] = "imported"
                imported_buckets.append(info)
        
        local_buckets = []
        for bucket_name in self.config.get("local_buckets", []):
            bucket_path = self.local_dir / bucket_name
            metadata_file = bucket_path / "bucket_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    metadata["type"] = "local"
                    local_buckets.append(metadata)
        
        return {
            "imported": imported_buckets,
            "local": local_buckets,
            "total": len(imported_buckets) + len(local_buckets)
        }
    
    def activate_bucket(self, bucket_identifier: str) -> bool:
        """Activate a bucket for use in the project"""
        if bucket_identifier not in self.config.get("active_buckets", []):
            self.config.setdefault("active_buckets", []).append(bucket_identifier)
            self._save_config(self.config)
            return True
        return False
    
    def deactivate_bucket(self, bucket_identifier: str) -> bool:
        """Deactivate a bucket"""
        if bucket_identifier in self.config.get("active_buckets", []):
            self.config["active_buckets"].remove(bucket_identifier)
            self._save_config(self.config)
            return True
        return False
    
    def get_active_buckets(self) -> List[str]:
        """Get list of currently active buckets"""
        return self.config.get("active_buckets", [])