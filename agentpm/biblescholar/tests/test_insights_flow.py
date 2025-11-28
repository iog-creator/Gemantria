"""Tests for insights_flow module."""

from __future__ import annotations

from unittest.mock import patch

from agentpm.biblescholar.bible_db_adapter import VerseRecord
from agentpm.biblescholar.insights_flow import (
    VerseContext,
    format_context_for_llm,
    get_verse_context,
)
from agentpm.biblescholar.lexicon_adapter import LexiconEntry
from agentpm.biblescholar.lexicon_flow import WordStudyResult
from agentpm.biblescholar.vector_adapter import VerseSimilarityResult


class TestGetVerseContext:
    """Test get_verse_context function."""

    @patch("agentpm.biblescholar.insights_flow.fetch_verse")
    @patch("agentpm.biblescholar.insights_flow.fetch_word_study")
    @patch("agentpm.biblescholar.insights_flow.similar_verses_for_reference")
    def test_get_verse_context_full(self, mock_similar, mock_word_study, mock_fetch_verse):
        """Test fetching full context."""
        # Mock primary verse
        mock_fetch_verse.side_effect = lambda ref, trans: (
            VerseRecord(1, "Genesis", 1, 1, "In the beginning", "KJV")
            if trans == "KJV"
            else VerseRecord(1, "Genesis", 1, 1, "In the beginning...", "ESV")
            if trans == "ESV"
            else None
        )

        # Mock lexicon
        mock_word_study.return_value = WordStudyResult(
            reference="Genesis 1:1",
            entries=[
                LexiconEntry(
                    entry_id=1,
                    strongs_id="H7225",
                    lemma="re'shiyth",
                    transliteration="re'shiyth",
                    definition="beginning",
                    usage="",
                    gloss="beginning",
                )
            ],
            db_status="available",
        )

        # Mock similar verses
        mock_similar.return_value = [
            VerseSimilarityResult(
                verse_id=2,
                book_name="John",
                chapter_num=1,
                verse_num=1,
                text="In the beginning was the Word",
                translation_source="KJV",
                similarity_score=0.9,
            )
        ]

        context = get_verse_context("Genesis 1:1", translations=["ESV"])

        assert context is not None
        assert context.reference == "Genesis 1:1"
        assert context.primary_text == "In the beginning"
        assert context.secondary_texts["ESV"] == "In the beginning..."
        assert len(context.lexicon_entries) == 1
        assert context.lexicon_entries[0].strongs_id == "H7225"
        assert len(context.similar_verses) == 1
        assert context.similar_verses[0].book_name == "John"

    @patch("agentpm.biblescholar.insights_flow.fetch_verse")
    def test_get_verse_context_not_found(self, mock_fetch_verse):
        """Test verse not found returns None."""
        mock_fetch_verse.return_value = None
        context = get_verse_context("Genesis 1:999")
        assert context is None

    @patch("agentpm.biblescholar.insights_flow.fetch_verse")
    @patch("agentpm.biblescholar.insights_flow.fetch_word_study")
    @patch("agentpm.biblescholar.insights_flow.similar_verses_for_reference")
    def test_get_verse_context_minimal(self, mock_similar, mock_word_study, mock_fetch_verse):
        """Test fetching minimal context (no lexicon/similar)."""
        mock_fetch_verse.return_value = VerseRecord(1, "Genesis", 1, 1, "Text", "KJV")

        context = get_verse_context("Genesis 1:1", include_lexicon=False, include_similar=False)

        assert context is not None
        assert context.primary_text == "Text"
        assert len(context.lexicon_entries) == 0
        assert len(context.similar_verses) == 0
        mock_word_study.assert_not_called()
        mock_similar.assert_not_called()


class TestFormatContextForLLM:
    """Test format_context_for_llm function."""

    def test_format_context(self):
        """Test formatting context to markdown."""
        context = VerseContext(
            reference="Genesis 1:1",
            primary_text="In the beginning",
            secondary_texts={"ESV": "In the beginning..."},
            lexicon_entries=[
                LexiconEntry(
                    entry_id=1,
                    strongs_id="H7225",
                    lemma="re'shiyth",
                    transliteration="re'shiyth",
                    definition="beginning",
                    usage="",
                    gloss="beginning",
                )
            ],
            similar_verses=[
                VerseSimilarityResult(
                    verse_id=2,
                    book_name="John",
                    chapter_num=1,
                    verse_num=1,
                    text="In the beginning was the Word",
                    translation_source="KJV",
                    similarity_score=0.9,
                )
            ],
        )

        output = format_context_for_llm(context)

        assert "# Context: Genesis 1:1" in output
        assert "## Text (KJV)" in output
        assert "> In the beginning" in output
        assert "## Other Translations" in output
        assert "**ESV**: In the beginning..." in output
        assert "## Lexicon (Original Language)" in output
        assert "- **re'shiyth** (Hebrew H7225): beginning" in output
        assert "## Similar Verses (Semantic)" in output
        assert "- **John 1:1** (0.90): In the beginning was the Word" in output
