from __future__ import annotations

"""BibleScholar Bible DB adapter (read-only).

This module provides read-only access to bible_db for verses and passages.
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
class VerseRecord:
    """A single verse record from bible_db.

    Attributes:
        verse_id: Primary key from bible.verses table.
        book_name: Book name (e.g., "Genesis", "Matthew").
        chapter_num: Chapter number (1-indexed).
        verse_num: Verse number (1-indexed).
        text: Verse text content.
        translation_source: Translation identifier (e.g., "KJV", "ESV").
    """

    verse_id: int
    book_name: str
    chapter_num: int
    verse_num: int
    text: str
    translation_source: str


class BibleDbAdapter:
    """Read-only adapter for bible_db database.

    This adapter provides SELECT-only access to bible.verses and related tables.
    It never performs INSERT, UPDATE, or DELETE operations.

    Attributes:
        _engine: SQLAlchemy engine (lazy-initialized).
        _db_status: Current database status ("available", "unavailable", "db_off").
    """

    def __init__(self) -> None:
        """Initialize the adapter (lazy engine initialization)."""
        self._engine = None
        self._db_status: Literal["available", "unavailable", "db_off"] = "db_off"

    def _ensure_engine(self) -> bool:
        """Ensure database engine is available.

        Returns:
            True if engine is available, False if DB is off/unavailable.

        Side effects:
            Sets self._db_status based on engine availability.
        """
        if self._engine is not None:
            return True

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

    def get_verse(
        self, book_name: str, chapter_num: int, verse_num: int, translation_source: str = "KJV"
    ) -> VerseRecord | None:
        """Get a single verse by reference.

        Args:
            book_name: Book name (e.g., "Genesis", "Matthew").
            chapter_num: Chapter number (1-indexed).
            verse_num: Verse number (1-indexed).
            translation_source: Translation identifier (default: "KJV").

        Returns:
            VerseRecord if found, None if not found or DB unavailable.
        """
        if not self._ensure_engine():
            return None

        try:
            query = text(
                """
                SELECT verse_id, book_name, chapter_num, verse_num, text, translation_source
                FROM bible.verses
                WHERE book_name = :book_name
                  AND chapter_num = :chapter_num
                  AND verse_num = :verse_num
                  AND translation_source = :translation_source
                LIMIT 1
                """
            )

            with self._engine.connect() as conn:
                result = conn.execute(
                    query,
                    {
                        "book_name": book_name,
                        "chapter_num": chapter_num,
                        "verse_num": verse_num,
                        "translation_source": translation_source,
                    },
                )
                row = result.fetchone()

                if row is None:
                    return None

                return VerseRecord(
                    verse_id=row[0],
                    book_name=row[1],
                    chapter_num=row[2],
                    verse_num=row[3],
                    text=row[4],
                    translation_source=row[5],
                )
        except (OperationalError, ProgrammingError):
            self._db_status = "unavailable"
            return None

    def get_passage(
        self,
        book_name: str,
        start_chapter: int,
        start_verse: int,
        end_chapter: int,
        end_verse: int,
        translation_source: str = "KJV",
    ) -> list[VerseRecord]:
        """Get a passage (range of verses).

        Args:
            book_name: Book name (e.g., "Genesis", "Matthew").
            start_chapter: Starting chapter number (1-indexed).
            start_verse: Starting verse number (1-indexed).
            end_chapter: Ending chapter number (1-indexed).
            end_verse: Ending verse number (1-indexed).
            translation_source: Translation identifier (default: "KJV").

        Returns:
            List of VerseRecord objects, ordered by chapter and verse.
            Empty list if no verses found or DB unavailable.
        """
        if not self._ensure_engine():
            return []

        try:
            query = text(
                """
                SELECT verse_id, book_name, chapter_num, verse_num, text, translation_source
                FROM bible.verses
                WHERE book_name = :book_name
                  AND translation_source = :translation_source
                  AND (
                    (chapter_num = :start_chapter AND verse_num >= :start_verse)
                    OR (chapter_num > :start_chapter AND chapter_num < :end_chapter)
                    OR (chapter_num = :end_chapter AND verse_num <= :end_verse)
                  )
                ORDER BY chapter_num, verse_num
                """
            )

            with self._engine.connect() as conn:
                result = conn.execute(
                    query,
                    {
                        "book_name": book_name,
                        "start_chapter": start_chapter,
                        "start_verse": start_verse,
                        "end_chapter": end_chapter,
                        "end_verse": end_verse,
                        "translation_source": translation_source,
                    },
                )

                verses = []
                for row in result:
                    verses.append(
                        VerseRecord(
                            verse_id=row[0],
                            book_name=row[1],
                            chapter_num=row[2],
                            verse_num=row[3],
                            text=row[4],
                            translation_source=row[5],
                        )
                    )

                return verses
        except (OperationalError, ProgrammingError):
            self._db_status = "unavailable"
            return []

    @property
    def db_status(self) -> Literal["available", "unavailable", "db_off"]:
        """Get current database status.

        Returns:
            "available" if DB is connected and working.
            "unavailable" if connection failed.
            "db_off" if DSN not set or DB not configured.
        """
        self._ensure_engine()  # Update status
        return self._db_status
