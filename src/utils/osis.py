# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
OSIS (Open Scripture Information Standard) utilities for verse reference extraction and normalization.
"""

import re
from typing import List, Dict


def extract_verse_references(text: str) -> List[Dict[str, str]]:
    """
    Extract verse references from text and normalize to OSIS format.

    Args:
        text: Text containing potential verse references

    Returns:
        List of dictionaries with 'label' and 'osis' keys
    """
    references = []

    # Common patterns for verse references
    patterns = [
        # Book Chapter:Verse (e.g., "Psalm 30:5")
        r"([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+(\d+):(\d+)",
        # Book Chapter (e.g., "Genesis 1")
        r"([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+(\d+)",
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            book_name = match.group(1).strip()
            chapter = match.group(2)
            verse = match.group(3) if len(match.groups()) > 2 else None

            # Normalize book names to OSIS abbreviations
            osis_book = normalize_book_to_osis(book_name)
            if osis_book:
                if verse:
                    osis_ref = f"{osis_book}.{chapter}.{verse}"
                    label = f"{book_name} {chapter}:{verse}"
                else:
                    osis_ref = f"{osis_book}.{chapter}"
                    label = f"{book_name} {chapter}"

                references.append({"label": label, "osis": osis_ref})

    return references


def normalize_book_to_osis(book_name: str) -> str | None:
    """
    Normalize a book name to OSIS abbreviation.

    Args:
        book_name: Human-readable book name

    Returns:
        OSIS book abbreviation or None if not recognized
    """
    # Common mappings - this is a simplified version
    book_mappings = {
        "genesis": "Gen",
        "exodus": "Exod",
        "leviticus": "Lev",
        "numbers": "Num",
        "deuteronomy": "Deut",
        "joshua": "Josh",
        "judges": "Judg",
        "ruth": "Ruth",
        "1 samuel": "1Sam",
        "2 samuel": "2Sam",
        "1 kings": "1Kgs",
        "2 kings": "2Kgs",
        "1 chronicles": "1Chr",
        "2 chronicles": "2Chr",
        "ezra": "Ezra",
        "nehemiah": "Neh",
        "esther": "Esth",
        "job": "Job",
        "psalms": "Ps",
        "psalm": "Ps",
        "proverbs": "Prov",
        "ecclesiastes": "Eccl",
        "song of solomon": "Song",
        "song of songs": "Song",
        "isaiah": "Isa",
        "jeremiah": "Jer",
        "lamentations": "Lam",
        "ezekiel": "Ezek",
        "daniel": "Dan",
        "hosea": "Hos",
        "joel": "Joel",
        "amos": "Amos",
        "obadiah": "Obad",
        "jonah": "Jonah",
        "micah": "Mic",
        "nahum": "Nah",
        "habakkuk": "Hab",
        "zephaniah": "Zeph",
        "haggai": "Hag",
        "zechariah": "Zech",
        "malachi": "Mal",
        "matthew": "Matt",
        "mark": "Mark",
        "luke": "Luke",
        "john": "John",
        "acts": "Acts",
        "romans": "Rom",
        "1 corinthians": "1Cor",
        "2 corinthians": "2Cor",
        "galatians": "Gal",
        "ephesians": "Eph",
        "philippians": "Phil",
        "colossians": "Col",
        "1 thessalonians": "1Thess",
        "2 thessalonians": "2Thess",
        "1 timothy": "1Tim",
        "2 timothy": "2Tim",
        "titus": "Titus",
        "philemon": "Phlm",
        "hebrews": "Heb",
        "james": "Jas",
        "1 peter": "1Pet",
        "2 peter": "2Pet",
        "1 john": "1John",
        "2 john": "2John",
        "3 john": "3John",
        "jude": "Jude",
        "revelation": "Rev",
    }

    # Normalize the input
    normalized = book_name.lower().strip()

    # Direct lookup
    if normalized in book_mappings:
        return book_mappings[normalized]

    # Try partial matches for common variations
    for key, value in book_mappings.items():
        if key in normalized or normalized in key:
            return value

    return None
