#!/usr/bin/env python3
"""
PLAN-072 M2 E22: Schema Proof

Generates schema proof from control-plane schema snapshot, validating
that schema introspection is working correctly.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHARE_MCP = ROOT / "share" / "mcp"
SHARE_ATLAS = ROOT / "share" / "atlas" / "control_plane"
SCHEMA_PROOF_PATH = SHARE_MCP / "schema_proof.json"
SCHEMA_SNAPSHOT = SHARE_ATLAS / "schema_snapshot.json"


def main() -> int:
    """Generate schema proof."""
    SHARE_MCP.mkdir(parents=True, exist_ok=True)

    # Load schema snapshot
    if not SCHEMA_SNAPSHOT.exists():
        proof = {
            "ok": False,
            "error": "schema_snapshot.json missing",
            "generated_at": datetime.now(UTC).isoformat(),
        }
        SCHEMA_PROOF_PATH.write_text(json.dumps(proof, indent=2), encoding="utf-8")
        print(json.dumps(proof, indent=2))
        return 1

    try:
        snapshot = json.loads(SCHEMA_SNAPSHOT.read_text(encoding="utf-8"))
    except Exception as e:
        proof = {
            "ok": False,
            "error": f"Failed to load schema snapshot: {e}",
            "generated_at": datetime.now(UTC).isoformat(),
        }
        SCHEMA_PROOF_PATH.write_text(json.dumps(proof, indent=2), encoding="utf-8")
        print(json.dumps(proof, indent=2))
        return 1

    # Validate schema proof: must have tables and schema field
    schema = snapshot.get("schema")
    tables = snapshot.get("tables", [])
    ok = schema is not None and len(tables) > 0

    proof = {
        "ok": ok,
        "method": "schema_snapshot",
        "schema": schema,
        "tables_count": len(tables),
        "generated_at": datetime.now(UTC).isoformat(),
    }

    SCHEMA_PROOF_PATH.write_text(json.dumps(proof, indent=2), encoding="utf-8")
    print(json.dumps(proof, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
