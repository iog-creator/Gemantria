"""Tests for Phase-3A graph stats importer."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from agentpm.db.loader import DbUnavailableError


class TestGraphStatsImport:
    """Test graph stats importer functionality."""

    @patch("scripts.db_import_graph_stats.get_control_engine")
    def test_import_happy_path(self, mock_get_engine, tmp_path):
        """Test successful import of graph_stats.json."""
        from scripts.db_import_graph_stats import import_graph_stats

        # Create test JSON file
        test_data = {
            "nodes": 100,
            "edges": 250,
            "clusters": 5,
            "density": 0.75,
            "centrality": {
                "avg_degree": 0.5,
                "avg_betweenness": 0.3,
            },
        }
        test_file = tmp_path / "graph_stats.json"
        test_file.write_text(json.dumps(test_data))

        # Mock engine and connection
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn
        mock_engine.begin.return_value.__exit__ = MagicMock(return_value=None)
        mock_get_engine.return_value = mock_engine

        # Mock execute result
        mock_result = MagicMock()
        mock_result.rowcount = (
            7  # nodes, edges, clusters, density, centrality, centrality.avg_degree, centrality.avg_betweenness
        )
        mock_conn.execute.return_value = mock_result

        # Run import
        result = import_graph_stats(test_file)

        # Assertions
        assert result["ok"] is True
        assert result["inserted"] == 7
        assert len(result["errors"]) == 0
        assert result["source_path"] == str(test_file)
        assert result["snapshot_id"] is not None

        # Verify engine.begin() was called
        mock_engine.begin.assert_called_once()
        # Verify execute was called (for insert)
        assert mock_conn.execute.called

    def test_import_missing_file(self):
        """Test import fails gracefully when source file is missing."""
        from scripts.db_import_graph_stats import import_graph_stats

        non_existent = Path("/nonexistent/graph_stats.json")
        result = import_graph_stats(non_existent)

        assert result["ok"] is False
        assert result["inserted"] == 0
        assert len(result["errors"]) > 0
        assert any("missing_export" in err for err in result["errors"])

    @patch("scripts.db_import_graph_stats.get_control_engine")
    def test_import_invalid_json(self, mock_get_engine, tmp_path):
        """Test import fails gracefully when JSON is invalid."""
        from scripts.db_import_graph_stats import import_graph_stats

        # Create invalid JSON file
        test_file = tmp_path / "graph_stats.json"
        test_file.write_text("{ invalid json }")

        result = import_graph_stats(test_file)

        assert result["ok"] is False
        assert result["inserted"] == 0
        assert len(result["errors"]) > 0
        assert any("invalid_json" in err for err in result["errors"])

    @patch("scripts.db_import_graph_stats.get_control_engine")
    def test_import_db_unavailable(self, mock_get_engine, tmp_path):
        """Test import fails gracefully when DB is unavailable."""
        from scripts.db_import_graph_stats import import_graph_stats

        # Create test JSON file
        test_data = {"nodes": 100}
        test_file = tmp_path / "graph_stats.json"
        test_file.write_text(json.dumps(test_data))

        # Mock engine to raise DbUnavailableError
        mock_get_engine.side_effect = DbUnavailableError("GEMATRIA_DSN not set")

        result = import_graph_stats(test_file)

        assert result["ok"] is False
        assert result["inserted"] == 0
        assert len(result["errors"]) > 0
        assert any("db_unavailable" in err for err in result["errors"])

    @patch("scripts.db_import_graph_stats.get_control_engine")
    def test_import_operational_error(self, mock_get_engine, tmp_path):
        """Test import fails gracefully on database connection errors."""
        from scripts.db_import_graph_stats import import_graph_stats
        from sqlalchemy.exc import OperationalError

        # Create test JSON file
        test_data = {"nodes": 100}
        test_file = tmp_path / "graph_stats.json"
        test_file.write_text(json.dumps(test_data))

        # Mock engine
        mock_engine = MagicMock()
        mock_get_engine.return_value = mock_engine

        # Mock begin() to raise OperationalError
        mock_engine.begin.side_effect = OperationalError("Connection failed", None, None)

        result = import_graph_stats(test_file)

        assert result["ok"] is False
        assert result["inserted"] == 0
        assert len(result["errors"]) > 0
        assert any("db_connection_error" in err for err in result["errors"])

    @patch("scripts.db_import_graph_stats.get_control_engine")
    def test_flatten_metrics(self, mock_get_engine, tmp_path):
        """Test that metrics are flattened correctly."""
        from scripts.db_import_graph_stats import flatten_metrics, import_graph_stats

        # Create test JSON with nested structure
        test_data = {
            "nodes": 100,
            "centrality": {
                "avg_degree": 0.5,
                "avg_betweenness": 0.3,
            },
        }
        test_file = tmp_path / "graph_stats.json"
        test_file.write_text(json.dumps(test_data))

        # Test flatten_metrics directly
        metrics = flatten_metrics(test_data)
        metric_names = [m[0] for m in metrics]

        assert "nodes" in metric_names
        assert "centrality" in metric_names
        assert "centrality.avg_degree" in metric_names
        assert "centrality.avg_betweenness" in metric_names

        # Test that import uses flattening correctly
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn
        mock_engine.begin.return_value.__exit__ = MagicMock(return_value=None)
        mock_get_engine.return_value = mock_engine

        mock_result = MagicMock()
        mock_result.rowcount = 4
        mock_conn.execute.return_value = mock_result

        result = import_graph_stats(test_file)
        assert result["ok"] is True
        assert result["inserted"] == 4

    @patch("scripts.db_import_graph_stats.get_control_engine")
    def test_import_driver_missing(self, mock_get_engine, tmp_path):
        """Test import fails gracefully when Postgres driver is missing."""
        from scripts.db_import_graph_stats import import_graph_stats
        from agentpm.db.loader import DbDriverMissingError

        # Create test JSON file
        test_data = {"nodes": 100}
        test_file = tmp_path / "graph_stats.json"
        test_file.write_text(json.dumps(test_data))

        # Mock engine to raise DbDriverMissingError
        mock_get_engine.side_effect = DbDriverMissingError("Postgres database driver not installed")

        result = import_graph_stats(test_file)

        assert result["ok"] is False
        assert result["inserted"] == 0
        assert len(result["errors"]) > 0
        assert any("db_driver_missing" in err for err in result["errors"])
        assert result.get("mode") == "db_off"
