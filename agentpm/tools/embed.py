#!/usr/bin/env python3
"""
Embed Tools - Generate embeddings for text.
"""

from __future__ import annotations

from typing import Any

from agentpm.adapters.lm_studio import embed as lm_embed


def generate_embeddings(text: str | list[str], **kwargs: Any) -> dict[str, Any]:
    """Generate embeddings for text.

    Args:
        text: Single text string or list of text strings.
        **kwargs: Additional arguments (ignored for now).

    Returns:
        Dict with:
        {
            "ok": bool,
            "embeddings": list[list[float]],  # List of embedding vectors
            "dimension": int,  # Embedding dimension
            "errors": list[str],
        }

    Raises:
        RuntimeError: If embedding service is unavailable or misconfigured (fail-closed).
        ValueError: If text is empty.
    """
    if not text:
        raise ValueError("Text cannot be empty")

    # Fail-closed: let RuntimeError propagate if service unavailable
    embeddings = lm_embed(text, model_slot="embedding")
    dimension = len(embeddings[0]) if embeddings else 0

    return {
        "ok": True,
        "embeddings": embeddings,
        "dimension": dimension,
        "errors": [],
    }
