"""Tests for Phase-3B system health aggregate."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))


class TestSystemHealth:
    """Test system health aggregate behavior."""

    @patch("scripts.system.system_health.subprocess.run")
    def test_all_off(self, mock_subprocess_run, capsys):
        """Test system health when all components are off."""
        from scripts.system.system_health import compute_system_health, print_human_summary

        # Mock subprocess responses
        def mock_run_side_effect(cmd, **kwargs):
            mock_result = MagicMock()
            cmd_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
            if "guard_db_health" in cmd_str:
                mock_result.stdout = json.dumps(
                    {
                        "ok": False,
                        "mode": "db_off",
                        "checks": {
                            "driver_available": False,
                            "connection_ok": False,
                            "graph_stats_ready": False,
                        },
                        "details": {"errors": ["driver_missing: Postgres driver not installed"]},
                    }
                )
            elif "guard_lm_health" in cmd_str:
                mock_result.stdout = json.dumps(
                    {
                        "ok": False,
                        "mode": "lm_off",
                        "details": {
                            "endpoint": "http://127.0.0.1:1234",
                            "errors": ["connection_refused: Connection refused"],
                        },
                    }
                )
            elif "graph_overview" in cmd_str:
                mock_result.stdout = json.dumps(
                    {
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
                )
            else:
                mock_result.stdout = "{}"
            mock_result.returncode = 0
            return mock_result

        mock_subprocess_run.side_effect = mock_run_side_effect

        result = compute_system_health()

        assert result["ok"] is False
        assert result["components"]["db"]["mode"] == "db_off"
        assert result["components"]["lm"]["mode"] == "lm_off"
        assert result["components"]["graph"]["mode"] == "db_off"

        # Test human summary
        summary = print_human_summary(result)
        assert "DB_HEALTH:   mode=db_off" in summary
        assert "LM_HEALTH:   mode=lm_off" in summary
        assert "GRAPH_OVERVIEW: mode=db_off" in summary

    @patch("scripts.system.system_health.subprocess.run")
    def test_all_ready(self, mock_subprocess_run):
        """Test system health when all components are ready."""
        from scripts.system.system_health import compute_system_health

        # Mock subprocess responses
        def mock_run_side_effect(cmd, **kwargs):
            mock_result = MagicMock()
            cmd_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
            if "guard_db_health" in cmd_str:
                mock_result.stdout = json.dumps(
                    {
                        "ok": True,
                        "mode": "ready",
                        "checks": {
                            "driver_available": True,
                            "connection_ok": True,
                            "graph_stats_ready": True,
                        },
                        "details": {"errors": []},
                    }
                )
            elif "guard_lm_health" in cmd_str:
                mock_result.stdout = json.dumps(
                    {
                        "ok": True,
                        "mode": "lm_ready",
                        "details": {
                            "endpoint": "http://127.0.0.1:1234",
                            "errors": [],
                        },
                    }
                )
            elif "graph_overview" in cmd_str:
                mock_result.stdout = json.dumps(
                    {
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
                )
            else:
                mock_result.stdout = "{}"
            mock_result.returncode = 0
            return mock_result

        mock_subprocess_run.side_effect = mock_run_side_effect

        result = compute_system_health()

        assert result["ok"] is True
        assert result["components"]["db"]["mode"] == "ready"
        assert result["components"]["lm"]["mode"] == "lm_ready"
        assert result["components"]["graph"]["mode"] == "db_on"

    @patch("scripts.system.system_health.subprocess.run")
    def test_partial_mixed(self, mock_subprocess_run):
        """Test system health with mixed component states."""
        from scripts.system.system_health import compute_system_health

        # Mock subprocess responses: DB partial, LM ready, graph db_off
        def mock_run_side_effect(cmd, **kwargs):
            mock_result = MagicMock()
            cmd_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
            if "guard_db_health" in cmd_str:
                mock_result.stdout = json.dumps(
                    {
                        "ok": False,
                        "mode": "partial",
                        "checks": {
                            "driver_available": True,
                            "connection_ok": True,
                            "graph_stats_ready": False,
                        },
                        "details": {
                            "errors": ["graph_stats_table_missing: gematria.graph_stats_snapshots does not exist"]
                        },
                    }
                )
            elif "guard_lm_health" in cmd_str:
                mock_result.stdout = json.dumps(
                    {
                        "ok": True,
                        "mode": "lm_ready",
                        "details": {
                            "endpoint": "http://127.0.0.1:1234",
                            "errors": [],
                        },
                    }
                )
            elif "graph_overview" in cmd_str:
                mock_result.stdout = json.dumps(
                    {
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
                )
            else:
                mock_result.stdout = "{}"
            mock_result.returncode = 0
            return mock_result

        mock_subprocess_run.side_effect = mock_run_side_effect

        result = compute_system_health()

        assert result["ok"] is False
        assert result["components"]["db"]["mode"] == "partial"
        assert result["components"]["lm"]["mode"] == "lm_ready"
        assert result["components"]["graph"]["mode"] == "db_off"

    @patch("scripts.system.system_health.subprocess.run")
    def test_malformed_json(self, mock_subprocess_run):
        """Test system health when a component returns malformed JSON."""
        from scripts.system.system_health import compute_system_health

        # Mock subprocess responses: one returns non-JSON
        def mock_run_side_effect(cmd, **kwargs):
            mock_result = MagicMock()
            cmd_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
            if "guard_db_health" in cmd_str:
                mock_result.stdout = json.dumps(
                    {
                        "ok": True,
                        "mode": "ready",
                        "checks": {
                            "driver_available": True,
                            "connection_ok": True,
                            "graph_stats_ready": True,
                        },
                        "details": {"errors": []},
                    }
                )
            elif "guard_lm_health" in cmd_str:
                # Malformed JSON
                mock_result.stdout = "not valid json {"
            elif "graph_overview" in cmd_str:
                mock_result.stdout = json.dumps(
                    {
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
                )
            else:
                mock_result.stdout = "{}"
            mock_result.returncode = 0
            return mock_result

        mock_subprocess_run.side_effect = mock_run_side_effect

        result = compute_system_health()

        assert result["ok"] is False  # System not ok because LM has malformed JSON
        assert result["components"]["db"]["mode"] == "ready"
        assert result["components"]["lm"]["mode"] == "unknown"
        assert result["components"]["graph"]["mode"] == "db_on"
        assert "malformed or missing JSON from lm_health" in str(result["components"]["lm"]["details"]["errors"])

    @patch("scripts.system.system_health.compute_system_health")
    def test_main_outputs_json(self, mock_compute_health, capsys):
        """Test main() outputs valid JSON and exits 0."""
        import scripts.system.system_health

        mock_compute_health.return_value = {
            "ok": True,
            "components": {
                "db": {
                    "ok": True,
                    "mode": "ready",
                    "checks": {
                        "driver_available": True,
                        "connection_ok": True,
                        "graph_stats_ready": True,
                    },
                    "details": {"errors": []},
                },
                "lm": {
                    "ok": True,
                    "mode": "lm_ready",
                    "details": {
                        "endpoint": "http://127.0.0.1:1234",
                        "errors": [],
                    },
                },
                "graph": {
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
                },
            },
        }

        result = scripts.system.system_health.main()

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["ok"] is True
        assert "components" in data
        assert "db" in data["components"]
        assert "lm" in data["components"]
        assert "graph" in data["components"]
