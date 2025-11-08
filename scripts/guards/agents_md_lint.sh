#!/usr/bin/env bash
set -euo pipefail

# Fail if root AGENTS.md contains folder-scoped headers
if rg -n "^# AGENTS.md - " AGENTS.md >/dev/null 2>&1; then
  echo "ROOT_AGENTS_BLOAT: root AGENTS.md contains folder-scoped headers"
  exit 1
fi

# Warn (non-fatal) if any code/docs dir lacks AGENTS.md quick-hint
# (directories discovered by the existing generator)
missing_output=$(python scripts/create_agents_md.py --dry-run 2>&1)
if echo "$missing_output" | grep -q "WOULD CREATE:"; then
  echo "HINT: missing folder AGENTS.md detected by generator"
fi

echo "[agents.md.lint] OK"
