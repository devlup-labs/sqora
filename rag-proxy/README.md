# RAG Proxy Service

A standalone FastAPI service that provides Retrieval-Augmented Generation (RAG) capabilities. It intercepts LLM chat completion requests, retrieves relevant documents from Qdrant, injects them into the system prompt, and forwards the augmented request to an LLM server.

## Features

- **Document Retrieval**: Query Qdrant vector database for similar documents
- **Context Injection**: Automatically augments system prompts with retrieved context
- **OpenAI Compatible**: Accepts requests in OpenAI chat completion format
- **Lazy Initialization**: Gracefully handles missing Qdrant connections
- **Environment Configuration**: All settings via environment variables

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

```bash
export QDRANT_URL=http://10.36.16.15:6333      # Qdrant server address
export QDRANT_COLLECTION=pyqs                    # Collection name
export VLLM_SERVER=http://10.36.16.15:8091      # LLM server address
export RAG_EMBED_MODEL=all-MiniLM-L6-v2         # Embedding model
```

### 3. Start the Service

```bash
# Option A: Using bash script
bash run.sh

# Option B: Direct uvicorn
python -m uvicorn rag_proxy:app --host 0.0.0.0 --port 5001
```

Server will be available at `http://localhost:5001`

## Usage

### Add Documents to Qdrant

```python
from rag_proxy import add_documents

docs = [
    "Document 1 text",
    "Document 2 text",
    "Document 3 text"
]
add_documents(docs)
```

### Retrieve Documents

```python
from rag_proxy import retrieve

results = retrieve("query text", k=5)
for doc in results:
    print(doc)
```

### Call Chat Endpoint

```bash
curl -X POST http://localhost:5001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Your question here"}
    ]
  }'
```

## Architecture

```
User Request
    ↓
Extract last user message
    ↓
Search Qdrant for similar documents
    ↓
Augment system prompt with retrieved context
    ↓
Forward to LLM server (e.g., Kyutai)
    ↓
Return LLM response
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `QDRANT_URL` | `http://10.36.16.15:6333` | Qdrant server URL |
| `QDRANT_COLLECTION` | `pyqs` | Qdrant collection name |
| `VLLM_SERVER` | `http://10.36.16.15:8091` | Target LLM server (Kyutai/vLLM) |
| `RAG_EMBED_MODEL` | `all-MiniLM-L6-v2` | Embedding model for vectorization |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `5001` | Server port |

## Requirements

- Python 3.10+
- FastAPI
- Uvicorn
- Sentence Transformers
- Qdrant Client
- httpx

## Testing

```bash
# Test 1: Add documents
python -c "
from rag_proxy import add_documents
add_documents(['test doc 1', 'test doc 2'])
print('✓ Documents added')
"

# Test 2: Retrieve
python -c "
from rag_proxy import retrieve
print(retrieve('test', k=1))
"

# Test 3: Chat endpoint
curl -X POST http://localhost:5001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "test"}]}'
```

## Deployment

### Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY rag_proxy.py .
CMD ["python", "-m", "uvicorn", "rag_proxy:app", "--host", "0.0.0.0", "--port", "5001"]
```

### Docker Compose

```yaml
services:
  rag-proxy:
    build: ./rag-proxy
    ports:
      - "5001:5001"
    environment:
      QDRANT_URL: http://qdrant:6333
      VLLM_SERVER: http://llm-server:8091
```

## Related Components

- **Qdrant**: Vector database at `http://10.36.16.15:6333`
- **Kyutai LLM**: LLM server at `http://10.36.16.15:8091`
- **Manim RAG**: `../manim/rag_index.py` - Similar service for Manim code examples

## Troubleshooting

### "Connection refused" Error
Qdrant server is not running. Make sure it's accessible at the configured `QDRANT_URL`.

### "Model not found" Error
Embedding model is being downloaded. First run may take time. Use `--reload` flag with uvicorn.

### No Documents Retrieved
Documents haven't been added yet. Use `add_documents()` to populate the collection.

## License

Part of the SQORA platform
