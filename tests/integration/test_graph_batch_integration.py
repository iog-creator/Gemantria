import os
from pathlib import Path

import pytest

from src.graph.graph import create_graph, run_pipeline


@pytest.fixture
def cleanup_review_file():
    """Clean up review.ndjson after tests."""
    yield
    review_file = Path("review.ndjson")
    if review_file.exists():
        review_file.unlink()


def test_graph_pipeline_structure():
    """Test that the graph has expected nodes and edges."""
    # Test that create_graph doesn't crash and returns a compiled graph
    graph = create_graph()

    # Check that graph has the expected nodes
    assert hasattr(graph, "nodes")
    assert hasattr(graph, "invoke")  # Should be a compiled graph

    # Check that checkpointer was set during creation
    from src.infra.checkpointer import get_checkpointer  # noqa: E402

    checkpointer = get_checkpointer()
    assert checkpointer is not None


def test_graph_pipeline_execution_empty_nouns(cleanup_review_file):
    """Test graph execution with empty noun list (strict mode should abort)."""
    # Set strict batch size
    original_batch_size = os.environ.get("BATCH_SIZE")
    original_allow_partial = os.environ.get("ALLOW_PARTIAL")

    try:
        os.environ["BATCH_SIZE"] = "1"  # Very small batch for testing
        os.environ["ALLOW_PARTIAL"] = "0"  # Strict mode

        result = run_pipeline("Genesis", "START")

        # Should have batch_result as None due to insufficient batch size
        assert result["batch_result"] is None
        # The error should be indicated by batch_result being None
        # In a real scenario, we'd check logs or other indicators

    finally:
        # Restore environment
        if original_batch_size is not None:
            os.environ["BATCH_SIZE"] = original_batch_size
        else:
            os.environ.pop("BATCH_SIZE", None)

        if original_allow_partial is not None:
            os.environ["ALLOW_PARTIAL"] = original_allow_partial
        else:
            os.environ.pop("ALLOW_PARTIAL", None)


def test_graph_pipeline_execution_allow_partial(cleanup_review_file):
    """Test graph execution with ALLOW_PARTIAL=1."""
    # Set permissive mode
    original_allow_partial = os.environ.get("ALLOW_PARTIAL")
    original_partial_reason = os.environ.get("PARTIAL_REASON")

    try:
        os.environ["ALLOW_PARTIAL"] = "1"
        os.environ["PARTIAL_REASON"] = "Integration test"

        result = run_pipeline("Genesis", "START")

        # Should not have error
        assert "error" not in result or result.get("error") is None
        assert "batch_result" in result

        # Since we have empty nouns, batch_result might be None or have empty results
        batch_result = result["batch_result"]
        if batch_result is not None:
            assert hasattr(batch_result, "config")
            assert batch_result.config.allow_partial is True
            assert batch_result.config.partial_reason == "Integration test"

    finally:
        # Restore environment
        if original_allow_partial is not None:
            os.environ["ALLOW_PARTIAL"] = original_allow_partial
        else:
            os.environ.pop("ALLOW_PARTIAL", None)

        if original_partial_reason is not None:
            os.environ["PARTIAL_REASON"] = original_partial_reason
        else:
            os.environ.pop("PARTIAL_REASON", None)


def test_graph_state_preservation():
    """Test that graph state is properly preserved between nodes."""
    result = run_pipeline("Genesis", "START")

    # Check that basic state fields are present
    assert "book_name" in result
    assert "mode" in result
    assert "nouns" in result
    assert "conflicts" in result
    assert "metadata" in result

    # Check values
    assert result["book_name"] == "Genesis"
    assert result["mode"] == "START"
    assert isinstance(result["nouns"], list)
    assert isinstance(result["conflicts"], list)
    assert isinstance(result["metadata"], dict)


def test_backward_compatibility():
    """Test that run_hello still works for backward compatibility."""
    from src.graph.graph import run_hello  # noqa: E402

    result = run_hello("Exodus", "TEST")

    # Should have same structure as run_pipeline
    assert "book_name" in result
    assert "mode" in result
    assert result["book_name"] == "Exodus"
    assert result["mode"] == "TEST"
