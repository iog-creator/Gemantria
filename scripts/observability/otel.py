#!/usr/bin/env python3
"""
OpenTelemetry span helpers for Gemantria pipeline observability.

Provides lightweight tracing with opt-in OTLP export or JSONL fallback.
No network required - all spans are written to evidence/otel.spans.jsonl.

Usage:
    from scripts.observability.otel import span_run, span_llm, span_tool

    with span_run("my-run-id") as ctx:
        with span_llm(agent="enrich_nouns", prompt_len=123, model="qwen2.5"):
            # LLM call here
            pass
        with span_tool("pg.query", sql="SELECT 1", rows=1):
            # Tool/DB call here
            pass
"""

from __future__ import annotations

import contextlib
import datetime
import json
import os
import pathlib
import time
import uuid
from typing import Any, Dict

EVIDENCE_DIR = pathlib.Path("evidence")
EVIDENCE_DIR.mkdir(exist_ok=True)
JSONL_PATH = EVIDENCE_DIR / "otel.spans.jsonl"
ENABLE = os.environ.get("ENABLE_OTEL", "0") == "1"
SERVICE = os.environ.get("OTEL_SERVICE_NAME", "gemantria")
OTLP = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT") or ""
RUN_ID = os.environ.get("PIPELINE_RUN_ID") or datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")

# Optional OTel SDK; if missing or no endpoint, we still emit JSONL spans.
_ot = None
try:
    from opentelemetry import trace as _trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.resources import Resource

    if OTLP:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

    _ot = True
except Exception:
    _ot = None

_TRACER = None


def _setup_tracer():
    global _TRACER
    if not _ot or not OTLP:
        _TRACER = None
        return
    resource = Resource.create({"service.name": SERVICE})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=OTLP)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    _trace.set_tracer_provider(provider)
    _TRACER = _trace.get_tracer("gemantria")


if _ot and OTLP:
    _setup_tracer()


def _now_iso():
    return datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _write_jsonl(rec: Dict[str, Any]):
    rec.setdefault("run_id", RUN_ID)
    with JSONL_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


@contextlib.contextmanager
def span(name: str, **attrs):
    """
    Create a span for timing and observability.

    Use as:
        with span("ai.enrich", node="enrich_nouns"):
            ...

    Produces an OTel span (if configured) and always writes a JSONL record.

    Args:
        name: Span name (e.g., "llm.call", "tool.call")
        **attrs: Additional attributes to attach to the span

    Yields:
        Dictionary with trace_id (if available)
    """
    if not ENABLE:
        # No-op but keep minimal timing evidence (JSONL only)
        t0 = time.perf_counter()
        ts = _now_iso()
        try:
            yield {"trace_id": None, "span_id": None, "run_id": RUN_ID}
        finally:
            dur_ms = round((time.perf_counter() - t0) * 1000, 3)
            _write_jsonl(
                {
                    "ts": ts,
                    "service": SERVICE,
                    "name": name,
                    "attrs": attrs,
                    "dur_ms": dur_ms,
                    "trace_id": None,
                    "span_id": str(uuid.uuid4()),
                }
            )
        return

    t0 = time.perf_counter()
    ts = _now_iso()
    trace_id_hex = None
    span_id_hex = None
    if _TRACER:
        with _TRACER.start_as_current_span(name) as sp:
            try:
                for k, v in attrs.items():
                    try:
                        sp.set_attribute(k, v)
                    except Exception:
                        pass
                ctx = sp.get_span_context()
                trace_id_hex = f"{ctx.trace_id:032x}" if ctx and ctx.trace_id is not None else None
                span_id_hex = f"{ctx.span_id:016x}" if ctx and ctx.span_id is not None else None
                yield {"trace_id": trace_id_hex, "span_id": span_id_hex, "run_id": RUN_ID}
            finally:
                dur_ms = round((time.perf_counter() - t0) * 1000, 3)
                _write_jsonl(
                    {
                        "ts": ts,
                        "service": SERVICE,
                        "name": name,
                        "attrs": attrs,
                        "dur_ms": dur_ms,
                        "trace_id": trace_id_hex,
                        "span_id": span_id_hex,
                    }
                )
    else:
        # Fallback: JSONL-only span
        try:
            sid = str(uuid.uuid4())
            yield {"trace_id": None, "span_id": sid, "run_id": RUN_ID}
        finally:
            dur_ms = round((time.perf_counter() - t0) * 1000, 3)
            _write_jsonl(
                {
                    "ts": ts,
                    "service": SERVICE,
                    "name": name,
                    "attrs": attrs,
                    "dur_ms": dur_ms,
                    "trace_id": None,
                    "span_id": sid,
                }
            )


def span_llm(agent: str, prompt_len: int | None = None, model: str | None = None):
    """
    Create a span for an LLM call.

    Args:
        agent: Agent name (e.g., "enrich_nouns", "score_graph")
        prompt_len: Length of the prompt in characters (optional)
        model: Model name (optional)

    Returns:
        Context manager for the LLM span
    """
    return span("llm.call", agent=agent, model=model or "unknown", prompt_len=prompt_len or -1)


def span_tool(tool: str, **attrs):
    """
    Create a span for a tool/DB call.

    Args:
        tool: Tool name (e.g., "pg.query", "gematria.lookup")
        **attrs: Additional attributes (e.g., sql="SELECT 1", rows=1)

    Returns:
        Context manager for the tool span
    """
    return span("tool.call", tool=tool, **attrs)


def span_run(run_id: str):
    """
    Create a root span for a pipeline run.

    Args:
        run_id: Unique run identifier

    Returns:
        Context manager for the run span
    """
    return span("pipeline.run", run_id=run_id)
