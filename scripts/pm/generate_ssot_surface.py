#!/usr/bin/env python3
"""
generate_ssot_surface.py

Generates share/SSOT_SURFACE_V17.json with DMS alignment status.
Replacing manual/static generation.

Schema V17 Extensions (Phase 24.B):
- dms_share_alignment: "OK" | "BROKEN"
- dms_share_mismatch_count: int
"""

import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHARE_ROOT = ROOT / "share"
SSOT_FILE = SHARE_ROOT / "SSOT_SURFACE_V17.json"


def get_dms_alignment_status() -> dict:
    """Run guard in HINT mode to get structured status."""
    guard_script = ROOT / "scripts" / "guards" / "guard_dms_share_alignment.py"
    if not guard_script.exists():
        return {
            "ok": False,
            "mode": "MISSING_GUARD",
            "dms_share_alignment": "UNKNOWN",
            "mismatch_count": -1,
        }

    try:
        res = subprocess.run([sys.executable, str(guard_script), "--mode", "HINT"], capture_output=True, text=True)
        data = json.loads(res.stdout)

        # Calculate mismatch count
        mismatch_count = 0
        mismatch_count += len(data.get("missing_in_share", []))
        mismatch_count += len(data.get("missing_in_dms", []))
        # extra_in_share can vary based on whitelists, but technically is a mismatch
        mismatch_count += len(data.get("extra_in_share", []))

        return {
            "dms_share_alignment": data.get("dms_share_alignment", "UNKNOWN"),
            "dms_share_mismatch_count": mismatch_count,
        }
    except Exception as e:
        return {"dms_share_alignment": "ERROR", "dms_share_mismatch_count": -1, "error": str(e)}


def generate_ssot_surface():
    ts = datetime.now(UTC).isoformat()

    alignment = get_dms_alignment_status()

    # Base structure (mimicking observed V17 structure + extensions)
    data = {
        "version": 17,
        "generated_by": "generate_ssot_surface.py",
        "generated_at": ts,
        "description": "High-level SSOT surface snapshot for Gemantria.",
        "db": {
            "status": "online",  # TODO: hook into actual DB check if needed
            "last_checked_at": ts,
        },
        "dms": {
            "doc_registry_count": 0,  # Placeholder, could query DB
            "hint_registry_status": "active",
        },
        "phases": {
            "last_completed": 23,
            "current": 24,
            "notes": "Phases 18-23 rebuilt from recovery doc. Phase 24 in progress.",
        },
        # Phase 24.B Extension
        "dms_share_alignment": alignment.get("dms_share_alignment", "UNKNOWN"),
        "dms_share_mismatch_count": alignment.get("dms_share_mismatch_count", -1),
        # Phase 24.A Extension (Unpinning)
        "current_phase": "24",
        "last_completed_phase": "23",
    }

    SHARE_ROOT.mkdir(parents=True, exist_ok=True)
    SSOT_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Generated {SSOT_FILE}")


if __name__ == "__main__":
    generate_ssot_surface()
