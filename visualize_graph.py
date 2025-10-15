"""'
visualize_graph.py


This script visualizes the travel graph stored in Neo4j.
It fetches City nodes and CONNECTED_TO relationships,
then uses NetworkX + PyVis to render an interactive HTML graph.
"""

from neo4j import GraphDatabase
import networkx as nx
from pyvis.network import Network
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

# ========== CONNECT TO NEO4J ==========
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


# ========== FUNCTION: FETCH GRAPH DATA ==========
def fetch_graph_data(tx):
    """
    Retrieve all City nodes and their CONNECTED_TO relationships.
    Returns list of (city1, city2) tuples.
    """
    query = """
    MATCH (c1:City)-[:CONNECTED_TO]->(c2:City)
    RETURN c1.name AS city1, c2.name AS city2
    """
    results = tx.run(query)
    return [(r["city1"], r["city2"]) for r in results]


# ========== FUNCTION: BUILD NETWORKX GRAPH ==========
def build_graph(edges):
    """
    Create a NetworkX graph from Neo4j city connections.
    Cities = blue nodes
    """
    G = nx.Graph()
    for city1, city2 in edges:
        G.add_node(city1, label=city1, color="#1f78b4")  # Blue for city
        G.add_node(city2, label=city2, color="#1f78b4")  # Blue for city
        G.add_edge(city1, city2)
    return G


# ========== FUNCTION: VISUALIZE USING PYVIS ==========
def visualize_graph(G, output_file="city_graph.html"):
    """
    Convert NetworkX graph to interactive PyVis visualization.
    Saves to HTML for browser viewing.
    """
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black", notebook=False)
    net.from_nx(G)
    net.force_atlas_2based()  # force-directed layout
    net.show(output_file)
    print(f"Graph visualization saved to: {output_file}")


# ========== MAIN ==========
def main():
    with driver.session() as session:
        edges = session.execute_read(fetch_graph_data)
        print(f"Fetched {len(edges)} city connections from Neo4j.")

        if not edges:
            print("No city relationships found. Please run load_to_neo4j.py first.")
            return

        G = build_graph(edges)
        visualize_graph(G)


# ========== SCRIPT ENTRY ==========
if __name__ == "__main__":
    main()
    driver.close()
