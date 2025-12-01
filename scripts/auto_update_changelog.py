#!/usr/bin/env python3
"""
auto_update_changelog.py — Automatically update CHANGELOG.md based on recent commits/PRs.

This script detects new features, fixes, and changes from git commits and PR descriptions,
then automatically adds entries to CHANGELOG.md in the [Unreleased] section.

Rule References: 027 (Docs Sync Gate), 058 (Auto-Housekeeping)

Usage:
    python scripts/auto_update_changelog.py  # Auto-update based on recent commits
    python scripts/auto_update_changelog.py --dry-run  # Show what would be added
    python scripts/auto_update_changelog.py --pr <pr-number>  # Update from PR description
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG_PATH = ROOT / "CHANGELOG.md"


def get_recent_commits(limit: int = 10) -> list[dict[str, Any]]:
    """Get recent git commits with messages."""
    try:
        result = subprocess.run(
            ["git", "log", f"-{limit}", "--pretty=format:%H|%s|%b"],
            capture_output=True,
            text=True,
            check=True,
        )
        commits = []
        for line in result.stdout.strip().split("\n\n"):
            if "|" in line:
                parts = line.split("|", 2)
                if len(parts) >= 2:
                    commits.append(
                        {
                            "hash": parts[0],
                            "subject": parts[1],
                            "body": parts[2] if len(parts) > 2 else "",
                        }
                    )
        return commits
    except subprocess.CalledProcessError:
        return []


def extract_feature_info(commit: dict[str, Any]) -> dict[str, Any] | None:
    """Extract feature information from commit message."""
    subject = commit.get("subject", "")
    body = commit.get("body", "")

    # Look for conventional commit format: type(scope): description
    match = re.match(r"^(feat|fix|docs|refactor|test|chore)(\([^)]+\))?:\s*(.+)$", subject)
    if not match:
        return None

    commit_type = match.group(1)
    scope = match.group(2) if match.group(2) else ""
    description = match.group(3)

    # Look for PR number in body or subject
    pr_match = re.search(r"\(PR\s*#(\d+)\)", body + " " + subject)
    pr_number = pr_match.group(1) if pr_match else None

    # Look for Phase-3B Feature #X pattern
    feature_match = re.search(r"Phase-3B\s+Feature\s*#(\d+)", body + " " + subject, re.IGNORECASE)
    feature_number = feature_match.group(1) if feature_match else None

    return {
        "type": commit_type,
        "scope": scope,
        "description": description,
        "pr_number": pr_number,
        "feature_number": feature_number,
        "hash": commit.get("hash", "")[:8],
    }


def format_changelog_entry(info: dict[str, Any]) -> str:
    """Format a changelog entry from feature info."""
    # Build entry text
    if info.get("feature_number"):
        entry = f"Phase-3B Feature #{info['feature_number']}: {info['description']}"
    elif info.get("pr_number"):
        entry = f"{info['description']} (PR #{info['pr_number']})"
    else:
        entry = info["description"]

    return f"- {entry}"


def read_changelog() -> str:
    """Read current CHANGELOG.md content."""
    if not CHANGELOG_PATH.exists():
        return "## [Unreleased]\n\n"
    return CHANGELOG_PATH.read_text()


def write_changelog(content: str) -> None:
    """Write updated CHANGELOG.md content."""
    CHANGELOG_PATH.write_text(content)


def update_changelog(entries: list[str], dry_run: bool = False) -> bool:
    """Add new entries to CHANGELOG.md [Unreleased] section."""
    content = read_changelog()

    # Find [Unreleased] section
    unreleased_match = re.search(r"##\s*\[Unreleased\]\s*\n", content)
    if not unreleased_match:
        # Create [Unreleased] section at the top
        content = "## [Unreleased]\n\n" + content
        unreleased_match = re.search(r"##\s*\[Unreleased\]\s*\n", content)

    if not unreleased_match:
        print("[auto_update_changelog] ERROR: Could not find or create [Unreleased] section")
        return False

    # Find insertion point (after [Unreleased] header, before first existing entry or next section)
    insert_pos = unreleased_match.end()
    next_section_match = re.search(r"\n##\s*\[", content[insert_pos:])
    if next_section_match:
        insert_pos += next_section_match.start()
    else:
        insert_pos = len(content)

    # Check if entries already exist
    existing_entries = set()
    for entry in entries:
        # Extract key part of entry for comparison
        key = entry.split(":")[0] if ":" in entry else entry
        if key in content:
            existing_entries.add(entry)

    new_entries = [e for e in entries if e not in existing_entries]
    if not new_entries:
        if not dry_run:
            print("[auto_update_changelog] All entries already present in CHANGELOG.md")
        return True

    # Insert new entries
    new_content = content[:insert_pos]
    if not new_content.endswith("\n\n"):
        new_content += "\n"
    new_content += "\n".join(new_entries) + "\n"
    new_content += content[insert_pos:]

    if dry_run:
        print("[auto_update_changelog] [DRY-RUN] Would add entries to CHANGELOG.md:")
        for entry in new_entries:
            print(f"  {entry}")
    else:
        write_changelog(new_content)
        print(f"[auto_update_changelog] ✓ Added {len(new_entries)} entries to CHANGELOG.md")

    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Automatically update CHANGELOG.md based on recent commits")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be added without making changes")
    parser.add_argument("--pr", type=int, help="PR number to extract changelog entry from")
    parser.add_argument("--limit", type=int, default=10, help="Number of recent commits to check (default: 10)")
    args = parser.parse_args()

    entries = []

    if args.pr:
        # Extract from PR description (would need GitHub API or gh CLI)
        print(f"[auto_update_changelog] PR extraction not yet implemented (PR #{args.pr})")
        return 1
    else:
        # Extract from recent commits
        commits = get_recent_commits(limit=args.limit)
        for commit in commits:
            info = extract_feature_info(commit)
            if info and info["type"] in ("feat", "fix", "docs"):
                entry = format_changelog_entry(info)
                entries.append(entry)

    if not entries:
        if not args.dry_run:
            print("[auto_update_changelog] No suitable commits found for CHANGELOG.md")
        return 0

    if update_changelog(entries, dry_run=args.dry_run):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
