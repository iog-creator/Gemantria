#!/usr/bin/env python3
"""
Tests for pmagent lm.status command

Phase-7G: Test LM status introspection.
"""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from agentpm.lm.lm_status import (
    check_lmstudio_health,
    check_ollama_health,
    compute_lm_status,
    print_lm_status_table,
)
from pmagent.cli import app


@pytest.fixture
def runner():
    """CLI test runner."""
    return CliRunner()


def test_check_ollama_health_ok(monkeypatch):
    """Test Ollama health check returns OK when service is reachable."""
    with patch("agentpm.lm.lm_status.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        result = check_ollama_health("http://127.0.0.1:11434")
        assert result == "OK"


def test_check_ollama_health_down(monkeypatch):
    """Test Ollama health check returns DOWN when service is unreachable."""
    import requests

    with patch("agentpm.lm.lm_status.requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError()
        result = check_ollama_health("http://127.0.0.1:11434")
        assert result == "DOWN"


def test_check_lmstudio_health_ok(monkeypatch):
    """Test LM Studio health check returns OK when service is reachable."""
    with patch("agentpm.lm.lm_status.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        result = check_lmstudio_health("http://127.0.0.1:9994")
        assert result == "OK"


def test_check_lmstudio_health_down(monkeypatch):
    """Test LM Studio health check returns DOWN when service is unreachable."""
    import requests

    with patch("agentpm.lm.lm_status.requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError()
        result = check_lmstudio_health("http://127.0.0.1:9994")
        assert result == "DOWN"


def test_check_health_only_localhost():
    """Test health checks only allow localhost URLs."""
    result_ollama = check_ollama_health("http://example.com:11434")
    assert result_ollama == "UNKNOWN"

    result_lmstudio = check_lmstudio_health("http://example.com:9994")
    assert result_lmstudio == "UNKNOWN"


@patch("agentpm.lm.lm_status.check_ollama_health", return_value="OK")
@patch("agentpm.lm.lm_status.check_lmstudio_health", return_value="OK")
def test_compute_lm_status_with_mocks(mock_lmstudio, mock_ollama, monkeypatch):
    """Test compute_lm_status with mocked health checks."""
    # Set up environment
    monkeypatch.setenv("INFERENCE_PROVIDER", "ollama")
    monkeypatch.setenv("LOCAL_AGENT_MODEL", "granite4:tiny-h")
    monkeypatch.setenv("EMBEDDING_MODEL", "granite-embedding:278m")
    monkeypatch.setenv("RERANKER_MODEL", "granite4:tiny-h")
    monkeypatch.setenv("RERANKER_STRATEGY", "granite_llm")
    monkeypatch.setenv("THEOLOGY_PROVIDER", "lmstudio")
    monkeypatch.setenv("THEOLOGY_MODEL", "Christian-Bible-Expert-v2.0-12B")
    monkeypatch.setenv("THEOLOGY_LMSTUDIO_BASE_URL", "http://127.0.0.1:9994")
    monkeypatch.setenv("OLLAMA_ENABLED", "true")
    monkeypatch.setenv("LM_STUDIO_ENABLED", "true")

    # Reload config module to pick up new env vars
    import importlib
    from scripts import config

    importlib.reload(config.env)

    status = compute_lm_status()

    assert status["ok"] is True
    assert len(status["slots"]) == 4

    # Check slot details
    slot_map = {slot["slot"]: slot for slot in status["slots"]}

    assert slot_map["local_agent"]["provider"] == "ollama"
    assert slot_map["local_agent"]["model"] == "granite4:tiny-h"
    assert slot_map["local_agent"]["service_status"] == "OK"

    assert slot_map["embedding"]["provider"] == "ollama"
    assert slot_map["embedding"]["model"] == "granite-embedding:278m"
    assert slot_map["embedding"]["service_status"] == "OK"

    assert slot_map["reranker"]["provider"] == "ollama"
    assert "granite4:tiny-h" in slot_map["reranker"]["model"]
    assert "granite_llm" in slot_map["reranker"]["model"]
    assert slot_map["reranker"]["service_status"] == "OK"

    assert slot_map["theology"]["provider"] == "lmstudio"
    assert slot_map["theology"]["model"] == "Christian-Bible-Expert-v2.0-12B"
    assert slot_map["theology"]["service_status"] == "OK"


@patch("agentpm.lm.lm_status.check_ollama_health", return_value="DOWN")
@patch("agentpm.lm.lm_status.check_lmstudio_health", return_value="DOWN")
def test_compute_lm_status_handles_down_services(mock_lmstudio, mock_ollama, monkeypatch):
    """Test compute_lm_status handles down services correctly."""
    monkeypatch.setenv("INFERENCE_PROVIDER", "ollama")
    monkeypatch.setenv("LOCAL_AGENT_MODEL", "granite4:tiny-h")
    monkeypatch.setenv("EMBEDDING_MODEL", "granite-embedding:278m")
    monkeypatch.setenv("RERANKER_MODEL", "granite4:tiny-h")
    monkeypatch.setenv("THEOLOGY_PROVIDER", "lmstudio")
    monkeypatch.setenv("THEOLOGY_MODEL", "Christian-Bible-Expert-v2.0-12B")

    import importlib
    from scripts import config

    importlib.reload(config.env)

    status = compute_lm_status()

    assert status["ok"] is False
    slot_map = {slot["slot"]: slot for slot in status["slots"]}
    assert slot_map["local_agent"]["service_status"] == "DOWN"
    assert slot_map["theology"]["service_status"] == "DOWN"


def test_compute_lm_status_default_providers(monkeypatch):
    """Test compute_lm_status uses default providers when not set."""
    # Clear provider env vars
    for key in [
        "LOCAL_AGENT_PROVIDER",
        "EMBEDDING_PROVIDER",
        "RERANKER_PROVIDER",
        "THEOLOGY_PROVIDER",
    ]:
        monkeypatch.delenv(key, raising=False)

    monkeypatch.setenv("INFERENCE_PROVIDER", "ollama")
    monkeypatch.setenv("LOCAL_AGENT_MODEL", "granite4:tiny-h")
    monkeypatch.setenv("EMBEDDING_MODEL", "granite-embedding:278m")
    monkeypatch.setenv("RERANKER_MODEL", "granite4:tiny-h")
    monkeypatch.setenv("THEOLOGY_MODEL", "Christian-Bible-Expert-v2.0-12B")

    import importlib
    from scripts import config

    importlib.reload(config.env)

    with (
        patch("agentpm.lm.lm_status.check_ollama_health", return_value="OK"),
        patch("agentpm.lm.lm_status.check_lmstudio_health", return_value="OK"),
    ):
        status = compute_lm_status()

        slot_map = {slot["slot"]: slot for slot in status["slots"]}
        # Defaults should be used
        assert slot_map["local_agent"]["provider"] == "ollama"
        assert slot_map["embedding"]["provider"] == "ollama"
        assert slot_map["reranker"]["provider"] == "ollama"
        assert slot_map["theology"]["provider"] == "lmstudio"


def test_print_lm_status_table():
    """Test table formatting."""
    status = {
        "ok": True,
        "slots": [
            {
                "slot": "local_agent",
                "provider": "ollama",
                "model": "granite4:tiny-h",
                "service_status": "OK",
            },
            {
                "slot": "embedding",
                "provider": "ollama",
                "model": "granite-embedding:278m",
                "service_status": "OK",
            },
            {
                "slot": "reranker",
                "provider": "ollama",
                "model": "granite4:tiny-h (granite_llm)",
                "service_status": "OK",
            },
            {
                "slot": "theology",
                "provider": "lmstudio",
                "model": "Christian-Bible-Expert-v2.0-12B",
                "service_status": "OK",
            },
        ],
    }

    table = print_lm_status_table(status)
    lines = table.split("\n")

    assert len(lines) >= 6  # Header + separator + 4 rows
    assert "Slot" in lines[0]
    assert "Provider" in lines[0]
    assert "Model" in lines[0]
    assert "Service" in lines[0]
    assert "local_agent" in lines[2]
    assert "theology" in lines[5]


@patch("pmagent.cli.compute_lm_status")
def test_lm_status_command_json(mock_compute, runner):
    """Test lm.status command with --json-only flag."""
    mock_status = {
        "ok": True,
        "slots": [
            {
                "slot": "local_agent",
                "provider": "ollama",
                "model": "granite4:tiny-h",
                "service_status": "OK",
            },
        ],
    }
    mock_compute.return_value = mock_status

    result = runner.invoke(app, ["lm", "status", "--json-only"])

    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert output["ok"] is True
    assert len(output["slots"]) == 1


@patch("pmagent.cli.compute_lm_status")
def test_lm_status_command_table(mock_compute, runner):
    """Test lm.status command prints table."""
    mock_status = {
        "ok": True,
        "slots": [
            {
                "slot": "local_agent",
                "provider": "ollama",
                "model": "granite4:tiny-h",
                "service_status": "OK",
            },
            {
                "slot": "embedding",
                "provider": "ollama",
                "model": "granite-embedding:278m",
                "service_status": "OK",
            },
        ],
    }
    mock_compute.return_value = mock_status

    result = runner.invoke(app, ["lm", "status"])

    assert result.exit_code == 0
    # JSON should be in stdout
    output = json.loads(result.stdout)
    assert output["ok"] is True
    # Table should be in stderr
    assert "Slot" in result.stderr
    assert "local_agent" in result.stderr
