from fastapi import FastAPI, Request
import os
import sys
import json
import uuid
from typing import List

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

app = FastAPI()

# -------------------------
# Configuration
# -------------------------

QDRANT_HOST = os.environ.get("QDRANT_HOST", "10.36.16.15")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", 6333))
QDRANT_COLLECTION = os.environ.get("QDRANT_COLLECTION", "pyqs")

EMBED_MODEL = os.environ.get(
    "RAG_EMBED_MODEL",
    "BAAI/bge-small-en-v1.5"
)

# -------------------------
# Initialize embedding model
# -------------------------

print("Loading embedding model...")
embedder = SentenceTransformer(EMBED_MODEL)

# -------------------------
# Connect to Qdrant
# -------------------------

print(f"Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}...")

try:
    client = QdrantClient(
        host=QDRANT_HOST,
        port=QDRANT_PORT
    )

    collections = client.get_collections()
    print("✓ Connected to Qdrant")
    print("Collections:", collections)

except Exception as e:
    print(f"❌ Cannot connect to Qdrant: {e}")
    sys.exit(1)

_collection_initialized = False


# -------------------------
# Ensure collection exists
# -------------------------

def ensure_collection():
    global _collection_initialized

    if _collection_initialized:
        return

    try:
        client.get_collection(QDRANT_COLLECTION)
        print(f"Collection '{QDRANT_COLLECTION}' already exists")

    except Exception:
        print(f"Creating collection '{QDRANT_COLLECTION}'")

        embedding_dim = embedder.get_sentence_embedding_dimension()

        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=embedding_dim,
                distance=Distance.COSINE
            )
        )

    _collection_initialized = True


# -------------------------
# Insert documents
# -------------------------

def add_documents(texts: List[str]):

    if not texts:
        return

    ensure_collection()

    vectors = embedder.encode(texts, convert_to_numpy=True)

    points = []

    for vec, text in zip(vectors, texts):

        points.append(
            PointStruct(
                id=uuid.uuid4().int >> 64,
                vector=vec.tolist(),
                payload={"text": text}
            )
        )

    client.upsert(
        collection_name=QDRANT_COLLECTION,
        points=points
    )

    print(f"Inserted {len(points)} documents")


# -------------------------
# Retrieve documents
# -------------------------

def retrieve(query: str, k: int = 3) -> List[str]:

    ensure_collection()

    qvec = embedder.encode([query], convert_to_numpy=True)[0]

    results = client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=qvec.tolist(),
        limit=k
    )

    return [hit.payload["text"] for hit in results]


# -------------------------
# API endpoint
# -------------------------

@app.post("/v1/chat/completions")
async def proxy_chat(request: Request):

    body = await request.json()
    messages = body.get("messages", [])

    user_msg = ""

    for m in reversed(messages):
        if m.get("role") == "user":
            user_msg = m.get("content", "")
            break

    retrieved = retrieve(user_msg, k=3) if user_msg else []

    return {
        "query": user_msg,
        "chunks": retrieved,
        "count": len(retrieved)
    }


# -------------------------
# CLI mode
# -------------------------

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage:")
        print("python rag_proxy.py '<query>' [k]")
        sys.exit(1)

    query = sys.argv[1]
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    print("\n" + "=" * 60)
    print(f"Query: {query}")
    print("=" * 60)

    try:

        results = retrieve(query, k)

        if not results:
            print("No documents found.")
            sys.exit(0)

        print(f"\nFound {len(results)} documents:\n")

        for i, doc in enumerate(results, 1):
            print(f"{i}. {doc}")
            print("-" * 60)

        print("\nJSON Output:")
        print(json.dumps({
            "query": query,
            "results": results,
            "count": len(results)
        }, indent=2))

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)