from __future__ import annotations

"""BibleScholar Relationship adapter (read-only).

This module provides read-only access to bible_db relationship tables
(verse_word_links, proper_names) for enriching RAG context.

See:
- docs/SSOT/BIBLESCHOLAR_MIGRATION_PLAN.md
- pmagent/biblescholar/AGENTS.md
"""

from dataclasses import dataclass
from typing import Literal

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from pmagent.db.loader import DbUnavailableError, get_bible_engine


@dataclass
class ProperName:
    """A proper name entry from bible.proper_names.

    Attributes:
        unified_name: Unified name identifier.
        type: Type of proper name (PERSON, PLACE, OTHER).
        category: Category classification.
        briefest: Briefest description.
        brief: Brief description.
        short: Short description.
        article: Full article text.
        description: Description text.
        parents: Parent relationships.
        siblings: Sibling relationships.
        partners: Partner relationships.
        offspring: Offspring relationships.
        tribe_nation: Tribe/nation information.
        summary: Summary text.
    """

    unified_name: str
    type: str | None
    category: str | None
    briefest: str | None
    brief: str | None
    short: str | None
    article: str | None
    description: str | None
    parents: str | None
    siblings: str | None
    partners: str | None
    offspring: str | None
    tribe_nation: str | None
    summary: str | None


@dataclass
class VerseWordLink:
    """A verse-word link from bible.verse_word_links.

    Attributes:
        link_id: Primary key.
        verse_id: Verse identifier.
        word_id: Word identifier.
        word_type: Type of word link.
    """

    link_id: int
    verse_id: int
    word_id: int
    word_type: str


@dataclass
class EnrichedContext:
    """Enriched RAG context for a verse.

    Attributes:
        verse_id: Verse identifier.
        proper_names: List of proper names found in the verse.
        word_links: List of verse-word links (if available).
        context_summary: Summary of contextual relationships.
    """

    verse_id: int
    proper_names: list[ProperName]
    word_links: list[VerseWordLink]
    context_summary: str | None


class RelationshipAdapter:
    """Read-only adapter for bible_db relationship tables.

    This adapter provides SELECT-only access to bible.verse_word_links and
    bible.proper_names. It never performs INSERT, UPDATE, or DELETE operations.

    DB-ONLY strategy: All queries use direct SQL against bible_db.
    """

    def __init__(self) -> None:
        """Initialize the relationship adapter."""
        self._db_status: Literal["ready", "unavailable"] = "ready"

    def get_proper_names_for_verse(self, verse_id: int, limit: int = 10) -> list[ProperName]:
        """Get proper names that appear in a verse.

        This method matches verse words against proper_names.unified_name
        to find relevant proper name entries.

        Args:
            verse_id: Verse identifier.
            limit: Maximum number of proper names to return.

        Returns:
            List of ProperName entries found in the verse.
        """
        if self._db_status == "unavailable":
            return []

        try:
            engine = get_bible_engine()
            with engine.connect() as conn:
                # Get words from the verse (both Hebrew and Greek)
                words_query = text(
                    """
                    SELECT DISTINCT word_text
                    FROM (
                        SELECT word_text
                        FROM bible.hebrew_ot_words
                        WHERE verse_id = :verse_id
                          AND word_text IS NOT NULL
                          AND word_text != ''
                        UNION
                        SELECT word_text
                        FROM bible.greek_nt_words
                        WHERE verse_id = :verse_id
                          AND word_text IS NOT NULL
                          AND word_text != ''
                    ) AS all_words
                    """
                )
                words_result = conn.execute(words_query, {"verse_id": verse_id})
                words = [row[0] for row in words_result]

                if not words:
                    return []

                # Match words against proper_names
                # Use ILIKE for case-insensitive matching
                proper_names: list[ProperName] = []
                for word in words:
                    # Try exact match first
                    name_query = text(
                        """
                        SELECT unified_name, type, category, briefest, brief, short,
                               article, description, parents, siblings, partners,
                               offspring, tribe_nation, summary
                        FROM bible.proper_names
                        WHERE unified_name ILIKE :word
                           OR unified_name ILIKE :word_pattern
                        LIMIT :limit_per_word
                        """
                    )
                    name_result = conn.execute(
                        name_query,
                        {
                            "word": word,
                            "word_pattern": f"%{word}%",
                            "limit_per_word": 5,
                        },
                    )

                    for row in name_result:
                        # Avoid duplicates
                        if any(pn.unified_name == row[0] for pn in proper_names):
                            continue

                        proper_names.append(
                            ProperName(
                                unified_name=row[0] or "",
                                type=row[1],
                                category=row[2],
                                briefest=row[3],
                                brief=row[4],
                                short=row[5],
                                article=row[6],
                                description=row[7],
                                parents=row[8],
                                siblings=row[9],
                                partners=row[10],
                                offspring=row[11],
                                tribe_nation=row[12],
                                summary=row[13],
                            )
                        )

                        if len(proper_names) >= limit:
                            break

                    if len(proper_names) >= limit:
                        break

                return proper_names[:limit]

        except (OperationalError, ProgrammingError, DbUnavailableError):
            self._db_status = "unavailable"
            return []

    def get_verse_word_links(self, verse_id: int) -> list[VerseWordLink]:
        """Get verse-word links for a verse.

        Args:
            verse_id: Verse identifier.

        Returns:
            List of VerseWordLink entries for the verse.
        """
        if self._db_status == "unavailable":
            return []

        try:
            engine = get_bible_engine()
            with engine.connect() as conn:
                links_query = text(
                    """
                    SELECT id, verse_id, word_id, word_type
                    FROM bible.verse_word_links
                    WHERE verse_id = :verse_id
                    ORDER BY id
                    """
                )
                links_result = conn.execute(links_query, {"verse_id": verse_id})
                return [
                    VerseWordLink(
                        link_id=row[0],
                        verse_id=row[1],
                        word_id=row[2],
                        word_type=row[3],
                    )
                    for row in links_result
                ]

        except (OperationalError, ProgrammingError, DbUnavailableError):
            self._db_status = "unavailable"
            return []

    def get_enriched_context(self, verse_id: int, include_word_links: bool = True) -> EnrichedContext | None:
        """Get enriched RAG context for a verse.

        This method combines proper names and word links to create
        an enriched context for RAG retrieval.

        Args:
            verse_id: Verse identifier.
            include_word_links: Whether to include verse-word links.

        Returns:
            EnrichedContext with proper names and word links, or None if verse not found.
        """
        if self._db_status == "unavailable":
            return None

        try:
            engine = get_bible_engine()
            with engine.connect() as conn:
                # Verify verse exists
                verse_check = text("SELECT verse_id FROM bible.verses WHERE verse_id = :verse_id")
                verse_result = conn.execute(verse_check, {"verse_id": verse_id})
                if verse_result.fetchone() is None:
                    return None

                # Get proper names
                proper_names = self.get_proper_names_for_verse(verse_id)

                # Get word links (if requested and available)
                word_links: list[VerseWordLink] = []
                if include_word_links:
                    word_links = self.get_verse_word_links(verse_id)

                # Generate context summary
                context_summary = None
                if proper_names:
                    names_list = ", ".join([pn.unified_name for pn in proper_names[:5]])
                    context_summary = f"Proper names: {names_list}"
                    if len(proper_names) > 5:
                        context_summary += f" (+{len(proper_names) - 5} more)"

                return EnrichedContext(
                    verse_id=verse_id,
                    proper_names=proper_names,
                    word_links=word_links,
                    context_summary=context_summary,
                )

        except (OperationalError, ProgrammingError, DbUnavailableError):
            self._db_status = "unavailable"
            return None

    def get_proper_name_by_unified_name(self, unified_name: str) -> ProperName | None:
        """Get a proper name entry by unified_name.

        Args:
            unified_name: Unified name identifier.

        Returns:
            ProperName entry if found, None otherwise.
        """
        if self._db_status == "unavailable":
            return None

        try:
            engine = get_bible_engine()
            with engine.connect() as conn:
                name_query = text(
                    """
                    SELECT unified_name, type, category, briefest, brief, short,
                           article, description, parents, siblings, partners,
                           offspring, tribe_nation, summary
                    FROM bible.proper_names
                    WHERE unified_name = :unified_name
                    LIMIT 1
                    """
                )
                name_result = conn.execute(name_query, {"unified_name": unified_name})
                row = name_result.fetchone()

                if row is None:
                    return None

                return ProperName(
                    unified_name=row[0] or "",
                    type=row[1],
                    category=row[2],
                    briefest=row[3],
                    brief=row[4],
                    short=row[5],
                    article=row[6],
                    description=row[7],
                    parents=row[8],
                    siblings=row[9],
                    partners=row[10],
                    offspring=row[11],
                    tribe_nation=row[12],
                    summary=row[13],
                )

        except (OperationalError, ProgrammingError, DbUnavailableError):
            self._db_status = "unavailable"
            return None

    def get_enriched_context_batch(
        self, verse_ids: list[int], include_word_links: bool = False
    ) -> dict[int, EnrichedContext]:
        """Get enriched RAG context for multiple verses (batch query).

        Optimizes context window queries by processing multiple verses together.

        Args:
            verse_ids: List of verse identifiers
            include_word_links: Whether to include verse-word links (default: False for performance)

        Returns:
            Dictionary mapping verse_id to EnrichedContext.

        Note:
            This is a simplified batch implementation. Full optimization
            would require complex SQL with GROUP BY. For Phase 15 Wave-2,
            we iterate per verse but with shared connection.
        """
        if not verse_ids or self._db_status == "unavailable":
            return {}

        result: dict[int, EnrichedContext] = {}

        for verse_id in verse_ids:
            ctx = self.get_enriched_context(verse_id, include_word_links=include_word_links)
            if ctx:
                result[verse_id] = ctx

        return result
