#!/usr/bin/env python3
"""
Vision Adapter for Multimodal Inference.

Handles multimodal inference for vision tasks using Qwen3-VL-4B.
Supports both LM Studio and Ollama providers.
"""

from __future__ import annotations

import base64
from typing import Iterable

import httpx

from scripts.config.env import get_lm_model_config


def _to_data_url(img: str | bytes) -> str:
    """Convert image to data URL format for OpenAI-style API."""
    if isinstance(img, bytes):
        b64 = base64.b64encode(img).decode("ascii")
    else:
        # assume base64 string or path - Cursor can extend
        if img.strip().startswith("data:image"):
            return img
        if "base64," in img:
            return img
        # TODO: add file path loader if needed
        b64 = img
    return f"data:image/png;base64,{b64}"


def vision_chat(
    prompt: str,
    images: Iterable[str | bytes] | None = None,
    *,
    system: str | None = None,
    model: str | None = None,
) -> str:
    """Call vision model (Qwen3-VL-4B) with multimodal prompt.

    Args:
        prompt: Text prompt for the vision task
        images: Iterable of image data (base64 strings or bytes)
        system: Optional system prompt
        model: Optional model override (defaults to VISION_MODEL from config)

    Returns:
        Response text from the vision model

    Raises:
        RuntimeError: If provider is unsupported or API call fails
    """
    cfg = get_lm_model_config()
    model_name = model or cfg.get("vision_model", "qwen3-vl-4b")
    provider = cfg.get("vision_provider", "lmstudio").strip().lower()

    if provider == "lmstudio":
        base_url = cfg.get("lmstudio_base_url", "http://localhost:1234/v1")
        url = f"{base_url}/chat/completions"
    elif provider == "ollama":
        base_url = cfg.get("ollama_base_url", "http://localhost:11434")
        url = f"{base_url}/v1/chat/completions"
    else:
        raise RuntimeError(f"Unsupported VISION_PROVIDER={provider}")

    # Build content array with images and text
    content = []
    if images:
        for img in images:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": _to_data_url(img)},
                }
            )
    content.append({"type": "text", "text": prompt})

    # Build messages array
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": content})

    # Build payload
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.7,
        "top_p": 0.95,
    }

    # Make API call
    with httpx.Client(timeout=120.0) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

    # Extract response (standard OpenAI-style)
    return data["choices"][0]["message"]["content"]
