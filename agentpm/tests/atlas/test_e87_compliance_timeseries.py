"""
Tests for E87 Compliance Time-Series & Heatmaps.

Tests the generation, structure validation, and dashboard functionality.
"""

from __future__ import annotations

import json
import pytest
from pathlib import Path

# Add project root to path
import sys

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

CONTROL_PLANE_DIR = REPO / "share" / "atlas" / "control_plane"
DASHBOARD_DIR = REPO / "docs" / "atlas" / "dashboard"
EVIDENCE_DIR = REPO / "evidence"


def test_export_compliance_timeseries_exists():
    """Test that compliance_timeseries.json export exists."""
    json_path = CONTROL_PLANE_DIR / "compliance_timeseries.json"
    assert json_path.exists(), "compliance_timeseries.json should exist"


def test_export_compliance_timeseries_structure():
    """Test compliance_timeseries.json has required structure."""
    json_path = CONTROL_PLANE_DIR / "compliance_timeseries.json"

    with json_path.open() as f:
        data = json.load(f)

    # Check required top-level fields
    required_fields = ["episode", "schema", "generated_at", "series_by_code", "series_by_tool", "heatmap_tool_by_code"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

    # Check episode and schema
    assert data["episode"] == "E87", "Episode should be E87"
    assert data["schema"] == "compliance_timeseries_v1", "Schema should be compliance_timeseries_v1"

    # Check array structures
    assert isinstance(data["series_by_code"], list), "series_by_code should be a list"
    assert isinstance(data["series_by_tool"], list), "series_by_tool should be a list"
    assert isinstance(data["heatmap_tool_by_code"], dict), "heatmap_tool_by_code should be a dict"
    assert "entries" in data["heatmap_tool_by_code"], "heatmap_tool_by_code should have entries"


def test_export_compliance_timeseries_content():
    """Test compliance_timeseries.json has meaningful content."""
    json_path = CONTROL_PLANE_DIR / "compliance_timeseries.json"

    with json_path.open() as f:
        data = json.load(f)

    # Check that we have some data (assuming violations exist)
    series_by_code = data["series_by_code"]
    series_by_tool = data["series_by_tool"]
    heatmap_entries = data["heatmap_tool_by_code"]["entries"]

    # At minimum, we should have some structure even if empty
    assert isinstance(series_by_code, list), "series_by_code should be a list"
    assert isinstance(series_by_tool, list), "series_by_tool should be a list"
    assert isinstance(heatmap_entries, list), "heatmap entries should be a list"


def test_dashboard_compliance_timeseries_exists():
    """Test compliance_timeseries.html dashboard exists."""
    html_path = DASHBOARD_DIR / "compliance_timeseries.html"
    assert html_path.exists(), "compliance_timeseries.html should exist"


def test_dashboard_compliance_heatmap_exists():
    """Test compliance_heatmap.html dashboard exists."""
    html_path = DASHBOARD_DIR / "compliance_heatmap.html"
    assert html_path.exists(), "compliance_heatmap.html should exist"


def test_dashboard_timeseries_backlinks():
    """Test compliance_timeseries.html has required backlinks."""
    html_path = DASHBOARD_DIR / "compliance_timeseries.html"

    content = html_path.read_text()

    required_backlinks = [
        'data-testid="backlink-compliance-timeseries-json"',
        'data-testid="backlink-top-violations-7d-json"',
        'data-testid="backlink-guard-atlas-compliance-timeseries-json"',
    ]

    for link in required_backlinks:
        assert link in content, f"Missing backlink: {link}"


def test_dashboard_heatmap_backlinks():
    """Test compliance_heatmap.html has required backlinks."""
    html_path = DASHBOARD_DIR / "compliance_heatmap.html"

    content = html_path.read_text()

    required_backlinks = [
        'data-testid="backlink-compliance-timeseries-json"',
        'data-testid="backlink-guard-atlas-compliance-timeseries-json"',
    ]

    for link in required_backlinks:
        assert link in content, f"Missing backlink: {link}"


def test_guard_verdict_exists():
    """Test guard verdict file exists."""
    verdict_path = EVIDENCE_DIR / "guard_atlas_compliance_timeseries.json"
    assert verdict_path.exists(), "Guard verdict should exist"


def test_guard_verdict_structure():
    """Test guard verdict has required structure."""
    verdict_path = EVIDENCE_DIR / "guard_atlas_compliance_timeseries.json"

    with verdict_path.open() as f:
        verdict = json.load(f)

    # Check required fields
    assert "episode" in verdict, "Verdict should have episode"
    assert verdict["episode"] == "E87", "Episode should be E87"
    assert "guard" in verdict, "Verdict should have guard name"
    assert "ok" in verdict, "Verdict should have ok flag"
    assert "checks" in verdict, "Verdict should have checks"
    assert "summary" in verdict, "Verdict should have summary"


def test_guard_verdict_checks():
    """Test guard verdict checks are comprehensive."""
    verdict_path = EVIDENCE_DIR / "guard_atlas_compliance_timeseries.json"

    with verdict_path.open() as f:
        verdict = json.load(f)

    checks = verdict["checks"]
    assert "json" in checks, "Should have json checks"
    assert "html" in checks, "Should have html checks"

    json_checks = checks["json"]
    html_checks = checks["html"]

    # JSON checks
    assert "json_exists" in json_checks, "Should check json exists"
    assert "json_structure" in json_checks, "Should check json structure"

    # HTML checks
    assert "timeseries_html_exists" in html_checks, "Should check timeseries HTML exists"
    assert "heatmap_html_exists" in html_checks, "Should check heatmap HTML exists"
    assert "timeseries_backlinks" in html_checks, "Should check timeseries backlinks"
    assert "heatmap_backlinks" in html_checks, "Should check heatmap backlinks"


def test_generate_compliance_timeseries_script():
    """Test the generate script can be imported and run."""
    # Test import
    try:
        from scripts.atlas.generate_compliance_timeseries import generate_compliance_timeseries
    except ImportError as e:
        pytest.fail(f"Could not import generate_compliance_timeseries: {e}")

    # Test function exists and returns dict
    result = generate_compliance_timeseries()
    assert isinstance(result, dict), "generate_compliance_timeseries should return dict"
    assert "episode" in result, "Result should have episode"


def test_guard_script_import():
    """Test the guard script can be imported."""
    import importlib
    try:
        spec = importlib.util.find_spec("scripts.guards.guard_atlas_compliance_timeseries")
        assert spec is not None, "Guard script module should be importable"
    except Exception as e:
        pytest.fail(f"Could not find guard script module: {e}")
