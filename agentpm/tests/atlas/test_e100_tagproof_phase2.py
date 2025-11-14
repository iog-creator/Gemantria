"""
PLAN-080 E100 — Phase-2 Tagproof Bundle Tests

Tests for the Phase-2 tagproof bundle generator and guard.
"""

import json
import pathlib
import shutil
import subprocess
import sys
from unittest.mock import patch

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[3]
FIXTURES_DIR = ROOT / "agentpm" / "tests" / "atlas" / "fixtures" / "e100"
EVIDENCE_DIR = ROOT / "evidence"
BUNDLE_SCRIPT = ROOT / "scripts" / "ci" / "tagproof_phase2_bundle.py"
GUARD_SCRIPT = ROOT / "scripts" / "guards" / "guard_tagproof_phase2.py"
BUNDLE_PATH = EVIDENCE_DIR / "tagproof_phase2_bundle.json"


def _load_fixture(name: str) -> dict:
    """Load a fixture JSON file."""
    path = FIXTURES_DIR / name
    if not path.exists():
        pytest.skip(f"Fixture {name} not found")
    return json.loads(path.read_text())


def _run_bundle_generator() -> subprocess.CompletedProcess:
    """Run the bundle generator script."""
    return subprocess.run(
        [sys.executable, str(BUNDLE_SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def _run_guard() -> subprocess.CompletedProcess:
    """Run the guard script."""
    return subprocess.run(
        [sys.executable, str(GUARD_SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_bundle_generator_creates_bundle():
    """Test that bundle generator creates a valid bundle file."""
    # Backup existing bundle if present
    backup = None
    if BUNDLE_PATH.exists():
        backup = BUNDLE_PATH.with_suffix(".json.backup")
        shutil.copy(str(BUNDLE_PATH), str(backup))

    try:
        result = _run_bundle_generator()
        assert BUNDLE_PATH.exists(), "Bundle file should be created"
        bundle = json.loads(BUNDLE_PATH.read_text())
        assert "version" in bundle
        assert "timestamp" in bundle
        assert "components" in bundle
        assert "meta" in bundle
    finally:
        if backup and backup.exists():
            shutil.copy(str(backup), str(BUNDLE_PATH))
            backup.unlink()


def test_bundle_generator_handles_missing_components():
    """Test that bundle generator handles missing components gracefully."""
    # Temporarily move evidence files
    backups = {}
    evidence_files = [
        "tv_coverage_receipt.json",
        "gatekeeper_coverage.json",
        "regenerate_all_receipt.json",
        "guard_regenerate_all.json",
        "browser_screenshot_integrated.json",
    ]

    for filename in evidence_files:
        path = EVIDENCE_DIR / filename
        if path.exists():
            backup = path.with_suffix(".json.backup")
            shutil.move(str(path), str(backup))
            backups[filename] = backup

    try:
        result = _run_bundle_generator()
        assert result.returncode == 1, "Should exit with 1 when components are missing"
        assert BUNDLE_PATH.exists(), "Bundle file should still be created"
        bundle = json.loads(BUNDLE_PATH.read_text())
        assert "components" in bundle
        # Check that missing components are marked with error
        for component_key in bundle["components"]:
            if "error" in bundle["components"][component_key]:
                assert bundle["components"][component_key]["error"] == "missing"
    finally:
        # Restore backups
        for filename, backup in backups.items():
            if backup.exists():
                shutil.move(str(backup), str(EVIDENCE_DIR / filename))


def test_guard_happy_path():
    """Test guard with all components present and ok:true."""
    # Load fixtures
    tv_coverage = _load_fixture("tv_coverage_ok.json")
    gatekeeper_coverage = _load_fixture("gatekeeper_coverage_ok.json")
    regeneration_guard = _load_fixture("regeneration_guard_ok.json")
    browser_screenshot = _load_fixture("browser_screenshot_ok.json")

    # Create a happy-path bundle
    bundle = {
        "version": 1,
        "timestamp": "2025-11-14T00:00:00Z",
        "components": {
            "tv_coverage": tv_coverage,
            "gatekeeper_coverage": gatekeeper_coverage,
            "regeneration_guard": regeneration_guard,
            "browser_screenshot": browser_screenshot,
        },
        "meta": {"phase": 2, "plan": "PLAN-080"},
    }

    # Write bundle to temp location
    backup = None
    if BUNDLE_PATH.exists():
        backup = BUNDLE_PATH.with_suffix(".json.backup")
        shutil.copy(str(BUNDLE_PATH), str(backup))

    try:
        BUNDLE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with BUNDLE_PATH.open("w") as f:
            json.dump(bundle, f)

        result = _run_guard()
        assert result.returncode == 0, "Guard should pass with all components ok"
        doc = json.loads(result.stdout)
        assert doc["ok"] is True
        assert doc["counts"]["components_ok"] == 4
        assert doc["counts"]["components_failed"] == 0
        assert doc["counts"]["components_missing"] == 0
    finally:
        if backup and backup.exists():
            shutil.copy(str(backup), str(BUNDLE_PATH))
            backup.unlink()
        elif BUNDLE_PATH.exists():
            BUNDLE_PATH.unlink()


@patch.dict("os.environ", {"STRICT_MODE": "1"}, clear=False)
def test_guard_missing_component():
    """Test guard with missing component."""
    # Load fixtures
    tv_coverage = _load_fixture("tv_coverage_ok.json")
    gatekeeper_coverage = _load_fixture("gatekeeper_coverage_ok.json")
    regeneration_guard = _load_fixture("regeneration_guard_ok.json")

    bundle = {
        "version": 1,
        "timestamp": "2025-11-14T00:00:00Z",
        "components": {
            "tv_coverage": tv_coverage,
            "gatekeeper_coverage": gatekeeper_coverage,
            "regeneration_guard": regeneration_guard,
            "browser_screenshot": {"error": "missing"},
        },
        "meta": {"phase": 2, "plan": "PLAN-080"},
    }

    # Write bundle to temp location
    backup = None
    if BUNDLE_PATH.exists():
        backup = BUNDLE_PATH.with_suffix(".json.backup")
        shutil.copy(str(BUNDLE_PATH), str(backup))

    try:
        BUNDLE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with BUNDLE_PATH.open("w") as f:
            json.dump(bundle, f)

        result = _run_guard()
        assert result.returncode == 1, "Guard should fail with missing component"
        doc = json.loads(result.stdout)
        assert doc["ok"] is False
        assert doc["counts"]["components_missing"] == 1
        assert "browser_screenshot" in doc["details"]["missing_components"]
    finally:
        if backup and backup.exists():
            shutil.copy(str(backup), str(BUNDLE_PATH))
            backup.unlink()
        elif BUNDLE_PATH.exists():
            BUNDLE_PATH.unlink()


@patch.dict("os.environ", {"STRICT_MODE": "0"}, clear=False)
def test_guard_failing_component():
    """Test guard with failing component."""
    # Load fixtures
    tv_coverage = _load_fixture("tv_coverage_ok.json")
    gatekeeper_coverage = _load_fixture("gatekeeper_coverage_ok.json")
    regeneration_guard = _load_fixture("regeneration_guard_failed.json")
    browser_screenshot = _load_fixture("browser_screenshot_ok.json")

    bundle = {
        "version": 1,
        "timestamp": "2025-11-14T00:00:00Z",
        "components": {
            "tv_coverage": tv_coverage,
            "gatekeeper_coverage": gatekeeper_coverage,
            "regeneration_guard": regeneration_guard,
            "browser_screenshot": browser_screenshot,
        },
        "meta": {"phase": 2, "plan": "PLAN-080"},
    }

    # Write bundle to temp location
    backup = None
    if BUNDLE_PATH.exists():
        backup = BUNDLE_PATH.with_suffix(".json.backup")
        shutil.copy(str(BUNDLE_PATH), str(backup))

    try:
        BUNDLE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with BUNDLE_PATH.open("w") as f:
            json.dump(bundle, f)

        result = _run_guard()
        assert result.returncode == 1, "Guard should fail with failing component"
        doc = json.loads(result.stdout)
        assert doc["ok"] is False
        assert doc["counts"]["components_failed"] > 0
        assert "regeneration_guard" in doc["details"]["component_errors"]
    finally:
        if backup and backup.exists():
            shutil.copy(str(backup), str(BUNDLE_PATH))
            backup.unlink()
        elif BUNDLE_PATH.exists():
            BUNDLE_PATH.unlink()


def test_guard_handles_missing_bundle():
    """Test that guard handles missing bundle file gracefully."""
    backup = None
    if BUNDLE_PATH.exists():
        backup = BUNDLE_PATH.with_suffix(".json.backup")
        shutil.move(str(BUNDLE_PATH), str(backup))

    try:
        result = _run_guard()
        assert result.returncode == 1, "Guard should fail when bundle is missing"
        doc = json.loads(result.stdout)
        assert doc["ok"] is False
        assert doc["checks"]["bundle_exists"] is False
    finally:
        if backup and backup.exists():
            shutil.move(str(backup), str(BUNDLE_PATH))


def test_guard_counts_consistency():
    """Test that guard counts are consistent."""
    # Use real bundle if it exists
    if not BUNDLE_PATH.exists():
        pytest.skip("Bundle file does not exist")

    result = _run_guard()
    doc = json.loads(result.stdout)

    counts = doc["counts"]
    total = counts["components_total"]
    ok = counts["components_ok"]
    failed = counts["components_failed"]
    missing = counts["components_missing"]

    assert ok + failed + missing == total, f"Counts should sum to total: {ok} + {failed} + {missing} = {total}"
