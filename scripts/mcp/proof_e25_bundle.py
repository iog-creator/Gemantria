#!/usr/bin/env python3
"""
PLAN-072 M2 E25: Complete Bundle Proof

Generates complete bundle proof aggregating all E21-E24 proofs,
validating that the entire proof suite is complete.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHARE_MCP = ROOT / "share" / "mcp"
BUNDLE_PROOF_PATH = SHARE_MCP / "bundle_proof.json"

# Proof files from E21-E24
PROOF_FILES = {
    "e21_por": SHARE_MCP / "por_proof.json",
    "e22_schema": SHARE_MCP / "schema_proof.json",
    "e23_gatekeeper": SHARE_MCP / "gatekeeper_proof.json",
    "e24_tagproof": SHARE_MCP / "tagproof_proof.json",
}


def main() -> int:
    """Generate bundle proof."""
    SHARE_MCP.mkdir(parents=True, exist_ok=True)

    proofs: dict[str, dict] = {}
    all_ok = True

    # Load all individual proofs
    for name, path in PROOF_FILES.items():
        if not path.exists():
            proofs[name] = {"ok": False, "error": "missing"}
            all_ok = False
            continue

        try:
            proof_data = json.loads(path.read_text(encoding="utf-8"))
            proofs[name] = proof_data
            if not proof_data.get("ok", False):
                all_ok = False
        except Exception as e:
            proofs[name] = {"ok": False, "error": f"Failed to load: {e}"}
            all_ok = False

    bundle_proof = {
        "ok": all_ok,
        "method": "bundle_aggregate",
        "proofs": proofs,
        "proofs_count": len(proofs),
        "all_ok": all_ok,
        "generated_at": datetime.now(UTC).isoformat(),
    }

    BUNDLE_PROOF_PATH.write_text(json.dumps(bundle_proof, indent=2), encoding="utf-8")
    print(json.dumps(bundle_proof, indent=2))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
