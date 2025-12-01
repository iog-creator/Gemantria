#!/usr/bin/env python3
"""
Generate Knowledge MCP Proof Snapshot (PLAN-073 M1 E05)

Aggregates E01-E04 proof artifacts into a unified snapshot.
Reads evidence files and optionally envelope.json, computes overall_ok,
and writes knowledge_mcp_proof.{json,txt}.

Rule References: RFC-078 (Postgres Knowledge MCP), Rule 050 (OPS Contract),
Rule 039 (Execution Contract)

Usage:
    python scripts/mcp/generate_proof_snapshot.py
    make mcp.proof.snapshot
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
    print(f"ERROR: Failed to import required modules: {e}", file=sys.stderr)
    sys.exit(1)

SCHEMA_PATH = ROOT / "schemas" / "mcp_proof_snapshot.v1.schema.json"
EVIDENCE_DIR = ROOT / "evidence"
SHARE_MCP_DIR = ROOT / "share" / "mcp"
SHARE_MCP_DIR.mkdir(parents=True, exist_ok=True)

PROOF_JSON = SHARE_MCP_DIR / "knowledge_mcp_proof.json"
PROOF_TXT = SHARE_MCP_DIR / "knowledge_mcp_proof.txt"

# Evidence file paths
E01_EVIDENCE = EVIDENCE_DIR / "guard_mcp_schema.json"
E02_EVIDENCE = EVIDENCE_DIR / "guard_mcp_db_ro.final.json"
E03_ENVELOPE = SHARE_MCP_DIR / "envelope.json"
E04_EVIDENCE = EVIDENCE_DIR / "guard_mcp_query.json"


def _load_json_file(path: Path) -> dict | None:
    """Load JSON file, return None if missing."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def _load_schema() -> dict:
    """Load JSON schema for validation."""
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")
    return json.loads(SCHEMA_PATH.read_text())


def _aggregate_components() -> tuple[dict, list[str]]:
    """Aggregate component statuses and collect artifact paths."""
    components = {}
    artifacts = []

    # E01: Schema guard
    e01_data = _load_json_file(E01_EVIDENCE)
    components["e01_schema"] = {
        "ok": e01_data.get("ok", False) if e01_data else False,
        "present": e01_data is not None,
        "details": e01_data.get("details", {}) if e01_data else {},
    }
    if E01_EVIDENCE.exists():
        artifacts.append(str(E01_EVIDENCE.relative_to(ROOT)))

    # E02: RO DSN guard
    e02_data = _load_json_file(E02_EVIDENCE)
    components["e02_ro_dsn"] = {
        "ok": e02_data.get("ok", False) if e02_data else False,
        "present": e02_data is not None,
        "details": e02_data.get("details", {}) if e02_data else {},
    }
    if E02_EVIDENCE.exists():
        artifacts.append(str(E02_EVIDENCE.relative_to(ROOT)))

    # E03: Ingest envelope (optional)
    e03_data = _load_json_file(E03_ENVELOPE)
    components["e03_ingest"] = {
        "ok": e03_data is not None,  # Present = ok for optional component
        "present": e03_data is not None,
        "details": {"envelope_schema": e03_data.get("schema")} if e03_data else {},
    }
    if E03_ENVELOPE.exists():
        artifacts.append(str(E03_ENVELOPE.relative_to(ROOT)))

    # E04: Query guard
    e04_data = _load_json_file(E04_EVIDENCE)
    components["e04_query"] = {
        "ok": e04_data.get("ok", False) if e04_data else False,
        "present": e04_data is not None,
        "details": e04_data.get("details", {}) if e04_data else {},
    }
    if E04_EVIDENCE.exists():
        artifacts.append(str(E04_EVIDENCE.relative_to(ROOT)))

    return components, artifacts


def _compute_overall_ok(components: dict) -> bool:
    """Compute overall_ok: all required components (E01, E02, E04) must be ok."""
    return (
        components["e01_schema"]["ok"]
        and components["e02_ro_dsn"]["ok"]
        and components["e04_query"]["ok"]
    )


def _generate_text_summary(snapshot: dict) -> str:
    """Generate human-readable text summary."""
    lines = []
    lines.append("Knowledge MCP Proof Snapshot")
    lines.append("=" * 50)
    lines.append(f"Generated: {snapshot['generated_at']}")
    lines.append(f"Overall Status: {'✓ OK' if snapshot['overall_ok'] else '✗ FAIL'}")
    lines.append("")
    lines.append("Components:")
    for comp_name, comp_data in snapshot["components"].items():
        status = "✓" if comp_data["ok"] else "✗"
        present = "present" if comp_data["present"] else "missing"
        lines.append(f"  {status} {comp_name}: {present}")
    lines.append("")
    lines.append(f"Artifacts ({len(snapshot['artifacts'])}):")
    for artifact in snapshot["artifacts"]:
        lines.append(f"  - {artifact}")
    return "\n".join(lines)


def main() -> int:
    """Main snapshot generation logic."""
    strict_mode = os.getenv("STRICT_MODE", "0") == "1"

    # Load schema
    try:
        schema = _load_schema()
    except FileNotFoundError as e:
        if strict_mode:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1
        else:
            print(f"HINT: Schema file not found: {e} (HINT mode)", file=sys.stderr)
            return 0

    # Aggregate components
    components, artifacts = _aggregate_components()
    overall_ok = _compute_overall_ok(components)

    # Build snapshot
    snapshot = {
        "schema": "mcp_proof_snapshot.v1",
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "components": components,
        "artifacts": artifacts,
        "overall_ok": overall_ok,
    }

    # Validate against schema
    try:
        validate(instance=snapshot, schema=schema)
    except ValidationError as e:
        if strict_mode:
            print(f"ERROR: Snapshot validation failed: {e.message}", file=sys.stderr)
            return 1
        else:
            print(f"HINT: Snapshot validation failed: {e.message} (HINT mode)", file=sys.stderr)
            # Continue in HINT mode

    # Write JSON
    PROOF_JSON.write_text(json.dumps(snapshot, indent=2))
    print(f"Generated: {PROOF_JSON.relative_to(ROOT)}")

    # Write text summary
    text_summary = _generate_text_summary(snapshot)
    PROOF_TXT.write_text(text_summary)
    print(f"Generated: {PROOF_TXT.relative_to(ROOT)}")

    if strict_mode and not overall_ok:
        print("ERROR: Overall status is not OK (STRICT mode)", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
