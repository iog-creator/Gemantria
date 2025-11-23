"""
Tests for Phase D Autopilot Summary Export.

Tests the export generation, structure validation, and guard functionality.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

# Add project root to path
import sys

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

CONTROL_PLANE_DIR = REPO / "share" / "atlas" / "control_plane"
EVIDENCE_DIR = REPO / "evidence"
EXPORT_SCRIPT = REPO / "scripts" / "db" / "control_autopilot_summary_export.py"
GUARD_SCRIPT = REPO / "scripts" / "guards" / "guard_control_autopilot_summary.py"


def test_export_script_exists():
    """Test that export script exists."""
    assert EXPORT_SCRIPT.exists(), "control_autopilot_summary_export.py should exist"
    assert EXPORT_SCRIPT.is_file(), "control_autopilot_summary_export.py should be a file"


def test_guard_script_exists():
    """Test that guard script exists."""
    assert GUARD_SCRIPT.exists(), "guard_control_autopilot_summary.py should exist"
    assert GUARD_SCRIPT.is_file(), "guard_control_autopilot_summary.py should be a file"


def test_export_autopilot_summary_exists():
    """Test that autopilot_summary.json export exists."""
    json_path = CONTROL_PLANE_DIR / "autopilot_summary.json"
    assert json_path.exists(), "autopilot_summary.json should exist"


def test_export_autopilot_summary_structure():
    """Test autopilot_summary.json has required structure."""
    json_path = CONTROL_PLANE_DIR / "autopilot_summary.json"

    with json_path.open() as f:
        data = json.load(f)

    # Check required top-level fields
    required_fields = [
        "schema",
        "generated_at",
        "ok",
        "stats",
        "window_days",
    ]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

    # Check schema
    assert data["schema"] == "autopilot_summary_v1", "Schema should be autopilot_summary_v1"

    # Check stats structure
    assert isinstance(data["stats"], dict), "stats should be a dict"
    assert isinstance(data["window_days"], int), "window_days should be an int"


def test_export_autopilot_summary_stats_structure():
    """Test that stats dict has correct structure for each tool."""
    json_path = CONTROL_PLANE_DIR / "autopilot_summary.json"

    with json_path.open() as f:
        data = json.load(f)

    stats = data.get("stats", {})
    for tool, tool_stats in stats.items():
        assert isinstance(tool_stats, dict), f"Tool {tool} stats should be a dict"
        required_tool_fields = ["total", "success", "error"]
        for field in required_tool_fields:
            assert field in tool_stats, f"Tool {tool} missing field: {field}"
            assert isinstance(tool_stats[field], int), f"Tool {tool} {field} should be an int"


def test_guard_passes():
    """Test that guard script passes on valid export."""
    result = subprocess.run(
        [sys.executable, str(GUARD_SCRIPT), "--write-evidence", "guard_control_autopilot_summary.json"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )

    # Guard should exit 0 (pass) or exit 0 in HINT mode even if ok=false
    assert result.returncode == 0, f"Guard should pass (exit 0). Output: {result.stdout}\nError: {result.stderr}"

    # Check evidence file was created
    evidence_path = EVIDENCE_DIR / "guard_control_autopilot_summary.json"
    assert evidence_path.exists(), "Guard evidence file should exist"

    with evidence_path.open() as f:
        evidence = json.load(f)

    assert evidence["guard"] == "guard_control_autopilot_summary", "Guard name should match"
    assert "checks" in evidence, "Evidence should have checks"
    assert "file_exists" in evidence["checks"], "Evidence should check file_exists"


def test_export_can_be_generated():
    """Test that export script can be run (hermetic - may have empty stats)."""
    result = subprocess.run(
        [sys.executable, str(EXPORT_SCRIPT)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=30,
    )

    # Export should exit 0 even if DB is empty (hermetic tolerance)
    assert result.returncode == 0, f"Export should exit 0. Output: {result.stdout}\nError: {result.stderr}"

    # Verify file was created
    json_path = CONTROL_PLANE_DIR / "autopilot_summary.json"
    assert json_path.exists(), "Export should create autopilot_summary.json"
