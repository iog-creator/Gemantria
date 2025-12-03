"""Unit tests for relationship_adapter.py (Phase 14 PR 14.4 PoC)."""

from __future__ import annotations

import pytest

from pmagent.biblescholar.relationship_adapter import (
    EnrichedContext,
    ProperName,
    RelationshipAdapter,
    VerseWordLink,
)


class TestRelationshipAdapter:
    """Test RelationshipAdapter methods."""

    def test_adapter_initialization(self) -> None:
        """Test adapter initializes correctly."""
        adapter = RelationshipAdapter()
        assert adapter is not None

    def test_get_proper_names_for_verse_hermetic(self) -> None:
        """Test get_proper_names_for_verse in hermetic mode (DB-off)."""
        adapter = RelationshipAdapter()
        # In hermetic mode, should return empty list gracefully
        result = adapter.get_proper_names_for_verse(66573)
        # Should not raise, may return empty list if DB unavailable
        assert isinstance(result, list)

    def test_get_verse_word_links_hermetic(self) -> None:
        """Test get_verse_word_links in hermetic mode (DB-off)."""
        adapter = RelationshipAdapter()
        # In hermetic mode, should return empty list gracefully
        result = adapter.get_verse_word_links(66573)
        # Should not raise, may return empty list if DB unavailable
        assert isinstance(result, list)

    def test_get_enriched_context_hermetic(self) -> None:
        """Test get_enriched_context in hermetic mode (DB-off)."""
        adapter = RelationshipAdapter()
        # In hermetic mode, should return None gracefully
        result = adapter.get_enriched_context(66573)
        # Should not raise, may return None if DB unavailable
        assert result is None or isinstance(result, EnrichedContext)

    def test_get_proper_name_by_unified_name_hermetic(self) -> None:
        """Test get_proper_name_by_unified_name in hermetic mode (DB-off)."""
        adapter = RelationshipAdapter()
        # In hermetic mode, should return None gracefully
        result = adapter.get_proper_name_by_unified_name("Jesus")
        # Should not raise, may return None if DB unavailable
        assert result is None or isinstance(result, ProperName)

    @pytest.mark.live_db
    def test_get_proper_names_for_verse_live(self) -> None:
        """Test get_proper_names_for_verse with live DB (Mark 1:1)."""
        from pmagent.biblescholar.lexicon_adapter import LexiconAdapter

        lexicon_adapter = LexiconAdapter()
        verse_id = lexicon_adapter._verse_ref_to_id("Mark.1.1")
        if not verse_id:
            pytest.skip("Could not resolve Mark 1:1 verse_id")

        adapter = RelationshipAdapter()
        result = adapter.get_proper_names_for_verse(verse_id, limit=10)
        # Should return list (may be empty if no matches)
        assert isinstance(result, list)
        for pn in result:
            assert isinstance(pn, ProperName)
            assert pn.unified_name

    @pytest.mark.live_db
    def test_get_verse_word_links_live(self) -> None:
        """Test get_verse_word_links with live DB (Mark 1:1)."""
        from pmagent.biblescholar.lexicon_adapter import LexiconAdapter

        lexicon_adapter = LexiconAdapter()
        verse_id = lexicon_adapter._verse_ref_to_id("Mark.1.1")
        if not verse_id:
            pytest.skip("Could not resolve Mark 1:1 verse_id")

        adapter = RelationshipAdapter()
        result = adapter.get_verse_word_links(verse_id)
        # Should return list (may be empty if table not populated)
        assert isinstance(result, list)
        for link in result:
            assert isinstance(link, VerseWordLink)
            assert link.verse_id == verse_id

    @pytest.mark.live_db
    def test_get_enriched_context_live(self) -> None:
        """Test get_enriched_context with live DB (Mark 1:1)."""
        from pmagent.biblescholar.lexicon_adapter import LexiconAdapter

        lexicon_adapter = LexiconAdapter()
        verse_id = lexicon_adapter._verse_ref_to_id("Mark.1.1")
        if not verse_id:
            pytest.skip("Could not resolve Mark 1:1 verse_id")

        adapter = RelationshipAdapter()
        result = adapter.get_enriched_context(verse_id)
        # Should return EnrichedContext or None
        if result:
            assert isinstance(result, EnrichedContext)
            assert result.verse_id == verse_id
            assert isinstance(result.proper_names, list)
            assert isinstance(result.word_links, list)


class TestProperName:
    """Test ProperName dataclass."""

    def test_proper_name_creation(self) -> None:
        """Test ProperName can be created."""
        pn = ProperName(
            unified_name="Jesus",
            type="PERSON",
            category="PERSON",
            briefest="Son of God",
            brief=None,
            short=None,
            article=None,
            description=None,
            parents=None,
            siblings=None,
            partners=None,
            offspring=None,
            tribe_nation=None,
            summary=None,
        )
        assert pn.unified_name == "Jesus"
        assert pn.type == "PERSON"


class TestEnrichedContext:
    """Test EnrichedContext dataclass."""

    def test_enriched_context_creation(self) -> None:
        """Test EnrichedContext can be created."""
        ctx = EnrichedContext(
            verse_id=66573,
            proper_names=[],
            word_links=[],
            context_summary=None,
        )
        assert ctx.verse_id == 66573
        assert ctx.proper_names == []
        assert ctx.word_links == []
