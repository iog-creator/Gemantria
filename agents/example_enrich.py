"""
Example instrumentation pattern for OTel spans in agent functions.

This demonstrates how to wrap LLM calls and tool/DB calls with spans
for observability. Replicate this pattern in actual agent implementations.
"""

from __future__ import annotations

from scripts.observability.otel import span_llm, span_tool


def enrich_noun(noun_text: str) -> dict:
    """
    Example enrichment function with OTel instrumentation.

    This shows the pattern:
    1. Wrap LLM calls with span_llm()
    2. Wrap tool/DB calls with span_tool()
    3. Spans are automatically written to evidence/otel.spans.jsonl
    """
    # LLM hop
    with span_llm(agent="enrich_nouns", prompt_len=len(noun_text), model="qwen2.5"):
        llm_out = call_llm(noun_text)  # existing function

    # Tool hop (DB)
    with span_tool("gematria.lookup", noun=noun_text):
        value = lookup_gematria(noun_text)  # existing function

    return {"text": noun_text, "value": value, "llm": llm_out}


def call_llm(text: str) -> str:
    """Placeholder for actual LLM call."""
    return '{"insight": "Example insight", "confidence": 0.95}'


def lookup_gematria(text: str) -> int:
    """Placeholder for actual gematria lookup."""
    return 42
