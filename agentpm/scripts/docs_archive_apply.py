"""
DM-00X: Apply archive plan - move archive candidates to archive/docs/

This script:
- Reads all archive_candidate documents from control.kb_document
- Moves files to archive/docs/... preserving directory structure
- Updates DB status to 'archived'
- Writes a receipt of what was moved

Usage:
    python agentpm/scripts/docs_archive_apply.py [--dry-run]
"""

from __future__ import annotations

import json
import shutil
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import psycopg
from scripts.config.env import get_rw_dsn

RECEIPT_PATH = REPO_ROOT / "share" / "exports" / "docs-control" / "archive-receipt.json"
ARCHIVE_BASE = REPO_ROOT / "archive" / "docs"


@dataclass
class ArchiveMove:
    path: str
    target: str
    moved: bool
    error: str | None = None


def fetch_all_archive_candidates(conn: psycopg.Connection) -> List[str]:
    """Fetch all archive_candidate paths from the database."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT path
            FROM control.kb_document
            WHERE status = 'archive_candidate'
            ORDER BY path
            """
        )
        return [row[0] for row in cur.fetchall()]


def compute_target_path(source_path: str) -> Path:
    """
    Compute the target path under archive/docs/ preserving directory structure.

    Examples:
    - evidence/file.txt -> archive/docs/evidence/file.txt
    - archive/old/file.txt -> archive/docs/old/file.txt
    - docs/temp/file.txt -> archive/docs/docs/temp/file.txt
    """
    # If already in archive/, just change archive/ to archive/docs/
    if source_path.startswith("archive/"):
        rel = source_path[len("archive/") :]
        return ARCHIVE_BASE / rel

    # Otherwise, preserve full path under archive/docs/
    return ARCHIVE_BASE / source_path


def move_file(source: Path, target: Path, dry_run: bool) -> tuple[bool, str | None]:
    """Move a file to the archive location."""
    if not source.exists():
        return False, "Source file does not exist"

    if target.exists():
        return False, f"Target already exists: {target}"

    if dry_run:
        return True, None

    try:
        # Create parent directories
        target.parent.mkdir(parents=True, exist_ok=True)
        # Move the file
        shutil.move(str(source), str(target))
        return True, None
    except Exception as e:
        return False, str(e)


def update_db_status(conn: psycopg.Connection, paths: List[str], dry_run: bool) -> int:
    """Update DB status from archive_candidate to archived."""
    if dry_run:
        return len(paths)

    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE control.kb_document
            SET status = 'archived'
            WHERE path = ANY(%s) AND status = 'archive_candidate'
            """,
            (paths,),
        )
        return cur.rowcount


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Apply archive plan - move archive candidates")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be moved without actually moving"
    )
    args = parser.parse_args()

    dsn = get_rw_dsn()
    if not dsn:
        print("ERROR: GEMATRIA_DSN not set. Cannot connect to DB.", file=sys.stderr)
        sys.exit(1)

    try:
        with psycopg.connect(dsn) as conn:
            conn.autocommit = False

            # Fetch all archive candidates
            candidate_paths = fetch_all_archive_candidates(conn)

            if not candidate_paths:
                print("No archive candidates found in database.")
                sys.exit(0)

            print(
                f"\n{'[DRY RUN] ' if args.dry_run else ''}Processing {len(candidate_paths)} archive candidates...\n"
            )

            moves: List[ArchiveMove] = []
            moved_paths: List[str] = []

            for source_path in candidate_paths:
                source_file = REPO_ROOT / source_path
                target_file = compute_target_path(source_path)
                target_rel = str(target_file.relative_to(REPO_ROOT))

                moved, error = move_file(source_file, target_file, args.dry_run)

                moves.append(
                    ArchiveMove(path=source_path, target=target_rel, moved=moved, error=error)
                )

                if moved:
                    moved_paths.append(source_path)
                    if not args.dry_run:
                        print(f"✓ Moved: {source_path} -> {target_rel}")
                    else:
                        print(f"  Would move: {source_path} -> {target_rel}")
                else:
                    print(f"✗ Failed: {source_path} ({error})", file=sys.stderr)

            # Update DB status for successfully moved files
            if moved_paths and not args.dry_run:
                updated_count = update_db_status(conn, moved_paths, args.dry_run)
                conn.commit()
                print(f"\n✓ Updated {updated_count} database records to 'archived' status")

            # Write receipt
            receipt = {
                "dry_run": args.dry_run,
                "total_candidates": len(candidate_paths),
                "successfully_moved": len(moved_paths),
                "failed": len(moves) - len(moved_paths),
                "moves": [asdict(m) for m in moves],
                "generated_at": json.dumps({"$date": "now"}, default=str),
            }

            RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
            with RECEIPT_PATH.open("w", encoding="utf-8") as f:
                json.dump(receipt, f, indent=2, ensure_ascii=False)

            print(f"\n✓ Receipt written to: {RECEIPT_PATH}")
            print("\nSummary:")
            print(f"  Total candidates: {len(candidate_paths)}")
            print(f"  Successfully moved: {len(moved_paths)}")
            print(f"  Failed: {len(moves) - len(moved_paths)}")

            if args.dry_run:
                print("\n⚠  This was a dry run. Run without --dry-run to actually move files.")
            else:
                print("\n✅ Archive operation complete!")
                print("   Run 'pmagent docs dashboard-refresh' to update exports.")

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
