"""RAG Retrieval Engine for Phase 15 Wave-2 (Option B profile).

This module implements the Advanced RAG retrieval engine with:
- 1024-D embedding-based relevance scoring (pgvector)
- Reranker fallback layer (mandatory per Option B)
- 5-verse context window expansion
- Phase 14 RelationshipAdapter integration

See: docs/SSOT/PHASE15_WAVE2_SPEC.md
"""

from __future__ import annotations

from typing import Any

# from pmagent.biblescholar.contextual_chunks import expand_context_window  # Wave-3
from pmagent.biblescholar.embedding_adapter import EmbeddingAdapter
from pmagent.biblescholar.reranker_adapter import RerankerAdapter


class RAGRetriever:
    """Main RAG retrieval orchestrator (Option B profile).

    This retriever combines:
    - 1024-D embedding-based vector search (pgvector)
    - Cross-encoder reranking (Granite/BGE)
    - 5-verse context window expansion
    - Phase 14 enriched metadata (Greek words, proper names, cross-language hints)

    Hermetic behavior:
        - DB unavailable: Returns empty list
        - LM unavailable: Uses embedding scores only (no reranking)
    """

    def __init__(self) -> None:
        """Initialize RAG retriever with embedding and reranker adapters."""
        self.embedding_adapter = EmbeddingAdapter()
        self.reranker_adapter = RerankerAdapter()

    def retrieve_contextual_chunks(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Retrieve and rank contextual chunks for a query.

        Args:
            query: Natural language query string
            top_k: Number of chunks to retrieve (default: 5)

        Returns:
            List of ranked chunks matching rag_retrieval.schema.json

        Raises:
            ValueError: If query is empty or top_k < 1
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        if top_k < 1:
            raise ValueError("top_k must be >= 1")

        # Step 1: Compute query embedding (1024-D)
        query_embedding = self.embedding_adapter.compute_query_embedding(query)
        if query_embedding is None:
            # Hermetic fallback: LM unavailable for query embedding
            return []

        # Step 2: Vector search via pgvector
        search_results = self.embedding_adapter.vector_search(query_embedding, top_k=top_k)
        if not search_results:
            # Hermetic fallback: DB unavailable or no results
            return []

        # Step 3: Build initial chunks with cosine similarity scores
        chunks = []
        for verse_id, similarity_score in search_results:
            chunk = {
                "verse_id": verse_id,
                "cosine": similarity_score,  # SSOT field name (Rule 045)
                "relevance_score": similarity_score,  # Will be updated after reranking
            }
            chunks.append(chunk)

        # Step 4: Apply reranker (Rule 045 blend)
        # Reranker will update chunks with rerank_score and edge_strength
        chunks = self.reranker_adapter.rerank_chunks(chunks, query)

        # Update relevance_score to edge_strength (Rule 045 blend result)
        for chunk in chunks:
            if "edge_strength" in chunk:
                chunk["relevance_score"] = chunk["edge_strength"]

        # Step 5: Expand context windows (5-verse)
        # For Phase 15 Wave-2, we'll add context_window metadata
        # Full context expansion will be implemented in Wave-3
        for chunk in chunks:
            verse_id = chunk["verse_id"]
            # TODO: Convert verse_id to verse_ref for context expansion
            # For now, just add placeholder context_window field
            chunk["context_window"] = []

        # Step 6: Enrich with Phase 14 metadata
        # This will be fully wired in Component 5 (Phase 14 adapter integration)
        for chunk in chunks:
            chunk["enriched_metadata"] = {
                "greek_words": [],
                "proper_names": [],
                "cross_language_hints": [],
            }

        return chunks[:top_k]  # Return top_k chunks
