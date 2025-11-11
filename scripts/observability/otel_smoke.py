#!/usr/bin/env python3
"""
Smoke test for OpenTelemetry span helpers.

Verifies that spans are created and written to evidence/otel.spans.jsonl.
"""

from __future__ import annotations

import os
import pathlib

# Set ENABLE_OTEL before importing otel module
os.environ.setdefault("ENABLE_OTEL", "1")

from scripts.observability.otel import span_run, span_llm, span_tool


def main():
    """Run smoke test with sample spans."""
    with span_run("smoke-run") as rctx:
        with span_llm(agent="enrich_nouns", prompt_len=123, model="qwen2.5") as lctx:
            pass
        with span_tool("pg.query", sql="SELECT 1", rows=1):
            pass

    # Verify file was created
    jsonl_path = pathlib.Path("evidence/otel.spans.jsonl")
    if jsonl_path.exists():
        print("OK")
    else:
        print("FAIL: evidence/otel.spans.jsonl not created")
        exit(1)


if __name__ == "__main__":
    main()
