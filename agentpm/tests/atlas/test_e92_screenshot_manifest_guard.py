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
    result = _run_guard()
    assert result.stdout.strip(), f"guard emitted no stdout: {result}"
    data = json.loads(result.stdout)
    assert "ok" in data
    assert "checks" in data
    assert "counts" in data


def test_guard_screenshot_manifest_reports_manifest_path_when_present():
    result = _run_guard()
    data = json.loads(result.stdout)
    # We don't require ok==True here; only that when manifest exists,
    # details.manifest_path is present for debugging.
    details = data.get("details") or {}
    if data["checks"].get("manifest_exists"):
        assert "manifest_path" in details
