"""Example instrumented agent: rerank."""

from __future__ import annotations

from scripts.observability.otel_helpers import span_llm


def rerank(query: str, candidates, model: str = "rerank-v1"):
    """Rerank candidates by relevance (instrumented example)."""
    prompt_len = len(query or "")
    with span_llm(agent="rerank", model=model, prompt_len=prompt_len):
        scored = [{"candidate": c, "score": 1.0} for c in candidates]
    return scored


if __name__ == "__main__":
    print(rerank("who is", ["a", "b", "c"]))
