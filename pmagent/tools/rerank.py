#!/usr/bin/env python3
"""
Rerank Tools - Rerank passages using SSOT blend formula.
"""

from __future__ import annotations

from typing import Any

from src.rerank.blender import blend_strength, compute_rerank


def rerank_passages(
    query: str, passages: list[str], cosine_scores: list[float] | None = None, **kwargs: Any
) -> dict[str, Any]:
    """Rerank passages using SSOT blend formula.

    Args:
        query: Query text.
        passages: List of passage texts to rerank.
        cosine_scores: Optional pre-computed cosine similarity scores (one per passage).
        **kwargs: Additional arguments (ignored for now).

    Returns:
        Dict with:
        {
            "ok": bool,
            "ranked": list[dict],  # Each dict has: {"passage": str, "cosine": float, "rerank": float, "strength": float, "class": str}
            "errors": list[str],
        }

    Raises:
        ValueError: If query or passages are invalid.
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    if not passages:
        raise ValueError("Passages list cannot be empty")

    # If cosine scores not provided, compute fallback (all 0.5)
    if cosine_scores is None:
        cosine_scores = [0.5] * len(passages)
    elif len(cosine_scores) != len(passages):
        raise ValueError(f"cosine_scores length ({len(cosine_scores)}) != passages length ({len(passages)})")

    ranked: list[dict[str, Any]] = []

    for i, passage in enumerate(passages):
        cosine = cosine_scores[i]
        # Compute rerank score
        rerank = compute_rerank(query, passage, cosine)
        # Blend strength
        strength = blend_strength(cosine, rerank)
        # Classify
        if strength >= 0.90:
            edge_class = "strong"
        elif strength >= 0.75:
            edge_class = "weak"
        else:
            edge_class = "other"

        ranked.append(
            {
                "passage": passage,
                "cosine": cosine,
                "rerank": rerank,
                "strength": strength,
                "class": edge_class,
            }
        )

    # Sort by strength (descending)
    ranked.sort(key=lambda x: x["strength"], reverse=True)

    return {"ok": True, "ranked": ranked, "errors": []}
