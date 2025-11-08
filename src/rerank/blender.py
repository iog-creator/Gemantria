# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

from __future__ import annotations

import os
from typing import Any

# Blend weight: fixed 0.5 for now per spec
BLEND_W = float(os.getenv("EDGE_RERANK_BLEND_W", "0.5"))


def _fallback_rerank(cosine: float, meta: dict[str, Any] | None = None) -> float:
    """Deterministic CI-safe rerank:
    monotonic in cosine, slightly reshaped to avoid matching cosine exactly.
    """
    # Smoothstep-like shaping in [0,1]
    x = max(0.0, min(1.0, cosine))
    return 3 * (x**2) - 2 * (x**3)


def compute_rerank(
    source_text: str,
    target_text: str,
    cosine: float,
    meta: dict[str, Any] | None = None,
) -> float:
    """Hook for a real reranker (e.g., local LM Studio) with CI-safe fallback.
    CI must not make outbound calls; use MOCK_AI=1 to force fallback.
    """
    if os.getenv("MOCK_AI", "1") == "1":
        return _fallback_rerank(cosine, meta)
    # If you later wire a real model, guard with timeouts & no-internet CI policy.
    return _fallback_rerank(cosine, meta)  # current behavior: fallback


def blend_strength(cosine: float, rerank: float) -> float:
    # Edge strength = 0.5*cos + 0.5*rerank (BLEND_W governs; default=0.5)
    w = BLEND_W
    return (1.0 - w) * float(cosine) + w * float(rerank)


def classify_strength(strength: float) -> str:
    if strength >= 0.90:
        return "strong"
    if strength >= 0.75:
        return "weak"
    return "other"
