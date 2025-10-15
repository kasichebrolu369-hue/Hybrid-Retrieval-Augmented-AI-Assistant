import asyncio
import os
import pickle
import re
from neo4j import AsyncGraphDatabase
from pinecone import Pinecone
from openai import OpenAI 
from sentence_transformers import SentenceTransformer 
from config import (
    NEO4J_URI,
    NEO4J_USER,
    NEO4J_PASSWORD,
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    PINECONE_VECTOR_DIM,
    HF_API_TOKEN,
)

#          Initialize local sentence transformer

embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

                # Initialize external services

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)
neo4j_driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
hf_client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_API_TOKEN,
)

CACHE_FILE = "query_cache.pkl"

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f" Failed to load cache, ignoring: {e}")
    return {}

def save_cache(cache):
    try:
        with open(CACHE_FILE, "wb") as f:
            pickle.dump(cache, f)
    except Exception as e:
        print(f" Failed to save cache: {e}")

# Replaced Hugging Face embedding API call with local version
async def get_hf_embeddings(text):
    try:
        return await asyncio.to_thread(embedder.encode, text)
    except Exception as e:
        raise RuntimeError(f"Failed to generate embeddings locally: {e}")

async def query_pinecone(query, top_k=5):
    try:
        query_embedding = (await get_hf_embeddings(query)).tolist()  
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
            ),
        )
        matches = results.matches if hasattr(results, "matches") else []
        return [
            {
                "id": match.id,
                "text": match.metadata.get("text", "") if match.metadata else "",
                "score": match.score,
            }
            for match in matches
        ]
    except Exception as e:
        print(f" Pinecone query failed: {e}")
        return []

async def query_neo4j(city_names):
    try:
        async with neo4j_driver.session() as session:
            result = await session.run(
                """
                MATCH (c:City) WHERE c.name IN $city_names
                OPTIONAL MATCH (c)-[:CONNECTED_TO]->(related:City)
                RETURN c.name AS name, c.description AS description, c.region AS region,
                       c.best_time_to_visit AS best_time, c.tags AS tags,
                       collect(related.name) AS connected_cities
                """,
                city_names=city_names,
            )
            records = [record async for record in result]
            if not records:
                print("⚠️ Neo4j query returned no results.")
            return records
    except Exception as e:
        print(f" Neo4j query failed: {e}")
        return []

async def search_summary(pinecone_results):
    if not pinecone_results:
        return "No relevant travel information found."
    summary = "Relevant travel information:\n"
    for result in pinecone_results:
        summary += f"- {result['text']} (Score: {result['score']:.2f})\n"
    return summary.strip()

def extract_day_count(query):
    match = re.search(r"(\d+)[-\s]?day", query.lower())
    if match:
        return int(match.group(1))
    return 4

def extract_city_names(pinecone_results):
    city_names = set()
    known_cities = ["Hanoi", "Hoi An", "Ho Chi Minh", "Hue", "Da Nang", "Nha Trang"]
    for result in pinecone_results:
        text = result.get("text", "")
        for city in known_cities:
            if city.lower() in text.lower():
                city_names.add(city)
    if not city_names:
        city_names = {"Hanoi", "Hoi An"}
    return list(city_names)

async def generate_itinerary(query, pinecone_results, neo4j_results):
    pinecone_summary = await search_summary(pinecone_results)
    neo4j_context = "\n".join(
        [
            f"City: {r['name']}, Description: {r['description']}, Region: {r['region']}, "
            f"Best Time: {r['best_time']}, Tags: {', '.join(r.get('tags') or [])}, "
            f"Connected Cities: {', '.join(r['connected_cities']) if r['connected_cities'] else 'None'}"
            for r in neo4j_results
        ]
    ) if neo4j_results else "No city relationships found."

    day_count = extract_day_count(query)

    prompt = f"""
You are a skilled travel assistant specializing in creating romantic travel itineraries.

TASK: Create a detailed romantic itinerary for a trip to Vietnam lasting {day_count} days.

GUIDELINES:
- The itinerary should be clear and beautifully formatted using markdown.
- Organize the itinerary by days, each with a heading like "Day 1", "Day 2", etc.
- For each day, list 3-5 activities or recommendations using bullet points.
- Focus on romantic experiences, cultural highlights, dining, and nature.
- Write in an engaging, warm, and inviting tone.
- Use concise, vivid descriptions to help the user visualize the experience.
- Include tips on local culture, dining suggestions, and unique couple-friendly activities.
- Avoid unnecessary introductions or conclusions; focus on the itinerary content.
- Do not include any internal thought processes or planning steps in your output.

DATA:
Semantic Search Results: {pinecone_summary}
City Relationship Data: {neo4j_context}

If the data is incomplete, supplement with general recommendations for romantic travel in Vietnam.

Output the itinerary in markdown format with days and bullet points.
"""

    models = [
        "HuggingFaceTB/SmolLM3-3B:hf-inference",  #model 1
        "katanemo/Arch-Router-1.5B:hf-inference",  #model 2
    ]

    for model in models:
        try:
            completion = hf_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f" HF Inference API call failed for {model}: {e}")

    print(" All models failed. Returning fallback itinerary.")
    return f"""
# Romantic {day_count}-Day Itinerary for Vietnam

**Day 1: Hanoi - Romantic City Exploration**
- Morning: Stroll around Hoan Kiem Lake.
- Afternoon: Visit the Temple of Literature.
- Evening: Rooftop dinner in the Old Quarter.

**Day 2: Ha Long Bay - Scenic Cruise**
- Morning: Board a luxury cruise.
- Afternoon: Explore caves and emerald waters.
- Evening: Sunset dinner on deck.

**Day 3: Hoi An - Charming Ancient Town**
- Morning: Explore lantern-lit streets.
- Afternoon: Boat ride on Thu Bon River.
- Evening: Riverside local cuisine.

**Day 4: Ho Chi Minh City - Vibrant Romance**
- Morning: Notre-Dame Basilica visit.
- Afternoon: Couple's spa.
- Evening: Rooftop cocktails with city views.
"""[:1000]

async def process_query(query):
    cache = load_cache()
    if query in cache:
        print(" Retrieved from cache.")
        return cache[query]

    pinecone_results = await query_pinecone(query)
    city_names = extract_city_names(pinecone_results)
    neo4j_results = await query_neo4j(city_names)
    response = await generate_itinerary(query, pinecone_results, neo4j_results)

    cache[query] = response
    save_cache(cache)

    return response

async def main():
    print(" Welcome to the Vietnam Travel Assistant!")
    print("Type 'exit' to quit.")

    # Check Pinecone index status synchronously
    try:
        loop = asyncio.get_event_loop()
        stats = await loop.run_in_executor(None, index.describe_index_stats)
        if stats.dimension != PINECONE_VECTOR_DIM:
            raise ValueError(
                f"Index dimension {stats.dimension} does not match expected {PINECONE_VECTOR_DIM}"
            )
        print(f" Pinecone index '{PINECONE_INDEX_NAME}' is ready.")
    except Exception as e:
        print(f"Pinecone index error: {e}")
        return

    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
        print("Cache cleared successfully.")
    else:
        print(" No cache file found, starting fresh.")

    while True:
        query = input("Enter your travel question: ").strip()
        if query.lower() == "exit":
            break
        try:
            response = await process_query(query)
            print("\n Itinerary:")
            print(response)
            print("\n")
        except Exception as e:
            print(f" Error during processing: {e}")

    await neo4j_driver.close()

if __name__ == "__main__":
    asyncio.run(main())
