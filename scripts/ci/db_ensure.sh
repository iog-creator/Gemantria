#!/usr/bin/env bash
set -euo pipefail
DB="${GEMANTRIA_DB:-gematria}"
USER="${PGUSER:-postgres}"
if command -v psql >/dev/null 2>&1; then
  if ! psql -U "$USER" -tAc "SELECT 1 FROM pg_database WHERE datname='${DB}'" | grep -q 1; then
    createdb -U "$USER" "$DB" || true
  fi
fi
