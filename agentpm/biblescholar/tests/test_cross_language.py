"""Tests for Cross-Language Lemma Resolution (Phase 14 PR 14.3)."""

import json
from unittest.mock import patch

import pytest

from agentpm.biblescholar.cross_language_flow import resolve_cross_language_lemma
from agentpm.biblescholar.lexicon_adapter import LexiconEntry


class TestCrossLanguageResolution:
    """Test Greek-to-Hebrew lemma resolution logic."""

    @pytest.fixture
    def mock_mapping_file(self, tmp_path):
        """Create a temporary mapping file."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        mapping_file = config_dir / "greek_to_hebrew_strongs.json"

        data = {
            "schema": "gemantria/greek-hebrew-map.v1",
            "mappings": {
                "G2316": "H430",  # Theos -> Elohim
                "G9999": "H9999",  # Mapped but no DB entry
            },
        }
        mapping_file.write_text(json.dumps(data))
        return str(mapping_file)

    @patch("agentpm.biblescholar.cross_language_flow.LexiconAdapter")
    def test_resolve_successful_mapping(self, MockAdapter, mock_mapping_file):
        """Test successful resolution of a mapped Greek term."""
        # Setup mock adapter
        mock_instance = MockAdapter.return_value
        mock_instance.get_hebrew_entry.return_value = LexiconEntry(
            entry_id=1,
            strongs_id="H430",
            lemma="אֱלֹהִים",
            transliteration="Elohim",
            definition="God",
            usage="",
            gloss="God",
        )

        # Patch the mapping file path
        with patch("agentpm.biblescholar.cross_language_flow.MAPPING_FILE", mock_mapping_file):
            result = resolve_cross_language_lemma("G2316")

        assert result is not None
        assert result["greek_strongs"] == "G2316"
        assert result["hebrew_strongs"] == "H430"
        assert result["hebrew_lemma"] == "אֱלֹהִים"
        assert result["mapping_source"] == "static_map"

        # Verify adapter called correctly
        mock_instance.get_hebrew_entry.assert_called_once_with("H430")

    def test_resolve_unmapped_term(self, mock_mapping_file):
        """Test resolution returns None for unmapped term."""
        with patch("agentpm.biblescholar.cross_language_flow.MAPPING_FILE", mock_mapping_file):
            result = resolve_cross_language_lemma("G1234")  # Not in mapping

        assert result is None

    @patch("agentpm.biblescholar.cross_language_flow.LexiconAdapter")
    def test_resolve_mapped_but_no_hebrew_entry(self, MockAdapter, mock_mapping_file):
        """Test mapped term where Hebrew DB entry is missing."""
        mock_instance = MockAdapter.return_value
        mock_instance.get_hebrew_entry.return_value = None  # DB miss

        with patch("agentpm.biblescholar.cross_language_flow.MAPPING_FILE", mock_mapping_file):
            result = resolve_cross_language_lemma("G9999")

        assert result is not None
        assert result["greek_strongs"] == "G9999"
        assert result["hebrew_strongs"] == "H9999"
        assert result["hebrew_lemma"] is None  # Should be None if DB lookup fails

    def test_missing_mapping_file(self):
        """Test graceful failure when mapping file doesn't exist."""
        with patch("agentpm.biblescholar.cross_language_flow.MAPPING_FILE", "non_existent.json"):
            result = resolve_cross_language_lemma("G2316")

        assert result is None
