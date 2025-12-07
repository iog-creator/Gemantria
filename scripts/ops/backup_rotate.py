#!/usr/bin/env python3
"""
backup_rotate.py — Enforce Backup Retention Policy (Phase 24.D).

Policy:
1. Keep the N most recent backups (default 10).
2. Keep the latest backup for each of the last D days (default 7).
3. Delete backups that do not meet these criteria.

Usage:
    python3 scripts/ops/backup_rotate.py [--dry-run] [--recent 10] [--days 7]

Expected Backup Format:
    backup/{YYYYMMDD}_{HHMMSS}/ OR backup/{YYYYMMDD}T{HHMMSS}Z/
    Supports basic ISO-ish timestamp folders.
"""

import shutil
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Set

# Configure logging
logging.basicConfig(level=logging.INFO, format="[backup_rotate] %(message)s")
logger = logging.getLogger("backup_rotate")

ROOT = Path(__file__).resolve().parents[2]
BACKUP_ROOT = ROOT / "backup"


def parse_timestamp(dirname: str) -> datetime | None:
    """Attempt to parse valid timestamp from backup directory name."""
    # Common formats: 20251206_044916 or 20251206T044916Z
    try:
        if "T" in dirname and "Z" in dirname:
            return datetime.strptime(dirname, "%Y%m%dT%H%M%SZ")
        elif "_" in dirname:
            # Basic check to avoid crashing on random underscores
            parts = dirname.split("_")
            if len(parts) >= 2 and len(parts[0]) == 8 and len(parts[1]) >= 6:
                return datetime.strptime(f"{parts[0]}{parts[1][:6]}", "%Y%m%d%H%M%S")
    except ValueError:
        pass
    return None


def rotate_backups(dry_run: bool, keep_recent: int, keep_days: int) -> bool:
    if not BACKUP_ROOT.exists():
        logger.warning(f"Backup directory not found: {BACKUP_ROOT}")
        return True  # No backups implies nothing to rotate -> Success? Or should we safeguard?
        # If no backups, retention is vacuously satisfied.

    # 1. Discover Backups
    details = []
    for item in BACKUP_ROOT.iterdir():
        if item.is_dir():
            ts = parse_timestamp(item.name)
            if ts:
                details.append({"path": item, "ts": ts, "name": item.name})
            else:
                logger.debug(f"Skipping non-timestamped directory: {item.name}")

    # Sort descending (newest first)
    details.sort(key=lambda x: x["ts"], reverse=True)

    total_backups = len(details)
    logger.info(f"Found {total_backups} valid timestamped backups.")

    if total_backups == 0:
        return True

    # 2. Identify 'Keep' Set
    keep_set: Set[str] = set()

    # A. Recent count
    recent_list = details[:keep_recent]
    for b in recent_list:
        keep_set.add(b["name"])

    # B. Daily retention (last D days)
    # Map 'YYYY-MM-DD' -> List of backups, simplify to just picking the first (latest) for that day
    day_map: Dict[str, Dict] = {}

    # We iterate all backups to check daily coverage, not just recent ones?
    # Actually, iterate all backups, bucket by day.
    for b in details:
        day_key = b["ts"].strftime("%Y-%m-%d")
        if day_key not in day_map:
            day_map[day_key] = b
        else:
            # Since sorted desc, first one seen is latest. Already correct.
            pass

    # Select daily keepers for last 'keep_days' days?
    # Or just keep the latest backup of Any day found?
    # Policy: "latest backup per day for the last 7 days".
    # This implies backups older than 7 days that are NOT in 'recent' set are deleted?
    # Yes, typically.
    # But let's check if we want to keep older history. The spec says "Rotate... so backups don't fill the disk".
    # So deleting older than 7 days (outside of recent 10) is correct.

    # Just iterate the generated day_map keys. Sorted desc.
    sorted_days = sorted(day_map.keys(), reverse=True)
    # Take top D days
    days_to_keep = sorted_days[:keep_days]

    for day in days_to_keep:
        entry = day_map[day]
        keep_set.add(entry["name"])

    # 3. Calculate Deletion Set
    to_delete = []
    for b in details:
        if b["name"] not in keep_set:
            to_delete.append(b)

    logger.info(f"Retention Plan: Keep {len(keep_set)} | Delete {len(to_delete)}")

    # 4. Execute Rotation
    if not to_delete:
        logger.info("No backups to delete.")
        return True

    for item in to_delete:
        path = item["path"]
        name = item["name"]

        if dry_run:
            logger.info(f"[DRY-RUN] Would delete: {name}")
        else:
            try:
                logger.info(f"Deleting: {name}")
                shutil.rmtree(path)
            except Exception as e:
                logger.error(f"Failed to delete {name}: {e}")
                return False

    return True


def main():
    parser = argparse.ArgumentParser(description="Rotate backups based on retention policy.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate deletion.")
    parser.add_argument("--recent", type=int, default=10, help="Number of recent backups to keep.")
    parser.add_argument("--days", type=int, default=7, help="Number of days to keep daily backups.")
    args = parser.parse_args()

    success = rotate_backups(args.dry_run, args.recent, args.days)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
