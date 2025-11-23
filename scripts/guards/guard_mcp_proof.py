#!/usr/bin/env python3
"""
Guard: Knowledge MCP Proof Snapshot Validation (PLAN-073 M1 E05)

Validates that the proof snapshot exists, matches its schema, and overall_ok
is consistent with component statuses.
- HINT mode (default): Tolerates missing snapshot/components, emits hints, exits 0
- STRICT mode: Requires valid snapshot with overall_ok=True, fails otherwise

Rule References: RFC-078 (Postgres Knowledge MCP), Rule 050 (OPS Contract),
Rule 039 (Execution Contract)

Usage:
    python scripts/guards/guard_mcp_proof.py
    make guard.mcp.proof
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, UTC
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

try:
    from jsonschema import ValidationError, validate
except ImportError as e:
    print(json.dumps({"ok": False, "error": f"jsonschema not available: {e}"}))
    sys.exit(1)

EVIDENCE_DIR = ROOT / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
EVIDENCE_FILE = EVIDENCE_DIR / "guard_mcp_proof.json"

SCHEMA_PATH = ROOT / "schemas" / "mcp_proof_snapshot.v1.schema.json"
PROOF_JSON = ROOT / "share" / "mcp" / "knowledge_mcp_proof.json"


def _is_strict_mode() -> bool:
    """Determine if running in STRICT mode."""
    return os.getenv("STRICT_MODE", "0") == "1" or os.getenv("CI") == "true"


def _load_schema() -> dict | None:
    """Load JSON schema for validation."""
    if not SCHEMA_PATH.exists():
        return None
    try:
        return json.loads(SCHEMA_PATH.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def _validate_overall_ok_consistency(snapshot: dict) -> tuple[bool, str | None]:
    """Validate that overall_ok is consistent with component statuses."""
    components = snapshot.get("components", {})
    overall_ok = snapshot.get("overall_ok", False)

    # Required components: E01, E02, E04
    required_ok = (
        components.get("e01_schema", {}).get("ok", False)
        and components.get("e02_ro_dsn", {}).get("ok", False)
        and components.get("e04_query", {}).get("ok", False)
    )

    if overall_ok != required_ok:
        return False, f"overall_ok ({overall_ok}) inconsistent with required components ({required_ok})"

    return True, None


def main() -> int:
    """Main guard logic."""
    is_strict = _is_strict_mode()
    mode = "STRICT" if is_strict else "HINT"

    verdict = {
        "ok": True,
        "mode": mode,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "snapshot_present": False,
        "snapshot_valid": False,
        "overall_ok_consistent": False,
        "details": {},
    }

    # Check if snapshot exists
    if not PROOF_JSON.exists():
        verdict["ok"] = False
        verdict["details"]["error"] = "Proof snapshot file not found"
        if is_strict:
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            print("[guard_mcp_proof] ERROR: Proof snapshot not found (STRICT mode)", file=sys.stderr)
            return 1
        else:
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            print("[guard_mcp_proof] HINT: Proof snapshot not found (HINT mode)", file=sys.stderr)
            return 0

    verdict["snapshot_present"] = True

    # Load snapshot
    try:
        snapshot = json.loads(PROOF_JSON.read_text())
    except (OSError, json.JSONDecodeError) as e:
        verdict["ok"] = False
        verdict["details"]["error"] = f"Failed to parse snapshot: {e}"
        if is_strict:
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            print(f"[guard_mcp_proof] ERROR: Failed to parse snapshot (STRICT mode): {e}", file=sys.stderr)
            return 1
        else:
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            print(f"[guard_mcp_proof] HINT: Failed to parse snapshot (HINT mode): {e}", file=sys.stderr)
            return 0

    # Validate against schema
    schema = _load_schema()
    if schema:
        try:
            validate(instance=snapshot, schema=schema)
            verdict["snapshot_valid"] = True
        except ValidationError as e:
            verdict["ok"] = False
            verdict["details"]["validation_error"] = e.message
            if is_strict:
                print(json.dumps(verdict, indent=2))
                EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
                print(f"[guard_mcp_proof] ERROR: Schema validation failed (STRICT mode): {e.message}", file=sys.stderr)
                return 1
            else:
                print(json.dumps(verdict, indent=2))
                EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
                print(f"[guard_mcp_proof] HINT: Schema validation failed (HINT mode): {e.message}", file=sys.stderr)
                return 0
    else:
        # Schema missing, skip validation in HINT mode
        if is_strict:
            verdict["ok"] = False
            verdict["details"]["error"] = "Schema file not found"
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            print("[guard_mcp_proof] ERROR: Schema file not found (STRICT mode)", file=sys.stderr)
            return 1
        else:
            verdict["snapshot_valid"] = True  # Assume valid if schema missing in HINT mode

    # Validate overall_ok consistency
    is_consistent, error_msg = _validate_overall_ok_consistency(snapshot)
    verdict["overall_ok_consistent"] = is_consistent

    if not is_consistent:
        verdict["ok"] = False
        verdict["details"]["consistency_error"] = error_msg
        if is_strict:
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            print(f"[guard_mcp_proof] ERROR: Overall OK inconsistency (STRICT mode): {error_msg}", file=sys.stderr)
            return 1
        else:
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            print(f"[guard_mcp_proof] HINT: Overall OK inconsistency (HINT mode): {error_msg}", file=sys.stderr)
            return 0

    # All checks passed
    verdict["ok"] = True
    print(json.dumps(verdict, indent=2))
    EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
