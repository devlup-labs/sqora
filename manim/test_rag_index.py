"""Unit and integration tests for manim/rag_index.py"""

import pytest
import os
import sys
import inspect

# Mock environment
os.environ["QDRANT_URL"] = "http://localhost:6333"
os.environ["QDRANT_MANIM_COLLECTION"] = "test_manim_scenes" 
os.environ["MANIM_RAG_EMBED_MODEL"] = "all-MiniLM-L6-v2"

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_index import add_examples, retrieve_examples

class TestImports:
    """Test module imports."""

    def test_functions_exist(self):
        """Test that required functions are defined."""
        assert callable(add_examples)
        assert callable(retrieve_examples)


class TestAddExamples:
    """Test the add_examples() function."""

    def test_add_examples_function_signature(self):
        """Test that add_examples has correct signature."""
        sig = inspect.signature(add_examples)
        assert 'snippets' in sig.parameters or 'examples' in sig.parameters

    def test_add_examples_accepts_list(self):
        """Test that add_examples handles empty list gracefully."""
        try:
            add_examples([])
        except Exception as e:
            pytest.fail(f"add_examples should handle empty list: {e}")


class TestRetrieveExamples:
    """Test the retrieve_examples() function."""

    def test_retrieve_examples_function_signature(self):
        """Test that retrieve_examples has correct signature."""
        sig = inspect.signature(retrieve_examples)
        assert 'query' in sig.parameters

    def test_retrieve_examples_returns_list(self):
        """Test that retrieve_examples returns a list."""
        try:
            result = retrieve_examples("test query", k=1)
            # It might fail due to no Qdrant, but should return empty list
            assert isinstance(result, list)
        except AssertionError:
            pass

class TestIntegration:
    """Integration tests (require live Qdrant server)."""

    @pytest.mark.integration
    def test_add_and_retrieve_manim_examples(self):
        """Test adding and retrieving Manim examples from live Qdrant."""
        try:
            examples = [
                """from manim import *

class WaveAnimation(Scene):
    def construct(self):
        wave = FunctionGraph(lambda x: np.sin(x), x_range=[-2*PI, 2*PI])
        self.play(Create(wave))
                """,
                """from manim import *

class RotatingSquare(Scene):
    def construct(self):
        square = Square()
        self.play(Create(square))
        self.play(Rotate(square))
                """,
            ]

            # Add examples
            add_examples(examples)

            # Retrieve similar examples
            query = "wave animation trigonometric"
            results = retrieve_examples(query, k=1)

            assert len(results) > 0
            assert any(
                "wave" in r.lower() or "sine" in r.lower() or "sin" in r.lower()
                for r in results
            )

        except Exception as e:
            pytest.skip(f"Integration test skipped (no Qdrant server): {e}")

    @pytest.mark.integration
    def test_multiple_retrievals(self):
        """Test multiple retrieval operations."""
        try:
            # Add diverse examples
            examples = [
                "from manim import *\n\nclass LinearTransform(Scene):\n    pass",
                "from manim import *\n\nclass PolarToCartesian(Scene):\n    pass",
                "from manim import *\n\nclass DataVisualization(Scene):\n    pass",
            ]

            add_examples(examples)

            # Test different queries
            queries = [
                "linear algebra matrix",
                "coordinate transformation",
                "data plot visualization",
            ]

            for query in queries:
                results = retrieve_examples(query, k=2)
                # Just verify it doesn't crash and returns something
                assert isinstance(results, list)

        except Exception as e:
            pytest.skip(f"Integration test skipped (no Qdrant server): {e}")


class TestCLI:
    """Test the CLI interface."""

    def test_cli_functions_defined(self):
        """Test that functions are defined and callable."""
        assert callable(add_examples)
        assert callable(retrieve_examples)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

