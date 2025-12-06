from __future__ import annotations

"""Contextual fetch API for Phase 15 RAG integration.

This module provides a high-level API for fetching enriched contextual chunks
for BibleScholar RAG operations.

See:
- docs/SSOT/PHASE15_PLAN.md
- pmagent/biblescholar/AGENTS.md
"""

from dataclasses import dataclass
from typing import Any

from pmagent.biblescholar.contextual_chunks import build_contextual_chunks


@dataclass
class ContextualFetchResult:
    """Result of a contextual fetch operation.

    Attributes:
        verse_ref: Original verse reference.
        chunks: List of contextual chunks (typically one per verse).
        success: Whether the fetch succeeded.
        error: Error message if fetch failed.
    """

    verse_ref: str
    chunks: list[dict[str, Any]]
    success: bool
    error: str | None = None


def fetch_context_for_verse(verse_ref: str) -> ContextualFetchResult:
    """Fetch contextual chunks for a verse reference.

    This is the main API entry point for Phase 15 contextual chunk retrieval.
    It aggregates data from RelationshipAdapter and LexiconAdapter to build
    enriched chunks suitable for RAG operations.

    Args:
        verse_ref: Verse reference (e.g., "Mark 1:1" or "Gen.1.1")

    Returns:
        ContextualFetchResult with chunks and status.
    """
    try:
        chunks = build_contextual_chunks(verse_ref)
        if not chunks:
            return ContextualFetchResult(
                verse_ref=verse_ref,
                chunks=[],
                success=False,
                error="No chunks generated (verse not found or DB unavailable)",
            )

        return ContextualFetchResult(
            verse_ref=verse_ref,
            chunks=chunks,
            success=True,
            error=None,
        )
    except Exception as e:
        return ContextualFetchResult(
            verse_ref=verse_ref,
            chunks=[],
            success=False,
            error=f"Error building contextual chunks: {e!s}",
        )
