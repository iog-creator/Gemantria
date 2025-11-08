# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES_DIR = ROOT / ".cursor" / "rules"
INDEX = ROOT / "docs" / "SSOT" / "RULES_INDEX.md"
AGENTS = ROOT / "AGENTS.md"


def load_rules():
    rules = []
    for p in sorted(RULES_DIR.glob("*.mdc")):
        txt = p.read_text(encoding="utf-8", errors="ignore")
        desc = re.search(r"^description:\s*(.+)$", txt, re.MULTILINE)
        always = re.search(r"^alwaysApply:\s*(true|false)", txt, re.MULTILINE)
        links = re.findall(
            r"(AGENTS\.md|RULES_INDEX\.md|SHARE_MANIFEST\.json|SSOT_[^)\s]+|\.py|\.sh|\.sql|Makefile)",
            txt,
        )
        rules.append(
            {
                "file": p.name,
                "description": (desc.group(1).strip() if desc else "").lower(),
                "always": (always and always.group(1).lower() == "true") or False,
                "links": sorted(set(links)),
            }
        )
    return rules


def load_index_active():
    txt = INDEX.read_text(encoding="utf-8", errors="ignore")
    active = set()
    section = None
    for line in txt.splitlines():
        if line.strip().lower().startswith("## active"):
            section = "a"
            continue
        if line.strip().lower().startswith("## deprecated"):
            section = None
            continue
        m = re.match(r"-\s+([0-9a-zA-Z\-_\.]+)", line.strip())
        if m and section == "a":
            active.add(m.group(1))
    return active


def main():
    if not RULES_DIR.exists():
        print("ERR: .cursor/rules missing")
        sys.exit(2)
    rules = load_rules()
    active = load_index_active()
    # 1) Duplicated descriptions
    desc_map = {}
    for r in rules:
        if r["description"]:
            desc_map.setdefault(r["description"], []).append(r["file"])
    dups = {k: v for k, v in desc_map.items() if len(v) > 1}

    # 2) Overlapping purpose heuristics
    overlaps = [files for files in dups.values() if len(files) > 1]

    # 3) Non-canonical names: enforce NNN-name.mdc (NNN = 3 digits)
    noncanon = [r["file"] for r in rules if not re.match(r"^\d{3}-[a-z0-9\-]+\.mdc$", r["file"])]

    # 4) Broken index: files not in Active
    unindexed = sorted([r["file"] for r in rules if r["file"] not in active])

    # 5) Too many alwaysApply
    always = sorted([r["file"] for r in rules if r["always"]])
    recommended_always = {
        "000-ssot-index.mdc",
        "010-task-brief.mdc",
        "030-share-sync.mdc",
    }

    # 6) Cross-link coverage
    missing_links = [r["file"] for r in rules if not r["links"]]

    # 7) Agent ↔ rule references quick check
    agents_txt = AGENTS.read_text(encoding="utf-8", errors="ignore") if AGENTS.exists() else ""
    mentions_in_agents = [r["file"] for r in rules if r["file"] in agents_txt]

    print("== rules.lint ==")
    print("noncanonical_names:", noncanon[:50])
    print("duplicate_descriptions:", overlaps[:20])
    print("unindexed_rules:", unindexed[:50])
    print("alwaysApply_rules:", always)
    if len(always) > 3:
        print(
            "ALERT: too many alwaysApply; recommend keeping only:",
            sorted(recommended_always),
        )
    print("missing_cross_links:", missing_links[:50])
    print("mentioned_in_AGENTS:", mentions_in_agents[:50])
    print(
        "summary:",
        {
            "total_rules": len(rules),
            "alwaysApply_count": len(always),
            "unindexed_count": len(unindexed),
            "noncanonical_count": len(noncanon),
            "duplicates_count": len(overlaps),
        },
    )


if __name__ == "__main__":
    main()
