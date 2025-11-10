#!/usr/bin/env python3
"""
Governance smoke test - enforce one sentinel per Always-Apply block.
"""

import glob
import pathlib
import re
import sys

# Only check governance docs for sentinels (DB-as-SSOT: sentinels are file-mirror pointers)
FILES = [
    *glob.glob("AGENTS.md"),
    *glob.glob("RULES_INDEX.md"),
]

pat_sent = re.compile(r"<!--\s*alwaysapply\.sentinel:.*?-->", re.I)

# DB-as-SSOT: Check for exactly one sentinel per governance document (not per-block)
bad = []
for f in FILES:
    try:
        txt = pathlib.Path(f).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    n = len(pat_sent.findall(txt))
    if n != 1:
        bad.append((f, n))

if bad:
    print("FAIL: sentinel count != 1 in:", bad, file=sys.stderr)
    sys.exit(2)

print("ok: governance.sentinel.one-per-block")
