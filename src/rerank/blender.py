from __future__ import annotations
import os
import math
from typing import Dict, Any

# Blend weight: fixed 0.5 for now per spec
BLEND_W = float(os.getenv("EDGE_RERANK_BLEND_W", "0.5"))

def _fallback_rerank(cosine: float, meta: Dict[str, Any] | None = None) -> float:
    """
    Deterministic rerank fallback for CI/offline runs:
    - Monotonic in cosine but slightly reshaped to avoid trivially equal to cosine.
    """
    # Smoothstep-like shaping in [0,1]
    x = max(0.0, min(1.0, cosine))
    return (3 * (x**2) - 2 * (x**3))

def compute_rerank(source_text: str, target_text: str, cosine: float, meta: Dict[str, Any] | None = None) -> float:
    """
    Hook point for a real reranker (e.g., local LM Studio endpoint) with CI-safe fallback.
    CI must not make outbound calls; use MOCK_AI=1 to force fallback.
    """
    if os.getenv("MOCK_AI", "1") == "1":
        return _fallback_rerank(cosine, meta)
    # If you later wire a real model, guard with timeouts & no-internet CI policy.
    return _fallback_rerank(cosine, meta)  # current behavior: same as fallback

def blend_strength(cosine: float, rerank: float) -> float:
    # Edge strength = 0.5*cos + 0.5*rerank (BLEND_W governs but default=0.5)
    w = BLEND_W
    return (1.0 - w) * float(cosine) + w * float(rerank)

def classify_strength(strength: float) -> str:
    if strength >= 0.90:
        return "strong"
    if strength >= 0.75:
        return "weak"
    return "other"
