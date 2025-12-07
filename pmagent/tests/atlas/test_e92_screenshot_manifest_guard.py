import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]


def _run_guard() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "scripts/guards/guard_screenshot_manifest.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_guard_screenshot_manifest_outputs_json_with_ok_and_checks():
    """E92: Guard outputs valid JSON with required top-level fields."""
    result = _run_guard()
    assert result.stdout.strip(), f"guard emitted no stdout: {result}"
    data = json.loads(result.stdout)
    assert "ok" in data
    assert "checks" in data
    assert "counts" in data
    assert "details" in data


def test_guard_screenshot_manifest_reports_manifest_path_when_present():
    """E92: Guard reports manifest_path in details when manifest exists."""
    result = _run_guard()
    data = json.loads(result.stdout)
    # We don't require ok==True here; only that when manifest exists,
    # details.manifest_path is present for debugging.
    details = data.get("details") or {}
    if data["checks"].get("manifest_exists"):
        assert "manifest_path" in details


def test_guard_screenshot_manifest_validates_manifest_structure():
    """E92: Guard validates manifest JSON structure and non-empty entries."""
    result = _run_guard()
    data = json.loads(result.stdout)
    checks = data.get("checks", {})

    # If manifest exists, it should be validated
    if checks.get("manifest_exists"):
        assert "manifest_json_valid" in checks
        assert "manifest_nonempty" in checks
        # If JSON is valid, entries should be counted
        if checks.get("manifest_json_valid"):
            assert "counts" in data
            assert "manifest_entries" in data["counts"]


def test_guard_screenshot_manifest_validates_hash_shape():
    """E92: Guard validates hash determinism when hash fields are present."""
    result = _run_guard()
    data = json.loads(result.stdout)
    checks = data.get("checks", {})

    # Hash shape check should always be present
    assert "hash_shape_ok" in checks
    # If manifest has entries, hash validation should be consistent
    if checks.get("manifest_nonempty"):
        assert isinstance(checks["hash_shape_ok"], bool)


def test_guard_screenshot_manifest_reports_coverage():
    """E92: Guard reports Atlas page coverage status."""
    result = _run_guard()
    data = json.loads(result.stdout)
    checks = data.get("checks", {})
    counts = data.get("counts", {})

    # Coverage checks should be present
    assert "all_atlas_pages_covered" in checks
    assert "coverage_ok" in checks
    # Counts should include coverage metrics
    if checks.get("manifest_exists"):
        assert "atlas_pages" in counts
        assert "atlas_pages_uncovered" in counts


def test_guard_screenshot_manifest_passes_with_valid_manifest():
    """E92: Guard passes (ok=true) when manifest structure and hash determinism are valid."""
    result = _run_guard()
    data = json.loads(result.stdout)

    # If manifest exists and is valid, guard should pass
    checks = data.get("checks", {})
    if checks.get("manifest_exists") and checks.get("manifest_json_valid") and checks.get("manifest_nonempty"):
        # E92 requires manifest structure + hash determinism, coverage is advisory
        required_ok = (
            checks.get("manifest_exists", False)
            and checks.get("manifest_json_valid", False)
            and checks.get("manifest_nonempty", False)
            and checks.get("hash_shape_ok", False)
            and checks.get("coverage_ok", False)
        )
        # Guard should pass if all required checks pass
        if required_ok:
            assert data.get("ok") is True, f"Guard should pass when required checks pass: {checks}"
