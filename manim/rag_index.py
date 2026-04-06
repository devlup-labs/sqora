"""Simple RAG index for Manim code examples using Qdrant.

This module queries a remote Qdrant vector database for previously‑generated
or curated Manim scenes. When the `worker.generate_manim_code` function runs it
queries the Qdrant collection for examples similar to the user's requested topic
and injects those examples into Gemini's prompt.

Usage:

    from manim.rag_index import add_examples, retrieve_examples

    add_examples(["class GeneratedScene(Scene): ..."])
    hits = retrieve_examples("fourier series animation", k=3)

Configuration is done via environment variables:
- ``QDRANT_URL``: Qdrant server endpoint (default: http://qdrant-server:6333)
- ``QDRANT_MANIM_COLLECTION``: collection name (default: manim_scenes)
- ``MANIM_RAG_EMBED_MODEL``: embedding model (default: all-MiniLM-L6-v2)
"""

import os
from typing import List

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid

QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant-server:6333")
QDRANT_COLLECTION = os.environ.get("QDRANT_MANIM_COLLECTION", "manim_scenes")
EMBED_MODEL = os.environ.get("MANIM_RAG_EMBED_MODEL", "all-MiniLM-L6-v2")

embedder = SentenceTransformer(EMBED_MODEL)
client = QdrantClient(url=QDRANT_URL)

# lazy initialization flag
_collection_initialized = False


def _ensure_collection():
    """Create the Qdrant collection if it doesn't exist."""
    global _collection_initialized
    if _collection_initialized:
        return
    try:
        client.get_collection(QDRANT_COLLECTION)
        _collection_initialized = True
    except Exception:
        try:
            embedding_dim = embedder.get_sentence_embedding_dimension()
            client.create_collection(
                collection_name=QDRANT_COLLECTION,
                vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE),
            )
            _collection_initialized = True
        except Exception:
            pass  # Fail silently


def add_examples(snippets: List[str]) -> None:
    """Add one or more code snippets to the Qdrant collection."""
    if not snippets:
        return
    _ensure_collection()
    vectors = embedder.encode(snippets, convert_to_numpy=True)
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vec.tolist(),
            payload={"code": snippet},
        )
        for vec, snippet in zip(vectors, snippets)
    ]
    client.upsert(collection_name=QDRANT_COLLECTION, points=points)


def retrieve_examples(query: str, k: int = 3) -> List[str]:
    """Return up to *k* stored code snippets relevant to *query*.

    The returned strings are the raw code examples; the caller is responsible
    for formatting them into the prompt (e.g. surrounding them with comments).
    """
    try:
        _ensure_collection()
        qvec = embedder.encode([query], convert_to_numpy=True)[0]
        results = client.search(
            collection_name=QDRANT_COLLECTION,
            query_vector=qvec.tolist(),
            limit=k,
        )
        return [hit.payload["code"] for hit in results]
    except Exception:
        return []


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Manage manim RAG index on Qdrant")
    sub = parser.add_subparsers(dest="cmd")

    add = sub.add_parser("add", help="add snippet(s) from stdin or file")
    add.add_argument("--file", "-f", help="read text from file instead of stdin")

    args = parser.parse_args()
    if args.cmd == "add":
        text = ""
        if args.file:
            text = open(args.file).read()
        else:
            text = sys.stdin.read()
        add_examples([text])
        print(f"Added 1 snippet to Qdrant collection '{QDRANT_COLLECTION}'")
    else:
        parser.print_help()
