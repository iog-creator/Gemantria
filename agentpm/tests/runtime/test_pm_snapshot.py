"""
Tests for pm.snapshot integration (AgentPM-First:M3).

Verifies that pm.snapshot composes health, status explain, reality-check,
AI tracking, and share manifest into a single snapshot artifact.

Note: These tests verify the unified snapshot helper contract rather than
executing the full pm_snapshot.py script (which runs at module import time).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


class TestPmSnapshotIntegration:
    """Test pm.snapshot integration with pmagent commands."""

    def test_unified_snapshot_helper_contract(self):
        """Test that the unified snapshot helper has the expected contract."""
        from agentpm.status.snapshot import get_system_snapshot

        # Verify the function exists and is callable
        assert callable(get_system_snapshot)

        # Verify it accepts expected parameters
        import inspect

        sig = inspect.signature(get_system_snapshot)
        params = list(sig.parameters.keys())
        assert "include_reality_check" in params
        assert "include_ai_tracking" in params
        assert "include_share_manifest" in params
        assert "include_eval_insights" in params
        assert "reality_check_mode" in params
        assert "use_lm_for_explain" in params

    def test_snapshot_helper_components(self):
        """Test that the unified snapshot helper returns expected components."""
        from agentpm.status.snapshot import get_system_snapshot

        # Call with minimal options (hermetic mode)
        result = get_system_snapshot(
            include_reality_check=True,
            include_ai_tracking=True,
            include_share_manifest=True,
            include_eval_insights=True,
            reality_check_mode="HINT",
            use_lm_for_explain=False,
        )

        # Verify structure
        assert isinstance(result, dict)
        assert "system_health" in result
        assert "status_explain" in result
        assert "reality_check" in result
        assert "ai_tracking" in result
        assert "share_manifest" in result
        assert "eval_insights" in result

        # Verify each component has expected structure
        assert isinstance(result["system_health"], dict)
        assert isinstance(result["status_explain"], dict)
        assert isinstance(result["reality_check"], dict)
        assert isinstance(result["ai_tracking"], dict)
        assert isinstance(result["share_manifest"], dict)
        assert isinstance(result["eval_insights"], dict)

    def test_snapshot_helper_handles_db_off_gracefully(self):
        """Test that the unified snapshot helper handles DB-off mode gracefully."""
        from agentpm.status.snapshot import get_system_snapshot

        # Call with DB potentially off (hermetic mode)
        result = get_system_snapshot(
            include_reality_check=True,
            include_ai_tracking=True,
            include_share_manifest=True,
            include_eval_insights=True,
            reality_check_mode="HINT",
            use_lm_for_explain=False,
        )

        # Verify structure is always present (hermetic behavior)
        assert isinstance(result, dict)
        assert "system_health" in result
        assert "status_explain" in result
        assert "reality_check" in result
        assert "ai_tracking" in result
        assert "share_manifest" in result
        assert "eval_insights" in result

        # Verify ai_tracking has mode indicator
        ai_tracking = result["ai_tracking"]
        assert "mode" in ai_tracking
        assert ai_tracking["mode"] in ["db_on", "db_off", "error"]

    def test_snapshot_helper_includes_ai_tracking(self):
        """Test that the unified snapshot helper includes AI tracking summary."""
        from agentpm.status.snapshot import get_system_snapshot

        result = get_system_snapshot(
            include_reality_check=True,
            include_ai_tracking=True,
            include_share_manifest=True,
            include_eval_insights=True,
            reality_check_mode="HINT",
            use_lm_for_explain=False,
        )

        # Verify AI tracking structure
        ai_tracking = result["ai_tracking"]
        assert isinstance(ai_tracking, dict)
        assert "ok" in ai_tracking
        assert "mode" in ai_tracking

        # If DB is on, should have agent_run and agent_run_cli
        if ai_tracking.get("mode") == "db_on":
            assert "agent_run" in ai_tracking or "error" in ai_tracking
            assert "agent_run_cli" in ai_tracking or "error" in ai_tracking

    def test_snapshot_helper_includes_eval_insights(self):
        """Test that the unified snapshot helper includes eval insights summary."""
        from agentpm.status.snapshot import get_system_snapshot

        result = get_system_snapshot(
            include_reality_check=True,
            include_ai_tracking=True,
            include_share_manifest=True,
            include_eval_insights=True,
            reality_check_mode="HINT",
            use_lm_for_explain=False,
        )

        # Verify eval insights structure
        eval_insights = result["eval_insights"]
        assert isinstance(eval_insights, dict)
        assert "lm_indicator" in eval_insights
        assert "db_health" in eval_insights
        assert "edge_class_counts" in eval_insights

        # Verify each eval export has availability flag
        for key in ["lm_indicator", "db_health", "edge_class_counts"]:
            export_data = eval_insights[key]
            assert isinstance(export_data, dict)
            assert "available" in export_data
            # If not available, should have a note
            if not export_data.get("available", False):
                assert "note" in export_data

    def test_snapshot_helper_eval_insights_optional(self):
        """Test that eval insights can be excluded from snapshot."""
        from agentpm.status.snapshot import get_system_snapshot

        # Call without eval insights
        result = get_system_snapshot(
            include_reality_check=True,
            include_ai_tracking=True,
            include_share_manifest=True,
            include_eval_insights=False,
            reality_check_mode="HINT",
            use_lm_for_explain=False,
        )

        # Verify eval_insights is not present
        assert "eval_insights" not in result

    def test_snapshot_helper_includes_kb_registry(self):
        """Test that the unified snapshot helper includes KB registry summary."""
        from agentpm.status.snapshot import get_system_snapshot

        result = get_system_snapshot(
            include_reality_check=True,
            include_ai_tracking=True,
            include_share_manifest=True,
            include_eval_insights=True,
            include_kb_registry=True,
            reality_check_mode="HINT",
            use_lm_for_explain=False,
        )

        # Verify KB registry structure
        kb_registry = result["kb_registry"]
        assert isinstance(kb_registry, dict)
        assert "available" in kb_registry
        assert "total" in kb_registry
        assert "valid" in kb_registry
        assert "errors_count" in kb_registry
        assert "warnings_count" in kb_registry

    def test_snapshot_helper_kb_registry_optional(self):
        """Test that KB registry can be excluded from snapshot."""
        from agentpm.status.snapshot import get_system_snapshot

        # Call without KB registry
        result = get_system_snapshot(
            include_reality_check=True,
            include_ai_tracking=True,
            include_share_manifest=True,
            include_eval_insights=True,
            include_kb_registry=False,
            reality_check_mode="HINT",
            use_lm_for_explain=False,
        )

        # Verify kb_registry is not present
        assert "kb_registry" not in result

    def test_snapshot_helper_kb_registry_handles_missing_file(self):
        """Test that KB registry summary handles missing registry file gracefully."""
        from agentpm.status.snapshot import get_system_snapshot

        # Call with KB registry (file may not exist)
        result = get_system_snapshot(
            include_reality_check=True,
            include_ai_tracking=True,
            include_share_manifest=True,
            include_eval_insights=True,
            include_kb_registry=True,
            reality_check_mode="HINT",
            use_lm_for_explain=False,
        )

        # Verify structure is always present (hermetic behavior)
        kb_registry = result["kb_registry"]
        assert isinstance(kb_registry, dict)
        assert "available" in kb_registry
        assert "total" in kb_registry
        # If file doesn't exist, should return empty registry gracefully
        if not kb_registry.get("available", False):
            assert kb_registry.get("total", 0) == 0

    def test_snapshot_helper_includes_kb_hints(self):
        """Test that the unified snapshot helper includes KB hints (KB-Reg:M4)."""
        from agentpm.status.snapshot import get_system_snapshot

        result = get_system_snapshot(
            include_reality_check=True,
            include_ai_tracking=True,
            include_share_manifest=True,
            include_eval_insights=True,
            include_kb_registry=True,
            reality_check_mode="HINT",
            use_lm_for_explain=False,
        )

        # Verify KB hints structure
        kb_hints = result.get("kb_hints", [])
        assert isinstance(kb_hints, list)
        # Each hint should have level, code, message
        for hint in kb_hints:
            assert "level" in hint
            assert "code" in hint
            assert "message" in hint
            assert hint["level"] in ["WARN", "INFO"]
            assert hint["code"].startswith("KB_")

    def test_snapshot_helper_includes_kb_doc_health(self):
        """Test that the unified snapshot helper includes KB doc-health metrics (AgentPM-Next:M3)."""
        from agentpm.status.snapshot import get_system_snapshot

        result = get_system_snapshot(
            include_reality_check=True,
            include_ai_tracking=True,
            include_share_manifest=True,
            include_eval_insights=True,
            include_kb_registry=True,
            include_kb_doc_health=True,
            reality_check_mode="HINT",
            use_lm_for_explain=False,
        )

        # Verify KB doc-health structure
        kb_doc_health = result["kb_doc_health"]
        assert isinstance(kb_doc_health, dict)
        assert "available" in kb_doc_health
        assert "metrics" in kb_doc_health

        # Verify metrics structure
        metrics = kb_doc_health.get("metrics", {})
        assert "kb_fresh_ratio" in metrics
        assert "kb_missing_count" in metrics
        assert "kb_stale_count_by_subsystem" in metrics
        assert "kb_fixes_applied_last_7d" in metrics
        assert "kb_debt_burned_down" in metrics
        assert "notes" in metrics

    def test_snapshot_helper_kb_doc_health_optional(self):
        """Test that KB doc-health can be excluded from snapshot."""
        from agentpm.status.snapshot import get_system_snapshot

        # Call without KB doc-health
        result = get_system_snapshot(
            include_reality_check=True,
            include_ai_tracking=True,
            include_share_manifest=True,
            include_eval_insights=True,
            include_kb_registry=True,
            include_kb_doc_health=False,
            reality_check_mode="HINT",
            use_lm_for_explain=False,
        )

        # Verify kb_doc_health is not present
        assert "kb_doc_health" not in result

    def test_snapshot_helper_kb_doc_health_handles_missing_registry(self):
        """Test that KB doc-health handles missing registry gracefully."""
        from agentpm.status.snapshot import get_system_snapshot

        # Call with KB doc-health (registry may not exist)
        result = get_system_snapshot(
            include_reality_check=True,
            include_ai_tracking=True,
            include_share_manifest=True,
            include_eval_insights=True,
            include_kb_registry=True,
            include_kb_doc_health=True,
            reality_check_mode="HINT",
            use_lm_for_explain=False,
        )

        # Verify structure is always present (hermetic behavior)
        kb_doc_health = result["kb_doc_health"]
        assert isinstance(kb_doc_health, dict)
        assert "available" in kb_doc_health
        assert "metrics" in kb_doc_health
        # If registry doesn't exist, should return unavailable gracefully
        if not kb_doc_health.get("available", False):
            assert "error" in kb_doc_health or "note" in kb_doc_health.get("metrics", {})
