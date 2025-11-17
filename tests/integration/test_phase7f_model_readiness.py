"""Phase-7F Model Readiness Tests

Tests all four model slots to ensure they're configured and working:
1. LOCAL_AGENT_MODEL (Granite via Ollama)
2. EMBEDDING_MODEL (Granite-278m via Ollama)
3. RERANKER_MODEL (Granite4 acts as reranker)
4. THEOLOGY_MODEL (Christian-Bible-Expert-v2.0-12B via theology_lmstudio or ollama)

All tests are availability-aware and will skip if models/services are not available.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402
import requests  # noqa: E402

from scripts.config.env import get_lm_model_config  # noqa: E402


@pytest.fixture(scope="module")
def model_config():
    """Get model configuration for testing."""
    return get_lm_model_config()


def _ollama_has_model(name: str) -> bool:
    """Check if Ollama has the specified model installed."""
    try:
        from agentpm.adapters.ollama import check_model_installed

        return check_model_installed(name)
    except Exception:
        return False


def _lmstudio_theology_available() -> bool:
    """Check if LM Studio theology endpoint is available."""
    cfg = get_lm_model_config()
    base_url = cfg.get("theology_lmstudio_base_url", "http://127.0.0.1:1234")
    try:
        # Try a simple health check or ping
        url = f"{base_url.rstrip('/')}/v1/models"
        response = requests.get(url, timeout=2.0)
        return response.status_code == 200
    except Exception:
        return False


def _skip_if_model_missing(name: str) -> None:
    """Skip test if Ollama model is not installed."""
    if not _ollama_has_model(name):
        pytest.skip(f"Phase-7F: Ollama model '{name}' not installed; skipping.")


def _skip_if_theology_lmstudio_unavailable() -> None:
    """Skip test if theology provider is lmstudio but not reachable."""
    cfg = get_lm_model_config()
    provider = cfg.get("theology_provider", "lmstudio").strip()
    if provider == "lmstudio":
        if not _lmstudio_theology_available():
            pytest.skip("Phase-7F: LM Studio theology not reachable on localhost; skipping.")


class TestSlot1LocalAgent:
    """Test Slot 1: LOCAL_AGENT_MODEL (Granite via Ollama)"""

    def test_config_has_granite(self, model_config):
        """Verify Granite model is configured."""
        provider = model_config.get("provider", "").strip()
        local_agent = model_config.get("local_agent_model")

        assert provider == "ollama", f"Expected provider=ollama, got {provider}"
        assert local_agent is not None, "LOCAL_AGENT_MODEL not configured"
        assert "granite" in local_agent.lower(), f"Expected Granite model, got {local_agent}"

    def test_granite_chat(self, model_config):
        """Test Granite chat via Ollama adapter."""
        _skip_if_model_missing(model_config.get("local_agent_model", "granite4:tiny-h"))

        from agentpm.adapters.lm_studio import chat

        response = chat(
            "Say: GRANITE-READY",
            model_slot="local_agent",
            system="You are a helpful assistant.",
        )

        assert isinstance(response, str), "Response should be a string"
        assert len(response) > 0, "Response should not be empty"
        # Check if response contains expected text (case-insensitive)
        assert "granite" in response.lower() or "ready" in response.lower(), (
            f"Response should mention GRANITE-READY, got: {response[:100]}"
        )


class TestSlot2Embedding:
    """Test Slot 2: EMBEDDING_MODEL (Granite-278m via Ollama)"""

    def test_config_has_granite_embedding(self, model_config):
        """Verify Granite embedding model is configured."""
        provider = model_config.get("provider", "").strip()
        embedding = model_config.get("embedding_model")

        assert provider == "ollama", f"Expected provider=ollama, got {provider}"
        assert embedding is not None, "EMBEDDING_MODEL not configured"
        assert "granite" in embedding.lower() or "embedding" in embedding.lower(), (
            f"Expected Granite embedding model, got {embedding}"
        )

    def test_granite_embedding(self, model_config):
        """Test Granite embeddings via Ollama adapter."""
        _skip_if_model_missing(model_config.get("embedding_model", "granite-embedding:278m"))

        from agentpm.adapters.lm_studio import embed

        texts = ["hello", "world"]
        embeddings = embed(texts, model_slot="embedding")

        assert isinstance(embeddings, list), "Embeddings should be a list"
        assert len(embeddings) == 2, f"Expected 2 embeddings, got {len(embeddings)}"

        for i, emb_vec in enumerate(embeddings):
            assert isinstance(emb_vec, list), f"Embedding {i} should be a list"
            assert len(emb_vec) > 0, f"Embedding {i} should have dimension > 0"
            assert all(isinstance(x, (int, float)) for x in emb_vec), f"Embedding {i} should contain numbers"


class TestSlot3Reranker:
    """Test Slot 3: RERANKER_MODEL (Granite4 acts as reranker)"""

    def test_config_has_granite_reranker(self, model_config):
        """Verify Granite reranker model is configured."""
        provider = model_config.get("provider", "").strip()
        reranker = model_config.get("reranker_model")
        strategy = model_config.get("reranker_strategy", "embedding_only")

        assert provider == "ollama", f"Expected provider=ollama, got {provider}"
        assert reranker is not None, "RERANKER_MODEL not configured"
        assert "granite" in reranker.lower(), f"Expected Granite reranker model, got {reranker}"
        assert strategy in ("embedding_only", "granite_llm"), (
            f"Expected reranker_strategy in (embedding_only, granite_llm), got {strategy}"
        )

    def test_granite_reranker(self, model_config):
        """Test Granite reranker via Ollama adapter."""
        _skip_if_model_missing(model_config.get("reranker_model", "granite4:tiny-h"))

        from agentpm.adapters.lm_studio import rerank

        query = "Who parted the Red Sea?"
        docs = [
            "Moses led the Israelites out of Egypt and parted the Red Sea.",
            "David was a king of Israel who wrote many psalms.",
            "Paul was an apostle who wrote letters to early churches.",
        ]

        results = rerank(query, docs, model_slot="reranker")

        assert isinstance(results, list), "Results should be a list"
        assert len(results) == len(docs), f"Expected {len(docs)} results, got {len(results)}"

        # Check that results are tuples of (doc, score)
        for result in results:
            assert isinstance(result, tuple), "Each result should be a tuple"
            assert len(result) == 2, "Each result should be (doc, score)"
            doc, score = result
            assert isinstance(doc, str), "Document should be a string"
            assert isinstance(score, (int, float)), "Score should be a number"
            assert 0.0 <= score <= 1.0, f"Score should be in [0.0, 1.0], got {score}"

        # Check that results are sorted by score (highest first)
        scores = [score for _, score in results]
        assert scores == sorted(scores, reverse=True), "Results should be sorted by score (highest first)"

        # Verify reranker strategy is used
        strategy = model_config.get("reranker_strategy", "embedding_only")
        assert strategy in ("embedding_only", "granite_llm"), (
            f"Expected reranker_strategy in (embedding_only, granite_llm), got {strategy}"
        )


class TestSlot4Theology:
    """Test Slot 4: THEOLOGY_MODEL (Christian-Bible-Expert-v2.0-12B via theology_lmstudio or ollama)"""

    def test_config_has_theology_model(self, model_config):
        """Verify theology model is configured."""
        theology = model_config.get("theology_model")
        provider = model_config.get("theology_provider", "theology").strip()

        assert theology is not None, "THEOLOGY_MODEL not configured"
        assert "christian" in theology.lower() or "bible" in theology.lower(), (
            f"Expected Christian/Bible model, got {theology}"
        )
        assert provider in ("lmstudio", "ollama"), f"Expected theology_provider in (lmstudio, ollama), got {provider}"

    def test_theology_chat(self, model_config):
        """Test theology chat via theology adapter."""
        provider = model_config.get("theology_provider", "lmstudio").strip()

        if provider == "lmstudio":
            _skip_if_theology_lmstudio_unavailable()
        elif provider == "ollama":
            _skip_if_model_missing(model_config.get("theology_model", "Christian-Bible-Expert-v2.0-12B"))
        else:
            pytest.skip(f"Phase-7F: theology_provider is '{provider}', not 'lmstudio' or 'ollama'; skipping.")

        from agentpm.adapters.lm_studio import chat

        response = chat(
            "Summarize John 3:16 in one sentence.",
            model_slot="theology",
            system="You are a Christian Bible expert.",
        )

        assert isinstance(response, str), "Response should be a string"
        assert len(response) > 0, "Response should not be empty"

        # Check for theological content (case-insensitive)
        response_lower = response.lower()
        theological_keywords = ["god", "jesus", "christ", "love", "world", "believe", "eternal", "life"]
        assert any(keyword in response_lower for keyword in theological_keywords), (
            f"Response should contain theological content, got: {response[:200]}"
        )


class TestEndToEndPipeline:
    """End-to-end pipeline test using all four slots"""

    def test_all_slots_used(self, model_config):
        """Test that all four slots are used in a mini RAG pipeline."""
        from agentpm.adapters.lm_studio import embed, rerank, chat

        # Skip if required models/services are not available
        _skip_if_model_missing(model_config.get("local_agent_model", "granite4:tiny-h"))
        _skip_if_model_missing(model_config.get("embedding_model", "granite-embedding:278m"))
        _skip_if_model_missing(model_config.get("reranker_model", "granite4:tiny-h"))

        # Step 1: User question
        query = "Who parted the Red Sea?"

        # Step 2: Use Granite embeddings (slot 2) to search corpus
        corpus = [
            "Moses led the Israelites out of Egypt and parted the Red Sea with his staff.",
            "David was a king of Israel who wrote many psalms and defeated Goliath.",
            "Paul was an apostle who wrote letters to early churches about faith.",
        ]

        # Embed query and corpus
        query_embedding = embed([query], model_slot="embedding")[0]
        corpus_embeddings = embed(corpus, model_slot="embedding")

        assert len(query_embedding) > 0, "Query embedding should have dimension > 0"
        assert len(corpus_embeddings) == len(corpus), "Should have embeddings for all corpus docs"

        # Step 3: Use Granite reranker (slot 3) to order passages
        reranked = rerank(query, corpus, model_slot="reranker")

        assert len(reranked) == len(corpus), "Should rerank all documents"
        # Check that Moses document is in top results (may not be exactly first due to LLM non-determinism)
        top_docs = [doc for doc, _ in reranked[:2]]  # Check top 2
        moses_found = any("moses" in doc.lower() or "parted" in doc.lower() for doc in top_docs)
        assert moses_found, f"Moses doc should be in top 2 results, got: {top_docs}"
        top_doc = reranked[0][0]  # Use top doc for next step

        # Step 4: Use Granite (slot 1) for optional reasoning
        reasoning_prompt = f"Given this question: {query}\nAnd this top passage: {top_doc}\nProvide a brief answer."
        granite_response = chat(reasoning_prompt, model_slot="local_agent")

        assert isinstance(granite_response, str), "Granite response should be a string"
        assert len(granite_response) > 0, "Granite response should not be empty"

        # Step 5: Use Christian LLM (slot 4) for final theological answer
        # Skip if theology provider is not available
        provider = model_config.get("theology_provider", "lmstudio").strip()
        if provider == "lmstudio":
            _skip_if_theology_lmstudio_unavailable()
        elif provider == "ollama":
            _skip_if_model_missing(model_config.get("theology_model", "Christian-Bible-Expert-v2.0-12B"))
        else:
            pytest.skip(f"Phase-7F: theology_provider is '{provider}', not 'lmstudio' or 'ollama'; skipping.")

        final_prompt = f"Question: {query}\nContext: {top_doc}\nProvide a theological answer."
        theology_response = chat(final_prompt, model_slot="theology")

        assert isinstance(theology_response, str), "Theology response should be a string"
        assert len(theology_response) > 0, "Theology response should not be empty"

        # Verify theological content
        theology_lower = theology_response.lower()
        theological_keywords = ["moses", "red sea", "israel", "egypt", "god", "miracle"]
        assert any(keyword in theology_lower for keyword in theological_keywords), (
            f"Theology response should mention Moses/Red Sea, got: {theology_response[:200]}"
        )

        # Verify provider configuration
        provider = model_config.get("provider", "").strip()
        assert provider == "ollama", f"Provider should be ollama, got {provider}"
