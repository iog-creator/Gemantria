#!/usr/bin/env python3

import sys, os

REQUIRED = [
    ".cursor/rules/000-ssot-index.mdc",
    ".cursor/rules/050-ops-contract.mdc",
    ".cursor/rules/051-cursor-insight.mdc",
    ".cursor/rules/052-tool-priority.mdc",
    ".cursor/rules/060-pipeline-sequence.mdc",
    "RULES_INDEX.md",
    "AGENTS.md",
    "src/graph/AGENTS.md",
    "src/nodes/AGENTS.md",
]

missing = [p for p in REQUIRED if not os.path.exists(p)]

if missing:
    print("ERROR: missing Cursor surfaces:\n - " + "\n - ".join(missing), file=sys.stderr)
    sys.exit(2)

print("OK: Cursor surfaces present.")
