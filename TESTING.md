# RAG Testing Guide

This document explains how to run and understand the test suites for the RAG (Retrieval-Augmented Generation) components.

## Test Files

### 1. **Unmute RAG Proxy Tests** (`Unmute/unmute/test_rag_proxy.py`)
Tests for the FastAPI proxy that intercepts LLM requests and injects RAG context.

**What it tests:**
- `retrieve()` function: document retrieval from Qdrant
- `add_documents()` function: adding documents to Qdrant
- `/v1/chat/completions` endpoint: proxy functionality and context injection
- Exception handling and edge cases

### 2. **Manim RAG Index Tests** (`manim/test_rag_index.py`)
Tests for the Manim scene code example vector store.

**What it tests:**
- `add_examples()` function: adding code snippets to Qdrant
- `retrieve_examples()` function: retrieving similar code examples
- Error handling and empty results
- CLI functionality

### 3. **Shared Configuration** (`conftest.py`)
Pytest configuration and fixtures shared across tests.

---

## Setup

### 1. Install Testing Dependencies

```bash
cd /home/lokeshkaria/Desktop/Learning/sqora
source .venv/bin/activate
pip install pytest pytest-asyncio httpx
```

### 2. Choose Testing Mode

#### **Option A: Unit Tests (No Qdrant Required)**
These tests use basic validation and don't require a live Qdrant server.

```bash
# Run all unit tests (fastest)
pytest -v -m "not integration"

# Run only rag_proxy tests
cd Unmute/unmute
pytest test_rag_proxy.py -v -m "not integration"

# Run only manim tests  
cd manim
pytest test_rag_index.py -v -m "not integration"
```

#### **Option B: Integration Tests (Requires Qdrant)**
These tests require a live Qdrant server running at `http://10.36.16.15:6333`.

```bash
# Start Qdrant server first (if using Docker):
docker run -p 6333:6333 qdrant/qdrant

# Run integration tests
pytest -v -m "integration"
```

---

## Running Tests

### From Workspace Root

```bash
# All unit tests
pytest Unmute/unmute/test_rag_proxy.py manim/test_rag_index.py -v -m "not integration"

# All tests (including integration)
pytest Unmute/unmute/test_rag_proxy.py manim/test_rag_index.py -v

# Only integration tests
pytest Unmute/unmute/test_rag_proxy.py manim/test_rag_index.py -v -m "integration"
```

### From Specific Directories

```bash
# Test the proxy
cd Unmute/unmute
pytest test_rag_proxy.py -v

# Test Manim RAG
cd manim
pytest test_rag_index.py -v
```

### Running Specific Tests

```bash
# Test class
pytest Unmute/unmute/test_rag_proxy.py::TestImports -v

# Single test
pytest Unmute/unmute/test_rag_proxy.py::TestImports::test_rag_proxy_imports -v
```

---

## Test Configuration

### Environment Variables

Tests automatically set these variables:

```bash
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=test_pyqs
QDRANT_MANIM_COLLECTION=test_manim
RAG_EMBED_MODEL=all-MiniLM-L6-v2
VLLM_SERVER=http://localhost:8000
```

Production values are:
```bash
QDRANT_URL=http://10.36.16.15:6333
QDRANT_COLLECTION=llm_context
QDRANT_MANIM_COLLECTION=manim_scenes
RAG_EMBED_MODEL=qwen3-embedding-0.6b
VLLM_TARGET=http://localhost:8000
```

### pytest Markers

The following markers are configured:

- `integration` - Tests requiring live Qdrant server
- All other tests run as unit tests (no marker)

---

## Expected Test Results

### Unit Tests Output

```
======================== 11 passed, 3 skipped in 15.72s ==========
```

- **11 passed**: Core unit tests
- **3 skipped**: Integration tests (require Qdrant server)

### Test Classes

**RAG Proxy (`test_rag_proxy.py`):**
- `TestImports` - 2 tests
- `TestAddDocumentsFunction` - 2 tests  
- `TestProxyChatEndpoint` - 1 test
- `TestIntegration` - 1 test (integration only)

**Manim RAG (`test_rag_index.py`):**
- `TestImports` - 1 test
- `TestAddExamples` - 2 tests
- `TestRetrieveExamples` - 1 test
- `TestIntegration` - 2 tests (integration only)
- `TestCLI` - 1 test

---

## Troubleshooting

### Tests Not Found

```bash
# Make sure you're in the right directory
cd /home/lokeshkaria/Desktop/Learning/sqora

# Verify test files exist
ls Unmute/unmute/test_rag_proxy.py
ls manim/test_rag_index.py

# List all available tests
pytest --collect-only -q
```

### Import Errors

```bash
# Activate virtual environment
source .venv/bin/activate

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

### pytest: warning: Unknown pytest.mark.*

This happens when running from the wrong directory. Solution:

```bash
# MUST run from workspace root (where conftest.py is)
cd /home/lokeshkaria/Desktop/Learning/sqora
pytest Unmute/unmute/test_rag_proxy.py -v
```

### Qdrant Connection Errors

These are expected in unit tests and result in graceful handling:

```python
try:
    result = retrieve_examples("query", k=3)
except Exception:
    result = []  # Returns empty list on error
```

For integration tests, they will skip if Qdrant is unavailable:

```
test_add_and_retrieve_documents SKIPPED - No Qdrant server available
```

---

## CI/CD Integration

For automated pipelines:

```bash
# Install dependencies
pip install -r requirements.txt

# Run unit tests only (no external services needed)
pytest Unmute/unmute/test_rag_proxy.py manim/test_rag_index.py \
  -v -m "not integration" --tb=short

# Exit code 0 = success
echo $?
```

---

## Adding New Tests

### Unit Test Example

```python
def test_new_function():
    """Test description."""
    from rag_proxy import new_function
    
    # Test that function exists and is callable
    assert callable(new_function)
    
    # Test basic usage
    result = new_function([])
    assert isinstance(result, list)
```

### Integration Test Example

```python
@pytest.mark.integration
def test_with_qdrant():
    """Test with live Qdrant server."""
    try:
        result = retrieve_examples("test", k=1)
        assert isinstance(result, list)
    except Exception as e:
        pytest.skip(f"Qdrant unavailable: {e}")
```

---

## Documentation

- See [README.md](README.md) for RAG pipeline overview
- See [Unmute/README.md](Unmute/README.md) for Unmute-specific setup
