from __future__ import annotations

"""BibleScholar Vector similarity adapter (read-only).

This module provides read-only access to bible_db for verse vector similarity queries.
It uses centralized DSN loaders and handles DB-off mode gracefully.

Uses 1024-dimensional embeddings from bible.verse_embeddings table (BGE-M3 compatible).
Previously used 768-dim embeddings from bible.verses.embedding (deprecated).

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
class VerseSimilarityResult:
    """A verse similarity result from vector search.

    Attributes:
        verse_id: Primary key from bible.verses table.
        book_name: Book name (e.g., "Genesis", "Matthew").
        chapter_num: Chapter number (1-indexed).
        verse_num: Verse number (1-indexed).
        text: Verse text content.
        translation_source: Translation identifier (e.g., "KJV", "ESV").
        similarity_score: Cosine similarity score (0.0 to 1.0, higher is more similar).
    """

    verse_id: int
    book_name: str
    chapter_num: int
    verse_num: int
    text: str
    translation_source: str
    similarity_score: float


class BibleVectorAdapter:
    """Read-only adapter for bible_db vector similarity queries.

    This adapter provides SELECT-only access to bible.verse_embeddings with vector similarity search.
    Uses 1024-dimensional embeddings (BGE-M3 compatible) from verse_embeddings table.
    Joins with bible.verses to retrieve verse text and metadata.
    It uses pgvector's cosine distance operator (<->) for similarity calculations.
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

    def find_similar_by_verse(
        self, verse_id: int, limit: int = 10, translation_source: str | None = None
    ) -> list[VerseSimilarityResult]:
        """Find similar verses by verse_id using vector similarity.

        Args:
            verse_id: Primary key of the source verse.
            limit: Maximum number of results to return (default: 10).
            translation_source: Optional translation filter (e.g., "KJV"). If None, searches all translations.

        Returns:
            List of VerseSimilarityResult objects, ordered by similarity (highest first).
            Empty list if verse not found, no similar verses, or DB unavailable.
        """
        if not self._ensure_engine():
            return []

        try:
            # First, get the source verse's embedding from verse_embeddings (1024-dim)
            source_query = text(
                """
                SELECT embedding
                FROM bible.verse_embeddings
                WHERE verse_id = :verse_id
                  AND embedding IS NOT NULL
                LIMIT 1
                """
            )

            with self._engine.connect() as conn:
                source_result = conn.execute(source_query, {"verse_id": verse_id})
                source_row = source_result.fetchone()

                if source_row is None:
                    return []

                source_embedding = source_row[0]
                if source_embedding is None:
                    return []

                # Build similarity query - join verse_embeddings with verses to get text
                if translation_source:
                    similarity_query = text(
                        """
                        SELECT
                            v.verse_id,
                            v.book_name,
                            v.chapter_num,
                            v.verse_num,
                            v.text,
                            v.translation_source,
                            1 - (ve.embedding <-> :source_embedding) AS similarity_score
                        FROM bible.verse_embeddings ve
                        JOIN bible.verses v ON v.verse_id = ve.verse_id
                        WHERE ve.embedding IS NOT NULL
                          AND ve.verse_id != :verse_id
                          AND v.translation_source = :translation_source
                        ORDER BY ve.embedding <-> :source_embedding
                        LIMIT :limit
                        """
                    )
                    params = {
                        "verse_id": verse_id,
                        "source_embedding": source_embedding,
                        "translation_source": translation_source,
                        "limit": limit,
                    }
                else:
                    similarity_query = text(
                        """
                        SELECT
                            v.verse_id,
                            v.book_name,
                            v.chapter_num,
                            v.verse_num,
                            v.text,
                            v.translation_source,
                            1 - (ve.embedding <-> :source_embedding) AS similarity_score
                        FROM bible.verse_embeddings ve
                        JOIN bible.verses v ON v.verse_id = ve.verse_id
                        WHERE ve.embedding IS NOT NULL
                          AND ve.verse_id != :verse_id
                        ORDER BY ve.embedding <-> :source_embedding
                        LIMIT :limit
                        """
                    )
                    params = {
                        "verse_id": verse_id,
                        "source_embedding": source_embedding,
                        "limit": limit,
                    }

                result = conn.execute(similarity_query, params)
                similar_verses = []

                for row in result:
                    similar_verses.append(
                        VerseSimilarityResult(
                            verse_id=row[0],
                            book_name=row[1],
                            chapter_num=row[2],
                            verse_num=row[3],
                            text=row[4],
                            translation_source=row[5],
                            similarity_score=float(row[6]),
                        )
                    )

                return similar_verses
        except (OperationalError, ProgrammingError):
            self._db_status = "unavailable"
            return []

    def find_similar_by_ref(
        self,
        book_name: str,
        chapter_num: int,
        verse_num: int,
        translation_source: str = "KJV",
        limit: int = 10,
    ) -> list[VerseSimilarityResult]:
        """Find similar verses by Bible reference using vector similarity.

        Args:
            book_name: Book name (e.g., "Genesis", "Matthew").
            chapter_num: Chapter number (1-indexed).
            verse_num: Verse number (1-indexed).
            translation_source: Translation identifier (default: "KJV").
            limit: Maximum number of results to return (default: 10).

        Returns:
            List of VerseSimilarityResult objects, ordered by similarity (highest first).
            Empty list if verse not found, no similar verses, or DB unavailable.
        """
        if not self._ensure_engine():
            return []

        try:
            # First, get the source verse's verse_id and embedding from verse_embeddings (1024-dim)
            # Need to join with verses to get verse_id from book/chapter/verse
            source_query = text(
                """
                SELECT v.verse_id, ve.embedding
                FROM bible.verses v
                JOIN bible.verse_embeddings ve ON ve.verse_id = v.verse_id
                WHERE v.book_name = :book_name
                  AND v.chapter_num = :chapter_num
                  AND v.verse_num = :verse_num
                  AND v.translation_source = :translation_source
                  AND ve.embedding IS NOT NULL
                LIMIT 1
                """
            )

            with self._engine.connect() as conn:
                source_result = conn.execute(
                    source_query,
                    {
                        "book_name": book_name,
                        "chapter_num": chapter_num,
                        "verse_num": verse_num,
                        "translation_source": translation_source,
                    },
                )
                source_row = source_result.fetchone()

                if source_row is None:
                    return []

                source_verse_id = source_row[0]
                source_embedding = source_row[1]
                if source_embedding is None:
                    return []

                # Find similar verses - join verse_embeddings with verses to get text
                similarity_query = text(
                    """
                    SELECT
                        v.verse_id,
                        v.book_name,
                        v.chapter_num,
                        v.verse_num,
                        v.text,
                        v.translation_source,
                        1 - (ve.embedding <-> :source_embedding) AS similarity_score
                    FROM bible.verse_embeddings ve
                    JOIN bible.verses v ON v.verse_id = ve.verse_id
                    WHERE ve.embedding IS NOT NULL
                      AND ve.verse_id != :verse_id
                    ORDER BY ve.embedding <-> :source_embedding
                    LIMIT :limit
                    """
                )

                result = conn.execute(
                    similarity_query,
                    {
                        "verse_id": source_verse_id,
                        "source_embedding": source_embedding,
                        "limit": limit,
                    },
                )

                similar_verses = []
                for row in result:
                    similar_verses.append(
                        VerseSimilarityResult(
                            verse_id=row[0],
                            book_name=row[1],
                            chapter_num=row[2],
                            verse_num=row[3],
                            text=row[4],
                            translation_source=row[5],
                            similarity_score=float(row[6]),
                        )
                    )

                return similar_verses
        except (OperationalError, ProgrammingError):
            self._db_status = "unavailable"
            return []

    def find_similar_by_embedding(
        self,
        query_embedding: list[float],
        limit: int = 10,
        translation_source: str | None = None,
    ) -> list[VerseSimilarityResult]:
        """Find similar verses by query embedding using vector similarity.

        Args:
            query_embedding: Query embedding vector (1024-dim from BGE-M3).
            limit: Maximum number of results to return (default: 10).
            translation_source: Optional translation filter (e.g., "KJV").

        Returns:
            List of VerseSimilarityResult objects, ordered by similarity (highest first).
            Empty list if DB unavailable.
        """
        if not self._ensure_engine():
            return []

        try:
            # Convert embedding to pgvector format (string representation)
            embedding_str = f"[{','.join(map(str, query_embedding))}]"

            if translation_source:
                # Format embedding directly in SQL to avoid parameter binding issues with ::vector
                similarity_query = text(
                    f"""
                    SELECT
                        v.verse_id,
                        v.book_name,
                        v.chapter_num,
                        v.verse_num,
                        v.text,
                        v.translation_source,
                        1 - (ve.embedding <-> '{embedding_str}'::vector) AS similarity_score
                    FROM bible.verses v
                    JOIN bible.verse_embeddings ve ON v.verse_id = ve.verse_id
                    WHERE ve.embedding IS NOT NULL
                      AND v.translation_source = :translation_source
                    ORDER BY ve.embedding <-> '{embedding_str}'::vector
                    LIMIT :limit
                    """
                )
                params = {
                    "translation_source": translation_source,
                    "limit": limit,
                }
            else:
                similarity_query = text(
                    f"""
                    SELECT
                        v.verse_id,
                        v.book_name,
                        v.chapter_num,
                        v.verse_num,
                        v.text,
                        v.translation_source,
                        1 - (ve.embedding <-> '{embedding_str}'::vector) AS similarity_score
                    FROM bible.verses v
                    JOIN bible.verse_embeddings ve ON v.verse_id = ve.verse_id
                    WHERE ve.embedding IS NOT NULL
                    ORDER BY ve.embedding <-> '{embedding_str}'::vector
                    LIMIT :limit
                    """
                )
                params = {
                    "limit": limit,
                }

            with self._engine.connect() as conn:
                result = conn.execute(similarity_query, params)
                similar_verses = []

                for row in result:
                    similar_verses.append(
                        VerseSimilarityResult(
                            verse_id=row[0],
                            book_name=row[1],
                            chapter_num=row[2],
                            verse_num=row[3],
                            text=row[4],
                            translation_source=row[5],
                            similarity_score=float(row[6]),
                        )
                    )

                return similar_verses
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
