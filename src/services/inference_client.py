from __future__ import annotations

import os
from types import SimpleNamespace

import requests

from src.infra.structured_logger import get_logger

LOG = get_logger("gemantria.inference_client")


class InferenceClient:
    """
    Minimal OpenAI-compatible client selector.

    - INFERENCE_PROVIDER=lmstudio  -> uses OPENAI_BASE_URL (default http://127.0.0.1:1234/v1)
    - INFERENCE_PROVIDER=vllm      -> uses VLLM_BASE_URL   (default http://127.0.0.1:8001/v1)
    """

    def __init__(self, api_key: str | None = None):
        provider = (os.getenv("INFERENCE_PROVIDER") or "lmstudio").lower()
        if provider == "vllm":
            base = os.getenv("VLLM_BASE_URL", "http://127.0.0.1:8001/v1")
        else:
            base = os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:1234/v1")
        self.base_url = base.rstrip("/")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "dummy")
        self._session = requests.Session()
        self._timeout = 60.0
        LOG.info("inference_client_init", provider=provider, base_url=self.base_url)

    def chat_completions(
        self,
        messages_batch: list[list[dict]] | list[dict],
        model: str,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> list[SimpleNamespace]:
        """
        Execute chat completion request(s).

        Args:
            messages_batch: List of message lists (batched) or single message list
            model: Model name to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            List of SimpleNamespace objects with 'text' attribute
        """
        # Handle both batched and single requests
        is_batch = messages_batch and isinstance(messages_batch[0], list)
        if not is_batch:
            # Single request - wrap in list
            messages_batch = [messages_batch]

        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        results = []
        for messages in messages_batch:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }
            if max_tokens is not None:
                payload["max_tokens"] = max_tokens
            else:
                # Default max_tokens for detailed theological analysis
                payload["max_tokens"] = 8192

            try:
                resp = self._session.post(url, headers=headers, json=payload, timeout=self._timeout)
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                results.append(SimpleNamespace(text=content))
            except Exception as e:
                LOG.error("chat_completion_failed", error=str(e), url=url, model=model)
                raise

        # Always return list for compatibility with batched usage
        return results
