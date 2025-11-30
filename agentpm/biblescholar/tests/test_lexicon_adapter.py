"""Tests for lexicon_adapter module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from sqlalchemy import Engine
from sqlalchemy.exc import OperationalError

from agentpm.biblescholar.lexicon_adapter import LexiconAdapter, LexiconEntry


class TestLexiconAdapter:
    """Test LexiconAdapter read-only operations."""

    def test_adapter_initialization(self):
        """Test adapter initializes with unknown status."""
        adapter = LexiconAdapter()
        assert adapter._engine is None
        assert adapter._db_status == "unknown"

    @patch("agentpm.biblescholar.lexicon_adapter.get_bible_engine")
    def test_get_hebrew_entry_success(self, mock_get_engine):
        """Test successful Hebrew entry retrieval."""
        # Mock engine and connection
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_row = (1, "H1", "בראשית", "bereshit", "In the beginning", "Usage notes", "beginning")
        mock_result.fetchone.return_value = mock_row
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = LexiconAdapter()
        entry = adapter.get_hebrew_entry("H1")

        assert entry is not None
        assert isinstance(entry, LexiconEntry)
        assert entry.strongs_id == "H1"
        assert entry.lemma == "בראשית"
        assert adapter.db_status == "available"

    @patch("agentpm.biblescholar.lexicon_adapter.get_bible_engine")
    def test_get_hebrew_entry_not_found(self, mock_get_engine):
        """Test Hebrew entry not found returns None."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = LexiconAdapter()
        entry = adapter.get_hebrew_entry("H99999")

        assert entry is None

    @patch("agentpm.biblescholar.lexicon_adapter.get_bible_engine")
    def test_get_greek_entry_success(self, mock_get_engine):
        """Test successful Greek entry retrieval."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_row = (1, "G1", "α", "alpha", "First letter", "Usage notes", "alpha")  # noqa: RUF001
        mock_result.fetchone.return_value = mock_row
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = LexiconAdapter()
        entry = adapter.get_greek_entry("G1")

        assert entry is not None
        assert isinstance(entry, LexiconEntry)
        assert entry.strongs_id == "G1"
        assert entry.lemma == "α"  # noqa: RUF001
        assert adapter.db_status == "available"

    @patch("agentpm.biblescholar.lexicon_adapter.get_bible_engine")
    def test_get_greek_entry_not_found(self, mock_get_engine):
        """Test Greek entry not found returns None."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = LexiconAdapter()
        entry = adapter.get_greek_entry("G99999")

        assert entry is None

    @patch("agentpm.biblescholar.lexicon_adapter.get_bible_engine")
    def test_get_entries_for_reference_success(self, mock_get_engine):
        """Test successful retrieval of entries for a verse reference."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()

        # Mock verse query
        verse_result = MagicMock()
        verse_result.fetchone.return_value = (123,)
        mock_conn.execute.return_value = verse_result

        # Mock Hebrew words query
        hebrew_result = MagicMock()
        hebrew_result.__iter__.return_value = [("H1",), ("H2",)]
        mock_conn.execute.side_effect = [verse_result, hebrew_result, MagicMock()]

        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = LexiconAdapter()

        # Mock the get_hebrew_entry calls
        with patch.object(adapter, "get_hebrew_entry") as mock_get_hebrew:
            mock_get_hebrew.side_effect = [
                LexiconEntry(1, "H1", "word1", None, None, None, None),
                LexiconEntry(2, "H2", "word2", None, None, None, None),
            ]

            entries = adapter.get_entries_for_reference("Genesis", 1, 1)

            assert len(entries) == 2
            assert entries[0].strongs_id == "H1"
            assert entries[1].strongs_id == "H2"

    @patch("agentpm.biblescholar.lexicon_adapter.get_bible_engine")
    def test_get_entries_for_reference_verse_not_found(self, mock_get_engine):
        """Test verse not found returns empty list."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = LexiconAdapter()
        entries = adapter.get_entries_for_reference("Invalid", 999, 999)

        assert entries == []

    @patch("agentpm.biblescholar.lexicon_adapter.get_bible_engine")
    def test_db_off_mode(self, mock_get_engine):
        """Test DB-off mode returns None/empty."""
        from agentpm.db.loader import DbUnavailableError

        mock_get_engine.side_effect = DbUnavailableError("DB unavailable")

        adapter = LexiconAdapter()
        entry = adapter.get_hebrew_entry("H1")

        assert entry is None
        assert adapter.db_status == "db_off"

    @patch("agentpm.biblescholar.lexicon_adapter.get_bible_engine")
    def test_operational_error_handling(self, mock_get_engine):
        """Test operational errors are handled gracefully."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = OperationalError("Connection failed", None, None)
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = LexiconAdapter()
        entry = adapter.get_hebrew_entry("H1")

        assert entry is None
        assert adapter.db_status == "unavailable"

    def test_adapter_no_write_methods(self):
        """Test that adapter only exposes read methods (no INSERT/UPDATE/DELETE)."""
        adapter = LexiconAdapter()

        # Check that only read methods exist
        all_methods = {name for name in dir(adapter) if not name.startswith("__")}

        # Verify no write-related methods
        write_keywords = {"insert", "update", "delete", "create", "save", "write"}
        adapter_methods = {m.lower() for m in all_methods if callable(getattr(adapter, m, None))}

        for keyword in write_keywords:
            assert keyword not in adapter_methods, f"Found write method with keyword: {keyword}"
