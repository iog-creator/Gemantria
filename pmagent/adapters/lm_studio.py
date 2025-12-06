#!/usr/bin/env python3
"""
LM Studio Adapter

Phase-3C P0: LM Studio HTTP client adapter with hermetic lm_off behavior.
Phase-7D: Aligned with canonical model loader (get_lm_model_config()).
"""

from __future__ import annotations

from typing import Any, Literal

import requests
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout

from scripts.config.env import (
    get_lm_model_config,
    get_lm_studio_enabled,
    get_lm_studio_settings,
    openai_cfg,
)

# Phase-7E: Import Ollama adapter for provider routing
try:
    from pmagent.adapters import ollama as ollama_adapter
except ImportError:
    ollama_adapter = None

# Phase-7F: Import Theology adapter for theology slot
try:
    from pmagent.adapters import theology as theology_adapter
except ImportError:
    theology_adapter = None

ModelSlot = Literal["theology", "local_agent", "math", None]


def lm_studio_chat(
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.0,
    max_tokens: int = 512,
    timeout: float = 30.0,
    model_slot: ModelSlot = None,
) -> dict[str, Any]:
    """
    Call LM Studio if configured, otherwise return a hermetic lm_off payload.

    Phase-7D: Uses canonical model loader (get_lm_model_config()) for model selection.
    Supports model slots: "theology", "local_agent", "math", or None (legacy fallback).

    Args:
        messages: List of message dicts with "role" and "content" keys.
        temperature: Sampling temperature (default: 0.0).
        max_tokens: Maximum tokens to generate (default: 512).
        timeout: Request timeout in seconds (default: 30.0).
        model_slot: Model slot to use ("theology", "local_agent", "math", or None for legacy).

    Returns:
        Dictionary with:
        - ok: bool (True if call succeeded)
        - mode: "lm_on" | "lm_off"
        - reason: str | None (error reason if mode is lm_off)
        - response: dict | None (LM Studio API response if ok)
    """
    # Phase-7D: Check if LM Studio is enabled
    if not get_lm_studio_enabled():
        return {
            "ok": False,
            "mode": "lm_off",
            "reason": "lm_studio_disabled",
            "response": None,
        }

    # Phase-7D: Use canonical model config
    model_config = get_lm_model_config()
    base_url = model_config.get("base_url")
    if not base_url:
        return {
            "ok": False,
            "mode": "lm_off",
            "reason": "lm_studio_base_url_not_configured",
            "response": None,
        }

    # Phase-7D: Select model based on slot
    model = None
    if model_slot == "theology":
        model = model_config.get("theology_model")
    elif model_slot == "local_agent":
        model = model_config.get("local_agent_model")
    elif model_slot == "math":
        model = model_config.get("math_model")
    else:
        # Legacy fallback: try get_lm_studio_settings() for backward compatibility
        legacy_settings = get_lm_studio_settings()
        model = legacy_settings.get("model")

    if not model:
        return {
            "ok": False,
            "mode": "lm_off",
            "reason": f"lm_studio_model_not_configured (slot={model_slot})",
            "response": None,
        }

    # Get API key from openai_cfg() (Phase-7D alignment)
    openai_config = openai_cfg()
    api_key = openai_config.get("api_key")

    try:
        base_url = base_url.rstrip("/")
        if not base_url.endswith("/v1"):
            base_url = f"{base_url}/v1"

        url = f"{base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        resp = requests.post(
            url,
            json=payload,
            headers=headers if headers else None,
            timeout=timeout,
        )
        resp.raise_for_status()

        return {
            "ok": True,
            "mode": "lm_on",
            "reason": None,
            "response": resp.json(),
        }

    except ConnectionError as e:
        return {
            "ok": False,
            "mode": "lm_off",
            "reason": f"connection_error: {e}",
            "response": None,
        }
    except Timeout as e:
        return {
            "ok": False,
            "mode": "lm_off",
            "reason": f"timeout: {e}",
            "response": None,
        }
    except HTTPError as e:
        return {
            "ok": False,
            "mode": "lm_off",
            "reason": f"http_error: {e.response.status_code if e.response else 'unknown'}",
            "response": None,
        }
    except RequestException as e:
        return {
            "ok": False,
            "mode": "lm_off",
            "reason": f"request_error: {e}",
            "response": None,
        }
    except Exception as e:  # noqa: BLE001
        return {
            "ok": False,
            "mode": "lm_off",
            "reason": f"unexpected_error: {e}",
            "response": None,
        }


def chat(
    prompt: str,
    model: str | None = None,
    *,
    model_slot: ModelSlot = None,
    system: str | None = None,
) -> str:
    """Provider-aware chat helper.

    Routes to appropriate adapter based on per-slot provider configuration.
    - Theology slot → theology adapter (supports both providers)
    - Per-slot provider → ollama or lmstudio adapter
    - Falls back to default provider if slot provider not configured

    Args:
        prompt: User prompt text.
        model: Explicit model name (optional).
        model_slot: Model slot ("theology", "local_agent", "math", or None).
        system: System prompt (optional).

    Returns:
        Response text string.

    Raises:
        RuntimeError: If adapter not available or model not configured.
    """
    cfg = get_lm_model_config()

    # Determine provider for this slot
    if model_slot == "theology":
        slot_provider = cfg.get("theology_provider", "lmstudio")
    elif model_slot == "local_agent":
        slot_provider = cfg.get("local_agent_provider") or cfg.get("provider", "lmstudio")
    elif model_slot == "math":
        slot_provider = cfg.get("provider", "lmstudio")  # Math uses default provider
    else:
        slot_provider = cfg.get("provider", "lmstudio")

    slot_provider = slot_provider.strip()

    # Route theology slot to theology adapter (supports both providers)
    if model_slot == "theology":
        if theology_adapter is None:
            raise RuntimeError("Theology adapter not available (import failed)")
        return theology_adapter.chat(prompt, system=system, model=model)

    # Route to Ollama if slot provider is ollama and enabled
    if slot_provider == "ollama":
        if not cfg.get("ollama_enabled", True):
            raise RuntimeError("Ollama is disabled (OLLAMA_ENABLED=false)")
        if ollama_adapter is None:
            raise RuntimeError("Ollama adapter not available (import failed)")
        return ollama_adapter.chat(prompt, model=model, model_slot=model_slot, system=system)

    # Route to LM Studio (default for lmstudio provider)
    if not cfg.get("lm_studio_enabled", True):
        raise RuntimeError("LM Studio is disabled (LM_STUDIO_ENABLED=false)")

    # LM Studio / OpenAI-style chat path
    # Convert prompt to messages format
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    # Call lm_studio_chat
    result = lm_studio_chat(
        messages=messages,
        model_slot=model_slot,
        temperature=0.0,
        max_tokens=512,
    )

    if not result.get("ok"):
        raise RuntimeError(f"LM Studio chat failed: {result.get('reason', 'unknown')}")

    # Extract response text from OpenAI-compatible format
    response = result.get("response", {})
    choices = response.get("choices", [])
    if choices:
        message = choices[0].get("message", {})
        return message.get("content", "")
    raise RuntimeError("LM Studio response missing content")


def embed(texts: str | list[str], *, model_slot: str | None = None) -> list[list[float]]:
    """Provider-aware embedding helper.

    Routes to appropriate adapter based on embedding_provider configuration.

    Args:
        texts: Single text string or list of text strings.
        model_slot: Model slot name (defaults to "embedding" for Ollama, ignored for LM Studio).

    Returns:
        List of embedding vectors (each is a list of floats).

    Raises:
        RuntimeError: If provider adapter not available or model not configured.
    """
    cfg = get_lm_model_config()
    provider = cfg.get("embedding_provider") or cfg.get("provider", "lmstudio")
    provider = provider.strip()

    if provider == "ollama":
        if not cfg.get("ollama_enabled", True):
            raise RuntimeError("Ollama is disabled (OLLAMA_ENABLED=false)")
        if ollama_adapter is None:
            raise RuntimeError("Ollama adapter not available (import failed)")
        # Ollama adapter uses model_slot internally via config
        return ollama_adapter.embed(texts)

    # LM Studio / OpenAI-style embedding path
    if not cfg.get("lm_studio_enabled", True):
        raise RuntimeError("LM Studio is disabled (LM_STUDIO_ENABLED=false)")

    import requests

    base_url = cfg.get("base_url", "http://127.0.0.1:9994/v1")
    model = cfg.get("embedding_model")
    if not model:
        raise RuntimeError("No EMBEDDING_MODEL configured")

    openai_config = openai_cfg()
    api_key = openai_config.get("api_key")

    # Normalize texts to list
    text_list = [texts] if isinstance(texts, str) else texts

    # Call embeddings endpoint for each text (simple loop, can batch later)
    embeddings = []
    base_url = base_url.rstrip("/")
    if not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"

    url = f"{base_url}/embeddings"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    for text in text_list:
        payload = {"model": model, "input": text}
        resp = requests.post(url, json=payload, headers=headers, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
        embedding_vec = data.get("data", [{}])[0].get("embedding", [])
        embeddings.append(embedding_vec)

    return embeddings


def rerank(
    query: str, docs: list[str], model: str | None = None, *, model_slot: str | None = None
) -> list[tuple[str, float]]:
    """Provider-aware reranker helper.

    Routes to appropriate adapter based on reranker_provider configuration.

    Args:
        query: Search query string
        docs: List of candidate document texts
        model: Explicit model name (optional)
        model_slot: Model slot (defaults to "reranker")

    Returns:
        List of (document, score) tuples, sorted by score (highest first)

    Raises:
        RuntimeError: If provider adapter not available or model not configured.
    """
    cfg = get_lm_model_config()
    provider = cfg.get("reranker_provider") or cfg.get("provider", "lmstudio")
    provider = provider.strip()

    if provider == "ollama":
        if not cfg.get("ollama_enabled", True):
            raise RuntimeError("Ollama is disabled (OLLAMA_ENABLED=false)")
        if ollama_adapter is None:
            raise RuntimeError("Ollama adapter not available (import failed)")
        return ollama_adapter.rerank(query, docs, model=model, model_slot=model_slot or "reranker")

    # LM Studio reranker: Return neutral scores (can be enhanced later)
    if not cfg.get("lm_studio_enabled", True):
        raise RuntimeError("LM Studio is disabled (LM_STUDIO_ENABLED=false)")
    scores = [(doc, 0.5) for doc in docs]
    return scores
