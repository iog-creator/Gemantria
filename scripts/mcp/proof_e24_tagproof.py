#!/usr/bin/env python3
"""
PLAN-072 M2 E24: Tagproof Bundle Proof

Generates tagproof proof from Phase-2 tagproof bundle, validating
that all required components are present and valid.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "evidence"
SHARE_MCP = ROOT / "share" / "mcp"
TAGPROOF_PROOF_PATH = SHARE_MCP / "tagproof_proof.json"
TAGPROOF_BUNDLE = EVIDENCE_DIR / "tagproof_phase2_bundle.json"


def main() -> int:
    """Generate tagproof proof."""
    SHARE_MCP.mkdir(parents=True, exist_ok=True)

    # Load tagproof bundle
    if not TAGPROOF_BUNDLE.exists():
        proof = {
            "ok": False,
            "error": "tagproof_phase2_bundle.json missing",
            "generated_at": datetime.now(UTC).isoformat(),
        }
        TAGPROOF_PROOF_PATH.write_text(json.dumps(proof, indent=2), encoding="utf-8")
        print(json.dumps(proof, indent=2))
        return 1

    try:
        bundle = json.loads(TAGPROOF_BUNDLE.read_text(encoding="utf-8"))
    except Exception as e:
        proof = {
            "ok": False,
            "error": f"Failed to load tagproof bundle: {e}",
            "generated_at": datetime.now(UTC).isoformat(),
        }
        TAGPROOF_PROOF_PATH.write_text(json.dumps(proof, indent=2), encoding="utf-8")
        print(json.dumps(proof, indent=2))
        return 1

    # Validate tagproof proof: required components must be present
    # In HINT mode, allow browser_screenshot failures (similar to guard_tagproof_phase2.py)
    import os

    strict_mode = os.getenv("STRICT_MODE", "0") == "1" or os.getenv("CI") == "true"

    components = bundle.get("components", {})
    required = ["tv_coverage", "gatekeeper_coverage", "regeneration_guard", "browser_screenshot"]
    all_present = all(key in components for key in required)

    # Check if components have errors (but allow browser_screenshot failures in HINT mode)
    component_errors = []
    for key in required:
        comp = components.get(key, {})
        # Skip browser_screenshot in HINT mode
        if key == "browser_screenshot" and not strict_mode:
            continue
        if "error" in comp and comp.get("error") != "missing":
            component_errors.append(key)
        # Also check if component has ok=False (guard verdict style)
        if comp.get("ok") is False and "error" not in comp:
            component_errors.append(key)

    no_errors = len(component_errors) == 0

    proof = {
        "ok": all_present and no_errors,
        "method": "tagproof_bundle",
        "mode": "STRICT" if strict_mode else "HINT",
        "components_count": len(components),
        "required_present": all_present,
        "no_errors": no_errors,
        "component_errors": component_errors if component_errors else None,
        "generated_at": datetime.now(UTC).isoformat(),
    }

    TAGPROOF_PROOF_PATH.write_text(json.dumps(proof, indent=2), encoding="utf-8")
    print(json.dumps(proof, indent=2))
    return 0 if proof["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
