"""Theology adapter for Christian-Bible-Expert-v2.0-12B model.

Phase-7F: Dedicated adapter for theology model, separate from LM Studio critical path.

This adapter supports two providers:
- theology_lmstudio: Local LM Studio on 127.0.0.1 (no internet)
- ollama: Local Ollama (no internet)

No fallbacks to internet-based providers.
"""

from __future__ import annotations


import requests
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout

from scripts.config.env import get_lm_model_config


def chat(
    prompt: str,
    *,
    system: str | None = None,
    model: str | None = None,
) -> str:
    """Chat with theology model (Christian-Bible-Expert-v2.0-12B).

    Phase-7F: Routes to appropriate provider based on configuration.
    Supports theology_lmstudio (local LM Studio) and ollama (local Ollama).

    Args:
        prompt: User prompt text
        system: System prompt (optional)
        model: Explicit model name (optional, uses THEOLOGY_MODEL from config)

    Returns:
        Response text string

    Raises:
        RuntimeError: If theology model not configured or provider unavailable
    """
    cfg = get_lm_model_config()
    theology_model = model or cfg.get("theology_model")

    if not theology_model:
        raise RuntimeError("No THEOLOGY_MODEL configured")

    provider = cfg.get("theology_provider", "lmstudio").strip()

    if provider == "lmstudio":
        # Check if LM Studio is enabled
        if not cfg.get("lm_studio_enabled", True):
            raise RuntimeError("LM Studio is disabled (LM_STUDIO_ENABLED=false)")

        # Local LM Studio on 127.0.0.1 (no internet)
        base_url = cfg.get("theology_lmstudio_base_url", "http://127.0.0.1:1234")
        api_key = cfg.get("theology_lmstudio_api_key", "changeme")

        # Ensure base_url is localhost/127.0.0.1 (security check)
        if "127.0.0.1" not in base_url and "localhost" not in base_url:
            raise RuntimeError(f"Theology LM Studio base URL must be localhost/127.0.0.1, got {base_url!r}")

        # Build messages
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # Call LM Studio chat/completions endpoint
        clean_base = base_url.rstrip("/")
        if clean_base.endswith("/v1"):
            clean_base = clean_base[:-3]
        url = f"{clean_base}/v1/chat/completions"

        headers = {"Content-Type": "application/json"}
        if api_key and api_key != "changeme":
            headers["Authorization"] = f"Bearer {api_key}"

        payload = {
            "model": theology_model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1024,
        }

        try:
            # Increased timeout to 300s to allow for model loading
            response = requests.post(url, json=payload, headers=headers, timeout=300.0)
            response.raise_for_status()
            data = response.json()

            if "choices" not in data or not data["choices"]:
                raise RuntimeError(f"LM Studio response missing choices: {data!r}")

            content = data["choices"][0].get("message", {}).get("content", "")
            if not content:
                raise RuntimeError(f"LM Studio response missing content: {data!r}")

            return content

        except ConnectionError as e:
            raise RuntimeError(f"Theology LM Studio not reachable at {base_url}: {e!s}") from e
        except (HTTPError, RequestException, Timeout) as e:
            raise RuntimeError(f"Theology LM Studio call failed: {e!s}") from e

    elif provider == "ollama":
        # Check if Ollama is enabled
        if not cfg.get("ollama_enabled", True):
            raise RuntimeError("Ollama is disabled (OLLAMA_ENABLED=false)")

        # Local Ollama (no internet)
        from pmagent.adapters import ollama as ollama_adapter

        return ollama_adapter.chat(
            prompt=prompt,
            model=theology_model,
            model_slot="theology",
            system=system,
        )

    else:
        raise RuntimeError(f"Unsupported theology provider: {provider!r}. Supported providers: lmstudio, ollama")
