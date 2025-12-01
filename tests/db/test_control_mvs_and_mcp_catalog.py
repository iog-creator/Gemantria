"""Test control-plane MVs and MCP catalog evidence scripts (DB-off behavior)."""

import json
from pathlib import Path

import pytest

# Add project root to path
REPO = Path(__file__).resolve().parents[2]


def test_control_mvs_snapshot_evidence_structure():
    """Test that mv_schema.json has correct structure (DB-off validation)."""
    evidence_file = REPO / "share" / "atlas" / "control_plane" / "mv_schema.json"

    # If file doesn't exist, that's OK (DB-off case)
    if not evidence_file.exists():
        pytest.skip("Evidence file not found (DB-off case)")

    # Read and parse JSON
    content = evidence_file.read_text(encoding="utf-8")
    data = json.loads(content)

    # Validate top-level keys
    required_keys = {"schema", "generated_at", "ok", "connection_ok", "materialized_views"}
    assert required_keys.issubset(data.keys()), f"Missing required keys: {required_keys - data.keys()}"

    # Validate schema
    assert data["schema"] == "control"

    # Validate generated_at is ISO format
    assert "T" in data["generated_at"] or "Z" in data["generated_at"]

    # Validate ok and connection_ok are booleans
    assert isinstance(data["ok"], bool)
    assert isinstance(data["connection_ok"], bool)

    # Validate materialized_views is a list
    assert isinstance(data["materialized_views"], list)

    # If DB-off (ok=False or connection_ok=False), error should be present
    if not data["ok"] or not data["connection_ok"]:
        assert "error" in data, "DB-off case should have 'error' field"
        assert isinstance(data["error"], str)
        assert len(data["error"]) > 0

    # If DB-on, validate MV results structure
    if data["ok"] and data["connection_ok"]:
        for mv in data["materialized_views"]:
            assert "name" in mv
            assert "columns" in mv
            assert isinstance(mv["columns"], list)
            for col in mv["columns"]:
                assert "name" in col
                assert "type" in col
                assert "nullable" in col


def test_mcp_catalog_stub_evidence_structure():
    """Test that mcp_catalog_stub.json has correct structure (DB-off validation)."""
    evidence_file = REPO / "evidence" / "mcp_catalog_stub.json"

    # If file doesn't exist, that's OK (DB-off case)
    if not evidence_file.exists():
        pytest.skip("Evidence file not found (DB-off case)")

    # Read and parse JSON
    content = evidence_file.read_text(encoding="utf-8")
    data = json.loads(content)

    # Validate top-level keys
    required_keys = {"schema", "generated_at", "ok", "connection_ok", "tools"}
    assert required_keys.issubset(data.keys()), f"Missing required keys: {required_keys - data.keys()}"

    # Validate schema
    assert data["schema"] == "control"

    # Validate generated_at is ISO format
    assert "T" in data["generated_at"] or "Z" in data["generated_at"]

    # Validate ok and connection_ok are booleans
    assert isinstance(data["ok"], bool)
    assert isinstance(data["connection_ok"], bool)

    # Validate tools is a list
    assert isinstance(data["tools"], list)

    # If DB-off (ok=False or connection_ok=False), error should be present
    if not data["ok"] or not data["connection_ok"]:
        assert "error" in data, "DB-off case should have 'error' field"
        assert isinstance(data["error"], str)
        assert len(data["error"]) > 0

    # If DB-on, validate tool results structure
    if data["ok"] and data["connection_ok"]:
        for tool in data["tools"]:
            assert "tool_name" in tool
            assert "input_schema_ref" in tool
            assert "output_schema_ref" in tool
            assert "ring" in tool
            assert "read_only" in tool
            assert isinstance(tool["ring"], int)
            assert isinstance(tool["read_only"], bool)
