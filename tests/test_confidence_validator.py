"""
Unit tests for confidence validator runtime threshold behavior.

Verifies that the validator:
- Uses runtime env variable (not module-time constant)
- Defaults to 0.80 when env var is missing
- Respects env overrides
- Correctly validates 69 items with 0.85 confidence at default threshold
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from src.nodes.confidence_validator import confidence_validator_node, ConfidenceValidationError


def make_batch(n: int, ai_conf: float = 0.85, gem_conf: float = 1.0) -> list[dict]:
    """Helper to build a batch of noun dicts."""
    return [
        {
            "noun_id": f"n-{i}",
            "name": f"noun_{i}",
            "gematria_confidence": gem_conf,  # set to 1.0 so this gate always passes
            "confidence": ai_conf,  # the AI confidence under test
        }
        for i in range(n)
    ]


@pytest.fixture
def mock_db_connection():
    """Mock database connection and cursor."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    return mock_conn, mock_cursor


@patch("src.nodes.confidence_validator.psycopg.connect")
def test_default_threshold_is_080_when_env_missing(mock_connect, monkeypatch, mock_db_connection):
    """Ensure no override is present → validator should default to 0.80 at runtime."""
    mock_conn, _mock_cursor = mock_db_connection
    mock_connect.return_value = mock_conn
    monkeypatch.delenv("AI_CONFIDENCE_THRESHOLD", raising=False)

    batch = make_batch(1, ai_conf=0.85, gem_conf=1.0)
    state = {"enriched_nouns": batch, "run_id": str(uuid.uuid4())}

    result = confidence_validator_node(state)
    summary = result["confidence_validation"]

    assert summary["thresholds"]["ai"] == pytest.approx(0.80)
    assert summary["passed"] is True
    assert len([r for r in summary["results"] if r["validation_passed"]]) == 1


@patch("src.nodes.confidence_validator.psycopg.connect")
def test_env_override_applies_at_runtime(mock_connect, monkeypatch, mock_db_connection):
    """Override to 0.90 → an item at 0.85 should fail the AI gate."""
    mock_conn, _mock_cursor = mock_db_connection
    mock_connect.return_value = mock_conn
    monkeypatch.setenv("AI_CONFIDENCE_THRESHOLD", "0.90")

    batch = make_batch(1, ai_conf=0.85, gem_conf=1.0)
    state = {"enriched_nouns": batch, "run_id": str(uuid.uuid4())}

    with pytest.raises(ConfidenceValidationError) as exc_info:
        confidence_validator_node(state)

    assert "Confidence validation failed" in str(exc_info.value)
    assert len(exc_info.value.low_confidence_nouns) == 1
    assert exc_info.value.low_confidence_nouns[0]["ai_confidence"] == 0.85


@patch("src.nodes.confidence_validator.psycopg.connect")
def test_sixty_nine_items_pass_at_default(mock_connect, monkeypatch, mock_db_connection):
    """With no env var, default=0.80 → 69 items at 0.85 should all pass."""
    mock_conn, _mock_cursor = mock_db_connection
    mock_connect.return_value = mock_conn
    monkeypatch.delenv("AI_CONFIDENCE_THRESHOLD", raising=False)

    batch = make_batch(69, ai_conf=0.85, gem_conf=1.0)
    state = {"enriched_nouns": batch, "run_id": str(uuid.uuid4())}

    result = confidence_validator_node(state)
    summary = result["confidence_validation"]

    assert summary["thresholds"]["ai"] == pytest.approx(0.80)
    assert summary["passed"] is True
    validated_count = len([r for r in summary["results"] if r["validation_passed"]])
    assert validated_count == 69


@patch("src.nodes.confidence_validator.psycopg.connect")
def test_mixed_confidences_split_correctly(mock_connect, monkeypatch, mock_db_connection):
    """Mixed distribution: half 0.79 (fail), half 0.85 (pass) at default 0.80."""
    mock_conn, _mock_cursor = mock_db_connection
    mock_connect.return_value = mock_conn
    monkeypatch.delenv("AI_CONFIDENCE_THRESHOLD", raising=False)

    lows = make_batch(10, ai_conf=0.79, gem_conf=1.0)
    highs = make_batch(10, ai_conf=0.85, gem_conf=1.0)
    batch = lows + highs

    state = {"enriched_nouns": batch, "run_id": str(uuid.uuid4())}

    with pytest.raises(ConfidenceValidationError) as exc_info:
        confidence_validator_node(state)

    assert len(exc_info.value.low_confidence_nouns) == 10
    # Check that all failed items have 0.79 confidence
    for item in exc_info.value.low_confidence_nouns:
        assert item["ai_confidence"] == 0.79


@patch("src.nodes.confidence_validator.psycopg.connect")
def test_gematria_gate_independent_of_ai(mock_connect, monkeypatch, mock_db_connection):
    """Even with high AI, gematria below its threshold should fail."""
    mock_conn, _mock_cursor = mock_db_connection
    mock_connect.return_value = mock_conn
    monkeypatch.delenv("AI_CONFIDENCE_THRESHOLD", raising=False)

    batch = [
        {"noun_id": "ok", "name": "ok_noun", "gematria_confidence": 1.0, "confidence": 0.85},  # pass
        {"noun_id": "bad", "name": "bad_noun", "gematria_confidence": 0.0, "confidence": 0.99},  # fail gematria gate
    ]

    state = {"enriched_nouns": batch, "run_id": str(uuid.uuid4())}

    with pytest.raises(ConfidenceValidationError) as exc_info:
        confidence_validator_node(state)

    assert len(exc_info.value.low_confidence_nouns) == 1
    assert exc_info.value.low_confidence_nouns[0]["gematria_confidence"] == 0.0
    assert exc_info.value.low_confidence_nouns[0]["ai_confidence"] == 0.99
