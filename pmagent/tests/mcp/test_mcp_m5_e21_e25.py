"""PLAN-073 M5: Runtime checkpointer integration + Atlas trace links tests (E21-E25)."""

from __future__ import annotations

import json
import pathlib

# pytestmark removed: PLAN-073 M5 implemented
# xfail_reason = "PLAN-073 M5 (runtime checkpointer integration + Atlas trace links) staged; implementation pending."
# pytestmark = pytest.mark.xfail(reason=xfail_reason, strict=False)


def test_e21_runtime_checkpointer_postgres_active():
    """Runtime checkpointer receipt shows postgres active."""
    p = pathlib.Path("share/mcp/runtime_checkpointer.json")
    assert p.exists(), "runtime_checkpointer.json missing"
    data = json.loads(p.read_text())
    assert data.get("active") == "postgres"


def test_e22_runtime_session_trace_id():
    """Session trace includes trace_id."""
    p = pathlib.Path("share/mcp/session_trace.json")
    assert p.exists(), "session_trace.json missing"
    data = json.loads(p.read_text())
    tid = data.get("trace_id")
    assert isinstance(tid, str) and len(tid) >= 8


def test_e23_atlas_trace_link_present():
    """Atlas HTML includes trace link/marker."""
    p = pathlib.Path("share/atlas/index.html")
    assert p.exists(), "atlas index.html missing"
    text = p.read_text(errors="ignore")
    assert "data-trace-id=" in text or "trace-link" in text


def test_e24_fallback_memory_when_not_strict():
    """Fallback to memory when STRICT=0 recorded."""
    p = pathlib.Path("share/mcp/runtime_checkpointer.json")
    assert p.exists(), "runtime_checkpointer.json missing"
    data = json.loads(p.read_text())
    assert data.get("strict") in (True, False)
    # When STRICT=0, active should be memory
    if data.get("strict") is False:
        assert data.get("active") == "memory"


def test_e25_env_mismatch_warn_guard():
    """Environment mismatch warning guard exists."""
    p = pathlib.Path("share/mcp/env_mismatch.warn.json")
    assert p.exists(), "env_mismatch.warn.json missing"
