"""
Collect nouns node wrapper for pipeline integration.

Related Rules: Rule-039 (Execution Contract), Rule-050 (OPS Contract)
Related ADRs: ADR-032 (Organic AI Discovery)
"""

from typing import Any

from src.nodes.ai_noun_discovery import discover_nouns_for_book
from src.ssot.noun_adapter import adapt_ai_noun
from src.infra.structured_logger import get_logger, log_json

LOG = get_logger("gematria.collect_nouns")


def collect_nouns_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Collect nouns for a book (AI-driven discovery or use provided nouns).

    This node wraps the AI noun discovery process and normalizes nouns using
    the SSOT adapter at the discovery boundary.
    """
    try:
        book = state.get("book") or state.get("book_name", "Genesis")

        # If nouns already provided, use them
        if state.get("nouns"):
            log_json(LOG, 20, "nouns_provided", count=len(state["nouns"]))
            timing_samples = []
        else:
            # Discover nouns via AI
            log_json(LOG, 20, "discovering_nouns", book=book)
            state["nouns"], timing_samples = discover_nouns_for_book(book)

        # Normalize nouns using SSOT adapter at discovery boundary
        state["nouns"] = [adapt_ai_noun(n) for n in state["nouns"]]

        # Log metrics
        if "metrics" not in state:
            state["metrics"] = {}
        state["metrics"]["ai_call_latencies_ms"] = timing_samples

        log_json(LOG, 20, "nouns_collected", count=len(state["nouns"]))
        return state

    except Exception as e:
        log_json(LOG, 40, "collect_nouns_failed", error=str(e), book=state.get("book"))
        raise
