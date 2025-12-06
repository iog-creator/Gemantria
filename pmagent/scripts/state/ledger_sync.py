#!/usr/bin/env python3
"""
Ledger Sync - System State Ledger Synchronization

Reads AGENTS.md, SSOT docs, share exports and writes hash rows into
control.system_state_ledger.

Non-destructive v1: only INSERT rows with name + hash.

Rule References: Rule 006 (AGENTS.md Governance), Rule 027 (Docs Sync Gate),
Rule 030 (Share Sync), Rule 069 (Reality Green)

Usage:
    python -m pmagent.scripts.state.ledger_sync
    pmagent state sync
    make state.sync
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.config.env import get_rw_dsn  # noqa: E402
import psycopg  # noqa: E402


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of file content."""
    content = file_path.read_bytes()
    return hashlib.sha256(content).hexdigest()


def sync_ledger() -> int:
    """Sync system state ledger with current artifact hashes."""
    repo_root = ROOT

    # Define artifacts to track
    artifacts = [
        # Root AGENTS.md
        (repo_root / "AGENTS.md", "AGENTS.md", "root"),
        # SSOT docs
        (repo_root / "docs/SSOT/MASTER_PLAN.md", "MASTER_PLAN.md", "docs/SSOT"),
        (repo_root / "docs/runbooks/DB_HEALTH.md", "DB_HEALTH.md", "docs/runbooks"),
        (
            repo_root / "docs/runbooks/PM_SNAPSHOT_CURRENT.md",
            "PM_SNAPSHOT_CURRENT.md",
            "docs/runbooks",
        ),
        (repo_root / "RULES_INDEX.md", "RULES_INDEX.md", "root"),
        # Share exports (control-plane)
        (
            repo_root / "share/atlas/control_plane/system_health.json",
            "system_health.json",
            "share/atlas/control_plane",
        ),
        (
            repo_root / "share/atlas/control_plane/lm_indicator.json",
            "lm_indicator.json",
            "share/atlas/control_plane",
        ),
        # Share exports (docs-control)
        (
            repo_root / "share/exports/docs-control/canonical.json",
            "canonical.json",
            "share/exports/docs-control",
        ),
        (
            repo_root / "share/exports/docs-control/summary.json",
            "summary.json",
            "share/exports/docs-control",
        ),
    ]

    # Get DSN
    try:
        dsn = get_rw_dsn()
    except Exception as e:
        print(f"ERROR: Failed to get DSN: {e}", file=sys.stderr)
        return 1

    if not dsn:
        print("SKIP: GEMATRIA_DSN not set", file=sys.stderr)
        return 0

    # Connect to database
    try:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                inserted = 0
                skipped = 0

                for file_path, name, source_of_truth in artifacts:
                    if not file_path.exists():
                        print(f"SKIP: {name} not found at {file_path}", file=sys.stderr)
                        skipped += 1
                        continue

                    try:
                        file_hash = compute_file_hash(file_path)
                        status = "current"

                        # Insert ledger entry (non-destructive: always insert new row)
                        cur.execute(
                            """
                            INSERT INTO control.system_state_ledger
                                (name, source_of_truth, hash, status, generated_at)
                            VALUES (%s, %s, %s, %s, now())
                            """,
                            (name, source_of_truth, file_hash, status),
                        )

                        print(f"✓ Synced: {name} ({source_of_truth}) -> {file_hash[:16]}...")
                        inserted += 1

                    except Exception as e:
                        print(f"ERROR: Failed to sync {name}: {e}", file=sys.stderr)
                        return 1

                conn.commit()
                print(f"\n✓ Ledger sync complete: {inserted} inserted, {skipped} skipped")
                return 0

    except Exception as e:
        print(f"ERROR: Database connection failed: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """CLI entrypoint."""
    return sync_ledger()


if __name__ == "__main__":
    sys.exit(main())
