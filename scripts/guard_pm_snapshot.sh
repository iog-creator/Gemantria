#!/usr/bin/env bash
set -euo pipefail
SNAPSHOT_PATH="${1:-share/pm.snapshot.md}"
STRICT="${STRICT_PM_SNAPSHOT:-0}"

if [ ! -f "$SNAPSHOT_PATH" ]; then
  echo "FAIL: snapshot missing: $SNAPSHOT_PATH"
  exit 3
fi

# Always print quick posture for evidence
echo "SNAPSHOT_PATH=$SNAPSHOT_PATH"
grep -nE '^## Posture \(DSNs \+ STRICT flags\)|^-\s*(BIBLE_DB_DSN|GEMATRIA_DSN|CHECKPOINTER|ENFORCE_STRICT):' "$SNAPSHOT_PATH" || true

if [ "${STRICT}" = "1" ]; then
  # In STRICT, DSNs must not be '(unset)'. Fail if unset appears for either DB.
  if grep -qE 'BIBLE_DB_DSN:\s*\(unset\)|GEMATRIA_DSN:\s*\(unset\)' "$SNAPSHOT_PATH"; then
    echo "FAIL: STRICT tag build requires DSNs present; found '(unset)' in PM snapshot."
    exit 4
  fi
fi
echo "GUARD_OK"

