"""Tests for pmagent CLI health commands (Phase-3B Feature #4)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from pmagent.cli import app


@pytest.fixture
def runner():
    """Create a Typer CLI test runner."""
    return CliRunner()


@patch("pmagent.cli.compute_system_health")
def test_health_system_all_off(mock_system_health, runner):
    """Test system health when all components are off."""
    mock_system_health.return_value = {
        "ok": False,
        "components": {
            "db": {
                "ok": False,
                "mode": "db_off",
                "details": {"errors": ["driver_missing: Postgres database driver not available"]},
            },
            "lm": {
                "ok": False,
                "mode": "lm_off",
                "details": {"endpoint": "http://127.0.0.1:1234", "errors": ["connection_refused: Connection refused"]},
            },
            "graph": {
                "ok": False,
                "mode": "db_off",
                "reason": "Postgres database driver not available",
            },
        },
    }

    result = runner.invoke(app, ["health", "system"])

    assert result.exit_code == 0
    assert "SYSTEM_HEALTH" in result.stderr
    assert "mode=db_off" in result.stderr
    assert "mode=lm_off" in result.stderr
    assert '"ok": false' in result.stdout


@patch("pmagent.cli.compute_system_health")
def test_health_system_all_ready(mock_system_health, runner):
    """Test system health when all components are ready."""
    mock_system_health.return_value = {
        "ok": True,
        "components": {
            "db": {
                "ok": True,
                "mode": "ready",
                "checks": {"driver_available": True, "connection_ok": True, "graph_stats_ready": True},
                "details": {"errors": []},
            },
            "lm": {
                "ok": True,
                "mode": "lm_ready",
                "details": {"endpoint": "http://127.0.0.1:1234", "errors": []},
            },
            "graph": {
                "ok": True,
                "mode": "db_on",
                "stats": {"nodes": 100, "edges": 200, "avg_degree": 4.0},
            },
        },
    }

    result = runner.invoke(app, ["health", "system"])

    assert result.exit_code == 0
    assert "SYSTEM_HEALTH" in result.stderr
    assert "mode=ready" in result.stderr
    assert "mode=lm_ready" in result.stderr
    assert "mode=db_on" in result.stderr
    assert '"ok": true' in result.stdout


@patch("pmagent.cli.check_db_health")
def test_health_db_off(mock_db_health, runner):
    """Test DB health when database is off."""
    mock_db_health.return_value = {
        "ok": False,
        "mode": "db_off",
        "checks": {
            "driver_available": False,
            "connection_ok": False,
            "graph_stats_ready": False,
        },
        "details": {
            "errors": ["driver_missing: Postgres database driver not available"],
        },
    }

    result = runner.invoke(app, ["health", "db"])

    assert result.exit_code == 0
    assert "DB_HEALTH" in result.stderr
    assert "mode=db_off" in result.stderr
    assert '"mode": "db_off"' in result.stdout


@patch("pmagent.cli.check_lm_health")
def test_health_lm_off(mock_lm_health, runner):
    """Test LM health when LM Studio is off."""
    mock_lm_health.return_value = {
        "ok": False,
        "mode": "lm_off",
        "details": {
            "endpoint": "http://127.0.0.1:1234",
            "errors": ["connection_refused: Connection refused"],
        },
    }

    result = runner.invoke(app, ["health", "lm"])

    assert result.exit_code == 0
    assert "LM_HEALTH" in result.stderr
    assert "mode=lm_off" in result.stderr
    assert '"mode": "lm_off"' in result.stdout


@patch("pmagent.cli.compute_graph_overview")
def test_health_graph_db_off(mock_graph_overview, runner):
    """Test graph overview when database is off."""
    mock_graph_overview.return_value = {
        "ok": False,
        "mode": "db_off",
        "stats": {
            "nodes": None,
            "edges": None,
            "avg_degree": None,
            "snapshot_count": None,
            "last_import_at": None,
        },
        "reason": "Postgres database driver not available",
    }

    result = runner.invoke(app, ["health", "graph"])

    assert result.exit_code == 0
    assert "GRAPH_OVERVIEW" in result.stderr
    assert "mode=db_off" in result.stderr
    assert '"mode": "db_off"' in result.stdout


@patch("pmagent.cli.compute_system_health")
def test_health_system_json_only(mock_system_health, runner):
    """Test system health with --json-only flag."""
    mock_system_health.return_value = {
        "ok": False,
        "components": {
            "db": {"ok": False, "mode": "db_off"},
            "lm": {"ok": False, "mode": "lm_off"},
            "graph": {"ok": False, "mode": "db_off"},
        },
    }

    result = runner.invoke(app, ["health", "system", "--json-only"])

    assert result.exit_code == 0
    assert "SYSTEM_HEALTH" not in result.stdout  # Should not have summary in stdout
    assert "SYSTEM_HEALTH" not in result.stderr  # Should not have summary in stderr
    # Should have JSON
    data = json.loads(result.stdout)
    assert data["ok"] is False

