
from fastapi import FastAPI
import asyncio
from hybrid_chat import process_query

app = FastAPI(title="Hybrid AI Travel Assistant")

@app.get("/")
def home():
    return {"status": "Hybrid AI Chat is running!"}

@app.get("/ask")
async def ask(query: str):
    response = await process_query(query)
    return {"query": query, "response": response}
