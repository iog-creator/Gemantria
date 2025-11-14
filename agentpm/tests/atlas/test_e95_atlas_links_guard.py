import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]


def _run_guard() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "scripts/guards/guard_atlas_links.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_guard_atlas_links_outputs_json_with_core_fields():
    result = _run_guard()
    assert result.stdout.strip(), f"guard emitted no stdout: {result}"
    data = json.loads(result.stdout)
    assert "ok" in data
    assert "checks" in data
    assert "counts" in data
    assert "details" in data


def test_guard_atlas_links_has_debug_lists():
    result = _run_guard()
    data = json.loads(result.stdout)
    details = data.get("details") or {}
    for key in ("broken_internal_links", "unmarked_external_links"):
        assert key in details
