"""Tests for contextual_fetch module (Phase 15)."""

from __future__ import annotations

import pytest

from agentpm.biblescholar.contextual_fetch import ContextualFetchResult, fetch_context_for_verse


class TestContextualFetch:
    """Test contextual fetch API."""

    def test_fetch_context_for_verse_invalid(self) -> None:
        """Test that invalid references return error result."""
        result = fetch_context_for_verse("invalid reference")
        assert isinstance(result, ContextualFetchResult)
        assert result.success is False
        assert result.verse_ref == "invalid reference"
        assert result.chunks == []
        assert result.error is not None

    def test_fetch_context_for_verse_hermetic(self) -> None:
        """Test hermetic mode (DB off) returns graceful error."""
        result = fetch_context_for_verse("Mark 1:1")
        assert isinstance(result, ContextualFetchResult)
        # In hermetic mode, may succeed with empty chunks or fail gracefully
        assert result.verse_ref == "Mark 1:1"
        # Should not raise exception

    @pytest.mark.live_db
    def test_fetch_context_for_verse_success(self) -> None:
        """Test successful fetch for valid verse."""
        result = fetch_context_for_verse("Mark 1:1")
        assert isinstance(result, ContextualFetchResult)
        assert result.verse_ref == "Mark 1:1"
        if result.success:
            assert len(result.chunks) > 0
            chunk = result.chunks[0]
            assert "verse_id" in chunk
            assert "verse_ref" in chunk
        else:
            # If DB unavailable, should have error message
            assert result.error is not None
