#!/usr/bin/env python3
"""
guard_dms_share_alignment.py

Verifies that:
1. Every tracked doc in DMS (share_path set) exists in share/
2. Every expected governance doc in share/ has a registry entry
3. No orphans exist in either direction (unless whitelisted)

Modes:
- STRICT: Exit non-zero on mismatch
- HINT: Log warnings, exit 0
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# Pre-flight DB check (mandatory - Rule 050 evidence-first)
preflight_script = ROOT / "scripts" / "ops" / "preflight_db_check.py"
result = subprocess.run([sys.executable, str(preflight_script), "--mode", "strict"], capture_output=True)
if result.returncode != 0:
    print(result.stderr.decode(), file=sys.stderr)
    sys.exit(result.returncode)

try:
    from sqlalchemy import text
    from pmagent.db.loader import get_control_engine

    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False


SHARE_ROOT = ROOT / "share"

# Files/Patterns explicitly allowed in share/ even if not in registry
# (Matches sync_share.py + specifics)
# See docs/SSOT/SHARE_FOLDER_ANALYSIS.md for SSOT on share/ layout and non-DMS-managed surfaces
ALLOWED_FILES = {
    # Console v2 / Bootstrap (JSON surfaces)
    "SSOT_SURFACE_V17.json",
    "PM_BOOTSTRAP_STATE.json",
    "kb_registry.json",
    "HANDOFF_KERNEL.json",
    "REALITY_GREEN_SUMMARY.json",
    "planning_context.json",  # planning pipeline output for agents (not a managed doc)
    # Legacy Summaries (JSON)
    "PHASE16_AUDIT_SNAPSHOT.json",
    "PHASE16_CLASSIFICATION_REPORT.json",
    "PHASE18_AGENTS_SYNC_SUMMARY.json",
    "PHASE18_SHARE_EXPORTS_SUMMARY.json",
    "PHASE18_LEDGER_REPAIR_SUMMARY.json",
    "PHASE19_SHARE_HYGIENE_SUMMARY.json",
    "PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.json",
    # PM Introspection Surfaces (Phase 27.M - generated agent working surfaces)
    # See docs/SSOT/SHARE_FOLDER_ANALYSIS.md for SSOT on share/ layout
    "schema_snapshot.md",
    "SSOT_SURFACE_V17.md",
    "agents_md.head.md",
    "governance_freshness.md",
    "hint_registry.md",
    "PM_BOOTSTRAP_STATE.md",
    "planning_lane_status.md",
    "pm_snapshot.md",
    "planning_context.md",
    "HANDOFF_KERNEL.md",
    "REALITY_GREEN_SUMMARY.md",
    "doc_registry.md",
    "next_steps.head.md",
    "doc_sync_state.md",
    "pm_system_introspection_evidence.md",
    "pm_contract.head.md",
    "live_posture.md",
    # Phase specific docs explicitly managed by other tools (Phase 16-23 and beyond)
    "PHASE16_DB_RECON_REPORT.md",
    "PHASE16_PURGE_EXECUTION_LOG.md",
    "PHASE18_AGENTS_SYNC_SUMMARY.md",
    "PHASE18_INDEX.md",
    "PHASE18_LEDGER_REPAIR_SUMMARY.md",
    "PHASE18_SHARE_EXPORTS_SUMMARY.md",
    "PHASE19_SHARE_HYGIENE_SUMMARY.md",
    "PHASE20_INDEX.md",
    "PHASE20_ORCHESTRATOR_UI_MODEL.md",
    "PHASE20_UI_RESET_DECISION.md",
    "PHASE21_CONSOLE_SERVE_PLAN.md",
    "PHASE21_INDEX.md",
    "PHASE22_OPERATOR_WORKFLOW.md",
    "PHASE22_INDEX.md",
    "PHASE23_INDEX.md",
    "PHASE23_STRESS_PLAN.md",
    "PHASE23_BASELINE_NOTE.md",
    "PHASE23_BOOTSTRAP_HARDENING_NOTE.md",
    "PHASE23_STRESS_SMOKE_NOTE.md",
    "PHASE23_FAILURE_INJECTION_NOTE.md",
    "PHASE23_PHASE_DONE_CHECKLIST.md",
    "PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md",
}

ALLOWED_SUBDIRS = {
    "orchestrator",
    "orchestrator_assistant",
    "atlas",
    "exports",
    "handoff",  # kernel bundle directory (PM_KERNEL.json, PM_SUMMARY.md) - Phase 24.E deliverables
    "pm_boot",  # PM/OA boot capsule (Phase 27.H) - generated view of kernel + governance + behavioral contracts
    "oa",  # OA runtime workspace (Phase 27.E) - CONTEXT.json and DSPy program surfaces
}


def check_alignment(mode: str) -> dict:
    if not DB_AVAILABLE:
        return {
            "ok": False,
            "error": "DB_UNAVAILABLE",
            "details": ["Database library not available"],
        }

    report = {
        "ok": True,
        "mode": mode,
        "dms_share_alignment": "OK",
        "missing_in_share": [],
        "missing_in_dms": [],
        "extra_in_share": [],
    }

    try:
        engine = get_control_engine()
        with engine.connect() as conn:
            # 1. Get DMS view
            rows = conn.execute(
                text("""
                SELECT logical_name, share_path, enabled 
                FROM control.doc_registry 
                WHERE share_path IS NOT NULL AND enabled = TRUE
            """)
            ).fetchall()

            dms_map = {}
            for row in rows:
                lp = row.share_path
                # Normalize relative to ROOT
                if lp.startswith("share/"):
                    path = (ROOT / lp).resolve()
                else:
                    path = (SHARE_ROOT / lp).resolve()

                try:
                    rel_path = path.relative_to(SHARE_ROOT)
                    dms_map[str(rel_path)] = row.logical_name
                except ValueError:
                    # Path not inside share?
                    pass

            # 2. Check DMS -> Share (Missing in Share)
            for rel_path, logical_name in dms_map.items():
                full_path = SHARE_ROOT / rel_path
                if not full_path.exists():
                    report["missing_in_share"].append(rel_path)

            # 3. Check Share -> DMS (Missing in DMS / Extra)
            if SHARE_ROOT.exists():
                for item in SHARE_ROOT.iterdir():
                    if item.name in ALLOWED_FILES:
                        continue
                    if item.is_dir():
                        if item.name in ALLOWED_SUBDIRS:
                            continue
                        # Unexpected subdir
                        report["extra_in_share"].append(f"{item.name}/")
                        continue

                    if item.suffix != ".md":
                        # We mostly track MDs for now, but report others as extras if not allowed
                        # report["extra_in_share"].append(item.name) # Too strict?
                        pass

                    rel_name = item.name
                    if rel_name not in dms_map:
                        # Candidate for missing in DMS
                        # We only strictly enforce this for PHASE* files or similar governance docs
                        if rel_name.upper().startswith("PHASE"):
                            report["missing_in_dms"].append(rel_name)
                        else:
                            # Untracked file
                            report["extra_in_share"].append(rel_name)

    except Exception as e:
        return {"ok": False, "error": str(e), "details": []}

    if report["missing_in_share"] or report["missing_in_dms"] or report["extra_in_share"]:
        report["ok"] = False
        report["dms_share_alignment"] = "BROKEN"

    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="HINT", choices=["HINT", "STRICT"])
    args = parser.parse_args()

    result = check_alignment(args.mode)

    print(json.dumps(result, indent=2))

    if args.mode == "STRICT" and not result["ok"]:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
