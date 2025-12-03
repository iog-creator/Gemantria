"""Tests for bible_db_adapter module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from sqlalchemy import Engine
from sqlalchemy.exc import OperationalError

from pmagent.biblescholar.bible_db_adapter import BibleDbAdapter, VerseRecord


class TestBibleDbAdapter:
    """Test BibleDbAdapter read-only operations."""

    def test_adapter_initialization(self):
        """Test adapter initializes with db_off status."""
        adapter = BibleDbAdapter()
        assert adapter._engine is None
        assert adapter._db_status == "db_off"

    @patch("pmagent.biblescholar.bible_db_adapter.get_bible_engine")
    def test_get_verse_success(self, mock_get_engine):
        """Test successful verse retrieval."""
        # Mock engine and connection
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_row = MagicMock()

        mock_row.__getitem__.side_effect = lambda i: {
            0: 1,  # verse_id
            1: "Genesis",  # book_name
            2: 1,  # chapter_num
            3: 1,  # verse_num
            4: "In the beginning",  # text
            5: "KJV",  # translation_source
        }[i]

        mock_result.fetchone.return_value = mock_row
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = BibleDbAdapter()
        verse = adapter.get_verse("Genesis", 1, 1, "KJV")

        assert verse is not None
        assert isinstance(verse, VerseRecord)
        assert verse.verse_id == 1
        assert verse.book_name == "Genesis"
        assert verse.chapter_num == 1
        assert verse.verse_num == 1
        assert verse.text == "In the beginning"
        assert verse.translation_source == "KJV"

    @patch("pmagent.biblescholar.bible_db_adapter.get_bible_engine")
    def test_get_verse_not_found(self, mock_get_engine):
        """Test verse not found returns None."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_result = MagicMock()

        mock_result.fetchone.return_value = None
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = BibleDbAdapter()
        verse = adapter.get_verse("Genesis", 1, 999, "KJV")

        assert verse is None

    @patch("pmagent.biblescholar.bible_db_adapter.get_bible_engine")
    def test_get_verse_db_unavailable(self, mock_get_engine):
        """Test DB unavailable returns None."""
        mock_get_engine.side_effect = OperationalError("Connection failed", None, None)

        adapter = BibleDbAdapter()
        verse = adapter.get_verse("Genesis", 1, 1, "KJV")

        assert verse is None
        assert adapter.db_status == "unavailable"

    @patch("pmagent.biblescholar.bible_db_adapter.get_bible_engine")
    def test_get_verse_db_off(self, mock_get_engine):
        """Test DB off (DSN not set) returns None."""
        from pmagent.db.loader import DbUnavailableError

        mock_get_engine.side_effect = DbUnavailableError("BIBLE_DB_DSN not set")

        adapter = BibleDbAdapter()
        verse = adapter.get_verse("Genesis", 1, 1, "KJV")

        assert verse is None
        assert adapter.db_status == "db_off"

    @patch("pmagent.biblescholar.bible_db_adapter.get_bible_engine")
    def test_get_passage_success(self, mock_get_engine):
        """Test successful passage retrieval."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_result = MagicMock()

        # Mock multiple rows
        mock_rows = [
            MagicMock(),
            MagicMock(),
        ]

        mock_rows[0].__getitem__.side_effect = lambda i: {
            0: 1,
            1: "Genesis",
            2: 1,
            3: 1,
            4: "Verse 1",
            5: "KJV",
        }[i]

        mock_rows[1].__getitem__.side_effect = lambda i: {
            0: 2,
            1: "Genesis",
            2: 1,
            3: 2,
            4: "Verse 2",
            5: "KJV",
        }[i]

        mock_result.__iter__.return_value = iter(mock_rows)
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = BibleDbAdapter()
        verses = adapter.get_passage("Genesis", 1, 1, 1, 2, "KJV")

        assert len(verses) == 2
        assert all(isinstance(v, VerseRecord) for v in verses)
        assert verses[0].verse_num == 1
        assert verses[1].verse_num == 2

    @patch("pmagent.biblescholar.bible_db_adapter.get_bible_engine")
    def test_get_passage_empty(self, mock_get_engine):
        """Test passage with no results returns empty list."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_result = MagicMock()

        mock_result.__iter__.return_value = iter([])
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = BibleDbAdapter()
        verses = adapter.get_passage("Genesis", 1, 999, 1, 1000, "KJV")

        assert verses == []

    @patch("pmagent.biblescholar.bible_db_adapter.get_bible_engine")
    def test_db_status_property(self, mock_get_engine):
        """Test db_status property updates correctly."""
        mock_engine = MagicMock(spec=Engine)
        mock_get_engine.return_value = mock_engine

        adapter = BibleDbAdapter()
        status = adapter.db_status

        assert status == "available"
        mock_get_engine.assert_called_once()

    @patch("pmagent.biblescholar.bible_db_adapter.get_bible_engine")
    def test_search_verses_success(self, mock_get_engine):
        """Test successful verse search."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_result = MagicMock()

        # Mock multiple rows
        mock_rows = [
            MagicMock(),
            MagicMock(),
        ]

        mock_rows[0].__getitem__.side_effect = lambda i: {
            0: 1,
            1: "Genesis",
            2: 1,
            3: 1,
            4: "In the beginning God created",
            5: "KJV",
        }[i]

        mock_rows[1].__getitem__.side_effect = lambda i: {
            0: 2,
            1: "John",
            2: 1,
            3: 1,
            4: "In the beginning was the Word",
            5: "KJV",
        }[i]

        mock_result.__iter__.return_value = iter(mock_rows)
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = BibleDbAdapter()
        verses = adapter.search_verses("beginning", "KJV", 20)

        assert len(verses) == 2
        assert all(isinstance(v, VerseRecord) for v in verses)
        assert verses[0].book_name == "Genesis"
        assert verses[1].book_name == "John"
        # Verify query was called with ILIKE pattern
        call_args = mock_conn.execute.call_args
        assert "%beginning%" in str(call_args)

    @patch("pmagent.biblescholar.bible_db_adapter.get_bible_engine")
    def test_search_verses_no_results(self, mock_get_engine):
        """Test search with no results returns empty list."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_result = MagicMock()

        mock_result.__iter__.return_value = iter([])
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = BibleDbAdapter()
        verses = adapter.search_verses("nonexistentword", "KJV", 20)

        assert verses == []

    @patch("pmagent.biblescholar.bible_db_adapter.get_bible_engine")
    def test_search_verses_with_limit(self, mock_get_engine):
        """Test search respects limit parameter."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_result = MagicMock()

        mock_result.__iter__.return_value = iter([])
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        adapter = BibleDbAdapter()
        adapter.search_verses("test", "KJV", limit=10)

        # Verify limit was passed to query parameters
        call_args = mock_conn.execute.call_args
        # call_args[0] contains positional args: (query_text, params_dict)
        params = call_args[0][1]
        assert params["limit"] == 10

    @patch("pmagent.biblescholar.bible_db_adapter.get_bible_engine")
    def test_search_verses_db_unavailable(self, mock_get_engine):
        """Test DB unavailable returns empty list."""
        mock_get_engine.side_effect = OperationalError("Connection failed", None, None)

        adapter = BibleDbAdapter()
        verses = adapter.search_verses("test", "KJV")

        assert verses == []
        assert adapter.db_status == "unavailable"

    @patch("pmagent.biblescholar.bible_db_adapter.get_bible_engine")
    def test_search_verses_db_off(self, mock_get_engine):
        """Test DB off (DSN not set) returns empty list."""
        from pmagent.db.loader import DbUnavailableError

        mock_get_engine.side_effect = DbUnavailableError("BIBLE_DB_DSN not set")

        adapter = BibleDbAdapter()
        verses = adapter.search_verses("test", "KJV")

        assert verses == []
        assert adapter.db_status == "db_off"

    def test_adapter_no_write_methods(self):
        """Test that adapter only exposes read methods (no INSERT/UPDATE/DELETE)."""
        adapter = BibleDbAdapter()

        # Verify no write-related methods
        write_keywords = {"insert", "update", "delete", "create", "save", "write"}
        all_methods = {name for name in dir(adapter) if not name.startswith("__")}
        adapter_methods = {m.lower() for m in all_methods if callable(getattr(adapter, m, None))}

        for keyword in write_keywords:
            assert keyword not in adapter_methods, f"Found write method with keyword: {keyword}"
