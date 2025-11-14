import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
COMPLIANCE_JSON = REPO / "share" / "atlas" / "control_plane" / "graph_compliance.json"
COMPLIANCE_HTML = REPO / "docs" / "atlas" / "dashboard" / "graph_compliance.html"
GENERATOR_SCRIPT = REPO / "scripts" / "db" / "control_graph_compliance_metrics_export.py"
GUARD_SCRIPT = REPO / "scripts" / "guards" / "guard_graph_compliance.py"


def test_e90_generator_script_exists():
    """Test that generator script exists."""
    assert GENERATOR_SCRIPT.exists(), f"{GENERATOR_SCRIPT} must exist"


def test_e90_graph_compliance_json_exists():
    """Test that graph_compliance.json exists."""
    assert COMPLIANCE_JSON.exists(), f"{COMPLIANCE_JSON} must exist"


def test_e90_graph_compliance_json_structure():
    """Test that graph_compliance.json has correct structure."""
    assert COMPLIANCE_JSON.exists(), f"{COMPLIANCE_JSON} must exist"

    with open(COMPLIANCE_JSON) as f:
        data = json.load(f)

    # Check required keys
    required_keys = {
        "episode",
        "schema",
        "generated_at",
        "summary",
        "details",
    }
    assert required_keys.issubset(data.keys()), f"Missing required keys: {required_keys - set(data.keys())}"

    # Check episode
    assert data["episode"] == "E90", f"Expected episode E90, got {data.get('episode')}"

    # Check schema
    assert data["schema"] == "graph_compliance_v1", f"Expected schema graph_compliance_v1, got {data.get('schema')}"

    # Check summary structure
    assert isinstance(data["summary"], dict), "summary must be a dict"
    required_summary_keys = {"nodes", "patterns", "tools", "batches"}
    assert required_summary_keys.issubset(data["summary"].keys()), (
        f"summary missing keys: {required_summary_keys - set(data['summary'].keys())}"
    )

    # Check details is a list
    assert isinstance(data["details"], list), "details must be a list"


def test_e90_graph_compliance_html_exists():
    """Test that graph_compliance.html exists."""
    assert COMPLIANCE_HTML.exists(), f"{COMPLIANCE_HTML} must exist"


def test_e90_graph_compliance_html_structure():
    """Test that graph_compliance.html has required structure."""
    assert COMPLIANCE_HTML.exists(), f"{COMPLIANCE_HTML} must exist"

    content = COMPLIANCE_HTML.read_text()

    # Check for required backlinks
    required_backlinks = [
        "backlink-graph-compliance-json",
        "backlink-compliance-summary-json",
        "backlink-guard-graph-compliance-json",
        "backlink-compliance-summary-dashboard",
        "backlink-compliance-timeseries-dashboard",
    ]
    for backlink in required_backlinks:
        assert f'data-testid="{backlink}"' in content, f"Missing backlink: {backlink} in graph_compliance.html"

    # Check for E90 badge
    assert 'class="badge">E90' in content or 'badge">E90' in content, "Missing E90 badge"

    # Check for Chart.js
    assert "chart.js" in content.lower() or "chart.umd" in content.lower(), "Missing Chart.js reference"

    # Check for canvas element
    assert 'id="complianceChart"' in content, "Missing compliance chart canvas"


def test_e90_guard_runs_and_reports():
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
