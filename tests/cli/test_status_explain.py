#!/usr/bin/env python3
"""
Tests for status.explain CLI command.

Phase-8A: Verifies CLI command output format and JSON option.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import typer.testing  # noqa: E402

from pmagent.cli import app  # noqa: E402

runner = typer.testing.CliRunner()


@patch("pmagent.cli.explain_system_status")
def test_status_explain_default_output(mock_explain):
    """Test that pmagent status.explain returns formatted text by default."""
    mock_explain.return_value = {
        "level": "WARN",
        "headline": "Database is partially configured",
        "details": "Database is connected, but some tables or features are missing.",
    }

    result = runner.invoke(app, ["status", "explain"])

    assert result.exit_code == 0
    assert "[WARN]" in result.stdout
    assert "Database is partially configured" in result.stdout
    assert "some tables" in result.stdout


@patch("pmagent.cli.explain_system_status")
def test_status_explain_json_only(mock_explain):
    """Test that pmagent status.explain --json-only returns valid JSON."""
    mock_explain.return_value = {
        "level": "OK",
        "headline": "All systems nominal",
        "details": "Database is ready and all checks passed. All 4 LM slot(s) are operational.",
        "documentation": {
            "available": True,
            "total": 5,
            "by_subsystem": {"docs": 3, "agentpm": 1, "root": 1},
            "by_type": {"ssot": 2, "adr": 1, "agents_md": 2},
            "hints": [],
            "key_docs": [],
        },
    }

    result = runner.invoke(app, ["status", "explain", "--json-only"])

    assert result.exit_code == 0

    # Parse JSON output
    data = json.loads(result.stdout)

    assert data["level"] == "OK"
    assert data["headline"] == "All systems nominal"
    assert "details" in data
    assert isinstance(data["details"], str)
    # KB-Reg:M5: Verify documentation section is present
    assert "documentation" in data
    assert isinstance(data["documentation"], dict)
    assert "available" in data["documentation"]
    assert "total" in data["documentation"]


@patch("pmagent.cli.explain_system_status")
def test_status_explain_no_lm(mock_explain):
    """Test that pmagent status.explain --no-lm skips LM enhancement."""
    mock_explain.return_value = {
        "level": "ERROR",
        "headline": "Database is offline",
        "details": "Database is not reachable.",
    }

    result = runner.invoke(app, ["status", "explain", "--no-lm"])

    assert result.exit_code == 0
    # Should have been called with use_lm=False
    mock_explain.assert_called_once_with(use_lm=False)
    assert "[ERROR]" in result.stdout


@patch("pmagent.cli.explain_system_status")
def test_status_explain_error_level_prints_to_stderr(mock_explain):
    """Test that ERROR level explanations also print to stderr."""
    mock_explain.return_value = {
        "level": "ERROR",
        "headline": "Database is offline",
        "details": "Database is not reachable. This prevents data operations.",
    }

    result = runner.invoke(app, ["status", "explain"])

    assert result.exit_code == 0
    # Should appear in both stdout and stderr
    assert "[ERROR]" in result.stdout
    assert "Database is offline" in result.stdout


@patch("pmagent.cli.explain_system_status")
def test_status_explain_ok_level(mock_explain):
    """Test that OK level explanations work correctly."""
    mock_explain.return_value = {
        "level": "OK",
        "headline": "All systems nominal",
        "details": "Database is ready and all checks passed. All 4 LM slot(s) are operational.",
    }

    result = runner.invoke(app, ["status", "explain"])

    assert result.exit_code == 0
    assert "[OK]" in result.stdout
    assert "All systems nominal" in result.stdout
