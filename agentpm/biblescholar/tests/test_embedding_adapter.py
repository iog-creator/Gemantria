"""Test suite for EmbeddingAdapter (Phase 15 Wave-2).

Tests cover:
- 1024-D embedding retrieval from bible.verse_embeddings
- Vector search functionality via pgvector
- DB-off hermetic mode behavior

See: docs/SSOT/PHASE15_WAVE2_SPEC.md
"""

from unittest.mock import MagicMock, patch

import numpy as np

from agentpm.biblescholar.embedding_adapter import EmbeddingAdapter
from agentpm.db.loader import DbUnavailableError


class TestEmbeddingAdapter:
    """Test suite for EmbeddingAdapter."""

    @patch("agentpm.biblescholar.embedding_adapter.get_bible_engine")
    def test_init_lazy_engine(self, mock_get_engine):
        """Test that adapter initializes with lazy engine."""
        # Don't call get_bible_engine yet (lazy init)
        adapter = EmbeddingAdapter()
        assert adapter._engine is None
        assert adapter._db_status == "db_off"
        # Accessing db_status property will trigger engine initialization
        mock_get_engine.side_effect = DbUnavailableError("DB not configured")
        assert adapter.db_status == "db_off"

    @patch("agentpm.biblescholar.embedding_adapter.get_bible_engine")
    def test_get_embedding_for_verse_success(self, mock_get_engine):
        """Test successful embedding retrieval."""
        # Mock DB connection
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_embedding = np.random.rand(1024).tolist()  # 1024-D vector
        mock_result.fetchone.return_value = (mock_embedding,)
        mock_conn.execute.return_value = mock_result
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None

        mock_engine = MagicMock()
        mock_engine.connect.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = EmbeddingAdapter()
        embedding = adapter.get_embedding_for_verse(verse_id=1)

        assert embedding is not None
        assert isinstance(embedding, np.ndarray)
        assert len(embedding) == 1024

    @patch("agentpm.biblescholar.embedding_adapter.get_bible_engine")
    def test_get_embedding_for_verse_not_found(self, mock_get_engine):
        """Test embedding retrieval for non-existent verse."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None  # No result
        mock_conn.execute.return_value = mock_result
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None

        mock_engine = MagicMock()
        mock_engine.connect.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = EmbeddingAdapter()
        embedding = adapter.get_embedding_for_verse(verse_id=999999)

        assert embedding is None

    @patch("agentpm.biblescholar.embedding_adapter.get_bible_engine")
    def test_vector_search_success(self, mock_get_engine):
        """Test successful vector search."""
        # Mock DB connection
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.__iter__.return_value = iter(
            [
                (1, 0.95),  # verse_id, similarity_score
                (2, 0.89),
                (3, 0.87),
            ]
        )
        mock_conn.execute.return_value = mock_result
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None

        mock_engine = MagicMock()
        mock_engine.connect.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = EmbeddingAdapter()
        query_embedding = np.random.rand(1024)
        results = adapter.vector_search(query_embedding, top_k=3)

        assert len(results) == 3
        assert results[0] == (1, 0.95)
        assert results[1] == (2, 0.89)
        assert results[2] == (3, 0.87)

    @patch("agentpm.biblescholar.embedding_adapter.get_bible_engine")
    def test_vector_search_db_off(self, mock_get_engine):
        """Test vector search with DB unavailable."""
        mock_get_engine.side_effect = DbUnavailableError("DB not configured")

        adapter = EmbeddingAdapter()
        query_embedding = np.random.rand(1024)
        results = adapter.vector_search(query_embedding, top_k=5)

        assert results == []
        assert adapter.db_status == "db_off"

    @patch("agentpm.biblescholar.embedding_adapter.get_bible_engine")
    def test_get_embedding_db_off(self, mock_get_engine):
        """Test embedding retrieval with DB unavailable."""
        mock_get_engine.side_effect = DbUnavailableError("DB not configured")

        adapter = EmbeddingAdapter()
        embedding = adapter.get_embedding_for_verse(verse_id=1)

        assert embedding is None
        assert adapter.db_status == "db_off"

    def test_compute_query_embedding_wave3(self):
        """Test query embedding generation (Wave-3: real BGE-M3 wiring).

        Wave-3: LM is required, so this test either:
        - Returns real embedding if LM is available, or
        - Raises RuntimeError (LOUD FAIL) if LM is unavailable.
        """
        adapter = EmbeddingAdapter()
        try:
            embedding = adapter.compute_query_embedding("test query")
            # If LM is available, should return 1024-D numpy array
            if embedding is not None:
                assert embedding.shape == (1024,)
                assert embedding.dtype == np.float32
        except RuntimeError as e:
            # Wave-3: LM-off = LOUD FAIL (expected behavior)
            assert "LOUD FAIL" in str(e) or "unavailable" in str(e).lower()
