#!/usr/bin/env python3
"""
Guard: Required Hints Enforcement

Checks that envelopes contain all REQUIRED hints from the DMS hint_registry.
Empty REQUIRED set is OK (guard passes).
HINT mode: graceful degradation if DB unavailable.
STRICT mode: fail-closed if DB unavailable.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from agentpm.db.loader import DbUnavailableError, TableMissingError
from agentpm.hints.registry import load_hints_for_flow


def guard_hints_required(
    flow_name: str,
    envelope_path: Path | None = None,
    envelope_data: dict[str, Any] | None = None,
    mode: str = "HINT",
) -> dict[str, Any]:
    """
    Guard: Check that envelope contains all REQUIRED hints from DMS.

    Args:
        flow_name: Flow identifier (e.g., "handoff.generate", "capability_session", "reality_check")
        envelope_path: Path to envelope JSON file (if envelope_data not provided)
        envelope_data: Envelope dict (if envelope_path not provided)
        mode: "HINT" (graceful degradation) or "STRICT" (fail-closed)

    Returns:
        Dictionary with guard verdict:
        {
            "ok": bool,
            "flow": str,
            "required_hints_count": int,
            "found_hints_count": int,
            "missing": list[str] (logical names),
            "found": list[str] (logical names),
            "mode": str,
            "db_available": bool,
        }
    """
    # Load envelope
    if envelope_data is None:
        if envelope_path is None:
            return {
                "ok": False,
                "flow": flow_name,
                "error": "Either envelope_path or envelope_data must be provided",
            }
        if not envelope_path.exists():
            return {
                "ok": False,
                "flow": flow_name,
                "error": f"Envelope file not found: {envelope_path}",
            }
        try:
            envelope_data = json.loads(envelope_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return {
                "ok": False,
                "flow": flow_name,
                "error": f"Failed to load envelope: {exc}",
            }

    # Determine scope from flow_name
    scope_map = {
        "handoff.generate": "handoff",
        "capability_session": "agentpm",
        "reality_check": "status_api",
        "status_snapshot": "status_api",
    }
    scope = scope_map.get(flow_name, "handoff")  # default

    # Load REQUIRED hints from DMS
    try:
        hints = load_hints_for_flow(
            scope=scope,
            applies_to={"flow": flow_name},
            mode=mode,
        )
        required_hints = hints.get("required", [])
        db_available = True
    except (DbUnavailableError, TableMissingError) as exc:
        if mode == "STRICT":
            return {
                "ok": False,
                "flow": flow_name,
                "error": f"DMS unavailable in STRICT mode: {exc}",
                "mode": mode,
                "db_available": False,
            }
        # HINT mode: graceful degradation - empty REQUIRED set is OK
        return {
            "ok": True,
            "flow": flow_name,
            "required_hints_count": 0,
            "found_hints_count": 0,
            "missing": [],
            "found": [],
            "mode": mode,
            "db_available": False,
            "note": f"DMS unavailable (graceful degradation): {exc}",
        }
    except Exception as exc:
        if mode == "STRICT":
            return {
                "ok": False,
                "flow": flow_name,
                "error": f"Failed to load hints from DMS: {exc}",
                "mode": mode,
                "db_available": False,
            }
        # HINT mode: graceful degradation
        return {
            "ok": True,
            "flow": flow_name,
            "required_hints_count": 0,
            "found_hints_count": 0,
            "missing": [],
            "found": [],
            "mode": mode,
            "db_available": False,
            "note": f"Failed to load hints (graceful degradation): {exc}",
        }

    # Empty REQUIRED set is OK
    if not required_hints:
        return {
            "ok": True,
            "flow": flow_name,
            "required_hints_count": 0,
            "found_hints_count": 0,
            "missing": [],
            "found": [],
            "mode": mode,
            "db_available": True,
            "note": "No REQUIRED hints configured for this flow",
        }

    # Extract logical names of required hints
    required_logical_names = {
        hint.get("logical_name") for hint in required_hints if hint.get("logical_name")
    }

    # Check envelope for required_hints array
    envelope_required_hints = envelope_data.get("required_hints", [])
    found_logical_names = {
        hint.get("logical_name") for hint in envelope_required_hints if hint.get("logical_name")
    }

    # Find missing hints
    missing = list(required_logical_names - found_logical_names)
    found = list(required_logical_names & found_logical_names)

    # Guard passes if all required hints are found
    ok = len(missing) == 0

    return {
        "ok": ok,
        "flow": flow_name,
        "required_hints_count": len(required_logical_names),
        "found_hints_count": len(found),
        "missing": missing,
        "found": found,
        "mode": mode,
        "db_available": True,
    }


def main() -> int:
    """CLI entrypoint for guard."""
    import argparse

    parser = argparse.ArgumentParser(description="Guard: Required Hints Enforcement")
    parser.add_argument("--flow", required=True, help="Flow name (e.g., handoff.generate)")
    parser.add_argument("--envelope", type=Path, help="Path to envelope JSON file")
    parser.add_argument("--mode", default="HINT", choices=["HINT", "STRICT"], help="Guard mode")
    parser.add_argument("--json-only", action="store_true", help="Output JSON only")

    args = parser.parse_args()

    verdict = guard_hints_required(
        flow_name=args.flow,
        envelope_path=args.envelope,
        mode=args.mode,
    )

    if args.json_only:
        print(json.dumps(verdict, indent=2))
    else:
        if verdict.get("ok"):
            print(f"✅ Guard passed: {args.flow}")
            if verdict.get("required_hints_count", 0) > 0:
                print(
                    f"   Found {verdict['found_hints_count']}/{verdict['required_hints_count']} required hints"
                )
        else:
            print(f"❌ Guard failed: {args.flow}")
            if verdict.get("missing"):
                print(f"   Missing hints: {', '.join(verdict['missing'])}")
            if verdict.get("error"):
                print(f"   Error: {verdict['error']}")

    return 0 if verdict.get("ok", False) else 1


if __name__ == "__main__":
    sys.exit(main())
