"""
Tests for eval exports helpers (AgentPM-First:M4).

Verifies that eval export helpers are hermetic, tolerant of missing files,
and return expected structures.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


class TestEvalExportsHelpers:
    """Test eval exports helper functions."""

    def test_load_lm_indicator_hermetic(self):
        """Test that load_lm_indicator works in hermetic mode (file may be missing)."""
        # Import directly to avoid dependency chain issues
        import importlib.util

        eval_exports_path = ROOT / "agentpm" / "status" / "eval_exports.py"
        spec = importlib.util.spec_from_file_location("eval_exports", eval_exports_path)
        eval_exports = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(eval_exports)
        load_lm_indicator = eval_exports.load_lm_indicator

        result = load_lm_indicator()

        # Verify structure
        assert isinstance(result, dict)
        assert "available" in result

        # If not available, should have a note
        if not result.get("available", False):
            assert "note" in result

    def test_load_edge_class_counts_hermetic(self):
        """Test that load_edge_class_counts works in hermetic mode (file may be missing)."""
        # Import directly to avoid dependency chain issues
        import importlib.util

        eval_exports_path = ROOT / "agentpm" / "status" / "eval_exports.py"
        spec = importlib.util.spec_from_file_location("eval_exports", eval_exports_path)
        eval_exports = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(eval_exports)
        load_edge_class_counts = eval_exports.load_edge_class_counts

        result = load_edge_class_counts()

        # Verify structure
        assert isinstance(result, dict)
        assert "available" in result

        # If not available, should have a note
        if not result.get("available", False):
            assert "note" in result

    def test_load_db_health_snapshot_hermetic(self):
        """Test that load_db_health_snapshot works in hermetic mode (file may be missing)."""
        # Import directly to avoid dependency chain issues
        import importlib.util

        eval_exports_path = ROOT / "agentpm" / "status" / "eval_exports.py"
        spec = importlib.util.spec_from_file_location("eval_exports", eval_exports_path)
        eval_exports = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(eval_exports)
        load_db_health_snapshot = eval_exports.load_db_health_snapshot

        result = load_db_health_snapshot()

        # Verify structure
        assert isinstance(result, dict)
        assert "available" in result

        # If not available, should have a note
        if not result.get("available", False):
            assert "note" in result

    def test_get_eval_insights_summary(self):
        """Test that get_eval_insights_summary returns expected structure."""
        # Import directly to avoid dependency chain issues
        import importlib.util

        eval_exports_path = ROOT / "agentpm" / "status" / "eval_exports.py"
        spec = importlib.util.spec_from_file_location("eval_exports", eval_exports_path)
        eval_exports = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(eval_exports)
        get_eval_insights_summary = eval_exports.get_eval_insights_summary

        result = get_eval_insights_summary()

        # Verify structure
        assert isinstance(result, dict)
        assert "lm_indicator" in result
        assert "db_health" in result
        assert "edge_class_counts" in result

        # Verify each export has availability flag
        for key in ["lm_indicator", "db_health", "edge_class_counts"]:
            export_data = result[key]
            assert isinstance(export_data, dict)
            assert "available" in export_data
