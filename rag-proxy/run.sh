#!/bin/bash

# RAG Proxy Service Startup Script
# Starts the Retrieval-Augmented Generation FastAPI proxy

set -e

# Configuration
QDRANT_URL="${QDRANT_URL:-http://10.36.16.15:6333}"
QDRANT_COLLECTION="${QDRANT_COLLECTION:-pyqs}"
VLLM_SERVER="${VLLM_SERVER:-http://10.36.16.15:8091}"
RAG_EMBED_MODEL="${RAG_EMBED_MODEL:-all-MiniLM-L6-v2}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-5001}"

echo "=========================================="
echo "Starting RAG Proxy Service"
echo "=========================================="
echo "Qdrant URL:      $QDRANT_URL"
echo "Qdrant Collection: $QDRANT_COLLECTION"
echo "LLM Target:      $VLLM_SERVER"
echo "Embedding Model: $RAG_EMBED_MODEL"
echo "Server:          $HOST:$PORT"
echo "=========================================="

# Set environment variables
export QDRANT_URL
export QDRANT_COLLECTION
export VLLM_SERVER
export RAG_EMBED_MODEL

# Start the service
python -m uvicorn rag_proxy:app --host "$HOST" --port "$PORT" --reload
