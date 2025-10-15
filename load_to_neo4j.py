"""
load_to_neo4j.py

This script connects to Neo4j and loads travel data (cities, connections)
into a knowledge graph.

Nodes:
- City

Relationships:
- (City)-[:CONNECTED_TO]->(City)
"""

import json
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, DATA_FILE


# CONNECT TO NEO4J DATABASE 
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


# FUNCTION: LOAD JSON DATA 
def load_data():
    """Read the Vietnam travel dataset JSON file."""
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


#  FUNCTION: CREATE NODES AND RELATIONSHIPS 
def load_to_neo4j(tx, data):
    """
    - Batch create City nodes with properties
    - Create :CONNECTED_TO relationships based on connections
    """

    # Create city nodes in batch
    tx.run(
        """
        UNWIND $cities AS city
        MERGE (c:City {name: city.name})
        SET c.description = city.description,
            c.region = city.region,
            c.best_time_to_visit = city.best_time_to_visit,
            c.tags = city.tags,
            c.semantic_text = city.semantic_text
        """,
        cities=data,
    )

    # Create id -> name map for looking up target city names in connections
    id_name_map = {city['id']: city['name'] for city in data}

    # Create city connections relationships
    for city in data:
        city_name = city['name']
        for connection in city.get('connections', []):
            target_id = connection['target']
            relation = connection['relation'].upper()  # e.g. "CONNECTED_TO"
            target_name = id_name_map.get(target_id)

            if target_name:
                # Use parameterized query to prevent injection and allow reuse
                tx.run(
                    f"""
                    MATCH (c1:City {{name: $city_name}})
                    MATCH (c2:City {{name: $target_name}})
                    MERGE (c1)-[r:{relation}]->(c2)
                    """,
                    city_name=city_name,
                    target_name=target_name,
                )


#  MAIN FUNCTION 
def main():
    data = load_data()
    try:
        with driver.session() as session:
            session.execute_write(load_to_neo4j, data)
        print("Data successfully loaded into Neo4j!")
    except Exception as e:
        print(f"Failed to load data into Neo4j: {e}")
    finally:
        driver.close()


#  SCRIPT ENTRY POINT 
if __name__ == "__main__":
    main()
