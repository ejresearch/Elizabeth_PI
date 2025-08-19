#!/usr/bin/env python3
"""
Test the graph visualization
"""

from lizzy_lightrag_manager import LightRAGManager

print("=" * 80)
print("TESTING GRAPH VISUALIZATION")
print("=" * 80)

# Initialize manager
manager = LightRAGManager(base_dir="lightrag_working_dir")
manager.load_bucket_config()

# Test visualization with a bucket that has data
print("\n📊 Visualizing shakespeare_plays knowledge graph...")
viz_file = manager.visualize_knowledge_graph("shakespeare_plays", max_nodes=30)

if viz_file:
    print(f"✅ Success! Graph saved to: {viz_file}")
    print(f"\n📌 You can open this file to see the knowledge graph visualization")
    print(f"   It shows the top 30 most connected entities from Shakespeare's plays")
else:
    print("❌ Visualization failed")

print("\n" + "=" * 80)
print("GRAPH FEATURES:")
print("=" * 80)
print("""
The visualization shows:
• Nodes = Entities (characters, concepts, locations)
• Node size = Number of connections (bigger = more connected)
• Node colors = Different connected components
• Edges = Relationships between entities
• Labels = Names of highly connected entities

This helps you understand the knowledge structure and find
key concepts that can inspire your writing!
""")