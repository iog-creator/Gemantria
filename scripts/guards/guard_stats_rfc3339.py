#!/usr/bin/env python3
"""
Guard: Enforce RFC3339/ISO-8601 generated_at in graph_stats.json.
Validates that generated_at is a string matching RFC3339 format (not epoch float).
"""

import json
import re
import sys
from pathlib import Path

# RFC3339 pattern: YYYY-MM-DDTHH:MM:SS[.fraction]Z or [+-]HH:MM
RFC3339_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$"
)

STATS_PATH = Path("exports/graph_stats.json")


def validate_rfc3339(timestamp: str) -> bool:
    """Check if timestamp matches RFC3339 format."""
    return bool(RFC3339_PATTERN.match(timestamp))


def main():
    if not STATS_PATH.exists():
        print("SKIP: graph_stats.json not found (tolerated).")
        sys.exit(0)

    try:
        with open(STATS_PATH, encoding="utf-8") as f:
            stats = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to read graph_stats.json: {e}", file=sys.stderr)
        sys.exit(2)

    generated_at = stats.get("generated_at")
    if generated_at is None:
        print("SKIP: generated_at missing (tolerated).")
        sys.exit(0)

    if isinstance(generated_at, (int, float)):
        print(
            f"ERROR: generated_at is numeric ({generated_at}), expected RFC3339 string",
            file=sys.stderr,
        )
        sys.exit(2)

    if not isinstance(generated_at, str):
        print(
            f"ERROR: generated_at is {type(generated_at).__name__}, expected string",
            file=sys.stderr,
        )
        sys.exit(2)

    if not validate_rfc3339(generated_at):
        print(
            f"ERROR: generated_at '{generated_at}' does not match RFC3339 format",
            file=sys.stderr,
        )
        sys.exit(2)

    print(f"OK: generated_at is RFC3339: {generated_at}")


if __name__ == "__main__":
    main()

