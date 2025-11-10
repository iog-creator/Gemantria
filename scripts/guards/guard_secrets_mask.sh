#!/usr/bin/env bash
set -euo pipefail
# HINT by default; STRICT with STRICT_SECRETS_MASK=1
STRICT="${STRICT_SECRETS_MASK:-0}"

# Scan common evidence/docs for DSN-like strings that are NOT masked (no ****@)
# Exclude .venv and node_modules; keep it lightweight.
BAD=$(rg -n --no-heading -g '!**/.venv/**' -g '!**/node_modules/**' \
     -e 'postgres(ql)?://[^*[:space:]]+@' docs/ evidence/ || true)

if [ -n "$BAD" ]; then
  echo '{ "ok": false, "note": "Found unmasked DSN-like strings in artifacts" }'
  echo "$BAD" >&2
  [ "$STRICT" = "1" ] && exit 1 || exit 0
fi
echo '{ "ok": true, "note": "No unmasked DSN patterns in artifacts" }'

