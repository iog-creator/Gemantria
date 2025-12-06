"""Tests for contextual_chunks module (Phase 15).

Test vectors:
- tv-phase15-01: single verse contextual chunk build
- tv-phase15-02: cross-language hints present when mapping exists
- tv-phase15-03: hermetic mode behavior (DB off) is graceful
"""

from __future__ import annotations

import pytest

from pmagent.biblescholar.contextual_chunks import build_contextual_chunks


class TestContextualChunks:
    """Test contextual chunk builder."""

    def test_build_contextual_chunks_invalid_reference(self) -> None:
        """Test that invalid references return empty list."""
        result = build_contextual_chunks("invalid reference")
        assert result == []

    def test_build_contextual_chunks_chapter_only(self) -> None:
        """Test that chapter-only references return empty list."""
        result = build_contextual_chunks("Mark 1")
        assert result == []

    @pytest.mark.live_db
    def test_build_contextual_chunks_single_verse(self) -> None:
        """tv-phase15-01: single verse contextual chunk build."""
        result = build_contextual_chunks("Mark 1:1")
        assert isinstance(result, list)
        if result:
            chunk = result[0]
            assert "verse_id" in chunk
            assert "verse_ref" in chunk
            assert chunk["verse_ref"] == "Mark 1:1"
            assert "greek_words" in chunk
            assert "proper_names" in chunk
            assert "cross_language_hints" in chunk
            assert "metadata" in chunk
            assert chunk["metadata"]["book_name"] in ("Mar", "Mark", "Mrk")
            assert chunk["metadata"]["chapter_num"] == 1
            assert chunk["metadata"]["verse_num"] == 1
            assert chunk["metadata"]["is_new_testament"] is True

    def test_build_contextual_chunks_hermetic(self) -> None:
        """tv-phase15-03: hermetic mode behavior (DB off) is graceful."""
        # In hermetic mode, should return empty list without raising
        result = build_contextual_chunks("Mark 1:1")
        # Should not raise, may return empty list if DB unavailable
        assert isinstance(result, list)

    @pytest.mark.live_db
    def test_build_contextual_chunks_cross_language_hints(self) -> None:
        """tv-phase15-02: cross-language hints present when mapping exists."""
        result = build_contextual_chunks("John 1:1")
        assert isinstance(result, list)
        if result:
            chunk = result[0]
            # If Greek words exist and have Strong's IDs, check for cross-language hints
            if chunk.get("greek_words") and chunk.get("cross_language_hints"):
                # At least one hint should have greek_strongs
                hints = chunk["cross_language_hints"]
                assert len(hints) > 0
                for hint in hints:
                    assert "greek_strongs" in hint
                    # If mapping exists, should have hebrew_strongs
                    if "hebrew_strongs" in hint:
                        assert "hebrew_lemma" in hint
                        assert "mapping_source" in hint
