"""Tests for pmagent CLI graph commands (Phase-3B Feature #5)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from pmagent.cli import app


@pytest.fixture
def runner():
    """Create a Typer CLI test runner."""
    return CliRunner()


@patch("pmagent.cli.compute_graph_overview")
def test_graph_overview_db_off_via_cli(mock_overview, runner):
    """Test graph overview when database is off."""
    mock_overview.return_value = {
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

    result = runner.invoke(app, ["graph", "overview"])

    assert result.exit_code == 0
    assert "GRAPH_OVERVIEW" in result.stderr
    assert "mode=db_off" in result.stderr
    assert '"mode": "db_off"' in result.stdout


@patch("pmagent.cli.compute_graph_overview")
def test_graph_overview_ready_via_cli(mock_overview, runner):
    """Test graph overview when database is ready."""
    mock_overview.return_value = {
        "ok": True,
        "mode": "db_on",
        "stats": {
            "nodes": 100,
            "edges": 200,
            "avg_degree": 4.0,
            "snapshot_count": 1,
            "last_import_at": "2024-01-15T10:30:00+00:00",
        },
        "reason": None,
    }

    result = runner.invoke(app, ["graph", "overview"])

    assert result.exit_code == 0
    assert "GRAPH_OVERVIEW" in result.stderr
    assert "mode=db_on" in result.stderr
    assert '"nodes": 100' in result.stdout
    assert '"edges": 200' in result.stdout


@patch("pmagent.cli.import_graph_stats")
def test_graph_import_success(mock_import, runner, tmp_path):
    """Test successful graph import."""
    test_file = tmp_path / "graph_stats.json"
    test_file.write_text('{"nodes": 100, "edges": 200}')

    mock_import.return_value = {
        "ok": True,
        "inserted": 7,
        "errors": [],
        "source_path": str(test_file),
        "snapshot_id": "123e4567-e89b-12d3-a456-426614174000",
    }

    result = runner.invoke(app, ["graph", "import", "--input", str(test_file)])

    assert result.exit_code == 0
    assert "GRAPH_IMPORT" in result.stderr
    assert "snapshots_imported=1" in result.stderr
    assert "rows_inserted=7" in result.stderr
    assert '"ok": true' in result.stdout
    mock_import.assert_called_once_with(test_file)


@patch("pmagent.cli.import_graph_stats")
def test_graph_import_failure(mock_import, runner, tmp_path):
    """Test graph import failure."""
    test_file = tmp_path / "graph_stats.json"
    test_file.write_text('{"nodes": 100}')

    mock_import.return_value = {
        "ok": False,
        "inserted": 0,
        "errors": ["db_driver_missing: database driver not installed"],
        "source_path": str(test_file),
        "snapshot_id": None,
    }

    result = runner.invoke(app, ["graph", "import", "--input", str(test_file)])

    assert result.exit_code == 1
    assert "GRAPH_IMPORT" in result.stderr
    assert "failed" in result.stderr
    assert '"ok": false' in result.stdout


@patch("pmagent.cli.import_graph_stats")
def test_graph_import_default_path(mock_import, runner):
    """Test graph import with default path."""
    default_path = Path("exports/graph_stats.json")
    mock_import.return_value = {
        "ok": True,
        "inserted": 5,
        "errors": [],
        "source_path": str(default_path),
        "snapshot_id": "123e4567-e89b-12d3-a456-426614174000",
    }

    result = runner.invoke(app, ["graph", "import"])

    assert result.exit_code == 0
    assert "GRAPH_IMPORT" in result.stderr
    # Verify default path was used
    mock_import.assert_called_once_with(default_path)


@patch("pmagent.cli.compute_graph_overview")
def test_graph_overview_json_only(mock_overview, runner):
    """Test graph overview with --json-only flag."""
    mock_overview.return_value = {
        "ok": True,
        "mode": "db_on",
        "stats": {"nodes": 100, "edges": 200},
    }

    result = runner.invoke(app, ["graph", "overview", "--json-only"])

    assert result.exit_code == 0
    assert "GRAPH_OVERVIEW" not in result.stdout
    assert "GRAPH_OVERVIEW" not in result.stderr
    # Should have JSON
    data = json.loads(result.stdout)
    assert data["ok"] is True

