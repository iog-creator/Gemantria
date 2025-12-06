#!/usr/bin/env python3
"""Tests for pmagent health lm command using LM Studio adapter (Phase-3C P1)."""

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


@patch("scripts.guards.guard_lm_health.lm_studio_chat")
@patch("scripts.guards.guard_lm_health.get_lm_studio_settings")
def test_health_lm_ready_via_adapter(mock_settings, mock_chat, runner):
    """Test LM health when LM Studio is ready via adapter."""
    mock_settings.return_value = {
        "enabled": True,
        "base_url": "http://localhost:1234/v1",
        "model": "test-model",
        "api_key": None,
    }
    mock_chat.return_value = {
        "ok": True,
        "mode": "lm_on",
        "reason": None,
        "response": {"choices": [{"message": {"content": "hi"}}]},
    }

    result = runner.invoke(app, ["health", "lm"])

    assert result.exit_code == 0
    assert "LM_HEALTH" in result.stderr
    assert "mode=lm_ready" in result.stderr
    data = json.loads(result.stdout)
    assert data["ok"] is True
    assert data["mode"] == "lm_ready"


@patch("scripts.guards.guard_lm_health.lm_studio_chat")
@patch("scripts.guards.guard_lm_health.get_lm_studio_settings")
def test_health_lm_off_via_adapter(mock_settings, mock_chat, runner):
    """Test LM health when LM Studio is off via adapter."""
    mock_settings.return_value = {
        "enabled": True,
        "base_url": "http://localhost:1234/v1",
        "model": "test-model",
        "api_key": None,
    }
    mock_chat.return_value = {
        "ok": False,
        "mode": "lm_off",
        "reason": "connection_error: Connection refused",
        "response": None,
    }

    result = runner.invoke(app, ["health", "lm"])

    assert result.exit_code == 0
    assert "LM_HEALTH" in result.stderr
    assert "mode=lm_off" in result.stderr
    data = json.loads(result.stdout)
    assert data["ok"] is False
    assert data["mode"] == "lm_off"
    assert len(data["details"]["errors"]) > 0


@patch("scripts.guards.guard_lm_health.get_lm_studio_settings")
def test_health_lm_disabled(mock_settings, runner):
    """Test LM health when LM Studio is disabled."""
    mock_settings.return_value = {
        "enabled": False,
        "base_url": "http://localhost:1234/v1",
        "model": None,
        "api_key": None,
    }

    result = runner.invoke(app, ["health", "lm"])

    assert result.exit_code == 0
    assert "LM_HEALTH" in result.stderr
    assert "mode=lm_off" in result.stderr
    data = json.loads(result.stdout)
    assert data["ok"] is False
    assert data["mode"] == "lm_off"
    assert "lm_studio_disabled_or_unconfigured" in str(data["details"]["errors"])
