"""Tests for lexicon_flow module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from agentpm.biblescholar.lexicon_adapter import LexiconAdapter, LexiconEntry
from agentpm.biblescholar.lexicon_flow import (
    fetch_lexicon_entry,
    fetch_word_study,
    get_db_status,
    WordStudyResult,
)


class TestFetchLexiconEntry:
    """Test fetch_lexicon_entry function."""

    @patch("agentpm.biblescholar.lexicon_flow.LexiconAdapter")
    def test_fetch_hebrew_entry(self, mock_adapter_class):
        """Test fetching Hebrew entry by Strong's ID."""
        mock_adapter = MagicMock(spec=LexiconAdapter)
        mock_entry = LexiconEntry(1, "H1", "בראשית", None, None, None, None)
        mock_adapter.get_hebrew_entry.return_value = mock_entry
        mock_adapter_class.return_value = mock_adapter

        result = fetch_lexicon_entry("H1")

        assert result == mock_entry
        mock_adapter.get_hebrew_entry.assert_called_once_with("H1")
        mock_adapter.get_greek_entry.assert_not_called()

    @patch("agentpm.biblescholar.lexicon_flow.LexiconAdapter")
    def test_fetch_greek_entry(self, mock_adapter_class):
        """Test fetching Greek entry by Strong's ID."""
        mock_adapter = MagicMock(spec=LexiconAdapter)
        mock_entry = LexiconEntry(1, "G1", "α", None, None, None, None)  # noqa: RUF001
        mock_adapter.get_greek_entry.return_value = mock_entry
        mock_adapter_class.return_value = mock_adapter

        result = fetch_lexicon_entry("G1")

        assert result == mock_entry
        mock_adapter.get_greek_entry.assert_called_once_with("G1")
        mock_adapter.get_hebrew_entry.assert_not_called()

    @patch("agentpm.biblescholar.lexicon_flow.LexiconAdapter")
    def test_fetch_entry_no_prefix(self, mock_adapter_class):
        """Test fetching entry without prefix tries both Hebrew and Greek."""
        mock_adapter = MagicMock(spec=LexiconAdapter)
        mock_entry = LexiconEntry(1, "H1", "word", None, None, None, None)
        mock_adapter.get_hebrew_entry.return_value = mock_entry
        mock_adapter.get_greek_entry.return_value = None
        mock_adapter_class.return_value = mock_adapter

        result = fetch_lexicon_entry("1")

        assert result == mock_entry
        mock_adapter.get_hebrew_entry.assert_called_once_with("1")
        # get_greek_entry is only called if get_hebrew_entry returns None
        mock_adapter.get_greek_entry.assert_not_called()

    @patch("agentpm.biblescholar.lexicon_flow.LexiconAdapter")
    def test_fetch_entry_not_found(self, mock_adapter_class):
        """Test entry not found returns None."""
        mock_adapter = MagicMock(spec=LexiconAdapter)
        mock_adapter.get_hebrew_entry.return_value = None
        mock_adapter.get_greek_entry.return_value = None
        mock_adapter_class.return_value = mock_adapter

        result = fetch_lexicon_entry("H99999")

        assert result is None


class TestFetchWordStudy:
    """Test fetch_word_study function."""

    @patch("agentpm.biblescholar.lexicon_flow.LexiconAdapter")
    @patch("agentpm.biblescholar.lexicon_flow.parse_reference")
    def test_fetch_word_study_success(self, mock_parse, mock_adapter_class):
        """Test successful word study retrieval."""
        mock_parse.return_value = ("Genesis", 1, 1)
        mock_adapter = MagicMock(spec=LexiconAdapter)
        mock_entry = LexiconEntry(1, "H1", "word", None, None, None, None)
        mock_adapter.get_entries_for_reference.return_value = [mock_entry]
        mock_adapter.db_status = "available"
        mock_adapter_class.return_value = mock_adapter

        result = fetch_word_study("Genesis 1:1")

        assert isinstance(result, WordStudyResult)
        assert result.reference == "Genesis 1:1"
        assert len(result.entries) == 1
        assert result.entries[0].strongs_id == "H1"
        assert result.db_status == "available"
        mock_adapter.get_entries_for_reference.assert_called_once_with("Genesis", 1, 1)

    @patch("agentpm.biblescholar.lexicon_flow.LexiconAdapter")
    @patch("agentpm.biblescholar.lexicon_flow.parse_reference")
    def test_fetch_word_study_invalid_reference(self, mock_parse, mock_adapter_class):
        """Test invalid reference returns empty result."""
        mock_parse.return_value = None
        mock_adapter = MagicMock(spec=LexiconAdapter)
        mock_adapter.db_status = "db_off"
        mock_adapter_class.return_value = mock_adapter

        result = fetch_word_study("invalid reference")

        assert isinstance(result, WordStudyResult)
        assert result.reference == "invalid reference"
        assert result.entries == []
        assert result.db_status == "db_off"
        mock_adapter.get_entries_for_reference.assert_not_called()

    @patch("agentpm.biblescholar.lexicon_flow.LexiconAdapter")
    @patch("agentpm.biblescholar.lexicon_flow.parse_reference")
    def test_fetch_word_study_no_entries(self, mock_parse, mock_adapter_class):
        """Test verse with no lexicon entries."""
        mock_parse.return_value = ("Genesis", 1, 1)
        mock_adapter = MagicMock(spec=LexiconAdapter)
        mock_adapter.get_entries_for_reference.return_value = []
        mock_adapter.db_status = "available"
        mock_adapter_class.return_value = mock_adapter

        result = fetch_word_study("Genesis 1:1")

        assert isinstance(result, WordStudyResult)
        assert result.entries == []
        assert result.db_status == "available"


class TestGetDbStatus:
    """Test get_db_status function."""

    @patch("agentpm.biblescholar.lexicon_flow.LexiconAdapter")
    def test_get_db_status_with_adapter(self, mock_adapter_class):
        """Test getting status with provided adapter."""
        mock_adapter = MagicMock(spec=LexiconAdapter)
        mock_adapter.db_status = "available"

        result = get_db_status(mock_adapter)

        assert result == "available"
        mock_adapter_class.assert_not_called()

    @patch("agentpm.biblescholar.lexicon_flow.LexiconAdapter")
    def test_get_db_status_without_adapter(self, mock_adapter_class):
        """Test getting status without provided adapter."""
        mock_adapter = MagicMock(spec=LexiconAdapter)
        mock_adapter.db_status = "db_off"
        mock_adapter_class.return_value = mock_adapter

        result = get_db_status()

        assert result == "db_off"
        mock_adapter_class.assert_called_once()
