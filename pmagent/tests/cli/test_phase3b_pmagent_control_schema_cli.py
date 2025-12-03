"""Tests for pmagent CLI control schema command (Phase-3B Feature #8)."""

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


@patch("pmagent.cli.compute_control_schema")
def test_control_schema_db_off(mock_schema, runner):
    """Test control schema when database is off."""
    mock_schema.return_value = {
        "ok": False,
        "mode": "db_off",
        "reason": "Postgres database driver not available",
        "tables": {},
    }

    result = runner.invoke(app, ["control", "schema"])

    assert result.exit_code == 0
    assert "CONTROL_SCHEMA" in result.stderr
    assert "mode=db_off" in result.stderr
    assert "Postgres database driver not available" in result.stderr

    # Verify JSON output
    output_json = json.loads(result.stdout)
    assert output_json["ok"] is False
    assert output_json["mode"] == "db_off"
    assert output_json["tables"] == {}


@patch("pmagent.cli.compute_control_schema")
def test_control_schema_db_on(mock_schema, runner):
    """Test control schema when database is on."""
    mock_schema.return_value = {
        "ok": True,
        "mode": "db_on",
        "reason": None,
        "tables": {
            "control.agent_run": {
                "columns": [
                    {
                        "name": "id",
                        "data_type": "uuid",
                        "is_nullable": False,
                        "default": "gen_random_uuid()",
                    },
                    {
                        "name": "project_id",
                        "data_type": "bigint",
                        "is_nullable": False,
                        "default": None,
                    },
                ],
                "primary_key": ["id"],
                "indexes": [
                    {
                        "name": "idx_agent_run_project",
                        "columns": ["project_id"],
                        "unique": False,
                    },
                ],
            },
            "public.ai_interactions": {
                "columns": [
                    {
                        "name": "id",
                        "data_type": "integer",
                        "is_nullable": False,
                        "default": "nextval('ai_interactions_id_seq'::regclass)",
                    },
                ],
                "primary_key": ["id"],
                "indexes": [],
            },
        },
    }

    result = runner.invoke(app, ["control", "schema"])

    assert result.exit_code == 0
    assert "CONTROL_SCHEMA" in result.stderr
    assert "mode=db_on" in result.stderr

    # Verify JSON output
    output_json = json.loads(result.stdout)
    assert output_json["ok"] is True
    assert output_json["mode"] == "db_on"
    assert "tables" in output_json
    assert "control.agent_run" in output_json["tables"]
    assert "public.ai_interactions" in output_json["tables"]

    # Verify table structure
    agent_run = output_json["tables"]["control.agent_run"]
    assert "columns" in agent_run
    assert "primary_key" in agent_run
    assert "indexes" in agent_run
    assert len(agent_run["columns"]) == 2
    assert agent_run["primary_key"] == ["id"]


@patch("pmagent.cli.compute_control_schema")
def test_control_schema_json_only(mock_schema, runner):
    """Test control schema with --json-only flag."""
    mock_schema.return_value = {
        "ok": False,
        "mode": "db_off",
        "reason": "Database not available",
        "tables": {},
    }

    result = runner.invoke(app, ["control", "schema", "--json-only"])

    assert result.exit_code == 0
    # Should not have stderr output with --json-only
    assert "CONTROL_SCHEMA" not in result.stderr

    # Verify JSON output
    output_json = json.loads(result.stdout)
    assert output_json["ok"] is False
    assert output_json["mode"] == "db_off"


@patch("pmagent.cli.compute_control_schema")
def test_control_schema_empty_tables(mock_schema, runner):
    """Test control schema when no tables are found."""
    mock_schema.return_value = {
        "ok": True,
        "mode": "db_on",
        "reason": None,
        "tables": {},
    }

    result = runner.invoke(app, ["control", "schema"])

    assert result.exit_code == 0
    assert "CONTROL_SCHEMA" in result.stderr
    assert "mode=db_on" in result.stderr

    # Verify JSON output
    output_json = json.loads(result.stdout)
    assert output_json["ok"] is True
    assert output_json["tables"] == {}


@patch("pmagent.cli.compute_control_schema")
def test_control_schema_table_structure(mock_schema, runner):
    """Test that table structure includes all required fields."""
    mock_schema.return_value = {
        "ok": True,
        "mode": "db_on",
        "reason": None,
        "tables": {
            "control.tool_catalog": {
                "columns": [
                    {
                        "name": "id",
                        "data_type": "uuid",
                        "is_nullable": False,
                        "default": "gen_random_uuid()",
                    },
                    {
                        "name": "name",
                        "data_type": "text",
                        "is_nullable": False,
                        "default": None,
                    },
                ],
                "primary_key": ["id"],
                "indexes": [
                    {
                        "name": "idx_tool_catalog_project",
                        "columns": ["project_id"],
                        "unique": False,
                    },
                    {
                        "name": "idx_tool_catalog_ring",
                        "columns": ["ring"],
                        "unique": False,
                    },
                ],
            },
        },
    }

    result = runner.invoke(app, ["control", "schema"])

    assert result.exit_code == 0

    # Verify JSON structure
    output_json = json.loads(result.stdout)
    table = output_json["tables"]["control.tool_catalog"]

    # Verify columns structure
    assert len(table["columns"]) == 2
    for col in table["columns"]:
        assert "name" in col
        assert "data_type" in col
        assert "is_nullable" in col
        assert "default" in col

    # Verify primary key
    assert isinstance(table["primary_key"], list)
    assert "id" in table["primary_key"]

    # Verify indexes structure
    assert len(table["indexes"]) == 2
    for idx in table["indexes"]:
        assert "name" in idx
        assert "columns" in idx
        assert "unique" in idx
        assert isinstance(idx["columns"], list)


@patch("pmagent.cli.compute_control_schema")
def test_control_schema_connection_error(mock_schema, runner):
    """Test control schema when connection fails."""
    mock_schema.return_value = {
        "ok": False,
        "mode": "db_off",
        "reason": "Connection error: connection refused",
        "tables": {},
    }

    result = runner.invoke(app, ["control", "schema"])

    assert result.exit_code == 0
    assert "CONTROL_SCHEMA" in result.stderr
    assert "mode=db_off" in result.stderr
    assert "connection refused" in result.stderr

    # Verify JSON output
    output_json = json.loads(result.stdout)
    assert output_json["ok"] is False
    assert output_json["mode"] == "db_off"
    assert "connection refused" in output_json["reason"]
