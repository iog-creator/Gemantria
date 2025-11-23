#!/usr/bin/env python3
"""
Echo redacted RO DSN (PLAN-073 M1 E02)

Prints a single redacted DSN line showing which DSN source was used.
Uses centralized DSN loader (get_ro_dsn()) for consistency.

Rule References: RFC-078 (Postgres Knowledge MCP), Rule 050 (OPS Contract)

Usage:
    python scripts/mcp/echo_dsn_ro.py
    make mcp.dsn.echo
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

try:
    from scripts.config.env import get_ro_dsn, redact, env
except ImportError:
    print("ERROR: Failed to import scripts.config.env", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    """Echo redacted RO DSN with source information."""
    dsn = get_ro_dsn()

    if not dsn:
        print("HINT: No RO DSN available (check GEMATRIA_RO_DSN, ATLAS_DSN_RO, ATLAS_DSN)", file=sys.stderr)
        return 0

    # Determine which source was used
    source = "unknown"
    if env("GEMATRIA_RO_DSN"):
        source = "GEMATRIA_RO_DSN"
    elif env("ATLAS_DSN_RO"):
        source = "ATLAS_DSN_RO"
    elif env("ATLAS_DSN"):
        source = "ATLAS_DSN"
    elif env("GEMATRIA_DSN"):
        source = "GEMATRIA_DSN (fallback to RW)"

    # Redact the DSN
    redacted = redact(dsn)
    if redacted:
        print(f"{redacted} (source: {source})")
    else:
        print(f"{dsn} (source: {source})", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
