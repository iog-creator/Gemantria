import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
BROWSER_JSON = REPO / "share" / "atlas" / "control_plane" / "violations_browser.json"
BROWSER_HTML = REPO / "docs" / "atlas" / "browser" / "violations.html"
GENERATOR_SCRIPT = REPO / "scripts" / "atlas" / "generate_violations_browser.py"
GUARD_SCRIPT = REPO / "scripts" / "guards" / "guard_violation_browser.py"


def test_e89_generator_script_exists():
    """Test that generator script exists."""
    assert GENERATOR_SCRIPT.exists(), f"{GENERATOR_SCRIPT} must exist"


def test_e89_browser_json_exists():
    """Test that violations_browser.json exists."""
    assert BROWSER_JSON.exists(), f"{BROWSER_JSON} must exist"


def test_e89_browser_json_structure():
    """Test that violations_browser.json has correct structure."""
    assert BROWSER_JSON.exists(), f"{BROWSER_JSON} must exist"

    with open(BROWSER_JSON) as f:
        data = json.load(f)

    # Check required keys
    required_keys = {
        "episode",
        "schema",
        "generated_at",
        "violations",
        "filters",
        "stats",
    }
    assert required_keys.issubset(data.keys()), f"Missing required keys: {required_keys - set(data.keys())}"

    # Check episode
    assert data["episode"] == "E89", f"Expected episode E89, got {data.get('episode')}"

    # Check schema
    assert data["schema"] == "violations_browser_v1", f"Expected schema violations_browser_v1, got {data.get('schema')}"

    # Check violations is a list
    assert isinstance(data["violations"], list), "violations must be a list"

    # Check filters structure
    assert isinstance(data["filters"], dict), "filters must be a dict"
    assert "tools" in data["filters"], "filters must have 'tools'"
    assert "rings" in data["filters"], "filters must have 'rings'"

    # Check stats structure
    assert isinstance(data["stats"], dict), "stats must be a dict"
    assert "total_violations" in data["stats"], "stats must have 'total_violations'"
    assert "total_count_7d" in data["stats"], "stats must have 'total_count_7d'"
    assert "total_count_30d" in data["stats"], "stats must have 'total_count_30d'"


def test_e89_browser_html_exists():
    """Test that violations.html exists."""
    assert BROWSER_HTML.exists(), f"{BROWSER_HTML} must exist"


def test_e89_browser_html_structure():
    """Test that violations.html has required structure."""
    assert BROWSER_HTML.exists(), f"{BROWSER_HTML} must exist"

    content = BROWSER_HTML.read_text()

    # Check for required backlinks
    required_backlinks = [
        "backlink-compliance-summary",
        "backlink-compliance-timeseries",
        "backlink-compliance-heatmap",
        "backlink-violations-browser-json",
        "backlink-guard-violation-browser-json",
    ]
    for backlink in required_backlinks:
        assert f'data-testid="{backlink}"' in content, f"Missing backlink: {backlink} in violations.html"

    # Check for E89 badge
    assert 'class="badge">E89' in content or 'badge">E89' in content, "Missing E89 badge"

    # Check for search/filter controls
    assert 'id="search"' in content, "Missing search input"
    assert 'id="filter-tool"' in content, "Missing tool filter"
    assert 'id="filter-ring"' in content, "Missing ring filter"
    assert 'id="sort-by"' in content, "Missing sort control"


def test_e89_guard_runs_and_reports():
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
        assert "checks" in verdict, "Guard verdict must have 'checks' field"
    except json.JSONDecodeError:
        pytest.fail(f"Guard output is not valid JSON: {proc.stdout}")
