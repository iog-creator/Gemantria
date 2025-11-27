"""
Vector Store Adapter for Control Plane DMS.

This module provides the interface for storing and retrieving document embeddings
in the control.kb_document table using pgvector.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from agentpm.adapters.lm_studio import embed
from agentpm.db.loader import get_control_engine

logger = logging.getLogger("vector_store")


@dataclass
class SearchResult:
    """A semantic search result."""

    path: str
    title: str | None
    similarity: float
    content_preview: str | None = None


class VectorStore:
    """Adapter for vector operations on control.kb_document."""

    def __init__(self):
        self._engine = get_control_engine()

    def generate_embedding(self, text_content: str) -> list[float] | None:
        """Generate embedding for text using configured provider."""
        try:
            embeddings = embed(text_content)
            if embeddings and len(embeddings) > 0:
                return embeddings[0]
            return None
        except Exception as e:
            logger.warning(f"Failed to generate embedding: {e}")
            return None

    def upsert_embedding(self, path: str, content: str) -> bool:
        """
        Generate and save embedding for a document.

        Args:
            path: Document path (must already exist in kb_document)
            content: Document content to embed

        Returns:
            True if successful, False otherwise.
        """
        embedding = self.generate_embedding(content)
        if not embedding:
            return False

        try:
            # Convert to pgvector string format
            embedding_str = f"[{','.join(map(str, embedding))}]"

            query = text("""
                UPDATE control.kb_document
                SET embedding = CAST(:embedding_str AS vector)
                WHERE path = :path
            """)

            with self._engine.connect() as conn:
                conn.execute(query, {"embedding_str": embedding_str, "path": path})
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update embedding for {path}: {e}")
            return False

    def search(self, query: str, limit: int = 5, threshold: float = 0.10) -> list[SearchResult]:
        """
        Search for documents similar to query.

        Args:
            query: Search query string
            limit: Maximum number of results
            threshold: Minimum similarity score (0-1)

        Returns:
            List of SearchResult objects
        """
        embedding = self.generate_embedding(query)
        if not embedding:
            logger.warning("Could not generate embedding for query")
            return []

        try:
            embedding_str = f"[{','.join(map(str, embedding))}]"

            # First, get count of documents with embeddings
            count_sql = text("""
                SELECT COUNT(*) 
                FROM control.kb_document
                WHERE embedding IS NOT NULL
            """)

            # 1 - cosine distance = cosine similarity
            sql = text(f"""
                SELECT 
                    path,
                    title,
                    1 - (embedding <-> CAST('{embedding_str}' AS vector)) as similarity
                FROM control.kb_document
                WHERE embedding IS NOT NULL
                  AND (1 - (embedding <-> CAST('{embedding_str}' AS vector))) > :threshold
                ORDER BY similarity DESC
                LIMIT :limit
            """)

            results = []
            with self._engine.connect() as conn:
                # Get total count of documents with embeddings
                total_with_embeddings = conn.execute(count_sql).scalar() or 0

                # Get results above threshold
                rows = conn.execute(sql, {"limit": limit, "threshold": threshold})
                for row in rows:
                    results.append(SearchResult(path=row[0], title=row[1], similarity=float(row[2])))

                # If no results, try to get top results below threshold for diagnostics
                if not results and total_with_embeddings > 0:
                    diagnostic_sql = text(f"""
                        SELECT 
                            path,
                            title,
                            1 - (embedding <-> CAST('{embedding_str}' AS vector)) as similarity
                        FROM control.kb_document
                        WHERE embedding IS NOT NULL
                        ORDER BY similarity DESC
                        LIMIT 3
                    """)
                    diag_rows = conn.execute(diagnostic_sql)
                    diag_results = []
                    for row in diag_rows:
                        diag_results.append({"path": row[0], "title": row[1], "similarity": float(row[2])})
                    if diag_results:
                        max_sim = max(r["similarity"] for r in diag_results)
                        logger.info(
                            f"Search found {total_with_embeddings} documents with embeddings, but none above threshold {threshold:.2f}. Max similarity: {max_sim:.3f}"
                        )

            return results
        except (OperationalError, ProgrammingError) as e:
            logger.error(f"Vector search failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            return []
