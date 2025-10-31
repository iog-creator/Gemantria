#!/usr/bin/env python3
"""
Assert only the specified rules are marked alwaysApply: true.
Intended as a fast guard for Cursor rule bloat/regression.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT / ".cursor" / "rules"
ALLOWED = {
    "000-ssot-index.mdc",
    "010-task-brief.mdc",
    "030-share-sync.mdc",
    "039-execution-contract.mdc",
    "040-ci-triage-playbook.mdc",
    "049-gpt5-contract-v5.2.mdc",
    "050-connector-failure.mdc",
}


def main() -> None:
    offenders = []
    for p in sorted(RULES_DIR.glob("*.mdc")):
        text = p.read_text(errors="ignore")
        # poor-man's frontmatter parse: look for `alwaysApply:` in first 100 lines
        header = "\n".join(text.splitlines()[:100])
        m = re.search(r"alwaysApply:\s*(true|True|1)", header)
        if m and p.name not in ALLOWED:
            offenders.append(p.name)
    if offenders:
        msg = f"only {', '.join(sorted(ALLOWED))} may be alwaysApply; found: {', '.join(offenders)}"
        print(f"[rules.navigator.check] FAIL: {msg}", file=sys.stderr)
        sys.exit(2)
    print(f"[rules.navigator.check] PASS: only {', '.join(sorted(ALLOWED))} are alwaysApply")


if __name__ == "__main__":
    main()
