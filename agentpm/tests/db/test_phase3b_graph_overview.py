"""
Tests for Phase-3B Feature #1: DB-backed graph overview.

Verifies that graph_overview handles DB-off/partial/ready modes correctly
and computes stats from graph_stats table.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from agentpm.db.models_graph_stats import GraphStatsSnapshot


class TestGraphOverview:
    """Test graph overview DB feature."""

    @patch("scripts.graph.graph_overview.check_db_health")
    def test_db_off_mode(self, mock_check_db_health):
        """Test overview returns ok:false with mode=db_off when DB is unavailable."""
        from scripts.graph.graph_overview import compute_graph_overview, print_human_summary

        # Mock DB health check to return db_off
        mock_check_db_health.return_value = {
            "ok": False,
            "mode": "db_off",
            "checks": {"driver_available": False, "connection_ok": False, "graph_stats_ready": False},
            "details": {"errors": ["driver_missing: Postgres database driver not installed"]},
        }

        overview = compute_graph_overview()

        assert overview["ok"] is False
        assert overview["mode"] == "db_off"
        assert overview["reason"] is not None
        assert "driver" in overview["reason"].lower() or "database" in overview["reason"].lower()

        summary = print_human_summary(overview)
        assert "mode=db_off" in summary

    @patch("scripts.graph.graph_overview.check_db_health")
    def test_partial_mode(self, mock_check_db_health):
        """Test overview returns ok:false with mode=partial when table is missing."""
        from scripts.graph.graph_overview import compute_graph_overview, print_human_summary

        # Mock DB health check to return partial (table missing)
        mock_check_db_health.return_value = {
            "ok": False,
            "mode": "partial",
            "checks": {
                "driver_available": True,
                "connection_ok": True,
                "graph_stats_ready": False,
            },
            "details": {"errors": ["graph_stats_table_missing: gematria.graph_stats_snapshots does not exist"]},
        }

        overview = compute_graph_overview()

        assert overview["ok"] is False
        assert overview["mode"] == "partial"
        assert overview["reason"] is not None

        summary = print_human_summary(overview)
        assert "mode=partial" in summary

    @patch("scripts.graph.graph_overview.check_db_health")
    @patch("scripts.graph.graph_overview.get_control_engine")
    def test_ready_basic_stats(self, mock_get_engine, mock_check_db_health):
        """Test overview computes stats correctly when DB is ready."""
        from scripts.graph.graph_overview import compute_graph_overview, print_human_summary

        # Mock DB health check to return ready
        mock_check_db_health.return_value = {
            "ok": True,
            "mode": "ready",
            "checks": {
                "driver_available": True,
                "connection_ok": True,
                "graph_stats_ready": True,
            },
            "details": {"errors": []},
        }

        # Mock SQLAlchemy session
        mock_engine = MagicMock()
        mock_session = MagicMock()
        mock_sessionmaker = MagicMock(return_value=mock_session)
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=None)

        # Mock latest snapshot query
        snapshot_id = uuid4()
        mock_session.execute.return_value.scalar_one_or_none.side_effect = [
            snapshot_id,  # Latest snapshot ID
            100,  # nodes
            200,  # edges
            None,  # avg_degree (not found, will calculate)
            1,  # snapshot_count
            datetime.now(timezone.utc),  # last_import_at
        ]

        # Mock count query for snapshot_count
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_count_result
        mock_session.execute.return_value.scalar_one_or_none.side_effect = [
            snapshot_id,
            100,
            200,
            None,
        ]
        mock_session.execute.return_value.scalar_one.return_value = 1
        mock_session.execute.return_value.scalar_one_or_none.side_effect = [
            snapshot_id,
            100,
            200,
            None,
            datetime.now(timezone.utc),
        ]

        # Fix the mock to handle multiple execute calls properly
        def execute_side_effect(query, *args, **kwargs):
            result = MagicMock()
            # Latest snapshot query
            if "snapshot_id" in str(query) and "order_by" in str(query):
                result.scalar_one_or_none.return_value = snapshot_id
            # Nodes query
            elif "nodes" in str(query):
                result.scalar_one_or_none.return_value = 100
            # Edges query
            elif "edges" in str(query):
                result.scalar_one_or_none.return_value = 200
            # Avg degree query
            elif "centrality.avg_degree" in str(query):
                result.scalar_one_or_none.return_value = None
            # Snapshot count query
            elif "count" in str(query) and "distinct" in str(query):
                result.scalar_one.return_value = 1
            # Last import query
            elif "max" in str(query) and "created_at" in str(query):
                result.scalar_one_or_none.return_value = datetime.now(timezone.utc)
            else:
                result.scalar_one_or_none.return_value = None
                result.scalar_one.return_value = 0
            return result

        mock_session.execute.side_effect = execute_side_effect
        mock_get_engine.return_value = mock_engine

        with patch("scripts.graph.graph_overview.sessionmaker", return_value=mock_sessionmaker):
            overview = compute_graph_overview()

        assert overview["ok"] is True
        assert overview["mode"] == "db_on"
        assert overview["stats"]["nodes"] == 100
        assert overview["stats"]["edges"] == 200
        assert overview["stats"]["avg_degree"] == 4.0  # (200 * 2) / 100
        assert overview["stats"]["snapshot_count"] == 1
        assert overview["stats"]["last_import_at"] is not None

        summary = print_human_summary(overview)
        assert "nodes=100" in summary
        assert "edges=200" in summary
        assert "avg_degree=4.00" in summary
        assert "snapshots=1" in summary

    @patch("scripts.graph.graph_overview.check_db_health")
    @patch("scripts.graph.graph_overview.get_control_engine")
    def test_ready_empty_graph(self, mock_get_engine, mock_check_db_health):
        """Test overview handles empty graph (zero nodes) without division-by-zero."""
        from scripts.graph.graph_overview import compute_graph_overview, print_human_summary

        # Mock DB health check to return ready
        mock_check_db_health.return_value = {
            "ok": True,
            "mode": "ready",
            "checks": {
                "driver_available": True,
                "connection_ok": True,
                "graph_stats_ready": True,
            },
            "details": {"errors": []},
        }

        # Mock SQLAlchemy session
        mock_engine = MagicMock()
        mock_session = MagicMock()
        mock_sessionmaker = MagicMock(return_value=mock_session)
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=None)

        snapshot_id = uuid4()

        def execute_side_effect(query, *args, **kwargs):
            result = MagicMock()
            if "snapshot_id" in str(query) and "order_by" in str(query):
                result.scalar_one_or_none.return_value = snapshot_id
            elif "nodes" in str(query):
                result.scalar_one_or_none.return_value = 0
            elif "edges" in str(query):
                result.scalar_one_or_none.return_value = 0
            elif "centrality.avg_degree" in str(query):
                result.scalar_one_or_none.return_value = None
            elif "count" in str(query) and "distinct" in str(query):
                result.scalar_one.return_value = 1
            elif "max" in str(query) and "created_at" in str(query):
                result.scalar_one_or_none.return_value = datetime.now(timezone.utc)
            else:
                result.scalar_one_or_none.return_value = None
                result.scalar_one.return_value = 0
            return result

        mock_session.execute.side_effect = execute_side_effect
        mock_get_engine.return_value = mock_engine

        with patch("scripts.graph.graph_overview.sessionmaker", return_value=mock_sessionmaker):
            overview = compute_graph_overview()

        assert overview["ok"] is True
        assert overview["mode"] == "db_on"
        assert overview["stats"]["nodes"] == 0
        assert overview["stats"]["edges"] == 0
        # avg_degree should be None when nodes=0 (avoid division by zero)
        assert overview["stats"]["avg_degree"] is None

        summary = print_human_summary(overview)
        assert "nodes=0" in summary
        assert "edges=0" in summary
        assert "avg_degree=N/A" in summary

    @patch("scripts.graph.graph_overview.check_db_health")
    @patch("scripts.graph.graph_overview.get_control_engine")
    def test_ready_no_snapshots(self, mock_get_engine, mock_check_db_health):
        """Test overview handles case with no snapshots in database."""
        from scripts.graph.graph_overview import compute_graph_overview, print_human_summary

        # Mock DB health check to return ready
        mock_check_db_health.return_value = {
            "ok": True,
            "mode": "ready",
            "checks": {
                "driver_available": True,
                "connection_ok": True,
                "graph_stats_ready": True,
            },
            "details": {"errors": []},
        }

        # Mock SQLAlchemy session
        mock_engine = MagicMock()
        mock_session = MagicMock()
        mock_sessionmaker = MagicMock(return_value=mock_session)
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=None)

        # Mock latest snapshot query to return None (no snapshots)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        mock_get_engine.return_value = mock_engine

        with patch("scripts.graph.graph_overview.sessionmaker", return_value=mock_sessionmaker):
            overview = compute_graph_overview()

        assert overview["ok"] is True
        assert overview["mode"] == "db_on"
        assert overview["reason"] == "no snapshots found"
        assert overview["stats"]["nodes"] is None
        assert overview["stats"]["edges"] is None

        summary = print_human_summary(overview)
        assert "mode=db_on" in summary or "no snapshots" in summary.lower()
