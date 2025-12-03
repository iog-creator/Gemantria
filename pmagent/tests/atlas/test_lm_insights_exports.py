#!/usr/bin/env python3
"""
Tests for LM insights exports (Phase-4A).

Verifies that LM insights exports work correctly with db_off + LM-off tolerance.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scripts.db.control_lm_insights_export import (
    compute_insights,
    db_off_insights_payload,
    load_json_file,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
USAGE_PATH = REPO_ROOT / "share" / "atlas" / "control_plane" / "lm_usage_7d.json"
HEALTH_PATH = REPO_ROOT / "share" / "atlas" / "control_plane" / "lm_health_7d.json"


def test_insights_db_off() -> None:
    """Test LM insights export when DB is unavailable (db_off tolerance)."""
    # Mock missing files
    with patch("scripts.db.control_lm_insights_export.load_json_file", return_value=None):
        result = compute_insights(window_days=7)

        assert result.ok is False
        assert result.connection_ok is False
        assert result.db_off is True
        assert result.total_calls == 0
        assert result.successful_calls == 0
        assert result.failed_calls == 0
        assert result.success_rate == 0.0
        assert result.error_rate == 0.0
        assert result.top_error_reason == "db_off"
        assert result.error is not None


def test_insights_db_off_connection_false() -> None:
    """Test LM insights export when connection_ok is False."""
    usage_data = {
        "connection_ok": False,
        "error": "database error",
        "total_calls": 0,
        "successful_calls": 0,
        "failed_calls": 0,
    }
    health_data = {
        "connection_ok": False,
        "error": "database error",
        "success_rate": 0.0,
        "error_rate": 1.0,
        "error_types": {},
    }

    with patch("scripts.db.control_lm_insights_export.load_json_file") as mock_load:
        mock_load.side_effect = [usage_data, health_data]
        result = compute_insights(window_days=7)

        assert result.ok is False
        assert result.connection_ok is False
        assert result.db_off is True
        assert result.total_calls == 0
        assert result.top_error_reason == "db_off"


def test_insights_basic_counts() -> None:
    """Test LM insights export with basic counts."""
    usage_data = {
        "connection_ok": True,
        "total_calls": 100,
        "successful_calls": 80,
        "failed_calls": 20,
        "ok": True,
    }
    health_data = {
        "connection_ok": True,
        "success_rate": 0.8,
        "error_rate": 0.2,
        "error_types": {"connection_error": 15, "timeout": 5},
        "ok": True,
    }

    with patch("scripts.db.control_lm_insights_export.load_json_file") as mock_load:
        mock_load.side_effect = [usage_data, health_data]
        result = compute_insights(window_days=7)

        assert result.ok is True
        assert result.connection_ok is True
        assert result.db_off is False
        assert result.total_calls == 100
        assert result.successful_calls == 80
        assert result.failed_calls == 20
        assert result.success_rate == 0.8
        assert result.error_rate == 0.2
        assert result.top_error_reason == "connection_error"
        assert result.error is None


def test_insights_missing_breakdown() -> None:
    """Test LM insights export when backend breakdown is unavailable."""
    usage_data = {
        "connection_ok": True,
        "total_calls": 50,
        "successful_calls": 45,
        "failed_calls": 5,
        "ok": True,
    }
    health_data = {
        "connection_ok": True,
        "success_rate": 0.9,
        "error_rate": 0.1,
        "error_types": {},
        "ok": True,
    }

    with patch("scripts.db.control_lm_insights_export.load_json_file") as mock_load:
        mock_load.side_effect = [usage_data, health_data]
        result = compute_insights(window_days=7)

        assert result.ok is True
        assert result.connection_ok is True
        assert result.db_off is False
        assert result.total_calls == 50
        # Backend breakdown should be None when unavailable
        assert result.lm_studio_calls is None
        assert result.remote_calls is None
        assert result.lm_studio_usage_ratio is None
        # top_error_reason should be "unknown_error" when there are failures but no error_types
        assert result.top_error_reason == "unknown_error"


def test_insights_no_errors() -> None:
    """Test LM insights export when there are no errors."""
    usage_data = {
        "connection_ok": True,
        "total_calls": 100,
        "successful_calls": 100,
        "failed_calls": 0,
        "ok": True,
    }
    health_data = {
        "connection_ok": True,
        "success_rate": 1.0,
        "error_rate": 0.0,
        "error_types": {},
        "ok": True,
    }

    with patch("scripts.db.control_lm_insights_export.load_json_file") as mock_load:
        mock_load.side_effect = [usage_data, health_data]
        result = compute_insights(window_days=7)

        assert result.ok is True
        assert result.connection_ok is True
        assert result.db_off is False
        assert result.total_calls == 100
        assert result.successful_calls == 100
        assert result.failed_calls == 0
        assert result.success_rate == 1.0
        assert result.error_rate == 0.0
        assert result.top_error_reason is None


def test_db_off_insights_payload() -> None:
    """Test db_off_insights_payload helper function."""
    result = db_off_insights_payload("test error", window_days=7)

    assert result.ok is False
    assert result.connection_ok is False
    assert result.db_off is True
    assert result.total_calls == 0
    assert result.success_rate == 0.0
    assert result.error_rate == 0.0
    assert result.top_error_reason == "db_off"
    assert result.error == "test error"


def test_load_json_file_missing() -> None:
    """Test load_json_file with missing file."""
    result = load_json_file(Path("/nonexistent/file.json"))
    assert result is None


def test_load_json_file_invalid() -> None:
    """Test load_json_file with invalid JSON."""
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("invalid json {")
        temp_path = Path(f.name)

    try:
        result = load_json_file(temp_path)
        assert result is None
    finally:
        temp_path.unlink()
