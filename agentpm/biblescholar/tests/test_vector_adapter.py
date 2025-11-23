"""Tests for vector_adapter module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from sqlalchemy import Engine
from sqlalchemy.exc import OperationalError

from agentpm.biblescholar.vector_adapter import BibleVectorAdapter, VerseSimilarityResult


class TestBibleVectorAdapter:
    """Test BibleVectorAdapter read-only operations."""

    def test_adapter_initialization(self):
        """Test adapter initializes with db_off status."""
        adapter = BibleVectorAdapter()
        assert adapter._engine is None
        assert adapter._db_status == "db_off"

    @patch("agentpm.biblescholar.vector_adapter.get_bible_engine")
    def test_find_similar_by_verse_id_success(self, mock_get_engine):
        """Test successful similarity search by verse_id."""
        # Mock engine and connection
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()

        # Mock source verse query
        mock_source_result = MagicMock()
        mock_source_row = ([0.1] * 768,)  # Mock embedding vector
        mock_source_result.fetchone.return_value = mock_source_row

        # Mock similarity query
        mock_similarity_result = MagicMock()
        mock_similarity_rows = [
            (2, "Genesis", 1, 2, "And the earth was without form", "KJV", 0.95),
            (3, "Genesis", 1, 3, "And God said", "KJV", 0.92),
        ]
        mock_similarity_result.__iter__.return_value = iter(mock_similarity_rows)

        # Set up connection context manager
        mock_conn.execute.side_effect = [mock_source_result, mock_similarity_result]
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = BibleVectorAdapter()
        results = adapter.find_similar_by_verse(verse_id=1, limit=10)

        assert len(results) == 2
        assert isinstance(results[0], VerseSimilarityResult)
        assert results[0].verse_id == 2
        assert results[0].similarity_score == 0.95
        assert adapter.db_status == "available"

    @patch("agentpm.biblescholar.vector_adapter.get_bible_engine")
    def test_find_similar_by_verse_id_no_embedding(self, mock_get_engine):
        """Test verse with no embedding returns empty list."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_source_result = MagicMock()
        mock_source_result.fetchone.return_value = None  # Verse not found
        mock_conn.execute.return_value = mock_source_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = BibleVectorAdapter()
        results = adapter.find_similar_by_verse(verse_id=99999, limit=10)

        assert results == []

    @patch("agentpm.biblescholar.vector_adapter.get_bible_engine")
    def test_find_similar_by_verse_id_null_embedding(self, mock_get_engine):
        """Test verse with null embedding returns empty list."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_source_result = MagicMock()
        mock_source_row = (None,)  # Null embedding
        mock_source_result.fetchone.return_value = mock_source_row
        mock_conn.execute.return_value = mock_source_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = BibleVectorAdapter()
        results = adapter.find_similar_by_verse(verse_id=1, limit=10)

        assert results == []

    @patch("agentpm.biblescholar.vector_adapter.get_bible_engine")
    def test_find_similar_by_ref_success(self, mock_get_engine):
        """Test successful similarity search by reference."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()

        # Mock source verse query (verse_id + embedding)
        mock_source_result = MagicMock()
        mock_source_row = (1, [0.1] * 768)  # verse_id, embedding
        mock_source_result.fetchone.return_value = mock_source_row

        # Mock similarity query
        mock_similarity_result = MagicMock()
        mock_similarity_rows = [
            (2, "Genesis", 1, 2, "And the earth was without form", "KJV", 0.95),
        ]
        mock_similarity_result.__iter__.return_value = iter(mock_similarity_rows)

        mock_conn.execute.side_effect = [mock_source_result, mock_similarity_result]
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = BibleVectorAdapter()
        results = adapter.find_similar_by_ref("Genesis", 1, 1, "KJV", limit=10)

        assert len(results) == 1
        assert results[0].verse_id == 2
        assert results[0].book_name == "Genesis"
        assert results[0].similarity_score == 0.95

    @patch("agentpm.biblescholar.vector_adapter.get_bible_engine")
    def test_find_similar_by_ref_not_found(self, mock_get_engine):
        """Test reference not found returns empty list."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_source_result = MagicMock()
        mock_source_result.fetchone.return_value = None
        mock_conn.execute.return_value = mock_source_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = BibleVectorAdapter()
        results = adapter.find_similar_by_ref("InvalidBook", 999, 999, "KJV", limit=10)

        assert results == []

    @patch("agentpm.biblescholar.vector_adapter.get_bible_engine")
    def test_find_similar_by_verse_id_with_translation_filter(self, mock_get_engine):
        """Test similarity search with translation filter."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()

        mock_source_result = MagicMock()
        mock_source_row = ([0.1] * 768,)
        mock_source_result.fetchone.return_value = mock_source_row

        mock_similarity_result = MagicMock()
        mock_similarity_rows = [
            (2, "Genesis", 1, 2, "And the earth was without form", "ESV", 0.95),
        ]
        mock_similarity_result.__iter__.return_value = iter(mock_similarity_rows)

        mock_conn.execute.side_effect = [mock_source_result, mock_similarity_result]
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = BibleVectorAdapter()
        results = adapter.find_similar_by_verse(verse_id=1, limit=10, translation_source="ESV")

        assert len(results) == 1
        assert results[0].translation_source == "ESV"

    @patch("agentpm.biblescholar.vector_adapter.get_bible_engine")
    def test_db_unavailable_handling(self, mock_get_engine):
        """Test DB unavailable returns empty list."""
        from agentpm.db.loader import DbUnavailableError

        mock_get_engine.side_effect = DbUnavailableError("DB not configured")

        adapter = BibleVectorAdapter()
        results = adapter.find_similar_by_verse(verse_id=1, limit=10)

        assert results == []
        assert adapter.db_status == "db_off"

    @patch("agentpm.biblescholar.vector_adapter.get_bible_engine")
    def test_operational_error_handling(self, mock_get_engine):
        """Test operational error sets status to unavailable."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = OperationalError("Connection failed", None, None)
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = BibleVectorAdapter()
        results = adapter.find_similar_by_verse(verse_id=1, limit=10)

        assert results == []
        assert adapter.db_status == "unavailable"

    @patch("agentpm.biblescholar.vector_adapter.get_bible_engine")
    def test_db_status_property(self, mock_get_engine):
        """Test db_status property updates status."""
        from agentpm.db.loader import DbUnavailableError

        mock_get_engine.side_effect = DbUnavailableError("DB not configured")

        adapter = BibleVectorAdapter()
        assert adapter.db_status == "db_off"
