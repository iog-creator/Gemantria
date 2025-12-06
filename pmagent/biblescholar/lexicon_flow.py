from __future__ import annotations

"""BibleScholar lexicon/word-study flow (read-only).

This module provides simple, composable flows for retrieving lexicon entries
from bible_db using the lexicon_adapter. No LM calls, no Gematria here.

See:
- docs/SSOT/BIBLESCHOLAR_MIGRATION_PLAN.md
- pmagent/biblescholar/AGENTS.md
"""

from dataclasses import dataclass
from typing import Literal

from pmagent.biblescholar.bible_passage_flow import parse_reference
from pmagent.biblescholar.lexicon_adapter import LexiconAdapter, LexiconEntry


@dataclass
class WordStudyResult:
    """Result of a word study query.

    Attributes:
        reference: Bible reference string (e.g., "Genesis 1:1").
        entries: List of lexicon entries found for words in the verse.
        db_status: Database status at time of query.
    """

    reference: str
    entries: list[LexiconEntry]
    db_status: Literal["available", "unavailable", "db_off"]


def fetch_lexicon_entry(strongs_id: str) -> LexiconEntry | None:
    """Fetch a lexicon entry by Strong's number.

    Automatically determines whether to query Hebrew or Greek based on Strong's prefix.

    Args:
        strongs_id: Strong's number (e.g., "H1" for Hebrew, "G1" for Greek).

    Returns:
        LexiconEntry if found, None if not found or DB unavailable.
    """
    adapter = LexiconAdapter()

    # Determine language from Strong's prefix
    if strongs_id.upper().startswith("H"):
        return adapter.get_hebrew_entry(strongs_id)
    elif strongs_id.upper().startswith("G"):
        return adapter.get_greek_entry(strongs_id)
    else:
        # Try Hebrew first, then Greek
        entry = adapter.get_hebrew_entry(strongs_id)
        if entry:
            return entry
        return adapter.get_greek_entry(strongs_id)


def fetch_word_study(reference: str) -> WordStudyResult:
    """Fetch word study data for a Bible reference.

    Retrieves all lexicon entries for words in the specified verse.

    Args:
        reference: Bible reference string (e.g., "Genesis 1:1", "Matthew 5:3").

    Returns:
        WordStudyResult with lexicon entries and database status.
    """
    adapter = LexiconAdapter()

    # Parse reference
    parsed = parse_reference(reference)
    if parsed is None:
        return WordStudyResult(reference=reference, entries=[], db_status=adapter.db_status)

    book_name, chapter_num, verse_num = parsed

    # Get entries for the verse
    entries = adapter.get_entries_for_reference(book_name, chapter_num, verse_num)

    return WordStudyResult(reference=reference, entries=entries, db_status=adapter.db_status)


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
