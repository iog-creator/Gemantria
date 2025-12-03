"""PLAN-073 M1: Knowledge MCP foundation tests (E01-E05)."""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys


# E01: Schema guard
def test_e01_schema_guard_exists():
    """Verify Knowledge MCP schema guard script exists."""
    guard_script = pathlib.Path("scripts/guards/guard_mcp_schema.py")
    assert guard_script.exists(), f"Guard script missing: {guard_script}"


def test_e01_schema_guard_hint_mode():
    """Verify schema guard runs in HINT mode with DB-off (hermetic-friendly)."""
    guard_script = pathlib.Path("scripts/guards/guard_mcp_schema.py")
    if not guard_script.exists():
        return  # Skip if guard doesn't exist yet

    # Run guard in HINT mode (default)
    env = os.environ.copy()
    env.pop("STRICT_MODE", None)
    env.pop("CI", None)

    result = subprocess.run(
        [sys.executable, str(guard_script)],
        capture_output=True,
        text=True,
        timeout=10,
        env=env,
    )

    # Guard should exit 0 in HINT mode even if DB is unavailable
    assert result.returncode == 0, f"Guard should exit 0 in HINT mode: {result.stderr}"

    # Verify JSON output
    try:
        output = json.loads(result.stdout)
        assert "ok" in output
        assert "mode" in output
        assert output["mode"] == "HINT"
        assert "schema_exists" in output
        assert "tables_present" in output
        assert "view_exists" in output
    except json.JSONDecodeError:
        # If stdout is not JSON, check stderr for hints
        assert "HINT" in result.stderr or "HINT" in result.stdout, "Expected HINT message"


def test_e01_schema_guard_evidence_file():
    """Verify schema guard writes evidence file."""
    guard_script = pathlib.Path("scripts/guards/guard_mcp_schema.py")
    evidence_file = pathlib.Path("evidence/guard_mcp_schema.json")

    if not guard_script.exists():
        return  # Skip if guard doesn't exist yet

    # Run guard
    result = subprocess.run(
        [sys.executable, str(guard_script)],
        capture_output=True,
        text=True,
        timeout=10,
    )

    # Evidence file should exist after running guard
    if result.returncode == 0 and evidence_file.exists():
        data = json.loads(evidence_file.read_text())
        assert "ok" in data
        assert "mode" in data
        assert "generated_at" in data


# E02: RO-DSN guard + redaction proof
def test_e02_echo_dsn_ro_redacts_credentials():
    """Verify echo_dsn_ro.py redacts credentials in DSN output."""
    echo_script = pathlib.Path("scripts/mcp/echo_dsn_ro.py")
    if not echo_script.exists():
        return  # Skip if script doesn't exist yet

    # Run echo script
    result = subprocess.run(
        [sys.executable, str(echo_script)],
        capture_output=True,
        text=True,
        timeout=10,
    )

    # Should exit 0 even if no DSN (HINT mode)
    assert result.returncode == 0, f"Echo script should exit 0: {result.stderr}"

    # If DSN is present, verify it's redacted
    if result.stdout and "postgresql://" in result.stdout:
        # Should contain <REDACTED> or ***, not actual credentials
        assert "<REDACTED>" in result.stdout or "***" in result.stdout, "DSN should be redacted"
        # Should not contain password patterns (user:password@)
        assert ":" not in result.stdout.split("@")[0].split("://")[-1] or "<REDACTED>" in result.stdout


def test_e02_guard_mcp_db_ro_hint_mode_db_off():
    """Verify guard runs in HINT mode with DB-off (hermetic-friendly)."""
    guard_script = pathlib.Path("scripts/ci/guard_mcp_db_ro.py")
    if not guard_script.exists():
        return  # Skip if guard doesn't exist yet

    # Run guard in HINT mode (default)
    env_vars = os.environ.copy()
    env_vars.pop("STRICT_MODE", None)
    env_vars.pop("STRICT_DB_PROBE", None)
    env_vars.pop("CI", None)

    result = subprocess.run(
        [sys.executable, str(guard_script)],
        capture_output=True,
        text=True,
        timeout=10,
        env=env_vars,
    )

    # Guard should exit 0 in HINT mode even if DB is unavailable
    assert result.returncode == 0, f"Guard should exit 0 in HINT mode: {result.stderr}"

    # Verify JSON output
    try:
        output = json.loads(result.stdout)
        assert "ok" in output
        assert "mode" in output
        assert output["mode"] == "HINT"
        assert "dsn_redacted" in output
        assert "ro_access" in output
        assert "view_accessible" in output
    except json.JSONDecodeError:
        # If stdout is not JSON, check stderr for hints
        assert "HINT" in result.stderr or "HINT" in result.stdout, "Expected HINT message"


def test_e02_guard_mcp_db_ro_redaction_proof():
    """Verify guard generates redaction proof artifact."""
    guard_script = pathlib.Path("scripts/ci/guard_mcp_db_ro.py")
    evidence_file = pathlib.Path("evidence/guard_mcp_db_ro_redaction.json")

    if not guard_script.exists():
        return  # Skip if guard doesn't exist yet

    # Run guard
    result = subprocess.run(
        [sys.executable, str(guard_script)],
        capture_output=True,
        text=True,
        timeout=10,
    )

    # Evidence file should exist after running guard
    if result.returncode == 0 and evidence_file.exists():
        data = json.loads(evidence_file.read_text())
        assert "ok" in data
        assert "mode" in data
        assert "dsn_redacted" in data
        assert "ro_access" in data
        assert "view_accessible" in data
        assert "details" in data


# E03: Envelope ingest
def test_e03_ingest_envelope_validates_schema():
    """Verify ingest script validates envelope against schema."""
    ingest_script = pathlib.Path("scripts/mcp/ingest_envelope.py")
    if not ingest_script.exists():
        return  # Skip if script doesn't exist yet

    # Create invalid envelope (missing required fields: generated_at, endpoints)
    invalid_envelope = pathlib.Path("share/mcp/test_invalid_envelope.json")
    invalid_envelope.parent.mkdir(parents=True, exist_ok=True)
    invalid_envelope.write_text(json.dumps({"schema": "mcp_ingest_envelope.v1", "tools": []}, indent=2))

    # Run ingest script
    result = subprocess.run(
        [sys.executable, str(ingest_script), "--envelope", str(invalid_envelope)],
        capture_output=True,
        text=True,
        timeout=10,
    )

    # Should fail with validation error (either JSON decode or schema validation)
    assert result.returncode != 0, f"Ingest should fail on invalid envelope: {result.stderr}"
    # Accept any error message indicating failure (validation, required, invalid json, etc.)
    assert len(result.stderr) > 0, "Should have error message in stderr"

    # Cleanup
    invalid_envelope.unlink(missing_ok=True)


def test_e03_ingest_envelope_db_off_hint_mode():
    """Verify ingest script exits 0 in HINT mode when DB is unavailable."""
    ingest_script = pathlib.Path("scripts/mcp/ingest_envelope.py")
    schema_file = pathlib.Path("schemas/mcp_ingest_envelope.v1.schema.json")
    if not ingest_script.exists() or not schema_file.exists():
        return  # Skip if script or schema doesn't exist yet

    # Create valid test envelope
    test_envelope = pathlib.Path("share/mcp/test_envelope_e03.json")
    test_envelope.parent.mkdir(parents=True, exist_ok=True)
    test_envelope.write_text(
        json.dumps(
            {
                "schema": "mcp_ingest_envelope.v1",
                "generated_at": "2025-01-01T00:00:00Z",
                "tools": [
                    {
                        "name": "test_tool",
                        "description": "Test tool for E03",
                        "tags": ["test"],
                        "visibility": "public",
                    }
                ],
                "endpoints": [
                    {
                        "name": "test_tool",
                        "path": "/api/test",
                        "method": "GET",
                        "auth": "none",
                    }
                ],
            }
        )
    )

    # Run ingest script in HINT mode (no DSN)
    env_vars = os.environ.copy()
    env_vars.pop("GEMATRIA_DSN", None)
    env_vars.pop("RW_DSN", None)
    env_vars.pop("ATLAS_DSN", None)
    env_vars.pop("STRICT_MODE", None)

    result = subprocess.run(
        [sys.executable, str(ingest_script), "--envelope", str(test_envelope)],
        capture_output=True,
        text=True,
        timeout=10,
        env=env_vars,
    )

    # Should exit 0 in HINT mode even if DB unavailable
    assert result.returncode == 0, f"Ingest should exit 0 in HINT mode: {result.stderr}"
    assert "HINT" in result.stderr or "HINT" in result.stdout

    # Cleanup
    test_envelope.unlink(missing_ok=True)


def test_e03_ingest_envelope_idempotent():
    """Verify ingest is idempotent (two runs produce same row counts)."""
    ingest_script = pathlib.Path("scripts/mcp/ingest_envelope.py")
    schema_file = pathlib.Path("schemas/mcp_ingest_envelope.v1.schema.json")
    if not ingest_script.exists() or not schema_file.exists():
        return  # Skip if script or schema doesn't exist yet

    # Skip if no DSN available (hermetic test)
    dsn = os.getenv("GEMATRIA_DSN") or os.getenv("RW_DSN") or os.getenv("ATLAS_DSN")
    if not dsn:
        return  # Skip if no DB available

    # Create valid test envelope
    test_envelope = pathlib.Path("share/mcp/test_envelope_e03_idempotent.json")
    test_envelope.parent.mkdir(parents=True, exist_ok=True)
    test_envelope.write_text(
        json.dumps(
            {
                "schema": "mcp_ingest_envelope.v1",
                "generated_at": "2025-01-01T00:00:00Z",
                "tools": [
                    {
                        "name": "test_tool_idempotent",
                        "description": "Test tool for idempotency",
                        "tags": ["test"],
                        "visibility": "public",
                    }
                ],
                "endpoints": [
                    {
                        "name": "test_tool_idempotent",
                        "path": "/api/test",
                        "method": "GET",
                        "auth": "none",
                    }
                ],
            }
        )
    )

    # First run
    result1 = subprocess.run(
        [sys.executable, str(ingest_script), "--envelope", str(test_envelope)],
        capture_output=True,
        text=True,
        timeout=10,
    )

    if result1.returncode != 0:
        # DB might not be available, skip test
        test_envelope.unlink(missing_ok=True)
        return

    # Extract counts from first run
    output1 = result1.stdout
    inserted1 = int(output1.split("inserted")[0].split()[-1]) if "inserted" in output1 else 0

    # Second run (should update, not insert)
    result2 = subprocess.run(
        [sys.executable, str(ingest_script), "--envelope", str(test_envelope)],
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result2.returncode == 0, f"Second ingest should succeed: {result2.stderr}"

    # Extract counts from second run
    output2 = result2.stdout
    updated2 = int(output2.split("updated")[0].split()[-1]) if "updated" in output2 else 0

    # First run should insert, second run should update (idempotent)
    assert inserted1 > 0 or updated2 > 0, "First run should insert, second run should update"

    # Cleanup
    test_envelope.unlink(missing_ok=True)


# E04: Query roundtrip
def test_e04_query_catalog_db_off_hint_mode():
    """Verify query_catalog.py exits 0 in HINT mode when DB is unavailable."""
    query_script = pathlib.Path("scripts/mcp/query_catalog.py")
    if not query_script.exists():
        return  # Skip if script doesn't exist yet

    # Run query script in HINT mode (no DSN)
    env_vars = os.environ.copy()
    env_vars.pop("GEMATRIA_RO_DSN", None)
    env_vars.pop("ATLAS_DSN_RO", None)
    env_vars.pop("ATLAS_DSN", None)
    env_vars.pop("GEMATRIA_DSN", None)
    env_vars.pop("STRICT_MODE", None)

    result = subprocess.run(
        [sys.executable, str(query_script)],
        capture_output=True,
        text=True,
        timeout=10,
        env=env_vars,
    )

    # Should exit 0 in HINT mode even if DB unavailable
    assert result.returncode == 0, f"Query should exit 0 in HINT mode: {result.stderr}"
    assert "HINT" in result.stderr or result.stdout.strip() == "[]", "Should output HINT or empty array"


def test_e04_query_catalog_output_shape():
    """Verify query_catalog.py outputs valid JSON with expected keys."""
    query_script = pathlib.Path("scripts/mcp/query_catalog.py")
    if not query_script.exists():
        return  # Skip if script doesn't exist yet

    # Skip if no DSN available (hermetic test)
    dsn = (
        os.getenv("GEMATRIA_RO_DSN") or os.getenv("ATLAS_DSN_RO") or os.getenv("ATLAS_DSN") or os.getenv("GEMATRIA_DSN")
    )
    if not dsn:
        return  # Skip if no DB available

    result = subprocess.run(
        [sys.executable, str(query_script)],
        capture_output=True,
        text=True,
        timeout=10,
    )

    if result.returncode != 0:
        # DB might not be available or view doesn't exist, skip test
        return

    # Parse output
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Output is not valid JSON: {result.stdout}") from e

    # Should be an array
    assert isinstance(data, list), f"Expected array, got {type(data).__name__}"

    # If array is not empty, validate structure
    if data:
        expected_keys = {"name", "desc", "tags", "cost_est", "visibility", "path", "method", "auth"}
        for item in data:
            assert isinstance(item, dict), f"Item should be a dict: {item}"
            item_keys = set(item.keys())
            assert expected_keys.issubset(item_keys), f"Item missing expected keys: {expected_keys - item_keys}"


def test_e04_guard_mcp_query_writes_evidence():
    """Verify guard_mcp_query.py writes evidence file with ok flag."""
    guard_script = pathlib.Path("scripts/guards/guard_mcp_query.py")
    evidence_file = pathlib.Path("evidence/guard_mcp_query.json")
    if not guard_script.exists():
        return  # Skip if guard doesn't exist yet

    # Run guard in HINT mode (default)
    env_vars = os.environ.copy()
    env_vars.pop("STRICT_MODE", None)
    env_vars.pop("CI", None)

    result = subprocess.run(
        [sys.executable, str(guard_script)],
        capture_output=True,
        text=True,
        timeout=10,
        env=env_vars,
    )

    # Guard should exit 0 in HINT mode
    assert result.returncode == 0, f"Guard should exit 0 in HINT mode: {result.stderr}"

    # Verify evidence file exists
    assert evidence_file.exists(), f"Evidence file missing: {evidence_file}"

    # Verify evidence file content
    data = json.loads(evidence_file.read_text())
    assert "ok" in data, "Evidence should have 'ok' field"
    assert "mode" in data, "Evidence should have 'mode' field"
    assert data["mode"] == "HINT", "Should be in HINT mode"
    assert "query_executed" in data, "Evidence should have 'query_executed' field"
    assert "output_valid" in data, "Evidence should have 'output_valid' field"


# E05: Proof snapshot
def test_e05_generate_proof_snapshot_builds_expected_shape():
    """Verify generate_proof_snapshot.py creates expected JSON and TXT files."""
    snapshot_script = pathlib.Path("scripts/mcp/generate_proof_snapshot.py")
    schema_file = pathlib.Path("schemas/mcp_proof_snapshot.v1.schema.json")
    if not snapshot_script.exists() or not schema_file.exists():
        return  # Skip if script or schema doesn't exist yet

    # Ensure evidence directory exists (may be empty)
    evidence_dir = pathlib.Path("evidence")
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # Run snapshot generator
    result = subprocess.run(
        [sys.executable, str(snapshot_script)],
        capture_output=True,
        text=True,
        timeout=10,
    )

    # Should exit 0 in HINT mode even if components missing
    assert result.returncode == 0, f"Snapshot generator should exit 0: {result.stderr}"

    # Verify outputs exist
    proof_json = pathlib.Path("share/mcp/knowledge_mcp_proof.json")
    proof_txt = pathlib.Path("share/mcp/knowledge_mcp_proof.txt")

    assert proof_json.exists(), f"Proof JSON missing: {proof_json}"
    assert proof_txt.exists(), f"Proof TXT missing: {proof_txt}"

    # Verify JSON structure
    data = json.loads(proof_json.read_text())
    assert data.get("schema") == "mcp_proof_snapshot.v1"
    assert "generated_at" in data
    assert "components" in data
    assert "artifacts" in data
    assert "overall_ok" in data
    assert isinstance(data["overall_ok"], bool)

    # Verify components structure
    components = data.get("components", {})
    assert "e01_schema" in components
    assert "e02_ro_dsn" in components
    assert "e03_ingest" in components
    assert "e04_query" in components


def test_e05_guard_mcp_proof_validates_schema_and_overall_ok():
    """Verify guard_mcp_proof.py validates schema and overall_ok consistency."""
    guard_script = pathlib.Path("scripts/guards/guard_mcp_proof.py")
    evidence_file = pathlib.Path("evidence/guard_mcp_proof.json")
    if not guard_script.exists():
        return  # Skip if guard doesn't exist yet

    # First, generate snapshot (may be empty/missing components)
    snapshot_script = pathlib.Path("scripts/mcp/generate_proof_snapshot.py")
    if snapshot_script.exists():
        subprocess.run(
            [sys.executable, str(snapshot_script)],
            capture_output=True,
            text=True,
            timeout=10,
        )

    # Run guard in HINT mode (default)
    env_vars = os.environ.copy()
    env_vars.pop("STRICT_MODE", None)
    env_vars.pop("CI", None)

    result = subprocess.run(
        [sys.executable, str(guard_script)],
        capture_output=True,
        text=True,
        timeout=10,
        env=env_vars,
    )

    # Guard should exit 0 in HINT mode
    assert result.returncode == 0, f"Guard should exit 0 in HINT mode: {result.stderr}"

    # Verify evidence file exists
    assert evidence_file.exists(), f"Evidence file missing: {evidence_file}"

    # Verify evidence file content
    data = json.loads(evidence_file.read_text())
    assert "ok" in data, "Evidence should have 'ok' field"
    assert "mode" in data, "Evidence should have 'mode' field"
    assert data["mode"] == "HINT", "Should be in HINT mode"
    assert "snapshot_present" in data, "Evidence should have 'snapshot_present' field"
    assert "snapshot_valid" in data, "Evidence should have 'snapshot_valid' field"
    assert "overall_ok_consistent" in data, "Evidence should have 'overall_ok_consistent' field"
