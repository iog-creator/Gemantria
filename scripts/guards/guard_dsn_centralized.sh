#!/usr/bin/env bash
set -euo pipefail
# Enforces DSN centralization:
#  - Only Python files are in scope.
#  - The ONLY file allowed to touch DSN env vars is: src/gemantria/dsn.py
#  - Everything else must call dsn_ro/dsn_rw/dsn_atlas from that module.
#  - Flags: direct os.getenv/os.environ with DSN keys, hardcoded postgres:// strings

ROOT="${ROOT:-$(git rev-parse --show-toplevel)}"
ALLOW="${ROOT}/scripts/guards/.dsn_direct.allowlist"

# Scope: Python files under src/ and scripts/ (skip tests/vendors if present)
mapfile -t CANDIDATES < <(
  git ls-files \
    | grep -E '^(src|scripts)/.*\.py$' \
    | grep -Ev '(^tests/|/vendor/|/site-packages/)'
)

SHIM="src/gemantria/dsn.py"

bad=()
for f in "${CANDIDATES[@]}"; do
  # The shim is allowed to access env directly; everyone else must not.
  if [[ "$f" == "$SHIM" ]]; then
    continue
  fi
  
  # Check for direct DSN env access (os.getenv/os.environ with DSN keys)
  if grep -E -n \
      -e 'os\.getenv\([^)]*["'\''](GEMATRIA_DSN|RW_DSN|AI_AUTOMATION_DSN|BIBLE_RO_DSN|RO_DSN|ATLAS_DSN|ATLAS_DSN_RW|ATLAS_DSN_RO|BIBLE_DB_DSN)' \
      -e 'os\.environ\[[^\]]*["'\''](GEMATRIA_DSN|RW_DSN|AI_AUTOMATION_DSN|BIBLE_RO_DSN|RO_DSN|ATLAS_DSN|ATLAS_DSN_RW|ATLAS_DSN_RO|BIBLE_DB_DSN)' \
      -e 'os\.environ\.get\([^)]*["'\''](GEMATRIA_DSN|RW_DSN|AI_AUTOMATION_DSN|BIBLE_RO_DSN|RO_DSN|ATLAS_DSN|ATLAS_DSN_RW|ATLAS_DSN_RO|BIBLE_DB_DSN)' \
      -- "$f" >/dev/null; then
    bad+=("$f")
    continue
  fi
  
  # Check for hardcoded postgres:// DSN strings (but allow comments and docstrings)
  if grep -E -n \
      -e 'postgres(ql)?://[^"'\''\s)]+' \
      -- "$f" | grep -vE '^\s*#|"""|'\'''\''|^[^:]*:.*#.*postgres' >/dev/null; then
    bad+=("$f")
    continue
  fi
done

# Apply allowlist if present
if [ -f "$ALLOW" ] && [ -s "$ALLOW" ]; then
  ALLOWED=()
  while IFS= read -r line; do
    # Skip comments and empty lines
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${line// }" ]] && continue
    # Extract file path (first word)
    ALLOWED+=("$(echo "$line" | awk '{print $1}')")
  done < "$ALLOW"
  
  # Filter out allowed files
  FILTERED=()
  for f in "${bad[@]}"; do
    ALLOWED_FLAG=0
    for a in "${ALLOWED[@]}"; do
      if [[ "$f" == "$a" ]] || [[ "$f" == *"$a"* ]]; then
        ALLOWED_FLAG=1
        break
      fi
    done
    [ "$ALLOWED_FLAG" = "0" ] && FILTERED+=("$f")
  done
  bad=("${FILTERED[@]}")
fi

if ((${#bad[@]})); then
  printf '{ "ok": false, "violations": %s }\n' "$(printf '%s\n' "${bad[@]}" | jq -R . | jq -s .)"
  exit 1
fi

printf '{ "ok": true, "violations": [] }\n'
exit 0
