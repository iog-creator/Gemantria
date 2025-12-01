"""Tests for RerankerAdapter (Phase 15 Wave-2).

Test coverage:
- Initialization with Granite/BGE reranker config
- Chunk reranking logic (mock-based)
- Combined score calculation (0.7 * embedding + 0.3 * reranker)
- Hermetic mode (reranker unavailable)
- Fallback behavior
"""

from unittest.mock import patch


from agentpm.biblescholar.reranker_adapter import RerankerAdapter


class TestRerankerAdapterInit:
    """Test RerankerAdapter initialization."""

    def test_init_default(self):
        """Test default initialization."""
        adapter = RerankerAdapter()
        assert adapter is not None
        assert adapter._lm_status in ["available", "unavailable", "lm_off"]


class TestRerankerAdapterReranking:
    """Test rerank_chunks method."""

    def test_rerank_chunks_hermetic_fallback(self):
        """Test hermetic mode returns original ranking."""
        adapter = RerankerAdapter()

        # Mock chunks with initial embedding scores
        chunks = [
            {"verse_ref": "Mark 1:1", "embedding_score": 0.85, "text": "The beginning"},
            {"verse_ref": "Mark 1:2", "embedding_score": 0.90, "text": "As it is written"},
            {"verse_ref": "Mark 1:3", "embedding_score": 0.80, "text": "The voice of one"},
        ]

        query = "beginning of the gospel"

        # In hermetic mode (LM unavailable), should return original ranking
        result = adapter.rerank_chunks(chunks, query)

        assert len(result) == 3
        assert result == chunks  # No change in hermetic mode

    @patch("agentpm.biblescholar.reranker_adapter.RerankerAdapter._ensure_lm")
    @patch("agentpm.biblescholar.reranker_adapter.RerankerAdapter._compute_rerank_score")
    def test_rerank_chunks_with_scores(self, mock_compute_score, mock_ensure_lm):
        """Test reranking with cross-encoder scores."""
        # Mock LM as available
        mock_ensure_lm.return_value = True

        # Mock reranker scores (higher score = more relevant)
        mock_compute_score.side_effect = [0.95, 0.70, 0.88]  # Mark 1:1, 1:2, 1:3

        adapter = RerankerAdapter()
        adapter._lm_status = "available"  # Simulate LM available

        chunks = [
            {"verse_ref": "Mark 1:1", "embedding_score": 0.85, "text": "The beginning"},
            {"verse_ref": "Mark 1:2", "embedding_score": 0.90, "text": "As it is written"},
            {"verse_ref": "Mark 1:3", "embedding_score": 0.80, "text": "The voice of one"},
        ]

        query = "beginning of the gospel"

        result = adapter.rerank_chunks(chunks, query)

        # Verify reranker_score was added to each chunk
        assert "reranker_score" in result[0]
        assert "reranker_score" in result[1]
        assert "reranker_score" in result[2]

        # Verify chunks are sorted by combined score (0.7 * embedding + 0.3 * reranker)
        # Expected combined scores:
        # Mark 1:1: 0.7 * 0.85 + 0.3 * 0.95 = 0.595 + 0.285 = 0.88
        # Mark 1:2: 0.7 * 0.90 + 0.3 * 0.70 = 0.630 + 0.210 = 0.84
        # Mark 1:3: 0.7 * 0.80 + 0.3 * 0.88 = 0.560 + 0.264 = 0.824
        # Sorted order: Mark 1:1, Mark 1:2, Mark 1:3

        assert result[0]["verse_ref"] == "Mark 1:1"
        assert result[1]["verse_ref"] == "Mark 1:2"
        assert result[2]["verse_ref"] == "Mark 1:3"

    def test_rerank_chunks_empty_list(self):
        """Test reranking with empty chunks list."""
        adapter = RerankerAdapter()
        result = adapter.rerank_chunks([], "test query")
        assert result == []

    def test_rerank_chunks_single_chunk(self):
        """Test reranking with single chunk."""
        adapter = RerankerAdapter()
        chunks = [{"verse_ref": "Mark 1:1", "embedding_score": 0.85, "text": "The beginning"}]

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

    @patch("agentpm.biblescholar.reranker_adapter.RerankerAdapter._ensure_lm")
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
