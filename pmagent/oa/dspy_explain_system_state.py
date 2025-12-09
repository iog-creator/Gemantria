#!/usr/bin/env python3
"""
OA DSPy Module: ExplainSystemState (Phase 28C)

First OA skill: Explains current system state to orchestrator based on
kernel & health surfaces (kernel handoff, REALITY_GREEN summary, pm snapshot, CONTEXT).

This module:
- Reads authoritative kernel and health surfaces
- Produces grounded Markdown explanation of system state
- Never guesses state not present in inputs
- Reports UNCERTAIN when required surfaces are missing
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, TYPE_CHECKING

# Guard dspy import - falls back gracefully if not installed
try:
    import dspy

    HAS_DSPY = True
except ImportError:
    HAS_DSPY = False
    dspy = None  # type: ignore

if TYPE_CHECKING or not HAS_DSPY:
    # Type stubs for when dspy is not available
    class SignatureStub:
        pass

    class ModuleStub:
        pass

    if not HAS_DSPY:

        class DummyField:
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                pass

        class dspy:  # type: ignore  # noqa: N801
            class Signature(SignatureStub):
                pass

            class Module(ModuleStub):
                pass

            class ChainOfThought:
                def __init__(self, *args: Any, **kwargs: Any) -> None:
                    pass

            @staticmethod
            def InputField(*args: Any, **kwargs: Any) -> Any:
                return None

            @staticmethod
            def OutputField(*args: Any, **kwargs: Any) -> Any:
                return None


# ============================================================================
# DSPy Signature
# ============================================================================


class ExplainSystemStateSig(dspy.Signature if HAS_DSPY else SignatureStub):  # type: ignore
    """
    ExplainSystemState — Explain the current system state to the orchestrator.

    This module reads the authoritative kernel and health surfaces and produces a
    grounded, human-readable explanation of system state.

    It must:
    - Describe current_phase, last_completed_phase, and branch from the kernel.
    - Report OK/DEGRADED/UNCERTAIN mode based only on health checks.
    - Summarize database health (db.mode etc.).
    - Summarize local model health (LM Studio provider, slots).
    - Explain docs/DMS/share/AGENTS/ledger status.
    - Call out non-blocking hints/warnings (repo drift, missing share docs) as warnings.
    - Never invent state that isn't present in inputs.
    """

    # Inputs
    user_question: str = dspy.InputField(  # type: ignore
        desc="Natural language question about system state (or default explanation request)"
    )
    kernel: str = dspy.InputField(  # type: ignore
        desc="Kernel state as JSON string (current_phase, last_completed_phase, branch, health)"
    )
    reality_summary: str = dspy.InputField(  # type: ignore
        desc="REALITY_GREEN_SUMMARY.json as JSON string (reality_green, checks array)"
    )
    pm_snapshot: str = dspy.InputField(  # type: ignore
        desc="PM snapshot/system_health.json as JSON string (db.mode, lm.mode, lm.provider)"
    )
    context_meta: str = dspy.InputField(  # type: ignore
        desc="OA context metadata as JSON string (active_goal, constraints, etc.)"
    )

    # Outputs
    answer_markdown: str = dspy.OutputField(  # type: ignore
        desc="Grounded Markdown explanation of system state"
    )
    status_label: str = dspy.OutputField(  # type: ignore
        desc="Overall status: 'OK' | 'DEGRADED' | 'UNCERTAIN'"
    )
    covered_sections: str = dspy.OutputField(  # type: ignore
        desc="Comma-separated list of sections covered (e.g., 'phase,mode,db,lm,dms')"
    )


# ============================================================================
# Helper: build_facts
# ============================================================================


def build_facts(
    kernel: Dict[str, Any],
    reality_summary: Dict[str, Any],
    pm_snapshot: Dict[str, Any],
    context_meta: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Extract key facts from surfaces for LM consumption.

    Args:
        kernel: Kernel state dict (from HANDOFF_KERNEL.json or PM_KERNEL.json)
        reality_summary: REALITY_GREEN_SUMMARY.json dict
        pm_snapshot: PM snapshot/system_health.json dict
        context_meta: OA context dict (from CONTEXT.json)

    Returns:
        Compact facts dict for LM prompt.
    """
    facts: Dict[str, Any] = {}

    # Phase / branch from kernel
    facts["current_phase"] = kernel.get("current_phase")
    facts["last_completed_phase"] = kernel.get("last_completed_phase")
    facts["branch"] = kernel.get("branch")

    # Kernel health
    health = kernel.get("health", {})
    facts["reality_green"] = health.get("reality_green") or reality_summary.get("reality_green", False)

    # DB / LM from snapshot
    db = pm_snapshot.get("db", {})
    lm = pm_snapshot.get("lm", {})
    facts["db_mode"] = db.get("mode") or ((db.get("reachable") and "ready") or "db_off")
    facts["lm_mode"] = lm.get("mode") or ((lm.get("provider") and "lm_ready") or "lm_off")
    facts["lm_provider"] = lm.get("provider")

    # Checks from reality_summary
    checks = reality_summary.get("checks", [])
    facts["checks"] = checks

    # Extract key check statuses
    check_map: Dict[str, bool] = {}
    for check in checks:
        name = check.get("name", "")
        passed = check.get("passed", False)
        check_map[name] = passed

    facts["check_statuses"] = {
        "dms_alignment": check_map.get("DMS Alignment", None),
        "bootstrap_consistency": check_map.get("Bootstrap Consistency", None),
        "share_sync": check_map.get("Share Sync & Exports", None),
        "backup_system": check_map.get("Backup System", None),
        "repo_alignment": check_map.get("Repo Alignment", None),  # Hint-level
        "agents_sync": check_map.get("AGENTS.md Sync", None),
        "ledger_verification": check_map.get("Ledger Verification", None),
        "db_health": check_map.get("DB Health", None),
        "control_plane_health": check_map.get("Control-Plane Health", None),
    }

    # Warnings/hints (non-blocking)
    warnings: List[str] = []
    for check in checks:
        if not check.get("passed", False) and check.get("name") in (
            "Repo Alignment",
            "Share Sync & Exports",
        ):
            msg = check.get("message", "")
            if msg:
                warnings.append(f"{check.get('name')}: {msg}")

    facts["warnings"] = warnings

    # CONTEXT
    facts["active_goal"] = context_meta.get("active_goal")
    facts["constraints"] = context_meta.get("constraints", [])

    return facts


# ============================================================================
# DSPy Module
# ============================================================================


class ExplainSystemState(dspy.Module if HAS_DSPY else ModuleStub):  # type: ignore
    """DSPy module for explaining system state."""

    def __init__(self, lm: Any | None = None):
        """Initialize module with optional LM (defaults to dspy.settings.lm)."""
        if not HAS_DSPY:
            raise RuntimeError("DSPy not installed. Install with: pip install dspy-ai")

        super().__init__()
        # Use provided LM or fall back to dspy.settings.lm
        self.lm = lm
        self.explainer = dspy.ChainOfThought(ExplainSystemStateSig)

    def forward(
        self,
        user_question: str,
        kernel: Dict[str, Any],
        reality_summary: Dict[str, Any],
        pm_snapshot: Dict[str, Any],
        context_meta: Dict[str, Any],
    ) -> Any:
        """
        Generate system state explanation.

        Args:
            user_question: User's question (or empty for default)
            kernel: Kernel state dict
            reality_summary: REALITY_GREEN_SUMMARY dict
            pm_snapshot: PM snapshot dict
            context_meta: OA context dict

        Returns:
            DSPy prediction with answer_markdown, status_label, covered_sections
        """
        # Default question if empty
        if not user_question.strip():
            user_question = (
                "Explain the current system state, including phase, "
                "branch, overall mode, DB health, LM health, docs/DMS/share, "
                "and any warnings or hints."
            )

        # Serialize dicts to JSON strings for DSPy signature
        kernel_json = json.dumps(kernel, default=str)
        reality_json = json.dumps(reality_summary, default=str)
        snapshot_json = json.dumps(pm_snapshot, default=str)
        context_json = json.dumps(context_meta, default=str)

        # Call DSPy predictor
        # Temporarily override LM if provided
        if self.lm:
            original_lm = dspy.settings.lm
            dspy.settings.lm = self.lm
            try:
                result = self.explainer(
                    user_question=user_question,
                    kernel=kernel_json,
                    reality_summary=reality_json,
                    pm_snapshot=snapshot_json,
                    context_meta=context_json,
                )
            finally:
                dspy.settings.lm = original_lm
        else:
            result = self.explainer(
                user_question=user_question,
                kernel=kernel_json,
                reality_summary=reality_json,
                pm_snapshot=snapshot_json,
                context_meta=context_json,
            )

        return result


# ============================================================================
# Validator: evaluate_explain_system_state
# ============================================================================


def evaluate_explain_system_state(
    kernel: Dict[str, Any],
    reality_summary: Dict[str, Any],
    pm_snapshot: Dict[str, Any],
    context_meta: Dict[str, Any],
    answer_markdown: str,
    status_label: str,
    covered_sections: str,
) -> float:
    """
    Evaluate explanation quality against inputs.

    Returns a score in [0, 1] indicating how well the answer matches the surfaces.

    Args:
        kernel: Kernel state dict
        reality_summary: REALITY_GREEN_SUMMARY dict
        pm_snapshot: PM snapshot dict
        context_meta: OA context dict
        answer_markdown: Generated explanation
        status_label: Generated status label
        covered_sections: Comma-separated sections list

    Returns:
        Score in [0, 1] (higher = better match)
    """
    score = 1.0
    text = answer_markdown.lower()

    # Extract expected values
    phase = str(kernel.get("current_phase", ""))
    last_phase = str(kernel.get("last_completed_phase", ""))
    branch = str(kernel.get("branch", ""))

    health = kernel.get("health", {})
    reality_green = bool(health.get("reality_green") or reality_summary.get("reality_green", False))

    db = pm_snapshot.get("db", {})
    lm = pm_snapshot.get("lm", {})
    db_mode = str(db.get("mode") or ((db.get("reachable") and "ready") or "db_off"))
    lm_mode = str(lm.get("mode") or ((lm.get("provider") and "lm_ready") or "lm_off"))

    # 1) Check phase & branch present
    if phase and phase not in text:
        score -= 0.1
    if last_phase and last_phase not in text:
        score -= 0.05
    if branch and branch not in text:
        score -= 0.05

    # 2) Check DB & LM modes mentioned
    if db_mode and db_mode not in text:
        score -= 0.1
    if lm_mode and lm_mode not in text:
        score -= 0.1

    # 3) Check status_label consistency
    if reality_green and status_label != "OK":
        score -= 0.2
    if (not reality_green) and status_label == "OK":
        score -= 0.2

    # 4) Ensure some coverage sections present
    sections_list = [s.strip() for s in covered_sections.split(",") if s.strip()]
    required_sections = {"phase", "mode", "db", "lm"}
    if not required_sections.issubset(set(sections_list)):
        score -= 0.1

    # 5) Check that warnings are mentioned if present
    checks = reality_summary.get("checks", [])
    has_warnings = any(
        not c.get("passed", False) and c.get("name") in ("Repo Alignment", "Share Sync & Exports") for c in checks
    )
    if has_warnings and "warn" not in text:
        score -= 0.05

    # Clamp
    if score < 0.0:
        score = 0.0
    if score > 1.0:
        score = 1.0

    return score


# ============================================================================
# DSPy LM Configuration Helper
# ============================================================================


def configure_dspy_lm() -> Any:
    """
    Configure DSPy LM from project's LM configuration.

    Uses LOCAL_AGENT_MODEL and provider settings to create a DSPy LM instance.

    Returns:
        Configured dspy.LM instance (or None if DSPy not available)

    Raises:
        RuntimeError: If DSPy not installed or LM configuration invalid
    """
    if not HAS_DSPY:
        raise RuntimeError("DSPy not installed. Install with: pip install dspy-ai")

    from scripts.config.env import get_lm_model_config, openai_cfg

    cfg = get_lm_model_config()
    provider = cfg.get("local_agent_provider") or cfg.get("provider", "lmstudio")
    provider = provider.strip()

    # Get model and base URL
    model = cfg.get("local_agent_model")
    if not model:
        raise RuntimeError("No LOCAL_AGENT_MODEL configured for OA DSPy")

    # For OpenAI-compatible APIs (LM Studio)
    if provider == "lmstudio":
        openai_cfg_dict = openai_cfg()
        base_url = openai_cfg_dict.get("base_url", "http://127.0.0.1:9994/v1")
        api_key = openai_cfg_dict.get("api_key")

        # DSPy supports OpenAI-compatible APIs via dspy.LM with api_base
        try:
            # Ensure base_url ends with /v1 if not already
            if not base_url.endswith("/v1"):
                base_url = base_url.rstrip("/") + "/v1"

            # DSPy LM configuration for OpenAI-compatible APIs
            # Model format: "openai/model-name" or just model name
            lm = dspy.LM(model=model, api_base=base_url, api_key=api_key or "not-needed")
            return lm
        except Exception as e:
            raise RuntimeError(f"Failed to configure DSPy LM for LM Studio: {e}") from e

    # For Ollama
    elif provider == "ollama":
        # ollama_base_url = cfg.get("ollama_base_url", "http://127.0.0.1:11434")
        # DSPy doesn't have native Ollama support, but we can use a custom LM wrapper
        # For now, raise an error and suggest using LM Studio
        raise RuntimeError(
            "Ollama provider not yet supported for DSPy. "
            "Set LOCAL_AGENT_PROVIDER=lmstudio or use LM Studio for OA DSPy modules."
        )

    else:
        raise RuntimeError(f"Unknown provider for DSPy LM: {provider}")


# ============================================================================
# CLI Entry Point
# ============================================================================


def cli_explain_system_state(question: str | None = None) -> None:
    """
    CLI entry point for manual testing.

    Loads surfaces from share/ and calls ExplainSystemState module.

    Args:
        question: Optional user question (defaults to standard explanation request)
    """
    if not HAS_DSPY:
        print("ERROR: DSPy not installed. Install with: pip install dspy-ai")
        return

    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[2]
    SHARE = ROOT / "share"

    # Load surfaces
    kernel_path = SHARE / "HANDOFF_KERNEL.json"
    if not kernel_path.exists():
        kernel_path = SHARE / "pm_boot" / "PM_KERNEL.json"
    if not kernel_path.exists():
        kernel_path = SHARE / "handoff" / "PM_KERNEL.json"

    reality_path = SHARE / "REALITY_GREEN_SUMMARY.json"
    snapshot_path = SHARE / "atlas" / "control_plane" / "system_health.json"
    context_path = SHARE / "oa" / "CONTEXT.json"

    def load_json(path: Path) -> Dict[str, Any]:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"WARNING: Failed to load {path}: {e}")
                return {}
        return {}

    kernel = load_json(kernel_path)
    reality_summary = load_json(reality_path)
    pm_snapshot = load_json(snapshot_path)
    context_data = load_json(context_path)
    context_meta = context_data.get("context", {})

    # Configure DSPy LM
    try:
        lm = configure_dspy_lm()
    except Exception as e:
        print(f"ERROR: Failed to configure DSPy LM: {e}")
        return

    # Create module
    module = ExplainSystemState(lm=lm)

    # Default question
    user_question = question or "Explain the current system state for me."

    # Call module
    try:
        result = module(
            user_question=user_question,
            kernel=kernel,
            reality_summary=reality_summary,
            pm_snapshot=pm_snapshot,
            context_meta=context_meta,
        )

        # Print results
        print("=" * 80)
        print("SYSTEM STATE EXPLANATION")
        print("=" * 80)
        print()
        print(result.answer_markdown)
        print()
        print("=" * 80)
        print(f"Status: {result.status_label}")
        print(f"Covered Sections: {result.covered_sections}")
        print("=" * 80)

    except Exception as e:
        print(f"ERROR: Module execution failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    import sys

    question = sys.argv[1] if len(sys.argv) > 1 else None
    cli_explain_system_state(question)
