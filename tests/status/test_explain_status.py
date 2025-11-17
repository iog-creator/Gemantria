#!/usr/bin/env python3
"""
Tests for status explanation module.

Phase-8A: Verifies rule-based explanation logic and LM enhancement fallback.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentpm.status.explain import explain_system_status, summarize_system_status  # noqa: E402


def test_summarize_healthy_system():
    """Test that a fully healthy system returns OK level."""
    status = {
        "db": {"reachable": True, "mode": "ready", "notes": "Database is ready"},
        "lm": {
            "slots": [
                {"name": "local_agent", "service": "OK"},
                {"name": "embedding", "service": "OK"},
                {"name": "reranker", "service": "OK"},
                {"name": "theology", "service": "OK"},
            ],
            "notes": "All slots OK",
        },
    }

    result = summarize_system_status(status)

    assert result["level"] == "OK"
    assert "nominal" in result["headline"].lower() or "all systems" in result["headline"].lower()
    assert "ready" in result["details"].lower() or "operational" in result["details"].lower()


def test_summarize_db_off():
    """Test that db_off mode returns ERROR level."""
    status = {
        "db": {"reachable": False, "mode": "db_off", "notes": "Database unavailable"},
        "lm": {"slots": [], "notes": "No slots"},
    }

    result = summarize_system_status(status)

    assert result["level"] == "ERROR"
    assert "offline" in result["headline"].lower() or "database" in result["headline"].lower()
    assert "offline" in result["details"].lower() or "not reachable" in result["details"].lower()


def test_summarize_db_partial():
    """Test that partial DB mode returns WARN level."""
    status = {
        "db": {
            "reachable": True,
            "mode": "partial",
            "notes": "Database connected but some tables missing",
        },
        "lm": {"slots": [], "notes": "No slots"},
    }

    result = summarize_system_status(status)

    assert result["level"] == "WARN"
    assert "partial" in result["headline"].lower()
    assert "partial" in result["details"].lower() or "missing" in result["details"].lower()


def test_summarize_lm_slot_down():
    """Test that down LM slots increase warning level."""
    status = {
        "db": {"reachable": True, "mode": "ready", "notes": "Database is ready"},
        "lm": {
            "slots": [
                {"name": "local_agent", "service": "DOWN"},
                {"name": "embedding", "service": "OK"},
                {"name": "reranker", "service": "OK"},
                {"name": "theology", "service": "OK"},
            ],
            "notes": "Some slots down",
        },
    }

    result = summarize_system_status(status)

    assert result["level"] == "WARN"
    assert "down" in result["headline"].lower() or "lm" in result["headline"].lower()
    assert "local_agent" in result["details"] or "1 of 4" in result["details"]


def test_summarize_db_partial_and_lm_down():
    """Test that partial DB + down LM slots results in ERROR level."""
    status = {
        "db": {
            "reachable": True,
            "mode": "partial",
            "notes": "Database connected but some tables missing",
        },
        "lm": {
            "slots": [
                {"name": "local_agent", "service": "DOWN"},
                {"name": "embedding", "service": "OK"},
            ],
            "notes": "Some slots down",
        },
    }

    result = summarize_system_status(status)

    assert result["level"] == "ERROR"
    assert "database" in result["headline"].lower() or "issues" in result["headline"].lower()


def test_summarize_lm_unknown_slots():
    """Test that unknown/disabled LM slots result in WARN level."""
    status = {
        "db": {"reachable": True, "mode": "ready", "notes": "Database is ready"},
        "lm": {
            "slots": [
                {"name": "local_agent", "service": "UNKNOWN"},
                {"name": "embedding", "service": "DISABLED"},
                {"name": "reranker", "service": "OK"},
                {"name": "theology", "service": "OK"},
            ],
            "notes": "Some slots unknown",
        },
    }

    result = summarize_system_status(status)

    assert result["level"] == "WARN"
    assert "unknown" in result["headline"].lower() or "disabled" in result["headline"].lower()


@patch("agentpm.status.explain.get_system_status")
def test_explain_system_status_healthy(mock_get_status):
    """Test explain_system_status with healthy system."""
    mock_get_status.return_value = {
        "db": {"reachable": True, "mode": "ready", "notes": "Database is ready"},
        "lm": {
            "slots": [
                {"name": "local_agent", "service": "OK"},
                {"name": "embedding", "service": "OK"},
            ],
            "notes": "All slots OK",
        },
    }

    result = explain_system_status(use_lm=False)

    assert "level" in result
    assert "headline" in result
    assert "details" in result
    assert result["level"] in ("OK", "WARN", "ERROR")


@patch("agentpm.status.explain.get_system_status")
def test_explain_system_status_never_raises(mock_get_status):
    """Test that explain_system_status never raises, even on errors."""
    mock_get_status.side_effect = Exception("Test error")

    # Should not raise
    result = explain_system_status(use_lm=False)

    # Should return a dict with required keys (even if empty/default)
    assert isinstance(result, dict)
    assert "level" in result
    assert "headline" in result
    assert "details" in result


@patch("agentpm.status.explain._enhance_with_lm")
@patch("agentpm.status.explain.get_system_status")
def test_explain_system_status_with_lm(mock_get_status, mock_enhance):
    """Test that explain_system_status calls LM enhancement when use_lm=True."""
    mock_get_status.return_value = {
        "db": {"reachable": True, "mode": "ready", "notes": "Database is ready"},
        "lm": {
            "slots": [{"name": "local_agent", "service": "OK"}],
            "notes": "All slots OK",
        },
    }
    mock_enhance.return_value = {
        "level": "OK",
        "headline": "All systems nominal",
        "details": "Enhanced explanation",
    }

    result = explain_system_status(use_lm=True)

    # Should have called enhance
    mock_enhance.assert_called_once()
    assert result["details"] == "Enhanced explanation"


@patch("agentpm.status.explain._enhance_with_lm")
@patch("agentpm.status.explain.get_system_status")
def test_explain_system_status_no_lm_when_disabled(mock_get_status, mock_enhance):
    """Test that explain_system_status skips LM when use_lm=False."""
    mock_get_status.return_value = {
        "db": {"reachable": True, "mode": "ready", "notes": "Database is ready"},
        "lm": {"slots": [], "notes": "No slots"},
    }

    result = explain_system_status(use_lm=False)

    # Should not have called enhance
    mock_enhance.assert_not_called()
    assert "level" in result


@patch("agentpm.adapters.lm_studio.chat")
@patch("agentpm.status.explain.get_system_status")
def test_enhance_with_lm_fallback_on_error(mock_get_status, mock_chat):
    """Test that LM enhancement falls back to rule-based on error."""
    mock_get_status.return_value = {
        "db": {"reachable": True, "mode": "ready", "notes": "Database is ready"},
        "lm": {
            "slots": [{"name": "local_agent", "service": "OK"}],
            "notes": "All slots OK",
        },
    }
    mock_chat.side_effect = Exception("LM call failed")

    # Should not raise, should return rule-based explanation
    result = explain_system_status(use_lm=True)

    assert "level" in result
    assert "headline" in result
    assert "details" in result
