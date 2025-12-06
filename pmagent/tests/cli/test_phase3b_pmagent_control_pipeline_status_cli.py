"""Tests for pmagent CLI control pipeline-status command (Phase-3B Feature #9)."""

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


@patch("pmagent.cli.compute_control_pipeline_status")
def test_control_pipeline_status_db_off(mock_status, runner):
    """Test control pipeline-status when database is off."""
    mock_status.return_value = {
        "ok": False,
        "mode": "db_off",
        "reason": "Postgres database driver not available",
        "window_hours": 24,
        "summary": {
            "total_runs": 0,
            "pipelines": {},
        },
    }

    result = runner.invoke(app, ["control", "pipeline-status"])

    assert result.exit_code == 0
    assert "CONTROL_PIPELINE_STATUS" in result.stderr
    assert "mode=db_off" in result.stderr
    assert "window_hours=24" in result.stderr
    assert json.loads(result.stdout) == {
        "ok": False,
        "mode": "db_off",
        "reason": "Postgres database driver not available",
        "window_hours": 24,
        "summary": {
            "total_runs": 0,
            "pipelines": {},
        },
    }


@patch("pmagent.cli.compute_control_pipeline_status")
def test_control_pipeline_status_db_on_empty(mock_status, runner):
    """Test control pipeline-status when database is on but no runs found."""
    mock_status.return_value = {
        "ok": True,
        "mode": "db_on",
        "reason": None,
        "window_hours": 24,
        "summary": {
            "total_runs": 0,
            "pipelines": {},
        },
    }

    result = runner.invoke(app, ["control", "pipeline-status"])

    assert result.exit_code == 0
    assert "CONTROL_PIPELINE_STATUS" in result.stderr
    assert "mode=db_on" in result.stderr
    assert "total_runs=0" in result.stderr
    assert "pipelines=none" in result.stderr
    assert json.loads(result.stdout) == {
        "ok": True,
        "mode": "db_on",
        "reason": None,
        "window_hours": 24,
        "summary": {
            "total_runs": 0,
            "pipelines": {},
        },
    }


@patch("pmagent.cli.compute_control_pipeline_status")
def test_control_pipeline_status_db_on_with_runs(mock_status, runner):
    """Test control pipeline-status when database is on and runs are present."""
    mock_status.return_value = {
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
                    "last_run_started_at": "2024-01-15T10:30:00+00:00",
                    "last_run_status": "success",
                },
                "noun_extractor": {
                    "total": 2,
                    "by_status": {
                        "success": 2,
                        "failed": 0,
                        "running": 0,
                        "other": 0,
                    },
                    "last_run_started_at": "2024-01-15T09:15:00+00:00",
                    "last_run_status": "success",
                },
            },
        },
    }

    result = runner.invoke(app, ["control", "pipeline-status"])

    assert result.exit_code == 0
    assert "CONTROL_PIPELINE_STATUS" in result.stderr
    assert "mode=db_on" in result.stderr
    assert "total_runs=5" in result.stderr
    assert "graph_builder" in result.stderr
    assert "noun_extractor" in result.stderr
    output_json = json.loads(result.stdout)
    assert output_json["ok"] is True
    assert output_json["mode"] == "db_on"
    assert output_json["summary"]["total_runs"] == 5
    assert "graph_builder" in output_json["summary"]["pipelines"]
    assert "noun_extractor" in output_json["summary"]["pipelines"]


@patch("pmagent.cli.compute_control_pipeline_status")
def test_control_pipeline_status_custom_window(mock_status, runner):
    """Test control pipeline-status with custom window hours."""
    mock_status.return_value = {
        "ok": True,
        "mode": "db_on",
        "reason": None,
        "window_hours": 48,
        "summary": {
            "total_runs": 0,
            "pipelines": {},
        },
    }

    result = runner.invoke(app, ["control", "pipeline-status", "--window-hours", "48"])

    assert result.exit_code == 0
    assert "window_hours=48" in result.stderr
    mock_status.assert_called_once_with(window_hours=48)


def test_control_pipeline_status_json_only(runner):
    """Test control pipeline-status with --json-only flag."""
    with patch("pmagent.cli.compute_control_pipeline_status") as mock_status:
        mock_status.return_value = {
            "ok": True,
            "mode": "db_on",
            "reason": None,
            "window_hours": 24,
            "summary": {
                "total_runs": 1,
                "pipelines": {
                    "test_pipeline": {
                        "total": 1,
                        "by_status": {
                            "success": 1,
                            "failed": 0,
                            "running": 0,
                            "other": 0,
                        },
                        "last_run_started_at": "2024-01-15T10:30:00+00:00",
                        "last_run_status": "success",
                    }
                },
            },
        }
        result = runner.invoke(app, ["control", "pipeline-status", "--json-only"])

        assert result.exit_code == 0
        assert "CONTROL_PIPELINE_STATUS" not in result.stderr  # No human summary on stderr
        assert json.loads(result.stdout) == mock_status.return_value


@patch("pmagent.cli.compute_control_pipeline_status")
def test_control_pipeline_status_db_error(mock_status, runner):
    """Test control pipeline-status when a database error occurs."""
    mock_status.return_value = {
        "ok": False,
        "mode": "db_off",
        "reason": "Connection error: could not connect to server",
        "window_hours": 24,
        "summary": {
            "total_runs": 0,
            "pipelines": {},
        },
    }

    result = runner.invoke(app, ["control", "pipeline-status"])

    assert result.exit_code == 0
    assert "CONTROL_PIPELINE_STATUS" in result.stderr
    assert "mode=db_off" in result.stderr
    assert "Connection error" in result.stderr
    assert json.loads(result.stdout) == mock_status.return_value
