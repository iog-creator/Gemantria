#!/usr/bin/env python3
"""
check_agents_md_sync.py — Check if AGENTS.md files need updates based on code changes.

This script detects when code changes in a directory should trigger AGENTS.md updates.
It compares file modification times and git history to identify potentially stale AGENTS.md files.

Rule References: 006 (AGENTS.md Governance), 027 (Docs Sync Gate), 017 (Agent Docs Presence)

Usage:
    python scripts/check_agents_md_sync.py  # Check all directories
    python scripts/check_agents_md_sync.py --staged  # Check only staged changes
    python scripts/check_agents_md_sync.py --verbose  # Show detailed output
"""

import argparse
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def get_git_changed_files(staged_only: bool = False) -> set[Path]:
    """Get list of changed files from git."""
    try:
        if staged_only:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                check=True,
            )
        else:
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
    # Skip if file is in root or excluded directories
    excluded = {".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache"}

    # Find the first directory that should have AGENTS.md
    current = file_path.parent
    while current != ROOT.parent:
        if current.name in excluded:
            return None

        # Check if this directory type requires AGENTS.md
        rel_path = current.relative_to(ROOT)
        path_str = str(rel_path)

        # Source directories
        if path_str.startswith("src/") and current.name not in excluded:
            return current

        # AgentPM directories (agent automation modules)
        if path_str.startswith("agentpm/") and current.name not in excluded:
            return current

        # Tool directories
        if path_str in ["scripts", "migrations", "tests", "tools"]:
            return current

        # Docs directories
        if path_str.startswith("docs/") and current.name not in excluded:
            return current

        # WebUI directories
        if path_str.startswith("webui/") and current.name not in excluded:
            return current

        current = current.parent

    return None


def get_agents_md_mtime(agents_path: Path) -> datetime | None:
    """Get modification time of AGENTS.md file."""
    if not agents_path.exists():
        return None

    try:
        # Try git log first (more accurate for committed files)
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(agents_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            timestamp = int(result.stdout.strip())
            return datetime.fromtimestamp(timestamp)
    except Exception:
        pass

    # Fallback to filesystem mtime
    try:
        return datetime.fromtimestamp(agents_path.stat().st_mtime)
    except Exception:
        return None


def get_code_files_mtime(directory: Path) -> datetime | None:
    """Get most recent modification time of code files in directory."""
    code_extensions = {".py", ".ts", ".tsx", ".js", ".jsx", ".sql", ".yaml", ".yml", ".json"}
    max_mtime = None

    for file_path in directory.rglob("*"):
        if file_path.is_file() and file_path.suffix in code_extensions:
            # Skip AGENTS.md and other docs
            if file_path.name in {"AGENTS.md", "README.md"}:
                continue

            try:
                # Try git log first
                result = subprocess.run(
                    ["git", "log", "-1", "--format=%ct", "--", str(file_path)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0 and result.stdout.strip():
                    timestamp = int(result.stdout.strip())
                    file_mtime = datetime.fromtimestamp(timestamp)
                else:
                    # Fallback to filesystem
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)

                if max_mtime is None or file_mtime > max_mtime:
                    max_mtime = file_mtime
            except Exception:
                continue

    return max_mtime


def check_agents_md_sync(staged_only: bool = False, verbose: bool = False) -> int:
    """Check if AGENTS.md files are in sync with code changes."""
    changed_files = get_git_changed_files(staged_only)

    if not changed_files:
        if verbose:
            print("[check_agents_md_sync] No changed files detected")
        return 0

    # Map directories to their changed files
    dirs_with_changes: dict[Path, set[Path]] = {}
    for file_path in changed_files:
        # Skip AGENTS.md files themselves
        if file_path.name == "AGENTS.md":
            continue

        # Skip if not a code file
        code_extensions = {".py", ".ts", ".tsx", ".js", ".jsx", ".sql", ".yaml", ".yml"}
        if file_path.suffix not in code_extensions:
            continue

        directory = get_directory_for_file(file_path)
        if directory:
            if directory not in dirs_with_changes:
                dirs_with_changes[directory] = set()
            dirs_with_changes[directory].add(file_path)

    if not dirs_with_changes:
        if verbose:
            print("[check_agents_md_sync] No code changes in directories requiring AGENTS.md")
        return 0

    issues = []
    for directory, changed_files in dirs_with_changes.items():
        agents_path = directory / "AGENTS.md"

        if not agents_path.exists():
            issues.append(f"  ⚠️  {directory.relative_to(ROOT)}/: Code changed but AGENTS.md missing")
            continue

        # Check if AGENTS.md was updated recently
        agents_mtime = get_agents_md_mtime(agents_path)
        if agents_mtime is None:
            continue

        # Check if any code files are newer than AGENTS.md
        code_mtime = get_code_files_mtime(directory)
        if code_mtime and code_mtime > agents_mtime:
            # Allow 1 hour grace period for same-commit updates
            if code_mtime - agents_mtime > timedelta(hours=1):
                issues.append(
                    f"  ⚠️  {directory.relative_to(ROOT)}/AGENTS.md: "
                    f"Code updated {code_mtime.strftime('%Y-%m-%d %H:%M')} "
                    f"but AGENTS.md last updated {agents_mtime.strftime('%Y-%m-%d %H:%M')}"
                )

    if issues:
        print("[check_agents_md_sync] POTENTIAL SYNC ISSUES DETECTED:")
        print("")
        for issue in issues:
            print(issue)
        print("")
        print("💡 HINT: Update AGENTS.md files to reflect code changes per Rule 006 & Rule 027")
        print("   Run: python scripts/create_agents_md.py --dry-run  # Check for missing files")
        return 1

    if verbose:
        print("[check_agents_md_sync] ✓ All AGENTS.md files appear in sync with code changes")
    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check if AGENTS.md files need updates based on code changes")
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Check only staged changes (default: all changes since HEAD)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output",
    )
    args = parser.parse_args()

    exit_code = check_agents_md_sync(staged_only=args.staged, verbose=args.verbose)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
