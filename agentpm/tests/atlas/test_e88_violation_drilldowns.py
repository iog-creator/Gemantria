import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
VIOLATIONS_DIR = REPO / "docs" / "atlas" / "webproof" / "violations"
GENERATOR_SCRIPT = REPO / "scripts" / "atlas" / "generate_violation_pages.py"
GUARD_SCRIPT = REPO / "scripts" / "guards" / "guard_compliance_drilldowns.py"


def test_e88_generator_script_exists():
    """Test that generator script exists."""
    assert GENERATOR_SCRIPT.exists(), f"{GENERATOR_SCRIPT} must exist"


def test_e88_violations_directory_exists():
    """Test that violations directory exists."""
    assert VIOLATIONS_DIR.exists(), f"{VIOLATIONS_DIR} must exist"


def test_e88_violation_pages_generated():
    """Test that at least one violation page exists."""
    if not VIOLATIONS_DIR.exists():
        pytest.skip("Violations directory does not exist (run generator first)")

    pages = list(VIOLATIONS_DIR.glob("*.html"))
    assert len(pages) > 0, "At least one violation page must exist"


def test_e88_violation_page_structure():
    """Test that violation pages have required structure."""
    if not VIOLATIONS_DIR.exists():
        pytest.skip("Violations directory does not exist")

    pages = list(VIOLATIONS_DIR.glob("*.html"))
    if not pages:
        pytest.skip("No violation pages found")

    # Check first page
    page_path = pages[0]
    content = page_path.read_text()

    # Check for required backlinks
    required_backlinks = [
        "backlink-node-page",
        "backlink-pattern-page",
        "backlink-guard-receipt",
        "backlink-compliance-summary",
        "backlink-compliance-timeseries",
    ]
    for backlink in required_backlinks:
        assert f'data-testid="{backlink}"' in content, f"Missing backlink: {backlink} in {page_path.name}"

    # Check for E88 badge
    assert 'class="badge">E88' in content or 'badge">E88' in content, "Missing E88 badge"


def test_e88_guard_runs_and_reports():
    """Test that guard script runs and reports correctly."""
    from subprocess import run

    proc = run(
        ["python3", str(GUARD_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )

    # Guard should exit 0 (success) or 1 (failure), not crash
    assert proc.returncode in (0, 1), f"Guard exited with unexpected code: {proc.returncode}"

    # Guard should output JSON
    assert proc.stdout.strip() != "", "Guard must output JSON verdict"

    # Parse JSON output
    try:
        verdict = json.loads(proc.stdout.strip())
        assert "ok" in verdict, "Guard verdict must have 'ok' field"
        assert "errors" in verdict, "Guard verdict must have 'errors' field"
        assert "violations_checked" in verdict, "Guard verdict must have 'violations_checked' field"
        assert "pages_found" in verdict, "Guard verdict must have 'pages_found' field"
    except json.JSONDecodeError:
        pytest.fail(f"Guard output is not valid JSON: {proc.stdout}")
