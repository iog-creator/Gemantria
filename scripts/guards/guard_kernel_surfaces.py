#!/usr/bin/env python3
"""
Guard: check_kernel_surfaces.py

Verifies the integrity of the Handoff Kernel Bundle:
- share/handoff/PM_KERNEL.json
- share/handoff/PM_SUMMARY.md

Checks:
1. Files exist.
2. PM_KERNEL.json parses and adheres to basic schema.
3. Ground truth files referenced in kernel exist.
4. current_phase matches PM_BOOTSTRAP_STATE.json phase.
"""

import argparse
import json
import sys
from pathlib import Path

# Setup paths
REPO_ROOT = Path(__file__).resolve().parents[2]
SHARE_DIR = REPO_ROOT / "share"
HANDOFF_DIR = SHARE_DIR / "handoff"
KERNEL_JSON = HANDOFF_DIR / "PM_KERNEL.json"
SUMMARY_MD = HANDOFF_DIR / "PM_SUMMARY.md"
BOOTSTRAP_STATE = SHARE_DIR / "PM_BOOTSTRAP_STATE.json"


def check_file_exists(path: Path, issues: list):
    if not path.exists():
        issues.append(f"Missing file: {path.relative_to(REPO_ROOT)}")
        return False
    return True


def run_checks() -> dict:
    issues = []
    details = {}

    # 1. Existence Checks
    exists_json = check_file_exists(KERNEL_JSON, issues)
    exists_md = check_file_exists(SUMMARY_MD, issues)

    if not exists_json:
        # Cannot proceed further
        return {"ok": False, "issues": issues, "details": details}

    # 2. Parse JSON & Schema Check
    try:
        with open(KERNEL_JSON, encoding="utf-8") as f:
            kernel_data = json.load(f)
    except json.JSONDecodeError as e:
        issues.append(f"Invalid JSON in PM_KERNEL.json: {e}")
        return {"ok": False, "issues": issues, "details": details}

    required_keys = [
        "current_phase",
        "branch",
        "last_completed_phase",
        "next_actions",
        "ground_truth_files",
        "constraints",
        "generated_at_utc",
    ]

    missing_keys = [k for k in required_keys if k not in kernel_data]
    if missing_keys:
        issues.append(f"Missing keys in PM_KERNEL.json: {missing_keys}")

    # 3. Content consistency with Bootstrap
    if BOOTSTRAP_STATE.exists():
        try:
            with open(BOOTSTRAP_STATE, encoding="utf-8") as f:
                bootstrap = json.load(f)

            bs_phase = bootstrap.get("meta", {}).get("current_phase")
            k_phase = kernel_data.get("current_phase")

            if bs_phase and k_phase and bs_phase != k_phase:
                issues.append(f"Phase Mismatch: Bootstrap={bs_phase} vs Kernel={k_phase}")
        except Exception as e:
            issues.append(f"Error reading Bootstrap State: {e}")
    else:
        issues.append("PM_BOOTSTRAP_STATE.json missing (cannot verify phase match)")

    # 4. Ground Truth Files verification
    gt_files = kernel_data.get("ground_truth_files", [])
    if isinstance(gt_files, list):
        for rel_path in gt_files:
            abs_path = REPO_ROOT / rel_path
            if not abs_path.exists():
                issues.append(f"Ground Truth file missing: {rel_path}")

    return {
        "ok": len(issues) == 0,
        "issues": issues,
        "details": {
            "kernel_path": str(KERNEL_JSON.relative_to(REPO_ROOT)),
            "checked_phase": kernel_data.get("current_phase"),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Guard Handoff Kernel Surfaces")
    parser.add_argument("--mode", choices=["HINT", "STRICT"], default="HINT", help="Guard mode")
    args = parser.parse_args()

    result = run_checks()

    if args.mode == "HINT":
        if result["ok"]:
            print(json.dumps(result, indent=2))
            sys.exit(0)
        else:
            # In HINT mode, we print issues but exit 0 (unless catastrophic, but specs say warn)
            result["status"] = "WARNING (HINT MODE)"
            print(json.dumps(result, indent=2))
            sys.exit(0)
    else:  # STRICT
        if result["ok"]:
            print(json.dumps(result, indent=2))
            sys.exit(0)
        else:
            print(json.dumps(result, indent=2))
            sys.exit(1)


if __name__ == "__main__":
    main()
