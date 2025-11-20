#!/usr/bin/env python3
"""
Bible Tools - Retrieve Bible passages.
"""

from __future__ import annotations

from typing import Any

from agentpm.biblescholar.passage import get_passage_and_commentary
from agentpm.biblescholar.bible_passage_flow import get_db_status


def retrieve_bible_passages(reference: str, use_lm: bool = True, **kwargs: Any) -> dict[str, Any]:
    """Retrieve Bible passages by reference.

    Args:
        reference: Bible reference string (e.g., "John 3:16-18").
        use_lm: If True, generate theology commentary (fail-closed if unavailable); if False, return fallback.
        **kwargs: Additional arguments (ignored for now).

    Returns:
        Dict with:
        {
            "ok": bool,
            "reference": str,
            "verses": list[dict],
            "commentary": dict,
            "errors": list[str],
        }

    Raises:
        RuntimeError: If database is unavailable or use_lm=True and theology model service is unavailable (fail-closed).
        ValueError: If reference is empty or invalid.
    """
    if not reference or not reference.strip():
        raise ValueError("Reference cannot be empty")

    # Fail-closed: check database availability first
    db_status = get_db_status()
    if db_status != "available":
        raise RuntimeError(f"Bible database unavailable: {db_status}")

    # Fail-closed: let RuntimeError propagate if use_lm=True and service unavailable
    result = get_passage_and_commentary(reference, use_lm=use_lm)

    return {
        "ok": len(result.get("errors", [])) == 0,
        **result,
    }
