#!/usr/bin/env bash
set -euo pipefail

# Create read-only role and set ATLAS_DSN
# Usage: ./scripts/ops/create_ro_dsn.sh [GEMATRIA_DSN]

# Ensure we're in the virtual environment (required for psycopg)
if [ -z "${VIRTUAL_ENV:-}" ] && [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
    echo "✅ Activated virtual environment: ${VIRTUAL_ENV}"
fi

GEMATRIA_DSN="${1:-${GEMATRIA_DSN:-}}"

if [ -z "${GEMATRIA_DSN:-}" ]; then
  # Try to read from .env
  if [ -f .env ]; then
    GEMATRIA_DSN=$(grep "^GEMATRIA_DSN=" .env | head -n 1 | cut -d'=' -f2- | sed "s/^['\"]//;s/['\"]$//")
  fi
fi

if [ -z "${GEMATRIA_DSN:-}" ]; then
  echo "ERROR: GEMATRIA_DSN not set. Provide as argument or set in environment/.env"
  exit 1
fi

# Extract database name (handle both /dbname and /dbname?query formats)
DB_NAME=$(echo "${GEMATRIA_DSN}" | sed -n 's|.*://[^/]*/\([^?]*\).*|\1|p' | sed 's|/$||')
if [ -z "${DB_NAME}" ]; then
  DB_NAME="gematria"  # default
fi

RO_USER="gemantria_ro"
RO_PASSWORD=$(openssl rand -base64 32 2>/dev/null | tr -d "=+/" | cut -c1-25 || echo "changeme_$(date +%s)")

echo "Creating read-only role: ${RO_USER}"
echo "Database: ${DB_NAME}"
echo ""

# Try to create the role (may fail if DB not running - that's OK, we'll still output the DSN)
if psql "${GEMATRIA_DSN}" -c "SELECT 1" >/dev/null 2>&1; then
  psql "${GEMATRIA_DSN}" <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${RO_USER}') THEN
    CREATE ROLE ${RO_USER} LOGIN PASSWORD '${RO_PASSWORD}' NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
  ELSE
    ALTER ROLE ${RO_USER} WITH PASSWORD '${RO_PASSWORD}';
  END IF;
END \$\$;

GRANT CONNECT ON DATABASE ${DB_NAME} TO ${RO_USER};
GRANT USAGE ON SCHEMA public TO ${RO_USER};
GRANT USAGE ON SCHEMA gematria TO ${RO_USER};
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ${RO_USER};
GRANT SELECT ON ALL TABLES IN SCHEMA gematria TO ${RO_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO ${RO_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA gematria GRANT SELECT ON TABLES TO ${RO_USER};
SQL
  echo "✅ Read-only role created successfully"
else
  echo "⚠️  Cannot connect to database (may not be running)"
  echo "   Role will be created when database is available"
  echo "   Use this DSN once database is ready:"
fi

# Construct ATLAS_DSN - replace user with RO_USER and add password
# Handle DSNs with or without user:pass
if echo "${GEMATRIA_DSN}" | grep -q "://[^:]*:[^@]*@"; then
  # Has user:pass, replace user and password
  ATLAS_DSN=$(echo "${GEMATRIA_DSN}" | sed "s|://[^:]*:[^@]*@|://${RO_USER}:${RO_PASSWORD}@|")
elif echo "${GEMATRIA_DSN}" | grep -q "://[^/@]*@"; then
  # Has user but no password, replace user and add password
  ATLAS_DSN=$(echo "${GEMATRIA_DSN}" | sed "s|://[^/@]*@|://${RO_USER}:${RO_PASSWORD}@|")
else
  # No user, add user:pass
  ATLAS_DSN=$(echo "${GEMATRIA_DSN}" | sed "s|://|://${RO_USER}:${RO_PASSWORD}@|")
fi

echo ""
echo "Add to .env:"
echo "ATLAS_DSN='${ATLAS_DSN}'"
echo ""
echo "Or export for current session:"
echo "export ATLAS_DSN='${ATLAS_DSN}'"
echo ""
echo "To test (once DB is running):"
echo "psql \"${ATLAS_DSN}\" -c \"SELECT current_user, current_database()\""
