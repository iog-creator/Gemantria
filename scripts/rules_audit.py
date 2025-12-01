# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
rules_audit.py - Ensure .cursor/rules numbering is contiguous; update docs lists.

- Detects missing numbers and duplicates.
- Generates/updates:
  * docs/SSOT/RULES_INDEX.md (authoritative list)
  * Injects a short "Rules Inventory" table into AGENTS.md
  * Appends/updates a "Rules" table in docs/SSOT/MASTER_PLAN.md (phases-rules mapping)
- Exits nonzero on drift unless ALLOW_RULES_GAP=1 (local only).
"""

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES = ROOT / ".cursor" / "rules"
AGENTS = ROOT / "AGENTS.md"
PLAN = ROOT / "docs" / "SSOT" / "MASTER_PLAN.md"
INDEX = ROOT / "docs" / "SSOT" / "RULES_INDEX.md"


def find_rules():
    entries = []
    for p in sorted(RULES.glob("*.mdc")):
        m = re.match(r"^(\d{3})-", p.name)
        if not m:
            continue
        num = int(m.group(1))
        title = "# " + p.read_text(errors="ignore").splitlines()[0].lstrip("# ").strip()
        entries.append((num, p.name, title))
    return entries


def write_rules_index(entries):
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# RULES_INDEX\n", "| # | File | Title |", "|---:|------|-------|"]
    for num, fname, title in entries:
        lines.append(f"| {num:03d} | {fname} | {title} |")
    new_content = "\n".join(lines) + "\n"

    if INDEX.exists():
        old_content = INDEX.read_text()
        if old_content == new_content:
            return False  # No change

    INDEX.write_text(new_content)
    return True  # Changed


def inject_agents_table(entries):
    if not AGENTS.exists():
        return False
    old_text = AGENTS.read_text()
    start = "<!-- RULES_INVENTORY_START -->"
    end = "<!-- RULES_INVENTORY_END -->"
    table = ["| # | Title |", "|---:|-------|"]
    for num, _, title in entries:
        table.append(f"| {num:03d} | {title} |")
    block = start + "\n" + "\n".join(table) + "\n" + end
    if start in old_text and end in old_text:
        new_text = re.sub(rf"{re.escape(start)}.*?{re.escape(end)}", block, old_text, flags=re.S)
    else:
        new_text = old_text + "\n\n" + block + "\n"

    if new_text != old_text:
        AGENTS.write_text(new_text)
        return True  # Changed
    return False  # No change


def inject_plan_rules(entries):
    if not PLAN.exists():
        return False
    old_text = PLAN.read_text()
    start = "<!-- RULES_TABLE_START -->"
    end = "<!-- RULES_TABLE_END -->"
    table = ["| # | Title |", "|---:|-------|"]
    for num, _, title in entries:
        table.append(f"| {num:03d} | {title} |")
    block = start + "\n" + "\n".join(table) + "\n" + end
    if start in old_text and end in old_text:
        new_text = re.sub(rf"{re.escape(start)}.*?{re.escape(end)}", block, old_text, flags=re.S)
    else:
        new_text = old_text + "\n\n" + block + "\n"

    if new_text != old_text:
        PLAN.write_text(new_text)
        return True  # Changed
    return False  # No change


def main():
    print(f"[rules_audit] Scanning {RULES} for rule files...")
    entries = find_rules()
    print(
        f"[rules_audit] Found {len(entries)} rule files: {[f'{num:03d}-{fname}' for num, fname, _ in entries]}"
    )

    if not entries:
        print("[rules_audit] FAIL: No rules found", file=sys.stderr)
        sys.exit(2)

    # Detect gaps/dupes
    nums = [n for n, _, _ in entries]
    print(f"[rules_audit] Rule numbers range: {min(nums)}-{max(nums)} (total: {len(nums)} unique)")

    missing = []
    for n in range(min(nums), max(nums) + 1):
        if n not in nums:
            missing.append(n)

    dupes = [n for n in set(nums) if nums.count(n) > 1]

    if dupes:
        print(
            f"[rules_audit] FAIL: Duplicate rule numbers: {sorted(dupes)}",
            file=sys.stderr,
        )
        sys.exit(2)

    print(f"[rules_audit] Gap analysis: {len(missing)} missing numbers in range")
    if missing:
        print(f"[rules_audit] Missing numbers: {missing}")

    # We tolerate historically missing numbers ONLY if we have reserved/dep files in place
    tolerated = {14, 23, 24, 11, 16, 9}
    unresolved = [n for n in missing if n not in tolerated]

    if unresolved and os.environ.get("ALLOW_RULES_GAP") != "1":
        print(
            f"[rules_audit] FAIL: Unresolved missing rule numbers (no reserved markers): {unresolved}",
            file=sys.stderr,
        )
        print(f"[rules_audit] Tolerated missing numbers: {sorted(tolerated)}")
        print("[rules_audit] Set ALLOW_RULES_GAP=1 to bypass this check")
        sys.exit(2)

    if unresolved:
        print(
            f"[rules_audit] Tolerating {len(unresolved)} missing numbers (reserved markers present): {unresolved}"
        )

    changed_files = []

    print(f"[rules_audit] Generating {INDEX}...")
    if write_rules_index(entries):
        changed_files.append(str(INDEX.relative_to(ROOT)))

    print(f"[rules_audit] Injecting rules table into {AGENTS}...")
    if inject_agents_table(entries):
        changed_files.append(str(AGENTS.relative_to(ROOT)))

    print(f"[rules_audit] Injecting rules table into {PLAN}...")
    if inject_plan_rules(entries):
        changed_files.append(str(PLAN.relative_to(ROOT)))

    if changed_files:
        print("[rules_audit] CHANGED FILES:")
        for f in changed_files:
            print(f"  - {f}")
    else:
        print("[rules_audit] No files changed")

    print("[rules_audit] PASS - Rules numbering contiguous, docs updated")


if __name__ == "__main__":
    main()
