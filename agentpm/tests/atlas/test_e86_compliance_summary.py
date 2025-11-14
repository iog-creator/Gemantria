"""Tests for E86 Compliance Summary Dashboard."""

import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
COMPLIANCE_SUMMARY_JSON = REPO / "share" / "atlas" / "control_plane" / "compliance_summary.json"
DASHBOARD_HTML = REPO / "docs" / "atlas" / "dashboard" / "compliance_summary.html"


def test_e86_export_present():
    """E86: compliance_summary.json exists."""
    assert COMPLIANCE_SUMMARY_JSON.exists(), "compliance_summary.json must exist"


def test_e86_export_structure():
    """E86: compliance_summary.json has correct structure."""
    assert COMPLIANCE_SUMMARY_JSON.exists(), "compliance_summary.json must exist"

    with COMPLIANCE_SUMMARY_JSON.open() as f:
        data = json.load(f)

    # Check required keys
    assert "episode" in data, "Missing 'episode' key"
    assert data["episode"] == "E86", f"Wrong episode: expected E86, got {data['episode']}"

    assert "schema" in data, "Missing 'schema' key"
    assert "generated_at" in data, "Missing 'generated_at' key"
    assert "metrics" in data, "Missing 'metrics' key"

    # Check metrics structure
    metrics = data["metrics"]
    assert "total_violations" in metrics, "Missing 'total_violations' in metrics"
    assert "violations_by_code" in metrics, "Missing 'violations_by_code' in metrics"
    assert "violations_by_tool" in metrics, "Missing 'violations_by_tool' in metrics"
    assert "top_offenders" in metrics, "Missing 'top_offenders' in metrics"

    # Check total_violations structure
    total_violations = metrics["total_violations"]
    assert isinstance(total_violations, dict), "total_violations must be a dict"
    assert "24h" in total_violations, "total_violations missing '24h'"
    assert "7d" in total_violations, "total_violations missing '7d'"
    assert "30d" in total_violations, "total_violations missing '30d'"


def test_e86_dashboard_present():
    """E86: compliance_summary.html exists."""
    assert DASHBOARD_HTML.exists(), "compliance_summary.html must exist"


def test_e86_dashboard_backlinks():
    """E86: dashboard HTML has required backlinks."""
    assert DASHBOARD_HTML.exists(), "compliance_summary.html must exist"

    content = DASHBOARD_HTML.read_text()

    required_backlinks = [
        "backlink-compliance-summary-json",
        "backlink-compliance-head-json",
        "backlink-top-violations-7d-json",
        "backlink-top-violations-30d-json",
        "backlink-guard-atlas-compliance-summary-json",
    ]

    for backlink_id in required_backlinks:
        assert f'data-testid="{backlink_id}"' in content, f"Missing backlink: {backlink_id}"
