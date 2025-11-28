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

# Minimum query length for search
MIN_QUERY_LENGTH = 2


def search_verses(
    query: str, translation: str = "KJV", limit: int = 20, adapter: BibleDbAdapter | None = None
) -> list[VerseRecord]:
    """Search verses by keyword in text content.

    Args:
        query: Search keyword (case-insensitive, minimum 2 characters).
        translation: Translation identifier (default: "KJV").
        limit: Maximum number of results to return (default: 20).
        adapter: Optional BibleDbAdapter instance (creates new one if not provided).

    Returns:
        List of VerseRecord objects matching the query, ordered by book, chapter, verse.
        Empty list if query is too short, no matches found, or DB unavailable.
    """
    # Validate query length
    if not query or len(query.strip()) < MIN_QUERY_LENGTH:
        return []

    if adapter is None:
        adapter = BibleDbAdapter()

    return adapter.search_verses(query.strip(), translation, limit)


def get_db_status(
    adapter: BibleDbAdapter | None = None,
) -> Literal["available", "unavailable", "db_off"]:
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
