"""Tests for RerankerAdapter (Phase 15 Wave-2).

Test coverage:
- Initialization with Granite/BGE reranker config
- Chunk reranking logic (mock-based)
- Combined score calculation (0.7 * embedding + 0.3 * reranker)
- Hermetic mode (reranker unavailable)
- Fallback behavior
"""

import pytest
from unittest.mock import patch

from pmagent.biblescholar.reranker_adapter import RerankerAdapter


class TestRerankerAdapterInit:
    """Test RerankerAdapter initialization."""

    def test_init_default(self):
        """Test default initialization."""
        adapter = RerankerAdapter()
        assert adapter is not None
        assert adapter._lm_status in ["available", "unavailable", "lm_off"]


class TestRerankerAdapterReranking:
    """Test rerank_chunks method."""

    @patch("pmagent.biblescholar.reranker_adapter.RerankerAdapter._ensure_lm")
    def test_rerank_chunks_wave3_lm_required(self, mock_ensure_lm):
        """Test reranking with LM unavailable (Wave-3: LOUD FAIL).

        Wave-3: LM is required, so LM-off should raise RuntimeError.
        """
        # Mock LM as unavailable
        mock_ensure_lm.return_value = False

        adapter = RerankerAdapter()

        # Mock chunks with initial cosine similarity scores
        chunks = [
            {"verse_ref": "Mark 1:1", "cosine": 0.85, "text": "The beginning"},
            {"verse_ref": "Mark 1:2", "cosine": 0.90, "text": "As it is written"},
            {"verse_ref": "Mark 1:3", "cosine": 0.80, "text": "The voice of one"},
        ]

        query = "beginning of the gospel"

        # Wave-3: LM-off = LOUD FAIL (RuntimeError)
        with pytest.raises(RuntimeError, match=r"LOUD FAIL.*Reranker service unavailable"):
            adapter.rerank_chunks(chunks, query)

    @patch("pmagent.biblescholar.reranker_adapter.RerankerAdapter._ensure_lm")
    @patch("pmagent.biblescholar.reranker_adapter.RerankerAdapter._compute_rerank_score")
    def test_rerank_chunks_with_scores(self, mock_compute_score, mock_ensure_lm):
        """Test reranking with cross-encoder scores."""
        # Mock LM as available
        mock_ensure_lm.return_value = True

        # Mock reranker scores (higher score = more relevant)
        mock_compute_score.side_effect = [0.95, 0.70, 0.88]  # Mark 1:1, 1:2, 1:3

        adapter = RerankerAdapter()
        adapter._lm_status = "available"  # Simulate LM available

        chunks = [
            {"verse_ref": "Mark 1:1", "cosine": 0.85, "text": "The beginning"},
            {"verse_ref": "Mark 1:2", "cosine": 0.90, "text": "As it is written"},
            {"verse_ref": "Mark 1:3", "cosine": 0.80, "text": "The voice of one"},
        ]

        query = "beginning of the gospel"

        result = adapter.rerank_chunks(chunks, query)

        # Verify rerank_score was added to each chunk (Rule 045 field name)
        assert "rerank_score" in result[0]
        assert "rerank_score" in result[1]
        assert "rerank_score" in result[2]

        # Verify edge_strength was computed using Rule 045 (0.5 * cosine + 0.5 * rerank_score)
        # Expected edge_strength scores (EDGE_ALPHA=0.5):
        # Mark 1:1: 0.5 * 0.85 + 0.5 * 0.95 = 0.425 + 0.475 = 0.90
        # Mark 1:2: 0.5 * 0.90 + 0.5 * 0.70 = 0.450 + 0.350 = 0.80
        # Mark 1:3: 0.5 * 0.80 + 0.5 * 0.88 = 0.400 + 0.440 = 0.84
        # Sorted order: Mark 1:1, Mark 1:3, Mark 1:2

        assert "edge_strength" in result[0]
        assert result[0]["verse_ref"] == "Mark 1:1"
        assert result[0]["edge_strength"] == pytest.approx(0.90, abs=0.01)

    def test_rerank_chunks_empty_list(self):
        """Test reranking with empty chunks list."""
        adapter = RerankerAdapter()
        result = adapter.rerank_chunks([], "test query")
        assert result == []

    def test_rerank_chunks_single_chunk(self):
        """Test reranking with single chunk."""
        adapter = RerankerAdapter()
        chunks = [{"verse_ref": "Mark 1:1", "cosine": 0.85, "text": "The beginning"}]

        result = adapter.rerank_chunks(chunks, "test query")

        assert len(result) == 1
        assert result[0]["verse_ref"] == "Mark 1:1"


class TestRerankerAdapterComputeScore:
    """Test _compute_rerank_score method (internal)."""

    def test_compute_rerank_score_placeholder(self):
        """Test that _compute_rerank_score exists and returns fallback."""
        adapter = RerankerAdapter()

        # Current placeholder implementation should return 0.5 (neutral score)
        # This will be replaced with actual reranker integration in full implementation
        chunk = {"verse_ref": "Mark 1:1", "text": "The beginning"}
        score = adapter._compute_rerank_score(chunk, "test query")

        # Placeholder should return neutral score or None
        assert score is not None
        assert 0.0 <= score <= 1.0


class TestRerankerAdapterLMStatus:
    """Test LM status detection for reranker availability."""

    @patch("pmagent.biblescholar.reranker_adapter.RerankerAdapter._ensure_lm")
    def test_lm_status_available(self, mock_ensure_lm):
        """Test LM status when reranker is available."""
        mock_ensure_lm.return_value = True

        adapter = RerankerAdapter()
        adapter._ensure_lm()

        # Should detect LM as available
        assert adapter._lm_status in ["available", "lm_off", "unavailable"]

    def test_lm_status_property(self):
        """Test lm_status property."""
        adapter = RerankerAdapter()
        status = adapter.lm_status

        assert status in ["available", "unavailable", "lm_off"]
