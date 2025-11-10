#!/usr/bin/env bash
set -euo pipefail
# Fails if any executable call uses bare "python " outside .py files, .venv, .md files, and the guard script itself.
# Excludes comments and existence checks (which python, command -v python).
matches=$(rg -n --no-heading -g '!**/.venv/**' -g '!**/*.py' -g '!**/*.md' -g '!scripts/guards/guard_python_runner.sh' \
     -e '^\s*(python\s|@python\s|\tpython\s|python\s-c|python\s-m)' \
     -e '\s+python\s+[^-]' | grep -v '#.*python' | grep -v 'which python' | grep -v 'command.*python' || true)
if [ -n "$matches" ]; then
  echo "FAIL: Found bare 'python ' invocations. Use \$(PYTHON) or python3." >&2
  echo "$matches" >&2
  exit 1
fi
echo '{ "ok": true, "note": "No bare python invocations found." }'

