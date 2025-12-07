#!/usr/bin/env python3
"""
Tests for LM indicator export (Phase-4C).

Verifies that the indicator export correctly derives status from insights
and handles db_off, no_calls, high_error_rate, and healthy states.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[3]
INDICATOR_SCRIPT = REPO_ROOT / "scripts" / "db" / "control_lm_indicator_export.py"
OUT_DIR = REPO_ROOT / "share" / "atlas" / "control_plane"
INSIGHTS_PATH = OUT_DIR / "lm_insights_7d.json"
OUT_INDICATOR_PATH = OUT_DIR / "lm_indicator.json"


def test_indicator_script_exists() -> None:
    """Test that indicator export script exists."""
    assert INDICATOR_SCRIPT.exists(), f"Indicator script missing: {INDICATOR_SCRIPT}"


def test_indicator_db_off() -> None:
    """Test indicator with db_off=true → status='offline', reason='db_off'."""
    # Import the compute_indicator function
    import sys
    import importlib.util

    spec = importlib.util.spec_from_file_location("indicator_export", INDICATOR_SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["indicator_export"] = module
    spec.loader.exec_module(module)

    # Mock insights data with db_off=true
    insights_data = {
        "schema": "control",
        "generated_at": datetime.now(UTC).isoformat(),
        "window_days": 7,
        "since": datetime.now(UTC).isoformat(),
        "ok": False,
        "connection_ok": False,
        "db_off": True,
        "total_calls": 0,
        "successful_calls": 0,
        "failed_calls": 0,
        "success_rate": 0.0,
        "error_rate": 0.0,
        "top_error_reason": "db_off",
    }

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch(
            "pathlib.Path.read_text",
            return_value=json.dumps(insights_data),
        ),
    ):
        indicator = module.compute_indicator()

    assert indicator.status == "offline"
    assert indicator.reason == "db_off"
    assert indicator.db_off is True
    assert indicator.total_calls == 0
    assert indicator.success_rate == 0.0
    assert indicator.error_rate == 0.0
    assert indicator.top_error_reason == "db_off"


def test_indicator_no_calls() -> None:
    """Test indicator with db_off=false, total_calls=0 → status='offline', reason='no_calls'."""
    import sys
    import importlib.util

    spec = importlib.util.spec_from_file_location("indicator_export", INDICATOR_SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["indicator_export"] = module
    spec.loader.exec_module(module)

    insights_data = {
        "schema": "control",
        "generated_at": datetime.now(UTC).isoformat(),
        "window_days": 7,
        "since": datetime.now(UTC).isoformat(),
        "ok": True,
        "connection_ok": True,
        "db_off": False,
        "total_calls": 0,
        "successful_calls": 0,
        "failed_calls": 0,
        "success_rate": 0.0,
        "error_rate": 0.0,
        "top_error_reason": None,
    }

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch(
            "pathlib.Path.read_text",
            return_value=json.dumps(insights_data),
        ),
    ):
        indicator = module.compute_indicator()

    assert indicator.status == "offline"
    assert indicator.reason == "no_calls"
    assert indicator.db_off is False
    assert indicator.total_calls == 0


def test_indicator_high_error_rate() -> None:
    """Test indicator with error_rate>=0.2 → status='degraded', reason='high_error_rate'."""
    import sys
    import importlib.util

    spec = importlib.util.spec_from_file_location("indicator_export", INDICATOR_SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["indicator_export"] = module
    spec.loader.exec_module(module)

    insights_data = {
        "schema": "control",
        "generated_at": datetime.now(UTC).isoformat(),
        "window_days": 7,
        "since": datetime.now(UTC).isoformat(),
        "ok": True,
        "connection_ok": True,
        "db_off": False,
        "total_calls": 100,
        "successful_calls": 70,
        "failed_calls": 30,
        "success_rate": 0.7,
        "error_rate": 0.3,  # >= 0.2 threshold
        "top_error_reason": "timeout",
    }

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch(
            "pathlib.Path.read_text",
            return_value=json.dumps(insights_data),
        ),
    ):
        indicator = module.compute_indicator()

    assert indicator.status == "degraded"
    assert indicator.reason == "high_error_rate"
    assert indicator.db_off is False
    assert indicator.total_calls == 100
    assert indicator.success_rate == 0.7
    assert indicator.error_rate == 0.3
    assert indicator.top_error_reason == "timeout"


def test_indicator_healthy() -> None:
    """Test indicator with error_rate<0.2 → status='healthy', reason='ok'."""
    import sys
    import importlib.util

    spec = importlib.util.spec_from_file_location("indicator_export", INDICATOR_SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["indicator_export"] = module
    spec.loader.exec_module(module)

    insights_data = {
        "schema": "control",
        "generated_at": datetime.now(UTC).isoformat(),
        "window_days": 7,
        "since": datetime.now(UTC).isoformat(),
        "ok": True,
        "connection_ok": True,
        "db_off": False,
        "total_calls": 1000,
        "successful_calls": 980,
        "failed_calls": 20,
        "success_rate": 0.98,
        "error_rate": 0.02,  # < 0.2 threshold
        "top_error_reason": None,
    }

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch(
            "pathlib.Path.read_text",
            return_value=json.dumps(insights_data),
        ),
    ):
        indicator = module.compute_indicator()

    assert indicator.status == "healthy"
    assert indicator.reason == "ok"
    assert indicator.db_off is False
    assert indicator.total_calls == 1000
    assert indicator.success_rate == 0.98
    assert indicator.error_rate == 0.02
    assert indicator.window_days == 7
    assert indicator.generated_at is not None
    assert len(indicator.generated_at) > 0  # Should be ISO timestamp


def test_indicator_missing_insights_file() -> None:
    """Test indicator when insights file is missing → emits offline indicator."""
    import sys
    import importlib.util

    spec = importlib.util.spec_from_file_location("indicator_export", INDICATOR_SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["indicator_export"] = module
    spec.loader.exec_module(module)

    with patch("pathlib.Path.exists", return_value=False):
        indicator = module.compute_indicator()

    assert indicator.status == "offline"
    assert indicator.reason == "db_off"
    assert indicator.db_off is True
    assert indicator.total_calls == 0
    assert indicator.success_rate == 0.0
    assert indicator.error_rate == 0.0


def test_indicator_all_keys_present() -> None:
    """Test that indicator export includes all required keys."""
    import sys
    import importlib.util

    spec = importlib.util.spec_from_file_location("indicator_export", INDICATOR_SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["indicator_export"] = module
    spec.loader.exec_module(module)

    insights_data = {
        "schema": "control",
        "generated_at": datetime.now(UTC).isoformat(),
        "window_days": 7,
        "since": datetime.now(UTC).isoformat(),
        "ok": True,
        "connection_ok": True,
        "db_off": False,
        "total_calls": 500,
        "successful_calls": 490,
        "failed_calls": 10,
        "success_rate": 0.98,
        "error_rate": 0.02,
        "top_error_reason": "network_error",
    }

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch(
            "pathlib.Path.read_text",
            return_value=json.dumps(insights_data),
        ),
    ):
        indicator = module.compute_indicator()

    # Verify all required keys are present
    assert hasattr(indicator, "status")
    assert hasattr(indicator, "reason")
    assert hasattr(indicator, "success_rate")
    assert hasattr(indicator, "error_rate")
    assert hasattr(indicator, "total_calls")
    assert hasattr(indicator, "db_off")
    assert hasattr(indicator, "top_error_reason")
    assert hasattr(indicator, "window_days")
    assert hasattr(indicator, "generated_at")

    # Verify values match insights
    assert indicator.success_rate == 0.98
    assert indicator.error_rate == 0.02
    assert indicator.total_calls == 500
    assert indicator.window_days == 7
    assert indicator.top_error_reason == "network_error"
