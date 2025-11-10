#!/usr/bin/env bash
set -euo pipefail

# Mode: HINT by default (ok: true with counts), STRICT if STRICT_DSN_CENTRAL=1 (fail on offenders not in allowlist)
STRICT="${STRICT_DSN_CENTRAL:-0}"
ALLOWLIST_FILE="scripts/guards/.dsn_direct.allowlist"

# Canonical exceptions (files allowed to touch DSN envs directly)
ALLOWED_CANON='(scripts/config/env\.py|scripts/ops/dsn_resolve\.py)'
ROOTS='src|scripts'
DSN_KEYS='GEMATRIA_DSN|RW_DSN|AI_AUTOMATION_DSN|BIBLE_RO_DSN|RO_DSN|ATLAS_DSN|ATLAS_DSN_RW|ATLAS_DSN_RO|BIBLE_DB_DSN'
BAD_PY='os\.getenv\(\s*"(?:'"$DSN_KEYS"')'
BAD_PY2='os\.environ\.get\(\s*"(?:'"$DSN_KEYS"')'
BAD_SH='(^|[^A-Za-z0-9_])('"$DSN_KEYS"')([[:space:]]|[^A-Za-z0-9_])'

# Gather offenders (Python)
rg -n --no-heading -g '!**/.venv/**' -g '!**/tests/**' -g '!**/*.md' -g '!**/*.json' \
   -e "$BAD_PY|$BAD_PY2" src scripts | rg -v "$ALLOWED_CANON" || true > /tmp/dsn_bad_py.txt
# Gather offenders (Shell/Make)
rg -n --no-heading -g '!**/.venv/**' -g '!**/tests/**' -g '!**/*.md' -g '!**/*.json' \
   -e "$BAD_SH" src scripts \
 | rg -v "$ALLOWED_CANON" \
 | rg -v 'dsn\.test\.(ro|rw)|dsn_resolve\.py|psql.*(BIBLE_RO_DSN|GEMATRIA_DSN|RW_DSN|AI_AUTOMATION_DSN)' \
 || true > /tmp/dsn_bad_sh.txt

# Apply project allowlist (legacy scripts migrating over time)
touch "$ALLOWLIST_FILE"
grep -v '^\s*$' "$ALLOWLIST_FILE" | grep -v '^\s*#' || true > /tmp/dsn_allow.txt
filter_allowlist() {
  if [ -s /tmp/dsn_allow.txt ]; then
    # Keep only lines not matching any allowlist glob
    # Convert globs to ripgrep alternation
    local rgpat
    rgpat="$(sed 's/[].[^$*+?(){|\\]/\\&/g;s/\*/.*/g' /tmp/dsn_allow.txt | paste -sd'|' -)"
    if [ -n "${rgpat:-}" ]; then
      rg -v "(${rgpat})" || true
    else
      cat
    fi
  else
    cat
  fi
}
cat /tmp/dsn_bad_py.txt | filter_allowlist > /tmp/dsn_bad_py.eff.txt
cat /tmp/dsn_bad_sh.txt | filter_allowlist > /tmp/dsn_bad_sh.eff.txt

bad_py_count=$(wc -l < /tmp/dsn_bad_py.eff.txt || echo 0)
bad_sh_count=$(wc -l < /tmp/dsn_bad_sh.eff.txt || echo 0)
total=$(( bad_py_count + bad_sh_count ))

if [ "$STRICT" = "1" ] && [ "$total" -gt 0 ]; then
  echo '{ "ok": false, "mode": "STRICT", "bad_py": '"$bad_py_count"', "bad_sh": '"$bad_sh_count"' }'
  echo "---- Python offenders (effective) ----" >&2; cat /tmp/dsn_bad_py.eff.txt >&2 || true
  echo "---- Shell offenders (effective) -----" >&2; cat /tmp/dsn_bad_sh.eff.txt >&2 || true
  exit 1
fi
echo '{ "ok": true, "mode": "HINT", "bad_py": '"$bad_py_count"', "bad_sh": '"$bad_sh_count"' }'
