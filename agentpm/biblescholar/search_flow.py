"""BibleScholar keyword search flow (read-only).

This module provides a simple, composable flow for searching verses by keyword
from bible_db using the bible_db_adapter. No LM calls, no Gematria here.

See:
- docs/SSOT/BIBLESCHOLAR_MIGRATION_PLAN.md
- agentpm/biblescholar/AGENTS.md
"""

from __future__ import annotations

from typing import Literal

from agentpm.biblescholar.bible_db_adapter import BibleDbAdapter, VerseRecord
from agentpm.tools.bible import search_bible_verses

# Minimum query length for search
MIN_QUERY_LENGTH = 2


def search_verses(
    query: str, translation: str, limit: int = 20, adapter: BibleDbAdapter | None = None
) -> list[VerseRecord]:
    """Search verses by keyword in text content.

    Args:
        query: Search keyword (case-insensitive, minimum 2 characters).
        translation: Translation identifier (required, e.g., "KJV", "ESV", "ASV", "YLT").
        limit: Maximum number of results to return (default: 20).
        adapter: Optional BibleDbAdapter instance (ignored, kept for compatibility).

    Returns:
        List of VerseRecord objects matching the query, ordered by book, chapter, verse.
        Empty list if query is too short, no matches found, or DB unavailable.
    """
    # Tool handles validation, but we can keep this check for early exit
    if not query or len(query.strip()) < MIN_QUERY_LENGTH:
        return []

    # Use the tool
    result = search_bible_verses(query, translation=translation, limit=limit)

    if not result.get("ok", False):
        return []

    records = []
    for r in result.get("results", []):
        records.append(
            VerseRecord(
                verse_id=r["verse_id"],
                book_name=r["book_name"],
                chapter_num=r["chapter_num"],
                verse_num=r["verse_num"],
                text=r["text"],
                translation_source=r["translation_source"],
            )
        )

    return records


def get_db_status(adapter: BibleDbAdapter | None = None) -> Literal["available", "unavailable", "db_off"]:
    """Get current database status.

    Args:
        adapter: Optional BibleDbAdapter instance (creates new one if not provided).

    Returns:
        "available" if DB is connected and working.
        "unavailable" if connection failed.
        "db_off" if DSN not set or DB not configured.
    """
    if adapter is None:
        adapter = BibleDbAdapter()

    return adapter.db_status
