import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]


def _run_guard() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "scripts/guards/guard_browser_verification.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_guard_browser_verification_outputs_json_with_core_fields():
    result = _run_guard()
    assert result.stdout.strip(), f"guard emitted no stdout: {result}"
    data = json.loads(result.stdout)
    # Shape tests only; not asserting ok == True so dev/tag lanes can differ
    assert "ok" in data
    assert "checks" in data
    assert "counts" in data
    assert "details" in data


def test_guard_browser_verification_includes_required_page_metadata():
    result = _run_guard()
    data = json.loads(result.stdout)
    details = data.get("details") or {}
    # Always expect these keys in details for debugging
    assert "report_path" in details
    assert "webproof_dir" in details
    assert "missing_required_pages" in details
