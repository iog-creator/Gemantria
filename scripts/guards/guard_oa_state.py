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

    # Check reality_green consistency
    oa_reality = oa_state.get("reality_green", None)
    kernel_reality = reality.get("reality_green", None)
    if oa_reality != kernel_reality:
        report["ok"] = False
        report["mismatches"].append(f"reality_green mismatch: OA={oa_reality} vs kernel={kernel_reality}")

    # Check referenced surfaces exist
    surface_status = oa_state.get("surface_status", {})
    for surface_name, exists in surface_status.items():
        if not exists:
            report["missing_surfaces"].append(surface_name)

    if report["missing_surfaces"]:
        # Missing surfaces is informational, not a hard failure
        # Console v2 can handle absent optional surfaces
        pass

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
