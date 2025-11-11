#!/usr/bin/env python3
"""
Guard: Forbid scheduled/nightly workflows by default.

Fails if any .github/workflows/*.yml(yaml) contains a top-level `schedule:` trigger.

HINT/housekeeping: Use workflow_dispatch/manual only.
"""

from __future__ import annotations

import sys
import pathlib
import re

WF_DIR = pathlib.Path(".github/workflows")
if not WF_DIR.exists():
    sys.exit(0)

bad = []
for p in WF_DIR.glob("**/*.y*ml"):
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    # naive but robust-enough scan for a top-level 'schedule:' (start of line or after 'on:')
    if re.search(r"(?m)^[ \t]*schedule:\s*$", text):
        bad.append(str(p))

if bad:
    print("FAIL: Nightly/scheduled triggers are forbidden by policy.", file=sys.stderr)
    for b in bad:
        print(f" - {b}", file=sys.stderr)
    print(
        "\nRemediation: remove top-level `schedule:` blocks; prefer workflow_dispatch/manual.",
        file=sys.stderr,
    )
    sys.exit(1)
else:
    print("OK: No scheduled/nightly workflows detected.")
    sys.exit(0)
