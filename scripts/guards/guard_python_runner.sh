#!/usr/bin/env bash
set -euo pipefail
# Fails if any executable call uses bare "python " outside .py files and .venv.
if rg -n --no-heading -g '!**/.venv/**' -g '!**/*.py' \
     -e '(^|[^A-Za-z0-9_])python([[:space:]]|$)' ; then
  echo "FAIL: Found bare 'python ' invocations. Use \$(PYTHON) or python3." >&2
  exit 1
fi
echo '{ "ok": true, "note": "No bare python invocations found." }'

