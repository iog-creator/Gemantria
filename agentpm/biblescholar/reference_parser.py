"""
Bible reference parser for OSIS and human-readable formats.

Pure-function module with no DB dependencies. Replaces legacy bible_reference_parser.py.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ParsedReference:
    """Parsed Bible reference structure."""

    book: str
    chapter: int
    verse: int | None
    end_verse: int | None = None
    translation: str = "KJV"

    def __post_init__(self) -> None:
        """Validate parsed reference."""
        if self.chapter < 1:
            raise ValueError(f"Chapter must be >= 1, got {self.chapter}")
        if self.verse is not None and self.verse < 1:
            raise ValueError(f"Verse must be >= 1, got {self.verse}")
        if self.end_verse is not None and self.end_verse < 1:
            raise ValueError(f"End verse must be >= 1, got {self.end_verse}")
        if self.end_verse is not None and self.verse is not None and self.end_verse < self.verse:
            raise ValueError(f"End verse ({self.end_verse}) must be >= start verse ({self.verse})")


# Standard Bible book name mappings (full name -> abbreviation)
# Based on common Bible database abbreviations
_BOOK_NAME_MAPPING: dict[str, str] = {
    # Old Testament
    "Genesis": "Gen",
    "Exodus": "Exo",
    "Leviticus": "Lev",
    "Numbers": "Num",
    "Deuteronomy": "Deu",
    "Joshua": "Jos",
    "Judges": "Jdg",
    "Ruth": "Rut",
    "1Samuel": "1Sa",
    "1 Samuel": "1Sa",
    "2Samuel": "2Sa",
    "2 Samuel": "2Sa",
    "1Kings": "1Ki",
    "1 Kings": "1Ki",
    "2Kings": "2Ki",
    "2 Kings": "2Ki",
    "1Chronicles": "1Ch",
    "1 Chronicles": "1Ch",
    "2Chronicles": "2Ch",
    "2 Chronicles": "2Ch",
    "Ezra": "Ezr",
    "Nehemiah": "Neh",
    "Esther": "Est",
    "Job": "Job",
    "Psalms": "Psa",
    "Psalm": "Psa",
    "Proverbs": "Pro",
    "Ecclesiastes": "Ecc",
    "Songofsolomon": "Sng",
    "Song of Solomon": "Sng",
    "Song of Songs": "Sng",
    "Isaiah": "Isa",
    "Jeremiah": "Jer",
    "Lamentations": "Lam",
    "Ezekiel": "Eze",
    "Daniel": "Dan",
    "Hosea": "Hos",
    "Joel": "Joel",
    "Amos": "Amos",
    "Obadiah": "Oba",
    "Jonah": "Jon",
    "Micah": "Mic",
    "Nahum": "Nah",
    "Habakkuk": "Hab",
    "Zephaniah": "Zep",
    "Haggai": "Hag",
    "Zechariah": "Zec",
    "Malachi": "Mal",
    # New Testament
    "Matthew": "Mat",
    "Matt": "Mat",
    "Mark": "Mar",
    "Luke": "Luk",
    "John": "Joh",
    "Acts": "Act",
    "Romans": "Rom",
    "1Corinthians": "1Co",
    "1 Corinthians": "1Co",
    "2Corinthians": "2Co",
    "2 Corinthians": "2Co",
    "Galatians": "Gal",
    "Ephesians": "Eph",
    "Philippians": "Phi",
    "Colossians": "Col",
    "1Thessalonians": "1Th",
    "1 Thessalonians": "1Th",
    "2Thessalonians": "2Th",
    "2 Thessalonians": "2Th",
    "1Timothy": "1Ti",
    "1 Timothy": "1Ti",
    "2Timothy": "2Ti",
    "2 Timothy": "2Ti",
    "Titus": "Tit",
    "Philemon": "Phm",
    "Hebrews": "Heb",
    "James": "Jam",
    "1Peter": "1Pe",
    "1 Peter": "1Pe",
    "2Peter": "2Pe",
    "2 Peter": "2Pe",
    "1John": "1Jo",
    "1 John": "1Jo",
    "2John": "2Jo",
    "2 John": "2Jo",
    "3John": "3Jo",
    "3 John": "3Jo",
    "Jude": "Jud",
    "Revelation": "Rev",
    "Revelations": "Rev",  # Common misspelling
}


def normalize_book_name(book_name: str) -> str:
    """Normalize book name to standard abbreviation.

    Args:
        book_name: Book name (full or abbreviated).

    Returns:
        Normalized book name abbreviation.
    """
    book_name_clean = book_name.strip()

    # Try exact match first
    if book_name_clean in _BOOK_NAME_MAPPING:
        return _BOOK_NAME_MAPPING[book_name_clean]

    # Try case-insensitive match
    for full_name, abbr in _BOOK_NAME_MAPPING.items():
        if full_name.lower() == book_name_clean.lower():
            return abbr

    # Handle numbered books (1Corinthians -> 1Co, etc.)
    if book_name_clean and book_name_clean[0].isdigit():
        # Try to match the rest after the number
        match = re.match(r"^([123])\s*(.+)$", book_name_clean, re.IGNORECASE)
        if match:
            rest = match.group(2).strip()
            # Try to find the book name
            for full_name, abbr in _BOOK_NAME_MAPPING.items():
                if full_name.lower().replace(" ", "").endswith(rest.lower()):
                    return abbr
            # Try direct match on rest
            if rest in _BOOK_NAME_MAPPING:
                return _BOOK_NAME_MAPPING[rest]
            for full_name, abbr in _BOOK_NAME_MAPPING.items():
                if full_name.lower() == rest.lower():
                    return abbr

    # If it's already an abbreviation or unrecognized, return as-is
    return book_name_clean


def parse_reference(ref: str) -> ParsedReference:
    """Parse Bible reference string into structured ParsedReference.

    Supports formats:
    - "John 3:16" (standard format)
    - "Gen 1:1-5" (verse range)
    - "Gen.1.1" (OSIS format)
    - "Gen.1.1-5" (OSIS format with verse range)

    Args:
        ref: Bible reference string.

    Returns:
        ParsedReference object.

    Raises:
        ValueError: If reference format is invalid or unparseable.
    """
    ref = ref.strip()
    if not ref:
        raise ValueError("Empty reference string")

    # Try OSIS format first (e.g., "Gen.1.1" or "Gen.1.1-5")
    osis_pattern = r"^([A-Za-z][A-Za-z0-9]*)\s*\.\s*(\d+)\s*\.\s*(\d+)(?:\s*-\s*(\d+))?$"
    osis_match = re.match(osis_pattern, ref)
    if osis_match:
        book_raw = osis_match.group(1)
        chapter = int(osis_match.group(2))
        verse = int(osis_match.group(3))
        end_verse = int(osis_match.group(4)) if osis_match.group(4) else None
        book = normalize_book_name(book_raw)
        return ParsedReference(book=book, chapter=chapter, verse=verse, end_verse=end_verse)

    # Try standard format: "Book Chapter:Verse" or "Book Chapter:Verse-EndVerse"
    # Allow numbered books (1 Corinthians, 2 Samuel, etc.)
    standard_pattern = r"^([\d\s]*[A-Za-z][A-Za-z0-9\s]+?)\s+(\d+):(\d+)(?:\s*-\s*(\d+))?$"
    standard_match = re.match(standard_pattern, ref)
    if standard_match:
        book_raw = standard_match.group(1).strip()
        chapter = int(standard_match.group(2))
        verse = int(standard_match.group(3))
        end_verse = int(standard_match.group(4)) if standard_match.group(4) else None
        book = normalize_book_name(book_raw)
        return ParsedReference(book=book, chapter=chapter, verse=verse, end_verse=end_verse)

    # Try format without verse: "Book Chapter" (verse will be None)
    # Allow numbered books
    chapter_only_pattern = r"^([\d\s]*[A-Za-z][A-Za-z0-9\s]+?)\s+(\d+)$"
    chapter_only_match = re.match(chapter_only_pattern, ref)
    if chapter_only_match:
        book_raw = chapter_only_match.group(1).strip()
        chapter = int(chapter_only_match.group(2))
        book = normalize_book_name(book_raw)
        return ParsedReference(book=book, chapter=chapter, verse=None)

    raise ValueError(f"Invalid reference format: {ref}")
