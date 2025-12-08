#!/usr/bin/env python3
"""
OA State Module (Phase 27.B/C)

Builds and writes a kernel-aligned state snapshot for the Orchestrator Assistant.
OA is a read-only consumer of kernel surfaces:
- PM_BOOTSTRAP_STATE.json
- SSOT_SURFACE_V17.json
- REALITY_GREEN_SUMMARY.json
- Atlas/LM/exports surfaces as listed in PM_BOOTSTRAP_STATE.webui.console_v2.surfaces_consumed

The resulting STATE.json provides a normalized view for Console v2 consumption.
"""

from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any


# Paths relative to repo root
ROOT = Path(__file__).resolve().parents[2]
SHARE = ROOT / "share"

# Kernel surfaces
PM_BOOTSTRAP_STATE = SHARE / "PM_BOOTSTRAP_STATE.json"
SSOT_SURFACE = SHARE / "SSOT_SURFACE_V17.json"
REALITY_GREEN_SUMMARY = SHARE / "REALITY_GREEN_SUMMARY.json"

# Reference surfaces (from PM_BOOTSTRAP_STATE.webui.console_v2.surfaces_consumed)
ATLAS_SYSTEM_HEALTH = SHARE / "atlas" / "control_plane" / "system_health.json"
ATLAS_LM_INDICATOR = SHARE / "atlas" / "control_plane" / "lm_indicator.json"
DOCS_CONTROL_CANONICAL = SHARE / "exports" / "docs-control" / "canonical.json"
DOCS_CONTROL_SUMMARY = SHARE / "exports" / "docs-control" / "summary.json"
KB_REGISTRY = SHARE / "kb_registry.json"

# OA context surface (Phase 27.E)
OA_CONTEXT_DIR = SHARE / "oa"
OA_CONTEXT_FILE = OA_CONTEXT_DIR / "CONTEXT.json"

# Output
OA_STATE_DIR = SHARE / "orchestrator_assistant"
OA_STATE_FILE = OA_STATE_DIR / "STATE.json"


def _load_json(path: Path) -> dict[str, Any] | None:
    """Load JSON file, return None if missing."""
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _path_exists(path: Path) -> bool:
    """Check if path exists relative to repo root."""
    return path.exists()


def build_oa_state() -> dict[str, Any]:
    """
    Build a normalized OA state dict from kernel surfaces.

    Returns a state dict suitable for Console v2 consumption, containing:
    - branch and phase from kernel surfaces
    - reality_green status
    - references to atlas/lm/docs-control surfaces
    - DMS hint summary (if available)
    """
    # Load kernel surfaces
    bootstrap = _load_json(PM_BOOTSTRAP_STATE) or {}
    ssot = _load_json(SSOT_SURFACE) or {}
    reality = _load_json(REALITY_GREEN_SUMMARY) or {}

    # Load OA context surface (Phase 27.E)
    oa_context_data = _load_json(OA_CONTEXT_FILE) or {"version": 1, "context": {}}
    oa_context = oa_context_data.get("context", {})

    # Extract key fields
    branch = bootstrap.get("branch", "unknown")
    current_phase = ssot.get("current_phase", str(ssot.get("phases", {}).get("current", "unknown")))
    last_completed_phase = ssot.get(
        "last_completed_phase", str(ssot.get("phases", {}).get("last_completed", "unknown"))
    )
    reality_green = reality.get("reality_green", False)

    # Build minimal checks summary (names and passed status only)
    checks_summary = []
    for check in reality.get("checks", []):
        checks_summary.append(
            {
                "name": check.get("name", "unknown"),
                "passed": check.get("passed", False),
            }
        )

    # DMS hint summary from reality checks
    dms_hint_summary = {}
    for check in reality.get("checks", []):
        if check.get("name") == "DMS Hint Registry":
            details = check.get("details", {})
            dms_hint_summary = {
                "total_hints": details.get("total_hints", 0),
                "flows_with_hints": details.get("flows_with_hints", 0),
            }
            break

    # Reference surface paths (for Console v2 to verify/consume)
    # Listed as repo-relative paths matching PM_BOOTSTRAP_STATE.webui.console_v2.surfaces_consumed
    ref_surfaces = {
        "pm_bootstrap_state": str(PM_BOOTSTRAP_STATE.relative_to(ROOT)),
        "ssot_surface": str(SSOT_SURFACE.relative_to(ROOT)),
        "reality_green_summary": str(REALITY_GREEN_SUMMARY.relative_to(ROOT)),
        "atlas_system_health": str(ATLAS_SYSTEM_HEALTH.relative_to(ROOT)),
        "atlas_lm_indicator": str(ATLAS_LM_INDICATOR.relative_to(ROOT)),
        "docs_control_canonical": str(DOCS_CONTROL_CANONICAL.relative_to(ROOT)),
        "docs_control_summary": str(DOCS_CONTROL_SUMMARY.relative_to(ROOT)),
        "kb_registry": str(KB_REGISTRY.relative_to(ROOT)),
    }

    # Check which surfaces exist
    surface_status = {
        "pm_bootstrap_state": _path_exists(PM_BOOTSTRAP_STATE),
        "ssot_surface": _path_exists(SSOT_SURFACE),
        "reality_green_summary": _path_exists(REALITY_GREEN_SUMMARY),
        "atlas_system_health": _path_exists(ATLAS_SYSTEM_HEALTH),
        "atlas_lm_indicator": _path_exists(ATLAS_LM_INDICATOR),
        "docs_control_canonical": _path_exists(DOCS_CONTROL_CANONICAL),
        "docs_control_summary": _path_exists(DOCS_CONTROL_SUMMARY),
        "kb_registry": _path_exists(KB_REGISTRY),
    }

    # Build normalized state
    state = {
        "version": 1,
        "source": "kernel",
        "generated_at": datetime.now(UTC).isoformat(),
        "branch": branch,
        "current_phase": current_phase,
        "last_completed_phase": last_completed_phase,
        "reality_green": reality_green,
        "checks_summary": checks_summary,
        "dms_hint_summary": dms_hint_summary,
        "surfaces": ref_surfaces,
        "surface_status": surface_status,
        "oa_context": oa_context,  # Phase 27.E: Task context for DSPy programs
        # Phase 27.E Batch 3: OA Tools Interface
        # Lists available tools for DSPy program consumption
        "oa_tools": {
            "version": 1,
            "tools": [
                "oa.kernel_status",
                "oa.reality_check",
                "oa.guard.run",
                "oa.bootstrap_state",
                "oa.ssot_surface",
                "oa.reality_summary",
                "oa.handoff_kernel",
            ],
            "interface": "pmagent.oa.tools",
            "registry": "docs/SSOT/oa/OA_TOOLS_REGISTRY.md",
        },
        # Phase 27.F: Reasoning Bridge Scaffolding
        "reasoning_bridge": {
            "version": 1,
            "programs": [
                "SafeOPSDecision",
                "OPSBlockGenerator",
                "GuardFailureInterpreter",
                "PhaseTransitionValidator",
            ],
            "schemas": {
                "envelope": "ReasoningEnvelope",
                "result": "ReasoningResult",
            },
            "implementation_status": "DESIGN_ONLY",
        },
    }

    return state


def write_oa_state(path: Path | None = None) -> Path:
    """
    Build OA state and write to STATE.json.

    Args:
        path: Optional output path (defaults to share/orchestrator_assistant/STATE.json)

    Returns:
        Path to written file
    """
    output_path = path or OA_STATE_FILE
    output_path.parent.mkdir(parents=True, exist_ok=True)

    state = build_oa_state()
    output_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    return output_path


if __name__ == "__main__":
    # Direct invocation for testing
    out = write_oa_state()
    print(f"Wrote OA state to {out}")
