"""
Cleanup root directory - move old/temporary files to archive.

This script identifies and moves temporary/old files from the repository root
to archive/docs/root-cleanup/ preserving directory structure.

Files to archive:
- Evidence files (evidence*.json, evidence*.txt)
- Backup bundles (backup-*.bundle, backup-*.tar.gz)
- Guard outputs (guard_*.json)
- PR evidence (pr_*.json, evidence.pr*.json)
- Temporary exports (export.*.json, *.head.json)
- Temporary state files (.last_doctor.json, etc.)
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

ARCHIVE_BASE = REPO_ROOT / "archive" / "docs" / "root-cleanup"
RECEIPT_PATH = REPO_ROOT / "share" / "exports" / "docs-control" / "root-cleanup-receipt.json"


@dataclass
class CleanupMove:
    path: str
    target: str
    moved: bool
    error: str | None = None
    reason: str = ""


def should_archive(path: Path) -> tuple[bool, str]:
    """
    Determine if a file should be archived and why.

    Returns: (should_archive, reason)
    """
    name = path.name

    # Evidence files
    if name.startswith("evidence") and (name.endswith(".json") or name.endswith(".txt")):
        return True, "evidence file"

    # Backup bundles
    if name.startswith("backup-") and (name.endswith(".bundle") or name.endswith(".tar.gz")):
        return True, "backup bundle"

    # Guard outputs
    if name.startswith("guard_") and name.endswith(".json"):
        return True, "guard output"

    # PR evidence
    if (name.startswith("pr_") or name.startswith("evidence.pr")) and name.endswith(".json"):
        return True, "PR evidence"

    # Temporary exports
    if name.startswith("export.") and name.endswith(".json"):
        return True, "temporary export"

    # Head/tail snapshots
    if name.endswith(".head.json") or name.endswith(".tail.json"):
        return True, "snapshot file"

    # Temporary state files
    if name.startswith(".last_") or name == ".current_branch.txt":
        return True, "temporary state file"

    # Tree/snapshot files
    if name.endswith(".tree.txt") or name.endswith(".name.txt"):
        return True, "temporary tree/name file"

    return False, ""


def compute_target_path(source_path: Path) -> Path:
    """Compute target path under archive/docs/root-cleanup/"""
    rel = source_path.relative_to(REPO_ROOT)
    return ARCHIVE_BASE / rel


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


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Cleanup root directory - move old/temporary files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be moved without actually moving")
    parser.add_argument("--list-only", action="store_true", help="Just list files that would be archived")
    args = parser.parse_args()

    # Files that should NEVER be archived
    PROTECTED = {
        "AGENTS.md",
        "README.md",
        "README_FULL.md",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "MASTER_PLAN.md",
        "NEXT_STEPS.md",
        "PROGRESS_SUMMARY.md",
        "RULES_INDEX.md",
        "SHARE_MANIFEST.json",
        "package.json",
        "package-lock.json",
        "vercel.json",
        "bible_db_structure.sql",
        "activate_venv.sh",
        "conftest.py",
        "pyproject.toml",
        "pytest.ini",
        "ruff.toml",
        "mypy.ini",
        ".env",
        ".env.local",
        ".env.example",
        ".env.protected",
        ".cursorignore",
        ".cursorindexingignore",
        ".ci-trigger",
        "CODEOWNERS",
        "LICENSE",
        "DATA_FLOW_DIAGRAM.md",
        "GEMANTRIA_MASTER_REFERENCE_v2.md",
        "Prompting Guide for Our Core LLM models.md",
        "gemini.md",
        "walkthrough.md",
    }

    # ADR files should stay
    PROTECTED_PATTERNS = ["ADR-", ".git", ".venv", "node_modules"]

    # Scan root directory
    candidates: List[tuple[Path, str]] = []
    for item in REPO_ROOT.iterdir():
        if not item.is_file():
            continue

        # Skip protected files
        if item.name in PROTECTED:
            continue

        # Skip protected patterns
        if any(item.name.startswith(pattern) for pattern in PROTECTED_PATTERNS):
            continue

        # Check if should archive
        should, reason = should_archive(item)
        if should:
            candidates.append((item, reason))

    if not candidates:
        print("No files to archive in root directory.")
        sys.exit(0)

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Found {len(candidates)} files to archive:\n")

    if args.list_only:
        for path, reason in candidates:
            print(f"  {path.name} ({reason})")
        sys.exit(0)

    moves: List[CleanupMove] = []
    moved_paths: List[str] = []

    for source_path, reason in candidates:
        target_path = compute_target_path(source_path)
        target_rel = str(target_path.relative_to(REPO_ROOT))

        moved, error = move_file(source_path, target_path, args.dry_run)

        moves.append(
            CleanupMove(
                path=str(source_path.relative_to(REPO_ROOT)), target=target_rel, moved=moved, error=error, reason=reason
            )
        )

        if moved:
            moved_paths.append(str(source_path.relative_to(REPO_ROOT)))
            if not args.dry_run:
                print(f"✓ Moved: {source_path.name} -> {target_rel}")
            else:
                print(f"  Would move: {source_path.name} -> {target_rel}")
        else:
            print(f"✗ Failed: {source_path.name} ({error})", file=sys.stderr)

    # Write receipt
    receipt = {
        "dry_run": args.dry_run,
        "total_candidates": len(candidates),
        "successfully_moved": len(moved_paths),
        "failed": len(moves) - len(moved_paths),
        "moves": [asdict(m) for m in moves],
    }

    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RECEIPT_PATH.open("w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Receipt written to: {RECEIPT_PATH}")
    print("\nSummary:")
    print(f"  Total candidates: {len(candidates)}")
    print(f"  Successfully moved: {len(moved_paths)}")
    print(f"  Failed: {len(moves) - len(moved_paths)}")

    if args.dry_run:
        print("\n⚠  This was a dry run. Run without --dry-run to actually move files.")
    else:
        print("\n✅ Root cleanup complete!")


if __name__ == "__main__":
    main()
