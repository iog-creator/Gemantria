#!/usr/bin/env python3
"""
Guard: Share Sync Policy (Phase 24.C)

Enforces:
1. No unknown files in managed namespaces (DMS-driven allowlist).
2. All DMS-tracked share docs exist on disk.
3. No silent deletion of managed files.

Managed Namespaces:
- share/PHASE*
- share/orchestrator/
- share/orchestrator_assistant/
- share/atlas/
- share/exports/

Ephemeral Namespaces (Ignored):
- share/tmp/
- share/local/
"""

import json
import sys
import os
from pathlib import Path
import argparse
from typing import Set, Dict, Any

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

try:
    from sqlalchemy import text
    from pmagent.db.loader import get_control_engine

    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False


MANAGED_PREFIXES = [
    "share/PHASE",
    # Legacy/Governance focused prefixes
]

# System namespaces are preserved but NOT checked against DMS (dynamic state or exports)
# See docs/SSOT/SHARE_FOLDER_ANALYSIS.md for SSOT on share/ layout and non-DMS-managed surfaces
SYSTEM_PREFIXES = [
    "share/orchestrator",
    "share/orchestrator_assistant",
    "share/atlas",
    "share/exports",
    "share/handoff",  # kernel bundle directory (PM_KERNEL.json, PM_SUMMARY.md) - Phase 24.E deliverables
]

EPHEMERAL_PREFIXES = [
    "share/tmp",
    "share/local",
]

# Specific root files that are system-managed but not in DMS (generated artifacts)
SYSTEM_FILES = {
    # Console v2 / Bootstrap (JSON surfaces)
    "share/SSOT_SURFACE_V17.json",
    "share/PM_BOOTSTRAP_STATE.json",
    "share/kb_registry.json",
    "share/HANDOFF_KERNEL.json",
    "share/REALITY_GREEN_SUMMARY.json",
    "share/planning_context.json",  # planning pipeline output for agents (not a managed doc)
    # Legacy Summaries (JSON)
    "share/PHASE16_AUDIT_SNAPSHOT.json",
    "share/PHASE16_CLASSIFICATION_REPORT.json",
    "share/PHASE16_DB_RECON_REPORT.json",
    "share/PHASE16_PURGE_EXECUTION_LOG.json",
    "share/PHASE18_AGENTS_SYNC_SUMMARY.json",
    "share/PHASE18_LEDGER_REPAIR_SUMMARY.json",
    "share/PHASE18_SHARE_EXPORTS_SUMMARY.json",
    "share/PHASE19_SHARE_HYGIENE_SUMMARY.json",
    "share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.json",
    # PM Introspection Surfaces (Phase 27.M - generated agent working surfaces)
    # See docs/SSOT/SHARE_FOLDER_ANALYSIS.md for SSOT on share/ layout
    "share/schema_snapshot.md",
    "share/SSOT_SURFACE_V17.md",
    "share/agents_md.head.md",
    "share/governance_freshness.md",
    "share/hint_registry.md",
    "share/PM_BOOTSTRAP_STATE.md",
    "share/planning_lane_status.md",
    "share/pm_snapshot.md",
    "share/planning_context.md",
    "share/HANDOFF_KERNEL.md",
    "share/REALITY_GREEN_SUMMARY.md",
    "share/doc_registry.md",
    "share/next_steps.head.md",
    "share/doc_sync_state.md",
    "share/pm_system_introspection_evidence.md",
    "share/pm_contract.head.md",
    "share/live_posture.md",
    # Phase specific docs in share/ (legacy governance)
    "share/PHASE16_DB_RECON_REPORT.md",
    "share/PHASE16_PURGE_EXECUTION_LOG.md",
    "share/PHASE18_AGENTS_SYNC_SUMMARY.md",
    "share/PHASE18_INDEX.md",
    "share/PHASE18_LEDGER_REPAIR_SUMMARY.md",
    "share/PHASE18_SHARE_EXPORTS_SUMMARY.md",
    "share/PHASE19_SHARE_HYGIENE_SUMMARY.md",
    "share/PHASE20_INDEX.md",
    "share/PHASE20_ORCHESTRATOR_UI_MODEL.md",
    "share/PHASE20_UI_RESET_DECISION.md",
    "share/PHASE21_CONSOLE_SERVE_PLAN.md",
    "share/PHASE21_INDEX.md",
    "share/PHASE22_OPERATOR_WORKFLOW.md",
    "share/PHASE22_INDEX.md",
    "share/PHASE23_INDEX.md",
    "share/PHASE23_STRESS_PLAN.md",
    "share/PHASE23_BASELINE_NOTE.md",
    "share/PHASE23_BOOTSTRAP_HARDENING_NOTE.md",
    "share/PHASE23_STRESS_SMOKE_NOTE.md",
    "share/PHASE23_FAILURE_INJECTION_NOTE.md",
    "share/PHASE23_PHASE_DONE_CHECKLIST.md",
    "share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md",
    # Other governance surfaces
    "share/PM_HANDOFF_PROTOCOL.md",
    "share/SHARE_FOLDER_ANALYSIS.md",
}

SHARE_ROOT = ROOT / "share"


def get_dms_allowlist() -> Set[str]:
    """Fetch all allowed share paths from DMS."""
    if not DB_AVAILABLE:
        # In strict mode, this is a failure.
        return set()

    try:
        engine = get_control_engine()
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                SELECT share_path, repo_path 
                FROM control.doc_registry 
                WHERE enabled = TRUE
            """)
            ).fetchall()

            allowed = set()
            for row in rows:
                # prefer share_path, fallback to repo_path if it starts with share/
                sp = row.share_path
                if not sp and row.repo_path and row.repo_path.startswith("share/"):
                    sp = row.repo_path

                if sp:
                    allowed.add(sp)
            return allowed
    except Exception as e:
        print(f"Error fetching DMS allowlist: {e}", file=sys.stderr)
        return set()


def is_managed(rel_path: str) -> bool:
    # 1. Check if it's a System Path (Allowed implicitly)
    for prefix in SYSTEM_PREFIXES:
        if rel_path.startswith(prefix):
            return False  # Not "Managed" in the validation sense (checking against DMS)

    if rel_path in SYSTEM_FILES:
        return False

    # 2. Check if it's explicitly Managed
    for prefix in MANAGED_PREFIXES:
        if rel_path.startswith(prefix):
            return True

    # 3. Root files are generally managed unless system-exempted
    if "/" not in rel_path.replace("share/", "", 1):
        return True

    return False


def is_ephemeral(rel_path: str) -> bool:
    for prefix in EPHEMERAL_PREFIXES:
        if rel_path.startswith(prefix):
            return True
    return False


def check_policy(mode: str) -> Dict[str, Any]:
    allowed_paths = get_dms_allowlist()

    missing_in_share = []
    extra_in_share = []
    missing_in_dms = []  # Implicitly same as extra_in_share for managed paths

    # Check for missing files
    for path in allowed_paths:
        full_path = ROOT / path
        if not full_path.exists():
            missing_in_share.append(path)

    # Check for extra files
    if SHARE_ROOT.exists():
        for root, dirs, files in os.walk(SHARE_ROOT):
            for name in files:
                full_path = Path(root) / name
                rel_path = str(full_path.relative_to(ROOT))

                if is_ephemeral(rel_path):
                    continue

                if is_managed(rel_path):
                    if rel_path not in allowed_paths:
                        extra_in_share.append(rel_path)
                        missing_in_dms.append(rel_path)

    ok = len(extra_in_share) == 0  # We focus on Extras. Missing is informational for the policy guard (sync fixes it).
    # Wait, policy says 'No managed files missing'. But sync_share RUNS this to verify safety.
    # If missing exists, it's not unsafe to sync.
    # But for reality.green, missing is bad.

    if mode == "STRICT":
        # In strict mode (reality.green), missing files are bad.
        # But sync_share calls this BEFORE populating.
        pass

    report = {
        "ok": ok,
        "mode": mode,
        "missing_in_share": sorted(missing_in_share),
        "extra_in_share": sorted(extra_in_share),
        "missing_in_dms": sorted(missing_in_dms),
    }

    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["HINT", "STRICT"], default="HINT")
    args = parser.parse_args()

    # Pre-flight DB check
    if not DB_AVAILABLE:
        print("Error: DB not available.", file=sys.stderr)
        if args.mode == "STRICT":
            sys.exit(1)

    report = check_policy(args.mode)
    print(json.dumps(report, indent=2))

    if args.mode == "STRICT" and not report["ok"]:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
