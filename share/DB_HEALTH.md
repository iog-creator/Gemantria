# DB Health Runbook

## Purpose

This runbook explains how to check database health posture and interpret the results. The DB health check verifies driver availability, database connectivity, and table readiness.

## Quick Start

### CLI Usage (Primary Interface)

The `pmagent` CLI is the primary interface for health checks:

```bash
# Check DB health
pmagent health db

# Or using Python module directly
python -m pmagent.cli health db
```

### Make Target (Convenience Wrapper)

The Make target is a thin wrapper around `pmagent`:

```bash
make db.health.smoke
```

Both methods output:
- **JSON** to stdout (machine-friendly)
- **Human-readable summary** to stderr

Example output:
```
DB_HEALTH: mode=ready (all checks passed)
```

## DB Health Modes

The DB health check reports one of three modes:

### `ready` - All Systems Operational

**Meaning**: Database driver is installed, connection works, and required tables are accessible.

**What it checks**:
- ✅ Postgres driver (psycopg/psycopg2) is available
- ✅ Control database (GEMATRIA_DSN) is reachable
- ✅ `gematria.graph_stats_snapshots` table exists and is queryable

**Next steps**: You're ready to use database-backed features. Proceed with normal operations.

### `db_off` - Database Unavailable

**Meaning**: Database driver is missing or connection cannot be established.

**Common reasons**:
- **Driver not installed**: Postgres driver (psycopg/psycopg2) is not in the Python environment
- **Connection failed**: Database server is not running or DSN is incorrect
- **DSN not set**: `GEMATRIA_DSN` environment variable is not configured

**Next steps**:
1. **If driver missing**: Install the Postgres driver:
   ```bash
   pip install psycopg[binary,pool]~=3.2
   # OR
   pip install psycopg2-binary>=2.9
   ```
2. **If connection failed**: 
   - Verify database server is running: `pg_isready` or `systemctl status postgresql`
   - Check DSN configuration in `.env.local` or `.env`:
     ```bash
     make dsns.echo  # Prints redacted DSNs for verification
     ```
   - Ensure `GEMATRIA_DSN` points to a valid database
3. **If DSN not set**: Configure database connection:
   ```bash
   # Create .env.local with:
   GEMATRIA_DSN=postgresql://user:pass@host:port/gematria
   ```

### `partial` - Database Connected but Tables Missing

**Meaning**: Database driver and connection work, but required tables are not present.

**Common reasons**:
- **Table missing**: `gematria.graph_stats_snapshots` table has not been created
- **Schema not initialized**: Database migrations have not been run

**Next steps**:
1. **Run migrations**: Apply database schema migrations to create required tables
2. **Import graph stats**: If using the graph stats importer, ensure the table exists:
   ```bash
   # Check if table exists
   psql "$GEMATRIA_DSN" -c "SELECT 1 FROM gematria.graph_stats_snapshots LIMIT 1;"
   ```
3. **Verify schema**: Ensure the `gematria` schema exists and is accessible

## Detailed Health Check

For detailed JSON output, run the guard directly:

```bash
make guard.db.health
```

This outputs structured JSON with:
- `ok`: Boolean indicating overall health
- `mode`: One of `ready`, `db_off`, `partial`
- `checks`: Individual check results (driver, connection, table)
- `details.errors`: List of error messages if any checks failed

Example output:
```json
{
  "ok": true,
  "mode": "ready",
  "checks": {
    "driver_available": true,
    "connection_ok": true,
    "graph_stats_ready": true
  },
  "details": {
    "errors": []
  }
}
```

## Integration with Other Tools

### PM Snapshot

The DB health check is automatically included in PM snapshots:

```bash
make pm.snapshot
```

The snapshot includes a "DB Health Guard" section with status and JSON output.

### Bring-up Script

The bring-up script (`make bringup.001`) runs DB health check as part of Step 4a and saves results to `evidence/bringup_001/db_health.json`.

## Troubleshooting

### "driver_missing" Error

**Problem**: Postgres driver is not installed.

**Solution**:
```bash
# Check if driver is installed
python3 -c "import psycopg; print('psycopg OK')" || python3 -c "import psycopg2; print('psycopg2 OK')"

# Install driver
pip install psycopg[binary,pool]~=3.2
```

### "connection_failed" Error

**Problem**: Cannot connect to database.

**Solution**:
1. Verify database server is running
2. Check DSN configuration: `make dsns.echo`
3. Test connection manually: `psql "$GEMATRIA_DSN" -c "SELECT 1;"`
4. Check firewall/network settings if connecting to remote database

### "graph_stats_table_missing" Error

**Problem**: Required table does not exist.

**Solution**:
1. Run database migrations to create schema
2. Verify schema exists: `psql "$GEMATRIA_DSN" -c "\dn gematria"`
3. Create table manually if needed (see migration scripts)

## Related Documentation

- **Phase-3A Implementation**: See `AGENTS.md` for Phase-3A DB activation details
- **DSN Configuration**: See `docs/runbooks/DSN_SECRETS.md` for DSN management
- **Database Architecture**: See `docs/ADRs/ADR-001-database-architecture.md` for DB design

## Make Targets

- `make db.health.smoke` - Quick health check with summary output
- `make guard.db.health` - Detailed JSON health check
- `make snapshot.db.health.smoke` - Verify DB health integration in snapshot
- `make test.phase3a.db.health` - Run DB health guard tests

