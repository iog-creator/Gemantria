"""PLAN-073 M6: Agent runtime bindings + Atlas deep-links tests (E26-E30)."""

from __future__ import annotations

import json
import pathlib

import pytest

xfail_reason = "PLAN-073 M6 (agent runtime bindings + Atlas deep-links) staged; implementation pending."

pytestmark = pytest.mark.xfail(reason=xfail_reason, strict=False)


# E26: Agent runtime bindings receipt (what is wired where at runtime)
def test_e26_agent_runtime_bindings():
    p = pathlib.Path("share/mcp/agent_runtime.bindings.json")
    assert p.exists(), "agent_runtime.bindings.json missing"
    data = json.loads(p.read_text())
    assert "checkpointer" in data and "catalog" in data


# E27: Atlas node page carries a deep-link/trace marker
def test_e27_atlas_node_trace_link():
    p = pathlib.Path("share/atlas/nodes/0.html")
    assert p.exists(), "atlas node page missing"
    txt = p.read_text(errors="ignore")
    assert ("data-trace-id=" in txt) or ("trace-link" in txt)


# E28: Index → trace deep-link list exists
def test_e28_atlas_trace_list():
    p = pathlib.Path("share/atlas/trace_links.json")
    assert p.exists(), "trace_links.json missing"
    data = json.loads(p.read_text())
    assert isinstance(data.get("links", []), list)


# E29: Envelope→trace mapping for provenance
def test_e29_envelope_trace_map():
    p = pathlib.Path("share/mcp/envelope_trace.map.json")
    assert p.exists(), "envelope_trace.map.json missing"
    data = json.loads(p.read_text())
    assert isinstance(data, dict)


# E30: Link-check guard receipt (does not break CI)
def test_e30_trace_link_guard():
    p = pathlib.Path("share/mcp/trace_link.guard.json")
    assert p.exists(), "trace_link.guard.json missing"
