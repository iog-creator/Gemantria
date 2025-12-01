"""Test control-plane smoke script DB-off behavior."""

import json
from pathlib import Path

import pytest

# Add project root to path
REPO = Path(__file__).resolve().parents[2]


def test_control_plane_smoke_evidence_structure():
    """Test that control_plane_smoke.json has correct structure (DB-off validation)."""
    evidence_file = REPO / "evidence" / "control_plane_smoke.json"

    # If file doesn't exist, that's OK (DB-off case)
    if not evidence_file.exists():
        pytest.skip("Evidence file not found (DB-off case)")

    # Read and parse JSON
    content = evidence_file.read_text(encoding="utf-8")
    data = json.loads(content)

    # Validate top-level keys
    required_keys = {"schema", "generated_at", "ok", "connection_ok", "tables"}
    assert required_keys.issubset(
        data.keys()
    ), f"Missing required keys: {required_keys - data.keys()}"

    # Validate schema
    assert data["schema"] == "control"

    # Validate generated_at is ISO format
    assert "T" in data["generated_at"] or "Z" in data["generated_at"]

    # Validate ok and connection_ok are booleans
    assert isinstance(data["ok"], bool)
    assert isinstance(data["connection_ok"], bool)

    # Validate tables is a list
    assert isinstance(data["tables"], list)

    # If DB-off (ok=False or connection_ok=False), error should be present
    if not data["ok"] or not data["connection_ok"]:
        assert "error" in data, "DB-off case should have 'error' field"
        assert isinstance(data["error"], str)
        assert len(data["error"]) > 0

    # If DB-on, validate table results structure
    if data["ok"] and data["connection_ok"]:
        for table in data["tables"]:
            assert "name" in table
            assert "insert_ok" in table
            assert "select_ok" in table
            assert isinstance(table["insert_ok"], bool)
            assert isinstance(table["select_ok"], bool)
