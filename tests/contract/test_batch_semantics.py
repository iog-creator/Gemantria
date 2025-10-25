import os
from pathlib import Path

import pytest

from src.graph.batch_processor import (
    BatchAbortError,
    BatchConfig,
    BatchProcessor,
    process_batch,
)


@pytest.fixture
def cleanup_review_file():
    """Clean up review.ndjson after tests."""
    yield
    review_file = Path("review.ndjson")
    if review_file.exists():
        review_file.unlink()


def test_batch_size_enforcement_strict_mode(cleanup_review_file):
    """Test that batch processing aborts when insufficient nouns in strict mode."""
    config = BatchConfig(batch_size=3, allow_partial=False)
    processor = BatchProcessor(config)

    # Only 2 nouns, but batch_size=3
    nouns = ["אדם", "חוה"]

    with pytest.raises(BatchAbortError) as exc_info:
        processor.process_nouns(nouns)

    error = exc_info.value
    assert error.nouns_available == 2
    assert error.batch_size == 3

    # Should create review.ndjson
    review_file = Path("review.ndjson")
    assert review_file.exists()

    content = review_file.read_text()
    lines = content.strip().split("\n")
    assert len(lines) == 2  # One line per noun

    # Check content structure
    import json  # noqa: E402

    for line in lines:
        entry = json.loads(line)
        assert "noun" in entry
        assert "status" in entry
        assert entry["status"] == "pending_review"


def test_batch_size_allow_partial_override(cleanup_review_file):
    """Test that ALLOW_PARTIAL=1 allows processing with insufficient nouns."""
    config = BatchConfig(
        batch_size=3,
        allow_partial=True,
        partial_reason="Testing partial batch processing",
    )
    processor = BatchProcessor(config)

    nouns = ["אדם", "חוה"]  # Only 2 nouns

    # Should not raise error
    result = processor.process_nouns(nouns)

    assert result.nouns_processed == 2
    assert result.config.allow_partial is True
    assert result.config.partial_reason == "Testing partial batch processing"
    assert len(result.results) == 2

    # Should NOT create review.ndjson
    review_file = Path("review.ndjson")
    assert not review_file.exists()


def test_batch_manifest_recording():
    """Test that batch results include proper manifest with hash proofs."""
    config = BatchConfig(batch_size=2, allow_partial=True)
    processor = BatchProcessor(config)

    nouns = ["אדם", "חוה"]
    result = processor.process_nouns(nouns)

    # Check manifest structure
    manifest = result.manifest
    assert manifest["batch_id"] == result.batch_id
    assert manifest["input_count"] == 2
    assert manifest["processed_count"] == 2
    assert manifest["allow_partial"] is True
    assert manifest["batch_size"] == 2
    assert manifest["validation"] == "deterministic_hash_proof"

    # Check hash arrays
    assert len(manifest["input_hashes"]) == 2
    assert len(manifest["result_hashes"]) == 2

    # All hashes should be strings
    assert all(isinstance(h, str) for h in manifest["input_hashes"])
    assert all(isinstance(h, str) for h in manifest["result_hashes"])


def test_batch_deterministic_id():
    """Test that batch IDs are deterministic based on content."""
    config = BatchConfig(batch_size=2, allow_partial=True)

    # Same nouns in different order should produce same batch ID
    nouns1 = ["אדם", "חוה"]
    nouns2 = ["חוה", "אדם"]

    result1 = process_batch(nouns1, config)
    result2 = process_batch(nouns2, config)

    assert result1.batch_id == result2.batch_id
    assert len(result1.batch_id) == 16  # Short ID format


def test_batch_result_structure():
    """Test that batch results have expected structure."""
    config = BatchConfig(batch_size=2, allow_partial=True)
    result = process_batch(["אדם", "חוה"], config)

    # Check result structure
    assert hasattr(result, "batch_id")
    assert hasattr(result, "config")
    assert hasattr(result, "nouns_processed")
    assert hasattr(result, "results")
    assert hasattr(result, "manifest")
    assert hasattr(result, "created_at")

    # Check to_dict serialization
    result_dict = result.to_dict()
    assert "batch_id" in result_dict
    assert "config" in result_dict
    assert "nouns_processed" in result_dict
    assert "results" in result_dict
    assert "manifest" in result_dict
    assert "created_at" in result_dict


def test_env_config_loading():
    """Test that BatchConfig loads properly from environment."""
    # Set environment variables
    original_batch_size = os.environ.get("BATCH_SIZE")
    original_allow_partial = os.environ.get("ALLOW_PARTIAL")
    original_partial_reason = os.environ.get("PARTIAL_REASON")

    try:
        os.environ["BATCH_SIZE"] = "25"
        os.environ["ALLOW_PARTIAL"] = "1"
        os.environ["PARTIAL_REASON"] = "Test override"

        config = BatchConfig.from_env()
        assert config.batch_size == 25
        assert config.allow_partial is True
        assert config.partial_reason == "Test override"

    finally:
        # Restore original environment
        if original_batch_size is not None:
            os.environ["BATCH_SIZE"] = original_batch_size
        else:
            os.environ.pop("BATCH_SIZE", None)

        if original_allow_partial is not None:
            os.environ["ALLOW_PARTIAL"] = original_allow_partial
        else:
            os.environ.pop("ALLOW_PARTIAL", None)

        if original_partial_reason is not None:
            os.environ["PARTIAL_REASON"] = original_partial_reason
        else:
            os.environ.pop("PARTIAL_REASON", None)
