from __future__ import annotations

"""BibleScholar passage/verse retrieval flow (read-only).

This module provides a simple, composable flow for retrieving verses and passages
from bible_db using the bible_db_adapter. No LM calls, no Gematria here.

See:
- docs/SSOT/BIBLESCHOLAR_MIGRATION_PLAN.md
- agentpm/biblescholar/AGENTS.md
"""

import re
from typing import Literal

from agentpm.biblescholar.bible_db_adapter import BibleDbAdapter, VerseRecord


def parse_reference(reference: str) -> tuple[str, int, int] | None:
    """Parse a simple Bible reference string.

    Supports formats:
    - "Genesis 1:1"
    - "Gen 1:1"
    - "Matthew 5:3"

    Args:
        reference: Bible reference string.

    Returns:
        Tuple of (book_name, chapter_num, verse_num) if parseable, None otherwise.
    """
    # Simple regex for "Book Chapter:Verse" format
    pattern = r"^(\w+)\s+(\d+):(\d+)$"
    match = re.match(pattern, reference.strip())

    if not match:
        return None

    book_name = match.group(1)
    chapter_num = int(match.group(2))
    verse_num = int(match.group(3))

    # Normalize book name (capitalize first letter)
    book_name = book_name.capitalize()

    return (book_name, chapter_num, verse_num)


def fetch_verse(
    reference: str, translation_source: str = "KJV", adapter: BibleDbAdapter | None = None
) -> VerseRecord | None:
    """Fetch a single verse by reference string.

    Args:
        reference: Bible reference (e.g., "Genesis 1:1", "Matthew 5:3").
        translation_source: Translation identifier (default: "KJV").
        adapter: Optional BibleDbAdapter instance (creates new one if not provided).

    Returns:
        VerseRecord if found, None if not found or DB unavailable.
    """
    parsed = parse_reference(reference)
    if parsed is None:
        return None

    book_name, chapter_num, verse_num = parsed

    if adapter is None:
        adapter = BibleDbAdapter()

    return adapter.get_verse(book_name, chapter_num, verse_num, translation_source)


def fetch_passage(
    reference: str, translation_source: str = "KJV", adapter: BibleDbAdapter | None = None
) -> list[VerseRecord]:
    """Fetch a passage (single verse or range) by reference string.

    Supports formats:
    - "Genesis 1:1" (single verse)
    - "Genesis 1:1-3" (verse range within same chapter)
    - "Genesis 1:1-2:3" (range across chapters)

    Args:
        reference: Bible reference string.
        translation_source: Translation identifier (default: "KJV").
        adapter: Optional BibleDbAdapter instance (creates new one if not provided).

    Returns:
        List of VerseRecord objects, ordered by chapter and verse.
        Empty list if not found or DB unavailable.
    """
    if adapter is None:
        adapter = BibleDbAdapter()

    # Check for range (e.g., "Genesis 1:1-3" or "Genesis 1:1-2:3")
    range_pattern = r"^(\w+)\s+(\d+):(\d+)-(\d+):(\d+)$"
    range_match = re.match(range_pattern, reference.strip())

    if range_match:
        book_name = range_match.group(1).capitalize()
        start_chapter = int(range_match.group(2))
        start_verse = int(range_match.group(3))
        end_chapter = int(range_match.group(4))
        end_verse = int(range_match.group(5))

        return adapter.get_passage(book_name, start_chapter, start_verse, end_chapter, end_verse, translation_source)

    # Check for single-chapter range (e.g., "Genesis 1:1-3")
    single_range_pattern = r"^(\w+)\s+(\d+):(\d+)-(\d+)$"
    single_range_match = re.match(single_range_pattern, reference.strip())

    if single_range_match:
        book_name = single_range_match.group(1).capitalize()
        chapter_num = int(single_range_match.group(2))
        start_verse = int(single_range_match.group(3))
        end_verse = int(single_range_match.group(4))

        return adapter.get_passage(book_name, chapter_num, start_verse, chapter_num, end_verse, translation_source)

    # Single verse
    parsed = parse_reference(reference)
    if parsed is None:
        return []

    book_name, chapter_num, verse_num = parsed
    verse = adapter.get_verse(book_name, chapter_num, verse_num, translation_source)

    return [verse] if verse is not None else []


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
