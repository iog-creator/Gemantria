#!/usr/bin/env python3
"""
Guard: Verify a recent backup exists before destructive operations.

Usage:
    python scripts/guards/guard_backup_recent.py [--mode HINT|STRICT] [--max-age-minutes N]

Governance Rule (Phase 23.4):
    No destructive share/ or housekeeping operation may execute unless
    `make backup.surfaces` has succeeded within the past 5 minutes.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, UTC
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKUP_DIR = REPO_ROOT / "backup"
DEFAULT_MAX_AGE_MINUTES = 5


def find_recent_backup(max_age_minutes: int) -> tuple[Path | None, dict | None]:
    """Find the most recent backup within the allowed time window."""
    if not BACKUP_DIR.exists():
        return None, None

    now = datetime.now(UTC)
    cutoff = now - timedelta(minutes=max_age_minutes)

    # Find all backup directories with MANIFEST.json
    backups = []
    for entry in BACKUP_DIR.iterdir():
        if entry.is_dir():
            manifest = entry / "MANIFEST.json"
            if manifest.exists():
                try:
                    data = json.loads(manifest.read_text(encoding="utf-8"))
                    created_at = data.get("created_at", "")
                    # Parse ISO timestamp
                    if created_at:
                        ts = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        if ts >= cutoff:
                            backups.append((entry, data, ts))
                except (json.JSONDecodeError, ValueError):
                    pass

    if not backups:
        return None, None

    # Return most recent
    backups.sort(key=lambda x: x[2], reverse=True)
    return backups[0][0], backups[0][1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=["HINT", "STRICT"],
        default="HINT",
        help="HINT=warn only, STRICT=block if no recent backup",
    )
    parser.add_argument(
        "--max-age-minutes",
        type=int,
        default=DEFAULT_MAX_AGE_MINUTES,
        help=f"Maximum age of backup in minutes (default: {DEFAULT_MAX_AGE_MINUTES})",
    )
    args = parser.parse_args()

    backup_path, manifest = find_recent_backup(args.max_age_minutes)

    if backup_path and manifest:
        created = manifest.get("created_at", "unknown")
        branch = manifest.get("branch", "unknown")
        print(f"✅ Recent backup found: {backup_path.name}")
        print(f"   Created: {created}, Branch: {branch}")
        return 0

    # No recent backup found
    msg = (
        f"❌ No backup found within the last {args.max_age_minutes} minutes.\n"
        f"   Run: make backup.surfaces\n"
        f"   Before running destructive operations."
    )

    if args.mode == "STRICT":
        print(msg)
        print("\n🛑 STRICT MODE: Blocking execution.")
        return 1
    else:
        print(msg)
        print("\n⚠️ HINT MODE: Proceeding with warning.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
