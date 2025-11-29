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
from agentpm.biblescholar.reference_parser import parse_reference as parse_reference_new


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
    - OSIS format: "Gen.1.1"

    Args:
        reference: Bible reference string.

    Returns:
        Tuple of (book_name, chapter_num, verse_num) if parseable, None otherwise.
        Maintains backward compatibility with existing code that expects tuples.
    """
    try:
        parsed = parse_reference_new(reference)
        # Return tuple for backward compatibility
        # Note: book is already normalized by the new parser
        if parsed.verse is None:
            return None
        return (parsed.book, parsed.chapter, parsed.verse)
    except (ValueError, AttributeError):
        return None


def fetch_verse(
    reference: str, translation_source: str = "KJV", adapter: BibleDbAdapter | None = None
) -> VerseRecord | None:
    """Fetch a single verse by reference string.

    Args:
        reference: Bible reference (e.g., "Genesis 1:1", "Matthew 5:3", "Gen.1.1").
        translation_source: Translation identifier (default: "KJV").
        adapter: Optional BibleDbAdapter instance (creates new one if not provided).

    Returns:
        VerseRecord if found, None if not found or DB unavailable.
    """
    try:
        parsed = parse_reference_new(reference)
        if parsed.verse is None:
            return None
    except ValueError:
        return None

    if adapter is None:
        adapter = BibleDbAdapter()

    return adapter.get_verse(parsed.book, parsed.chapter, parsed.verse, translation_source)


def fetch_passage(
    reference: str, translation_source: str = "KJV", adapter: BibleDbAdapter | None = None
) -> list[VerseRecord]:
    """Fetch a passage (single verse or range) by reference string.

    Supports formats:
    - "Genesis 1:1" (single verse)
    - "Genesis 1:1-3" (verse range within same chapter)
    - "Genesis 1:1-2:3" (range across chapters)
    - OSIS format: "Gen.1.1" or "Gen.1.1-3"

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

    # Handle cross-chapter range (e.g., "Genesis 1:31-2:2")
    # The new parser doesn't support cross-chapter ranges directly, so check for this pattern first
    cross_chapter_pattern = r"^([A-Za-z0-9\s]+?)\s+(\d+):(\d+)-(\d+):(\d+)$"
    cross_chapter_match = re.match(cross_chapter_pattern, reference.strip())
    if cross_chapter_match:
        book_name = normalize_book_name(cross_chapter_match.group(1).strip())
        start_chapter = int(cross_chapter_match.group(2))
        start_verse = int(cross_chapter_match.group(3))
        end_chapter = int(cross_chapter_match.group(4))
        end_verse = int(cross_chapter_match.group(5))
        return adapter.get_passage(book_name, start_chapter, start_verse, end_chapter, end_verse, translation_source)

    # Try parsing with the new parser (handles single verses and same-chapter ranges)
    try:
        parsed = parse_reference_new(reference)
    except ValueError:
        return []

    # Handle verse range (end_verse is set)
    if parsed.end_verse is not None and parsed.verse is not None:
        # Range within same chapter
        return adapter.get_passage(
            parsed.book,
            parsed.chapter,
            parsed.verse,
            parsed.chapter,
            parsed.end_verse,
            translation_source,
        )

    # Single verse
    if parsed.verse is None:
        return []

    verse = adapter.get_verse(parsed.book, parsed.chapter, parsed.verse, translation_source)
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
