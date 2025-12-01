"""
Tests for Ollama rerank failure modes (404, timeout, connection errors).

Verifies that rerank functions handle HTTP errors, timeouts, and connection failures
gracefully by returning safe fallback results instead of crashing.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

# Calculate ROOT: tests/unit/test_*.py -> tests/ -> repo root
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentpm.adapters.ollama import OllamaAPIError, _rerank_embedding_only, rerank  # noqa: E402


class TestOllamaRerankFailures:
    """Test Ollama rerank failure handling."""

    def test_rerank_http_404_fallback(self):
        """Test that HTTP 404 errors fall back to embedding_only, then equal scores."""
        query = "test query"
        docs = ["doc1", "doc2", "doc3"]
        cfg = {
            "ollama_base_url": "http://127.0.0.1:11434",
            "embedding_model": "test-embedding",
            "reranker_model": "test-reranker",
            "reranker_strategy": "granite_llm",
        }

        with (
            patch("agentpm.adapters.ollama.get_lm_model_config", return_value=cfg),
            patch(
                "agentpm.adapters.ollama._post_json",
                side_effect=OllamaAPIError(
                    "404 Not Found", status_code=404, error_type="http_error"
                ),
            ),
        ):
            # Should fall back to embedding_only, which also fails, so returns equal scores
            result = rerank(query, docs)
            assert len(result) == len(docs)
            # All scores should be 0.5 (fallback)
            assert all(score == 0.5 for _, score in result)

    def test_rerank_http_500_fallback(self):
        """Test that HTTP 500 errors fall back gracefully."""
        query = "test query"
        docs = ["doc1", "doc2"]
        cfg = {
            "ollama_base_url": "http://127.0.0.1:11434",
            "embedding_model": "test-embedding",
            "reranker_model": "test-reranker",
            "reranker_strategy": "granite_llm",
        }

        with (
            patch("agentpm.adapters.ollama.get_lm_model_config", return_value=cfg),
            patch(
                "agentpm.adapters.ollama._post_json",
                side_effect=OllamaAPIError(
                    "500 Internal Server Error", status_code=500, error_type="http_error"
                ),
            ),
        ):
            result = rerank(query, docs)
            assert len(result) == len(docs)
            assert all(score == 0.5 for _, score in result)

    def test_rerank_timeout_fallback(self):
        """Test that timeout errors fall back gracefully."""
        query = "test query"
        docs = ["doc1", "doc2", "doc3"]
        cfg = {
            "ollama_base_url": "http://127.0.0.1:11434",
            "embedding_model": "test-embedding",
            "reranker_model": "test-reranker",
            "reranker_strategy": "granite_llm",
        }

        with (
            patch("agentpm.adapters.ollama.get_lm_model_config", return_value=cfg),
            patch(
                "agentpm.adapters.ollama._post_json",
                side_effect=OllamaAPIError("Connection timed out", error_type="timeout"),
            ),
        ):
            result = rerank(query, docs)
            assert len(result) == len(docs)
            assert all(score == 0.5 for _, score in result)

    def test_rerank_connection_error_fallback(self):
        """Test that connection errors fall back gracefully."""
        query = "test query"
        docs = ["doc1", "doc2"]
        cfg = {
            "ollama_base_url": "http://127.0.0.1:11434",
            "embedding_model": "test-embedding",
            "reranker_model": "test-reranker",
            "reranker_strategy": "granite_llm",
        }

        with (
            patch("agentpm.adapters.ollama.get_lm_model_config", return_value=cfg),
            patch(
                "agentpm.adapters.ollama._post_json",
                side_effect=OllamaAPIError("Connection refused", error_type="connection_error"),
            ),
        ):
            result = rerank(query, docs)
            assert len(result) == len(docs)
            assert all(score == 0.5 for _, score in result)

    def test_rerank_embedding_only_http_error(self):
        """Test that embedding_only strategy handles HTTP errors."""
        query = "test query"
        docs = ["doc1", "doc2"]
        cfg = {
            "ollama_base_url": "http://127.0.0.1:11434",
            "embedding_model": "test-embedding",
            "reranker_strategy": "embedding_only",
        }

        with patch(
            "agentpm.adapters.ollama._post_json",
            side_effect=OllamaAPIError("404 Not Found", status_code=404, error_type="http_error"),
        ):
            result = _rerank_embedding_only(query, docs, None, None, cfg)
            assert len(result) == len(docs)
            assert all(score == 0.5 for _, score in result)

    def test_rerank_embedding_only_partial_failure(self):
        """Test that embedding_only handles partial failures (some docs fail to embed)."""
        query = "test query"
        docs = ["doc1", "doc2", "doc3"]
        cfg = {
            "ollama_base_url": "http://127.0.0.1:11434",
            "embedding_model": "test-embedding",
            "reranker_strategy": "embedding_only",
        }

        # Mock: query embedding succeeds, but only 1 of 3 doc embeddings succeeds
        def mock_post_json(base_url, path, payload):
            if path == "/api/embeddings" and payload.get("prompt") == query:
                return {"embedding": [0.1, 0.2, 0.3]}
            elif path == "/api/embeddings" and payload.get("prompt") == "doc1":
                return {"embedding": [0.4, 0.5, 0.6]}
            else:
                # doc2 and doc3 fail
                raise OllamaAPIError("404 Not Found", status_code=404, error_type="http_error")

        with patch("agentpm.adapters.ollama._post_json", side_effect=mock_post_json):
            result = _rerank_embedding_only(query, docs, None, None, cfg)
            # Should return equal scores due to partial failure
            assert len(result) == len(docs)
            assert all(score == 0.5 for _, score in result)

    def test_rerank_granite_llm_json_parse_fallback(self):
        """Test that granite_llm falls back to embedding_only on JSON parse errors (existing behavior)."""
        query = "test query"
        docs = ["doc1", "doc2"]
        cfg = {
            "ollama_base_url": "http://127.0.0.1:11434",
            "embedding_model": "test-embedding",
            "reranker_model": "test-reranker",
            "reranker_strategy": "granite_llm",
        }

        # Mock: chat succeeds but returns invalid JSON, then embedding_only also fails
        def mock_post_json(base_url, path, payload):
            if path == "/api/chat":
                return {"message": {"content": "invalid json {not valid}"}}
            else:
                raise OllamaAPIError("404 Not Found", status_code=404, error_type="http_error")

        with (
            patch("agentpm.adapters.ollama.get_lm_model_config", return_value=cfg),
            patch("agentpm.adapters.ollama._post_json", side_effect=mock_post_json),
        ):
            result = rerank(query, docs)
            assert len(result) == len(docs)
            assert all(score == 0.5 for _, score in result)

    def test_rerank_no_embedding_model_fallback(self):
        """Test that missing embedding model returns equal scores."""
        query = "test query"
        docs = ["doc1", "doc2"]
        cfg = {
            "ollama_base_url": "http://127.0.0.1:11434",
            "reranker_strategy": "embedding_only",
            # No embedding_model configured
        }

        result = _rerank_embedding_only(query, docs, None, None, cfg)
        assert len(result) == len(docs)
        assert all(score == 0.5 for _, score in result)
