# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
from pathlib import Path
import re, sys, json

roots = [
    "AGENTS.md",
    "RULES_INDEX.md",
    "GPT_REFERENCE_GUIDE.md",
    "MASTER_PLAN.md",
    "README.md",
    "README_FULL.md",
    ".cursor/rules",
]

must = [
    r"HINT-only.*STRICT_RFC3339=0",
    r"STRICT.*STRICT_RFC3339=1",
    r'metadata\.source="?fallback_fast_lane"?',
    r"generated_at.*RFC3339",
    r"\bmake housekeeping\b",
]

bad = [
    r"generated_at.*\b\d{10}(\.\d+)?\b",  # epoch examples
    r"orchestrator.*--limit",  # disallowed flag
    r"\bfast[- ]lane\b.*optional",  # contract is permanent
]


def hitset(patterns, text):
    return [p for p in patterns if re.search(p, text, re.I | re.M)]


fails = []
scanned = []

for root in roots:
    for p in Path(".").glob(root):
        if p.is_dir():
            for f in p.rglob("*.md"):
                s = f.read_text(errors="ignore")
                scanned.append(str(f))
                if hitset(bad, s) or not all(hitset([m], s) for m in must):
                    fails.append(str(f))
        elif p.is_file():
            s = p.read_text(errors="ignore")
            scanned.append(str(p))
            if hitset(bad, s) or not all(hitset([m], s) for m in must):
                fails.append(str(p))

ok = set(scanned) - set(fails)
print(
    json.dumps(
        {
            "scanned": len(scanned),
            "ok": len(ok),
            "fails": len(fails),
            "fail_list": sorted(set(fails)),
        },
        indent=2,
    )
)

sys.exit(1 if fails else 0)
