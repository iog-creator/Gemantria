"""Tests for Phase-3A DB health guard."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


class TestDbHealthGuard:
    """Test DB health guard behavior."""

    @patch("scripts.guards.guard_db_health.get_control_engine")
    def test_driver_missing(self, mock_get_engine):
        """Test guard returns db_off when driver is missing."""
        from scripts.guards.guard_db_health import check_db_health
        from pmagent.db.loader import DbDriverMissingError

        mock_get_engine.side_effect = DbDriverMissingError("Postgres database driver not installed")

        result = check_db_health()

        assert result["ok"] is False
        assert result["mode"] == "db_off"
        assert result["checks"]["driver_available"] is False
        assert result["checks"]["connection_ok"] is False
        assert result["checks"]["graph_stats_ready"] is False
        assert len(result["details"]["errors"]) > 0
        assert any("driver_missing" in err for err in result["details"]["errors"])

    @patch("scripts.guards.guard_db_health.get_control_engine")
    def test_connection_failure(self, mock_get_engine):
        """Test guard returns db_off when connection fails."""
        from sqlalchemy.exc import OperationalError

        from scripts.guards.guard_db_health import check_db_health

        # Mock engine that raises OperationalError on connect
        mock_engine = MagicMock()
        mock_engine.connect.side_effect = OperationalError("Connection failed", None, None)
        mock_get_engine.return_value = mock_engine

        result = check_db_health()

        assert result["ok"] is False
        assert result["mode"] == "db_off"
        assert result["checks"]["driver_available"] is True
        assert result["checks"]["connection_ok"] is False
        assert result["checks"]["graph_stats_ready"] is False
        assert len(result["details"]["errors"]) > 0
        assert any("connection_failed" in err for err in result["details"]["errors"])

    @patch("scripts.guards.guard_db_health.get_control_engine")
    def test_graph_stats_table_missing(self, mock_get_engine):
        """Test guard returns partial when graph_stats table is missing."""
        from sqlalchemy.exc import ProgrammingError

        from scripts.guards.guard_db_health import check_db_health

        # Mock engine with successful connection but table missing
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=None)

        # First connect() succeeds (connection check)
        # Second connect() raises ProgrammingError (table missing)
        mock_engine.connect.side_effect = [
            MagicMock(__enter__=MagicMock(return_value=mock_conn), __exit__=MagicMock(return_value=None)),
            MagicMock(
                __enter__=MagicMock(side_effect=ProgrammingError("relation does not exist", None, None)),
                __exit__=MagicMock(return_value=None),
            ),
        ]

        # Mock execute for connection check
        mock_conn.execute = MagicMock()

        mock_get_engine.return_value = mock_engine

        result = check_db_health()

        assert result["ok"] is False
        assert result["mode"] == "partial"
        assert result["checks"]["driver_available"] is True
        assert result["checks"]["connection_ok"] is True
        assert result["checks"]["graph_stats_ready"] is False
        assert len(result["details"]["errors"]) > 0
        assert any("graph_stats_table_missing" in err for err in result["details"]["errors"])

    @patch("scripts.guards.guard_db_health.get_control_engine")
    def test_all_ready(self, mock_get_engine):
        """Test guard returns ready when all checks pass."""
        from scripts.guards.guard_db_health import check_db_health

        # Mock engine with all operations succeeding
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=None)
        mock_conn.execute = MagicMock()

        mock_engine.connect.return_value = MagicMock(
            __enter__=MagicMock(return_value=mock_conn), __exit__=MagicMock(return_value=None)
        )

        mock_get_engine.return_value = mock_engine

        result = check_db_health()

        assert result["ok"] is True
        assert result["mode"] == "ready"
        assert result["checks"]["driver_available"] is True
        assert result["checks"]["connection_ok"] is True
        assert result["checks"]["graph_stats_ready"] is True
        assert len(result["details"]["errors"]) == 0

    @patch("scripts.guards.guard_db_health.check_db_health")
    def test_main_outputs_json(self, mock_check_health, capsys):
        """Test main() outputs valid JSON and exits 0."""
        import scripts.guards.guard_db_health

        mock_check_health.return_value = {
            "ok": True,
            "mode": "ready",
            "checks": {
                "driver_available": True,
                "connection_ok": True,
                "graph_stats_ready": True,
            },
            "details": {
                "errors": [],
            },
        }

        result = scripts.guards.guard_db_health.main()

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["ok"] is True
        assert data["mode"] == "ready"
