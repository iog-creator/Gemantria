"""PLAN-072 M3: M2 Visualization Hooks tests."""

from __future__ import annotations

import json
import pathlib

import pytest

from agentpm.control_widgets.adapter import load_mcp_status_cards_widget_props


def test_mcp_status_cards_widget_props_exists():
    """MCP status cards widget props function exists and is callable."""
    assert callable(load_mcp_status_cards_widget_props)


def test_mcp_status_cards_widget_props_offline_safe():
    """MCP status cards widget props returns offline-safe defaults when file missing."""
    # Temporarily rename the file if it exists
    cards_path = pathlib.Path("share/atlas/control_plane/mcp_status_cards.json")
    backup_path = pathlib.Path("share/atlas/control_plane/mcp_status_cards.json.backup")

    # Backup if exists
    if cards_path.exists():
        cards_path.rename(backup_path)

    try:
        props = load_mcp_status_cards_widget_props()

        # Verify offline-safe structure
        assert props["status"] == "unknown"
        assert "label" in props
        assert "color" in props
        assert "icon" in props
        assert "tooltip_lines" in props
        assert "metrics" in props
        assert "source" in props
        assert props["metrics"]["totalCards"] == 0
        assert props["metrics"]["okCount"] == 0
        assert props["metrics"]["failedCount"] == 0
    finally:
        # Restore if backed up
        if backup_path.exists():
            backup_path.rename(cards_path)


def test_mcp_status_cards_widget_props_valid_file():
    """MCP status cards widget props loads correctly from valid file."""
    cards_path = pathlib.Path("share/atlas/control_plane/mcp_status_cards.json")

    if not cards_path.exists():
        pytest.skip("MCP status cards file not found (run generate_mcp_status_cards.py first)")

    props = load_mcp_status_cards_widget_props()

    # Verify structure
    assert "status" in props
    assert props["status"] in ["ok", "degraded", "unknown"]
    assert "label" in props
    assert "color" in props
    assert "icon" in props
    assert "tooltip_lines" in props
    assert isinstance(props["tooltip_lines"], list)
    assert "metrics" in props
    assert "source" in props

    # Verify metrics structure
    metrics = props["metrics"]
    assert "totalCards" in metrics
    assert "okCount" in metrics
    assert "failedCount" in metrics
    assert "generatedAt" in metrics
    assert isinstance(metrics["totalCards"], int)
    assert isinstance(metrics["okCount"], int)
    assert isinstance(metrics["failedCount"], int)


def test_mcp_status_cards_json_structure():
    """MCP status cards JSON file has correct structure."""
    cards_path = pathlib.Path("share/atlas/control_plane/mcp_status_cards.json")

    if not cards_path.exists():
        pytest.skip("MCP status cards file not found (run generate_mcp_status_cards.py first)")

    data = json.loads(cards_path.read_text(encoding="utf-8"))

    # Verify schema
    assert data.get("schema") == "mcp_status_cards_v1"
    assert "generated_at" in data
    assert "ok" in data
    assert "cards" in data
    assert "summary" in data

    # Verify cards structure
    cards = data.get("cards", {})
    expected_cards = ["e21_por", "e22_schema", "e23_gatekeeper", "e24_tagproof", "e25_bundle"]
    for card_name in expected_cards:
        assert card_name in cards
        card = cards[card_name]
        assert "name" in card
        assert "status" in card
        assert "ok" in card
        assert "label" in card
        assert "color" in card
        assert "icon" in card
        assert "details" in card

    # Verify summary structure
    summary = data.get("summary", {})
    assert "total_cards" in summary
    assert "ok_count" in summary
    assert "failed_count" in summary


def test_mcp_status_cards_integration():
    """MCP status cards integration test: widget props match JSON structure."""
    cards_path = pathlib.Path("share/atlas/control_plane/mcp_status_cards.json")

    if not cards_path.exists():
        pytest.skip("MCP status cards file not found (run generate_mcp_status_cards.py first)")

    # Load raw JSON
    raw_data = json.loads(cards_path.read_text(encoding="utf-8"))

    # Load widget props
    props = load_mcp_status_cards_widget_props()

    # Verify metrics match
    summary = raw_data.get("summary", {})
    assert props["metrics"]["totalCards"] == summary.get("total_cards", 0)
    assert props["metrics"]["okCount"] == summary.get("ok_count", 0)
    assert props["metrics"]["failedCount"] == summary.get("failed_count", 0)

    # Verify status matches
    raw_ok = raw_data.get("ok", False)
    if raw_ok and summary.get("failed_count", 0) == 0:
        assert props["status"] == "ok"
    elif summary.get("failed_count", 0) > 0:
        assert props["status"] == "degraded"
