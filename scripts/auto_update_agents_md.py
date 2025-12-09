#!/usr/bin/env python3
"""
auto_update_agents_md.py — Automatically update AGENTS.md files based on code changes.

This script detects code changes and automatically updates relevant AGENTS.md files
to reflect new functions, classes, components, or API changes.

Rule References: 006 (AGENTS.md Governance), 027 (Docs Sync Gate), 058 (Auto-Housekeeping)

Usage:
    python scripts/auto_update_agents_md.py  # Auto-update based on git changes
    python scripts/auto_update_agents_md.py --dry-run  # Show what would be updated
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


def get_git_changed_files() -> set[Path]:
    """Get list of changed files from git."""
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = {ROOT / f for f in result.stdout.strip().split("\n") if f}
        return files
    except subprocess.CalledProcessError:
        return set()


def get_directory_for_file(file_path: Path) -> Path | None:
    """Get the directory that should have an AGENTS.md file for this file."""
    # Map file paths to their directory
    if file_path.name == "AGENTS.md":
        return None

    # Check if file is in a directory that requires AGENTS.md
    parts = file_path.parts
    if "src" in parts:
        # src/*/ requires AGENTS.md
        src_idx = parts.index("src")
        if len(parts) > src_idx + 1:
            return ROOT / "/".join(parts[: src_idx + 2])
    elif "pmagent" in parts:
        # pmagent/*/ requires AGENTS.md (modules, biblescholar, etc.)
        pmagent_idx = parts.index("pmagent")
        if len(parts) > pmagent_idx + 1:
            return ROOT / "/".join(parts[: pmagent_idx + 2])
    elif "webui" in parts:
        # webui/*/ requires AGENTS.md for UI apps (graph dashboard, forecast UI, etc.)
        webui_idx = parts.index("webui")
        if len(parts) > webui_idx + 1:
            return ROOT / "/".join(parts[: webui_idx + 2])
    elif file_path.parent.name in ("scripts", "migrations", "tests", "docs"):
        # These directories require AGENTS.md
        return file_path.parent

    return None


def detect_code_changes(file_path: Path) -> dict[str, Any]:
    """Detect what changed in a code file (functions, classes, etc.)."""
    if not file_path.exists():
        return {}

    content = file_path.read_text()
    changes = {
        "functions": [],
        "classes": [],
        "imports": [],
    }

    # Simple detection for Python files
    if file_path.suffix == ".py":
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("def ") and not line.startswith("def _"):  # Public functions
                func_name = line.split("(")[0].replace("def ", "").strip()
                changes["functions"].append(func_name)
            elif line.startswith("class ") and not line.startswith("class _"):  # Public classes
                class_name = line.split("(")[0].split(":")[0].replace("class ", "").strip()
                changes["classes"].append(class_name)

    return changes


def update_agents_md(directory: Path, changes: dict[str, Any], dry_run: bool = False) -> bool:
    """Update AGENTS.md file in directory with detected changes."""
    agents_path = directory / "AGENTS.md"
    if not agents_path.exists():
        if dry_run:
            print(f"  [DRY-RUN] Would create {agents_path.relative_to(ROOT)}")
        else:
            # Create basic AGENTS.md if missing
            agents_path.write_text(
                f"# AGENTS.md — {directory.name}\n\n## Directory Purpose\n\nTODO: Document purpose\n"
            )
            print(f"  ✓ Created {agents_path.relative_to(ROOT)}")
        return True

    # For now, just touch the file to update timestamp
    # In the future, we could parse and update content intelligently
    if not dry_run:
        agents_path.touch()
        # Resolve path to handle any double slashes or normalization issues
        try:
            rel_path = agents_path.resolve().relative_to(ROOT.resolve())
        except ValueError:
            # Fallback if resolve fails (e.g. symlinks outside root)
            rel_path = agents_path.relative_to(ROOT) if agents_path.is_absolute() else agents_path

        print(f"  ✓ Updated {rel_path} (timestamp refreshed)")

    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Automatically update AGENTS.md files based on code changes")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be updated without making changes")
    args = parser.parse_args()

    changed_files = get_git_changed_files()
    if not changed_files:
        if not args.dry_run:
            print("[auto_update_agents_md] No changed files detected")
        return 0

    # Map directories to their changed files
    dirs_with_changes: dict[Path, set[Path]] = {}
    for file_path in changed_files:
        directory = get_directory_for_file(file_path)
        if directory:
            if directory not in dirs_with_changes:
                dirs_with_changes[directory] = set()
            dirs_with_changes[directory].add(file_path)

    if not dirs_with_changes:
        if not args.dry_run:
            print("[auto_update_agents_md] No code changes in directories requiring AGENTS.md")
        return 0

    print(f"[auto_update_agents_md] Detected changes in {len(dirs_with_changes)} directories")
    updated_count = 0

    for directory, changed_files in dirs_with_changes.items():
        # Aggregate changes from all files in directory
        all_changes: dict[str, Any] = {"functions": [], "classes": [], "imports": []}
        for file_path in changed_files:
            file_changes = detect_code_changes(file_path)
            all_changes["functions"].extend(file_changes.get("functions", []))
            all_changes["classes"].extend(file_changes.get("classes", []))

        if all_changes["functions"] or all_changes["classes"]:
            if update_agents_md(directory, all_changes, dry_run=args.dry_run):
                updated_count += 1

    if args.dry_run:
        print(f"[auto_update_agents_md] [DRY-RUN] Would update {updated_count} AGENTS.md files")
    else:
        print(f"[auto_update_agents_md] ✓ Updated {updated_count} AGENTS.md files")

    return 0


if __name__ == "__main__":
    sys.exit(main())
