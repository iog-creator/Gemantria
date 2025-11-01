#!/usr/bin/env bash

set -euo pipefail

: "${GEMATRIA_DSN:?GEMATRIA_DSN not set (e.g., postgres://user:pass@localhost:5432/gemantria)}"

psql "$GEMATRIA_DSN" -v ON_ERROR_STOP=1 -q -c "SELECT current_database();"

# Apply .sql files in lexical order
for f in $(ls -1 migrations/*.sql | sort); do
  echo "[migrate] applying $f"
  psql "$GEMATRIA_DSN" -v ON_ERROR_STOP=1 -q -f "$f"
done

echo "[migrate] done."
