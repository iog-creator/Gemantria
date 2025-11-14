#!/usr/bin/env python3
"""
Print a human-readable summary of LM health JSON output.

Reads JSON from stdin (from guard.lm.health) and prints a single summary line.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def print_summary(health_json: dict) -> str:
    """
    Generate a human-readable summary line from LM health JSON.

    Args:
        health_json: Dictionary from guard_lm_health.check_lm_health()

    Returns:
        Summary string like "LM_HEALTH: mode=lm_ready (ok)"
    """
    mode = health_json.get("mode", "unknown")
    ok = health_json.get("ok", False)
    errors = health_json.get("details", {}).get("errors", [])

    # Build reason string
    if ok and mode == "lm_ready":
        reason = "ok"
    elif mode == "lm_off":
        if errors:
            # Extract first error type (before colon)
            first_error = errors[0].split(":")[0] if ":" in errors[0] else errors[0]
            if "connection_refused" in first_error:
                reason = "endpoint not reachable"
            elif "timeout" in first_error:
                reason = "timeout"
            elif "invalid_response" in first_error:
                reason = "invalid response"
            else:
                # Use first error as reason (truncate if too long)
                reason = first_error.replace("_", " ")[:50]
        else:
            reason = "endpoint not reachable"
    else:
        if errors:
            # Use first error as reason (truncate if too long)
            reason = errors[0].split(":")[-1].strip()[:50]
        else:
            reason = "unknown status"

    return f"LM_HEALTH: mode={mode} ({reason})"


def main() -> int:
    """Read JSON from stdin and print summary."""
    try:
        data = json.load(sys.stdin)
        summary = print_summary(data)
        print(summary)
        return 0
    except json.JSONDecodeError as e:
        print(f"LM_HEALTH: mode=error (invalid JSON: {e})", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"LM_HEALTH: mode=error ({e})", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
