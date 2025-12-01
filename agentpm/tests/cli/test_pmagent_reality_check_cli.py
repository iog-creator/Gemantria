#!/usr/bin/env python3
"""Tests for pmagent reality-check check CLI command."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from pmagent.cli import app


@pytest.fixture
def runner():
    """Create a Typer CLI test runner."""
    return CliRunner()


@patch("pmagent.cli.mark_agent_run_success")
@patch("pmagent.cli.create_agent_run")
@patch("agentpm.reality.check.reality_check")
def test_reality_check_cli_hint_mode_ok(mock_check, mock_create_run, mock_mark_success, runner):
    """Test reality-check check command in HINT mode with overall_ok=True."""
    from agentpm.control_plane import AgentRun

    mock_run = AgentRun(
        id="test-run-id",
        created_at=None,
        updated_at=None,
        command="system.reality-check",
        status="started",
    )
    mock_create_run.return_value = mock_run
    mock_check.return_value = {
        "command": "reality.check",
        "mode": "HINT",
        "timestamp": "2025-11-20T12:00:00Z",
        "overall_ok": True,
        "env": {"ok": True, "dsn_ok": True},
        "db": {"ok": True},
        "lm": {"ok": True},
        "exports": {"ok": True},
        "eval_smoke": {"ok": True},
        "hints": [],
    }

    result = runner.invoke(app, ["reality-check", "check", "--mode", "hint"])

    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert output["overall_ok"] is True
    assert output["mode"] == "HINT"
    # Verify AI tracking: create_agent_run was called
    mock_create_run.assert_called_once_with("system.reality-check", {"mode": "hint", "no_dashboards": False})
    # Verify AI tracking: mark_agent_run_success was called with verdict
    mock_mark_success.assert_called_once_with(mock_run, mock_check.return_value)
    mock_check.assert_called_once_with(mode="HINT", skip_dashboards=False)
    mock_mark_success.assert_called_once()


@patch("pmagent.cli.mark_agent_run_success")
@patch("pmagent.cli.create_agent_run")
@patch("agentpm.reality.check.reality_check")
def test_reality_check_cli_strict_mode_ok(mock_check, mock_create_run, mock_mark_success, runner):
    """Test reality-check check command in STRICT mode with overall_ok=True."""
    from agentpm.control_plane import AgentRun

    mock_run = AgentRun(
        id="test-run-id",
        created_at=None,
        updated_at=None,
        command="system.reality-check",
        status="started",
    )
    mock_create_run.return_value = mock_run
    mock_check.return_value = {
        "command": "reality.check",
        "mode": "STRICT",
        "timestamp": "2025-11-20T12:00:00Z",
        "overall_ok": True,
        "env": {"ok": True, "dsn_ok": True},
        "db": {"ok": True},
        "lm": {"ok": True},
        "exports": {"ok": True},
        "eval_smoke": {"ok": True},
        "hints": [],
    }

    result = runner.invoke(app, ["reality-check", "check", "--mode", "strict"])

    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert output["overall_ok"] is True
    assert output["mode"] == "STRICT"
    # Verify AI tracking
    mock_create_run.assert_called_once_with("system.reality-check", {"mode": "strict", "no_dashboards": False})
    mock_mark_success.assert_called_once_with(mock_run, mock_check.return_value)
    mock_check.assert_called_once_with(mode="STRICT", skip_dashboards=False)


@patch("pmagent.cli.mark_agent_run_success")
@patch("pmagent.cli.create_agent_run")
@patch("agentpm.reality.check.reality_check")
def test_reality_check_cli_strict_mode_fail(mock_check, mock_create_run, mock_mark_success, runner):
    """Test reality-check check command in STRICT mode with overall_ok=False."""
    from agentpm.control_plane import AgentRun

    mock_run = AgentRun(
        id="test-run-id",
        created_at=None,
        updated_at=None,
        command="system.reality-check",
        status="started",
    )
    mock_create_run.return_value = mock_run
    mock_check.return_value = {
        "command": "reality.check",
        "mode": "STRICT",
        "timestamp": "2025-11-20T12:00:00Z",
        "overall_ok": False,
        "env": {"ok": True, "dsn_ok": True},
        "db": {"ok": True},
        "lm": {"ok": False, "mode": "lm_off"},
        "exports": {"ok": True},
        "eval_smoke": {"ok": True},
        "hints": ["LM not OK in STRICT mode"],
    }

    result = runner.invoke(app, ["reality-check", "check", "--mode", "strict"])

    assert result.exit_code == 1
    output = json.loads(result.stdout)
    assert output["overall_ok"] is False
    assert output["mode"] == "STRICT"
    assert len(output["hints"]) > 0
    # Verify AI tracking: CLI marks success even when overall_ok=False (only errors on exceptions)
    mock_create_run.assert_called_once_with("system.reality-check", {"mode": "strict", "no_dashboards": False})
    mock_mark_success.assert_called_once_with(mock_run, mock_check.return_value)


@patch("pmagent.cli.mark_agent_run_success")
@patch("pmagent.cli.create_agent_run")
@patch("agentpm.reality.check.reality_check")
def test_reality_check_cli_json_only(mock_check, mock_create_run, mock_mark_success, runner):
    """Test reality-check check command with --json-only flag."""
    from agentpm.control_plane import AgentRun

    mock_run = AgentRun(
        id="test-run-id",
        created_at=None,
        updated_at=None,
        command="system.reality-check",
        status="started",
    )
    mock_create_run.return_value = mock_run
    mock_check.return_value = {
        "command": "reality.check",
        "mode": "HINT",
        "overall_ok": True,
    }

    result = runner.invoke(app, ["reality-check", "check", "--json-only"])

    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert output["overall_ok"] is True
    # Verify AI tracking
    mock_create_run.assert_called_once()
    mock_mark_success.assert_called_once_with(mock_run, mock_check.return_value)
    # Should not have human-readable output in stderr when --json-only
    assert "LIVE STATUS" not in result.stderr


@patch("pmagent.cli.mark_agent_run_success")
@patch("pmagent.cli.create_agent_run")
@patch("agentpm.reality.check.reality_check")
def test_reality_check_cli_no_dashboards(mock_check, mock_create_run, mock_mark_success, runner):
    """Test reality-check check command with --no-dashboards flag."""
    from agentpm.control_plane import AgentRun

    mock_run = AgentRun(
        id="test-run-id",
        created_at=None,
        updated_at=None,
        command="system.reality-check",
        status="started",
    )
    mock_create_run.return_value = mock_run
    mock_check.return_value = {
        "command": "reality.check",
        "mode": "HINT",
        "overall_ok": True,
        "exports": {"skipped": True},
        "eval_smoke": {"skipped": True},
    }

    result = runner.invoke(app, ["reality-check", "check", "--no-dashboards"])

    assert result.exit_code == 0
    # Verify AI tracking
    mock_create_run.assert_called_once_with("system.reality-check", {"mode": "hint", "no_dashboards": True})
    mock_mark_success.assert_called_once_with(mock_run, mock_check.return_value)
    mock_check.assert_called_once_with(mode="HINT", skip_dashboards=True)


@patch("pmagent.cli.mark_agent_run_error")
@patch("pmagent.cli.create_agent_run")
@patch("agentpm.reality.check.reality_check")
def test_reality_check_cli_invalid_mode(mock_check, mock_create_run, mock_mark_error, runner):
    """Test reality-check check command with invalid mode."""
    from agentpm.control_plane import AgentRun

    mock_run = AgentRun(
        id="test-run-id",
        created_at=None,
        updated_at=None,
        command="system.reality-check",
        status="started",
    )
    mock_create_run.return_value = mock_run
    result = runner.invoke(app, ["reality-check", "check", "--mode", "invalid"])

    assert result.exit_code != 0
    assert "ERROR" in result.stderr or "invalid" in result.stderr.lower()
    mock_check.assert_not_called()
    # Verify AI tracking: create_agent_run was called, mark_agent_run_error was called
    mock_create_run.assert_called_once_with("system.reality-check", {"mode": "invalid", "no_dashboards": False})
    # mark_agent_run_error may be called multiple times (error message + exception)
    assert mock_mark_error.called
