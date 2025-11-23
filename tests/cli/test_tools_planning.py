#!/usr/bin/env python3
"""CLI tests for pmagent tools planning commands."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import typer.testing

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentpm.adapters.planning_common import PlanningCliResult  # noqa: E402
from pmagent.cli import app  # noqa: E402

runner = typer.testing.CliRunner()


@patch("pmagent.cli.mark_agent_run_error")
@patch("pmagent.cli.mark_agent_run_success")
@patch("pmagent.cli.create_agent_run", return_value="run-1")
@patch("pmagent.cli.planning_adapter.summarize_result")
@patch("pmagent.cli.planning_adapter.run_planning_prompt")
def test_tools_plan_prints_response(mock_run, mock_summary, mock_create, mock_success, mock_error):
    """tools.plan should print JSON summary and response body."""
    result_payload = PlanningCliResult(ok=True, mode="lm_on", provider="gemini", response="Step 1\nStep 2")
    mock_run.return_value = result_payload
    mock_summary.return_value = {"ok": True, "provider": "gemini"}

    result = runner.invoke(app, ["tools", "plan", "Design guarded change"])

    assert result.exit_code == 0
    assert '"provider": "gemini"' in result.stdout
    assert "=== Response ===" in result.stdout
    assert "Step 1" in result.stdout
    mock_create.assert_called_once()
    mock_success.assert_called_once()
    mock_error.assert_not_called()


@patch("pmagent.cli.mark_agent_run_error")
@patch("pmagent.cli.mark_agent_run_success")
@patch("pmagent.cli.create_agent_run", return_value="run-2")
@patch("pmagent.cli.get_lm_model_config")
@patch("pmagent.cli.planning_adapter.summarize_result", return_value={"ok": False, "reason": "cli_not_found:gemini"})
@patch("pmagent.cli.gemini_cli_adapter.run")
def test_tools_gemini_handles_disabled_cli(mock_run, mock_summary, mock_cfg, mock_create, mock_success, mock_error):
    """tools.gemini should surface CLI errors without crashing."""
    mock_cfg.return_value = {
        "planning_model": "gemini-2.5-pro",
        "gemini_cli_path": "gemini",
        "gemini_enabled": False,
    }
    mock_run.return_value = PlanningCliResult(
        ok=False,
        mode="lm_off",
        provider="gemini",
        reason="cli_not_found:gemini",
    )

    result = runner.invoke(app, ["tools", "gemini", "Plan something"])

    assert result.exit_code == 0
    assert '"reason": "cli_not_found:gemini"' in result.stdout
    mock_create.assert_called_once()
    mock_success.assert_called_once()
    mock_error.assert_not_called()


@patch("pmagent.cli.mark_agent_run_error")
@patch("pmagent.cli.mark_agent_run_success")
@patch("pmagent.cli.create_agent_run", return_value="run-3")
@patch("pmagent.cli.get_lm_model_config")
@patch("pmagent.cli.planning_adapter.summarize_result", return_value={"ok": False, "reason": "codex_disabled"})
@patch("pmagent.cli.codex_cli_adapter.run")
def test_tools_codex_reports_disabled_state(mock_run, mock_summary, mock_cfg, mock_create, mock_success, mock_error):
    """tools.codex should report disabled state cleanly."""
    mock_cfg.return_value = {
        "planning_model": "gpt-5-codex",
        "codex_cli_path": "codex",
        "codex_enabled": False,
    }
    mock_run.return_value = PlanningCliResult(
        ok=False,
        mode="lm_off",
        provider="codex",
        reason="codex_disabled",
    )

    result = runner.invoke(app, ["tools", "codex", "Generate diff"])

    assert result.exit_code == 0
    assert '"reason": "codex_disabled"' in result.stdout
    mock_create.assert_called_once()
    mock_success.assert_called_once()
    mock_error.assert_not_called()
