#!/usr/bin/env python3
"""
OSIS (Open Scripture Information Standard) parsing and normalization utilities.

Handles extraction and normalization of Bible verse references from text.
Supports various input formats and normalizes to OSIS standard format.

Examples:
- "Genesis 1:1" → "Gen.1.1"
- "Psalm 30:5" → "Ps.30.5"
- "Isaiah 43:2" → "Isa.43.2"
"""

import re
from typing import List, Dict


# OSIS book abbreviations mapping (subset for common books)
OSIS_BOOKS = {
    # Old Testament
    "gen": "Gen",
    "genesis": "Gen",
    "exo": "Exo",
    "exodus": "Exo",
    "lev": "Lev",
    "leviticus": "Lev",
    "num": "Num",
    "numbers": "Num",
    "deu": "Deu",
    "deuteronomy": "Deu",
    "jos": "Jos",
    "joshua": "Jos",
    "jdg": "Jdg",
    "judges": "Jdg",
    "rut": "Rut",
    "ruth": "Rut",
    "1sa": "1Sa",
    "1 samuel": "1Sa",
    "1samuel": "1Sa",
    "2sa": "2Sa",
    "2 samuel": "2Sa",
    "2samuel": "2Sa",
    "1ki": "1Ki",
    "1 kings": "1Ki",
    "1kings": "1Ki",
    "2ki": "2Ki",
    "2 kings": "2Ki",
    "2kings": "2Ki",
    "1ch": "1Ch",
    "1 chronicles": "1Ch",
    "1chronicles": "1Ch",
    "2ch": "2Ch",
    "2 chronicles": "2Ch",
    "2chronicles": "2Ch",
    "ezr": "Ezr",
    "ezra": "Ezr",
    "neh": "Neh",
    "nehemiah": "Neh",
    "est": "Est",
    "esther": "Est",
    "job": "Job",
    "psa": "Ps",
    "ps": "Ps",
    "psalm": "Ps",
    "psalms": "Ps",
    "pro": "Pro",
    "proverbs": "Pro",
    "ecc": "Ecc",
    "ecclesiastes": "Ecc",
    "son": "Son",
    "song": "Son",
    "song of solomon": "Son",
    "isa": "Isa",
    "isaiah": "Isa",
    "jer": "Jer",
    "jeremiah": "Jer",
    "lam": "Lam",
    "lamentations": "Lam",
    "eze": "Eze",
    "ezekiel": "Eze",
    "dan": "Dan",
    "daniel": "Dan",
    "hos": "Hos",
    "hosea": "Hos",
    "joe": "Joe",
    "joel": "Joe",
    "amo": "Amo",
    "amos": "Amo",
    "oba": "Oba",
    "obadiah": "Oba",
    "jon": "Jon",
    "jonah": "Jon",
    "mic": "Mic",
    "micah": "Mic",
    "nah": "Nah",
    "nahum": "Nah",
    "hab": "Hab",
    "habakkuk": "Hab",
    "zep": "Zep",
    "zephaniah": "Zep",
    "hag": "Hag",
    "haggai": "Hag",
    "zec": "Zec",
    "zechariah": "Zec",
    "mal": "Mal",
    "malachi": "Mal",
    # New Testament
    "mat": "Mat",
    "matthew": "Mat",
    "mar": "Mar",
    "mark": "Mar",
    "luk": "Luk",
    "luke": "Luk",
    "joh": "Joh",
    "john": "Joh",
    "act": "Act",
    "acts": "Act",
    "rom": "Rom",
    "romans": "Rom",
    "1co": "1Co",
    "1 corinthians": "1Co",
    "1corinthians": "1Co",
    "2co": "2Co",
    "2 corinthians": "2Co",
    "2corinthians": "2Co",
    "gal": "Gal",
    "galatians": "Gal",
    "eph": "Eph",
    "ephesians": "Eph",
    "phi": "Phi",
    "philippians": "Phi",
    "col": "Col",
    "colossians": "Col",
    "1th": "1Th",
    "1 thessalonians": "1Th",
    "1thessalonians": "1Th",
    "2th": "2Th",
    "2 thessalonians": "2Th",
    "2thessalonians": "2Th",
    "1ti": "1Ti",
    "1 timothy": "1Ti",
    "1timothy": "1Ti",
    "2ti": "2Ti",
    "2 timothy": "2Ti",
    "2timothy": "2Ti",
    "tit": "Tit",
    "titus": "Tit",
    "phm": "Phm",
    "philemon": "Phm",
    "heb": "Heb",
    "hebrews": "Heb",
    "jam": "Jam",
    "james": "Jam",
    "1pe": "1Pe",
    "1 peter": "1Pe",
    "1peter": "1Pe",
    "2pe": "2Pe",
    "2 peter": "2Pe",
    "2peter": "2Pe",
    "1jo": "1Jo",
    "1 john": "1Jo",
    "1john": "1Jo",
    "2jo": "2Jo",
    "2 john": "2Jo",
    "2john": "2Jo",
    "3jo": "3Jo",
    "3 john": "3Jo",
    "3john": "3Jo",
    "jud": "Jud",
    "jude": "Jud",
    "rev": "Rev",
    "revelation": "Rev",
}


def normalize_osis_book(book: str) -> str | None:
    """
    Normalize a book name/abbreviation to OSIS format.

    Args:
        book: Book name or abbreviation (case-insensitive)

    Returns:
        OSIS book abbreviation or None if not recognized
    """
    if not book:
        return None

    book_lower = book.lower().strip()
    return OSIS_BOOKS.get(book_lower)


def parse_verse_reference(text: str) -> Dict[str, str] | None:
    """
    Parse a single verse reference from text.

    Supports formats like:
    - "Genesis 1:1"
    - "Ps 30:5"
    - "Isaiah 43:2"
    - "Gen.1.1" (already OSIS)

    Args:
        text: Text containing a verse reference

    Returns:
        Dict with 'book', 'chapter', 'verse', 'osis' keys, or None if not parseable
    """
    if not text:
        return None

    # Clean up the text
    text = text.strip()

    # Pattern 1: Already OSIS format (Book.chapter.verse)
    osis_pattern = re.match(r"^([A-Za-z0-9]+)\.(\d+)\.(\d+)$", text)
    if osis_pattern:
        book_abbr, chapter, verse = osis_pattern.groups()
        osis_book = normalize_osis_book(book_abbr)
        if osis_book:
            return {
                "book": osis_book,
                "chapter": chapter,
                "verse": verse,
                "osis": f"{osis_book}.{chapter}.{verse}",
                "label": text,
            }

    # Pattern 2: "Book chapter:verse" format
    ref_pattern = re.match(r"^([A-Za-z\s]+)\s+(\d+):(\d+)$", text)
    if ref_pattern:
        book_name, chapter, verse = ref_pattern.groups()
        osis_book = normalize_osis_book(book_name)
        if osis_book:
            return {
                "book": osis_book,
                "chapter": chapter,
                "verse": verse,
                "osis": f"{osis_book}.{chapter}.{verse}",
                "label": text,
            }

    return None


def extract_verse_references(text: str) -> List[Dict[str, str]]:
    """
    Extract all verse references from text.

    Args:
        text: Text that may contain Bible verse references

    Returns:
        List of verse reference dictionaries, deduplicated by OSIS
    """
    if not text:
        return []

    references = []
    seen_osis = set()

    # Find potential references (simple heuristic: words followed by numbers)
    # This is a conservative approach - we look for patterns that look like references
    words = re.findall(r"\b[A-Za-z]+\s*\d+:\d+\b|\b[A-Za-z0-9]+\.\d+\.\d+\b", text)

    for word in words:
        ref = parse_verse_reference(word)
        if ref and ref["osis"] not in seen_osis:
            references.append(ref)
            seen_osis.add(ref["osis"])

    return references


def normalize_crossrefs(raw_refs: List[str]) -> List[Dict[str, str]]:
    """
    Normalize a list of raw cross-reference strings to OSIS format.

    Args:
        raw_refs: List of raw reference strings from model output

    Returns:
        List of normalized cross-reference dicts with 'label' and 'osis' keys
    """
    normalized = []

    for ref_text in raw_refs:
        refs = extract_verse_references(ref_text)
        for ref in refs:
            normalized.append({"label": ref["label"], "osis": ref["osis"]})

    # Deduplicate by OSIS
    seen = set()
    deduped = []
    for ref in normalized:
        if ref["osis"] not in seen:
            deduped.append(ref)
            seen.add(ref["osis"])

    return deduped
