#!/usr/bin/env python3
"""
Guard: Repository Root Surface Policy (Phase 27.G)

Validates that no unexpected files appear in the repository root.
Only files listed in docs/SSOT/ROOT_SURFACE_ALLOWLIST.txt are permitted.

- HINT mode (default): Emits warnings but exits 0
- STRICT mode: Fails on any unexpected files

Rule References: Phase 27.G, Rule 050 (OPS Contract), Rule 039 (Execution Contract)

Usage:
    python scripts/guards/guard_root_surface_policy.py [--mode HINT|STRICT]
    make guard.root.surface
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

ALLOWLIST_PATH = ROOT / "docs" / "SSOT" / "ROOT_SURFACE_ALLOWLIST.txt"


def load_allowlist() -> set[str]:
    """Load the canonical root surface allowlist."""
    if not ALLOWLIST_PATH.exists():
        print(
            f"[root-surface] ERROR: allowlist missing: {ALLOWLIST_PATH}",
            file=sys.stderr,
        )
        return set()

    allowlist = set()
    for line in ALLOWLIST_PATH.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            allowlist.add(line)

    return allowlist


def main() -> int:
    """Main guard logic."""
    parser = argparse.ArgumentParser(
        description="Guard: Repository Root Surface Policy"
    )
    parser.add_argument(
        "--mode",
        choices=["HINT", "STRICT"],
        default=os.getenv("STRICT_MODE", "0") == "1" and "STRICT" or "HINT",
        help="Guard mode: HINT (warn only) or STRICT (fail on violations)",
    )
    args = parser.parse_args()

    mode = args.mode
    is_strict = mode == "STRICT"

    # Load allowlist
    allowlist = load_allowlist()
    if not allowlist:
        if is_strict:
            print(
                "[root-surface] ERROR: Cannot validate without allowlist (STRICT mode)",
                file=sys.stderr,
            )
            return 1
        else:
            print(
                "[root-surface] HINT: Allowlist missing, skipping validation (HINT mode)",
                file=sys.stderr,
            )
            return 0

    # Get current root files (files only, not directories)
    current_files = {p.name for p in ROOT.iterdir() if p.is_file()}

    # Find unexpected files
    extra = sorted(f for f in current_files if f not in allowlist)

    if not extra:
        print("[root-surface] OK: no unexpected files in repo root")
        return 0

    # Report violations
    print(f"[root-surface] Unexpected files in repo root ({len(extra)}):", file=sys.stderr)
    for f in extra:
        print(f"  - {f}", file=sys.stderr)

    if is_strict:
        print(
            "[root-surface] ERROR: Root surface policy violation (STRICT mode)",
            file=sys.stderr,
        )
        print(
            f"[root-surface] Move these files to appropriate locations or add to {ALLOWLIST_PATH}",
            file=sys.stderr,
        )
        return 1
    else:
        print(
            "[root-surface] HINT: Root surface policy violation (HINT mode)",
            file=sys.stderr,
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
