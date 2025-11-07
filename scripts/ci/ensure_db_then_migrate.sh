#!/usr/bin/env bash
set -euo pipefail
emit() { if [ -x scripts/hint.sh ]; then scripts/hint.sh "$*"; else echo "HINT: $*"; fi; }

# Rule-043 (CI DB Bootstrap & Empty-Data Handling) - Any workflow that queries DB must create DB + run all migrations first
# scripts/ci/ensure_db_then_migrate.sh - Database bootstrap script for CI
echo "🔥🔥🔥 LOUD HINT: Rule-043 (CI DB Bootstrap & Empty-Data Handling) - Any workflow that queries DB must create DB + run all migrations first 🔥🔥🔥"
echo "🔥🔥🔥 LOUD HINT: scripts/ci/ensure_db_then_migrate.sh - Database bootstrap script for CI 🔥🔥🔥"

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

emit "verify: target_db=$target_db"
emit "verify: admin_dsn derived for bootstrap"

# Create database if missing
if ! psql "$admin_dsn" -tAc "SELECT 1 FROM pg_database WHERE datname='${target_db}'" | grep -q 1; then
  emit "verify: creating database '${target_db}'"
  psql "$admin_dsn" -c "CREATE DATABASE ${target_db};" || {
    echo "[ensure_db_then_migrate] failed to create database via psql, trying createdb..."
    # Fallback: try createdb with environment variables
    export PGHOST="${PGHOST:-localhost}"
    export PGPORT="${PGPORT:-5432}"
    export PGUSER="${PGUSER:-postgres}"
    createdb "${target_db}" || true
  }
fi

# Ensure vector extension and run migrations inside the target DB
emit "verify: ensuring extension 'vector'"
psql "$dsn" -v ON_ERROR_STOP=1 -c "CREATE EXTENSION IF NOT EXISTS vector;"

emit "verify: applying migrations from migrations/*.sql"
shopt -s nullglob
for f in migrations/*.sql; do
  emit "verify: applying $f"
  psql "$dsn" -v ON_ERROR_STOP=1 -f "$f"
done

emit "verify: database bootstrap OK"
