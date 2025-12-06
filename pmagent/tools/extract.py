#!/usr/bin/env python3
"""
Extract Tools - Extract concepts from text using theology model.
"""

from __future__ import annotations

from typing import Any

from pmagent.adapters.theology import chat as theology_chat


def extract_concepts(text: str, **kwargs: Any) -> dict[str, Any]:
    """Extract concepts from text using theology model.

    Args:
        text: Text to extract concepts from.
        **kwargs: Additional arguments (ignored for now).

    Returns:
        Dict with:
        {
            "ok": bool,
            "concepts": list[dict],  # Each dict has concept details
            "errors": list[str],
        }

    Raises:
        RuntimeError: If theology model service is unavailable or misconfigured (fail-closed).
        ValueError: If text is empty.
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    # Use theology model to extract concepts
    system_prompt = """You are a concept extraction AI. Extract significant concepts from the given text.
Return a JSON array of concepts, each with:
- "name": concept name
- "type": "person", "place", "thing", or "concept"
- "description": brief description
- "relevance": relevance score (0.0-1.0)

Return ONLY valid JSON, no markdown, no explanations."""

    prompt = f"Extract concepts from this text:\n\n{text}"

    # Fail-closed: let RuntimeError propagate if service unavailable
    response = theology_chat(prompt, system=system_prompt)

    # Try to parse JSON from response
    import json

    errors: list[str] = []
    concepts: list[dict[str, Any]] = []

    # Extract JSON from response (handle markdown code blocks)
    response_clean = response.strip()
    if response_clean.startswith("```"):
        # Remove markdown code block markers
        lines = response_clean.split("\n")
        response_clean = "\n".join(lines[1:-1]) if len(lines) > 2 else response_clean
    if response_clean.startswith("```json"):
        lines = response_clean.split("\n")
        response_clean = "\n".join(lines[1:-1]) if len(lines) > 2 else response_clean

    try:
        concepts = json.loads(response_clean)
        if not isinstance(concepts, list):
            concepts = []
            errors.append("Model response was not a JSON array")
    except json.JSONDecodeError as e:
        errors.append(f"Failed to parse JSON from model response: {response[:200]}")
        raise RuntimeError(f"Failed to parse JSON from theology model: {e!s}") from e

    return {"ok": len(errors) == 0, "concepts": concepts, "errors": errors}
