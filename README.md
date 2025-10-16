Hybrid AI Travel Assistant 
--------------------------------------------------
Overview

This project implements a Hybrid Knowledge AI System that generates contextual, multi-day travel itineraries for Vietnam using a combination of graph reasoning (Neo4j), semantic search (Pinecone), and language generation (Hugging Face models).

The assistant retrieves relevant travel nodes, enriches them with graph relations, and composes structured natural language responses — demonstrating a full Retrieval-Augmented Generation (RAG) pipeline.
_______________________
🧩 Core Components
Module	Description:

1.Neo4j (Docker)	Graph database for storing and querying relationships between cities and destinations.

2.Pinecone	Vector database for semantic text search using dense embeddings.

3.SentenceTransformer	Local embedding model (all-MiniLM-L6-v2) for cost-free vector generation.

4.Hugging Face Models	Language models (SmolLM3-3B, Zephyr-7B) for itinerary generation.

5.FastAPI / Streamlit	Interfaces for REST and interactive chat applications.

_______________________
Architecture

User Query


   ↓
   
Local SentenceTransformer Embeddings

   ↓
   
Pinecone (Vector Retrieval)

   ↓
   
Neo4j (Graph Context)

   ↓
   
Hybrid Context Fusion

   ↓
   
HuggingFace LLM (Reasoning & Response)

   ↓
   
Markdown-formatted Itinerary Output
_______________________

⚙️ Setup


Environment Setup


pip install -r requirements.txt



Configure config.py:
_______________________

Execution Pipeline


1.  Load and visualize graph

python load_to_neo4j.py
python visualize_graph.py


2. Upload semantic vectors


python pinecone_upload.py


3. Run hybrid AI assistant (CLI)



python hybrid_chat.py


4.Launch web UI (Streamlit)


streamlit run ui.py

____________________________
🧠 Features

Hybrid Retrieval: Combines graph and vector-based context retrieval.

Asynchronous Pipeline: Concurrent Pinecone and Neo4j queries for better performance.

Local Embeddings: Offline, fast, and cost-efficient.

Prompt Engineering: Structured markdown outputs with day-wise romantic itineraries.

Caching: Stores previous results to reduce recomputation.

LLM Fallback: Multi-model logic for consistent output.
_______________________________________________

📈 Technical Highlights


1.Metric	Implementation

2.Functionality	End-to-end working hybrid AI chat

3.Debugging	Fixed Pinecone v2 & HuggingFace API issues

4.Design	Modular, clean, documented

5.Reasoning	Prompt-tuned generation for domain tasks

6.Scalability	Async, Docker-based Neo4j, local embeddings

7.Bonus	Auto continuation for long responses
________________________________________________________
🧾 Results

Fully functional local pipeline (Neo4j in Docker, Streamlit UI).


Successfully generates multi-day itineraries for travel queries like:


“Create a romantic 3-day itinerary for Vietnam focusing on beaches and food.”



Response:

Day 1: Hanoi – The Heart of Vietnam

Morning: Start with a sunrise breakfast at Dong Xuan Market or Old Quarter for a vibrant, local start.

Afternoon: Explore Hang Gai Street for street food and Temple of Literature (Tay Ba Lai) for a cultural immersion.

Evening: Take a romantic boat ride on the Red River to Hoan Kiem Lake for a sunset view.

Dinner: Indulge in pho at Pho 88 or Bun Bo Hue at Cafe 88 for a hearty, authentic meal.

Night: End with a stroll along Hoan Kiem Lake and a romantic picnic under the stars.

Day 2: Da Lat – The Romantic Mountain Haven

Morning: Drive to Da Lat (about 3 hours), stopping at Truong Son Mountain for breathtaking views.

Afternoon: Visit the Da Lat Flower Market for a sensory overload of flowers and a romantic stroll.

Evening: Hike Lao Chai Valley for a scenic picnic and sunset views.

Dinner: Enjoy a romantic dinner at Da Lat City View Hotel with a view of the valley.

Night: Relax at Lao Chai Valley Resort with a hot spring or a fire pit.

Day 3: Ho Chi Minh City – Modern Romance

Morning: Explore Notre Dame Cathedral and War Remnants Museum for a blend of history and architecture.

Afternoon: Take a Mekong Delta boat tour to admire rice fields and floating markets.

Evening: Enjoy a Michelin-starred dinner at Central or Com Cau for a sophisticated meal.

Night: Stroll along the Saigon River at sunset or enjoy a river cruise for a romantic ambiance.


Tips: Use tuk-tuks or bikes in Hanoi; pack layers in Da Lat; avoid peak hours in Ho Chi Minh for better photos.
Local Tips:

Hanoi: Try bun bo Hue at 6am for the freshest broth.

Da Lat: Book a hotel with a view for the best sunset spots.

Ho Chi Minh: Use the City Hall as a landmark to navigate the city.

This itinerary blends Vietnam’s rich history, natural beauty, and culinary delights, ensuring a romantic journey through its diverse landscapes.


Screenshots included in the repo show working responses via Streamlit.
