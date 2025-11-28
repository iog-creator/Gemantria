#!/usr/bin/env python3
"""
PLAN-072 M2 E21: POR (Proof of Record) Proof

Generates POR proof from regeneration receipt, validating that all
regeneration steps completed successfully.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "evidence"
SHARE_MCP = ROOT / "share" / "mcp"
POR_PROOF_PATH = SHARE_MCP / "por_proof.json"
REGENERATION_RECEIPT = EVIDENCE_DIR / "regenerate_all_receipt.json"


def main() -> int:
    """Generate POR proof."""
    SHARE_MCP.mkdir(parents=True, exist_ok=True)

    # Load regeneration receipt
    if not REGENERATION_RECEIPT.exists():
        proof = {
            "ok": False,
            "error": "regeneration_receipt.json missing",
            "generated_at": datetime.now(UTC).isoformat(),
        }
        POR_PROOF_PATH.write_text(json.dumps(proof, indent=2), encoding="utf-8")
        print(json.dumps(proof, indent=2))
        return 1

    try:
        receipt = json.loads(REGENERATION_RECEIPT.read_text(encoding="utf-8"))
    except Exception as e:
        proof = {
            "ok": False,
            "error": f"Failed to load regeneration receipt: {e}",
            "generated_at": datetime.now(UTC).isoformat(),
        }
        POR_PROOF_PATH.write_text(json.dumps(proof, indent=2), encoding="utf-8")
        print(json.dumps(proof, indent=2))
        return 1

    # Validate POR: all steps must have succeeded
    ok = receipt.get("ok", False)
    steps = receipt.get("steps", [])
    all_steps_ok = all(step.get("success", False) for step in steps)

    proof = {
        "ok": ok and all_steps_ok,
        "method": "regeneration_receipt",
        "receipt_ok": ok,
        "all_steps_ok": all_steps_ok,
        "steps_count": len(steps),
        "generated_at": datetime.now(UTC).isoformat(),
    }

    POR_PROOF_PATH.write_text(json.dumps(proof, indent=2), encoding="utf-8")
    print(json.dumps(proof, indent=2))
    return 0 if proof["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
