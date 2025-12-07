#!/usr/bin/env python3
"""
Guard: Bootstrap Consistency (Phase 24.A)

Verifies that:
1. PM_BOOTSTRAP_STATE.json current_phase matches SSOT_SURFACE_V*.json.
2. PM_BOOTSTRAP_STATE.json last_completed_phase matches SSOT_SURFACE_V*.json.
3. (Optional) Phases listed in bootstrap exist in SSOT/DMS.
"""

import json
import sys
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP_PATH = ROOT / "share" / "PM_BOOTSTRAP_STATE.json"
SSOT_SURFACE_PATH = ROOT / "share" / "SSOT_SURFACE_V17.json"


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check_consistency(mode: str) -> dict:
    bootstrap = load_json(BOOTSTRAP_PATH)
    ssot = load_json(SSOT_SURFACE_PATH)

    mismatches = []

    if not bootstrap:
        mismatches.append(f"Bootstrap file missing at {BOOTSTRAP_PATH}")
    if not ssot:
        mismatches.append(f"SSOT Surface file missing at {SSOT_SURFACE_PATH}")

    if not mismatches:
        # Check current_phase
        b_cur = str(bootstrap.get("meta", {}).get("current_phase", "UNKNOWN"))
        s_cur = str(ssot.get("current_phase", "UNKNOWN"))

        if b_cur != s_cur:
            mismatches.append(f"current_phase mismatch: Bootstrap={b_cur}, SSOT={s_cur}")

        # Check last_completed_phase
        b_last = str(bootstrap.get("meta", {}).get("last_completed_phase", "UNKNOWN"))
        s_last = str(ssot.get("last_completed_phase", "UNKNOWN"))

        if b_last != s_last:
            mismatches.append(f"last_completed_phase mismatch: Bootstrap={b_last}, SSOT={s_last}")

        # Check integrity of phases map? (Optional per spec, leaving simple for now)

    ok = len(mismatches) == 0

    report = {
        "ok": ok,
        "mode": mode,
        "bootstrap_current_phase": bootstrap.get("meta", {}).get("current_phase"),
        "ssot_current_phase": ssot.get("current_phase"),
        "mismatches": mismatches,
    }

    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["HINT", "STRICT"], default="HINT")
    args = parser.parse_args()

    report = check_consistency(args.mode)
    print(json.dumps(report, indent=2))

    if args.mode == "STRICT" and not report["ok"]:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
