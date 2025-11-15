from __future__ import annotations

"""BibleScholar vector similarity flow (read-only).

This module provides simple, composable flows for finding similar verses
using vector similarity from bible_db. No LM calls, no Gematria here.

See:
- docs/SSOT/BIBLESCHOLAR_MIGRATION_PLAN.md
- agentpm/biblescholar/AGENTS.md
"""

from typing import Literal

from agentpm.biblescholar.bible_passage_flow import parse_reference
from agentpm.biblescholar.vector_adapter import BibleVectorAdapter, VerseSimilarityResult


def similar_verses_for_reference(
    reference: str, translation_source: str = "KJV", limit: int = 10
) -> list[VerseSimilarityResult]:
    """Find similar verses for a Bible reference using vector similarity.

    Args:
        reference: Bible reference string (e.g., "Genesis 1:1", "Matthew 5:3").
        translation_source: Translation identifier (default: "KJV").
        limit: Maximum number of similar verses to return (default: 10).

    Returns:
        List of VerseSimilarityResult objects, ordered by similarity (highest first).
        Empty list if reference is invalid, verse not found, or DB unavailable.
    """
    # Parse reference first (before creating adapter)
    parsed = parse_reference(reference)
    if parsed is None:
        return []

    book_name, chapter_num, verse_num = parsed

    # Create adapter and find similar verses
    adapter = BibleVectorAdapter()
    return adapter.find_similar_by_ref(book_name, chapter_num, verse_num, translation_source, limit)


def similar_verses_for_verse_id(verse_id: int, limit: int = 10) -> list[VerseSimilarityResult]:
    """Find similar verses by verse_id using vector similarity.

    Args:
        verse_id: Primary key of the source verse.
        limit: Maximum number of similar verses to return (default: 10).

    Returns:
        List of VerseSimilarityResult objects, ordered by similarity (highest first).
        Empty list if verse not found or DB unavailable.
    """
    adapter = BibleVectorAdapter()
    return adapter.find_similar_by_verse(verse_id, limit)


def get_db_status(
    adapter: BibleVectorAdapter | None = None,
) -> Literal["available", "unavailable", "db_off"]:
    """Get current database status.

    Args:
        adapter: Optional BibleVectorAdapter instance. If None, creates a new one.

    Returns:
        Database status string.
    """
    if adapter is None:
        adapter = BibleVectorAdapter()
    return adapter.db_status
