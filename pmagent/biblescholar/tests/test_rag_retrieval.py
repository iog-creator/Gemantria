"""Test vectors for Phase 15 Wave-2 RAG retrieval engine.

Test Vectors:
- TV-Phase15-Wave2-01: Basic retrieval with 1024-D embeddings
- TV-Phase15-Wave2-02: Reranker fallback improves ranking
- TV-Phase15-Wave2-03: 5-verse context window expansion
- TV-Phase15-Wave2-04: Cross-language lemma signals present
- TV-Phase15-Wave2-05: Hermetic mode graceful degradation

See: docs/SSOT/PHASE15_WAVE2_SPEC.md
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from pmagent.biblescholar.rag_retrieval import RAGRetriever


class TestRAGRetrieval:
    """Test suite for RAG retrieval engine."""

    @patch("pmagent.biblescholar.rag_retrieval.EmbeddingAdapter")
    @patch("pmagent.biblescholar.rag_retrieval.RerankerAdapter")
    def test_tv_phase15_wave2_01_basic_retrieval(self, mock_reranker_cls, mock_embedding_cls):
        """TV-Phase15-Wave2-01: Basic retrieval with 1024-D embeddings."""
        # Mock embedding adapter
        mock_embedding = MagicMock()
        mock_embedding.compute_query_embedding.return_value = np.random.rand(1024)
        mock_embedding.vector_search.return_value = [
            (12345, 0.92),  # verse_id, similarity_score
            (12346, 0.88),
            (12347, 0.85),
        ]
        mock_embedding_cls.return_value = mock_embedding

        # Mock reranker adapter (hermetic mode - returns original)
        mock_reranker = MagicMock()
        mock_reranker.rerank_chunks.side_effect = lambda chunks, q: chunks
        mock_reranker_cls.return_value = mock_reranker

        retriever = RAGRetriever()
        result = retriever.retrieve_contextual_chunks("test query", top_k=3)

        # Verify results
        assert len(result) == 3
        assert result[0]["verse_id"] == 12345
        assert result[0]["cosine"] == 0.92  # SSOT field name (Rule 045)
        assert "relevance_score" in result[0]

        # Verify embedding adapter was called
        mock_embedding.compute_query_embedding.assert_called_once_with("test query")
        mock_embedding.vector_search.assert_called_once()

    @patch("pmagent.biblescholar.rag_retrieval.EmbeddingAdapter")
    @patch("pmagent.biblescholar.rag_retrieval.RerankerAdapter")
    def test_tv_phase15_wave2_02_reranker_improves_ranking(self, mock_reranker_cls, mock_embedding_cls):
        """TV-Phase15-Wave2-02: Reranker fallback improves ranking."""
        # Mock embedding adapter
        mock_embedding = MagicMock()
        mock_embedding.compute_query_embedding.return_value = np.random.rand(1024)
        mock_embedding.vector_search.return_value = [
            (12345, 0.85),  # Lower embedding score
            (12346, 0.90),  # Higher embedding score
        ]
        mock_embedding_cls.return_value = mock_embedding

        # Mock reranker adapter - reranks to flip order
        def mock_rerank(chunks, query):
            # Add rerank scores that flip the order (Rule 045 field name)
            chunks[0]["rerank_score"] = 0.95  # Boost first chunk
            chunks[1]["rerank_score"] = 0.70  # Lower second chunk

            # Compute edge_strength using Rule 045 (0.5 * cosine + 0.5 * rerank_score)
            for chunk in chunks:
                cosine = chunk.get("cosine", chunk.get("embedding_score", 0.0))
                rerank_score = chunk.get("rerank_score", 0.5)
                chunk["edge_strength"] = 0.5 * cosine + 0.5 * rerank_score

            # Sort by edge_strength (descending)
            return sorted(chunks, key=lambda c: c["edge_strength"], reverse=True)

        mock_reranker = MagicMock()
        mock_reranker.rerank_chunks.side_effect = mock_rerank
        mock_reranker_cls.return_value = mock_reranker

        retriever = RAGRetriever()
        result = retriever.retrieve_contextual_chunks("test query", top_k=2)

        # Verify reranker improved ranking
        assert len(result) == 2
        # First result should have higher edge_strength due to reranking (Rule 045)
        assert "edge_strength" in result[0]
        assert result[0]["edge_strength"] > result[1]["edge_strength"]

        # Verify reranker was called
        mock_reranker.rerank_chunks.assert_called_once()

    @patch("pmagent.biblescholar.rag_retrieval.EmbeddingAdapter")
    @patch("pmagent.biblescholar.rag_retrieval.RerankerAdapter")
    def test_tv_phase15_wave2_03_context_window_expansion(self, mock_reranker_cls, mock_embedding_cls):
        """TV-Phase15-Wave2-03: 5-verse context window expansion."""
        # Mock embedding adapter
        mock_embedding = MagicMock()
        mock_embedding.compute_query_embedding.return_value = np.random.rand(1024)
        mock_embedding.vector_search.return_value = [(12345, 0.92)]
        mock_embedding_cls.return_value = mock_embedding

        # Mock reranker
        mock_reranker = MagicMock()
        mock_reranker.rerank_chunks.side_effect = lambda chunks, q: chunks
        mock_reranker_cls.return_value = mock_reranker

        retriever = RAGRetriever()
        result = retriever.retrieve_contextual_chunks("test query", top_k=1)

        # Verify context window metadata is present
        assert len(result) == 1
        assert "context_window" in result[0]
        # In Wave-2, this is a placeholder (empty list)
        # Full expansion will be implemented in Wave-3
        assert isinstance(result[0]["context_window"], list)

    @patch("pmagent.biblescholar.rag_retrieval.EmbeddingAdapter")
    @patch("pmagent.biblescholar.rag_retrieval.RerankerAdapter")
    def test_tv_phase15_wave2_04_cross_language_signals(self, mock_reranker_cls, mock_embedding_cls):
        """TV-Phase15-Wave2-04: Cross-language lemma signals present."""
        # Mock embedding adapter
        mock_embedding = MagicMock()
        mock_embedding.compute_query_embedding.return_value = np.random.rand(1024)
        mock_embedding.vector_search.return_value = [(12345, 0.92)]
        mock_embedding_cls.return_value = mock_embedding

        # Mock reranker
        mock_reranker = MagicMock()
        mock_reranker.rerank_chunks.side_effect = lambda chunks, q: chunks
        mock_reranker_cls.return_value = mock_reranker

        retriever = RAGRetriever()
        result = retriever.retrieve_contextual_chunks("test query", top_k=1)

        # Verify Phase 14 enrichment metadata is present
        assert len(result) == 1
        assert "enriched_metadata" in result[0]
        assert "greek_words" in result[0]["enriched_metadata"]
        assert "proper_names" in result[0]["enriched_metadata"]
        assert "cross_language_hints" in result[0]["enriched_metadata"]

    def test_tv_phase15_wave2_05_hermetic_mode(self):
        """TV-Phase15-Wave2-05: Hermetic mode graceful degradation."""
        retriever = RAGRetriever()
        # Should not crash when DB/LM is unavailable
        # compute_query_embedding returns None in hermetic mode
        result = retriever.retrieve_contextual_chunks("test query", top_k=5)
        assert isinstance(result, list)
        # Empty list is acceptable in hermetic mode
        assert len(result) == 0

    def test_rag_retriever_validation(self):
        """Test input validation."""
        retriever = RAGRetriever()

        # Empty query should raise ValueError
        with pytest.raises(ValueError, match="Query cannot be empty"):
            retriever.retrieve_contextual_chunks("", top_k=5)

        # top_k < 1 should raise ValueError
        with pytest.raises(ValueError, match="top_k must be >= 1"):
            retriever.retrieve_contextual_chunks("test query", top_k=0)
