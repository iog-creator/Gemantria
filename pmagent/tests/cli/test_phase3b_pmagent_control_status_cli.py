"""Tests for pmagent CLI control status command (Phase-3B Feature #6)."""

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


@patch("pmagent.cli.compute_control_status")
def test_control_status_db_off(mock_status, runner):
    """Test control status when database is off."""
    mock_status.return_value = {
        "ok": False,
        "mode": "db_off",
        "reason": "Postgres database driver not available",
        "tables": {
            "public.ai_interactions": {
                "present": False,
                "row_count": None,
                "latest_created_at": None,
            },
            "public.governance_artifacts": {
                "present": False,
                "row_count": None,
                "latest_created_at": None,
            },
            "control.agent_run": {"present": False, "row_count": None, "latest_created_at": None},
            "control.tool_catalog": {
                "present": False,
                "row_count": None,
                "latest_created_at": None,
            },
            "gematria.graph_stats_snapshots": {
                "present": False,
                "row_count": None,
                "latest_created_at": None,
            },
        },
    }

    result = runner.invoke(app, ["control", "status"])

    assert result.exit_code == 0
    assert "CONTROL_STATUS" in result.stderr
    assert "mode=db_off" in result.stderr
    assert '"mode": "db_off"' in result.stdout
    assert '"ok": false' in result.stdout


@patch("pmagent.cli.compute_control_status")
def test_control_status_ready_with_tables(mock_status, runner):
    """Test control status when database is ready with tables."""
    mock_status.return_value = {
        "ok": True,
        "mode": "ready",
        "reason": None,
        "tables": {
            "public.ai_interactions": {
                "present": True,
                "row_count": 42,
                "latest_created_at": "2024-01-15T10:30:00+00:00",
            },
            "public.governance_artifacts": {
                "present": True,
                "row_count": 15,
                "latest_created_at": "2024-01-15T09:00:00+00:00",
            },
            "control.agent_run": {
                "present": True,
                "row_count": 8,
                "latest_created_at": None,
            },
            "control.tool_catalog": {
                "present": True,
                "row_count": 5,
                "latest_created_at": "2024-01-14T12:00:00+00:00",
            },
            "gematria.graph_stats_snapshots": {
                "present": True,
                "row_count": 3,
                "latest_created_at": "2024-01-15T11:00:00+00:00",
            },
        },
    }

    result = runner.invoke(app, ["control", "status"])

    assert result.exit_code == 0
    assert "CONTROL_STATUS" in result.stderr
    assert "mode=ready" in result.stderr
    assert '"ok": true' in result.stdout
    assert '"mode": "ready"' in result.stdout
    # Check table counts in summary
    assert "ai_interactions(42)" in result.stderr
    assert "governance_artifacts(15)" in result.stderr
    assert "agent_run(8)" in result.stderr
    # Check JSON output
    data = json.loads(result.stdout)
    assert data["tables"]["public.ai_interactions"]["row_count"] == 42
    assert data["tables"]["gematria.graph_stats_snapshots"]["row_count"] == 3


@patch("pmagent.cli.compute_control_status")
def test_control_status_missing_table(mock_status, runner):
    """Test control status when some tables are missing."""
    mock_status.return_value = {
        "ok": True,
        "mode": "ready",
        "reason": None,
        "tables": {
            "public.ai_interactions": {
                "present": True,
                "row_count": 10,
                "latest_created_at": "2024-01-15T10:30:00+00:00",
            },
            "public.governance_artifacts": {
                "present": False,
                "row_count": None,
                "latest_created_at": None,
            },
            "control.agent_run": {
                "present": True,
                "row_count": 5,
                "latest_created_at": None,
            },
            "control.tool_catalog": {
                "present": False,
                "row_count": None,
                "latest_created_at": None,
            },
            "gematria.graph_stats_snapshots": {
                "present": True,
                "row_count": 2,
                "latest_created_at": "2024-01-15T11:00:00+00:00",
            },
        },
    }

    result = runner.invoke(app, ["control", "status"])

    assert result.exit_code == 0
    assert "CONTROL_STATUS" in result.stderr
    assert "mode=ready" in result.stderr
    # Should only show present tables in summary
    assert "ai_interactions(10)" in result.stderr
    assert "governance_artifacts" not in result.stderr or "governance_artifacts(0)" not in result.stderr
    # Check JSON shows missing tables
    data = json.loads(result.stdout)
    assert data["tables"]["public.governance_artifacts"]["present"] is False
    assert data["tables"]["public.governance_artifacts"]["row_count"] is None


@patch("pmagent.cli.compute_control_status")
def test_control_status_malformed_response(mock_status, runner):
    """Test control status handles malformed responses gracefully."""
    # Simulate a partial/malformed response
    mock_status.return_value = {
        "ok": False,
        "mode": "partial",
        "reason": "Connection error during table inspection",
        "tables": {},  # Empty tables dict
    }

    result = runner.invoke(app, ["control", "status"])

    assert result.exit_code == 0
    assert "CONTROL_STATUS" in result.stderr
    assert '"ok": false' in result.stdout
    # Should still output valid JSON
    data = json.loads(result.stdout)
    assert data["mode"] == "partial"


@patch("pmagent.cli.compute_control_status")
def test_control_status_json_only(mock_status, runner):
    """Test control status with --json-only flag."""
    mock_status.return_value = {
        "ok": True,
        "mode": "ready",
        "reason": None,
        "tables": {
            "public.ai_interactions": {
                "present": True,
                "row_count": 10,
                "latest_created_at": "2024-01-15T10:30:00+00:00",
            },
        },
    }

    result = runner.invoke(app, ["control", "status", "--json-only"])

    assert result.exit_code == 0
    assert "CONTROL_STATUS" not in result.stdout
    assert "CONTROL_STATUS" not in result.stderr
    # Should have JSON only
    data = json.loads(result.stdout)
    assert data["ok"] is True
    assert data["mode"] == "ready"


@patch("pmagent.cli.compute_control_status")
def test_control_status_empty_tables(mock_status, runner):
    """Test control status when all tables are empty."""
    mock_status.return_value = {
        "ok": True,
        "mode": "ready",
        "reason": None,
        "tables": {
            "public.ai_interactions": {
                "present": True,
                "row_count": 0,
                "latest_created_at": None,
            },
            "public.governance_artifacts": {
                "present": True,
                "row_count": 0,
                "latest_created_at": None,
            },
            "control.agent_run": {
                "present": True,
                "row_count": 0,
                "latest_created_at": None,
            },
            "control.tool_catalog": {
                "present": True,
                "row_count": 0,
                "latest_created_at": None,
            },
            "gematria.graph_stats_snapshots": {
                "present": True,
                "row_count": 0,
                "latest_created_at": None,
            },
        },
    }

    result = runner.invoke(app, ["control", "status"])

    assert result.exit_code == 0
    assert "CONTROL_STATUS" in result.stderr
    assert "mode=ready" in result.stderr
    # Should show tables with 0 counts
    assert "ai_interactions(0)" in result.stderr
    data = json.loads(result.stdout)
    assert data["tables"]["public.ai_interactions"]["row_count"] == 0
