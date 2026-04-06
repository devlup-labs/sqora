"""Shared test configuration and fixtures."""

import pytest
import os

# Set test environment variables
os.environ["QDRANT_URL"] = "http://localhost:6333"
os.environ["QDRANT_COLLECTION"] = "test_pyqs"
os.environ["QDRANT_MANIM_COLLECTION"] = "test_manim"
os.environ["RAG_EMBED_MODEL"] = "all-MiniLM-L6-v2"
os.environ["VLLM_SERVER"] = "http://localhost:8000"


@pytest.fixture
def mock_qdrant_response():
    """Fixture providing a mock Qdrant search response."""
    from unittest.mock import Mock

    def _make_response(texts):
        hits = []
        for text in texts:
            hit = Mock()
            hit.payload = {"text": text}
            hits.append(hit)
        return hits

    return _make_response


@pytest.fixture
def mock_manim_response():
    """Fixture providing a mock Manim code response."""
    from unittest.mock import Mock

    def _make_response(codes):
        hits = []
        for code in codes:
            hit = Mock()
            hit.payload = {"code": code}
            hits.append(hit)
        return hits

    return _make_response


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (require Qdrant server)"
    )
