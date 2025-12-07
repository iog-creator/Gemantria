"""
Tests for pmagent handoff status and boot commands.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_status_handoff_json():
    """Test status-handoff command with JSON output."""
    result = subprocess.run(
        [sys.executable, "-m", "pmagent", "handoff", "status-handoff", "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    envelope = json.loads(result.stdout)

    # Verify schema
    assert "ok" in envelope
    assert "kernel" in envelope
    assert "health" in envelope
    assert "degraded" in envelope
    assert "warnings" in envelope

    # Verify kernel fields
    kernel = envelope["kernel"]
    assert "current_phase" in kernel
    assert "branch" in kernel
    assert "ground_truth_files" in kernel

    print("✅ status-handoff JSON test passed")


def test_status_handoff_human():
    """Test status-handoff command with human output."""
    result = subprocess.run(
        [sys.executable, "-m", "pmagent", "handoff", "status-handoff"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    output = result.stdout

    # Check for expected content
    assert "Handoff Status:" in output
    assert "Phase:" in output
    assert "Branch:" in output

    print("✅ status-handoff human test passed")


def test_boot_pm_json():
    """Test boot-pm command with JSON output."""
    result = subprocess.run(
        [sys.executable, "-m", "pmagent", "handoff", "boot-pm", "--mode", "json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    envelope = json.loads(result.stdout)

    # Verify schema
    assert "ok" in envelope
    assert "mode" in envelope
    assert envelope["mode"] in ["NORMAL", "DEGRADED"]
    assert "snapshot" in envelope
    assert "kernel" in envelope
    assert "bootstrap" in envelope
    assert "health" in envelope
    assert "recommended_behavior" in envelope

    # Verify recommended_behavior has all agents
    behavior = envelope["recommended_behavior"]
    assert "pm" in behavior
    assert "oa" in behavior
    assert "ops" in behavior

    print("✅ boot-pm JSON test passed")


def test_boot_pm_seed():
    """Test boot-pm command with seed output."""
    result = subprocess.run(
        [sys.executable, "-m", "pmagent", "handoff", "boot-pm", "--mode", "seed"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    output = result.stdout

    # Check for expected content
    assert "You are the PM of Gemantria" in output
    assert "Kernel says:" in output
    assert "phase" in output
    assert "branch" in output

    print("✅ boot-pm seed test passed")


if __name__ == "__main__":
    print("Running Phase 26.B' smoke tests...")
    test_status_handoff_json()
    test_status_handoff_human()
    test_boot_pm_json()
    test_boot_pm_seed()
    print("\n✅ All tests passed!")
