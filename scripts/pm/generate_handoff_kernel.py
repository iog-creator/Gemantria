#!/usr/bin/env python3
"""
Generate share/HANDOFF_KERNEL.json
SSOT-driven generator for the Phase 24.E Handoff Kernel.
"""

import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHARE = ROOT / "share"


def get_git_branch() -> str:
    try:
        res = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return "unknown"


def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def find_latest_ssot_surface() -> Path:
    # Pattern: share/SSOT_SURFACE_V*.json
    candidates = list(SHARE.glob("SSOT_SURFACE_V*.json"))
    if not candidates:
        raise FileNotFoundError("No SSOT_SURFACE_V*.json found in share/")

    # Sort by version number implicit in filename or modification time?
    # Filename format: SSOT_SURFACE_V{N}.json
    # Extract N and sort
    def extract_version(p: Path) -> int:
        try:
            # SSOT_SURFACE_V17.json -> 17
            stem = p.stem  # SSOT_SURFACE_V17
            v_part = stem.split("_V")[-1]
            return int(v_part)
        except ValueError:
            return -1

    candidates.sort(key=extract_version, reverse=True)
    return candidates[0]


def main():
    try:
        # 1. Load Bootstrap State
        bootstrap_path = SHARE / "PM_BOOTSTRAP_STATE.json"
        bootstrap = load_json(bootstrap_path)
        b_meta = bootstrap.get("meta", {})

        # 2. Load SSOT Surface
        ssot_path = find_latest_ssot_surface()
        ssot = load_json(ssot_path)

        # 3. Load Reality Green Summary
        rg_summary_path = SHARE / "REALITY_GREEN_SUMMARY.json"
        # If missing, we can't fully populate health, but valid generator execution implies it exists (or we fail)
        if not rg_summary_path.exists():
            print(f"WARNING: {rg_summary_path} not found. Health data will be incomplete/false.", file=sys.stderr)
            rg_summary = {"reality_green": False, "checks": []}
        else:
            rg_summary = load_json(rg_summary_path)

        # 4. Extract Data
        # Phase info
        b_phase = b_meta.get("current_phase")
        b_last = b_meta.get("last_completed_phase")

        s_phase = ssot.get("current_phase")
        s_last = ssot.get("last_completed_phase")

        # Consistency Check
        if str(b_phase) != str(s_phase):
            print(f"WARNING: Phase mismatch! Bootstrap={b_phase}, SSOT={s_phase}", file=sys.stderr)
            # We continue but this is a degraded state

        # Health
        rg_ok = rg_summary.get("reality_green", False)
        checks_map = {}
        target_checks = ["DMS Alignment", "Bootstrap Consistency", "Share Sync Policy", "Backup System"]

        summary_checks = rg_summary.get("checks", [])
        # Convert list to dict for lookup
        summary_checks_lookup = {c.get("name"): c.get("passed", False) for c in summary_checks}

        for name in target_checks:
            checks_map[name] = summary_checks_lookup.get(name, False)

        # 5. Build Kernel
        kernel = {
            "version": 1,
            "current_phase": str(b_phase),
            "last_completed_phase": str(b_last),
            "branch": get_git_branch(),
            "health": {"reality_green": rg_ok, "checks": checks_map},
            "required_surfaces": [f"share/{bootstrap_path.name}", f"share/{ssot_path.name}"],
            "notes": {
                "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "reality_green_summary": f"share/{rg_summary_path.name}",
                "dms_share_alignment": ssot.get("dms_share_alignment", "UNKNOWN"),
                "dms_share_mismatch_count": ssot.get("dms_share_mismatch_count", -1),
            },
        }

        # 6. Write
        output_path = SHARE / "HANDOFF_KERNEL.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(kernel, f, indent=2)
            f.write("\n")  # POSIX newline

        print(f"Generated {output_path}")
        print(json.dumps(kernel, indent=2))

    except Exception as e:
        print(f"Error generating handoff kernel: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
