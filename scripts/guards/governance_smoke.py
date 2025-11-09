#!/usr/bin/env python3
"""
Governance smoke test - enforce one sentinel per Always-Apply block.
"""

import glob
import pathlib
import re
import sys

FILES = [
    *glob.glob("AGENTS.md"),
    *glob.glob("RULES_INDEX.md"),
    *glob.glob("README*.md"),
    *glob.glob("docs/**/*.md", recursive=True),
    *glob.glob("share/**/*.md", recursive=True),
    "MASTER_PLAN.md",
]

pat_block = re.compile(r"(?is)^[^\n]*Always[ -]Apply[^\n]*$\n(?:.*?\n)*?(?=^#|^\S|\Z)", re.M)
pat_sent = re.compile(r"<!--\s*alwaysapply\.sentinel:.*?-->", re.I)

bad = []
for f in FILES:
    try:
        txt = pathlib.Path(f).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    for b in pat_block.findall(txt):
        n = len(pat_sent.findall(b))
        if n != 1:
            bad.append((f, n))

if bad:
    print("FAIL: sentinel count != 1 in:", bad, file=sys.stderr)
    sys.exit(2)

print("ok: governance.sentinel.one-per-block")
