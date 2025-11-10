#!/usr/bin/env bash
set -euo pipefail
# Fails if any executable call uses bare "python " outside .py files, .venv, .md files, and the guard script itself.
if rg -n --no-heading -g '!**/.venv/**' -g '!**/*.py' -g '!**/*.md' -g '!scripts/guards/guard_python_runner.sh' \
     -e '(^|[^A-Za-z0-9_])python([[:space:]]|$)' ; then
  echo "FAIL: Found bare 'python ' invocations. Use \$(PYTHON) or python3." >&2
  exit 1
fi
echo '{ "ok": true, "note": "No bare python invocations found." }'

