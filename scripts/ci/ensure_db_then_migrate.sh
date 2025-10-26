#!/usr/bin/env bash
set -euo pipefail

# Expects: GEMATRIA_DSN (e.g., postgresql://postgres@localhost:5432/gematria)
# Requires: psql, createdb

if [ -z "${GEMATRIA_DSN:-}" ]; then
  echo "[ensure_db_then_migrate] ERROR: GEMATRIA_DSN is not set"
  exit 1
fi

dsn="$GEMATRIA_DSN"

# Extract components for an admin connection to 'postgres' DB to create target DB if needed.
# We do a simple replacement of '/<dbname>' with '/postgres' to get an admin DSN.
admin_dsn="$(printf '%s' "$dsn" | sed -E 's#(/)[^/?]+(\?|$)#\1postgres\2#')"

# Derive target database name from DSN (path segment after last '/')
target_db="$(printf '%s' "$dsn" | sed -E 's#.*/([^/?]+)(\?.*)?$#\1#')"

echo "[ensure_db_then_migrate] target_db=$target_db"
echo "[ensure_db_then_migrate] admin_dsn=$admin_dsn"

# Create database if missing
if ! psql "$admin_dsn" -tAc "SELECT 1 FROM pg_database WHERE datname='${target_db}'" | grep -q 1; then
  echo "[ensure_db_then_migrate] creating database '${target_db}' ..."
  createdb "${target_db}" -d "$admin_dsn" || createdb -U "${PGUSER:-postgres}" "${target_db}" || true
fi

# Ensure vector extension and run migrations inside the target DB
echo "[ensure_db_then_migrate] ensuring vector extension ..."
psql "$dsn" -v ON_ERROR_STOP=1 -c "CREATE EXTENSION IF NOT EXISTS vector;"

echo "[ensure_db_then_migrate] applying migrations ..."
shopt -s nullglob
for f in migrations/*.sql; do
  echo "[ensure_db_then_migrate] applying $f"
  psql "$dsn" -v ON_ERROR_STOP=1 -f "$f"
done

echo "[ensure_db_then_migrate] OK"
