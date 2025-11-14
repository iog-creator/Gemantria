import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
EVIDENCE_PATH = ROOT / "evidence" / "tv_coverage_receipt.json"


def _run_coverage() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "scripts/ci/tv_coverage.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def _run_guard() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "scripts/guards/guard_tv_coverage.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_tv_coverage_receipt_created_and_has_basic_shape():
    cov_result = _run_coverage()
    # Don't assert on exit code here; guard will handle failure semantics
    assert EVIDENCE_PATH.exists(), "tv_coverage_receipt.json should be created"
    data = json.loads(EVIDENCE_PATH.read_text())
    assert "ok" in data
    assert "pytest_exit_code" in data


def test_guard_tv_coverage_emits_json_with_core_fields():
    # Ensure receipt exists first
    _run_coverage()
    guard_result = _run_guard()
    assert guard_result.stdout.strip(), f"guard emitted no stdout: {guard_result}"
    doc = json.loads(guard_result.stdout)
    assert "ok" in doc
    assert "checks" in doc
    assert "counts" in doc
    assert "details" in doc
