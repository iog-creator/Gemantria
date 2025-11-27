"""Tests for bible_passage_flow module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from agentpm.biblescholar.bible_db_adapter import BibleDbAdapter, VerseRecord
from agentpm.biblescholar.bible_passage_flow import (
    fetch_passage,
    fetch_verse,
    get_db_status,
    parse_reference,
)


class TestParseReference:
    """Test reference parsing."""

    def test_parse_reference_success(self):
        """Test successful reference parsing."""
        result = parse_reference("Genesis 1:1")
        assert result == ("Gen", 1, 1)  # Book names are normalized to abbreviations

        result = parse_reference("Matthew 5:3")
        assert result == ("Mat", 5, 3)  # Book names are normalized to abbreviations

        result = parse_reference("Gen 1:1")
        assert result == ("Gen", 1, 1)

    def test_parse_reference_invalid(self):
        """Test invalid reference returns None."""
        assert parse_reference("invalid") is None
        assert parse_reference("") is None
        assert parse_reference("Genesis") is None
        assert parse_reference("1:1") is None


class TestFetchVerse:
    """Test fetch_verse function."""

    @patch("agentpm.biblescholar.bible_passage_flow.BibleDbAdapter")
    def test_fetch_verse_success(self, mock_adapter_class):
        """Test successful verse fetch."""
        mock_adapter = MagicMock(spec=BibleDbAdapter)
        mock_verse = VerseRecord(
            verse_id=1,
            book_name="Genesis",
            chapter_num=1,
            verse_num=1,
            text="In the beginning",
            translation_source="KJV",
        )
        mock_adapter.get_verse.return_value = mock_verse
        mock_adapter_class.return_value = mock_adapter

        result = fetch_verse("Genesis 1:1", "KJV")

        assert result is not None
        assert result.book_name == "Genesis"
        assert result.chapter_num == 1
        assert result.verse_num == 1
        mock_adapter.get_verse.assert_called_once_with("Gen", 1, 1, "KJV")  # Book names are normalized

    @patch("agentpm.biblescholar.bible_passage_flow.BibleDbAdapter")
    def test_fetch_verse_invalid_reference(self, mock_adapter_class):
        """Test invalid reference returns None."""
        result = fetch_verse("invalid reference", "KJV")
        assert result is None
        mock_adapter_class.assert_not_called()

    @patch("agentpm.biblescholar.bible_passage_flow.BibleDbAdapter")
    def test_fetch_verse_not_found(self, mock_adapter_class):
        """Test verse not found returns None."""
        mock_adapter = MagicMock(spec=BibleDbAdapter)
        mock_adapter.get_verse.return_value = None
        mock_adapter_class.return_value = mock_adapter

        result = fetch_verse("Genesis 1:999", "KJV")
        assert result is None


class TestFetchPassage:
    """Test fetch_passage function."""

    @patch("agentpm.biblescholar.bible_passage_flow.BibleDbAdapter")
    def test_fetch_passage_single_verse(self, mock_adapter_class):
        """Test fetching single verse as passage."""
        mock_adapter = MagicMock(spec=BibleDbAdapter)
        mock_verse = VerseRecord(
            verse_id=1,
            book_name="Genesis",
            chapter_num=1,
            verse_num=1,
            text="In the beginning",
            translation_source="KJV",
        )
        mock_adapter.get_verse.return_value = mock_verse
        mock_adapter_class.return_value = mock_adapter

        result = fetch_passage("Genesis 1:1", "KJV")

        assert len(result) == 1
        assert result[0].verse_num == 1

    @patch("agentpm.biblescholar.bible_passage_flow.BibleDbAdapter")
    def test_fetch_passage_range_same_chapter(self, mock_adapter_class):
        """Test fetching verse range within same chapter."""
        mock_adapter = MagicMock(spec=BibleDbAdapter)
        mock_verses = [
            VerseRecord(1, "Genesis", 1, 1, "Verse 1", "KJV"),
            VerseRecord(2, "Genesis", 1, 2, "Verse 2", "KJV"),
            VerseRecord(3, "Genesis", 1, 3, "Verse 3", "KJV"),
        ]
        mock_adapter.get_passage.return_value = mock_verses
        mock_adapter_class.return_value = mock_adapter

        result = fetch_passage("Genesis 1:1-3", "KJV")

        assert len(result) == 3
        mock_adapter.get_passage.assert_called_once_with("Gen", 1, 1, 1, 3, "KJV")  # Book names are normalized

    @patch("agentpm.biblescholar.bible_passage_flow.BibleDbAdapter")
    def test_fetch_passage_range_cross_chapter(self, mock_adapter_class):
        """Test fetching verse range across chapters."""
        mock_adapter = MagicMock(spec=BibleDbAdapter)
        mock_verses = [
            VerseRecord(1, "Genesis", 1, 31, "Verse 31", "KJV"),
            VerseRecord(2, "Genesis", 2, 1, "Verse 1", "KJV"),
            VerseRecord(3, "Genesis", 2, 2, "Verse 2", "KJV"),
        ]
        mock_adapter.get_passage.return_value = mock_verses
        mock_adapter_class.return_value = mock_adapter

        result = fetch_passage("Genesis 1:31-2:2", "KJV")

        assert len(result) == 3
        mock_adapter.get_passage.assert_called_once_with("Gen", 1, 31, 2, 2, "KJV")  # Book names are normalized

    @patch("agentpm.biblescholar.bible_passage_flow.BibleDbAdapter")
    def test_fetch_passage_invalid_reference(self, mock_adapter_class):
        """Test invalid reference returns empty list."""
        mock_adapter = MagicMock(spec=BibleDbAdapter)
        mock_adapter_class.return_value = mock_adapter

        result = fetch_passage("invalid reference", "KJV")
        assert result == []
        # Adapter is created but methods are not called for invalid references
        mock_adapter.get_verse.assert_not_called()
        mock_adapter.get_passage.assert_not_called()

    @patch("agentpm.biblescholar.bible_passage_flow.BibleDbAdapter")
    def test_fetch_passage_not_found(self, mock_adapter_class):
        """Test passage not found returns empty list."""
        mock_adapter = MagicMock(spec=BibleDbAdapter)
        mock_adapter.get_verse.return_value = None
        mock_adapter_class.return_value = mock_adapter

        result = fetch_passage("Genesis 1:999", "KJV")
        assert result == []


class TestGetDbStatus:
    """Test get_db_status function."""

    @patch("agentpm.biblescholar.bible_passage_flow.BibleDbAdapter")
    def test_get_db_status(self, mock_adapter_class):
        """Test getting database status."""
        mock_adapter = MagicMock(spec=BibleDbAdapter)
        mock_adapter.db_status = "available"
        mock_adapter_class.return_value = mock_adapter

        status = get_db_status()

        assert status == "available"
        mock_adapter_class.assert_called_once()


class TestMultiTranslationSupport:
    """Test multi-translation support in passage flow."""

    @patch("agentpm.biblescholar.bible_passage_flow.BibleDbAdapter")
    def test_fetch_verse_multiple_translations(self, mock_adapter_class):
        """Test fetching same verse from multiple translations."""
        mock_adapter = MagicMock(spec=BibleDbAdapter)
        mock_adapter_class.return_value = mock_adapter

        translations = ["KJV", "ESV", "ASV", "YLT"]
        for translation in translations:
            mock_verse = VerseRecord(
                verse_id=1,
                book_name="Genesis",
                chapter_num=1,
                verse_num=1,
                text=f"In the beginning ({translation})",
                translation_source=translation,
            )
            mock_adapter.get_verse.return_value = mock_verse

            result = fetch_verse("Genesis 1:1", translation)

            assert result is not None
            assert result.translation_source == translation
            mock_adapter.get_verse.assert_called_with("Gen", 1, 1, translation)

    @patch("agentpm.biblescholar.bible_passage_flow.BibleDbAdapter")
    def test_fetch_passage_multiple_translations(self, mock_adapter_class):
        """Test fetching passage from multiple translations."""
        mock_adapter = MagicMock(spec=BibleDbAdapter)
        mock_adapter_class.return_value = mock_adapter

        translations = ["KJV", "ESV", "ASV"]
        for translation in translations:
            mock_verses = [
                VerseRecord(1, "Genesis", 1, 1, f"Verse 1 ({translation})", translation),
                VerseRecord(2, "Genesis", 1, 2, f"Verse 2 ({translation})", translation),
            ]
            mock_adapter.get_passage.return_value = mock_verses

            result = fetch_passage("Genesis 1:1-2", translation)

            assert len(result) == 2
            assert all(v.translation_source == translation for v in result)
            mock_adapter.get_passage.assert_called_with("Gen", 1, 1, 1, 2, translation)
