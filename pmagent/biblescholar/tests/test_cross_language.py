"""Tests for Cross-Language Lemma Resolution (Phase 14 PR 14.3)."""

import json
from unittest.mock import MagicMock, patch

import pytest

from pmagent.biblescholar.cross_language_flow import resolve_cross_language_lemma


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

    @patch("pmagent.biblescholar.cross_language_flow.LexiconAdapter")
    def test_resolve_successful_mapping(self, MockAdapter, mock_mapping_file):
        """Test successful resolution of a mapped Greek term."""
        # Setup mock adapter with engine and connection chain
        mock_instance = MockAdapter.return_value
        mock_instance._ensure_engine.return_value = True

        # Mock the engine connection chain
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_row = ("אֱלֹהִים",)  # Hebrew lemma
        mock_result.fetchone.return_value = mock_row
        mock_conn.execute.return_value = mock_result
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=None)

        mock_engine = MagicMock()
        mock_engine.connect.return_value = mock_conn
        mock_instance._engine = mock_engine

        # Patch the mapping file path
        with patch("pmagent.biblescholar.cross_language_flow.MAPPING_FILE", mock_mapping_file):
            result = resolve_cross_language_lemma("G2316")

        assert result is not None
        assert result["greek_strongs"] == "G2316"
        assert result["hebrew_strongs"] == "H430"
        assert result["hebrew_lemma"] == "אֱלֹהִים"
        assert result["mapping_source"] == "static_map"

    def test_resolve_unmapped_term(self, mock_mapping_file):
        """Test resolution returns None for unmapped term."""
        with patch("pmagent.biblescholar.cross_language_flow.MAPPING_FILE", mock_mapping_file):
            result = resolve_cross_language_lemma("G1234")  # Not in mapping

        assert result is None

    @patch("pmagent.biblescholar.cross_language_flow.LexiconAdapter")
    def test_resolve_mapped_but_no_hebrew_entry(self, MockAdapter, mock_mapping_file):
        """Test mapped term where Hebrew DB entry is missing."""
        # Setup mock adapter with engine but no result
        mock_instance = MockAdapter.return_value
        mock_instance._ensure_engine.return_value = True

        # Mock the engine connection chain with no result
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None  # No DB entry found
        mock_conn.execute.return_value = mock_result
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=None)

        mock_engine = MagicMock()
        mock_engine.connect.return_value = mock_conn
        mock_instance._engine = mock_engine

        with patch("pmagent.biblescholar.cross_language_flow.MAPPING_FILE", mock_mapping_file):
            result = resolve_cross_language_lemma("G9999")

        # When DB lookup fails, the function returns None (not a partial result)
        assert result is None

    def test_missing_mapping_file(self):
        """Test graceful failure when mapping file doesn't exist."""
        with patch("pmagent.biblescholar.cross_language_flow.MAPPING_FILE", "non_existent.json"):
            result = resolve_cross_language_lemma("G2316")

        assert result is None
