"""Tests for pmagent CLI control summary command (Phase-3B Consolidation)."""

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


@patch("pmagent.cli.compute_control_summary")
def test_control_summary_db_off(mock_summary, runner):
    """Test control summary when all components are db_off."""
    mock_summary.return_value = {
        "ok": True,  # Acceptable when all are db_off (hermetic)
        "generated_at": "2024-01-15T10:30:00+00:00",
        "components": {
            "status": {
                "ok": False,
                "mode": "db_off",
                "reason": "Postgres database driver not available",
                "tables": {},
            },
            "tables": {
                "ok": False,
                "mode": "db_off",
                "error": "Postgres database driver not available",
                "tables": {},
            },
            "schema": {
                "ok": False,
                "mode": "db_off",
                "reason": "Postgres database driver not available",
                "tables": {},
            },
            "pipeline_status": {
                "ok": False,
                "mode": "db_off",
                "reason": "Postgres database driver not available",
                "window_hours": 24,
                "summary": {
                    "total_runs": 0,
                    "pipelines": {},
                },
            },
        },
    }

    result = runner.invoke(app, ["control", "summary"])

    assert result.exit_code == 0
    assert "CONTROL_SUMMARY" in result.stderr
    assert "ok=true" in result.stderr or "ok=False" not in result.stderr

    output_json = json.loads(result.stdout)
    assert "ok" in output_json
    assert "generated_at" in output_json
    assert "components" in output_json
    assert "status" in output_json["components"]
    assert "tables" in output_json["components"]
    assert "schema" in output_json["components"]
    assert "pipeline_status" in output_json["components"]


@patch("pmagent.cli.compute_control_summary")
def test_control_summary_db_on(mock_summary, runner):
    """Test control summary when all components are db_on and ok."""
    mock_summary.return_value = {
        "ok": True,
        "generated_at": "2024-01-15T10:30:00+00:00",
        "components": {
            "status": {
                "ok": True,
                "mode": "ready",
                "reason": None,
                "tables": {
                    "control.agent_run": {
                        "present": True,
                        "row_count": 10,
                        "latest_created_at": "2024-01-15T09:00:00+00:00",
                    }
                },
            },
            "tables": {
                "ok": True,
                "mode": "db_on",
                "error": None,
                "tables": {
                    "control.agent_run": 10,
                    "control.tool_catalog": 5,
                },
            },
            "schema": {
                "ok": True,
                "mode": "db_on",
                "reason": None,
                "tables": {
                    "control.agent_run": {
                        "columns": [],
                        "primary_key": ["id"],
                        "indexes": [],
                    }
                },
            },
            "pipeline_status": {
                "ok": True,
                "mode": "db_on",
                "reason": None,
                "window_hours": 24,
                "summary": {
                    "total_runs": 5,
                    "pipelines": {
                        "graph_builder": {
                            "total": 3,
                            "by_status": {
                                "success": 2,
                                "failed": 1,
                                "running": 0,
                                "other": 0,
                            },
                            "last_run_started_at": "2024-01-15T10:00:00+00:00",
                            "last_run_status": "success",
                        }
                    },
                },
            },
        },
    }

    result = runner.invoke(app, ["control", "summary"])

    assert result.exit_code == 0
    assert "CONTROL_SUMMARY" in result.stderr
    assert "ok=true" in result.stderr

    output_json = json.loads(result.stdout)
    assert output_json["ok"] is True
    assert "generated_at" in output_json
    assert len(output_json["components"]) == 4
    assert output_json["components"]["status"]["ok"] is True
    assert output_json["components"]["tables"]["ok"] is True
    assert output_json["components"]["schema"]["ok"] is True
    assert output_json["components"]["pipeline_status"]["ok"] is True


@patch("pmagent.cli.compute_control_summary")
def test_control_summary_mixed(mock_summary, runner):
    """Test control summary when some components are db_on and some db_off."""
    mock_summary.return_value = {
        "ok": False,  # One db_on component failed
        "generated_at": "2024-01-15T10:30:00+00:00",
        "components": {
            "status": {
                "ok": True,
                "mode": "ready",
                "reason": None,
                "tables": {},
            },
            "tables": {
                "ok": False,
                "mode": "db_off",
                "error": "Connection failed",
                "tables": {},
            },
            "schema": {
                "ok": True,
                "mode": "db_on",
                "reason": None,
                "tables": {},
            },
            "pipeline_status": {
                "ok": False,
                "mode": "db_off",
                "reason": "Connection failed",
                "window_hours": 24,
                "summary": {
                    "total_runs": 0,
                    "pipelines": {},
                },
            },
        },
    }

    result = runner.invoke(app, ["control", "summary"])

    assert result.exit_code == 0
    assert "CONTROL_SUMMARY" in result.stderr

    output_json = json.loads(result.stdout)
    assert "ok" in output_json
    assert "components" in output_json
    assert len(output_json["components"]) == 4


@patch("pmagent.cli.compute_control_summary")
def test_control_summary_json_only(mock_summary, runner):
    """Test control summary with --json-only flag."""
    mock_summary.return_value = {
        "ok": True,
        "generated_at": "2024-01-15T10:30:00+00:00",
        "components": {
            "status": {"ok": True, "mode": "ready"},
            "tables": {"ok": True, "mode": "db_on"},
            "schema": {"ok": True, "mode": "db_on"},
            "pipeline_status": {"ok": True, "mode": "db_on"},
        },
    }

    result = runner.invoke(app, ["control", "summary", "--json-only"])

    assert result.exit_code == 0
    assert "CONTROL_SUMMARY" not in result.stderr  # No human summary on stderr
    assert json.loads(result.stdout) == mock_summary.return_value


@patch("pmagent.cli.compute_control_summary")
def test_control_summary_with_errors(mock_summary, runner):
    """Test control summary when components raise exceptions."""
    mock_summary.return_value = {
        "ok": False,
        "generated_at": "2024-01-15T10:30:00+00:00",
        "components": {
            "status": {
                "ok": True,
                "mode": "ready",
                "reason": None,
                "tables": {},
            },
            "tables": {
                "ok": False,
                "mode": "error",
                "error": "Exception: Connection timeout",
                "tables": {},
            },
            "schema": {
                "ok": True,
                "mode": "db_on",
                "reason": None,
                "tables": {},
            },
            "pipeline_status": {
                "ok": False,
                "mode": "error",
                "reason": "Exception: Query failed",
                "window_hours": 24,
                "summary": {
                    "total_runs": 0,
                    "pipelines": {},
                },
            },
        },
    }

    result = runner.invoke(app, ["control", "summary"])

    assert result.exit_code == 0
    assert "CONTROL_SUMMARY" in result.stderr

    output_json = json.loads(result.stdout)
    assert output_json["ok"] is False
    assert output_json["components"]["tables"]["mode"] == "error"
    assert output_json["components"]["pipeline_status"]["mode"] == "error"
