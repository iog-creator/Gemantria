"""HINT-mode span helpers for lightweight instrumentation."""
from __future__ import annotations

import os
import uuid
from contextlib import contextmanager
from datetime import datetime

try:
    from scripts.observability.otel import _write_jsonl
except ImportError:
    _write_jsonl = None


@contextmanager
def span_llm(agent: str = "unknown", model: str = "unknown", prompt_len: int = 0):
    """Context manager for LLM call spans."""
    span = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "service": "gemantria",
        "name": "llm.call",
        "attrs": {"agent": agent, "model": model, "prompt_len": prompt_len},
        "dur_ms": 0.0,
        "trace_id": None,
        "span_id": str(uuid.uuid4()),
        "run_id": os.environ.get("PIPELINE_RUN_ID", "local-" + datetime.utcnow().strftime("%Y%m%d%H%M%S")),
    }
    t0 = datetime.utcnow()
    try:
        yield span
    finally:
        dur_ms = (datetime.utcnow() - t0).total_seconds() * 1000
        span["dur_ms"] = round(dur_ms, 3)
        try:
            path = os.environ.get("OTEL_JSONL", "evidence/otel.spans.jsonl")
            if _write_jsonl:
                _write_jsonl(span)
            else:
                import json
                with open(path, "a") as fh:
                    fh.write(json.dumps(span) + "\n")
        except Exception:
            pass


@contextmanager
def span_tool(name: str = "tool.call", **attrs):
    """Context manager for tool call spans."""
    span = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "service": "gemantria",
        "name": name,
        "attrs": attrs,
        "dur_ms": 0.0,
        "trace_id": None,
        "span_id": str(uuid.uuid4()),
        "run_id": os.environ.get("PIPELINE_RUN_ID", "local-" + datetime.utcnow().strftime("%Y%m%d%H%M%S")),
    }
    t0 = datetime.utcnow()
    try:
        yield span
    finally:
        dur_ms = (datetime.utcnow() - t0).total_seconds() * 1000
        span["dur_ms"] = round(dur_ms, 3)
        try:
            path = os.environ.get("OTEL_JSONL", "evidence/otel.spans.jsonl")
            if _write_jsonl:
                _write_jsonl(span)
            else:
                import json
                with open(path, "a") as fh:
                    fh.write(json.dumps(span) + "\n")
        except Exception:
            pass
