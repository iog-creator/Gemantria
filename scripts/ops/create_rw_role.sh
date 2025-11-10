#!/usr/bin/env bash
set -euo pipefail

# Create minimal-privilege read-write role for DDL operations
# Usage: ./scripts/ops/create_rw_role.sh [ATLAS_DSN_ADMIN]
#
# Requires: ATLAS_DSN_ADMIN (admin connection with CREATE ROLE privilege)
# Outputs: ATLAS_DSN_RW (read-write DSN for constrained DDL)

# Ensure we're in the virtual environment (required for psycopg)
if [ -z "${VIRTUAL_ENV:-}" ] && [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
    echo "✅ Activated virtual environment: ${VIRTUAL_ENV}"
fi

ATLAS_DSN_ADMIN="${1:-${ATLAS_DSN_ADMIN:-}}"

if [ -z "${ATLAS_DSN_ADMIN:-}" ]; then
  # Try to read from .env
  if [ -f .env ]; then
    ATLAS_DSN_ADMIN=$(grep "^ATLAS_DSN_ADMIN=" .env | head -n 1 | cut -d'=' -f2- | sed "s/^['\"]//;s/['\"]$//")
  fi
fi

if [ -z "${ATLAS_DSN_ADMIN:-}" ]; then
  echo "ERROR: ATLAS_DSN_ADMIN not set. Provide as argument or set in environment/.env"
  echo "       This script requires admin privileges to create roles."
  exit 1
fi

# Extract database name (handle both /dbname and /dbname?query formats)
DB_NAME=$(echo "${ATLAS_DSN_ADMIN}" | sed -n 's|.*://[^/]*/\([^?]*\).*|\1|p' | sed 's|/$||')
if [ -z "${DB_NAME}" ]; then
  DB_NAME="gematria"  # default
fi

RW_USER="gemantria_rw"
RW_PASSWORD=$(openssl rand -base64 32 2>/dev/null | tr -d "=+/" | cut -c1-25 || echo "changeme_$(date +%s)")

echo "Creating read-write role: ${RW_USER}"
echo "Database: ${DB_NAME}"
echo ""

# Verify admin connection
if ! psql "${ATLAS_DSN_ADMIN}" -c "SELECT 1" >/dev/null 2>&1; then
  echo "ERROR: Cannot connect to database with ATLAS_DSN_ADMIN"
  exit 1
fi

# Create role with minimal privileges
psql "${ATLAS_DSN_ADMIN}" <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${RW_USER}') THEN
    CREATE ROLE ${RW_USER} LOGIN PASSWORD '${RW_PASSWORD}' NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
  ELSE
    ALTER ROLE ${RW_USER} WITH PASSWORD '${RW_PASSWORD}';
  END IF;
END \$\$;

-- Database-level privileges
GRANT CONNECT ON DATABASE ${DB_NAME} TO ${RW_USER};

-- Schema-level privileges (gematria, telemetry, ops)
GRANT USAGE ON SCHEMA gematria TO ${RW_USER};
GRANT CREATE ON SCHEMA gematria TO ${RW_USER};

GRANT USAGE ON SCHEMA telemetry TO ${RW_USER};
GRANT CREATE ON SCHEMA telemetry TO ${RW_USER};

GRANT USAGE ON SCHEMA ops TO ${RW_USER};
GRANT CREATE ON SCHEMA ops TO ${RW_USER};

-- Table-level privileges (existing tables)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA gematria TO ${RW_USER};
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA telemetry TO ${RW_USER};
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ops TO ${RW_USER};

-- Sequence privileges (for SERIAL/BIGSERIAL columns)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA gematria TO ${RW_USER};
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA telemetry TO ${RW_USER};
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ops TO ${RW_USER};

-- Default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA gematria GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ${RW_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA telemetry GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ${RW_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA ops GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ${RW_USER};

ALTER DEFAULT PRIVILEGES IN SCHEMA gematria GRANT USAGE, SELECT ON SEQUENCES TO ${RW_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA telemetry GRANT USAGE, SELECT ON SEQUENCES TO ${RW_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA ops GRANT USAGE, SELECT ON SEQUENCES TO ${RW_USER};
SQL

echo "✅ Read-write role created successfully"
echo ""

# Construct ATLAS_DSN_RW - replace user with RW_USER and add password
# Handle DSNs with or without user:pass
if echo "${ATLAS_DSN_ADMIN}" | grep -q "://[^:]*:[^@]*@"; then
  # Has user:pass, replace user and password
  ATLAS_DSN_RW=$(echo "${ATLAS_DSN_ADMIN}" | sed "s|://[^:]*:[^@]*@|://${RW_USER}:${RW_PASSWORD}@|")
elif echo "${ATLAS_DSN_ADMIN}" | grep -q "://[^/@]*@"; then
  # Has user but no password, replace user and add password
  ATLAS_DSN_RW=$(echo "${ATLAS_DSN_ADMIN}" | sed "s|://[^/@]*@|://${RW_USER}:${RW_PASSWORD}@|")
else
  # No user, add user:pass
  ATLAS_DSN_RW=$(echo "${ATLAS_DSN_ADMIN}" | sed "s|://|://${RW_USER}:${RW_PASSWORD}@|")
fi

echo "Add to .env:"
echo "ATLAS_DSN_RW='${ATLAS_DSN_RW}'"
echo ""
echo "Or export for current session:"
echo "export ATLAS_DSN_RW='${ATLAS_DSN_RW}'"
echo ""
echo "To test (verify privileges):"
echo "psql \"${ATLAS_DSN_RW}\" -c \"SELECT current_user, current_database()\""
echo "psql \"${ATLAS_DSN_RW}\" -c \"SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('gematria','telemetry','ops')\""
echo ""
echo "⚠️  SECURITY: Never commit ATLAS_DSN_RW to version control"
echo "⚠️  SECURITY: This role has DDL privileges on gematria/telemetry/ops schemas only"

