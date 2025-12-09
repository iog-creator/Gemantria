#!/usr/bin/env python3
"""
Tests for ExplainSystemState DSPy module (Phase 28C).
"""

from __future__ import annotations

from typing import Any, Dict

import pytest

# Test fixtures: realistic kernel/health surfaces


@pytest.fixture
def green_kernel() -> Dict[str, Any]:
    """Fixture: All-green kernel state."""
    return {
        "version": 1,
        "current_phase": "28",
        "last_completed_phase": "27",
        "branch": "feat/phase28c-cleanup",
        "health": {
            "reality_green": True,
            "checks": {
                "DMS Alignment": True,
                "Bootstrap Consistency": True,
                "Share Sync Policy": True,
                "Backup System": True,
            },
        },
        "required_surfaces": [
            "share/PM_BOOTSTRAP_STATE.json",
            "share/SSOT_SURFACE_V17.json",
        ],
    }


@pytest.fixture
def green_reality_summary() -> Dict[str, Any]:
    """Fixture: All-green reality summary."""
    return {
        "reality_green": True,
        "checks": [
            {
                "name": "DB Health",
                "passed": True,
                "message": "DB is reachable and healthy",
            },
            {
                "name": "Control-Plane Health",
                "passed": True,
                "message": "Control plane is healthy",
            },
            {
                "name": "AGENTS.md Sync",
                "passed": True,
                "message": "All AGENTS.md files are in sync",
            },
            {
                "name": "Share Sync & Exports",
                "passed": True,
                "message": "All required exports present",
            },
            {
                "name": "Ledger Verification",
                "passed": True,
                "message": "All 6 tracked artifacts are current",
            },
            {
                "name": "DMS Alignment",
                "passed": True,
                "message": "DMS and share/ are aligned",
            },
        ],
    }


@pytest.fixture
def green_pm_snapshot() -> Dict[str, Any]:
    """Fixture: All-green PM snapshot."""
    return {
        "status": "healthy",
        "db": {
            "reachable": True,
            "mode": "ready",
            "last_checked": "2025-12-08T23:57:50Z",
        },
        "lm": {
            "mode": "lm_ready",
            "provider": "lmstudio",
            "slots": {
                "local_agent": {"status": "ready", "model": "ibm/granite-4-h-tiny"},
                "theology": {"status": "ready", "model": "christian-bible-expert-v2.0-12b"},
            },
        },
    }


@pytest.fixture
def degraded_kernel() -> Dict[str, Any]:
    """Fixture: Degraded kernel state."""
    return {
        "version": 1,
        "current_phase": "28",
        "last_completed_phase": "27",
        "branch": "feat/phase28c-cleanup",
        "health": {
            "reality_green": False,
            "checks": {
                "DMS Alignment": False,
                "Bootstrap Consistency": True,
                "Share Sync Policy": False,
                "Backup System": True,
            },
        },
    }


@pytest.fixture
def degraded_reality_summary() -> Dict[str, Any]:
    """Fixture: Degraded reality summary."""
    return {
        "reality_green": False,
        "checks": [
            {
                "name": "DB Health",
                "passed": True,
                "message": "DB is reachable and healthy",
            },
            {
                "name": "DMS Alignment",
                "passed": False,
                "message": "DMS and share/ have mismatches",
                "details": {"mismatch_count": 3},
            },
            {
                "name": "Share Sync & Exports",
                "passed": False,
                "message": "Missing required exports",
            },
        ],
    }


@pytest.fixture
def degraded_pm_snapshot() -> Dict[str, Any]:
    """Fixture: Degraded PM snapshot."""
    return {
        "status": "degraded",
        "db": {
            "reachable": True,
            "mode": "ready",
        },
        "lm": {
            "mode": "lm_off",
            "provider": None,
        },
    }


@pytest.fixture
def empty_context() -> Dict[str, Any]:
    """Fixture: Empty OA context."""
    return {
        "active_goal": None,
        "constraints": [],
        "pending_ops_blocks": [],
    }


# ============================================================================
# Unit Tests: build_facts
# ============================================================================


def test_build_facts_green(
    green_kernel: Dict[str, Any],
    green_reality_summary: Dict[str, Any],
    green_pm_snapshot: Dict[str, Any],
    empty_context: Dict[str, Any],
) -> None:
    """Test build_facts extracts correct facts from green state."""
    from pmagent.oa.dspy_explain_system_state import build_facts

    facts = build_facts(green_kernel, green_reality_summary, green_pm_snapshot, empty_context)

    assert facts["current_phase"] == "28"
    assert facts["last_completed_phase"] == "27"
    assert facts["branch"] == "feat/phase28c-cleanup"
    assert facts["reality_green"] is True
    assert facts["db_mode"] == "ready"
    assert facts["lm_mode"] == "lm_ready"
    assert facts["lm_provider"] == "lmstudio"
    assert facts["check_statuses"]["dms_alignment"] is True
    assert len(facts["warnings"]) == 0


def test_build_facts_degraded(
    degraded_kernel: Dict[str, Any],
    degraded_reality_summary: Dict[str, Any],
    degraded_pm_snapshot: Dict[str, Any],
    empty_context: Dict[str, Any],
) -> None:
    """Test build_facts extracts correct facts from degraded state."""
    from pmagent.oa.dspy_explain_system_state import build_facts

    facts = build_facts(degraded_kernel, degraded_reality_summary, degraded_pm_snapshot, empty_context)

    assert facts["reality_green"] is False
    assert facts["db_mode"] == "ready"
    assert facts["lm_mode"] == "lm_off"
    assert facts["check_statuses"]["dms_alignment"] is False
    assert len(facts["warnings"]) > 0


# ============================================================================
# Unit Tests: evaluate_explain_system_state
# ============================================================================


def test_evaluate_explain_system_state_green(
    green_kernel: Dict[str, Any],
    green_reality_summary: Dict[str, Any],
    green_pm_snapshot: Dict[str, Any],
    empty_context: Dict[str, Any],
) -> None:
    """Test validator gives high score for good green-state explanation."""
    from pmagent.oa.dspy_explain_system_state import evaluate_explain_system_state

    answer = """
    # System State

    Current phase: 28
    Last completed phase: 27
    Branch: feat/phase28c-cleanup

    ## Status: OK

    Database: ready
    LM: lm_ready (lmstudio)

    All checks passing.
    """
    status_label = "OK"
    covered_sections = "phase,mode,db,lm"

    score = evaluate_explain_system_state(
        green_kernel,
        green_reality_summary,
        green_pm_snapshot,
        empty_context,
        answer,
        status_label,
        covered_sections,
    )

    assert score >= 0.8, f"Expected high score, got {score}"


def test_evaluate_explain_system_state_degraded(
    degraded_kernel: Dict[str, Any],
    degraded_reality_summary: Dict[str, Any],
    degraded_pm_snapshot: Dict[str, Any],
    empty_context: Dict[str, Any],
) -> None:
    """Test validator penalizes incorrect status label."""
    from pmagent.oa.dspy_explain_system_state import evaluate_explain_system_state

    answer = """
    # System State

    Current phase: 28
    Database: ready
    LM: lm_off
    """
    status_label = "OK"  # Wrong! Should be DEGRADED
    covered_sections = "phase,db,lm"

    score = evaluate_explain_system_state(
        degraded_kernel,
        degraded_reality_summary,
        degraded_pm_snapshot,
        empty_context,
        answer,
        status_label,
        covered_sections,
    )

    assert score < 0.8, f"Expected lower score for incorrect status, got {score}"


def test_evaluate_explain_system_state_missing_sections(
    green_kernel: Dict[str, Any],
    green_reality_summary: Dict[str, Any],
    green_pm_snapshot: Dict[str, Any],
    empty_context: Dict[str, Any],
) -> None:
    """Test validator penalizes missing required sections."""
    from pmagent.oa.dspy_explain_system_state import evaluate_explain_system_state

    answer = "System is OK."
    status_label = "OK"
    covered_sections = "mode"  # Missing phase, db, lm

    score = evaluate_explain_system_state(
        green_kernel,
        green_reality_summary,
        green_pm_snapshot,
        empty_context,
        answer,
        status_label,
        covered_sections,
    )

    assert score < 0.9, f"Expected lower score for missing sections, got {score}"


# ============================================================================
# Integration Tests: ExplainSystemState Module
# ============================================================================


@pytest.mark.skipif(
    not __import__("sys").modules.get("dspy"),
    reason="DSPy not installed",
)
def test_explain_system_state_module_initialization() -> None:
    """Test module can be initialized (requires DSPy)."""
    from pmagent.oa.dspy_explain_system_state import ExplainSystemState, configure_dspy_lm

    try:
        lm = configure_dspy_lm()
        module = ExplainSystemState(lm=lm)
        assert module is not None
    except RuntimeError as e:
        if "DSPy not installed" in str(e) or "No LOCAL_AGENT_MODEL" in str(e):
            pytest.skip(f"Skipping test: {e}")
        raise


@pytest.mark.skipif(
    not __import__("sys").modules.get("dspy"),
    reason="DSPy not installed",
)
def test_explain_system_state_forward(
    green_kernel: Dict[str, Any],
    green_reality_summary: Dict[str, Any],
    green_pm_snapshot: Dict[str, Any],
    empty_context: Dict[str, Any],
) -> None:
    """Test module forward() produces valid output structure."""
    from pmagent.oa.dspy_explain_system_state import ExplainSystemState, configure_dspy_lm

    try:
        lm = configure_dspy_lm()
        module = ExplainSystemState(lm=lm)

        result = module(
            user_question="Explain the current system state.",
            kernel=green_kernel,
            reality_summary=green_reality_summary,
            pm_snapshot=green_pm_snapshot,
            context_meta=empty_context,
        )

        # Check output structure
        assert hasattr(result, "answer_markdown")
        assert hasattr(result, "status_label")
        assert hasattr(result, "covered_sections")
        assert isinstance(result.answer_markdown, str)
        assert result.status_label in ("OK", "DEGRADED", "UNCERTAIN")
        assert isinstance(result.covered_sections, str)

    except RuntimeError as e:
        if "DSPy not installed" in str(e) or "No LOCAL_AGENT_MODEL" in str(e):
            pytest.skip(f"Skipping test: {e}")
        raise


# ============================================================================
# Test: Signature Registry Integration
# ============================================================================


def test_explain_system_state_in_registry() -> None:
    """Test ExplainSystemState is registered in dspy_signatures."""
    from pmagent.oa.dspy_signatures import SIGNATURES, get_signature

    assert "ExplainSystemState" in SIGNATURES
    sig_class = get_signature("ExplainSystemState")
    assert sig_class is not None


def test_create_module_explain_system_state() -> None:
    """Test create_module returns ExplainSystemState module."""
    from pmagent.oa.dspy_signatures import create_module, is_dspy_available

    if not is_dspy_available():
        pytest.skip("DSPy not installed")

    module = create_module("ExplainSystemState")
    # Should return ExplainSystemState instance, not generic ReasoningModule
    assert module is not None
    from pmagent.oa.dspy_explain_system_state import ExplainSystemState

    assert isinstance(module, ExplainSystemState)
