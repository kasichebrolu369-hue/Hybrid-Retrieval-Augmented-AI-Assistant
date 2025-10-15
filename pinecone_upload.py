import json
import time
from huggingface_hub import InferenceClient
from pinecone import Pinecone
from config import (
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    PINECONE_VECTOR_DIM,
    DATA_FILE,
    HF_API_TOKEN,
)

pc = Pinecone(api_key=PINECONE_API_KEY)
hf_client = InferenceClient(
    provider="hf-inference",
    api_key=HF_API_TOKEN,
)

def get_hf_embeddings(texts):
    embeddings = hf_client.feature_extraction(
        texts,
        model="sentence-transformers/all-MiniLM-L6-v2"
    )
    return embeddings

def ensure_index_exists():
    existing_indexes = pc.list_indexes().names()
    if PINECONE_INDEX_NAME not in existing_indexes:
        raise RuntimeError(f"Index '{PINECONE_INDEX_NAME}' does not exist. Please create it manually.")
    print(f" Index '{PINECONE_INDEX_NAME}' exists.")
    return pc.Index(PINECONE_INDEX_NAME)

def load_texts():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    texts = []
    for item in data:
        text_to_embed = item.get("semantic_text") or item.get("description") or ""
        texts.append({"id": item["id"], "text": text_to_embed})
    print(f" Loaded {len(texts)} text records.")
    return texts

def upload_embeddings(index, texts, batch_size=50):
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_ids = [t["id"] for t in batch]
        batch_texts = [t["text"] for t in batch]

        embeddings = get_hf_embeddings(batch_texts)

        vectors = [
            {
                "id": batch_ids[j],
                "values": embeddings[j],
                "metadata": {"text": batch_texts[j]},
            }
            for j in range(len(batch))
        ]

        index.upsert(vectors=vectors)
        print(f"⬆ Upserted batch {i // batch_size + 1} ({len(batch)} items).")
        time.sleep(1)

def main():
    print(" Starting Pinecone upload...")
    index = ensure_index_exists()
    texts = load_texts()
    upload_embeddings(index, texts)
    print(" Upload complete!")

if __name__ == "__main__":
    main()