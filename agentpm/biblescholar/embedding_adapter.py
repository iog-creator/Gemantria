"""Embedding adapter for 1024-D BGE-M3 embeddings via pgvector.

This module provides read-only access to verse embeddings and
query embedding generation for RAG retrieval (Phase 15 Wave-2).

Uses bible.verse_embeddings table with 1024-dimensional vectors.
Follows existing BibleVectorAdapter pattern for DB access and hermetic mode.

See: docs/SSOT/PHASE15_WAVE2_SPEC.md
"""

from __future__ import annotations

from typing import Literal

import numpy as np
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from agentpm.db.loader import DbUnavailableError, get_bible_engine


class EmbeddingAdapter:
    """Adapter for 1024-D embeddings (DB-First, Rule 069).

    This adapter provides read-only access to bible.verse_embeddings
    for RAG retrieval. Uses pgvector for similarity search.

    Attributes:
        _engine: SQLAlchemy engine (lazy-initialized).
        _db_status: Current database status ("available", "unavailable", "db_off").
    """

    def __init__(self) -> None:
        """Initialize embedding adapter (lazy engine initialization)."""
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

    def get_embedding_for_verse(self, verse_id: int) -> np.ndarray | None:
        """Retrieve 1024-D embedding for a verse.

        Args:
            verse_id: Verse identifier from bible.verses

        Returns:
            1024-D numpy array, or None if not found or DB unavailable
        """
        if not self._ensure_engine():
            return None

        try:
            query = text(
                """
                SELECT embedding
                FROM bible.verse_embeddings
                WHERE verse_id = :verse_id
                  AND embedding IS NOT NULL
                LIMIT 1
                """
            )

            with self._engine.connect() as conn:
                result = conn.execute(query, {"verse_id": verse_id})
                row = result.fetchone()

                if row is None or row[0] is None:
                    return None

                # Convert pgvector embedding to numpy array
                return np.array(row[0], dtype=np.float32)
        except (OperationalError, ProgrammingError):
            self._db_status = "unavailable"
            return None

    def compute_query_embedding(self, query: str) -> np.ndarray | None:
        """Generate 1024-D query embedding via BGE-M3.

        Args:
            query: Natural language query string

        Returns:
            1024-D numpy array, or None if generation fails

        Note:
            This is a placeholder for BGE-M3 integration.
            Phase 15 Wave-2 focuses on retrieval; embedding generation
            will be wired in Wave-3 when LM Stack is fully integrated.
        """
        # TODO: Wire up BGE-M3 model for query encoding
        # For now, return None (hermetic mode safe)
        return None

    def vector_search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[tuple[int, float]]:
        """Perform pgvector cosine similarity search.

        Args:
            query_embedding: 1024-D query vector
            top_k: Number of results to return

        Returns:
            List of (verse_id, cosine_similarity) tuples, sorted by similarity desc.
            Empty list if DB unavailable.
        """
        if not self._ensure_engine():
            return []

        try:
            # Convert numpy array to pgvector format (string representation)
            embedding_list = query_embedding.tolist()
            embedding_str = f"[{','.join(map(str, embedding_list))}]"

            # Use pgvector cosine distance operator (<->)
            # Similarity = 1 - distance
            similarity_query = text(
                f"""
                SELECT
                    verse_id,
                    1 - (embedding <-> '{embedding_str}'::vector) AS similarity_score
                FROM bible.verse_embeddings
                WHERE embedding IS NOT NULL
                ORDER BY embedding <-> '{embedding_str}'::vector
                LIMIT :limit
                """
            )

            with self._engine.connect() as conn:
                result = conn.execute(similarity_query, {"limit": top_k})
                matches = []

                for row in result:
                    matches.append((int(row[0]), float(row[1])))

                return matches
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
