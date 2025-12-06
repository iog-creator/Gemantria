#!/usr/bin/env python3
"""Tests for system.reality_check tool (pmagent.tools.system)."""

from __future__ import annotations

from unittest.mock import patch

from pmagent.tools.system import reality_check


@patch("pmagent.tools.system.check_reality")
def test_system_reality_check_ok(mock_check):
    """Test system.reality_check when reality_check() returns overall_ok=True."""
    mock_check.return_value = {
        "command": "reality.check",
        "mode": "HINT",
        "overall_ok": True,
        "env": {"ok": True},
        "db": {"ok": True},
        "lm": {"ok": True},
    }

    result = reality_check()

    assert result["ok"] is True
    assert result["result"]["overall_ok"] is True
    assert result["result"]["mode"] == "HINT"


@patch("pmagent.tools.system.check_reality")
def test_system_reality_check_fail(mock_check):
    """Test system.reality_check when reality_check() returns overall_ok=False."""
    mock_check.return_value = {
        "command": "reality.check",
        "mode": "STRICT",
        "overall_ok": False,
        "env": {"ok": True},
        "db": {"ok": True},
        "lm": {"ok": False},
        "hints": ["LM not OK in STRICT mode"],
    }

    result = reality_check()

    assert result["ok"] is False
    assert result["result"]["overall_ok"] is False
    assert result["result"]["mode"] == "STRICT"


@patch("pmagent.tools.system.check_reality")
def test_system_reality_check_with_mode(mock_check):
    """Test system.reality_check with mode parameter."""
    mock_check.return_value = {
        "command": "reality.check",
        "mode": "STRICT",
        "overall_ok": True,
    }

    result = reality_check(mode="STRICT")

    assert result["ok"] is True
    # Only mode is passed, skip_dashboards uses default from reality_check() function
    mock_check.assert_called_once_with(mode="STRICT")


@patch("pmagent.tools.system.check_reality")
def test_system_reality_check_with_skip_dashboards(mock_check):
    """Test system.reality_check with skip_dashboards parameter."""
    mock_check.return_value = {
        "command": "reality.check",
        "mode": "HINT",
        "overall_ok": True,
        "exports": {"skipped": True},
        "eval_smoke": {"skipped": True},
    }

    result = reality_check(skip_dashboards=True)

    assert result["ok"] is True
    # Only skip_dashboards is passed, mode uses default from reality_check() function
    mock_check.assert_called_once_with(skip_dashboards=True)
