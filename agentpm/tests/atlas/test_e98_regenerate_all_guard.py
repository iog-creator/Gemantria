import json
import pathlib
import subprocess
import sys
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[3]
RECEIPT_PATH = ROOT / "evidence" / "regenerate_all_receipt.json"
FIXTURE_RECEIPT = ROOT / "agentpm" / "tests" / "atlas" / "fixtures" / "e98" / "sample_receipt.json"


def _run_guard() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "scripts/guards/guard_regenerate_all.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_guard_regenerate_all_emits_json_with_core_fields():
    """Test that guard emits JSON with required fields."""
    result = _run_guard()
    assert result.stdout.strip(), f"guard emitted no stdout: {result}"
    doc = json.loads(result.stdout)
    assert "ok" in doc
    assert "checks" in doc
    assert "counts" in doc
    assert "details" in doc


def test_guard_regenerate_all_handles_missing_receipt():
    """Test that guard handles missing receipt gracefully."""
    # Temporarily move receipt if it exists
    backup = None
    if RECEIPT_PATH.exists():
        backup = RECEIPT_PATH.with_suffix(".json.backup")
        shutil.move(str(RECEIPT_PATH), str(backup))

    try:
        result = _run_guard()
        doc = json.loads(result.stdout)
        assert doc["ok"] is False
        assert doc["checks"]["receipt_exists"] is False
    finally:
        # Restore receipt if it was moved
        if backup and backup.exists():
            shutil.move(str(backup), str(RECEIPT_PATH))


def test_guard_regenerate_all_validates_receipt_structure():
    """Test that guard validates receipt structure."""
    result = _run_guard()
    doc = json.loads(result.stdout)
    # If receipt exists, it should be validated
    if doc["checks"].get("receipt_exists"):
        assert "receipt_json_valid" in doc["checks"]
        assert "receipt_ok_flag" in doc["checks"]
