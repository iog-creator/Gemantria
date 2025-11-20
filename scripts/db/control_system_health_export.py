#!/usr/bin/env python3
"""
System Health Export for Atlas

Exports system health aggregate (DB + LM + graph) to share/atlas/control_plane/
for Atlas visualization and UI consumption.

Tolerates db_off and LM-off (no DB or LM Studio required; best-effort exports).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.system.system_health import compute_system_health

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "share" / "atlas" / "control_plane"
OUT_PATH = OUT_DIR / "system_health.json"


def main() -> int:
    """Export system health to JSON file."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        health = compute_system_health()
        OUT_PATH.write_text(json.dumps(health, indent=2) + "\n")
        print(f">> System health exported to {OUT_PATH}")
        return 0
    except Exception as e:
        # Fail gracefully - write empty/error export
        error_export = {
            "ok": False,
            "error": str(e),
            "components": {
                "db": {"ok": False, "mode": "unknown"},
                "lm": {"ok": False, "mode": "unknown"},
                "graph": {"ok": False, "mode": "unknown"},
            },
        }
        OUT_PATH.write_text(json.dumps(error_export, indent=2) + "\n")
        print(f">> System health export failed, wrote error export to {OUT_PATH}")
        return 0  # Always exit 0 (hermetic)


if __name__ == "__main__":
    sys.exit(main())
