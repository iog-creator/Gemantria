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

        Phase 15 Wave-3: Checks real reranker availability.
        LM-off during Wave-3 = LOUD FAIL (RuntimeError).

        Returns:
            True if LM is available, False if LM is off/unavailable.

        Side effects:
            Sets self._lm_status based on LM availability.
        """
        from agentpm.adapters.lm_studio import get_lm_model_config

        cfg = get_lm_model_config()
        provider = cfg.get("reranker_provider") or cfg.get("provider", "lmstudio")
        provider = provider.strip()

        # Check if reranker provider is enabled
        if provider == "ollama":
            if not cfg.get("ollama_enabled", True):
                self._lm_status = "lm_off"
                return False
        else:  # lmstudio
            if not cfg.get("lm_studio_enabled", True):
                self._lm_status = "lm_off"
                return False

        # Check if reranker model is configured
        reranker_model = cfg.get("reranker_model")
        if not reranker_model:
            self._lm_status = "lm_off"
            return False

        # Try a test rerank call to verify service is actually available
        try:
            from agentpm.adapters.lm_studio import rerank

            # Minimal test: rerank with dummy query/doc
            test_result = rerank("test", ["test doc"], model_slot="reranker")
            if test_result is not None:
                self._lm_status = "available"
                return True
            else:
                self._lm_status = "unavailable"
                return False
        except RuntimeError:
            # Service unavailable
            self._lm_status = "unavailable"
            return False

    def _compute_rerank_score(self, chunk: dict[str, Any], query: str) -> float:
        """Compute reranking score for a chunk using cross-encoder.

        Phase 15 Wave-3: Wired to real reranker service.
        LM-off during Wave-3 = LOUD FAIL (RuntimeError).

        Args:
            chunk: Chunk dict with 'text' field (or 'verse_ref' for verse text lookup)
            query: Query string

        Returns:
            Reranking score (0.0-1.0)

        Raises:
            RuntimeError: If LM service is unavailable (Wave-3 requires LM).
        """
        if not self._ensure_lm():
            # Wave-3: LM-off = LOUD FAIL
            raise RuntimeError(
                "LOUD FAIL: Reranker service unavailable. Wave-3 requires LM to be available for reranking."
            )

        from agentpm.adapters.lm_studio import rerank

        # Extract text from chunk
        chunk_text = chunk.get("text")
        if not chunk_text:
            # Fallback: try to get verse text from verse_ref
            verse_ref = chunk.get("verse_ref")
            if verse_ref:
                # For now, use verse_ref as text (can enhance later with verse lookup)
                chunk_text = verse_ref
            else:
                # No text available, return neutral score
                return 0.5

        try:
            # Call reranker with query and chunk text
            # rerank() returns list[tuple[doc, score]] for each doc
            results = rerank(query, [chunk_text], model_slot="reranker")
            if not results or len(results) == 0:
                return 0.5

            # Extract score from first (doc, score) tuple
            _, score = results[0]
            # Clamp to [0.0, 1.0] if needed
            return max(0.0, min(1.0, float(score)))
        except RuntimeError as e:
            # Wave-3: LM-off = LOUD FAIL
            raise RuntimeError(
                f"LOUD FAIL: Reranker service error during score computation. "
                f"Wave-3 requires LM to be available. Error: {e!s}"
            ) from e

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
