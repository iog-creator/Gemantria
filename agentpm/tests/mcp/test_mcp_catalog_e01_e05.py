"""PLAN-073 M1: MCP catalog foundation tests (E01-E05)."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys


# E01: Schema exists
def test_e01_schema_exists():
    """Verify Knowledge MCP schema file exists and is valid JSON Schema."""
    schema_path = pathlib.Path("docs/SSOT/SSOT_mcp_catalog.v1.schema.json")
    assert schema_path.exists(), f"Schema file missing: {schema_path}"
    data = json.loads(schema_path.read_text())
    # Verify it's a valid JSON Schema
    assert data.get("$schema") == "http://json-schema.org/draft-07/schema#"
    assert data.get("title") == "Knowledge MCP Catalog (v1)"
    # Verify required properties include "schema" and "tables"
    assert "schema" in data.get("required", [])
    assert "tables" in data.get("properties", {})


# E02: RO-DSN guard
def test_e02_ro_dsn_guard():
    """Verify RO-DSN guard script runs and produces guard JSON."""
    guard_script = pathlib.Path("scripts/guards/guard_mcp_rodsn.py")
    assert guard_script.exists(), f"Guard script missing: {guard_script}"
    assert guard_script.is_file() and (guard_script.stat().st_mode & 0o111), "Guard script not executable"

    # Run guard (may fail in hermetic mode, but should produce output)
    result = subprocess.run(
        [sys.executable, str(guard_script)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"Guard script failed: {result.stderr}"

    # Verify guard JSON output
    guard_json = pathlib.Path("share/mcp/rodsn.guard.json")
    if guard_json.exists():
        data = json.loads(guard_json.read_text())
        assert "ok" in data
        assert "dsn_redacted" in data


# E03: Envelope ingest
def test_e03_envelope_ingest():
    """Verify envelope ingest path works (file→share/mcp/envelopes/*.json)."""
    from agentpm.mcp.ingest import ingest

    # Create a minimal test envelope
    test_env = {"id": "test-env-001", "book": "Genesis", "data": {"test": True}}
    test_file = pathlib.Path("share/mcp/test_envelope.json")
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text(json.dumps(test_env))

    # Ingest it
    result_path = ingest(str(test_file))
    assert pathlib.Path(result_path).exists(), f"Ingested file missing: {result_path}"

    # Verify structure
    ingested = json.loads(pathlib.Path(result_path).read_text())
    assert "envelope" in ingested
    assert "stamp" in ingested
    assert ingested["stamp"]["id"] == "test-env-001"

    # Cleanup
    test_file.unlink(missing_ok=True)


# E04: Query roundtrip
def test_e04_query_roundtrip():
    """Verify minimal query roundtrip produces deterministic output."""
    query_script = pathlib.Path("scripts/mcp_query_roundtrip.py")
    assert query_script.exists(), f"Query script missing: {query_script}"

    # Ensure envelopes directory exists (may be empty)
    envdir = pathlib.Path("share/mcp/envelopes")
    envdir.mkdir(parents=True, exist_ok=True)

    # Run query
    result = subprocess.run(
        [sys.executable, str(query_script)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"Query script failed: {result.stderr}"

    # Verify output JSON
    output_json = pathlib.Path("share/mcp/query_result.json")
    assert output_json.exists(), "Query result JSON missing"
    data = json.loads(output_json.read_text())
    assert "count" in data
    assert isinstance(data["count"], int)


# E05: Proof snapshot
def test_e05_proof_snapshot():
    """Verify proof snapshot helper creates required files."""
    snapshot_script = pathlib.Path("scripts/mcp_proof_snapshot.sh")
    assert snapshot_script.exists(), f"Snapshot script missing: {snapshot_script}"
    assert snapshot_script.is_file() and (snapshot_script.stat().st_mode & 0o111), "Snapshot script not executable"

    # Run snapshot
    result = subprocess.run(
        ["bash", str(snapshot_script)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"Snapshot script failed: {result.stderr}"

    # Verify outputs
    generated_at = pathlib.Path("share/mcp/proof_snapshot.generated_at.txt")
    proof_ok = pathlib.Path("share/mcp/proof_ok.json")

    assert generated_at.exists(), "proof_snapshot.generated_at.txt missing"
    assert proof_ok.exists(), "proof_ok.json missing"

    # Verify proof_ok.json structure
    data = json.loads(proof_ok.read_text())
    assert data.get("proof") == "mcp"
    assert data.get("ok") is True
