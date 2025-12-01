#!/usr/bin/env python3
"""
Tests for LM dashboard configs (Phase-3D D2).

Verifies that dashboard configs reference correct data sources and have valid structure.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
USAGE_CONFIG = REPO_ROOT / "docs" / "atlas" / "config" / "lm_usage_dashboard.json"
HEALTH_CONFIG = REPO_ROOT / "docs" / "atlas" / "config" / "lm_health_dashboard.json"
USAGE_DATA = REPO_ROOT / "share" / "atlas" / "control_plane" / "lm_usage_7d.json"
HEALTH_DATA = REPO_ROOT / "share" / "atlas" / "control_plane" / "lm_health_7d.json"


def test_usage_dashboard_config_exists() -> None:
    """Test that usage dashboard config exists."""
    assert USAGE_CONFIG.exists(), f"Usage dashboard config missing: {USAGE_CONFIG}"


def test_health_dashboard_config_exists() -> None:
    """Test that health dashboard config exists."""
    assert HEALTH_CONFIG.exists(), f"Health dashboard config missing: {HEALTH_CONFIG}"


def test_usage_dashboard_schema() -> None:
    """Test that usage dashboard config has valid schema."""
    with open(USAGE_CONFIG, encoding="utf-8") as f:
        config = json.load(f)

    assert config.get("schema") == "atlas_dashboard", "Invalid schema"
    assert config.get("version") == "1.0", "Invalid version"
    assert config.get("title") == "LM Studio Usage (7d)", "Invalid title"
    assert (
        config.get("data_source") == "share/atlas/control_plane/lm_usage_7d.json"
    ), "Invalid data_source"
    assert config.get("db_off_safe") is True, "Must be db_off safe"
    assert "panels" in config, "Missing panels"


def test_health_dashboard_schema() -> None:
    """Test that health dashboard config has valid schema."""
    with open(HEALTH_CONFIG, encoding="utf-8") as f:
        config = json.load(f)

    assert config.get("schema") == "atlas_dashboard", "Invalid schema"
    assert config.get("version") == "1.0", "Invalid version"
    assert config.get("title") == "LM Studio Health (7d)", "Invalid title"
    assert (
        config.get("data_source") == "share/atlas/control_plane/lm_health_7d.json"
    ), "Invalid data_source"
    assert config.get("db_off_safe") is True, "Must be db_off safe"
    assert "panels" in config, "Missing panels"


def test_usage_dashboard_panels() -> None:
    """Test that usage dashboard has expected panels."""
    with open(USAGE_CONFIG, encoding="utf-8") as f:
        config = json.load(f)

    panels = config.get("panels", [])
    panel_ids = [p.get("id") for p in panels]

    assert "total_calls" in panel_ids, "Missing total_calls panel"
    assert "success_vs_failed" in panel_ids, "Missing success_vs_failed panel"
    assert "calls_by_day" in panel_ids, "Missing calls_by_day panel"
    assert "avg_latency" in panel_ids, "Missing avg_latency panel"


def test_health_dashboard_panels() -> None:
    """Test that health dashboard has expected panels."""
    with open(HEALTH_CONFIG, encoding="utf-8") as f:
        config = json.load(f)

    panels = config.get("panels", [])
    panel_ids = [p.get("id") for p in panels]

    assert "connection_status" in panel_ids, "Missing connection_status panel"
    assert "health_score" in panel_ids, "Missing health_score panel"
    assert "success_rate" in panel_ids, "Missing success_rate panel"
    assert "error_rate" in panel_ids, "Missing error_rate panel"


def test_usage_data_source_reference() -> None:
    """Test that usage dashboard references correct data source (file may not exist in CI)."""
    with open(USAGE_CONFIG, encoding="utf-8") as f:
        config = json.load(f)

    data_source = config.get("data_source")
    assert data_source == "share/atlas/control_plane/lm_usage_7d.json", "Invalid data source path"
    # Note: File may not exist in hermetic CI; that's OK (db_off safe)


def test_health_data_source_reference() -> None:
    """Test that health dashboard references correct data source (file may not exist in CI)."""
    with open(HEALTH_CONFIG, encoding="utf-8") as f:
        config = json.load(f)

    data_source = config.get("data_source")
    assert data_source == "share/atlas/control_plane/lm_health_7d.json", "Invalid data source path"
    # Note: File may not exist in hermetic CI; that's OK (db_off safe)
