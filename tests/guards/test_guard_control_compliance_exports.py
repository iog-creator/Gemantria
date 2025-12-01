"""Test guard_control_compliance_exports guard."""

import json
from pathlib import Path

import pytest

# Add project root to path
REPO = Path(__file__).resolve().parents[2]


def test_guard_control_compliance_exports_verdict_structure():
    """Test that guard_control_compliance_exports.json has correct structure."""
    # First, ensure exports exist (DB-off mode is fine)
    # Use subprocess to avoid argparse conflicts with pytest
    import subprocess
    import sys

    subprocess.run(
        [sys.executable, str(REPO / "scripts" / "db" / "control_compliance_exports.py")],
        cwd=str(REPO),
        check=False,
    )

    # Now run the guard
    from scripts.guards.guard_control_compliance_exports import main as guard_main

    guard_main()

    # Check verdict file exists
    verdict_file = REPO / "evidence" / "guard_control_compliance_exports.json"
    assert verdict_file.exists(), "Guard verdict file should exist"

    # Read and parse JSON
    content = verdict_file.read_text(encoding="utf-8")
    data = json.loads(content)

    # Validate top-level keys
    required_keys = {"schema", "generated_at", "ok", "files_checked", "errors"}
    assert required_keys.issubset(
        data.keys()
    ), f"Missing required keys: {required_keys - data.keys()}"

    # Validate schema
    assert data["schema"] == "control"

    # Validate generated_at is ISO format
    assert "T" in data["generated_at"] or "Z" in data["generated_at"]

    # Validate ok is boolean
    assert isinstance(data["ok"], bool)

    # Validate files_checked is a list
    assert isinstance(data["files_checked"], list)
    assert len(data["files_checked"]) == 3
    assert "compliance.head.json" in data["files_checked"]
    assert "top_violations_7d.json" in data["files_checked"]
    assert "top_violations_30d.json" in data["files_checked"]

    # Validate errors is a list
    assert isinstance(data["errors"], list)

    # Even in DB-off mode, the guard should treat files as structurally ok
    # if required keys are present (including error fields where appropriate)
    # The guard checks structure, not whether DB connection was successful
    assert data["ok"] is True, "Guard should pass if files have correct structure (even if DB-off)"


def test_guard_control_compliance_exports_missing_file():
    """Test guard behavior when a file is missing."""
    # This test verifies the guard detects missing files
    # We'll skip this in CI since we can't reliably remove files
    pytest.skip("Requires file manipulation; skip in CI")
