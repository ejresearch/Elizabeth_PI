#!/usr/bin/env python3
"""
Interactive Graph Visualizer for LightRAG Knowledge Graphs
Creates both static PNG and interactive HTML visualizations
"""

import os
import json
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import random
from networkx.algorithms import community
import colorsys
import tempfile

def create_interactive_graph(bucket_name: str, base_dir: str = "lightrag_working_dir", max_nodes: int = 100):
    """Create an interactive HTML visualization of the knowledge graph with enhanced features"""
    
    bucket_dir = os.path.join(base_dir, bucket_name)
    graphml_file = os.path.join(bucket_dir, "graph_chunk_entity_relation.graphml")
    
    if not os.path.exists(graphml_file):
        print(f"❌ No graph file found for {bucket_name}")
        return None
    
    # Load the graph
    G = nx.read_graphml(graphml_file)
    print(f"📊 Loaded graph with {len(G.nodes())} nodes and {len(G.edges())} edges")
    
    # Detect communities for better coloring
    try:
        communities_list = list(community.greedy_modularity_communities(G.to_undirected()))
        community_map = {}
        for i, comm in enumerate(communities_list):
            for node in comm:
                community_map[node] = i
        print(f"🎨 Detected {len(communities_list)} communities")
    except:
        community_map = {node: 0 for node in G.nodes()}
    
    # If graph is too large, get the most connected subgraph
    if len(G.nodes()) > max_nodes:
        print(f"📉 Reducing to top {max_nodes} most connected nodes...")
        node_degrees = dict(G.degree())
        top_nodes = sorted(node_degrees.items(), key=lambda x: x[1], reverse=True)[:max_nodes]
        top_node_ids = [node[0] for node in top_nodes]
        G = G.subgraph(top_node_ids).copy()
    
    # Create Pyvis network with enhanced settings
    net = Network(
        height="900px", 
        width="100%", 
        bgcolor="#1a1a2e", 
        font_color="#eee",
        notebook=False,
        cdn_resources='remote',
        select_menu=True,
        filter_menu=True
    )
    net.barnes_hut(gravity=-80000, central_gravity=0.3, spring_length=250, spring_strength=0.001, damping=0.09)
    
    # Generate colors for communities
    num_communities = len(set(community_map.values()))
    community_colors = {}
    for i in range(num_communities):
        hue = i / max(1, num_communities - 1)
        rgb = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
        color = '#{:02x}{:02x}{:02x}'.format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        community_colors[i] = color
    
    # Calculate centrality metrics for better insights
    betweenness = nx.betweenness_centrality(G)
    closeness = nx.closeness_centrality(G)
    pagerank = nx.pagerank(G)
    
    # Add nodes with enhanced styling and information
    degrees = dict(G.degree())
    for node in G.nodes():
        # Size based on PageRank (importance)
        size = min(15 + pagerank[node] * 500, 60)
        
        # Color based on community
        comm_id = community_map.get(node, 0)
        color = community_colors.get(comm_id, "#4ecdc4")
        
        # Add border color based on degree
        if degrees[node] > 10:
            border_color = "#ff6b6b"  # Red border for highly connected
            border_width = 3
        elif degrees[node] > 5:
            border_color = "#ffd93d"  # Yellow border for medium connected
            border_width = 2
        else:
            border_color = color  # Same as node color
            border_width = 1
        
        # Clean label
        label = str(node).replace('_', ' ').title()
        short_label = label[:25] + '...' if len(label) > 25 else label
        
        # Create detailed hover information
        hover_info = f"""<b>{label}</b><br>
        Community: {comm_id + 1}<br>
        Connections: {degrees[node]}<br>
        Betweenness: {betweenness[node]:.3f}<br>
        Closeness: {closeness[node]:.3f}<br>
        PageRank: {pagerank[node]:.4f}
        """
        
        # Get connected nodes for context
        neighbors = list(G.neighbors(node))
        if neighbors:
            neighbor_names = [str(n).replace('_', ' ').title() for n in neighbors[:5]]
            hover_info += f"<br><br><b>Connected to:</b><br>{'<br>'.join(neighbor_names)}"
            if len(neighbors) > 5:
                hover_info += f"<br>...and {len(neighbors) - 5} more"
        
        net.add_node(
            node, 
            label=short_label,
            size=size,
            color=color,
            borderWidth=border_width,
            borderWidthSelected=border_width + 2,
            title=hover_info,
            group=comm_id,
            value=degrees[node],
            physics=True
        )
    
    # Add edges with weights and labels if available
    for edge in G.edges(data=True):
        source, target = edge[0], edge[1]
        edge_data = edge[2]
        
        # Get edge weight or relationship type if available
        weight = edge_data.get('weight', 1)
        relation = edge_data.get('relation', '')
        
        # Style edges based on weight
        if weight > 2:
            edge_color = "#ff6b6b"
            edge_width = 2
        elif weight > 1:
            edge_color = "#888888"
            edge_width = 1
        else:
            edge_color = "#444444"
            edge_width = 0.5
        
        # Add edge with hover information
        edge_title = f"Weight: {weight}"
        if relation:
            edge_title = f"Relation: {relation}\n{edge_title}"
        
        net.add_edge(
            source, 
            target, 
            color=edge_color, 
            width=edge_width,
            title=edge_title,
            smooth={'type': 'curvedCW', 'roundness': 0.1}
        )
    
    # Set enhanced physics and interaction options with JSON string
    net.toggle_physics(True)
    net.show_buttons(filter_=['physics', 'interaction', 'layout'])
    net.set_edge_smooth('dynamic')
    
    
    # Save the interactive graph
    output_file = os.path.join(base_dir, f"{bucket_name}_interactive.html")
    net.save_graph(output_file)
    
    # Add custom search functionality to the HTML
    with open(output_file, 'r') as f:
        html_content = f.read()
    
    # Insert custom controls before </body>
    custom_html = f'''
    <div style="position: fixed; top: 10px; right: 10px; z-index: 1000; background: rgba(26,26,46,0.95); padding: 15px; border-radius: 8px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <h3 style="margin-top: 0; color: #4ecdc4;">🔍 Graph Explorer</h3>
        <input type="text" id="nodeSearch" placeholder="Search nodes..." style="padding: 8px; margin-bottom: 10px; width: 250px; border-radius: 4px; border: 1px solid #4ecdc4; background: #2a2a3e; color: white;">
        <br>
        <button onclick="searchNode()" style="padding: 8px 15px; background: #4ecdc4; color: #1a1a2e; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">Search</button>
        <button onclick="resetGraph()" style="padding: 8px 15px; background: #ff6b6b; color: white; border: none; border-radius: 4px; cursor: pointer; margin-left: 5px; font-weight: bold;">Reset</button>
        <button onclick="fitGraph()" style="padding: 8px 15px; background: #95e1d3; color: #1a1a2e; border: none; border-radius: 4px; cursor: pointer; margin-left: 5px; font-weight: bold;">Fit All</button>
        <hr style="border-color: #4ecdc4; margin: 15px 0;">
        <div id="graphStats" style="font-size: 13px; line-height: 1.6;">
            <b>Statistics:</b><br>
            Nodes: {len(G.nodes())}<br>
            Edges: {len(G.edges())}<br>
            Communities: {len(set(community_map.values()))}<br>
        </div>
        <hr style="border-color: #4ecdc4; margin: 15px 0;">
        <div style="font-size: 11px; color: #aaa;">
            <b>Shortcuts:</b><br>
            • Click & drag to pan<br>
            • Scroll to zoom<br>
            • Click node to select<br>
            • Ctrl+Click for multi-select<br>
        </div>
    </div>
    <script>
        function searchNode() {{
            var searchTerm = document.getElementById('nodeSearch').value.toLowerCase();
            if (searchTerm) {{
                var nodeIds = network.body.data.nodes.getIds();
                var matchingNodes = [];
                nodeIds.forEach(function(id) {{
                    var node = network.body.data.nodes.get(id);
                    if (node.label.toLowerCase().includes(searchTerm)) {{
                        matchingNodes.push(id);
                    }}
                }});
                if (matchingNodes.length > 0) {{
                    network.selectNodes(matchingNodes, true);
                    if (matchingNodes.length === 1) {{
                        network.focus(matchingNodes[0], {{scale: 1.5, animation: true}});
                    }} else {{
                        network.fit({{nodes: matchingNodes, animation: true}});
                    }}
                    console.log('Found ' + matchingNodes.length + ' matching nodes');
                }} else {{
                    alert('No nodes found matching: ' + searchTerm);
                }}
            }}
        }}
        
        function resetGraph() {{
            network.fit({{animation: true}});
            network.unselectAll();
            document.getElementById('nodeSearch').value = '';
        }}
        
        function fitGraph() {{
            network.fit({{animation: true}});
        }}
        
        // Enter key triggers search
        document.getElementById('nodeSearch').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                searchNode();
            }}
        }});
        
        // Focus search on page load
        window.addEventListener('load', function() {{
            document.getElementById('nodeSearch').focus();
        }});
    </script>
    '''
    
    html_content = html_content.replace('</body>', custom_html + '</body>')
    
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"✅ Enhanced interactive graph saved to: {output_file}")
    print(f"   📊 Graph: {len(G.nodes())} nodes, {len(G.edges())} edges, {len(set(community_map.values()))} communities")
    print(f"   ✨ Features: Search, Navigation, Community coloring, Hover details, Control panel")
    print(f"   🎮 Interactive: Click to select, Ctrl+Click to multi-select, Scroll to zoom")
    
    return output_file

def visualize_bucket_comparison(bucket_names: list, base_dir: str = "lightrag_working_dir"):
    """Compare multiple buckets by visualizing their key entities"""
    
    bucket_stats = {}
    
    for bucket in bucket_names:
        bucket_dir = os.path.join(base_dir, bucket)
        graphml_file = os.path.join(bucket_dir, "graph_chunk_entity_relation.graphml")
        
        if os.path.exists(graphml_file):
            G = nx.read_graphml(graphml_file)
            degrees = dict(G.degree())
            
            # Get top 10 entities
            top_entities = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]
            
            bucket_stats[bucket] = {
                "total_nodes": len(G.nodes()),
                "total_edges": len(G.edges()),
                "top_entities": [entity[0].replace('_', ' ').title() for entity in top_entities],
                "avg_degree": sum(degrees.values()) / len(degrees) if degrees else 0
            }
    
    # Create comparison visualization
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Knowledge Bucket Comparison", fontsize=16, fontweight='bold')
    
    # Plot 1: Node and Edge counts
    ax1 = axes[0, 0]
    buckets = list(bucket_stats.keys())
    nodes = [bucket_stats[b]["total_nodes"] for b in buckets]
    edges = [bucket_stats[b]["total_edges"] for b in buckets]
    
    x = range(len(buckets))
    width = 0.35
    ax1.bar([i - width/2 for i in x], nodes, width, label='Nodes', color='skyblue')
    ax1.bar([i + width/2 for i in x], edges, width, label='Edges', color='lightcoral')
    ax1.set_xticks(x)
    ax1.set_xticklabels(buckets, rotation=45, ha='right')
    ax1.set_ylabel('Count')
    ax1.set_title('Graph Size Comparison')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Average Degree
    ax2 = axes[0, 1]
    avg_degrees = [bucket_stats[b]["avg_degree"] for b in buckets]
    ax2.bar(buckets, avg_degrees, color='lightgreen')
    ax2.set_xticklabels(buckets, rotation=45, ha='right')
    ax2.set_ylabel('Average Degree')
    ax2.set_title('Graph Connectivity')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3 & 4: Top Entities
    for idx, (bucket, stats) in enumerate(list(bucket_stats.items())[:2]):
        ax = axes[1, idx]
        top_5 = stats["top_entities"][:5]
        ax.text(0.1, 0.9, f"{bucket}", fontsize=14, fontweight='bold', transform=ax.transAxes)
        for i, entity in enumerate(top_5):
            ax.text(0.1, 0.7 - i*0.15, f"{i+1}. {entity}", fontsize=10, transform=ax.transAxes)
        ax.axis('off')
        ax.set_title('Top Connected Entities')
    
    plt.tight_layout()
    
    # Save comparison
    output_file = os.path.join(base_dir, "bucket_comparison.png")
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Bucket comparison saved to: {output_file}")
    return output_file

def create_multi_graph_explorer(bucket_names: list, base_dir: str = "lightrag_working_dir", max_nodes_each: int = 30):
    """Create an interactive HTML page with multiple graphs side by side"""
    
    if not bucket_names:
        print("❌ No buckets specified for multi-graph explorer")
        return None
    
    print(f"🔄 Creating multi-graph explorer for {len(bucket_names)} buckets...")
    
    # Create individual graphs and collect their data
    graphs_data = []
    for bucket_name in bucket_names:
        bucket_dir = os.path.join(base_dir, bucket_name)
        graphml_file = os.path.join(bucket_dir, "graph_chunk_entity_relation.graphml")
        
        if not os.path.exists(graphml_file):
            print(f"⚠️ No graph file found for {bucket_name}, skipping...")
            continue
        
        try:
            # Load graph
            G = nx.read_graphml(graphml_file)
            print(f"📊 {bucket_name}: {len(G.nodes())} nodes, {len(G.edges())} edges")
            
            # Reduce to top connected nodes
            if len(G.nodes()) > max_nodes_each:
                node_degrees = dict(G.degree())
                top_nodes = sorted(node_degrees.items(), key=lambda x: x[1], reverse=True)[:max_nodes_each]
                top_node_ids = [node[0] for node in top_nodes]
                G = G.subgraph(top_node_ids).copy()
            
            # Community detection
            try:
                communities_list = list(community.greedy_modularity_communities(G.to_undirected()))
                community_map = {node: i for i, comm in enumerate(communities_list) for node in comm}
            except:
                community_map = {node: 0 for node in G.nodes()}
            
            # Calculate metrics
            degrees = dict(G.degree())
            betweenness = nx.betweenness_centrality(G)
            pagerank = nx.pagerank(G)
            
            graphs_data.append({
                'name': bucket_name,
                'graph': G,
                'communities': community_map,
                'degrees': degrees,
                'betweenness': betweenness,
                'pagerank': pagerank,
                'num_communities': len(set(community_map.values()))
            })
            
        except Exception as e:
            print(f"❌ Error loading {bucket_name}: {e}")
            continue
    
    if not graphs_data:
        print("❌ No valid graphs found")
        return None
    
    # Create multi-graph HTML
    output_file = os.path.join(base_dir, "multi_graph_explorer.html")
    
    html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Multi-Graph Knowledge Explorer</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', sans-serif;
            margin: 0;
            padding: 20px;
            background: #1a1a2e;
            color: white;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
        }}
        .graphs-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .graph-panel {{
            background: rgba(26,26,46,0.95);
            border-radius: 10px;
            border: 2px solid #4ecdc4;
            overflow: hidden;
        }}
        .graph-header {{
            background: #4ecdc4;
            color: #1a1a2e;
            padding: 15px;
            font-weight: bold;
            font-size: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .graph-viz {{
            height: 400px;
            position: relative;
        }}
        .graph-stats {{
            padding: 15px;
            font-size: 13px;
            background: rgba(78,205,196,0.1);
            border-top: 1px solid #4ecdc4;
        }}
        .controls {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(26,26,46,0.95);
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #4ecdc4;
            z-index: 1000;
            min-width: 250px;
        }}
        .controls h3 {{
            margin-top: 0;
            color: #4ecdc4;
        }}
        .control-group {{
            margin-bottom: 15px;
        }}
        .control-group label {{
            display: block;
            margin-bottom: 5px;
            font-size: 12px;
        }}
        .control-group input, .control-group select {{
            width: 100%;
            padding: 5px;
            border: 1px solid #4ecdc4;
            background: #2a2a3e;
            color: white;
            border-radius: 3px;
        }}
        .btn {{
            padding: 8px 15px;
            background: #4ecdc4;
            color: #1a1a2e;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            margin: 2px;
        }}
        .btn:hover {{ background: #45b7aa; }}
        .btn-secondary {{
            background: #ff6b6b;
            color: white;
        }}
        .btn-secondary:hover {{ background: #e55555; }}
        .comparison-stats {{
            background: rgba(26,26,46,0.95);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #4ecdc4;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Multi-Graph Knowledge Explorer</h1>
        <p>Comparing {len(graphs_data)} Knowledge Graphs</p>
    </div>
    
    <div class="controls">
        <h3>🎮 Global Controls</h3>
        <div class="control-group">
            <label>Search Across All Graphs:</label>
            <input type="text" id="globalSearch" placeholder="Enter search term...">
            <button class="btn" onclick="searchAllGraphs()">Search</button>
            <button class="btn btn-secondary" onclick="resetAllGraphs()">Reset</button>
        </div>
        <div class="control-group">
            <label>Sync Navigation:</label>
            <button class="btn" onclick="fitAllGraphs()">Fit All</button>
            <button class="btn" onclick="togglePhysics()">Toggle Physics</button>
        </div>
        <div class="control-group">
            <label>Compare Mode:</label>
            <button class="btn" onclick="highlightCommonNodes()">Show Common</button>
            <button class="btn" onclick="showUniqueNodes()">Show Unique</button>
        </div>
    </div>
    
    <div class="graphs-container">
'''
    
    # Add each graph
    for i, graph_data in enumerate(graphs_data):
        bucket_name = graph_data['name']
        G = graph_data['graph']
        community_map = graph_data['communities']
        degrees = graph_data['degrees']
        pagerank = graph_data['pagerank']
        num_communities = graph_data['num_communities']
        
        html_content += f'''
        <div class="graph-panel">
            <div class="graph-header">
                <span>📊 {bucket_name}</span>
                <span>{len(G.nodes())} nodes • {len(G.edges())} edges</span>
            </div>
            <div id="graph{i}" class="graph-viz"></div>
            <div class="graph-stats">
                <strong>Statistics:</strong><br>
                Communities: {num_communities}<br>
                Density: {nx.density(G):.3f}<br>
                Avg Degree: {sum(degrees.values()) / len(degrees):.1f}<br>
                Most Connected: {max(degrees.keys(), key=lambda x: degrees[x]) if degrees else 'None'}
            </div>
        </div>
        '''
    
    html_content += '''
    </div>
    
    <div class="comparison-stats">
        <h3>📈 Cross-Graph Analysis</h3>
        <div id="comparisonContent">
            <p>Use the controls above to analyze relationships between graphs.</p>
        </div>
    </div>
    
    <script>
        let networks = [];
        let graphsData = [];
        let physicsEnabled = true;
        
        // Initialize all graphs
        function initializeGraphs() {
    '''
    
    # Add JavaScript for each graph
    for i, graph_data in enumerate(graphs_data):
        G = graph_data['graph']
        community_map = graph_data['communities']
        degrees = graph_data['degrees']
        pagerank = graph_data['pagerank']
        
        # Generate colors for communities
        num_communities = len(set(community_map.values()))
        
        nodes_js = []
        edges_js = []
        
        # Add nodes
        for node in G.nodes():
            comm_id = community_map.get(node, 0)
            hue = (comm_id * 137.5) % 360  # Golden ratio spacing
            size = min(15 + pagerank[node] * 300, 50)
            
            label = str(node).replace('_', ' ').title()
            short_label = label[:20] + '...' if len(label) > 20 else label
            
            nodes_js.append({
                'id': node,
                'label': short_label,
                'size': size,
                'color': f'hsl({hue}, 70%, 60%)',
                'title': f"{label}<br>Connections: {degrees[node]}<br>PageRank: {pagerank[node]:.4f}<br>Community: {comm_id}",
                'group': comm_id
            })
        
        # Add edges
        for source, target in G.edges():
            edges_js.append({
                'from': source,
                'to': target,
                'color': '#444444',
                'width': 1
            })
        
        html_content += f'''
            // Graph {i}: {graph_data['name']}
            let nodes{i} = new vis.DataSet({json.dumps(nodes_js)});
            let edges{i} = new vis.DataSet({json.dumps(edges_js)});
            let data{i} = {{nodes: nodes{i}, edges: edges{i}}};
            
            let options{i} = {{
                nodes: {{
                    borderWidth: 2,
                    font: {{size: 12, color: 'white'}},
                    shadow: true
                }},
                edges: {{
                    smooth: true,
                    arrows: {{to: {{enabled: true, scaleFactor: 0.5}}}}
                }},
                physics: {{
                    enabled: true,
                    barnesHut: {{
                        gravitationalConstant: -20000,
                        centralGravity: 0.1,
                        springLength: 100,
                        springConstant: 0.04,
                        damping: 0.09
                    }}
                }},
                interaction: {{
                    hover: true,
                    selectConnectedEdges: true
                }}
            }};
            
            let network{i} = new vis.Network(document.getElementById('graph{i}'), data{i}, options{i});
            networks.push(network{i});
            graphsData.push({{
                name: '{graph_data['name']}',
                nodes: nodes{i},
                edges: edges{i},
                network: network{i}
            }});
        '''
    
    html_content += '''
        }
        
        // Global functions
        function searchAllGraphs() {
            let searchTerm = document.getElementById('globalSearch').value.toLowerCase();
            if (!searchTerm) return;
            
            let totalFound = 0;
            graphsData.forEach((graphData, index) => {
                let matchingNodes = [];
                graphData.nodes.forEach(node => {
                    if (node.label.toLowerCase().includes(searchTerm)) {
                        matchingNodes.push(node.id);
                    }
                });
                
                if (matchingNodes.length > 0) {
                    graphData.network.selectNodes(matchingNodes);
                    if (matchingNodes.length === 1) {
                        graphData.network.focus(matchingNodes[0], {scale: 1.5});
                    }
                    totalFound += matchingNodes.length;
                }
            });
            
            document.getElementById('comparisonContent').innerHTML = 
                `<p>Found <strong>${totalFound}</strong> nodes matching "${searchTerm}" across all graphs.</p>`;
        }
        
        function resetAllGraphs() {
            networks.forEach(network => {
                network.unselectAll();
                network.fit();
            });
            document.getElementById('globalSearch').value = '';
            document.getElementById('comparisonContent').innerHTML = 
                '<p>All graphs reset. Use controls above to analyze relationships.</p>';
        }
        
        function fitAllGraphs() {
            networks.forEach(network => network.fit({animation: true}));
        }
        
        function togglePhysics() {
            physicsEnabled = !physicsEnabled;
            networks.forEach(network => {
                network.setOptions({physics: {enabled: physicsEnabled}});
            });
        }
        
        function highlightCommonNodes() {
            // Find nodes that appear in multiple graphs
            let allNodes = new Set();
            let nodeCounts = {};
            
            graphsData.forEach(graphData => {
                graphData.nodes.forEach(node => {
                    let cleanLabel = node.label.toLowerCase().replace(/[^a-z0-9]/g, '');
                    allNodes.add(cleanLabel);
                    nodeCounts[cleanLabel] = (nodeCounts[cleanLabel] || 0) + 1;
                });
            });
            
            let commonNodes = Object.keys(nodeCounts).filter(node => nodeCounts[node] > 1);
            
            // Highlight common nodes in each graph
            let totalCommon = 0;
            graphsData.forEach(graphData => {
                let matchingIds = [];
                graphData.nodes.forEach(node => {
                    let cleanLabel = node.label.toLowerCase().replace(/[^a-z0-9]/g, '');
                    if (commonNodes.includes(cleanLabel)) {
                        matchingIds.push(node.id);
                    }
                });
                
                if (matchingIds.length > 0) {
                    graphData.network.selectNodes(matchingIds);
                    totalCommon += matchingIds.length;
                }
            });
            
            document.getElementById('comparisonContent').innerHTML = 
                `<p>Found <strong>${totalCommon}</strong> common nodes across graphs. <br>
                Common concepts: <strong>${commonNodes.length}</strong></p>`;
        }
        
        function showUniqueNodes() {
            // Logic for showing unique nodes would go here
            document.getElementById('comparisonContent').innerHTML = 
                '<p>Unique node analysis - feature coming soon!</p>';
        }
        
        // Initialize when page loads
        window.onload = function() {
            initializeGraphs();
            
            // Add keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                if (e.ctrlKey && e.key === 'f') {
                    e.preventDefault();
                    document.getElementById('globalSearch').focus();
                }
                if (e.key === 'Escape') {
                    resetAllGraphs();
                }
            });
        };
    </script>
</body>
</html>
    '''
    
    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Multi-graph explorer saved to: {output_file}")
    print(f"   📊 Graphs: {', '.join([g['name'] for g in graphs_data])}")
    print(f"   ✨ Features: Global search, sync navigation, common node detection")
    
    return output_file

def main():
    """Demo the graph visualizer"""
    print("=" * 80)
    print("GRAPH VISUALIZER DEMO")
    print("=" * 80)
    
    # Test with shakespeare_plays bucket
    print("\n📊 Creating interactive visualization for shakespeare_plays...")
    create_interactive_graph("shakespeare_plays", max_nodes=50)
    
    print("\n📊 Creating bucket comparison...")
    visualize_bucket_comparison(["shakespeare_plays", "screenwriting_books", "reference_sources"])
    
    print("\n🔍 Creating multi-graph explorer...")
    create_multi_graph_explorer(["shakespeare_plays", "romcom_scripts", "screenwriting_books"], max_nodes_each=25)
    
    print("\n✨ Visualizations complete!")
    print("Open the HTML files in your browser for interactive exploration.")

if __name__ == "__main__":
    main()