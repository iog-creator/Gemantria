"""Tests for cross_language_flow module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from agentpm.biblescholar.cross_language_flow import (
    CrossLanguageMatch,
    WordAnalysis,
    analyze_word_in_context,
    find_cross_language_connections,
    get_db_status,
)
from agentpm.biblescholar.lexicon_adapter import LexiconAdapter, LexiconEntry
from agentpm.biblescholar.lexicon_flow import WordStudyResult


class TestAnalyzeWordInContext:
    """Test analyze_word_in_context function."""

    @patch("agentpm.biblescholar.cross_language_flow.fetch_word_study")
    @patch("agentpm.biblescholar.cross_language_flow.fetch_lexicon_entry")
    @patch("agentpm.biblescholar.cross_language_flow.LexiconAdapter")
    def test_analyze_word_success(self, mock_adapter_class, mock_fetch_entry, mock_fetch_study):
        """Test successful word analysis."""
        # Mock word study result
        mock_entry = LexiconEntry(
            entry_id=1,
            strongs_id="H1",
            lemma="אָב",
            transliteration="ab",
            definition="father",
            usage=None,
            gloss="father",
        )
        mock_study = WordStudyResult(
            reference="Genesis 1:1",
            entries=[mock_entry],
            db_status="available",
        )
        mock_fetch_study.return_value = mock_study
        mock_fetch_entry.return_value = mock_entry

        # Mock adapter for occurrence queries
        mock_adapter = MagicMock(spec=LexiconAdapter)
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()

        # Mock occurrence query results
        mock_result.__iter__.return_value = iter([("Genesis", 1, 1), ("Genesis", 2, 2)])
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_adapter._engine = mock_engine
        mock_adapter._ensure_engine.return_value = True
        mock_adapter_class.return_value = mock_adapter

        # Mock count query
        mock_count_result = MagicMock()
        mock_count_result.fetchone.return_value = (2,)
        mock_conn.execute.side_effect = [mock_result, mock_count_result]

        result = analyze_word_in_context("Genesis 1:1", "H1")

        assert result is not None
        assert isinstance(result, WordAnalysis)
        assert result.strongs_id == "H1"
        assert result.lemma == "אָב"
        assert result.gloss == "father"
        assert result.occurrence_count == 2
        assert len(result.related_verses) == 2

    @patch("agentpm.biblescholar.cross_language_flow.fetch_word_study")
    def test_analyze_word_not_in_verse(self, mock_fetch_study):
        """Test word not in verse returns None."""
        mock_entry = LexiconEntry(
            entry_id=1,
            strongs_id="H2",
            lemma="אֵם",
            transliteration="em",
            definition="mother",
            usage=None,
            gloss="mother",
        )
        mock_study = WordStudyResult(
            reference="Genesis 1:1",
            entries=[mock_entry],  # Different Strong's ID
            db_status="available",
        )
        mock_fetch_study.return_value = mock_study

        result = analyze_word_in_context("Genesis 1:1", "H1")

        assert result is None

    @patch("agentpm.biblescholar.cross_language_flow.parse_reference")
    def test_analyze_word_invalid_reference(self, mock_parse):
        """Test invalid reference returns None."""
        mock_parse.return_value = None

        result = analyze_word_in_context("invalid", "H1")

        assert result is None

    @patch("agentpm.biblescholar.cross_language_flow.fetch_word_study")
    @patch("agentpm.biblescholar.cross_language_flow.fetch_lexicon_entry")
    @patch("agentpm.biblescholar.cross_language_flow.LexiconAdapter")
    def test_analyze_word_db_off(self, mock_adapter_class, mock_fetch_entry, mock_fetch_study):
        """Test word analysis when DB is off."""
        mock_entry = LexiconEntry(
            entry_id=1,
            strongs_id="H1",
            lemma="אָב",
            transliteration="ab",
            definition="father",
            usage=None,
            gloss="father",
        )
        mock_study = WordStudyResult(
            reference="Genesis 1:1",
            entries=[mock_entry],
            db_status="available",
        )
        mock_fetch_study.return_value = mock_study
        mock_fetch_entry.return_value = mock_entry

        mock_adapter = MagicMock(spec=LexiconAdapter)
        mock_adapter._ensure_engine.return_value = False
        mock_adapter_class.return_value = mock_adapter

        result = analyze_word_in_context("Genesis 1:1", "H1")

        assert result is not None
        assert result.occurrence_count == 0
        assert result.related_verses == []


class TestFindCrossLanguageConnections:
    """Test find_cross_language_connections function."""

    @patch("agentpm.biblescholar.cross_language_flow.fetch_word_study")
    @patch("agentpm.biblescholar.cross_language_flow.fetch_lexicon_entry")
    @patch("agentpm.biblescholar.cross_language_flow.similar_verses_for_reference")
    @patch("agentpm.biblescholar.cross_language_flow.LexiconAdapter")
    def test_find_connections_success(self, mock_adapter_class, mock_similar, mock_fetch_entry, mock_fetch_study):
        """Test successful cross-language connection finding."""
        # Mock word study to validate word exists in reference
        source_entry = LexiconEntry(
            entry_id=1,
            strongs_id="H1",
            lemma="אָב",
            transliteration="ab",
            definition="father",
            usage=None,
            gloss="father",
        )
        mock_study = WordStudyResult(
            reference="Genesis 1:1",
            entries=[source_entry],
            db_status="available",
        )
        mock_fetch_study.return_value = mock_study

        mock_fetch_entry.side_effect = [
            source_entry,  # Source
            LexiconEntry(2, "G1", "alpha", "alpha", "alpha", None, "alpha"),  # Target 1
            LexiconEntry(3, "G2", "beta", "beta", "beta", None, "beta"),  # Target 2
        ]

        # Mock similar verses
        from agentpm.biblescholar.vector_adapter import VerseSimilarityResult

        mock_similar_verses = [
            VerseSimilarityResult(1, "Matthew", 1, 1, "text", "KJV", 0.9),
            VerseSimilarityResult(2, "John", 1, 1, "text", "KJV", 0.8),
        ]
        mock_similar.return_value = mock_similar_verses

        # Mock adapter for database queries
        mock_adapter = MagicMock(spec=LexiconAdapter)
        mock_engine = MagicMock()
        mock_conn = MagicMock()

        # Mock verse_id query
        mock_verse_result = MagicMock()
        mock_verse_result.fetchone.side_effect = [(1,), (2,)]
        mock_conn.execute.return_value = mock_verse_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_adapter._engine = mock_engine
        mock_adapter._ensure_engine.return_value = True
        mock_adapter_class.return_value = mock_adapter

        # Mock Strong's query results
        mock_strongs_result = MagicMock()
        mock_strongs_result.__iter__.return_value = iter([("G1",), ("G2",)])
        mock_conn.execute.side_effect = [
            mock_verse_result,  # First verse_id query
            mock_strongs_result,  # First Strong's query
            mock_verse_result,  # Second verse_id query
            mock_strongs_result,  # Second Strong's query
        ]

        result = find_cross_language_connections("H1", reference="Genesis 1:1", limit=10)

        assert len(result) > 0
        assert all(isinstance(m, CrossLanguageMatch) for m in result)
        assert all(m.source_strongs == "H1" for m in result)
        assert all(m.target_strongs.startswith("G") for m in result)

    @patch("agentpm.biblescholar.cross_language_flow.fetch_lexicon_entry")
    def test_find_connections_no_source_entry(self, mock_fetch_entry):
        """Test when source entry not found returns empty list."""
        mock_fetch_entry.return_value = None

        result = find_cross_language_connections("H999", reference="Genesis 1:1")

        assert result == []

    @patch("agentpm.biblescholar.cross_language_flow.fetch_lexicon_entry")
    @patch("agentpm.biblescholar.cross_language_flow.similar_verses_for_reference")
    def test_find_connections_no_similar_verses(self, mock_similar, mock_fetch_entry):
        """Test when no similar verses found returns empty list."""
        source_entry = LexiconEntry(
            entry_id=1,
            strongs_id="H1",
            lemma="אָב",
            transliteration="ab",
            definition="father",
            usage=None,
            gloss="father",
        )
        mock_fetch_entry.return_value = source_entry
        mock_similar.return_value = []

        result = find_cross_language_connections("H1", reference="Genesis 1:1")

        assert result == []

    @patch("agentpm.biblescholar.cross_language_flow.fetch_lexicon_entry")
    @patch("agentpm.biblescholar.cross_language_flow.fetch_word_study")
    @patch("agentpm.biblescholar.cross_language_flow.LexiconAdapter")
    def test_find_connections_without_reference(self, mock_adapter_class, mock_fetch_study, mock_fetch_entry):
        """Test finding connections without explicit reference."""
        source_entry = LexiconEntry(
            entry_id=1,
            strongs_id="H1",
            lemma="אָב",
            transliteration="ab",
            definition="father",
            usage=None,
            gloss="father",
        )
        mock_fetch_entry.return_value = source_entry

        # Mock adapter to find first occurrence
        mock_adapter = MagicMock(spec=LexiconAdapter)
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = ("Genesis", 1, 1)
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_adapter._engine = mock_engine
        mock_adapter._ensure_engine.return_value = True
        mock_adapter_class.return_value = mock_adapter

        # Mock similar verses (empty for simplicity)
        with patch("agentpm.biblescholar.cross_language_flow.similar_verses_for_reference") as mock_similar:
            mock_similar.return_value = []
            result = find_cross_language_connections("H1", reference=None)

            assert result == []


class TestGetDbStatus:
    """Test get_db_status function."""

    @patch("agentpm.biblescholar.cross_language_flow.LexiconAdapter")
    def test_get_db_status(self, mock_adapter_class):
        """Test getting database status."""
        mock_adapter = MagicMock(spec=LexiconAdapter)
        mock_adapter.db_status = "available"
        mock_adapter_class.return_value = mock_adapter

        status = get_db_status()

        assert status == "available"
        mock_adapter_class.assert_called_once()
