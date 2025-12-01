import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]


def _run_guard(cwd: pathlib.Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "scripts/guards/guard_browser_verification.py"],
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
    )


def test_guard_browser_verification_outputs_json_with_core_fields():
    """Test that guard emits valid JSON with required top-level fields."""
    result = _run_guard()
    assert result.stdout.strip(), f"guard emitted no stdout: {result}"
    data = json.loads(result.stdout)
    # Shape tests only; not asserting ok == True so dev/tag lanes can differ
    assert "ok" in data
    assert "checks" in data
    assert "counts" in data
    assert "details" in data


def test_guard_browser_verification_includes_required_page_metadata():
    """Test that guard includes required metadata fields in details."""
    result = _run_guard()
    data = json.loads(result.stdout)
    details = data.get("details") or {}
    # Always expect these keys in details for debugging
    assert "report_path" in details
    assert "webproof_dir" in details
    assert "missing_required_pages" in details
    assert "pages_verified" in details
    assert "core_pages_missing" in details


def test_guard_browser_verification_checks_structure():
    """Test that checks dict includes expected keys."""
    result = _run_guard()
    data = json.loads(result.stdout)
    checks = data.get("checks") or {}
    # Core checks that should always be present
    assert "webproof_dir_exists" in checks
    assert "report_exists" in checks
    assert "report_json_valid" in checks
    assert "core_pages_verified" in checks
    assert "has_screenshots" in checks


def test_guard_browser_verification_counts_structure():
    """Test that counts dict includes expected metrics."""
    result = _run_guard()
    data = json.loads(result.stdout)
    counts = data.get("counts") or {}
    # Core counts that should always be present
    assert "screenshots" in counts
    assert "required_pages" in counts
    assert "pages_verified" in counts
    assert "missing_required_pages" in counts


def test_guard_browser_verification_handles_missing_report():
    """Test that guard handles missing report.json gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = pathlib.Path(tmpdir)
        webproof_dir = tmp_path / "evidence" / "webproof"
        webproof_dir.mkdir(parents=True)

        # Create a minimal guard script that uses the temp dir
        guard_script = tmp_path / "guard_test.py"
        guard_script.write_text(
            f"""
import json
import pathlib
import sys
sys.path.insert(0, "{ROOT}")

from scripts.guards.guard_browser_verification import main

# Override ROOT to point to temp dir
import scripts.guards.guard_browser_verification as gbv
gbv.ROOT = pathlib.Path("{tmp_path}")
gbv.WEBPROOF_DIR = gbv.ROOT / "evidence" / "webproof"
gbv.REPORT_PATH = gbv.WEBPROOF_DIR / "report.json"

raise SystemExit(main())
"""
        )

        result = subprocess.run(
            [sys.executable, str(guard_script)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0, "Guard should fail when report is missing"
        data = json.loads(result.stdout)
        assert data["checks"]["report_exists"] is False
        assert data["ok"] is False


def test_guard_browser_verification_validates_core_pages():
    """Test that guard correctly identifies core pages (index, catalog)."""
    result = _run_guard()
    data = json.loads(result.stdout)

    # If report exists and is valid, core pages should be verified
    if data["checks"]["report_json_valid"]:
        # Core pages should be in either verified or missing
        details = data.get("details") or {}
        pages_verified = details.get("pages_verified", [])
        core_pages_missing = details.get("core_pages_missing", [])

        # At least one core page should be verified if report is valid
        core_pages = ["index.html", "mcp_catalog_view.html"]
        core_verified = [p for p in core_pages if p in pages_verified]
        assert len(core_verified) > 0 or len(core_pages_missing) == 0, (
            "Core pages should be verified or explicitly missing"
        )
