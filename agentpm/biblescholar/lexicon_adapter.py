from __future__ import annotations

"""BibleScholar Lexicon adapter (read-only).

This module provides read-only access to bible_db lexicon tables (Hebrew/Greek entries).
It uses centralized DSN loaders and handles DB-off mode gracefully.

See:
- docs/SSOT/BIBLESCHOLAR_MIGRATION_PLAN.md
- agentpm/biblescholar/AGENTS.md
"""

from dataclasses import dataclass
from typing import Literal

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from agentpm.db.loader import DbUnavailableError, get_bible_engine


@dataclass
class LexiconEntry:
    """A lexicon entry from bible_db (Hebrew or Greek).

    Attributes:
        entry_id: Primary key from lexicon entries table.
        strongs_id: Strong's number identifier (e.g., "H1", "G1").
        lemma: Dictionary form of the word.
        transliteration: Romanized form of the word.
        definition: Definition text.
        usage: Usage notes.
        gloss: Brief translation/gloss.
    """

    entry_id: int
    strongs_id: str
    lemma: str
    transliteration: str | None
    definition: str | None
    usage: str | None
    gloss: str | None


class LexiconAdapter:
    """Read-only adapter for bible_db lexicon tables.

    This adapter provides SELECT-only access to bible.hebrew_entries and bible.greek_entries.
    It never performs INSERT, UPDATE, or DELETE operations.

    Attributes:
        _engine: SQLAlchemy engine (lazy-initialized).
        _db_status: Current database status ("available", "unavailable", "db_off").
    """

    def __init__(self) -> None:
        """Initialize the lexicon adapter (lazy engine initialization)."""
        self._engine = None
        self._db_status = "unknown"

    def _ensure_engine(self) -> bool:
        """Ensure database engine is available.

        Returns:
            True if engine is available, False if DB is off/unavailable.

        Side effects:
            Sets self._db_status based on engine availability.
        """
        if self._engine is not None:
            return self._db_status == "available"

        try:
            self._engine = get_bible_engine()
            self._db_status = "available"
            return True
        except DbUnavailableError:
            self._db_status = "db_off"
            return False
        except (OperationalError, ProgrammingError):
            self._db_status = "unavailable"
            return False

    def _verse_ref_to_id(self, verse_ref: str) -> int | None:
        """Convert textual verse reference to integer verse_id for Greek tables.

        Phase 14 PR 14.3: Adapter layer queries verses table to get verse_id.
        Uses DB-ONLY logic to resolve book abbreviations (e.g., "Mark" -> "Mrk").

        Args:
            verse_ref: Verse reference in format "Book.Chapter.Verse" (e.g., "Mark.1.1").

        Returns:
            Integer verse_id if found, None if verse not found or DB unavailable.
        """
        if not self._ensure_engine():
            return None

        try:
            # Parse reference using the pure-function parser first
            # This handles "Mark 1:1" -> book="Mrk", chapter=1, verse=1
            from agentpm.biblescholar.reference_parser import parse_reference

            parsed = parse_reference(verse_ref)

            # Query the DB for the verse_id using the parsed components
            # We prioritize the KJV translation as the anchor for Greek words
            query = text("""
                SELECT verse_id 
                FROM bible.verses 
                WHERE book_name = :book 
                  AND chapter_num = :chapter 
                  AND verse_num = :verse 
                  AND translation_source = 'KJV'
            """)

            with self._engine.connect() as conn:
                result = conn.execute(
                    query,
                    {"book": parsed.book, "chapter": parsed.chapter, "verse": parsed.verse},
                )
                row = result.fetchone()
                return row[0] if row else None
        except (OperationalError, ProgrammingError):
            return None

    @property
    def db_status(self) -> Literal["available", "unavailable", "db_off"]:
        """Get current database status."""
        return self._db_status

    def get_hebrew_entry(self, strongs_id: str) -> LexiconEntry | None:
        """Get a Hebrew lexicon entry by Strong's number.

        Args:
            strongs_id: Strong's number (e.g., "H1", "H1234").

        Returns:
            LexiconEntry if found, None if not found or DB unavailable.
        """
        if not self._ensure_engine():
            return None

        try:
            query = text(
                """
                SELECT entry_id, strongs_id, lemma, transliteration, definition, usage, gloss
                FROM bible.hebrew_entries
                WHERE strongs_id = :strongs_id
                LIMIT 1
                """
            )
            with self._engine.connect() as conn:
                result = conn.execute(query, {"strongs_id": strongs_id})
                row = result.fetchone()
                if row is None:
                    return None

                return LexiconEntry(
                    entry_id=row[0],
                    strongs_id=row[1],
                    lemma=row[2],
                    transliteration=row[3],
                    definition=row[4],
                    usage=row[5],
                    gloss=row[6],
                )
        except (OperationalError, ProgrammingError):
            self._db_status = "unavailable"
            return None

    def get_greek_entry(self, strongs_id: str) -> LexiconEntry | None:
        """Get a Greek lexicon entry by Strong's number.

        Args:
            strongs_id: Strong's number (e.g., "G1", "G1234").

        Returns:
            LexiconEntry if found, None if not found or DB unavailable.
        """
        if not self._ensure_engine():
            return None

        try:
            query = text(
                """
                SELECT entry_id, strongs_id, lemma, transliteration, definition, usage, gloss
                FROM bible.greek_entries
                WHERE strongs_id = :strongs_id
                LIMIT 1
                """
            )
            with self._engine.connect() as conn:
                result = conn.execute(query, {"strongs_id": strongs_id})
                row = result.fetchone()
                if row is None:
                    return None

                return LexiconEntry(
                    entry_id=row[0],
                    strongs_id=row[1],
                    lemma=row[2],
                    transliteration=row[3],
                    definition=row[4],
                    usage=row[5],
                    gloss=row[6],
                )
        except (OperationalError, ProgrammingError):
            self._db_status = "unavailable"
            return None

    def get_greek_words_for_verse(self, verse_ref: str) -> list[dict] | None:
        """Get all Greek words for a verse using textual reference.

        Phase 14 PR 14.3: Queries verses table for verse_id, then queries greek_nt_words.

        Args:
            verse_ref: Verse reference (e.g., "Mark.1.1").

        Returns:
            List of Greek word dictionaries, empty list if no words, None if DB unavailable.
        """
        if not self._ensure_engine():
            return None

        verse_id = self._verse_ref_to_id(verse_ref)
        if verse_id is None:
            return []

        try:
            query = text(
                """
                SELECT
                    w.word_position,
                    w.word_text AS surface,
                    w.strongs_id,
                    w.grammar_code,
                    e.lemma,
                    e.gloss
                FROM bible.greek_nt_words w
                LEFT JOIN bible.greek_entries e ON w.strongs_id = e.strongs_id
                WHERE w.verse_id = :verse_id
                ORDER BY w.word_position
                """
            )
            with self._engine.connect() as conn:
                result = conn.execute(query, {"verse_id": verse_id})
                rows = result.fetchall()

                words = []
                for row in rows:
                    words.append(
                        {
                            "word_position": row[0],
                            "surface": row[1],
                            "strongs_id": row[2],
                            "grammar_code": row[3],
                            "lemma": row[4],
                            "gloss": row[5],
                            "language": "GR",
                        }
                    )
                return words

        except (OperationalError, ProgrammingError):
            self._db_status = "unavailable"
            return None

    def get_entries_for_reference(
        self, book_name: str, chapter_num: int, verse_num: int
    ) -> list[LexiconEntry]:
        """Get lexicon entries for all words in a verse reference.

        This queries hebrew_ot_words and greek_nt_words to find Strong's numbers,
        then fetches the corresponding lexicon entries.

        Args:
            book_name: Book name (e.g., "Genesis", "Matthew").
            chapter_num: Chapter number (1-indexed).
            verse_num: Verse number (1-indexed).

        Returns:
            List of LexiconEntry objects (may be empty if no entries found or DB unavailable).
        """
        if not self._ensure_engine():
            return []

        try:
            # First, get the verse_id
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
            with self._engine.connect() as conn:
                verse_result = conn.execute(
                    verse_query,
                    {"book_name": book_name, "chapter_num": chapter_num, "verse_num": verse_num},
                )
                verse_row = verse_result.fetchone()
                if verse_row is None:
                    return []

                verse_id = verse_row[0]

                # Get Hebrew words with Strong's numbers
                hebrew_query = text(
                    """
                    SELECT DISTINCT strongs_id
                    FROM bible.hebrew_ot_words
                    WHERE verse_id = :verse_id
                      AND strongs_id IS NOT NULL
                      AND strongs_id != ''
                    """
                )
                hebrew_result = conn.execute(hebrew_query, {"verse_id": verse_id})
                hebrew_strongs = [row[0] for row in hebrew_result]

                # Get Greek words with Strong's numbers
                greek_query = text(
                    """
                    SELECT DISTINCT strongs_id
                    FROM bible.greek_nt_words
                    WHERE verse_id = :verse_id
                      AND strongs_id IS NOT NULL
                      AND strongs_id != ''
                    """
                )
                greek_result = conn.execute(greek_query, {"verse_id": verse_id})
                greek_strongs = [row[0] for row in greek_result]

                # Fetch lexicon entries
                entries: list[LexiconEntry] = []
                for strongs_id in hebrew_strongs:
                    entry = self.get_hebrew_entry(strongs_id)
                    if entry:
                        entries.append(entry)

                for strongs_id in greek_strongs:
                    entry = self.get_greek_entry(strongs_id)
                    if entry:
                        entries.append(entry)

                return entries
        except (OperationalError, ProgrammingError):
            self._db_status = "unavailable"
            return []
