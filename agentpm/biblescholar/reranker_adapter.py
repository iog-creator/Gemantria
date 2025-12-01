"""Reranker adapter for Phase 15 Wave-2 RAG engine.

This module provides the mandatory reranking layer (Option B profile)
using Granite Reranker (primary) or BGE Reranker (fallback).

Rationale (from Option B): Research confirms that a robust reranking step
significantly improves Context Precision and drastically lowers the LLM's
Hallucination rate by filtering noise introduced during initial retrieval.

See: docs/SSOT/PHASE15_WAVE2_SPEC.md
"""

from __future__ import annotations

from typing import Any, Literal


class RerankerAdapter:
    """Reranker adapter (non-negotiable per Option B).

    This adapter provides cross-encoder reranking for RAG retrieval.
    Uses Granite Reranker (primary) or BGE Reranker (fallback).

    Attributes:
        _lm_status: Current LM service status (\"available\", \"unavailable\", \"lm_off\").
    """

    def __init__(self) -> None:
        """Initialize reranker adapter (lazy LM initialization)."""
        self._lm_status: Literal["available", "unavailable", "lm_off"] = "lm_off"

    def _ensure_lm(self) -> bool:
        """Ensure LM service is available for reranking.

        Returns:
            True if LM is available, False if LM is off/unavailable.

        Side effects:
            Sets self._lm_status based on LM availability.
        """
        # TODO: Wire up Granite Reranker / BGE Reranker via LM Studio or Ollama
        # For now, assume LM is unavailable (hermetic mode)
        self._lm_status = "lm_off"
        return False

    def _compute_rerank_score(self, chunk: dict[str, Any], query: str) -> float:
        """Compute reranking score for a chunk using cross-encoder.

        Args:
            chunk: Chunk dict with 'text' field
            query: Query string

        Returns:
            Reranking score (0.0-1.0), or 0.5 (neutral) if LM unavailable
        """
        if not self._ensure_lm():
            # Hermetic fallback: return neutral score
            return 0.5

        # TODO: Implement actual reranker call
        # This will use Granite Reranker or BGE Reranker via LM API
        # For now, return neutral score
        return 0.5

    def rerank_chunks(self, chunks: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
        """Rerank chunks by relevance to query.

        Combined score = 0.7 * embedding_score + 0.3 * reranker_score

        Args:
            chunks: Initial chunks from embedding-based retrieval.
                    Each chunk must have 'embedding_score' field.
            query: Original query string

        Returns:
            Reranked chunks with updated reranker_score field,
            sorted by combined score (descending).

        Hermetic behavior:
            If LM unavailable, returns original ranking unchanged.
        """
        if not chunks:
            return []

        # Check LM availability
        if not self._ensure_lm():
            # Hermetic fallback: return original ranking
            return chunks

        # Compute reranker scores for each chunk
        for chunk in chunks:
            reranker_score = self._compute_rerank_score(chunk, query)
            chunk["reranker_score"] = reranker_score

        # Compute combined score for each chunk
        for chunk in chunks:
            embedding_score = chunk.get("embedding_score", 0.0)
            reranker_score = chunk.get("reranker_score", 0.5)

            # Combined score: 0.7 * embedding + 0.3 * reranker
            chunk["combined_score"] = 0.7 * embedding_score + 0.3 * reranker_score

        # Sort by combined score (descending)
        sorted_chunks = sorted(chunks, key=lambda c: c.get("combined_score", 0.0), reverse=True)

        return sorted_chunks

    @property
    def lm_status(self) -> Literal["available", "unavailable", "lm_off"]:
        """Get current LM service status.

        Returns:
            \"available\" if LM is connected and working.
            \"unavailable\" if connection failed.
            \"lm_off\" if LM service not configured.
        """
        self._ensure_lm()  # Update status
        return self._lm_status
