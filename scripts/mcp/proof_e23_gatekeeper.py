#!/usr/bin/env python3
"""
PLAN-072 M2 E23: Gatekeeper Coverage Proof

Generates gatekeeper proof from gatekeeper coverage manifest, validating
that all violation codes are covered by tests.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "evidence"
SHARE_MCP = ROOT / "share" / "mcp"
GATEKEEPER_PROOF_PATH = SHARE_MCP / "gatekeeper_proof.json"
GATEKEEPER_COVERAGE = EVIDENCE_DIR / "gatekeeper_coverage.json"


def main() -> int:
    """Generate gatekeeper proof."""
    SHARE_MCP.mkdir(parents=True, exist_ok=True)

    # Load gatekeeper coverage
    if not GATEKEEPER_COVERAGE.exists():
        proof = {
            "ok": False,
            "error": "gatekeeper_coverage.json missing",
            "generated_at": datetime.now(UTC).isoformat(),
        }
        GATEKEEPER_PROOF_PATH.write_text(json.dumps(proof, indent=2), encoding="utf-8")
        print(json.dumps(proof, indent=2))
        return 1

    try:
        coverage = json.loads(GATEKEEPER_COVERAGE.read_text(encoding="utf-8"))
    except Exception as e:
        proof = {
            "ok": False,
            "error": f"Failed to load gatekeeper coverage: {e}",
            "generated_at": datetime.now(UTC).isoformat(),
        }
        GATEKEEPER_PROOF_PATH.write_text(json.dumps(proof, indent=2), encoding="utf-8")
        print(json.dumps(proof, indent=2))
        return 1

    # Validate gatekeeper proof: all violation codes must be covered
    violation_codes = coverage.get("violation_codes", [])
    coverage_map = coverage.get("coverage", {})
    all_covered = all(coverage_map.get(code, False) for code in violation_codes)

    proof = {
        "ok": all_covered,
        "method": "gatekeeper_coverage",
        "violation_codes_count": len(violation_codes),
        "all_covered": all_covered,
        "generated_at": datetime.now(UTC).isoformat(),
    }

    GATEKEEPER_PROOF_PATH.write_text(json.dumps(proof, indent=2), encoding="utf-8")
    print(json.dumps(proof, indent=2))
    return 0 if all_covered else 1


if __name__ == "__main__":
    sys.exit(main())
