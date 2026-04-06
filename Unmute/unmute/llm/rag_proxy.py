from fastapi import FastAPI, Request
import os
import httpx
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List
import uuid

app = FastAPI()

# Qdrant server configuration
QDRANT_URL = os.environ.get("QDRANT_URL", "http://10.36.16.15:6333")
QDRANT_COLLECTION = os.environ.get("QDRANT_COLLECTION", "pyqs")
# Option 1: Point to Kyutai (recommended)
# Change this line in rag_proxy.py:
VLLM_TARGET = os.environ.get("VLLM_SERVER", "http://10.36.16.15:8091")  # Kyutai instead of vLLM
EMBED_MODEL = os.environ.get("RAG_EMBED_MODEL", "all-MiniLM-L6-v2")

# instantiate embedding model and Qdrant client
embedder = SentenceTransformer(EMBED_MODEL) 
client = QdrantClient(url=QDRANT_URL)

# ensure collection exists
_collection_initialized = False


def _ensure_collection():
    """Create the Qdrant collection if it doesn't exist (called lazily)."""
    global _collection_initialized
    if _collection_initialized:
        return
    try:
        client.get_collection(QDRANT_COLLECTION)
        _collection_initialized = True
    except Exception:
        # Create collection if it doesn't exist
        try:
            embedding_dim = embedder.get_sentence_embedding_dimension()
            client.create_collection(
                collection_name=QDRANT_COLLECTION,
                vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE),
            )
            _collection_initialized = True
        except Exception:
            pass  # Fail silently during init


def add_documents(texts: List[str]):
    """Add one or more documents to the Qdrant collection."""
    if not texts:
        return
    _ensure_collection()
    vectors = embedder.encode(texts, convert_to_numpy=True)
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vec.tolist(),
            payload={"text": text},
        )
        for vec, text in zip(vectors, texts)
    ]
    client.upsert(collection_name=QDRANT_COLLECTION, points=points)


def retrieve(query: str, k: int = 3) -> List[str]:
    """Return top‑k documents most similar to the query from Qdrant."""
    try:
        _ensure_collection()
        qvec = embedder.encode([query], convert_to_numpy=True)[0]
        results = client.query_points(
            collection_name=QDRANT_COLLECTION,
            query=qvec.tolist(),
            limit=k,
        )
        print(f"RAG Proxy: Retrieved {len(results.points)} chunks for query: {query!r}")
        return [hit.payload["text"] for hit in results.points]
    except Exception as e:
        print(f"RAG Proxy error during retrieve: {e}")
        return []


@app.post("/v1/chat/completions")
async def proxy_chat(request: Request):
    """Proxy that injects retrieval results into the system prompt before forwarding.

    The original body is forwarded to the real LLM server configured via the
    ``VLLM_SERVER`` environment variable.  Example usage:

        export KYUTAI_LLM_URL=http://localhost:5001  # start the proxy there
        python -m uvicorn unmute.rag_proxy:app --host 0.0.0.0 --port 5001

    Documents may be added by calling ``add_documents`` from another script or
    by mounting the RAG store and writing directly to the JSON file.
    """
    body = await request.json()
    messages = body.get("messages", [])
    # find last user message
    user_msg = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            user_msg = m.get("content", "")
            break
    if user_msg:
        retrieved = retrieve(user_msg, k=5)
        if retrieved:
            # build a single system prompt that contains the original system
            # content plus the retrieved text.  This is a very simple strategy;
            # you can insert the documents wherever makes sense.
            sys_index = next((i for i, m in enumerate(messages) if m.get("role") == "system"), None)
            prefix = "" if sys_index is None else messages[sys_index]["content"]
            augmented = prefix + "\n\n" + "\n\n---\n\n".join(retrieved)
            if sys_index is not None:
                messages[sys_index]["content"] = augmented
            else:
                messages.insert(0, {"role": "system", "content": augmented})
            body["messages"] = messages
    # forward to target LLM / vLLM server
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{VLLM_TARGET}/v1/chat/completions", json=body)
    return resp.json()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = sys.argv[1]
        results = retrieve(query)
        for r in results:
            print(r)
