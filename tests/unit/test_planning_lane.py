#!/usr/bin/env python3
"""Unit tests for the planning lane adapters and router integration."""

from __future__ import annotations

from subprocess import CompletedProcess
from unittest.mock import patch

import pytest

from agentpm.adapters import codex_cli, gemini_cli, planning
from agentpm.adapters.planning_common import PlanningCliResult, compose_prompt
from agentpm.lm.router import GraniteRouter, RouterTask


def test_compose_prompt_includes_system_and_prompt():
    """compose_prompt should label system and prompt sections."""
    result = compose_prompt("Do the thing", system="You are planner")
    assert result.startswith("[system]")
    assert "[prompt]" in result


def test_gemini_cli_disabled_returns_lm_off():
    """Gemini adapter should short-circuit when disabled."""
    result = gemini_cli.run("Plan", enabled=False)
    assert result.ok is False
    assert result.mode == "lm_off"
    assert result.reason == "gemini_disabled"


@patch("agentpm.adapters.gemini_cli.subprocess.run")
@patch("agentpm.adapters.gemini_cli._command_available", return_value=True)
def test_gemini_cli_success(mock_available, mock_run):
    """Gemini adapter should return stdout when CLI succeeds."""
    mock_run.return_value = CompletedProcess(
        args=["gemini", "chat"],
        returncode=0,
        stdout="Plan ready",
        stderr="",
    )

    result = gemini_cli.run("Plan backend", enabled=True, cli_path="gemini")

    assert result.ok is True
    assert result.response == "Plan ready"
    assert mock_available.called
    mock_run.assert_called_once()


def test_codex_cli_disabled_returns_lm_off():
    """Codex adapter should report disabled state when flag is false."""
    result = codex_cli.run("Rewrite", enabled=False)
    assert result.ok is False
    assert result.reason == "codex_disabled"


@patch("agentpm.adapters.codex_cli._command_available", return_value=False)
def test_codex_cli_missing_binary(mock_available):
    """Codex adapter should report missing CLI."""
    result = codex_cli.run("Refactor", enabled=True, cli_path="codex")
    assert result.ok is False
    assert result.reason == "cli_not_found:codex"
    mock_available.assert_called_once_with("codex")


@patch("agentpm.adapters.codex_cli.subprocess.run")
@patch("agentpm.adapters.codex_cli._command_available", return_value=True)
def test_codex_cli_success(mock_available, mock_run):
    """Codex adapter should surface stdout on success."""
    mock_run.return_value = CompletedProcess(
        args=["codex", "exec"],
        returncode=0,
        stdout="Diff ready",
        stderr="",
    )

    result = codex_cli.run("Refactor guard", enabled=True, cli_path="codex")

    assert result.ok is True
    assert result.response == "Diff ready"
    mock_run.assert_called_once()


@patch("agentpm.adapters.planning.get_lm_model_config")
@patch("agentpm.adapters.planning.gemini_cli.run")
def test_planning_prompt_uses_gemini_when_configured(mock_run, mock_cfg):
    """Planning adapter should call Gemini CLI when configured."""
    success = PlanningCliResult(ok=True, mode="lm_on", provider="gemini", response="Steps")
    mock_run.return_value = success
    mock_cfg.return_value = {
        "planning_provider": "gemini",
        "planning_model": "gemini-2.5-pro",
        "gemini_cli_path": "gemini",
        "gemini_enabled": True,
    }

    result = planning.run_planning_prompt("Design guard", system="Architect role")

    assert result is success
    kwargs = mock_run.call_args.kwargs
    assert kwargs["system"] == "Architect role"
    assert kwargs["model"] == "gemini-2.5-pro"


@patch("agentpm.adapters.planning.lm_studio_chat", return_value="Fallback plan")
@patch("agentpm.adapters.planning.get_lm_model_config")
@patch("agentpm.adapters.planning.gemini_cli.run")
def test_planning_prompt_falls_back_when_cli_disabled(mock_run, mock_cfg, mock_chat):
    """Planning adapter should fallback to local agent when CLI is unavailable."""
    mock_run.return_value = PlanningCliResult(
        ok=False, mode="lm_off", provider="gemini", reason="gemini_disabled"
    )
    mock_cfg.return_value = {
        "planning_provider": "gemini",
        "planning_model": "gemini-2.5-pro",
        "gemini_enabled": False,
        "local_agent_model": "granite4:tiny-h",
    }

    result = planning.run_planning_prompt("Need plan now")

    assert result.ok is True
    assert result.response == "Fallback plan"
    mock_chat.assert_called_once_with("Need plan now", model_slot="local_agent", system=None)


@patch("agentpm.adapters.planning.get_lm_model_config")
@patch("agentpm.adapters.planning.codex_cli.run")
def test_planning_prompt_uses_codex_provider(mock_run, mock_cfg):
    """Planning adapter should call Codex CLI when provider is codex."""
    success = PlanningCliResult(ok=True, mode="lm_on", provider="codex", response="Diff plan")
    mock_run.return_value = success
    mock_cfg.return_value = {
        "planning_provider": "codex",
        "planning_model": "gpt-5-codex",
        "codex_cli_path": "codex",
        "codex_enabled": True,
    }

    result = planning.run_planning_prompt("Generate diffs", system="Implementer")

    assert result is success
    kwargs = mock_run.call_args.kwargs
    assert kwargs["system"] == "Implementer"
    assert kwargs["model"] == "gpt-5-codex"


def test_router_routes_planning_slot_with_configured_provider():
    """Router should return planning slot decision with configured provider/model."""
    config = {
        "planning_provider": "gemini",
        "planning_model": "gemini-2.5-pro-plan",
        "gemini_enabled": True,
        "local_agent_model": "granite4:tiny-h",
    }
    router = GraniteRouter(config=config, dry_run=True)

    decision = router.route_task(RouterTask(kind="planning"))

    assert decision.slot == "planning"
    assert decision.provider == "gemini"
    assert decision.model_name == "gemini-2.5-pro-plan"
    assert decision.temperature == pytest.approx(0.2)
    assert decision.extra_params["planning_provider"] == "gemini"


def test_router_raises_when_planning_provider_disabled():
    """Router should fail fast if planning provider is disabled."""
    config = {
        "planning_provider": "codex",
        "planning_model": "gpt-5-codex-plan",
        "codex_enabled": False,
        "local_agent_model": "granite4:tiny-h",
    }
    router = GraniteRouter(config=config, dry_run=False)

    with pytest.raises(RuntimeError) as excinfo:
        router.route_task(RouterTask(kind="planning"))

    assert "Codex CLI is disabled" in str(excinfo.value)
