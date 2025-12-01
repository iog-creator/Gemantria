"""BibleScholar cross-language word analysis flow (read-only).

This module provides advanced word analysis and cross-language (Hebrew/Greek) connections.
It uses the lexicon adapter and vector search to find conceptual links.

See:
- docs/SSOT/BIBLESCHOLAR_MIGRATION_PLAN.md
- agentpm/biblescholar/AGENTS.md
"""

from __future__ import annotations

import json
import os
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, Literal

from agentpm.biblescholar.bible_passage_flow import parse_reference
from agentpm.biblescholar.lexicon_adapter import LexiconAdapter
from agentpm.biblescholar.lexicon_flow import fetch_lexicon_entry, fetch_word_study
from agentpm.biblescholar.vector_flow import similar_verses_for_reference


@dataclass
class WordAnalysis:
    """Analysis of a word in context.

    Attributes:
        strongs_id: Strong's number identifier (e.g., "H1", "G1").
        lemma: Dictionary form of the word.
        gloss: Brief translation/gloss.
        occurrence_count: Number of times this word appears in the Bible.
        related_verses: List of Bible references where this word appears.
    """

    strongs_id: str
    lemma: str
    gloss: str | None
    occurrence_count: int
    related_verses: list[str]


@dataclass
class CrossLanguageMatch:
    """Cross-language connection between words.

    Attributes:
        source_strongs: Source Strong's number (e.g., "H1").
        target_strongs: Target Strong's number in the other language (e.g., "G1").
        target_lemma: Dictionary form of the target word.
        similarity_score: Similarity score (0.0 to 1.0, higher is more similar).
        common_verses: List of Bible references where both words appear (may be empty).
    """

    source_strongs: str
    target_strongs: str
    target_lemma: str
    similarity_score: float
    common_verses: list[str]


# Path to the Greek-to-Hebrew Strong's mapping file
MAPPING_FILE = "config/greek_to_hebrew_strongs.json"


def resolve_cross_language_lemma(greek_strongs: str) -> Dict[str, Any] | None:
    """Resolve a Greek Strong's number to its Hebrew equivalent and lemma.

    Phase 14 PR 14.3: Track 3 - Cross-Language Lemma Resolution.
    Uses a static JSON mapping file to link Greek terms to Hebrew equivalents,
    then queries the Hebrew lexicon for the lemma.

    Args:
        greek_strongs: Greek Strong's number (e.g., "G2316").

    Returns:
        Dictionary with mapping details or None if no mapping exists.
        Format:
        {
            "greek_strongs": "G2316",
            "hebrew_strongs": "H430",
            "hebrew_lemma": "אֱלֹהִים",
            "mapping_source": "static_map"
        }
    """
    if not os.path.exists(MAPPING_FILE):
        return None

    try:
        with open(MAPPING_FILE, encoding="utf-8") as f:
            data = json.load(f)
            mappings = data.get("mappings", {})
    except (json.JSONDecodeError, OSError):
        return None

    hebrew_strongs = mappings.get(greek_strongs)
    if not hebrew_strongs:
        return None

    # Fetch Hebrew lemma from DB using LexiconAdapter
    adapter = LexiconAdapter()
    # We need to find the entry with this Strong's ID
    # Since LexiconAdapter is read-only and doesn't have a direct "get_by_strongs" method exposed publicly in the interface shown,
    # we might need to add one or use a direct query here if the adapter allows.
    # Looking at LexiconAdapter, it seems to lack a direct "get_entry_by_strongs" method in the snippet.
    # However, fetch_lexicon_entry in lexicon_flow might be useful, or we can add a helper here.

    # Let's use a direct DB query via the adapter's engine for now to ensure we get the lemma
    # This keeps it contained within the flow logic using the adapter's connection
    if not adapter._ensure_engine():
        return None

    try:
        from sqlalchemy import text

        query = text(
            "SELECT lemma FROM bible.hebrew_entries WHERE strongs_id = :strongs_id LIMIT 1"
        )
        with adapter._engine.connect() as conn:
            result = conn.execute(query, {"strongs_id": hebrew_strongs}).fetchone()
            hebrew_lemma = result[0] if result else None
    except Exception:
        hebrew_lemma = None

    if not hebrew_lemma:
        return None

    return {
        "greek_strongs": greek_strongs,
        "hebrew_strongs": hebrew_strongs,
        "hebrew_lemma": hebrew_lemma,
        "mapping_source": "static_map",
    }


def analyze_word_in_context(ref: str, strongs_id: str) -> WordAnalysis | None:
    """Analyze a word in context of a specific verse.

    Validates that the word exists in the verse, fetches lexicon details,
    and finds other occurrences of the word.

    Args:
        ref: Bible reference string (e.g., "Genesis 1:1").
        strongs_id: Strong's number identifier (e.g., "H1", "G1").

    Returns:
        WordAnalysis if word found in verse, None otherwise.
    """
    # Parse reference
    parsed = parse_reference(ref)
    if parsed is None:
        return None

    # Validate word exists in verse via lexicon_flow
    word_study = fetch_word_study(ref)
    if not word_study:
        return None

    # Check if the Strong's ID is in the verse
    strongs_ids_in_verse = {entry.strongs_id for entry in word_study.entries}
    if strongs_id.upper() not in strongs_ids_in_verse:
        return None

    # Fetch lexicon entry
    entry = fetch_lexicon_entry(strongs_id)
    if not entry:
        return None

    # Find other occurrences (simplified: query database for occurrences)
    adapter = LexiconAdapter()
    if not adapter._ensure_engine():
        return WordAnalysis(
            strongs_id=strongs_id,
            lemma=entry.lemma,
            gloss=entry.gloss,
            occurrence_count=0,
            related_verses=[],
        )

    # Query for occurrences of this Strong's number
    from sqlalchemy import text

    try:
        # Determine language from Strong's prefix
        is_hebrew = strongs_id.upper().startswith("H")
        word_table = "bible.hebrew_ot_words" if is_hebrew else "bible.greek_nt_words"

        query = text(
            f"""
            SELECT DISTINCT v.book_name, v.chapter_num, v.verse_num
            FROM {word_table} w
            JOIN bible.verses v ON w.verse_id = v.verse_id
            WHERE w.strongs_id = :strongs_id
            ORDER BY v.book_name, v.chapter_num, v.verse_num
            LIMIT 50
            """
        )

        with adapter._engine.connect() as conn:
            result = conn.execute(query, {"strongs_id": strongs_id.upper()})
            related_verses = [
                f"{row[0]} {row[1]}:{row[2]}" for row in result if row[0] and row[1] and row[2]
            ]

        # Get total count
        count_query = text(
            f"""
            SELECT COUNT(DISTINCT verse_id)
            FROM {word_table}
            WHERE strongs_id = :strongs_id
            """
        )
        with adapter._engine.connect() as conn:
            count_result = conn.execute(count_query, {"strongs_id": strongs_id.upper()})
            occurrence_count = count_result.fetchone()[0] or 0

        return WordAnalysis(
            strongs_id=strongs_id,
            lemma=entry.lemma,
            gloss=entry.gloss,
            occurrence_count=occurrence_count,
            related_verses=related_verses,
        )
    except Exception:
        # If query fails, return basic analysis
        return WordAnalysis(
            strongs_id=strongs_id,
            lemma=entry.lemma,
            gloss=entry.gloss,
            occurrence_count=0,
            related_verses=[],
        )


def find_cross_language_connections(
    strongs_id: str, reference: str | None = None, limit: int = 10
) -> list[CrossLanguageMatch]:
    """Find cross-language connections for a Strong's number.

    Uses vector similarity to find verses with the source word, then analyzes
    those verses to find frequently co-occurring words in the other language.

    For Phase A, this is simplified: it uses vector similarity between verses
    containing the word to find similar verses in the other testament, then
    extracts prominent words.

    Args:
        strongs_id: Source Strong's number (e.g., "H1" for Hebrew, "G1" for Greek).
        reference: Optional Bible reference to use as starting point for vector search.
                  If None, uses the first occurrence found.
        limit: Maximum number of similar verses to analyze (default: 10).

    Returns:
        List of CrossLanguageMatch objects, ordered by similarity score (highest first).
    """
    # Get source lexicon entry
    source_entry = fetch_lexicon_entry(strongs_id)
    if not source_entry:
        return []

    # Determine source language
    is_hebrew = strongs_id.upper().startswith("H")
    target_language_prefix = "G" if is_hebrew else "H"

    # Find a reference containing this word
    if reference is None:
        # Find first occurrence
        adapter = LexiconAdapter()
        if not adapter._ensure_engine():
            return []

        from sqlalchemy import text

        word_table = "bible.hebrew_ot_words" if is_hebrew else "bible.greek_nt_words"
        query = text(
            f"""
            SELECT DISTINCT v.book_name, v.chapter_num, v.verse_num
            FROM {word_table} w
            JOIN bible.verses v ON w.verse_id = v.verse_id
            WHERE w.strongs_id = :strongs_id
            ORDER BY v.book_name, v.chapter_num, v.verse_num
            LIMIT 1
            """
        )

        try:
            with adapter._engine.connect() as conn:
                result = conn.execute(query, {"strongs_id": strongs_id.upper()})
                row = result.fetchone()
                if row:
                    reference = f"{row[0]} {row[1]}:{row[2]}"
                else:
                    return []
        except Exception:
            return []
    else:
        # Validate word exists in reference
        word_study = fetch_word_study(reference)
        if not word_study:
            return []
        strongs_ids_in_verse = {entry.strongs_id for entry in word_study.entries}
        if strongs_id.upper() not in strongs_ids_in_verse:
            return []

    # Find similar verses using vector search
    similar_verses = similar_verses_for_reference(reference or "", "KJV", limit=limit)
    if not similar_verses:
        return []

    # Extract Strong's numbers from similar verses (in the other language)
    target_strongs_counter: Counter[str] = Counter()
    verse_to_strongs: dict[str, list[str]] = {}

    adapter = LexiconAdapter()
    if not adapter._ensure_engine():
        return []

    from sqlalchemy import text

    target_word_table = "bible.greek_nt_words" if is_hebrew else "bible.hebrew_ot_words"

    for similar_verse in similar_verses:
        verse_ref = (
            f"{similar_verse.book_name} {similar_verse.chapter_num}:{similar_verse.verse_num}"
        )

        # Get verse_id
        verse_query = text(
            """
            SELECT verse_id
            FROM bible.verses
            WHERE book_name = :book_name
              AND chapter_num = :chapter_num
              AND verse_num = :verse_num
            LIMIT 1
            """
        )

        try:
            with adapter._engine.connect() as conn:
                verse_result = conn.execute(
                    verse_query,
                    {
                        "book_name": similar_verse.book_name,
                        "chapter_num": similar_verse.chapter_num,
                        "verse_num": similar_verse.verse_num,
                    },
                )
                verse_row = verse_result.fetchone()
                if not verse_row:
                    continue

                verse_id = verse_row[0]

                # Get Strong's numbers from target language
                strongs_query = text(
                    f"""
                    SELECT DISTINCT strongs_id
                    FROM {target_word_table}
                    WHERE verse_id = :verse_id
                      AND strongs_id IS NOT NULL
                      AND strongs_id != ''
                      AND strongs_id LIKE :prefix
                    """
                )
                strongs_result = conn.execute(
                    strongs_query, {"verse_id": verse_id, "prefix": f"{target_language_prefix}%"}
                )
                target_strongs = [row[0] for row in strongs_result if row[0]]

                if target_strongs:
                    verse_to_strongs[verse_ref] = target_strongs
                    target_strongs_counter.update(target_strongs)
        except Exception:
            continue

    # Build CrossLanguageMatch objects
    matches: list[CrossLanguageMatch] = []
    for target_strongs, count in target_strongs_counter.most_common(limit):
        # Get target lexicon entry
        target_entry = fetch_lexicon_entry(target_strongs)
        if not target_entry:
            continue

        # Find common verses (verses that contain both source and target)
        common_verses = [
            verse_ref
            for verse_ref, strongs_list in verse_to_strongs.items()
            if target_strongs in strongs_list
        ]

        # Calculate similarity score (simplified: based on co-occurrence frequency)
        similarity_score = min(count / limit, 1.0)

        matches.append(
            CrossLanguageMatch(
                source_strongs=strongs_id,
                target_strongs=target_strongs,
                target_lemma=target_entry.lemma,
                similarity_score=similarity_score,
                common_verses=common_verses,
            )
        )

    # Sort by similarity score (highest first)
    matches.sort(key=lambda x: x.similarity_score, reverse=True)

    return matches


def get_db_status(
    adapter: LexiconAdapter | None = None,
) -> Literal["available", "unavailable", "db_off"]:
    """Get current database status.

    Args:
        adapter: Optional LexiconAdapter instance. If None, creates a new one.

    Returns:
        Database status string.
    """
    if adapter is None:
        adapter = LexiconAdapter()
    return adapter.db_status
