"""Tests for search_flow module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from pmagent.biblescholar.bible_db_adapter import BibleDbAdapter, VerseRecord
from pmagent.biblescholar.search_flow import get_db_status, search_verses


class TestSearchVerses:
    """Test search_verses function."""

    @patch("pmagent.biblescholar.search_flow.BibleDbAdapter")
    def test_search_verses_success(self, mock_adapter_class):
        """Test successful verse search."""
        mock_adapter = MagicMock(spec=BibleDbAdapter)
        mock_verses = [
            VerseRecord(1, "Genesis", 1, 1, "In the beginning God", "KJV"),
            VerseRecord(2, "John", 1, 1, "In the beginning was the Word", "KJV"),
        ]
        mock_adapter.search_verses.return_value = mock_verses
        mock_adapter_class.return_value = mock_adapter

        result = search_verses("beginning", "KJV", 20)

        assert len(result) == 2
        assert all(isinstance(v, VerseRecord) for v in result)
        mock_adapter.search_verses.assert_called_once_with("beginning", "KJV", 20)

    @patch("pmagent.biblescholar.search_flow.BibleDbAdapter")
    def test_search_verses_empty_query(self, mock_adapter_class):
        """Test empty query returns empty list."""
        result = search_verses("", "KJV")
        assert result == []
        mock_adapter_class.assert_not_called()

    @patch("pmagent.biblescholar.search_flow.BibleDbAdapter")
    def test_search_verses_short_query(self, mock_adapter_class):
        """Test query too short returns empty list."""
        result = search_verses("a", "KJV")  # Only 1 character
        assert result == []
        mock_adapter_class.assert_not_called()

    @patch("pmagent.biblescholar.search_flow.BibleDbAdapter")
    def test_search_verses_whitespace_only(self, mock_adapter_class):
        """Test whitespace-only query returns empty list."""
        result = search_verses("   ", "KJV")
        assert result == []
        mock_adapter_class.assert_not_called()

    @patch("pmagent.biblescholar.search_flow.BibleDbAdapter")
    def test_search_verses_no_results(self, mock_adapter_class):
        """Test search with no results returns empty list."""
        mock_adapter = MagicMock(spec=BibleDbAdapter)
        mock_adapter.search_verses.return_value = []
        mock_adapter_class.return_value = mock_adapter

        result = search_verses("nonexistentword", "KJV")
        assert result == []

    @patch("pmagent.biblescholar.search_flow.BibleDbAdapter")
    def test_search_verses_with_limit(self, mock_adapter_class):
        """Test search respects limit parameter."""
        mock_adapter = MagicMock(spec=BibleDbAdapter)
        mock_adapter.search_verses.return_value = []
        mock_adapter_class.return_value = mock_adapter

        search_verses("test", "KJV", limit=10)
        mock_adapter.search_verses.assert_called_once_with("test", "KJV", 10)

    @patch("pmagent.biblescholar.search_flow.BibleDbAdapter")
    def test_search_verses_strips_query(self, mock_adapter_class):
        """Test search strips whitespace from query."""
        mock_adapter = MagicMock(spec=BibleDbAdapter)
        mock_adapter.search_verses.return_value = []
        mock_adapter_class.return_value = mock_adapter

        search_verses("  test  ", "KJV")
        mock_adapter.search_verses.assert_called_once_with("test", "KJV", 20)

    @patch("pmagent.biblescholar.search_flow.BibleDbAdapter")
    def test_search_verses_db_unavailable(self, mock_adapter_class):
        """Test DB unavailable returns empty list."""
        mock_adapter = MagicMock(spec=BibleDbAdapter)
        mock_adapter.search_verses.return_value = []
        mock_adapter_class.return_value = mock_adapter

        result = search_verses("test", "KJV")
        assert result == []


class TestGetDbStatus:
    """Test get_db_status function."""

    @patch("pmagent.biblescholar.search_flow.BibleDbAdapter")
    def test_get_db_status(self, mock_adapter_class):
        """Test getting database status."""
        mock_adapter = MagicMock(spec=BibleDbAdapter)
        mock_adapter.db_status = "available"
        mock_adapter_class.return_value = mock_adapter

        status = get_db_status()

        assert status == "available"
        mock_adapter_class.assert_called_once()
