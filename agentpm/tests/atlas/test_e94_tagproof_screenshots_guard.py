import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]


def _run_guard() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "scripts/guards/guard_tagproof_screenshots.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_guard_tagproof_screenshots_outputs_core_fields():
    result = _run_guard()
    assert result.stdout.strip(), f"guard emitted no stdout: {result}"
    data = json.loads(result.stdout)
    assert "ok" in data
    assert "checks" in data
    assert "counts" in data
    assert "details" in data


def test_guard_tagproof_screenshots_includes_debug_lists():
    result = _run_guard()
    data = json.loads(result.stdout)
    details = data.get("details") or {}
    # These keys should always be present to help debug STRICT failures
    for key in ("tagproof_dirs", "manifest_paths", "unlisted_screenshots", "orphan_manifest_entries"):
        assert key in details
