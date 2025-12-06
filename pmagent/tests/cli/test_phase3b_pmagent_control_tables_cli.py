"""Tests for pmagent CLI control tables command (Phase-3B Feature #7)."""

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


@patch("pmagent.cli.compute_control_tables")
def test_control_tables_db_off(mock_tables, runner):
    """Test control tables when database is off."""
    mock_tables.return_value = {
        "ok": False,
        "mode": "db_off",
        "error": "Postgres database driver not available",
        "tables": {},
    }

    result = runner.invoke(app, ["control", "tables"])

    assert result.exit_code == 0
    assert "CONTROL_TABLES" in result.stderr
    assert "mode=db_off" in result.stderr
    assert '"mode": "db_off"' in result.stdout
    assert '"ok": false' in result.stdout


@patch("pmagent.cli.compute_control_tables")
def test_control_tables_db_on(mock_tables, runner):
    """Test control tables when database is on."""
    mock_tables.return_value = {
        "ok": True,
        "mode": "db_on",
        "error": None,
        "tables": {
            "public.ai_interactions": 42,
            "public.governance_artifacts": 15,
            "control.agent_run": 8,
            "control.tool_catalog": 5,
            "gematria.graph_stats_snapshots": 3,
            "gematria.concepts": 100,
        },
    }

    result = runner.invoke(app, ["control", "tables"])

    assert result.exit_code == 0
    assert "CONTROL_TABLES" in result.stderr
    assert "mode=db_on" in result.stderr
    assert '"ok": true' in result.stdout
    assert '"mode": "db_on"' in result.stdout
    # Check table counts in JSON
    data = json.loads(result.stdout)
    assert data["tables"]["public.ai_interactions"] == 42
    assert data["tables"]["gematria.concepts"] == 100
    # Check summary includes schema counts
    assert "schemas=" in result.stderr


@patch("pmagent.cli.compute_control_tables")
def test_control_tables_with_null_counts(mock_tables, runner):
    """Test control tables when some tables have null counts."""
    mock_tables.return_value = {
        "ok": True,
        "mode": "db_on",
        "error": None,
        "tables": {
            "public.ai_interactions": 10,
            "public.governance_artifacts": None,  # Query failed for this table
            "control.agent_run": 5,
        },
    }

    result = runner.invoke(app, ["control", "tables"])

    assert result.exit_code == 0
    assert "CONTROL_TABLES" in result.stderr
    assert "mode=db_on" in result.stderr
    # Check JSON shows null for failed query
    data = json.loads(result.stdout)
    assert data["tables"]["public.governance_artifacts"] is None
    assert data["tables"]["public.ai_interactions"] == 10


@patch("pmagent.cli.compute_control_tables")
def test_control_tables_empty_database(mock_tables, runner):
    """Test control tables when database has no tables."""
    mock_tables.return_value = {
        "ok": True,
        "mode": "db_on",
        "error": None,
        "tables": {},
    }

    result = runner.invoke(app, ["control", "tables"])

    assert result.exit_code == 0
    assert "CONTROL_TABLES" in result.stderr
    assert "mode=db_on" in result.stderr
    data = json.loads(result.stdout)
    assert data["tables"] == {}


@patch("pmagent.cli.compute_control_tables")
def test_control_tables_json_only(mock_tables, runner):
    """Test control tables with --json-only flag."""
    mock_tables.return_value = {
        "ok": True,
        "mode": "db_on",
        "error": None,
        "tables": {
            "public.ai_interactions": 10,
        },
    }

    result = runner.invoke(app, ["control", "tables", "--json-only"])

    assert result.exit_code == 0
    assert "CONTROL_TABLES" not in result.stdout
    assert "CONTROL_TABLES" not in result.stderr
    # Should have JSON only
    data = json.loads(result.stdout)
    assert data["ok"] is True
    assert data["mode"] == "db_on"


@patch("pmagent.cli.compute_control_tables")
def test_control_tables_connection_error(mock_tables, runner):
    """Test control tables when connection fails."""
    mock_tables.return_value = {
        "ok": False,
        "mode": "db_off",
        "error": "Connection error: connection refused",
        "tables": {},
    }

    result = runner.invoke(app, ["control", "tables"])

    assert result.exit_code == 0
    assert "CONTROL_TABLES" in result.stderr
    assert "mode=db_off" in result.stderr
    assert '"ok": false' in result.stdout
    data = json.loads(result.stdout)
    assert "error" in data
