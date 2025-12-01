"""
Tests for Phase-3A Step-6: DB health smoke target.

Verifies that db.health.smoke produces correct summary output for all modes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


class TestDbHealthSmoke:
    """Test DB health smoke summary output."""

    def test_summary_ready_mode(self):
        """Test summary for ready mode."""
        from scripts.db.print_db_health_summary import print_summary

        health_json = {
            "ok": True,
            "mode": "ready",
            "checks": {
                "driver_available": True,
                "connection_ok": True,
                "graph_stats_ready": True,
            },
            "details": {"errors": []},
        }

        summary = print_summary(health_json)
        assert "mode=ready" in summary
        assert "all checks passed" in summary

    def test_summary_db_off_driver_missing(self):
        """Test summary for db_off mode (driver missing)."""
        from scripts.db.print_db_health_summary import print_summary

        health_json = {
            "ok": False,
            "mode": "db_off",
            "checks": {
                "driver_available": False,
                "connection_ok": False,
                "graph_stats_ready": False,
            },
            "details": {"errors": ["driver_missing: Postgres database driver not installed"]},
        }

        summary = print_summary(health_json)
        assert "mode=db_off" in summary
        assert "driver not installed" in summary

    def test_summary_db_off_connection_failed(self):
        """Test summary for db_off mode (connection failed)."""
        from scripts.db.print_db_health_summary import print_summary

        health_json = {
            "ok": False,
            "mode": "db_off",
            "checks": {
                "driver_available": True,
                "connection_ok": False,
                "graph_stats_ready": False,
            },
            "details": {"errors": ["connection_failed: Connection refused"]},
        }

        summary = print_summary(health_json)
        assert "mode=db_off" in summary
        assert "connection failed" in summary

    def test_summary_partial_mode(self):
        """Test summary for partial mode (table missing)."""
        from scripts.db.print_db_health_summary import print_summary

        health_json = {
            "ok": False,
            "mode": "partial",
            "checks": {
                "driver_available": True,
                "connection_ok": True,
                "graph_stats_ready": False,
            },
            "details": {
                "errors": [
                    "graph_stats_table_missing: gematria.graph_stats_snapshots does not exist"
                ]
            },
        }

        summary = print_summary(health_json)
        assert "mode=partial" in summary
        assert "graph_stats table missing" in summary

    def test_summary_unknown_mode(self):
        """Test summary for unknown/error mode."""
        from scripts.db.print_db_health_summary import print_summary

        health_json = {
            "ok": False,
            "mode": "unknown",
            "checks": {},
            "details": {"errors": ["unexpected_error: Something went wrong"]},
        }

        summary = print_summary(health_json)
        assert "mode=unknown" in summary
        assert "Something went wrong" in summary or "unknown status" in summary

    def test_main_reads_stdin(self, capsys):
        """Test main function reads JSON from stdin."""
        from scripts.db.print_db_health_summary import main
        import io

        # Mock stdin with valid JSON
        test_json = {
            "ok": True,
            "mode": "ready",
            "checks": {"driver_available": True, "connection_ok": True, "graph_stats_ready": True},
            "details": {"errors": []},
        }

        with patch("sys.stdin", io.StringIO(json.dumps(test_json))):
            result = main()
            assert result == 0
            captured = capsys.readouterr()
            assert "DB_HEALTH: mode=ready" in captured.out

    def test_main_handles_invalid_json(self, capsys):
        """Test main function handles invalid JSON gracefully."""
        from scripts.db.print_db_health_summary import main
        import io

        with patch("sys.stdin", io.StringIO("not json")):
            result = main()
            assert result == 1
            captured = capsys.readouterr()
            assert "DB_HEALTH: mode=error" in captured.err
