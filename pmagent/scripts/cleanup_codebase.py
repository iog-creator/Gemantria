"""
Comprehensive codebase cleanup - identify and archive old/outdated files.

This script:
- Finds deprecated scripts and files
- Checks files against SSOT/AGENTS.md references
- Identifies temporary/old files
- Archives them to archive/docs/codebase-cleanup/

Usage:
    python pmagent/scripts/cleanup_codebase.py [--dry-run] [--check-references]
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

ARCHIVE_BASE = REPO_ROOT / "archive" / "docs" / "codebase-cleanup"
RECEIPT_PATH = REPO_ROOT / "share" / "exports" / "docs-control" / "codebase-cleanup-receipt.json"

# Directories to skip
SKIP_DIRS = {
    ".venv",
    "node_modules",
    ".git",
    "archive",
    "share",
    "evidence",
    "build",
    "dist",
    "__pycache__",
    ".pytest_cache",
    "gemantria.egg-info",
}


@dataclass
class CleanupCandidate:
    path: str
    reason: str
    referenced: bool = False
    reference_count: int = 0


def should_skip(path: Path) -> bool:
    """Check if path should be skipped."""
    parts = path.parts
    return any(skip in parts for skip in SKIP_DIRS)


def is_deprecated_script(path: Path) -> bool:
    """Check if a script is marked as deprecated (exits with DEPRECATED message)."""
    if not path.is_file() or not path.suffix == ".py":
        return False

    # Skip the cleanup script itself
    if "cleanup_codebase.py" in str(path):
        return False

    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        # Look for scripts that exit with DEPRECATED message (not just mention it)
        # Pattern: sys.stderr.write("DEPRECATED: ...") or sys.exit with DEPRECATED
        if re.search(r"sys\.(stderr\.write|exit).*DEPRECATED", content, re.IGNORECASE):
            return True
        # Also check for "DEPRECATED:" at start of stderr.write
        if re.search(r"DEPRECATED:\s*This\s+script", content, re.IGNORECASE):
            return True
    except Exception:
        return False

    return False


def is_temporary_file(path: Path) -> bool:
    """Check if file looks temporary."""
    name = path.name.lower()

    # Exclude important configuration files
    config_files = {
        "package.json",
        "package-lock.json",
        "ruff.toml",
        "mypy.ini",
        "pyproject.toml",
        "conftest.py",
        ".env",
        ".env.local",
        ".env.example",
    }
    if name in config_files:
        return False

    patterns = [
        "tmp_",
        "temp_",
        "old_",
        "backup_",
        ".old",
        ".bak",
        ".backup",
        "_old",
        "_backup",
        "_deprecated",
        ".tmp",
    ]
    return any(name.startswith(p) or name.endswith(p) for p in patterns)


def check_references(path: Path, repo_root: Path) -> tuple[bool, int]:
    """
    Check if file is referenced in AGENTS.md or SSOT docs.
    Returns (is_referenced, count).
    """
    if should_skip(path):
        return False, 0

    rel_path = str(path.relative_to(repo_root))
    name = path.name

    count = 0

    # Check AGENTS.md
    agents_md = repo_root / "AGENTS.md"
    if agents_md.exists():
        try:
            content = agents_md.read_text(encoding="utf-8", errors="ignore")
            if rel_path in content or name in content:
                count += content.count(rel_path) + content.count(name)
        except Exception:
            pass

    # Check SSOT directory
    ssot_dir = repo_root / "docs" / "SSOT"
    if ssot_dir.exists():
        for ssot_file in ssot_dir.rglob("*.md"):
            try:
                content = ssot_file.read_text(encoding="utf-8", errors="ignore")
                if rel_path in content or name in content:
                    count += content.count(rel_path) + content.count(name)
            except Exception:
                pass

    # Check .cursor/rules
    rules_dir = repo_root / ".cursor" / "rules"
    if rules_dir.exists():
        for rule_file in rules_dir.glob("*.mdc"):
            try:
                content = rule_file.read_text(encoding="utf-8", errors="ignore")
                if rel_path in content or name in content:
                    count += content.count(rel_path) + content.count(name)
            except Exception:
                pass

    return count > 0, count


def find_deprecated_scripts(repo_root: Path) -> List[CleanupCandidate]:
    """Find all deprecated scripts."""
    candidates = []

    for py_file in repo_root.rglob("*.py"):
        if should_skip(py_file):
            continue

        if is_deprecated_script(py_file):
            rel_path = str(py_file.relative_to(repo_root))
            candidates.append(CleanupCandidate(path=rel_path, reason="deprecated script (contains DEPRECATED marker)"))

    return candidates


def find_temporary_files(repo_root: Path) -> List[CleanupCandidate]:
    """Find temporary files."""
    candidates = []

    for file_path in repo_root.rglob("*"):
        if should_skip(file_path) or not file_path.is_file():
            continue

        if is_temporary_file(file_path):
            rel_path = str(file_path.relative_to(repo_root))
            candidates.append(
                CleanupCandidate(path=rel_path, reason="temporary file (tmp_/temp_/old_/backup_ pattern)")
            )

    return candidates


def find_orphan_candidates(repo_root: Path) -> List[CleanupCandidate]:
    """Find files listed in ORPHANS_CANDIDATE_REPORT.md (excluding config files)."""
    candidates = []
    orphan_report = repo_root / "docs" / "analysis" / "ORPHANS_CANDIDATE_REPORT.md"

    if not orphan_report.exists():
        return candidates

    # Files to exclude from orphan report (they're config files, not orphans)
    exclude_from_orphans = {
        "package.json",
        "package-lock.json",
        "ruff.toml",
        "mypy.ini",
        "conftest.py",
        "activate_venv.sh",
        "bible_db_structure.sql",
        "forest_overview.md",  # Referenced in SHARE_MANIFEST
    }

    try:
        content = orphan_report.read_text(encoding="utf-8", errors="ignore")
        # Extract file paths from the report
        # Pattern: `- `filename` (file)` or `- filename (file)`
        pattern = r"-\s+`?([^`\s]+)`?\s+\(file\)"
        matches = re.findall(pattern, content)

        for match in matches:
            # Skip excluded files
            if match in exclude_from_orphans:
                continue

            file_path = repo_root / match
            if file_path.exists() and file_path.is_file():
                rel_path = str(file_path.relative_to(repo_root))
                candidates.append(CleanupCandidate(path=rel_path, reason="listed in ORPHANS_CANDIDATE_REPORT.md"))
    except Exception as e:
        print(f"Warning: Could not parse orphan report: {e}", file=sys.stderr)

    return candidates


def compute_target_path(source_path: str, repo_root: Path) -> Path:
    """Compute target path under archive preserving directory structure."""
    # Preserve directory structure
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


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Comprehensive codebase cleanup")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be moved without actually moving")
    parser.add_argument(
        "--check-references",
        action="store_true",
        help="Check files against SSOT/AGENTS.md before archiving",
    )
    parser.add_argument("--list-only", action="store_true", help="Just list candidates without moving")
    args = parser.parse_args()

    print("\n🔍 Scanning codebase for cleanup candidates...\n")

    # Find all candidates
    all_candidates: List[CleanupCandidate] = []

    print("1. Finding deprecated scripts...")
    deprecated = find_deprecated_scripts(REPO_ROOT)
    all_candidates.extend(deprecated)
    print(f"   Found {len(deprecated)} deprecated scripts")

    print("2. Finding temporary files...")
    temp_files = find_temporary_files(REPO_ROOT)
    all_candidates.extend(temp_files)
    print(f"   Found {len(temp_files)} temporary files")

    print("3. Finding orphan candidates...")
    orphans = find_orphan_candidates(REPO_ROOT)
    all_candidates.extend(orphans)
    print(f"   Found {len(orphans)} orphan candidates")

    # Deduplicate
    seen = set()
    unique_candidates = []
    for candidate in all_candidates:
        if candidate.path not in seen:
            seen.add(candidate.path)
            unique_candidates.append(candidate)

    print(f"\n📊 Total unique candidates: {len(unique_candidates)}\n")

    if args.check_references:
        print("4. Checking references in SSOT/AGENTS.md...")
        for candidate in unique_candidates:
            file_path = REPO_ROOT / candidate.path
            if file_path.exists():
                referenced, count = check_references(file_path, REPO_ROOT)
                candidate.referenced = referenced
                candidate.reference_count = count
        print("   Reference check complete\n")

    if args.list_only:
        print("Candidates to archive:\n")
        for candidate in unique_candidates:
            ref_status = f" (referenced {candidate.reference_count}x)" if candidate.referenced else " (not referenced)"
            print(f"  {candidate.path}")
            print(f"    Reason: {candidate.reason}{ref_status}\n")
        return

    # Filter out referenced files if checking references
    if args.check_references:
        to_archive = [c for c in unique_candidates if not c.referenced]
        skipped = [c for c in unique_candidates if c.referenced]
        print(f"⚠  Skipping {len(skipped)} referenced files")
        print(f"📦 Will archive {len(to_archive)} files\n")
    else:
        to_archive = unique_candidates

    if not to_archive:
        print("No files to archive.")
        return

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Processing {len(to_archive)} files...\n")

    moves = []
    moved_paths = []

    for candidate in to_archive:
        source_file = REPO_ROOT / candidate.path
        target_file = compute_target_path(candidate.path, REPO_ROOT)
        target_rel = str(target_file.relative_to(REPO_ROOT))

        moved, error = move_file(source_file, target_file, args.dry_run)

        moves.append(
            {
                "path": candidate.path,
                "target": target_rel,
                "moved": moved,
                "error": error,
                "reason": candidate.reason,
            }
        )

        if moved:
            moved_paths.append(candidate.path)
            if not args.dry_run:
                print(f"✓ Moved: {candidate.path}")
            else:
                print(f"  Would move: {candidate.path}")
        else:
            print(f"✗ Failed: {candidate.path} ({error})", file=sys.stderr)

    # Write receipt
    receipt = {
        "dry_run": args.dry_run,
        "total_candidates": len(unique_candidates),
        "archived": len(moved_paths),
        "failed": len(moves) - len(moved_paths),
        "skipped_referenced": len(skipped) if args.check_references else 0,
        "moves": moves,
    }

    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RECEIPT_PATH.open("w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Receipt written to: {RECEIPT_PATH}")
    print("\nSummary:")
    print(f"  Total candidates: {len(unique_candidates)}")
    print(f"  Archived: {len(moved_paths)}")
    print(f"  Failed: {len(moves) - len(moved_paths)}")
    if args.check_references:
        print(f"  Skipped (referenced): {len(skipped)}")

    if args.dry_run:
        print("\n⚠  This was a dry run. Run without --dry-run to actually move files.")
    else:
        print("\n✅ Codebase cleanup complete!")


if __name__ == "__main__":
    main()
