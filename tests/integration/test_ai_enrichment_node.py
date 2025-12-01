import os

import psycopg
import pytest

from src.nodes.enrichment import enrichment_node


@pytest.mark.skipif(not os.getenv("GEMATRIA_DSN"), reason="no DB")
def test_ai_enrichment_inserts(monkeypatch):
    state = {"nouns": [{"name": "Adam", "hebrew": "אדם", "value": 45}]}
    out = enrichment_node(state)
    assert "confidence" in out["nouns"][0]


@pytest.mark.skipif(not os.getenv("GEMATRIA_DSN"), reason="no DB")
def test_enrichment_qwen_live_gate_enabled(monkeypatch):
    """Test that enrichment fails when Qwen Live Gate is enabled but models unavailable."""
    monkeypatch.setenv("ENFORCE_QWEN_LIVE", "1")
    monkeypatch.setenv("THEOLOGY_MODEL", "nonexistent-model")
    monkeypatch.setenv("ALLOW_MOCKS_FOR_TESTS", "0")

    state = {
        "validated_nouns": [
            {"name": "Adam", "hebrew": "אדם", "value": 45, "primary_verse": "Gen 1:1"}
        ]
    }

    with pytest.raises(Exception, match="Qwen Live Gate failed"):
        enrichment_node(state)


@pytest.mark.skipif(not os.getenv("GEMATRIA_DSN"), reason="no DB")
def test_enrichment_batches_step4(monkeypatch):
    """Test that enrichment processes nouns in batches of 4."""
    monkeypatch.setenv("LM_STUDIO_MOCK", "1")  # Use mock mode for this test
    monkeypatch.setenv("ENFORCE_QWEN_LIVE", "0")  # Disable live gate for mock test

    # Create 6 test nouns to test batching
    nouns = [
        {
            "name": f"noun{i}",
            "hebrew": f"heb{i}",
            "value": i,
            "primary_verse": f"Gen {i}:1",
        }
        for i in range(6)
    ]
    state = {"validated_nouns": nouns}

    result = enrichment_node(state)

    # Should have processed all nouns
    assert len(result["enriched_nouns"]) == 6
    assert result["ai_enrichments_generated"] == 6

    # Check that each enriched noun has required fields
    for noun in result["enriched_nouns"]:
        assert "confidence" in noun
        assert "insights" in noun
        assert 0.0 <= noun["confidence"] <= 1.0


@pytest.mark.skipif(not os.getenv("GEMATRIA_DSN"), reason="no DB")
@pytest.mark.requires_live_qwen
def test_enrichment_live_lm_studio():
    """Integration test requiring live LM Studio - marked to skip if not available."""
    # This test will only run when LM Studio is actually running
    # It tests the full pipeline with real AI inference
    nouns = [
        {"name": "Adam", "hebrew": "אדם", "value": 45, "primary_verse": "Genesis 2:19"},
        {"name": "Eve", "hebrew": "חוה", "value": 19, "primary_verse": "Genesis 3:20"},
    ]

    # Ensure we have the right environment
    assert os.getenv("ENFORCE_QWEN_LIVE") == "1"
    assert os.getenv("THEOLOGY_MODEL")
    assert os.getenv("LM_STUDIO_MOCK") != "1"

    state = {"validated_nouns": nouns, "run_id": "test-live-enrichment"}

    result = enrichment_node(state)

    # Should have generated enrichments for both nouns
    assert len(result["enriched_nouns"]) == 2
    assert result["ai_enrichments_generated"] == 2

    # Check enrichment quality
    for noun in result["enriched_nouns"]:
        assert "confidence" in noun
        assert "insights" in noun
        assert 0.0 <= noun["confidence"] <= 1.0

        # Check insight length (should be 150-250 words)
        word_count = len(noun["insights"].split())
        assert 150 <= word_count <= 250, f"Insight length {word_count} not in 150-250 word range"

    # Verify DB persistence
    with psycopg.connect(os.getenv("GEMATRIA_DSN")) as conn, conn.cursor() as cur:
        cur.execute(
            """
                SELECT COUNT(*) FROM ai_enrichment_log
                WHERE run_id = %s AND node = 'enrichment'
            """,
            ("test-live-enrichment",),
        )
        count = cur.fetchone()[0]
        assert count == 2

        # Verify health log entry
        cur.execute(
            """
                SELECT COUNT(*) FROM qwen_health_log
                WHERE run_id = %s AND verified = true
            """,
            ("test-live-enrichment",),
        )
        health_count = cur.fetchone()[0]
        assert health_count >= 1  # At least one health check recorded
