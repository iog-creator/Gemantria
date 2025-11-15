"""Tests for vector_flow module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from agentpm.biblescholar.vector_adapter import VerseSimilarityResult
from agentpm.biblescholar.vector_flow import (
    get_db_status,
    similar_verses_for_reference,
    similar_verses_for_verse_id,
)


class TestVectorFlow:
    """Test vector similarity flow functions."""

    @patch("agentpm.biblescholar.vector_flow.BibleVectorAdapter")
    @patch("agentpm.biblescholar.vector_flow.parse_reference")
    def test_similar_verses_for_reference_success(self, mock_parse, mock_adapter_class):
        """Test successful similarity search by reference."""
        # Mock parse_reference
        mock_parse.return_value = ("Genesis", 1, 1)

        # Mock adapter
        mock_adapter = MagicMock()
        mock_result = [
            VerseSimilarityResult(
                verse_id=2,
                book_name="Genesis",
                chapter_num=1,
                verse_num=2,
                text="And the earth was without form",
                translation_source="KJV",
                similarity_score=0.95,
            )
        ]
        mock_adapter.find_similar_by_ref.return_value = mock_result
        mock_adapter_class.return_value = mock_adapter

        results = similar_verses_for_reference("Genesis 1:1", "KJV", limit=10)

        assert len(results) == 1
        assert results[0].verse_id == 2
        mock_parse.assert_called_once_with("Genesis 1:1")
        mock_adapter.find_similar_by_ref.assert_called_once_with("Genesis", 1, 1, "KJV", 10)

    @patch("agentpm.biblescholar.vector_flow.BibleVectorAdapter")
    @patch("agentpm.biblescholar.vector_flow.parse_reference")
    def test_similar_verses_for_reference_invalid(self, mock_parse, mock_adapter_class):
        """Test invalid reference returns empty list."""
        mock_parse.return_value = None

        results = similar_verses_for_reference("invalid reference", "KJV", limit=10)

        assert results == []
        mock_parse.assert_called_once_with("invalid reference")
        mock_adapter_class.assert_not_called()

    @patch("agentpm.biblescholar.vector_flow.BibleVectorAdapter")
    def test_similar_verses_for_verse_id_success(self, mock_adapter_class):
        """Test successful similarity search by verse_id."""
        mock_adapter = MagicMock()
        mock_result = [
            VerseSimilarityResult(
                verse_id=2,
                book_name="Genesis",
                chapter_num=1,
                verse_num=2,
                text="And the earth was without form",
                translation_source="KJV",
                similarity_score=0.95,
            )
        ]
        mock_adapter.find_similar_by_verse.return_value = mock_result
        mock_adapter_class.return_value = mock_adapter

        results = similar_verses_for_verse_id(verse_id=1, limit=10)

        assert len(results) == 1
        assert results[0].verse_id == 2
        mock_adapter.find_similar_by_verse.assert_called_once_with(1, 10)

    @patch("agentpm.biblescholar.vector_flow.BibleVectorAdapter")
    def test_similar_verses_for_verse_id_empty(self, mock_adapter_class):
        """Test verse_id with no similar verses returns empty list."""
        mock_adapter = MagicMock()
        mock_adapter.find_similar_by_verse.return_value = []
        mock_adapter_class.return_value = mock_adapter

        results = similar_verses_for_verse_id(verse_id=99999, limit=10)

        assert results == []

    @patch("agentpm.biblescholar.vector_flow.BibleVectorAdapter")
    def test_get_db_status_with_adapter(self, mock_adapter_class):
        """Test get_db_status with provided adapter."""
        mock_adapter = MagicMock()
        mock_adapter.db_status = "available"
        mock_adapter_class.return_value = mock_adapter

        status = get_db_status(adapter=mock_adapter)

        assert status == "available"
        mock_adapter_class.assert_not_called()

    @patch("agentpm.biblescholar.vector_flow.BibleVectorAdapter")
    def test_get_db_status_without_adapter(self, mock_adapter_class):
        """Test get_db_status creates new adapter if not provided."""
        mock_adapter = MagicMock()
        mock_adapter.db_status = "db_off"
        mock_adapter_class.return_value = mock_adapter

        status = get_db_status()

        assert status == "db_off"
        mock_adapter_class.assert_called_once()
