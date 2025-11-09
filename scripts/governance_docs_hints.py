#!/usr/bin/env python3
"""
governance_docs_hints.py — Emit hints for governance documentation and rule changes

Per Rule 026 (Hints Envelope) and Rule 065 (GPT Documentation Sync), this script
emits hints when rules or documentation change, storing them in a file-based
hints envelope for auditability.

Hermetic: Works without database (Rule 046 compliance).
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "evidence"
HINTS_FILE = EVIDENCE_DIR / "governance_docs_hints.json"


def check_git_status() -> list[str]:
    """Check git status for modified rules/docs files."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        modified = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            # Parse git status line: "XY filename"
            status = line[:2]
            filename = line[3:]
            # Check if it's a rule or doc file
            if any(
                filename.startswith(prefix)
                for prefix in [
                    ".cursor/rules/",
                    "docs/SSOT/",
                    "AGENTS.md",
                    "RULES_INDEX.md",
                ]
            ):
                modified.append(filename)
        return modified
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Git not available or not a git repo - return empty
        return []


def check_recent_changes() -> list[str]:
    """Check for recently modified rules/docs files (last 24h)."""
    recent = []
    cutoff = datetime.now(UTC).timestamp() - (24 * 3600)  # 24 hours ago

    paths_to_check = [
        ROOT / ".cursor" / "rules",
        ROOT / "docs" / "SSOT",
        ROOT / "AGENTS.md",
        ROOT / "RULES_INDEX.md",
    ]

    for path in paths_to_check:
        if not path.exists():
            continue
        if path.is_file():
            if path.stat().st_mtime > cutoff:
                recent.append(str(path.relative_to(ROOT)))
        elif path.is_dir():
            for file_path in path.rglob("*.md"):
                if file_path.stat().st_mtime > cutoff:
                    recent.append(str(file_path.relative_to(ROOT)))

    return recent


def emit_hints_envelope(modified_files: list[str], recent_files: list[str]) -> dict:
    """Create a hints envelope for governance docs/rule changes."""
    hints = []

    if modified_files:
        hints.append(
            f"governance.docs: {len(modified_files)} rule/doc file(s) modified: {', '.join(modified_files[:3])}"
            + (f" (+{len(modified_files) - 3} more)" if len(modified_files) > 3 else "")
        )

    if recent_files:
        # Filter out files already in modified_files
        new_recent = [f for f in recent_files if f not in modified_files]
        if new_recent:
            hints.append(
                f"governance.docs: {len(new_recent)} rule/doc file(s) changed in last 24h: {', '.join(new_recent[:3])}"
                + (f" (+{len(new_recent) - 3} more)" if len(new_recent) > 3 else "")
            )

    # Check for new rules
    rules_dir = ROOT / ".cursor" / "rules"
    if rules_dir.exists():
        rule_files = sorted(rules_dir.glob("*.mdc"))
        if rule_files:
            latest_rule = max(rule_files, key=lambda p: p.stat().st_mtime)
            if latest_rule.stat().st_mtime > datetime.now(UTC).timestamp() - 3600:  # Last hour
                hints.append(f"governance.rules: New rule detected: {latest_rule.name}")

    # Check for GPT docs updates (Rule 065)
    gpt_docs = [
        ROOT / "docs" / "SSOT" / "GPT_SYSTEM_PROMPT.md",
        ROOT / "docs" / "SSOT" / "GPT_REFERENCE_GUIDE.md",
    ]
    for doc in gpt_docs:
        if doc.exists() and doc.stat().st_mtime > datetime.now(UTC).timestamp() - 3600:
            hints.append(f"governance.gpt: GPT documentation updated: {doc.name} (Rule 065)")

    envelope = {
        "type": "hints_envelope",
        "version": "1.0",
        "schema": "governance.docs-hints.v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "items": hints,
        "count": len(hints),
        "context": "governance_documentation",
        "rule_reference": "026, 065",
    }

    return envelope


def main() -> int:
    """Main function: check for changes and emit hints envelope."""
    modified = check_git_status()
    recent = check_recent_changes()

    envelope = emit_hints_envelope(modified, recent)

    # Write hints envelope to evidence directory
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    with HINTS_FILE.open("w", encoding="utf-8") as f:
        json.dump(envelope, f, indent=2, ensure_ascii=False)

    # Print hints to stderr (LOUD HINT pattern)
    if envelope["count"] > 0:
        for hint in envelope["items"]:
            print(f"HINT: {hint}", file=sys.stderr)
        print(f"HINT: governance.docs: Wrote {envelope['count']} hint(s) → {HINTS_FILE}", file=sys.stderr)
    else:
        print("HINT: governance.docs: No rule/doc changes detected", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
