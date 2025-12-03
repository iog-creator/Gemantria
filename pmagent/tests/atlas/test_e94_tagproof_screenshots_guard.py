import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]


def _run_guard(*extra_args: str) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "scripts/guards/guard_tagproof_screenshots.py", *extra_args]
    return subprocess.run(
        cmd,
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
    for key in (
        "tagproof_dirs",
        "manifest_paths",
        "unlisted_screenshots",
        "orphan_manifest_entries",
    ):
        assert key in details


def test_guard_tagproof_screenshots_writes_evidence(tmp_path: pathlib.Path):
    """Guard should be able to write an evidence JSON file when requested."""
    evidence_path = tmp_path / "guard_tagproof_screenshots.json"
    result = _run_guard("--write-evidence", str(evidence_path))
    assert result.stdout.strip(), f"guard emitted no stdout: {result}"
    assert evidence_path.exists(), "evidence file was not created"

    data = json.loads(evidence_path.read_text())
    # Evidence file should mirror core verdict structure
    assert "ok" in data
    assert "checks" in data
    assert "counts" in data
    assert "details" in data
