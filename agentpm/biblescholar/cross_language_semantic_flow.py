"""BibleScholar cross-language semantic flow (read-only).

Finds semantic connections between Hebrew (OT) and Greek (NT) words using
vector embeddings. Enables discovering how Hebrew concepts relate to Greek
translations and theological connections across testaments.

See:
- docs/SSOT/BIBLESCHOLAR_MIGRATION_PLAN.md
- agentpm/biblescholar/AGENTS.md
"""

from __future__ import annotations

from dataclasses import dataclass

from agentpm.biblescholar.bible_db_adapter import BibleDbAdapter
from agentpm.biblescholar.vector_adapter import BibleVectorAdapter, VerseSimilarityResult


@dataclass
class CrossLanguageConnection:
    """A Hebrew→Greek semantic connection.

    Attributes:
        hebrew_verse: Source Hebrew verse information
        greek_verse: Semantically similar Greek verse
        similarity_score: Cosine similarity (0.0-1.0)
    """

    hebrew_verse: dict
    greek_verse: VerseSimilarityResult
    similarity_score: float


@dataclass
class CrossLanguageResult:
    """Result from cross-language search.

    Attributes:
        strongs_id: Strong's number queried (H#### for Hebrew, G#### for Greek)
        lemma: Original language word
        hebrew_verses: Sample verses containing the Hebrew word
        connections: Hebrew→Greek semantic matches
        total_connections: Total number of connections found
    """

    strongs_id: str
    lemma: str
    hebrew_verses: list[dict]
    connections: list[CrossLanguageConnection]
    total_connections: int


def is_new_testament(book_name: str) -> bool:
    """Check if a book is in the New Testament.

    Args:
        book_name: Book abbreviation (e.g., "Mat", "Rom", "Gen")

    Returns:
        True if NT book, False if OT
    """
    nt_books = {
        "Mat",
        "Mrk",
        "Luk",
        "Jhn",
        "Act",
        "Rom",
        "1Co",
        "2Co",
        "Gal",
        "Eph",
        "Php",
        "Col",
        "1Th",
        "2Th",
        "1Ti",
        "2Ti",
        "Tit",
        "Phm",
        "Heb",
        "Jas",
        "1Pe",
        "2Pe",
        "1Jn",
        "2Jn",
        "3Jn",
        "Jud",
        "Rev",
    }
    return book_name in nt_books


def find_cross_language_connections(strongs_id: str, limit: int = 10) -> CrossLanguageResult | None:
    """Find Greek verses semantically similar to Hebrew word occurrences.

    Args:
        strongs_id: Strong's number (e.g., "H7965" for shalom)
        limit: Max connections to return

    Returns:
        CrossLanguageResult with Hebrew↔Greek connections, or None if word not found

    Example:
        >>> result = find_cross_language_connections("H7965", limit=5)  # shalom
        >>> for conn in result.connections:
        ...     print(f"Hebrew: {conn.hebrew_verse['text'][:50]}...")
        ...     print(f"Greek: {conn.greek_verse.text[:50]}... ({conn.similarity_score:.2%})")
    """
    # 1. Get verses containing the Hebrew word
    db_adapter = BibleDbAdapter()

    hebrew_verses_records = db_adapter.get_verses_by_strongs(strongs_id, limit=limit * 2)

    if not hebrew_verses_records:
        return None

    # Convert to dict format for serialization
    hebrew_verses = [
        {
            "verse_id": v.verse_id,
            "book_name": v.book_name,
            "chapter_num": v.chapter_num,
            "verse_num": v.verse_num,
            "text": v.text,
            "translation_source": v.translation_source,
        }
        for v in hebrew_verses_records
    ]

    # 2. For each Hebrew verse, find semantically similar Greek verses
    vector_adapter = BibleVectorAdapter()
    connections = []

    for heb_verse in hebrew_verses[:limit]:  # Limit Hebrew verses to search
        # Find verses similar to this Hebrew verse
        similar_verses = vector_adapter.find_similar_by_verse(
            heb_verse["verse_id"],
            limit=10,  # Get more candidates
            translation_source=None,  # Search all translations
        )

        # Filter to only Greek/NT verses
        greek_matches = [v for v in similar_verses if is_new_testament(v.book_name)]

        # Take top 2 Greek matches per Hebrew verse
        for greek_verse in greek_matches[:2]:
            connections.append(
                CrossLanguageConnection(
                    hebrew_verse=heb_verse,
                    greek_verse=greek_verse,
                    similarity_score=greek_verse.similarity_score,
                )
            )

    # Sort by similarity score
    connections.sort(key=lambda c: c.similarity_score, reverse=True)

    # Extract lemma from first verse (simplified - actual lemma would come from lexicon)
    lemma = strongs_id  # TODO: Get actual Hebrew lemma from lexicon table

    return CrossLanguageResult(
        strongs_id=strongs_id,
        lemma=lemma,
        hebrew_verses=hebrew_verses[:limit],
        connections=connections[:limit],
        total_connections=len(connections),
    )
