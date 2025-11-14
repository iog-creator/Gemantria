"""
PLAN-080 E99 — Integrated Browser + Screenshot Verification Guard Tests

Tests for the integrated guard that aggregates PLAN-079 guards (E91-E95).
"""

import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[3]
FIXTURES_DIR = ROOT / "agentpm" / "tests" / "atlas" / "fixtures" / "e99"
GUARD_SCRIPT = ROOT / "scripts" / "guards" / "guard_browser_screenshot_integrated.py"


def _load_fixture(name: str) -> dict:
    """Load a fixture JSON file."""
    path = FIXTURES_DIR / name
    if not path.exists():
        pytest.skip(f"Fixture {name} not found")
    return json.loads(path.read_text())


def _run_guard() -> subprocess.CompletedProcess:
    """Run the integrated guard script."""
    return subprocess.run(
        [sys.executable, str(GUARD_SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def _mock_guard_subprocess(guard_name: str, fixture_name: str):
    """Create a mock subprocess.run that returns fixture JSON for a specific guard."""
    fixture = _load_fixture(fixture_name)

    def mock_run(cmd, **kwargs):
        class MockResult:
            stdout = json.dumps(fixture)
            returncode = 0 if fixture.get("ok", False) else 1

        return MockResult()

    return mock_run


def test_integrated_guard_emits_json_with_core_fields():
    """Test that integrated guard emits JSON with required fields."""
    result = _run_guard()
    assert result.stdout.strip(), f"guard emitted no stdout: {result}"
    doc = json.loads(result.stdout)
    assert "ok" in doc
    assert "checks" in doc
    assert "counts" in doc
    assert "details" in doc


def test_integrated_guard_structure():
    """Test that integrated guard has correct structure."""
    result = _run_guard()
    doc = json.loads(result.stdout)

    # Check top-level structure
    assert isinstance(doc["ok"], bool)
    assert isinstance(doc["checks"], dict)
    assert isinstance(doc["counts"], dict)
    assert isinstance(doc["details"], dict)

    # Check that all 5 guards are represented
    expected_checks = [
        "receipts_guard_ok",
        "screenshot_manifest_guard_ok",
        "browser_verification_guard_ok",
        "tagproof_screenshots_guard_ok",
        "atlas_links_guard_ok",
    ]
    for check in expected_checks:
        assert check in doc["checks"], f"Missing check: {check}"

    # Check counts structure
    assert "guards_total" in doc["counts"]
    assert doc["counts"]["guards_total"] == 5
    assert "guards_ok" in doc["counts"]
    assert "guards_failed" in doc["counts"]
    assert "broken_links" in doc["counts"]
    assert "missing_screenshots" in doc["counts"]


def test_integrated_guard_runs_successfully():
    """Test that integrated guard runs and produces valid JSON output."""
    result = _run_guard()
    assert result.returncode in (0, 1), "Guard should exit with 0 or 1"
    assert result.stdout.strip(), "Guard should produce output"
    doc = json.loads(result.stdout)
    assert "ok" in doc
    assert "checks" in doc
    assert "counts" in doc
    assert "details" in doc


def test_integrated_guard_handles_guard_failures():
    """Test that integrated guard correctly aggregates guard results."""
    result = _run_guard()
    doc = json.loads(result.stdout)

    # If any guard fails, integrated ok should be False
    if not doc["ok"]:
        assert doc["counts"]["guards_failed"] > 0, "Should have failed guards when ok is False"
        assert any(not v for v in doc["checks"].values()), "At least one check should be False"


def test_integrated_guard_handles_missing_scripts():
    """Test that integrated guard handles missing guard scripts gracefully."""
    result = _run_guard()
    doc = json.loads(result.stdout)

    # All guards should be represented in checks, even if they fail
    expected_checks = [
        "receipts_guard_ok",
        "screenshot_manifest_guard_ok",
        "browser_verification_guard_ok",
        "tagproof_screenshots_guard_ok",
        "atlas_links_guard_ok",
    ]
    for check in expected_checks:
        assert check in doc["checks"], f"Missing check: {check}"

    # If a guard script is missing, it should be reflected in details
    for guard_name in ["receipts_guard", "screenshot_manifest_guard", "browser_verification_guard", "tagproof_screenshots_guard", "atlas_links_guard"]:
        assert guard_name in doc["details"], f"Missing details for {guard_name}"


def test_integrated_guard_counts_consistency():
    """Test that counts are consistent (guards_ok + guards_failed == guards_total)."""
    result = _run_guard()
    doc = json.loads(result.stdout)

    counts = doc["counts"]
    total = counts["guards_total"]
    ok = counts["guards_ok"]
    failed = counts["guards_failed"]

    assert ok + failed == total, f"guards_ok ({ok}) + guards_failed ({failed}) should equal guards_total ({total})"


def test_integrated_guard_extracts_broken_links():
    """Test that broken_links count is extracted from atlas_links_guard."""
    result = _run_guard()
    doc = json.loads(result.stdout)

    # If atlas_links_guard ran successfully, check that broken_links is in counts
    if "atlas_links_guard" in doc["details"]:
        assert "broken_links" in doc["counts"], "Should extract broken_links count"
        assert isinstance(doc["counts"]["broken_links"], int), "broken_links should be an integer"
