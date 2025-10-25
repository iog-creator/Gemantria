#!/usr/bin/env python3
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / ".cursor" / "rules"
DEPR = RULES / "deprecated"
INDEX = ROOT / "docs" / "SSOT" / "RULES_INDEX.md"

KEEP_ALWAYS = {"000-ssot-index.mdc", "010-task-brief.mdc", "030-share-sync.mdc"}


def next_index(prefix):
    nums = [
        int(p.name.split("-")[0])
        for p in RULES.glob("*.mdc")
        if re.match(r"^\d{3}-", p.name)
    ]
    n = max(nums + [0]) + 1
    return f"{n:03d}-{prefix}.mdc"


def dry():
    plan = {"demote": [], "rename": [], "deprecate": []}
    for p in RULES.glob("*.mdc"):
        if p.name in KEEP_ALWAYS:
            continue
        txt = p.read_text(encoding="utf-8", errors="ignore")
        always = re.search(r"^alwaysApply:\s*(true|false)", txt, re.MULTILINE)
        if always and always.group(1).lower() == "true":
            plan["demote"].append(p.name)
        if not re.match(r"^\d{3}-[a-z0-9\-]+\.mdc$", p.name):
            base = re.sub(r"[^a-z0-9\-]+", "-", p.stem.lower())
            plan["rename"].append((p.name, next_index(base or "rule")))
        # simple heuristic: if description overlaps with 000/010 purposes, mark for deprecate
        if "brief" in txt.lower() or "short brief" in txt.lower():
            if p.name not in KEEP_ALWAYS:
                plan["deprecate"].append(p.name)
    return plan


def apply(plan):
    DEPR.mkdir(parents=True, exist_ok=True)
    # demote alwaysApply -> false
    for fname in plan["demote"]:
        p = RULES / fname
        txt = p.read_text(encoding="utf-8", errors="ignore")
        txt = re.sub(
            r"^alwaysApply:\s*true", "alwaysApply: false", txt, flags=re.MULTILINE
        )
        p.write_text(txt, encoding="utf-8")
    # rename non-canonical
    for old, new in plan["rename"]:
        (RULES / old).rename(RULES / new)
    # deprecate overlapping/duplicate
    for fname in plan["deprecate"]:
        src = RULES / fname
        if not src.exists():
            continue
        txt = src.read_text(encoding="utf-8", errors="ignore")
        if not txt.lower().startswith("status: deprecated"):
            txt = "status: deprecated\n" + txt
        (DEPR / fname).write_text(txt, encoding="utf-8")
        src.unlink()

    # update RULES_INDEX.md
    if INDEX.exists():
        t = INDEX.read_text(encoding="utf-8", errors="ignore").splitlines()
        out = []
        in_active = False
        for line in t:
            if line.strip().lower().startswith("## active"):
                in_active = True
            elif line.strip().lower().startswith("## deprecated"):
                in_active = False
            if in_active and any(
                x[0] == line.strip().split()[-1] for x in plan["rename"]
            ):
                # naive: skip; we'll add fresh
                continue
            out.append(line)
        if "## Deprecated" not in "\n".join(out):
            out.append("\n## Deprecated (do not apply)")
        out.append(f"- auto-updated {date.today()}")
        INDEX.write_text("\n".join(out), encoding="utf-8")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "dry"
    plan = dry()
    print("== rules.refactor plan ==")
    print("demote_always:", plan["demote"][:50])
    print("rename_noncanonical:", plan["rename"][:50])
    print("deprecate_overlap:", plan["deprecate"][:50])
    if mode == "apply":
        apply(plan)
        print("APPLIED")
    else:
        print("DRY-RUN (no changes)")


if __name__ == "__main__":
    main()
