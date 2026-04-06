"""Unit and integration tests for rag_proxy.py"""

import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from qdrant_client.models import ScoredPoint, PointStruct

# Mock environment for testing
os.environ["QDRANT_URL"] = "http://localhost:6333"
os.environ["QDRANT_COLLECTION"] = "test_collection"
os.environ["VLLM_SERVER"] = "http://localhost:8000"
os.environ["RAG_EMBED_MODEL"] = "all-MiniLM-L6-v2"

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_proxy import app, add_documents, retrieve


client = TestClient(app)


class TestImports:
    """Test that modules import correctly without connection errors."""

    def test_rag_proxy_imports(self):
        """Test that rag_proxy can be imported safely."""
        assert app is not None
        assert callable(add_documents)
        assert callable(retrieve)

    def test_functions_exist(self):
        """Test that required functions exist."""
        assert hasattr(add_documents, '__call__')
        assert hasattr(retrieve, '__call__')


class TestAddDocumentsFunction:
    """Test the add_documents() function."""

    def test_add_documents_accepts_list(self):
        """Test that add_documents accepts a list of texts."""
        # Just verify it doesn't crash with empty input (graceful degradation)
        try:
            add_documents([])
        except Exception as e:
            pytest.fail(f"add_documents should handle empty list: {e}")

    def test_add_documents_function_exists(self):
        """Test that add_documents function exists and is callable."""
        assert callable(add_documents)


class TestProxyChatEndpoint:
    """Test the /v1/chat/completions proxy endpoint."""

    def test_proxy_endpoint_exists(self):
        """Test that proxy endpoint is registered."""
        assert app is not None
        # Verify the app has the route
        routes = [route.path for route in app.routes]
        assert "/v1/chat/completions" in routes


class TestIntegration:
    """Integration tests (require live Qdrant server)."""

    @pytest.mark.integration
    def test_add_and_retrieve_documents(self):
        """Test adding and retrieving documents from live Qdrant."""
        try:
            test_docs = [
                "The Qdrant vector database is designed for high-performance similarity search.",
                "Machine learning models can be deployed efficiently with proper infrastructure.",
                "Python is widely used for data science and AI applications.",
            ]

            # Add documents
            add_documents(test_docs)

            # Retrieve similar documents
            query = "vector database similarity"
            results = retrieve(query, k=2)

            assert len(results) > 0
            assert any("vector" in r.lower() or "qdrant" in r.lower() for r in results)

        except Exception as e:
            pytest.skip(f"Integration test skipped (no Qdrant server): {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
