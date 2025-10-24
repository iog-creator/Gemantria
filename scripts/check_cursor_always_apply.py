#!/usr/bin/env python3
"""
Assert only the three navigator rules are marked alwaysApply: true.
Intended as a fast guard for Cursor rule bloat/regression.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT / ".cursor" / "rules"
ALLOWED = {"000-ssot-index.mdc", "010-task-brief.mdc", "030-share-sync.mdc"}


def main() -> None:
    offenders = []
    for p in sorted(RULES_DIR.glob("*.mdc")):
        text = p.read_text(errors="ignore")
        # poor-man's frontmatter parse: look for `alwaysApply:` in the first 100 lines
        header = "\n".join(text.splitlines()[:100])
        m = re.search(r"alwaysApply:\s*(true|True|1)", header)
        if m and p.name not in ALLOWED:
            offenders.append(p.name)
    if offenders:
        msg = f"only 000/010/030 may be alwaysApply; found: {', '.join(offenders)}"
        print(f"[rules.navigator.check] FAIL: {msg}", file=sys.stderr)
        sys.exit(2)
    print("[rules.navigator.check] PASS: only navigators are alwaysApply (000/010/030)")


if __name__ == "__main__":
    main()
