import os
import json
import pytest

EXPORT = "share/atlas/control_plane/compliance_timeseries.json"
HTML_TS = "docs/atlas/dashboard/compliance_timeseries.html"
HTML_HM = "docs/atlas/dashboard/compliance_heatmap.html"


def test_e87_export_present():
    """Test that compliance_timeseries.json exists."""
    assert os.path.exists(EXPORT), f"{EXPORT} must exist"


def test_e87_export_structure():
    """Test that compliance_timeseries.json has correct structure."""
    assert os.path.exists(EXPORT), f"{EXPORT} must exist"

    with open(EXPORT) as f:
        data = json.load(f)

    # Check required keys
    required_keys = {
        "episode",
        "schema",
        "generated_at",
        "series_by_code",
        "series_by_tool",
        "heatmap",
    }
    assert required_keys.issubset(data.keys()), f"Missing required keys: {required_keys - set(data.keys())}"

    # Check episode
    assert data["episode"] == "E87", f"Expected episode E87, got {data.get('episode')}"

    # Check schema
    assert data["schema"] == "compliance_timeseries_v1", (
        f"Expected schema compliance_timeseries_v1, got {data.get('schema')}"
    )

    # Check series_by_code is a list
    assert isinstance(data["series_by_code"], list), "series_by_code must be a list"

    # Check series_by_tool is a list
    assert isinstance(data["series_by_tool"], list), "series_by_tool must be a list"

    # Check heatmap is a list
    assert isinstance(data["heatmap"], list), "heatmap must be a list"


def test_e87_html_timeseries_present():
    """Test that compliance_timeseries.html exists and has required elements."""
    assert os.path.exists(HTML_TS), f"{HTML_TS} must exist"

    with open(HTML_TS) as f:
        content = f.read()

    # Check for required backlinks
    required_backlinks = [
        "backlink-compliance-timeseries-json",
        "backlink-compliance-head-json",
        "backlink-top-violations-7d-json",
        "backlink-top-violations-30d-json",
        "backlink-guard-atlas-compliance-timeseries-json",
    ]
    for backlink in required_backlinks:
        assert f'data-testid="{backlink}"' in content, f"Missing backlink: {backlink}"

    # Check for Chart.js
    assert "chart.js" in content.lower() or "chart.umd" in content.lower(), "Missing Chart.js library"

    # Check for canvas elements
    assert "<canvas" in content, "Missing canvas elements for charts"


def test_e87_html_heatmap_present():
    """Test that compliance_heatmap.html exists and has required elements."""
    assert os.path.exists(HTML_HM), f"{HTML_HM} must exist"

    with open(HTML_HM) as f:
        content = f.read()

    # Check for required backlinks
    required_backlinks = [
        "backlink-compliance-timeseries-json",
        "backlink-compliance-head-json",
        "backlink-top-violations-7d-json",
        "backlink-top-violations-30d-json",
        "backlink-guard-atlas-compliance-timeseries-json",
    ]
    for backlink in required_backlinks:
        assert f'data-testid="{backlink}"' in content, f"Missing backlink: {backlink}"

    # Check for Chart.js
    assert "chart.js" in content.lower() or "chart.umd" in content.lower(), "Missing Chart.js library"

    # Check for canvas elements
    assert "<canvas" in content, "Missing canvas elements for charts"


def test_e87_guard_runs_and_reports():
    """Test that guard script runs and reports correctly."""
    from subprocess import run

    proc = run(
        ["python3", "scripts/guards/guard_compliance_timeseries_backlinks.py"],
        capture_output=True,
        text=True,
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
    except json.JSONDecodeError:
        pytest.fail(f"Guard output is not valid JSON: {proc.stdout}")
