import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
COVERAGE_PATH = ROOT / "evidence" / "gatekeeper_coverage.json"


def _run_coverage() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "scripts/ci/gatekeeper_coverage.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def _run_guard() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "scripts/guards/guard_gatekeeper_coverage.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_gatekeeper_coverage_manifest_created_and_has_shape():
    _run_coverage()
    assert COVERAGE_PATH.exists(), "gatekeeper_coverage.json should be created"
    data = json.loads(COVERAGE_PATH.read_text(encoding="utf-8"))
    assert "violation_codes" in data
    assert "coverage" in data


def test_guard_gatekeeper_coverage_emits_json_with_core_fields():
    _run_coverage()
    result = _run_guard()
    assert result.stdout.strip(), f"guard emitted no stdout: {result}"
    doc = json.loads(result.stdout)
    assert "ok" in doc
    assert "checks" in doc
    assert "counts" in doc
    assert "details" in doc
