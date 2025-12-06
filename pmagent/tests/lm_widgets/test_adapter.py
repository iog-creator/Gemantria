"""
Comprehensive tests for LM Indicator Widget adapter.

Tests all status states, error handling, contract compliance, and hermetic behavior.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch


from pmagent.lm_widgets.adapter import (
    OFFLINE_SAFE_DEFAULT,
    load_lm_indicator_widget_props,
)


def test_adapter_healthy(tmp_path: Path) -> None:
    """Test adapter with healthy state (error_rate < 0.2)."""
    indicator_data = {
        "status": "healthy",
        "reason": "ok",
        "success_rate": 0.98,
        "error_rate": 0.02,
        "total_calls": 1000,
        "db_off": False,
        "top_error_reason": None,
        "window_days": 7,
        "generated_at": "2025-01-15T10:00:00Z",
    }

    test_file = tmp_path / "lm_indicator.json"
    test_file.write_text(json.dumps(indicator_data), encoding="utf-8")

    with patch("pmagent.lm_widgets.adapter.INDICATOR_PATH", test_file):
        props = load_lm_indicator_widget_props()

    assert props["status"] == "healthy"
    assert props["reason"] == "ok"
    assert props["color"] == "green"
    assert props["icon"] == "status-healthy"
    assert props["label"] == "LM Studio healthy"
    assert props["metrics"]["successRate"] == 0.98
    assert props["metrics"]["errorRate"] == 0.02
    assert props["metrics"]["totalCalls"] == 1000
    assert props["metrics"]["dbOff"] is False
    assert "Total calls: 1,000" in props["tooltip_lines"]
    assert "Success rate: 98.0%" in props["tooltip_lines"]


def test_adapter_degraded(tmp_path: Path) -> None:
    """Test adapter with degraded state (error_rate >= 0.2, < 0.5)."""
    indicator_data = {
        "status": "degraded",
        "reason": "high_error_rate",
        "success_rate": 0.75,
        "error_rate": 0.25,
        "total_calls": 500,
        "db_off": False,
        "top_error_reason": "timeout",
        "window_days": 7,
        "generated_at": "2025-01-15T10:00:00Z",
    }

    test_file = tmp_path / "lm_indicator.json"
    test_file.write_text(json.dumps(indicator_data), encoding="utf-8")

    with patch("pmagent.lm_widgets.adapter.INDICATOR_PATH", test_file):
        props = load_lm_indicator_widget_props()

    assert props["status"] == "degraded"
    assert props["reason"] == "high_error_rate"
    assert props["color"] == "yellow"
    assert props["icon"] == "status-degraded"
    assert props["label"] == "LM Studio degraded (high error rate)"
    assert props["metrics"]["errorRate"] == 0.25
    assert "Error rate: 25.0%" in props["tooltip_lines"]
    assert "Top error: timeout" in props["tooltip_lines"]


def test_adapter_degraded_red(tmp_path: Path) -> None:
    """Test adapter with degraded state and error_rate >= 0.5 (red color)."""
    indicator_data = {
        "status": "degraded",
        "reason": "high_error_rate",
        "success_rate": 0.4,
        "error_rate": 0.6,
        "total_calls": 200,
        "db_off": False,
        "top_error_reason": "connection_error",
        "window_days": 7,
        "generated_at": "2025-01-15T10:00:00Z",
    }

    test_file = tmp_path / "lm_indicator.json"
    test_file.write_text(json.dumps(indicator_data), encoding="utf-8")

    with patch("pmagent.lm_widgets.adapter.INDICATOR_PATH", test_file):
        props = load_lm_indicator_widget_props()

    assert props["status"] == "degraded"
    assert props["color"] == "red"  # Red for error_rate >= 0.5
    assert props["metrics"]["errorRate"] == 0.6


def test_adapter_offline_db_off(tmp_path: Path) -> None:
    """Test adapter with offline state and db_off=true."""
    indicator_data = {
        "status": "offline",
        "reason": "db_off",
        "success_rate": 0.0,
        "error_rate": 0.0,
        "total_calls": 0,
        "db_off": True,
        "top_error_reason": "db_off",
        "window_days": 7,
        "generated_at": "2025-01-15T10:00:00Z",
    }

    test_file = tmp_path / "lm_indicator.json"
    test_file.write_text(json.dumps(indicator_data), encoding="utf-8")

    with patch("pmagent.lm_widgets.adapter.INDICATOR_PATH", test_file):
        props = load_lm_indicator_widget_props()

    assert props["status"] == "offline"
    assert props["reason"] == "db_off"
    assert props["color"] == "grey"
    assert props["icon"] == "status-offline"
    assert props["label"] == "LM Studio offline (database unavailable)"
    assert props["metrics"]["dbOff"] is True
    assert "Database unavailable" in props["tooltip_lines"]


def test_adapter_offline_no_calls(tmp_path: Path) -> None:
    """Test adapter with offline state and total_calls=0."""
    indicator_data = {
        "status": "offline",
        "reason": "no_calls",
        "success_rate": 0.0,
        "error_rate": 0.0,
        "total_calls": 0,
        "db_off": False,
        "top_error_reason": None,
        "window_days": 7,
        "generated_at": "2025-01-15T10:00:00Z",
    }

    test_file = tmp_path / "lm_indicator.json"
    test_file.write_text(json.dumps(indicator_data), encoding="utf-8")

    with patch("pmagent.lm_widgets.adapter.INDICATOR_PATH", test_file):
        props = load_lm_indicator_widget_props()

    assert props["status"] == "offline"
    assert props["reason"] == "no_calls"
    assert props["label"] == "LM Studio offline (no recent activity)"
    assert "No recent LM Studio activity" in props["tooltip_lines"]


def test_adapter_missing_file(tmp_path: Path) -> None:
    """Test adapter when indicator file is missing."""
    # Create a non-existent file path
    non_existent_file = tmp_path / "nonexistent.json"

    with patch("pmagent.lm_widgets.adapter.INDICATOR_PATH", non_existent_file):
        props = load_lm_indicator_widget_props()

    assert props == OFFLINE_SAFE_DEFAULT
    assert props["status"] == "offline"
    assert props["reason"] == "db_off"
    assert props["color"] == "grey"


def test_adapter_invalid_json(tmp_path: Path) -> None:
    """Test adapter with invalid JSON content."""
    test_file = tmp_path / "lm_indicator.json"
    test_file.write_text("invalid json content {", encoding="utf-8")

    with patch("pmagent.lm_widgets.adapter.INDICATOR_PATH", test_file):
        props = load_lm_indicator_widget_props()

    assert props == OFFLINE_SAFE_DEFAULT


def test_adapter_missing_fields(tmp_path: Path) -> None:
    """Test adapter with partial JSON (missing fields)."""
    indicator_data = {
        "status": "healthy",
        "reason": "ok",
        # Missing other fields
    }

    test_file = tmp_path / "lm_indicator.json"
    test_file.write_text(json.dumps(indicator_data), encoding="utf-8")

    with patch("pmagent.lm_widgets.adapter.INDICATOR_PATH", test_file):
        props = load_lm_indicator_widget_props()

    # Should use safe defaults for missing fields
    assert props["status"] == "healthy"
    assert props["reason"] == "ok"
    assert props["metrics"]["successRate"] is None
    assert props["metrics"]["errorRate"] is None
    assert props["metrics"]["totalCalls"] is None
    assert props["metrics"]["dbOff"] is True  # Default for missing db_off
    assert props["metrics"]["windowDays"] == 7  # Default


def test_adapter_widget_contract_compliance(tmp_path: Path) -> None:
    """Test that adapter returns all required contract fields."""
    indicator_data = {
        "status": "healthy",
        "reason": "ok",
        "success_rate": 0.95,
        "error_rate": 0.05,
        "total_calls": 100,
        "db_off": False,
        "top_error_reason": None,
        "window_days": 7,
        "generated_at": "2025-01-15T10:00:00Z",
    }

    test_file = tmp_path / "lm_indicator.json"
    test_file.write_text(json.dumps(indicator_data), encoding="utf-8")

    with patch("pmagent.lm_widgets.adapter.INDICATOR_PATH", test_file):
        props = load_lm_indicator_widget_props()

    # Verify all required fields present
    assert "status" in props
    assert "reason" in props
    assert "label" in props
    assert "color" in props
    assert "icon" in props
    assert "tooltip_lines" in props
    assert "metrics" in props
    assert "source" in props

    # Verify metrics structure
    metrics = props["metrics"]
    assert "successRate" in metrics
    assert "errorRate" in metrics
    assert "totalCalls" in metrics
    assert "dbOff" in metrics
    assert "topErrorReason" in metrics
    assert "windowDays" in metrics
    assert "generatedAt" in metrics

    # Verify source structure
    assert "path" in props["source"]


def test_adapter_color_mapping(tmp_path: Path) -> None:
    """Test color mapping for all statuses."""
    test_cases = [
        ("offline", "db_off", 0.0, "grey"),
        ("healthy", "ok", 0.1, "green"),
        ("degraded", "high_error_rate", 0.3, "yellow"),
        ("degraded", "high_error_rate", 0.6, "red"),
    ]

    for status, reason, error_rate, expected_color in test_cases:
        indicator_data = {
            "status": status,
            "reason": reason,
            "success_rate": 1.0 - error_rate,
            "error_rate": error_rate,
            "total_calls": 100,
            "db_off": False,
            "top_error_reason": None,
            "window_days": 7,
            "generated_at": "2025-01-15T10:00:00Z",
        }

        test_file = tmp_path / f"lm_indicator_{status}_{reason}.json"
        test_file.write_text(json.dumps(indicator_data), encoding="utf-8")

        with patch("pmagent.lm_widgets.adapter.INDICATOR_PATH", test_file):
            props = load_lm_indicator_widget_props()

        assert props["color"] == expected_color, f"Failed for {status}/{reason}/{error_rate}"


def test_adapter_icon_mapping(tmp_path: Path) -> None:
    """Test icon mapping for all statuses."""
    test_cases = [
        ("offline", "status-offline"),
        ("healthy", "status-healthy"),
        ("degraded", "status-degraded"),
    ]

    for status, expected_icon in test_cases:
        indicator_data = {
            "status": status,
            "reason": "ok" if status == "healthy" else "db_off",
            "success_rate": 0.9,
            "error_rate": 0.1,
            "total_calls": 100,
            "db_off": False,
            "top_error_reason": None,
            "window_days": 7,
            "generated_at": "2025-01-15T10:00:00Z",
        }

        test_file = tmp_path / f"lm_indicator_{status}.json"
        test_file.write_text(json.dumps(indicator_data), encoding="utf-8")

        with patch("pmagent.lm_widgets.adapter.INDICATOR_PATH", test_file):
            props = load_lm_indicator_widget_props()

        assert props["icon"] == expected_icon, f"Failed for {status}"


def test_adapter_tooltip_generation(tmp_path: Path) -> None:
    """Test tooltip_lines format and content."""
    indicator_data = {
        "status": "degraded",
        "reason": "high_error_rate",
        "success_rate": 0.7,
        "error_rate": 0.3,
        "total_calls": 500,
        "db_off": False,
        "top_error_reason": "timeout",
        "window_days": 7,
        "generated_at": "2025-01-15T10:00:00Z",
    }

    test_file = tmp_path / "lm_indicator.json"
    test_file.write_text(json.dumps(indicator_data), encoding="utf-8")

    with patch("pmagent.lm_widgets.adapter.INDICATOR_PATH", test_file):
        props = load_lm_indicator_widget_props()

    # Verify tooltip_lines is a list
    assert isinstance(props["tooltip_lines"], list)
    assert len(props["tooltip_lines"]) > 0

    # Verify content includes key metrics
    tooltip_text = " ".join(props["tooltip_lines"])
    assert "Total calls" in tooltip_text or "500" in tooltip_text
    assert "Error rate" in tooltip_text or "30.0%" in tooltip_text
    assert "Top error: timeout" in props["tooltip_lines"]
    assert "Window: 7 days" in props["tooltip_lines"]


def test_adapter_metrics_transformation(tmp_path: Path) -> None:
    """Test snake_case to camelCase conversion for metrics."""
    indicator_data = {
        "status": "healthy",
        "reason": "ok",
        "success_rate": 0.98,
        "error_rate": 0.02,
        "total_calls": 1000,
        "db_off": False,
        "top_error_reason": "network_error",
        "window_days": 7,
        "generated_at": "2025-01-15T10:00:00Z",
    }

    test_file = tmp_path / "lm_indicator.json"
    test_file.write_text(json.dumps(indicator_data), encoding="utf-8")

    with patch("pmagent.lm_widgets.adapter.INDICATOR_PATH", test_file):
        props = load_lm_indicator_widget_props()

    metrics = props["metrics"]
    # Verify camelCase transformation
    assert "successRate" in metrics  # snake_case → camelCase
    assert "errorRate" in metrics
    assert "totalCalls" in metrics
    assert "dbOff" in metrics
    assert "topErrorReason" in metrics
    assert "windowDays" in metrics
    assert "generatedAt" in metrics

    # Verify values preserved
    assert metrics["successRate"] == 0.98
    assert metrics["errorRate"] == 0.02
    assert metrics["totalCalls"] == 1000
    assert metrics["dbOff"] is False
    assert metrics["topErrorReason"] == "network_error"
    assert metrics["windowDays"] == 7
    assert metrics["generatedAt"] == "2025-01-15T10:00:00Z"


def test_adapter_hermetic(tmp_path: Path) -> None:
    """Test that adapter is hermetic (no DB/LM calls)."""
    # This test verifies that the adapter doesn't make external calls
    # by using file operations only and ensuring no exceptions from
    # missing DB/LM dependencies

    indicator_data = {
        "status": "healthy",
        "reason": "ok",
        "success_rate": 0.95,
        "error_rate": 0.05,
        "total_calls": 100,
        "db_off": False,
        "top_error_reason": None,
        "window_days": 7,
        "generated_at": "2025-01-15T10:00:00Z",
    }

    test_file = tmp_path / "lm_indicator.json"
    test_file.write_text(json.dumps(indicator_data), encoding="utf-8")

    # Use file operations - no DB/LM imports should be needed
    with patch("pmagent.lm_widgets.adapter.INDICATOR_PATH", test_file):
        # Should not raise any import errors or connection errors
        props = load_lm_indicator_widget_props()

    # Verify it works without any external dependencies
    assert props["status"] == "healthy"
    # No DB connection, no LM Studio API calls - purely file-based
