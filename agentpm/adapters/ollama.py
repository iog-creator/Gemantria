"""Ollama adapter for local Granite and other models.

This module provides minimal chat + embedding helpers around the Ollama HTTP API:

  POST /api/chat
  POST /api/embeddings

It is intentionally narrow: it only supports the features we need for AgentPM.
"""

from __future__ import annotations

import json
import math
from typing import List, Sequence
from urllib.request import Request, urlopen

from scripts.config.env import get_lm_model_config


TextLike = str | Sequence[str]


def _post_json(base_url: str, path: str, payload: dict) -> dict:
    """POST JSON to Ollama and return the parsed response."""
    url = base_url.rstrip("/") + path
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=60) as resp:  # noqa: S310
        raw = resp.read().decode("utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def _get_json(base_url: str, path: str) -> dict:
    """GET JSON from Ollama API."""
    url = base_url.rstrip("/") + path
    req = Request(url, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=10) as resp:  # noqa: S310
        raw = resp.read().decode("utf-8")
        return json.loads(raw)


def list_installed_models(base_url: str | None = None) -> list[str]:
    """List all installed Ollama models."""
    if base_url is None:
        cfg = get_lm_model_config()
        base_url = cfg.get("ollama_base_url", "http://127.0.0.1:11434")
    try:
        data = _get_json(base_url, "/api/tags")
        models = data.get("models", [])
        return [m.get("name", "") for m in models if m.get("name")]
    except Exception:
        return []


def check_model_installed(model_name: str, base_url: str | None = None) -> bool:
    """Check if a specific model is installed."""
    installed = list_installed_models(base_url)
    return any(
        installed_model == model_name or installed_model.startswith(f"{model_name}:") for installed_model in installed
    )


def _resolve_model_from_slot(cfg: dict, model: str | None, model_slot: str | None) -> str:
    """Resolve which model to call based on slot name."""
    if model:
        return model

    slot = (model_slot or "").strip() or "local_agent"
    if slot == "theology":
        return cfg.get("theology_model") or cfg.get("local_agent_model") or ""
    if slot == "math":
        return cfg.get("math_model") or cfg.get("local_agent_model") or ""
    if slot == "embedding":
        return cfg.get("embedding_model") or ""
    # default: local agent
    return cfg.get("local_agent_model") or ""


def embed(texts: TextLike) -> List[List[float]]:
    """Generate embeddings via Ollama's /api/embeddings endpoint.

    NOTE: we currently call the single-text API in a loop for multiple texts.
    This is simple and robust; we can batch later if needed.
    """
    cfg = get_lm_model_config()
    model = cfg.get("embedding_model")
    base_url = cfg.get("ollama_base_url", "http://127.0.0.1:11434")
    if not model:
        raise RuntimeError("No EMBEDDING_MODEL configured for Ollama")

    def _embed_one(text: str) -> List[float]:
        payload = {"model": model, "prompt": text}
        data = _post_json(base_url, "/api/embeddings", payload)
        if "embedding" not in data:
            raise RuntimeError(f"Ollama embeddings response missing 'embedding': {data!r}")
        return data["embedding"]

    if isinstance(texts, str):
        return [_embed_one(texts)]

    out: List[List[float]] = []
    for t in texts:
        out.append(_embed_one(str(t)))
    return out


def chat(
    prompt: str,
    model: str | None = None,
    *,
    model_slot: str | None = None,
    system: str | None = None,
) -> str:
    """Simple chat helper for Ollama /api/chat (non-streaming).

    We send:
      - messages: [system?, user]
      - stream: false  (so we get a single JSON object)
    """
    cfg = get_lm_model_config()
    base_url = cfg.get("ollama_base_url", "http://127.0.0.1:11434")
    resolved_model = _resolve_model_from_slot(cfg, model, model_slot)
    if not resolved_model:
        raise RuntimeError("No LOCAL_AGENT_MODEL / theology model configured for Ollama")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": resolved_model,
        "messages": messages,
        "stream": False,
    }
    data = _post_json(base_url, "/api/chat", payload)
    # For non-streaming responses, Ollama returns a single dict with "message".
    message = data.get("message") or {}
    content = message.get("content")
    if not isinstance(content, str):
        # Fallback: return the whole payload as a string for debugging.
        return json.dumps(data, ensure_ascii=False)
    return content


def rerank(
    query: str, docs: list[str], model: str | None = None, *, model_slot: str | None = None
) -> list[tuple[str, float]]:
    """Rerank documents using Granite-only stack.

    Phase-7F: Supports two strategies:
    - "embedding_only": Uses embedding model to compute similarity scores
    - "granite_llm": Uses Granite LLM to rank documents via structured prompt

    Args:
        query: The search query string
        docs: List of candidate document texts to rerank
        model: Explicit model name (optional)
        model_slot: Model slot name (defaults to "reranker")

    Returns:
        List of (document, score) tuples, sorted by score (highest first).
        Scores are in [0.0, 1.0] range.

    Raises:
        RuntimeError: If reranker model not configured or API call fails
    """
    cfg = get_lm_model_config()
    strategy = cfg.get("reranker_strategy", "embedding_only")

    if strategy == "embedding_only":
        return _rerank_embedding_only(query, docs, model, model_slot, cfg)
    elif strategy == "granite_llm":
        return _rerank_granite_llm(query, docs, model, model_slot, cfg)
    else:
        raise RuntimeError(
            f"Unsupported reranker strategy: {strategy!r}. Supported strategies: embedding_only, granite_llm"
        )


def _rerank_embedding_only(
    query: str, docs: list[str], model: str | None, model_slot: str | None, cfg: dict
) -> list[tuple[str, float]]:
    """Rerank using embedding similarity (Granite embeddings)."""
    base_url = cfg.get("ollama_base_url", "http://127.0.0.1:11434")
    embedding_model = cfg.get("embedding_model")

    if not embedding_model:
        raise RuntimeError("No EMBEDDING_MODEL configured for embedding_only rerank strategy")

    # Embed query
    query_embed_payload = {"model": embedding_model, "prompt": query}
    query_embed_data = _post_json(base_url, "/api/embeddings", query_embed_payload)
    if "embedding" not in query_embed_data:
        raise RuntimeError(f"Query embedding response missing 'embedding': {query_embed_data!r}")
    query_embedding = query_embed_data["embedding"]
    if not isinstance(query_embedding, list) or not query_embedding:
        raise RuntimeError(f"Invalid query embedding format: {type(query_embedding)}")

    # Embed documents
    doc_embeddings: list[list[float]] = []
    for doc in docs:
        doc_embed_payload = {"model": embedding_model, "prompt": doc}
        doc_embed_data = _post_json(base_url, "/api/embeddings", doc_embed_payload)
        if "embedding" not in doc_embed_data:
            raise RuntimeError(f"Doc embedding response missing 'embedding': {doc_embed_data!r}")
        doc_embedding = doc_embed_data["embedding"]
        if not isinstance(doc_embedding, list) or not doc_embedding:
            raise RuntimeError(f"Invalid doc embedding format: {type(doc_embedding)}")
        doc_embeddings.append(doc_embedding)

    # Compute cosine similarity scores
    scores: list[tuple[str, float]] = []
    for doc, doc_emb in zip(docs, doc_embeddings, strict=True):
        # Cosine similarity: dot product / (norm(query) * norm(doc))
        dot_product = sum(
            q * d
            for q, d in zip(query_embedding, doc_emb, strict=True)
            if isinstance(q, (int, float)) and isinstance(d, (int, float))
        )
        query_norm = math.sqrt(sum(x * x for x in query_embedding if isinstance(x, (int, float))))
        doc_norm = math.sqrt(sum(x * x for x in doc_emb if isinstance(x, (int, float))))
        if query_norm > 0 and doc_norm > 0:
            similarity = dot_product / (query_norm * doc_norm)
        else:
            similarity = 0.0
        # Normalize to [0.0, 1.0] (cosine similarity is already in [-1, 1], shift to [0, 1])
        normalized_score = (similarity + 1.0) / 2.0
        scores.append((doc, normalized_score))

    # Sort by score (highest first)
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def _rerank_granite_llm(
    query: str, docs: list[str], model: str | None, model_slot: str | None, cfg: dict
) -> list[tuple[str, float]]:
    """Rerank using Granite LLM with structured prompt."""
    base_url = cfg.get("ollama_base_url", "http://127.0.0.1:11434")
    reranker_model = model or cfg.get("reranker_model") or cfg.get("local_agent_model")

    if not reranker_model:
        raise RuntimeError("No RERANKER_MODEL or LOCAL_AGENT_MODEL configured for granite_llm rerank strategy")

    # Build structured prompt for ranking
    docs_text = "\n".join(f"{i + 1}. {doc}" for i, doc in enumerate(docs))
    system_prompt = "You are a ranking model. Given a query and numbered candidate documents, return a JSON list of objects with 'index' (1-based) and 'score' (0.0 to 1.0) fields, sorted by relevance (highest first)."
    user_prompt = f"""Query: {query}

Candidate documents:
{docs_text}

Return JSON list: [{{"index": 1, "score": 0.95}}, {{"index": 2, "score": 0.75}}, ...]"""

    # Call Granite LLM
    chat_payload = {
        "model": reranker_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.0,
        "format": "json",
    }

    try:
        chat_data = _post_json(base_url, "/api/chat", chat_payload)

        # Handle streaming responses (Ollama returns multiple JSON objects)
        if "raw" in chat_data:
            # Streaming response: accumulate content from all chunks
            raw_lines = chat_data["raw"].strip().split("\n")
            content_parts = []
            for line in raw_lines:
                if not line.strip():
                    continue
                try:
                    chunk = json.loads(line)
                    if "message" in chunk and "content" in chunk["message"]:
                        content_parts.append(chunk["message"]["content"])
                    if chunk.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue
            content = "".join(content_parts)
        elif "message" in chat_data and "content" in chat_data["message"]:
            # Non-streaming response
            content = chat_data["message"]["content"]
        else:
            raise RuntimeError(f"Chat response missing message.content: {chat_data!r}")

        if not isinstance(content, str):
            raise RuntimeError(f"Chat response content is not a string: {type(content)}")

        # Parse JSON response
        try:
            rankings = json.loads(content)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"Failed to parse JSON from Granite LLM response: {e!s}. Content: {content[:200]}"
            ) from e

        # Handle both list and single dict responses
        if isinstance(rankings, dict):
            rankings = [rankings]
        elif not isinstance(rankings, list):
            raise RuntimeError(f"Expected JSON list or dict, got {type(rankings)}: {rankings!r}")

        # Build (doc, score) tuples from rankings
        doc_scores: dict[int, float] = {}
        for item in rankings:
            if not isinstance(item, dict):
                continue
            idx = item.get("index")
            score = item.get("score")
            if isinstance(idx, int) and isinstance(score, (int, float)):
                # Normalize score to [0.0, 1.0]
                normalized_score = max(0.0, min(1.0, float(score)))
                doc_scores[idx] = normalized_score

        # Map indices to documents (1-based to 0-based)
        scores: list[tuple[str, float]] = []
        for i, doc in enumerate(docs):
            score = doc_scores.get(i + 1, 0.0)  # Default to 0.0 if not ranked
            scores.append((doc, score))

        # Sort by score (highest first)
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    except Exception as e:
        raise RuntimeError(f"Granite LLM rerank call failed: {e!s}") from e
