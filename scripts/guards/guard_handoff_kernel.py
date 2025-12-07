#!/usr/bin/env python3
"""
Guard: Handoff Kernel
Verifies share/HANDOFF_KERNEL.json is consistent with system state.
Phase 24.E
"""

import json
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHARE = ROOT / "share"


def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def run_check(strict: bool):
    try:
        # Load Files
        kernel_path = SHARE / "HANDOFF_KERNEL.json"
        bootstrap_path = SHARE / "PM_BOOTSTRAP_STATE.json"

        # Find SSOT
        candidates = list(SHARE.glob("SSOT_SURFACE_V*.json"))
        if not candidates:
            return fail("No SSOT_SURFACE_V*.json found", strict)

        # Logic to pick the one referenced in kernel or latest?
        # The kernel *specifies* required surfaces. We should check if they exist and match.

        if not kernel_path.exists():
            return fail("share/HANDOFF_KERNEL.json missing", strict)

        kernel = load_json(kernel_path)
        bootstrap = load_json(bootstrap_path)

        rg_summary_path = SHARE / "REALITY_GREEN_SUMMARY.json"
        rg_summary = load_json(rg_summary_path) if rg_summary_path.exists() else {"reality_green": False, "checks": []}

        mismatches = []

        # 1. Phase Consistency
        k_curr = str(kernel.get("current_phase"))
        k_last = str(kernel.get("last_completed_phase"))

        b_curr = str(bootstrap.get("meta", {}).get("current_phase"))
        b_last = str(bootstrap.get("meta", {}).get("last_completed_phase"))

        if k_curr != b_curr:
            mismatches.append(f"Kernel current_phase={k_curr} != Bootstrap={b_curr}")
        if k_last != b_last:
            mismatches.append(f"Kernel last_completed_phase={k_last} != Bootstrap={b_last}")

        # SSOT Consistency (check against ALL referenced SSOT surfaces or just the latest found?)
        # Let's check against valid referenced SSOT surface in kernel
        req_surfaces = kernel.get("required_surfaces", [])
        ssot_ref = next((s for s in req_surfaces if "SSOT_SURFACE_V" in s), None)

        if not ssot_ref:
            mismatches.append("No SSOT_SURFACE_V* in required_surfaces")
        else:
            ssot_path = ROOT / ssot_ref
            if not ssot_path.exists():
                mismatches.append(f"Referenced SSOT surface missing: {ssot_ref}")
            else:
                ssot = load_json(ssot_path)
                s_curr = str(ssot.get("current_phase"))
                s_last = str(ssot.get("last_completed_phase"))

                if k_curr != s_curr:
                    mismatches.append(f"Kernel current_phase={k_curr} != SSOT({ssot_ref})={s_curr}")
                if k_last != s_last:
                    mismatches.append(f"Kernel last_completed_phase={k_last} != SSOT({ssot_ref})={s_last}")

        # 2. Surface References
        if "share/PM_BOOTSTRAP_STATE.json" not in req_surfaces:
            mismatches.append("share/PM_BOOTSTRAP_STATE.json missing from required_surfaces")

        # 3. Reality Green Consistency
        k_rg = kernel.get("health", {}).get("reality_green")
        s_rg = rg_summary.get("reality_green")

        if k_rg != s_rg:
            mismatches.append(f"Kernel.health.reality_green={k_rg} != REALITY_GREEN_SUMMARY={s_rg}")

        k_checks = kernel.get("health", {}).get("checks", {})
        s_checks_list = rg_summary.get("checks", [])
        s_checks_map = {c.get("name"): c.get("passed") for c in s_checks_list}

        for name, k_passed in k_checks.items():
            if name not in s_checks_map:
                mismatches.append(f"Kernel check '{name}' not found in REALITY_GREEN_SUMMARY")
            elif k_passed != s_checks_map[name]:
                mismatches.append(f"Kernel check '{name}'={k_passed} != REALITY_GREEN_SUMMARY={s_checks_map[name]}")

        # 4. Schema Sanity
        if "version" not in kernel:
            mismatches.append("Missing version")
        if not kernel.get("branch"):
            mismatches.append("Missing/empty branch")

        # Result
        result = {
            "ok": len(mismatches) == 0,
            "mode": "STRICT" if strict else "HINT",
            "mismatches": mismatches,
        }

        print(json.dumps(result, indent=2))

        if strict and not result["ok"]:
            sys.exit(1)

    except Exception as e:
        print(json.dumps({"ok": False, "mode": "STRICT", "mismatches": [str(e)]}, indent=2))
        sys.exit(1)


def fail(msg, strict):
    res = {"ok": False, "mode": "STRICT" if strict else "HINT", "mismatches": [msg]}
    print(json.dumps(res, indent=2))
    if strict:
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["STRICT", "HINT"], default="HINT")
    args = parser.parse_args()

    run_check(args.mode == "STRICT")
