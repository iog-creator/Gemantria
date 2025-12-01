"""Test control-plane compliance exports DB-off behavior."""

import json
from pathlib import Path

import pytest

# Add project root to path
REPO = Path(__file__).resolve().parents[2]


def test_compliance_head_evidence_structure():
    """Test that compliance.head.json has correct structure (DB-off validation)."""
    evidence_file = REPO / "share" / "atlas" / "control_plane" / "compliance.head.json"

    # If file doesn't exist, that's OK (DB-off case)
    if not evidence_file.exists():
        pytest.skip("Evidence file not found (DB-off case)")

    # Read and parse JSON
    content = evidence_file.read_text(encoding="utf-8")
    data = json.loads(content)

    # Validate top-level keys
    required_keys = {"schema", "generated_at", "ok", "connection_ok", "summary"}
    assert required_keys.issubset(data.keys()), f"Missing required keys: {required_keys - data.keys()}"

    # Validate schema
    assert data["schema"] == "control"

    # Validate generated_at is ISO format
    assert "T" in data["generated_at"] or "Z" in data["generated_at"]

    # Validate ok and connection_ok are booleans
    assert isinstance(data["ok"], bool)
    assert isinstance(data["connection_ok"], bool)

    # Validate summary (may be None in DB-off case)
    assert data["summary"] is None or isinstance(data["summary"], dict)

    # If DB-off (ok=False or connection_ok=False), error should be present
    if not data["ok"] or not data["connection_ok"]:
        assert "error" in data, "DB-off case should have 'error' field"
        assert isinstance(data["error"], str)
        assert len(data["error"]) > 0

    # If DB-on, validate summary structure
    if data["ok"] and data["connection_ok"] and data["summary"]:
        assert "window_7d" in data["summary"]
        assert "window_30d" in data["summary"]
        for window_key in ["window_7d", "window_30d"]:
            window_data = data["summary"][window_key]
            assert "runs" in window_data
            assert "por_ok_ratio" in window_data
            assert "schema_ok_ratio" in window_data
            assert "provenance_ok_ratio" in window_data


def test_top_violations_7d_evidence_structure():
    """Test that top_violations_7d.json has correct structure (DB-off validation)."""
    evidence_file = REPO / "share" / "atlas" / "control_plane" / "top_violations_7d.json"

    # If file doesn't exist, that's OK (DB-off case)
    if not evidence_file.exists():
        pytest.skip("Evidence file not found (DB-off case)")

    # Read and parse JSON
    content = evidence_file.read_text(encoding="utf-8")
    data = json.loads(content)

    # Validate top-level keys
    required_keys = {"schema", "generated_at", "ok", "connection_ok", "window", "violations"}
    assert required_keys.issubset(data.keys()), f"Missing required keys: {required_keys - data.keys()}"

    # Validate schema
    assert data["schema"] == "control"

    # Validate window
    assert data["window"] == "7d"

    # Validate generated_at is ISO format
    assert "T" in data["generated_at"] or "Z" in data["generated_at"]

    # Validate ok and connection_ok are booleans
    assert isinstance(data["ok"], bool)
    assert isinstance(data["connection_ok"], bool)

    # Validate violations is a list
    assert isinstance(data["violations"], list)

    # If DB-off (ok=False or connection_ok=False), error should be present
    if not data["ok"] or not data["connection_ok"]:
        assert "error" in data, "DB-off case should have 'error' field"
        assert isinstance(data["error"], str)
        assert len(data["error"]) > 0

    # If DB-on, validate violations structure
    if data["ok"] and data["connection_ok"]:
        for violation in data["violations"]:
            assert "violation_code" in violation
            assert "count" in violation
            assert isinstance(violation["count"], int)


def test_top_violations_30d_evidence_structure():
    """Test that top_violations_30d.json has correct structure (DB-off validation)."""
    evidence_file = REPO / "share" / "atlas" / "control_plane" / "top_violations_30d.json"

    # If file doesn't exist, that's OK (DB-off case)
    if not evidence_file.exists():
        pytest.skip("Evidence file not found (DB-off case)")

    # Read and parse JSON
    content = evidence_file.read_text(encoding="utf-8")
    data = json.loads(content)

    # Validate top-level keys
    required_keys = {"schema", "generated_at", "ok", "connection_ok", "window", "violations"}
    assert required_keys.issubset(data.keys()), f"Missing required keys: {required_keys - data.keys()}"

    # Validate schema
    assert data["schema"] == "control"

    # Validate window
    assert data["window"] == "30d"

    # Validate generated_at is ISO format
    assert "T" in data["generated_at"] or "Z" in data["generated_at"]

    # Validate ok and connection_ok are booleans
    assert isinstance(data["ok"], bool)
    assert isinstance(data["connection_ok"], bool)

    # Validate violations is a list
    assert isinstance(data["violations"], list)

    # If DB-off (ok=False or connection_ok=False), error should be present
    if not data["ok"] or not data["connection_ok"]:
        assert "error" in data, "DB-off case should have 'error' field"
        assert isinstance(data["error"], str)
        assert len(data["error"]) > 0

    # If DB-on, validate violations structure
    if data["ok"] and data["connection_ok"]:
        for violation in data["violations"]:
            assert "violation_code" in violation
            assert "count" in violation
            assert isinstance(violation["count"], int)
