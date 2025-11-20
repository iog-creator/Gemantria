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


# Book name mapping cache
_book_name_cache: dict[str, str] | None = None


def _get_book_name_mapping() -> dict[str, str]:
    """Get mapping from full book names to database abbreviations.

    Returns:
        Dict mapping full names (e.g., "Genesis") to abbreviations (e.g., "Gen").
    """
    global _book_name_cache
    if _book_name_cache is not None:
        return _book_name_cache

    try:
        # Try to load from database first
        from agentpm.db.loader import get_bible_engine
        from sqlalchemy import text

        engine = get_bible_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT abbreviation, book_name FROM bible.book_abbreviations WHERE source = 'standard'")
            )
            mapping = {row[0]: row[1] for row in result}
            _book_name_cache = mapping
            return mapping

    except Exception:
        # Fallback mapping for common books if DB unavailable or query fails
        _book_name_cache = {
            "Genesis": "Gen",
            "Exodus": "Exo",
            "Leviticus": "Lev",
            "Numbers": "Num",
            "Deuteronomy": "Deu",
            "Joshua": "Jos",
            "Judges": "Jdg",
            "Ruth": "Rut",
            "1Samuel": "1Sa",
            "2Samuel": "2Sa",
            "1Kings": "1Ki",
            "2Kings": "2Ki",
            "1Chronicles": "1Ch",
            "2Chronicles": "2Ch",
            "Ezra": "Ezr",
            "Nehemiah": "Neh",
            "Esther": "Est",
            "Job": "Job",
            "Psalms": "Psa",
            "Proverbs": "Pro",
            "Ecclesiastes": "Ecc",
            "Songofsolomon": "Sng",
            "Isaiah": "Isa",
            "Jeremiah": "Jer",
            "Lamentations": "Lam",
            "Ezekiel": "Ezk",
            "Daniel": "Dan",
            "Hosea": "Hos",
            "Joel": "Jol",
            "Amos": "Amo",
            "Obadiah": "Oba",
            "Jonah": "Jon",
            "Micah": "Mic",
            "Nahum": "Nam",
            "Habakkuk": "Hab",
            "Zephaniah": "Zep",
            "Haggai": "Hag",
            "Zechariah": "Zec",
            "Malachi": "Mal",
            "Matthew": "Mat",
            "Mark": "Mrk",
            "Luke": "Luk",
            "John": "Jhn",
            "Acts": "Act",
            "Romans": "Rom",
            "1Corinthians": "1Co",
            "2Corinthians": "2Co",
            "Galatians": "Gal",
            "Ephesians": "Eph",
            "Philippians": "Php",
            "Colossians": "Col",
            "1Thessalonians": "1Th",
            "2Thessalonians": "2Th",
            "1Timothy": "1Ti",
            "2Timothy": "2Ti",
            "Titus": "Tit",
            "Philemon": "Phm",
            "Hebrews": "Heb",
            "James": "Jas",
            "1Peter": "1Pe",
            "2Peter": "2Pe",
            "1John": "1Jn",
            "2John": "2Jn",
            "3John": "3Jn",
            "Jude": "Jud",
            "Revelation": "Rev",
        }
        return _book_name_cache


def normalize_book_name(book_name: str) -> str:
    """Normalize book name to database format.

    Args:
        book_name: Book name (full or abbreviated).

    Returns:
        Normalized book name for database queries.
    """
    # First try to map full names to abbreviations (case-insensitive)
    mapping = _get_book_name_mapping()
    book_name_clean = book_name.strip()

    # Try exact match first
    if book_name_clean in mapping:
        return mapping[book_name_clean]

    # Try case-insensitive match
    for full_name, abbr in mapping.items():
        if full_name.lower() == book_name_clean.lower():
            return abbr

    # Handle numbered books (1Corinthians -> 1Co, etc.)
    if book_name_clean.startswith(("1", "2", "3")) and len(book_name_clean) > 1:
        rest = book_name_clean[1:]
        # Try exact match for the rest
        if rest in mapping:
            return mapping[rest]
        # Try case-insensitive match for the rest
        for full_name, abbr in mapping.items():
            if full_name.lower() == rest.lower():
                return abbr

    # If it's already an abbreviation, return as-is
    return book_name_clean


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

    # Normalize book name to database format
    book_name = normalize_book_name(book_name)

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
        book_name = normalize_book_name(range_match.group(1))
        start_chapter = int(range_match.group(2))
        start_verse = int(range_match.group(3))
        end_chapter = int(range_match.group(4))
        end_verse = int(range_match.group(5))

        return adapter.get_passage(book_name, start_chapter, start_verse, end_chapter, end_verse, translation_source)

    # Check for single-chapter range (e.g., "Genesis 1:1-3")
    single_range_pattern = r"^(\w+)\s+(\d+):(\d+)-(\d+)$"
    single_range_match = re.match(single_range_pattern, reference.strip())

    if single_range_match:
        book_name = normalize_book_name(single_range_match.group(1))
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
