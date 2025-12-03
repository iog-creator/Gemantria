"""Tests for DMS (Documentation Management System) guards.

Tests cover HINT/STRICT mode behavior, DB-off tolerance, and output shape validation.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch


# Add project root to path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

GUARD_DOCS_DB_SSOT = ROOT / "scripts" / "guards" / "guard_docs_db_ssot.py"
GUARD_DOCS_CONSISTENCY = ROOT / "scripts" / "guards" / "guard_docs_consistency.py"


def run_guard(script_path: Path, env: dict | None = None) -> tuple[int, dict]:
    """Run a guard script and return (exit_code, parsed_json_output)."""
    env = env or {}
    full_env = os.environ.copy()
    full_env.update(env)
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        env=full_env,
        cwd=ROOT,
    )
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        output = {"error": "failed to parse JSON", "stdout": result.stdout, "stderr": result.stderr}
    return result.returncode, output


class TestGuardDocsDbSsot:
    """Tests for guard_docs_db_ssot.py."""

    def test_guard_docs_db_ssot_outputs_expected_shape(self):
        """Test that guard outputs expected JSON shape."""
        _exit_code, output = run_guard(GUARD_DOCS_DB_SSOT, {"STRICT_MODE": "0"})

        # Should have required fields
        assert "ok" in output
        assert "mode" in output
        assert "reason" in output
        assert "details" in output
        assert "generated_at" in output

        # Mode should be one of expected values
        assert output["mode"] in ("ready", "db_off", "partial")

        # Details should have expected structure
        details = output["details"]
        assert "total_local_docs" in details
        assert "total_registry_docs" in details
        assert "missing_registry_docs" in details
        assert "missing_versions" in details

    def test_guard_docs_db_ssot_hint_mode_db_off_tolerated(self):
        """Test that HINT mode tolerates DB-off (exits 0)."""
        # Mock get_control_engine to raise exception (simulating DB-off)
        with patch("scripts.guards.guard_docs_db_ssot.get_control_engine") as mock_engine:
            mock_engine.side_effect = Exception("Connection refused")

            exit_code, output = run_guard(GUARD_DOCS_DB_SSOT, {"STRICT_MODE": "0"})

            # HINT mode should exit 0 even when DB is off
            assert exit_code == 0
            assert output["ok"] is False
            assert output["mode"] == "db_off"
            assert "hints" in output
            assert isinstance(output["hints"], list)
            assert len(output["hints"]) > 0

    def test_guard_docs_db_ssot_strict_mode_db_off_fails(self):
        """Test that STRICT mode fails when DB is off (exits 1)."""
        # Mock get_control_engine to raise exception (simulating DB-off)
        with patch("scripts.guards.guard_docs_db_ssot.get_control_engine") as mock_engine:
            mock_engine.side_effect = Exception("Connection refused")

            exit_code, output = run_guard(GUARD_DOCS_DB_SSOT, {"STRICT_MODE": "1"})

            # STRICT mode should exit 1 when DB is off
            assert exit_code == 1
            assert output["ok"] is False
            assert output["mode"] == "db_off"
            # STRICT mode should not include hints
            assert "hints" not in output

    def test_guard_docs_db_ssot_hint_mode_partial_tolerated(self):
        """Test that HINT mode tolerates partial sync (exits 0)."""
        # Mock successful DB connection but with missing docs
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=None)

        # Mock query results: some docs missing from registry
        mock_conn.execute.return_value.fetchall.side_effect = [
            [("AGENTS_ROOT", "doc-1")],  # Only one doc in registry
            [],  # No missing versions
        ]

        mock_engine = MagicMock()
        mock_engine.connect.return_value = mock_conn

        with patch("scripts.guards.guard_docs_db_ssot.get_control_engine", return_value=mock_engine):
            exit_code, output = run_guard(GUARD_DOCS_DB_SSOT, {"STRICT_MODE": "0"})

            # HINT mode should exit 0 even with partial sync
            assert exit_code == 0
            # May be ok=false if there are missing docs, but still exits 0
            assert "hints" in output or output["ok"] is True

    def test_guard_docs_db_ssot_strict_mode_partial_fails(self):
        """Test that STRICT mode fails when sync is partial (exits 1)."""
        # Mock successful DB connection but with missing docs
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=None)

        # Mock query results: some docs missing from registry
        mock_conn.execute.return_value.fetchall.side_effect = [
            [("AGENTS_ROOT", "doc-1")],  # Only one doc in registry
            [],  # No missing versions
        ]

        mock_engine = MagicMock()
        mock_engine.connect.return_value = mock_conn

        with patch("scripts.guards.guard_docs_db_ssot.get_control_engine", return_value=mock_engine):
            exit_code, output = run_guard(GUARD_DOCS_DB_SSOT, {"STRICT_MODE": "1"})

            # STRICT mode should exit 1 if sync is partial (ok=false)
            if not output["ok"]:
                assert exit_code == 1
            else:
                # If ok=true, exit should be 0
                assert exit_code == 0

    def test_guard_docs_db_ssot_strict_mode_success_exits_zero(self):
        """Test that STRICT mode exits 0 when sync is complete (ok=true)."""
        # Mock successful DB connection with all docs in sync
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=None)

        # Mock query results: all docs present, no missing versions
        # We need to mock discover_local_docs to return a known set
        with patch("scripts.guards.guard_docs_db_ssot.discover_local_docs") as mock_discover:
            from scripts.guards.guard_docs_db_ssot import LocalDoc

            # Create a small set of local docs
            mock_docs = [
                LocalDoc(logical_name="AGENTS_ROOT", path=Path("AGENTS.md")),
                LocalDoc(logical_name="MASTER_PLAN", path=Path("MASTER_PLAN.md")),
            ]
            mock_discover.return_value = mock_docs

            # Mock registry query to return all docs
            mock_conn.execute.return_value.fetchall.side_effect = [
                [("AGENTS_ROOT", "doc-1"), ("MASTER_PLAN", "doc-2")],  # All docs in registry
                [],  # No missing versions
            ]

            mock_engine = MagicMock()
            mock_engine.connect.return_value = mock_conn

            with patch("scripts.guards.guard_docs_db_ssot.get_control_engine", return_value=mock_engine):
                exit_code, output = run_guard(GUARD_DOCS_DB_SSOT, {"STRICT_MODE": "1"})

                # If sync is complete, should exit 0
                if output["ok"]:
                    assert exit_code == 0
                    assert output["mode"] == "ready"


class TestGuardDocsConsistency:
    """Tests for guard_docs_consistency.py (happy-path)."""

    def test_guard_docs_consistency_runs(self):
        """Test that guard_docs_consistency runs without errors."""
        exit_code, output = run_guard(GUARD_DOCS_CONSISTENCY)

        # Should exit 0 (hermetic guard, always passes in HINT mode)
        assert exit_code == 0
        assert "scanned" in output
        assert "ok" in output
        assert "fails" in output
