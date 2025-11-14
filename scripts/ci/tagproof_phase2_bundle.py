#!/usr/bin/env python3
"""
PLAN-080 E100 — Phase-2 Tagproof Bundle Generator

Assembles a Phase-2 tagproof bundle that combines all key guards/receipts:
- TV coverage (E96)
- Gatekeeper coverage (E97)
- Regeneration (E98)
- Browser/screenshot integrated (E99)

Outputs a single JSON bundle to evidence/tagproof_phase2_bundle.json.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "evidence"
BUNDLE_PATH = EVIDENCE_DIR / "tagproof_phase2_bundle.json"

# Component file paths
COMPONENT_PATHS = {
    "tv_coverage": EVIDENCE_DIR / "tv_coverage_receipt.json",
    "gatekeeper_coverage": EVIDENCE_DIR / "gatekeeper_coverage.json",
    "regeneration_receipt": EVIDENCE_DIR / "regenerate_all_receipt.json",
    "regeneration_guard": EVIDENCE_DIR / "guard_regenerate_all.json",
    "browser_screenshot": EVIDENCE_DIR / "browser_screenshot_integrated.json",
    # Optional guard verdicts
    "tv_coverage_guard": EVIDENCE_DIR / "guard_tv_coverage.json",
    "gatekeeper_coverage_guard": EVIDENCE_DIR / "guard_gatekeeper_coverage.json",
}


def _load_component(path: Path) -> dict[str, Any] | None:
    """Load a component JSON file, returning None if missing or invalid."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def main() -> int:
    """Generate the Phase-2 tagproof bundle."""
    components: dict[str, Any] = {}
    errors: dict[str, str] = {}

    # Load required components
    for key, path in COMPONENT_PATHS.items():
        component = _load_component(path)
        if component is None:
            errors[key] = "missing"
            components[key] = {"error": "missing"}
        else:
            components[key] = component

    # Structure the bundle
    bundle = {
        "version": 1,
        "timestamp": datetime.now(UTC).isoformat(),
        "components": components,
        "meta": {
            "phase": 2,
            "plan": "PLAN-080",
            "notes": "Phase-2 tagproof bundle",
            "errors": errors if errors else None,
        },
    }

    # Write bundle
    BUNDLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with BUNDLE_PATH.open("w") as f:
        json.dump(bundle, f, indent=2)

    print(f"Generated Phase-2 tagproof bundle: {BUNDLE_PATH}")
    if errors:
        print(f"Warnings: {len(errors)} component(s) missing: {', '.join(errors.keys())}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
