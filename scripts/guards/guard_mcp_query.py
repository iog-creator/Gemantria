#!/usr/bin/env python3
"""
Guard: Knowledge MCP Query Roundtrip Validation (PLAN-073 M1 E04)

Validates that query_catalog.py executes successfully and produces deterministic output.
- HINT mode (default): Tolerates missing DB/view, emits hints, exits 0
- STRICT mode: Requires successful query with valid output, fails otherwise

Rule References: RFC-078 (Postgres Knowledge MCP), Rule 050 (OPS Contract),
Rule 039 (Execution Contract)

Usage:
    python scripts/guards/guard_mcp_query.py
    make guard.mcp.query
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

EVIDENCE_DIR = ROOT / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
EVIDENCE_FILE = EVIDENCE_DIR / "guard_mcp_query.json"

QUERY_SCRIPT = ROOT / "scripts" / "mcp" / "query_catalog.py"

# Expected keys in catalog items
EXPECTED_KEYS = {"name", "desc", "tags", "cost_est", "visibility", "path", "method", "auth"}


def _is_strict_mode() -> bool:
    """Determine if running in STRICT mode."""
    return os.getenv("STRICT_MODE", "0") == "1" or os.getenv("CI") == "true"


def _run_query_script() -> tuple[int, str, str]:
    """Run query_catalog.py and return (returncode, stdout, stderr)."""
    if not QUERY_SCRIPT.exists():
        return 1, "", f"Query script not found: {QUERY_SCRIPT}"

    result = subprocess.run(
        [sys.executable, str(QUERY_SCRIPT)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    return result.returncode, result.stdout, result.stderr


def _validate_output(output: str) -> tuple[bool, str | None]:
    """Validate query output is valid JSON with expected structure."""
    if not output.strip():
        return False, "Empty output"

    try:
        data = json.loads(output)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

    if not isinstance(data, list):
        return False, f"Expected array, got {type(data).__name__}"

    # Validate each item has expected keys
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            return False, f"Item {i} is not an object"
        item_keys = set(item.keys())
        missing_keys = EXPECTED_KEYS - item_keys
        if missing_keys:
            return False, f"Item {i} missing keys: {missing_keys}"

    return True, None


def main() -> int:
    """Main guard logic."""
    is_strict = _is_strict_mode()
    mode = "STRICT" if is_strict else "HINT"

    verdict = {
        "ok": True,
        "mode": mode,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "query_executed": False,
        "output_valid": False,
        "output_count": 0,
        "details": {},
    }

    # Run query script
    returncode, stdout, stderr = _run_query_script()

    if returncode != 0:
        verdict["ok"] = False
        verdict["details"]["error"] = f"Query script failed: {stderr}"
        if is_strict:
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            print(f"[guard_mcp_query] ERROR: Query script failed (STRICT mode): {stderr}", file=sys.stderr)
            return 1
        else:
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            print(f"[guard_mcp_query] HINT: Query script failed (HINT mode): {stderr}", file=sys.stderr)
            return 0

    verdict["query_executed"] = True

    # Validate output
    is_valid, error_msg = _validate_output(stdout)
    verdict["output_valid"] = is_valid

    if not is_valid:
        verdict["ok"] = False
        verdict["details"]["validation_error"] = error_msg
        if is_strict:
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            print(f"[guard_mcp_query] ERROR: Output validation failed (STRICT mode): {error_msg}", file=sys.stderr)
            return 1
        else:
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            print(f"[guard_mcp_query] HINT: Output validation failed (HINT mode): {error_msg}", file=sys.stderr)
            return 0

    # Count items
    try:
        data = json.loads(stdout)
        verdict["output_count"] = len(data)
    except json.JSONDecodeError:
        pass  # Already validated above

    print(json.dumps(verdict, indent=2))
    EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
