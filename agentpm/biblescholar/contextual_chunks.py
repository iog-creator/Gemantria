from __future__ import annotations

"""Contextual chunk builder for Phase 15 RAG integration.

This module builds enriched contextual chunks for verses using:
- RelationshipAdapter (Phase 14) for proper names and verse-word links
- LexiconAdapter (Phase 14) for Greek words and lemmas
- Cross-language lemma resolution for Greek-to-Hebrew hints

See:
- docs/SSOT/PHASE15_PLAN.md
- agentpm/biblescholar/AGENTS.md
"""

from typing import Any

from agentpm.biblescholar.cross_language_flow import resolve_cross_language_lemma
from agentpm.biblescholar.lexicon_adapter import LexiconAdapter
from agentpm.biblescholar.reference_parser import parse_reference
from agentpm.biblescholar.relationship_adapter import RelationshipAdapter


def build_contextual_chunks(verse_ref: str) -> list[dict[str, Any]]:
    """Build contextual chunks for a verse reference.

    Args:
        verse_ref: Verse reference (e.g., "Mark 1:1" or "Gen.1.1")

    Returns:
        List of contextual chunk dictionaries matching the schema.
        Returns empty list if verse not found or DB unavailable.
    """
    # Parse reference
    try:
        parsed = parse_reference(verse_ref)
    except (ValueError, AttributeError):
        return []

    if parsed.verse is None:
        # Can't build chunks for chapter-only references
        return []

    # Convert to OSIS format for verse_id lookup
    # Format: "Book.Chapter.Verse" (e.g., "Mark.1.1")
    book_abbrev = parsed.book
    osis_ref = f"{book_abbrev}.{parsed.chapter}.{parsed.verse}"

    # Initialize adapters
    lexicon_adapter = LexiconAdapter()
    relationship_adapter = RelationshipAdapter()

    # Get verse_id
    verse_id = lexicon_adapter._verse_ref_to_id(osis_ref)
    if verse_id is None:
        return []

    # Build base chunk structure
    chunk: dict[str, Any] = {
        "verse_id": verse_id,
        "verse_ref": verse_ref,
        "greek_words": [],
        "proper_names": [],
        "cross_language_hints": [],
        "metadata": {
            "book_name": parsed.book,
            "chapter_num": parsed.chapter,
            "verse_num": parsed.verse,
            "is_new_testament": _is_new_testament(parsed.book),
        },
    }

    # Get Greek words (NT only)
    if chunk["metadata"]["is_new_testament"]:
        greek_words = lexicon_adapter.get_greek_words_for_verse(osis_ref)
        if greek_words:
            chunk["greek_words"] = greek_words

            # Resolve cross-language hints for Greek words
            for word in greek_words:
                strongs_id = word.get("strongs_id")
                if strongs_id and strongs_id.startswith("G"):
                    hint = resolve_cross_language_lemma(strongs_id)
                    if hint:
                        chunk["cross_language_hints"].append(hint)

    # Get proper names
    proper_names = relationship_adapter.get_proper_names_for_verse(verse_id, limit=10)
    if proper_names:
        chunk["proper_names"] = [
            {
                "unified_name": pn.unified_name,
                "type": pn.type,
                "category": pn.category,
                "briefest": pn.briefest,
                "brief": pn.brief,
            }
            for pn in proper_names
        ]

    return [chunk]


def expand_context_window(verse_ref: str, window_size: int = 5) -> list[dict[str, Any]]:
    """Expand context window around a verse (for RAG retrieval).

    Retrieves ±N verses from the seed verse to provide semantic continuity.
    For window_size=5, returns 5 verses: seed verse ±2 verses.

    Args:
        verse_ref: Seed verse reference (e.g., "Mark 1:3")
        window_size: Total window size (default: 5 = ±2 verses)

    Returns:
        List of contextual chunks for verses in the window.
        Empty list if seed verse not found or DB unavailable.

    Example:
        expand_context_window("Mark 1:3", window_size=5)
        Returns chunks for: Mark 1:1, 1:2, 1:3, 1:4, 1:5
    """
    # Parse seed reference
    try:
        parsed = parse_reference(verse_ref)
    except (ValueError, AttributeError):
        return []

    if parsed.verse is None:
        return []

    # Calculate window bounds
    offset = window_size // 2  # For window_size=5, offset=2
    start_verse = max(1, parsed.verse - offset)
    end_verse = parsed.verse + offset

    # Build chunks for all verses in window
    chunks = []
    for verse_num in range(start_verse, end_verse + 1):
        # Build reference for this verse
        window_verse_ref = f"{parsed.book} {parsed.chapter}:{verse_num}"

        # Build chunk for this verse
        verse_chunks = build_contextual_chunks(window_verse_ref)
        if verse_chunks:
            # Mark which verse is the seed
            for chunk in verse_chunks:
                chunk["is_seed_verse"] = verse_num == parsed.verse
            chunks.extend(verse_chunks)

    return chunks


def _is_new_testament(book_name: str) -> bool:
    """Check if book is in New Testament."""
    nt_books = {
        "Mat",
        "Mar",
        "Mark",
        "Mrk",
        "Luk",
        "Luke",
        "Joh",
        "John",
        "Act",
        "Acts",
        "Rom",
        "1Co",
        "1Cor",
        "1 Corinthians",
        "2Co",
        "2Cor",
        "2 Corinthians",
        "Gal",
        "Eph",
        "Phi",
        "Php",
        "Philippians",
        "Col",
        "1Th",
        "1Thess",
        "1 Thessalonians",
        "2Th",
        "2Thess",
        "2 Thessalonians",
        "1Ti",
        "1Tim",
        "1 Timothy",
        "2Ti",
        "2Tim",
        "2 Timothy",
        "Tit",
        "Titus",
        "Phm",
        "Philem",
        "Philemon",
        "Heb",
        "Jam",
        "Jas",
        "James",
        "1Pe",
        "1Pet",
        "1 Peter",
        "2Pe",
        "2Pet",
        "2 Peter",
        "1Jo",
        "1John",
        "1 John",
        "2Jo",
        "2John",
        "2 John",
        "3Jo",
        "3John",
        "3 John",
        "Jud",
        "Jude",
        "Rev",
        "Revelation",
    }
    return book_name in nt_books
