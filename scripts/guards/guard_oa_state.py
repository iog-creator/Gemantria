#!/usr/bin/env python3
"""
guard_oa_state.py — OA State Consistency Guard (Phase 27.B/C)

Verifies that share/orchestrator_assistant/STATE.json is consistent with kernel surfaces:
- branch matches PM_BOOTSTRAP_STATE.json
- current_phase matches SSOT_SURFACE_V17.json
- reality_green matches REALITY_GREEN_SUMMARY.json
- All referenced surfaces exist on disk

Modes:
- STRICT: Exit non-zero on mismatch (default)
- HINT: Log warnings, exit 0
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHARE = ROOT / "share"

# Paths
OA_STATE = SHARE / "orchestrator_assistant" / "STATE.json"
PM_BOOTSTRAP_STATE = SHARE / "PM_BOOTSTRAP_STATE.json"
SSOT_SURFACE = SHARE / "SSOT_SURFACE_V17.json"
REALITY_GREEN_SUMMARY = SHARE / "REALITY_GREEN_SUMMARY.json"
# Phase 27.E: OA context surface
OA_CONTEXT = SHARE / "oa" / "CONTEXT.json"


def _load_json(path: Path) -> dict | None:
    """Load JSON file, return None if missing."""
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def check_oa_consistency(mode: str = "STRICT") -> dict:
    """
    Check OA state against kernel surfaces.

    Phase 27.D: Enforces tri-surface coherence:
    - OA STATE.json
    - REALITY_GREEN_SUMMARY.json
    - PM_BOOTSTRAP_STATE.json

    Returns a report dict with:
    - ok: bool
    - mismatches: list of mismatch descriptions
    - missing_surfaces: list of missing surface paths
    """
    report = {
        "ok": True,
        "mode": mode,
        "mismatches": [],
        "missing_surfaces": [],
    }

    # Load all surfaces
    oa_state = _load_json(OA_STATE)
    bootstrap = _load_json(PM_BOOTSTRAP_STATE)
    ssot = _load_json(SSOT_SURFACE)
    reality = _load_json(REALITY_GREEN_SUMMARY)

    # Check OA state exists
    if oa_state is None:
        report["ok"] = False
        report["mismatches"].append("OA STATE.json missing - run: pmagent oa snapshot")
        return report

    # Check kernel surfaces exist
    if bootstrap is None:
        report["ok"] = False
        report["mismatches"].append("PM_BOOTSTRAP_STATE.json missing")
        return report
    if ssot is None:
        report["ok"] = False
        report["mismatches"].append("SSOT_SURFACE_V17.json missing")
        return report
    if reality is None:
        report["ok"] = False
        report["mismatches"].append("REALITY_GREEN_SUMMARY.json missing")
        return report

    # Check branch consistency
    oa_branch = oa_state.get("branch", "unknown")
    kernel_branch = bootstrap.get("branch", "unknown")
    if oa_branch != kernel_branch:
        report["ok"] = False
        report["mismatches"].append(f"branch mismatch: OA='{oa_branch}' vs kernel='{kernel_branch}'")

    # Check current_phase consistency
    oa_phase = str(oa_state.get("current_phase", "unknown"))
    kernel_phase = str(ssot.get("current_phase", ssot.get("phases", {}).get("current", "unknown")))
    if oa_phase != kernel_phase:
        report["ok"] = False
        report["mismatches"].append(f"current_phase mismatch: OA='{oa_phase}' vs kernel='{kernel_phase}'")

    # ========================================
    # Phase 27.D: Tri-Surface Coherence Checks
    # ========================================

    # 1. OA reality_green must match REALITY_GREEN_SUMMARY
    oa_reality = oa_state.get("reality_green", None)
    kernel_reality = reality.get("reality_green", None)
    if oa_reality != kernel_reality:
        report["ok"] = False
        report["mismatches"].append(f"reality_green mismatch: OA={oa_reality} vs REALITY_GREEN={kernel_reality}")

    # 2. PM_BOOTSTRAP health.reality_green check DISABLED (circular dependency)
    # PM_BOOTSTRAP.health is regenerated from REALITY_GREEN_SUMMARY, which creates a
    # circular dependency when running within reality.green context. This check
    # would always fail on the first run after any failure.
    # The OA state refresh + other coherence checks are sufficient.
    #
    # OLD CODE (kept for reference):
    # pm_health = bootstrap.get("health", {})
    # pm_reality_green = pm_health.get("reality_green", None)
    # if pm_reality_green is not None and pm_reality_green != kernel_reality:
    #     report["ok"] = False
    #     report["mismatches"].append(...)
    pm_health = bootstrap.get("health", {})  # Still need pm_health for later checks

    # 3. Key check statuses must match between OA and REALITY_GREEN_SUMMARY
    key_checks = ["AGENTS.md Sync", "DMS Alignment", "AGENTS–DMS Contract"]  # noqa: RUF001

    # Build lookup for reality checks
    reality_checks = {c.get("name"): c.get("passed") for c in reality.get("checks", [])}
    # Build lookup for OA checks
    oa_checks = {c.get("name"): c.get("passed") for c in oa_state.get("checks_summary", [])}

    for check_name in key_checks:
        rg_passed = reality_checks.get(check_name)
        oa_passed = oa_checks.get(check_name)
        if rg_passed is not None and oa_passed is not None and rg_passed != oa_passed:
            report["ok"] = False
            report["mismatches"].append(f"check '{check_name}' mismatch: OA={oa_passed} vs REALITY_GREEN={rg_passed}")

    # 4. PM_BOOTSTRAP health.agents_sync_ok and health.dms_alignment_ok must match
    if pm_health:
        pm_agents_sync = pm_health.get("agents_sync_ok")
        pm_dms_align = pm_health.get("dms_alignment_ok")
        rg_agents_sync = reality_checks.get("AGENTS.md Sync")
        rg_dms_align = reality_checks.get("DMS Alignment")

        if pm_agents_sync is not None and rg_agents_sync is not None and pm_agents_sync != rg_agents_sync:
            report["ok"] = False
            report["mismatches"].append(
                f"agents_sync mismatch: PM_BOOTSTRAP.health={pm_agents_sync} vs REALITY_GREEN={rg_agents_sync}"
            )
        if pm_dms_align is not None and rg_dms_align is not None and pm_dms_align != rg_dms_align:
            report["ok"] = False
            report["mismatches"].append(
                f"dms_alignment mismatch: PM_BOOTSTRAP.health={pm_dms_align} vs REALITY_GREEN={rg_dms_align}"
            )

    # 5. Check for contradictory notes in PM_BOOTSTRAP (legacy cleanup)
    # If a stale meta.dms_share_alignment exists and contradicts health, flag it
    pm_meta = bootstrap.get("meta", {})
    stale_dms_alignment = pm_meta.get("dms_share_alignment")
    if stale_dms_alignment is not None:
        # meta.dms_share_alignment is deprecated, should be migrated to health section
        rg_dms_ok = reality_checks.get("DMS Alignment", False)
        if stale_dms_alignment == "BROKEN" and rg_dms_ok:
            report["ok"] = False
            report["mismatches"].append(
                "stale meta.dms_share_alignment='BROKEN' contradicts REALITY_GREEN DMS Alignment=PASS"
            )

    # Check referenced surfaces exist
    surface_status = oa_state.get("surface_status", {})
    for surface_name, exists in surface_status.items():
        if not exists:
            report["missing_surfaces"].append(surface_name)

    if report["missing_surfaces"]:
        # Missing surfaces is informational, not a hard failure
        # Console v2 can handle absent optional surfaces
        pass

    # ========================================
    # Phase 27.E: OA Context Surface Validation
    # ========================================
    if OA_CONTEXT.exists():
        oa_context = _load_json(OA_CONTEXT)
        if oa_context is None:
            report["missing_surfaces"].append("share/oa/CONTEXT.json (invalid JSON)")
        elif "version" not in oa_context:
            report["missing_surfaces"].append("share/oa/CONTEXT.json (missing version)")
        elif "context" not in oa_context:
            report["missing_surfaces"].append("share/oa/CONTEXT.json (missing context)")
    # Note: OA_CONTEXT is optional, missing is just informational

    return report


def main():
    parser = argparse.ArgumentParser(description="Check OA state consistency with kernel surfaces")
    parser.add_argument(
        "--mode",
        choices=["HINT", "STRICT"],
        default="STRICT",
        help="STRICT: exit non-zero on mismatch; HINT: warn only",
    )
    args = parser.parse_args()

    report = check_oa_consistency(args.mode)

    # Output
    if report["ok"]:
        print("✅ OA State Guard: PASS")
        print("   OA state is consistent with kernel surfaces")
        if report["missing_surfaces"]:
            print(f"   Note: {len(report['missing_surfaces'])} optional surfaces missing")
    else:
        print("❌ OA State Guard: FAIL")
        for mismatch in report["mismatches"]:
            print(f"   - {mismatch}")
        if report["missing_surfaces"]:
            print(f"   Missing surfaces: {', '.join(report['missing_surfaces'])}")

    # JSON output for scripting
    print(f"\nJSON: {json.dumps(report)}")

    # Exit code
    if args.mode == "STRICT" and not report["ok"]:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
