#!/usr/bin/env bash
set -euo pipefail
# Fail if code in src/ or scripts/ (except the allowlist) directly reads DSN envs.
# Allowed files: scripts/config/env.py, scripts/ops/dsn_resolve.py
# Allowed patterns (existence checks in tooling), docs, tests are ignored here.
ALLOWED='(scripts/config/env\.py|scripts/ops/dsn_resolve\.py)'
ROOTS='src|scripts'
DSN_KEYS='GEMATRIA_DSN|RW_DSN|AI_AUTOMATION_DSN|BIBLE_RO_DSN|RO_DSN|ATLAS_DSN_RW|ATLAS_DSN_RO|BIBLE_DB_DSN'
BAD_PY='os\.getenv\(\s*"(?:'"$DSN_KEYS"')'
BAD_PY2='os\.environ\.get\(\s*"(?:'"$DSN_KEYS"')'
BAD_SH='\$\{?'"$DSN_KEYS"'\}?'

# 1) Python direct env reads
rg -n --no-heading -g '!**/.venv/**' -g '!**/tests/**' -g '!**/*.md' -g '!**/*.json' \
   -e "$BAD_PY|$BAD_PY2" src scripts \
 | rg -v "$ALLOWED" || true > /tmp/dsn_bad_py.txt

# 2) Shell/Make direct env uses (execution context) — allow Makefile targets we own
rg -n --no-heading -g '!**/.venv/**' -g '!**/tests/**' -g '!**/*.md' -g '!**/*.json' \
   -e "$BAD_SH" src scripts \
 | rg -v "$ALLOWED" \
 | rg -v 'dsn\.test\.(ro|rw)|dsn_resolve\.py|psql.*BIBLE_RO_DSN|psql.*(GEMATRIA_DSN|RW_DSN|AI_AUTOMATION_DSN)' \
 || true > /tmp/dsn_bad_sh.txt

if [ -s /tmp/dsn_bad_py.txt ] || [ -s /tmp/dsn_bad_sh.txt ]; then
  echo "FAIL: Found direct DSN env usage; use scripts/config/env.py (get_rw_dsn/get_bible_db_dsn)." >&2
  echo "---- Python offenders ----" >&2; cat /tmp/dsn_bad_py.txt >&2 || true
  echo "---- Shell offenders -----" >&2; cat /tmp/dsn_bad_sh.txt >&2 || true
  exit 1
fi
echo '{ "ok": true, "note": "DSN env access centralized" }'

