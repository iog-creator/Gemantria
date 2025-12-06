# HINT: Database Not Running - Critical Blocker

## Problem Detection

**Symptoms**:
- Connection errors: `No such file or directory` for `/var/run/postgresql/.s.PGSQL.5432`
- Error: `Is the server running locally and accepting connections on that socket?`
- `make reality.green` fails with "Database is unreachable (db_off)"
- `make share.sync` fails with registry sync error
- `make state.verify` fails with DB connection error

**Root Cause**: PostgreSQL database server is not running. The database is the Single Source of Truth (SSOT) for this project and is **required** for all governance operations.

## Exact Fix

### 1. Check PostgreSQL Status

```bash
# Check if PostgreSQL is running
systemctl status postgresql

# Alternative check
pg_isready -h /var/run/postgresql
```

### 2. Start PostgreSQL

```bash
# Start PostgreSQL service
sudo systemctl start postgresql

# Enable to start on boot
sudo systemctl enable postgresql

# Verify it's running
systemctl status postgresql
```

### 3. Verify Database Connectivity

```bash
# Activate venv and load environment
source .venv/bin/activate
set -a
source .env
set +a

# Test GEMATRIA_DSN connection
psql "$GEMATRIA_DSN" -c "SELECT current_database(), version();"

# Test BIBLE_DB_DSN connection
psql "$BIBLE_DB_DSN" -c "SELECT current_database();"
```

### 4. Re-run Failed Commands

After PostgreSQL is running:

```bash
# Re-run the governance checks
make reality.green

# Re-sync share exports
make share.sync

# Verify state ledger
make state.verify
```

## Why This Matters

**Governance Rules Violated** when DB is offline:

- **DB is SSOT**: All gematria data, document registry, embeddings, and governance state live in PostgreSQL
- **Rule-050/051/052**: DB access is a hard requirement, not optional
- **Rule-066**: LLM Subordination - DB is authoritative, not code or assumptions
- **Rule-069**: DMS-First workflow requires DB for all document operations
- **Phase 16**: Registry reconciliation cannot proceed without DB
- **Phase 17**: SSOT surface regeneration requires DB access

**Impact of proceeding without DB**:
- ❌ Cannot validate registry state
- ❌ Cannot sync SSOT documents to share/
- ❌ Cannot verify embeddings or governance state
- ❌ Cannot run housekeeping or regenerate KB
- ❌ **Phase 17 is BLOCKED** until DB is available

## Correct Agent Behavior

### ❌ WRONG (Proceeding despite DB being offline)
```python
# DO NOT DO THIS
try:
    db.connect()
except Exception:
    print("WARNING: DB offline, continuing anyway...")
    # Proceeds with incomplete/invalid work
```

### ✅ CORRECT (Stop immediately and emit hint)
```python
try:
    db.connect()
except Exception as e:
    print("❌ CRITICAL: Database is unreachable")
    print(f"Error: {e}")
    print("See: docs/hints/HINT-DB-002-postgres-not-running.md")
    print("\nRequired actions:")
    print("1. Start PostgreSQL: sudo systemctl start postgresql")
    print("2. Verify connection: pg_isready -h /var/run/postgresql")
    print("3. Re-run this command")
    sys.exit(1)
```

## When to Apply This Hint

Trigger this hint when:
- Any command fails with `/var/run/postgresql/.s.PGSQL.5432` error
- `make reality.green` reports "Database is unreachable"
- `make share.sync` fails with registry sync error
- Any `psql` command fails to connect
- **Before starting Phase 17** (DB is required for SSOT surface generation)

**Do NOT proceed with**:
- "Skipping DB checks for now"
- "Will fix DB later"
- "Continuing with file-only operations"
- Any work that requires registry, embeddings, or governance state

**Always STOP, start PostgreSQL, then continue.**

## Database Architecture (Quick Reference)

### Single Database: `gematria`

As of Phase 14, there is **one unified database**: `gematria`

**Schemas**:
- `public` - Bible text, verse data, gematria calculations
- `control` - Document registry, governance, hints, ledger
- `bible_db` - Legacy schema (read-only, being phased out)

**Key Tables**:
- `control.doc_registry` - DMS document registry (SSOT for all docs)
- `control.embedding_index` - Vector embeddings for semantic search
- `control.hint_registry` - Governance hints and rules
- `public.gematria_calculation` - Gematria values per verse/word
- `public.verse` - Bible verse text and metadata

### DSN Configuration

Both DSN variables point to the same database:

```bash
# In .env
GEMATRIA_DSN="postgresql://mccoy@/gematria?host=/var/run/postgresql"
BIBLE_DB_DSN="postgresql://mccoy@/gematria?host=/var/run/postgresql"
```

Note: `BIBLE_DB_DSN` is legacy naming; both connect to `gematria` database.

## Related Documentation

- [`docs/hints/HINT-DB-001-dsn-mandatory.md`](file:///home/mccoy/Projects/Gemantria.v2/docs/hints/HINT-DB-001-dsn-mandatory.md) - DSN requirements
- [`docs/hints/HINT-ENV-001-venv-not-activated.md`](file:///home/mccoy/Projects/Gemantria.v2/docs/hints/HINT-ENV-001-venv-not-activated.md) - Environment setup
- [`docs/runbooks/DB_HEALTH.md`](file:///home/mccoy/Projects/Gemantria.v2/docs/runbooks/DB_HEALTH.md) - Database health checks
- `AGENTS.md` - DB-First architecture section
