#!/usr/bin/env python3
"""
Test the fixed bucket statistics display
"""

from lizzy_lightrag_manager import LightRAGManager, BucketInterface

print("=" * 80)
print("TESTING FIXED BUCKET STATISTICS")
print("=" * 80)

# Initialize manager
manager = LightRAGManager(base_dir="lightrag_working_dir")

# Load configuration
manager.load_bucket_config()

# Create interface and display status
interface = BucketInterface(manager)
interface.display_bucket_status()

print("\nThe statistics should now show the actual counts!")
print("Compare with expected values:")
print("\n📚 Key buckets with data:")
print("  • shakespeare_plays: 8,665 entities, 7,257 relations")
print("  • screenwriting_books: 9,896 entities, 6,131 relations")
print("  • reference_sources: 21,012 entities, 22,000 relations")