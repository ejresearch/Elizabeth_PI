"""
Integration layer between the existing bucket system and the new library architecture
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from core_bucket_library import BucketLibrary, ProjectLightRAGManager
from core_knowledge import LightRAGManager
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
import asyncio

class BucketLibraryIntegration:
    """Integrates the bucket library with existing LightRAG systems"""
    
    def __init__(self, project_dir: str = None, project_name: str = None):
        """Initialize the integration layer"""
        if project_dir is None:
            project_dir = os.getcwd()
        
        if project_name is None:
            project_name = Path(project_dir).name
        
        self.project_dir = Path(project_dir)
        self.project_name = project_name
        
        # Initialize library and project manager
        self.library = BucketLibrary()
        self.project_manager = ProjectLightRAGManager(project_dir, project_name, self.library)
        
        # Initialize existing LightRAG manager for compatibility
        self.lightrag_manager = LightRAGManager(
            base_dir=str(self.project_manager.lightrag_dir)
        )
        
        # Map of bucket IDs to LightRAG instances
        self.active_instances = {}
        
    def migrate_existing_buckets(self) -> Dict:
        """Migrate existing buckets to the library system"""
        results = {
            "migrated": [],
            "failed": [],
            "skipped": []
        }
        
        # Check for existing buckets in old structure
        old_base_dir = self.project_dir / "lightrag_working_dir"
        
        if old_base_dir.exists():
            for bucket_dir in old_base_dir.iterdir():
                if bucket_dir.is_dir() and bucket_dir.name not in ["imported", "local"]:
                    try:
                        # Create bucket in library
                        result = self.library.create_bucket(
                            bucket_name=bucket_dir.name,
                            project_name=self.project_name,
                            description=f"Migrated from {self.project_name}"
                        )
                        
                        if result["success"]:
                            bucket_id = result["bucket_id"]
                            library_path = Path(result["path"])
                            
                            # Copy bucket contents
                            import shutil
                            for item in bucket_dir.iterdir():
                                if item.is_dir():
                                    shutil.copytree(item, library_path / item.name, dirs_exist_ok=True)
                                else:
                                    shutil.copy2(item, library_path / item.name)
                            
                            # Import to project
                            self.project_manager.import_from_library(bucket_id)
                            
                            results["migrated"].append({
                                "original": bucket_dir.name,
                                "bucket_id": bucket_id
                            })
                        else:
                            results["failed"].append({
                                "bucket": bucket_dir.name,
                                "error": result.get("error")
                            })
                    except Exception as e:
                        results["failed"].append({
                            "bucket": bucket_dir.name,
                            "error": str(e)
                        })
        
        return results
    
    def create_bucket(self, bucket_name: str, description: str = "", 
                     scope: str = "library") -> Dict:
        """Create a new bucket (library or local)"""
        if scope == "library":
            # Create in library and import to project
            result = self.library.create_bucket(bucket_name, self.project_name, description)
            if result["success"]:
                bucket_id = result["bucket_id"]
                self.project_manager.import_from_library(bucket_id)
                self._initialize_lightrag_instance(bucket_id, result["path"])
            return result
        else:
            # Create local bucket
            result = self.project_manager.create_local_bucket(bucket_name, description)
            if result["success"]:
                self._initialize_lightrag_instance(bucket_name, result["path"])
            return result
    
    def _initialize_lightrag_instance(self, bucket_id: str, bucket_path: str):
        """Initialize a LightRAG instance for a bucket"""
        rag = LightRAG(
            working_dir=bucket_path,
            embedding_func=openai_embed,
            llm_model_func=gpt_4o_mini_complete
        )
        
        # Initialize storages
        async def init_rag():
            await rag.initialize_storages()
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(init_rag())
        self.active_instances[bucket_id] = rag
    
    def get_bucket_instance(self, bucket_identifier: str) -> Optional[LightRAG]:
        """Get or create a LightRAG instance for a bucket"""
        if bucket_identifier not in self.active_instances:
            # Try to load the bucket
            bucket_info = self.library.get_bucket_info(bucket_identifier)
            if bucket_info:
                self._initialize_lightrag_instance(
                    bucket_identifier, 
                    bucket_info["storage"]["path"]
                )
            else:
                # Check if it's a local bucket
                local_path = self.project_manager.local_dir / bucket_identifier
                if local_path.exists():
                    self._initialize_lightrag_instance(bucket_identifier, str(local_path))
                else:
                    return None
        
        return self.active_instances.get(bucket_identifier)
    
    def add_document_to_bucket(self, bucket_identifier: str, document: str, 
                              metadata: Dict = None) -> Dict:
        """Add a document to a bucket"""
        rag = self.get_bucket_instance(bucket_identifier)
        if not rag:
            return {"success": False, "error": f"Bucket {bucket_identifier} not found"}
        
        try:
            # Use async insert
            async def insert_doc():
                await rag.ainsert(document)
            
            loop = asyncio.get_event_loop() if asyncio.get_event_loop().is_running() else asyncio.new_event_loop()
            loop.run_until_complete(insert_doc())
            
            return {"success": True, "message": "Document added successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def query_bucket(self, bucket_identifier: str, query: str, 
                    mode: str = "hybrid") -> Dict:
        """Query a bucket"""
        rag = self.get_bucket_instance(bucket_identifier)
        if not rag:
            return {"success": False, "error": f"Bucket {bucket_identifier} not found"}
        
        try:
            param = QueryParam(mode=mode)
            
            async def run_query():
                return await rag.aquery(query, param=param)
            
            loop = asyncio.get_event_loop() if asyncio.get_event_loop().is_running() else asyncio.new_event_loop()
            result = loop.run_until_complete(run_query())
            
            return {
                "success": True,
                "result": result,
                "mode": mode,
                "bucket": bucket_identifier
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_available_buckets(self) -> Dict:
        """List all buckets available to the project"""
        project_buckets = self.project_manager.list_all_buckets()
        library_buckets = self.library.list_library_buckets()
        
        # Find library buckets not yet imported
        imported_ids = set(b.get("id") for b in project_buckets["imported"])
        available_for_import = [
            b for b in library_buckets 
            if b["id"] not in imported_ids
        ]
        
        return {
            "project": project_buckets,
            "library": {
                "imported": project_buckets["imported"],
                "available": available_for_import,
                "total": len(library_buckets)
            }
        }
    
    def share_bucket_with_project(self, bucket_identifier: str, 
                                 target_project: str) -> Dict:
        """Share a bucket with another project"""
        return self.library.share_bucket_between_projects(
            bucket_identifier, 
            self.project_name, 
            target_project
        )
    
    def export_bucket(self, bucket_identifier: str, export_path: str) -> Dict:
        """Export a bucket to an external location"""
        return self.library.export_bucket(bucket_identifier, export_path)
    
    def promote_local_bucket(self, local_bucket_name: str, 
                           description: str = "") -> Dict:
        """Promote a local bucket to the library"""
        return self.project_manager.promote_to_library(local_bucket_name, description)
    
    def get_library_dashboard(self) -> Dict:
        """Get comprehensive dashboard data"""
        return {
            "library_stats": self.library.get_library_stats(),
            "project_buckets": self.project_manager.list_all_buckets(),
            "active_buckets": self.project_manager.get_active_buckets(),
            "project_name": self.project_name,
            "project_dir": str(self.project_dir)
        }
    
    def search_library(self, query: str) -> List[Dict]:
        """Search the library for buckets"""
        return self.library.search_buckets(query)
    
    def batch_import_buckets(self, bucket_ids: List[str]) -> Dict:
        """Import multiple buckets from the library"""
        results = {
            "imported": [],
            "failed": []
        }
        
        for bucket_id in bucket_ids:
            result = self.project_manager.import_from_library(bucket_id)
            if result["success"]:
                results["imported"].append(bucket_id)
            else:
                results["failed"].append({
                    "bucket_id": bucket_id,
                    "error": result.get("error")
                })
        
        return results
    
    def synchronize_bucket(self, bucket_identifier: str) -> Dict:
        """Synchronize a bucket between library and project"""
        # This ensures the bucket is up to date in both locations
        bucket_info = self.library.get_bucket_info(bucket_identifier)
        if not bucket_info:
            return {"success": False, "error": "Bucket not found in library"}
        
        # Re-import to ensure sync
        return self.project_manager.import_from_library(bucket_identifier)