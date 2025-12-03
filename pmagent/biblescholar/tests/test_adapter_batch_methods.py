"""Test batch methods for Phase 14 adapters."""

from pmagent.biblescholar.relationship_adapter import RelationshipAdapter
from pmagent.biblescholar.lexicon_adapter import LexiconAdapter


def test_relationship_adapter_batch_method_exists():
    """Test that get_enriched_context_batch method exists."""
    adapter = RelationshipAdapter()
    assert hasattr(adapter, "get_enriched_context_batch")

    # Test with empty list
    result = adapter.get_enriched_context_batch([])
    assert result == {}


def test_lexicon_adapter_batch_method_exists():
    """Test that get_greek_words_batch method exists."""
    adapter = LexiconAdapter()
    assert hasattr(adapter, "get_greek_words_batch")

    # Test with empty list
    result = adapter.get_greek_words_batch([])
    assert result == {}
