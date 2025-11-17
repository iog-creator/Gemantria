# Control Tables Runbook

## Purpose

The `pmagent control tables` command provides a schema-qualified list of all tables across Postgres schemas, with row counts when the database is available. It helps operators understand the database structure and data volume without requiring direct database access.

## Quick Start

### CLI Usage (Primary Interface)

The `pmagent` CLI is the primary interface for control-plane operations:

```bash
# List all tables with row counts
pmagent control tables

# Or using Python module directly
python -m pmagent.cli control tables
```

### Make Target (Convenience Wrapper)

The Make target is a thin wrapper around `pmagent`:

```bash
make control.tables.smoke
```

Both methods output:
- **JSON** to stdout (machine-friendly)
- **Human-readable summary** to stderr

## Example Outputs

### DB-Off Example

When the database is unavailable (driver missing, connection failed, etc.):

```json
{
  "ok": false,
  "mode": "db_off",
  "error": "Postgres database driver not available",
  "tables": {}
}
```

```
CONTROL_TABLES: mode=db_off (Postgres database driver not available)
```

### DB-On Example (With Tables)

When the database is ready and tables are populated:

```json
{
  "ok": true,
  "mode": "db_on",
  "error": null,
  "tables": {
    "public.ai_interactions": 42,
    "public.governance_artifacts": 15,
    "control.agent_run": 8,
    "control.tool_catalog": 5,
    "control.capability_rule": 3,
    "gematria.graph_stats_snapshots": 3,
    "gematria.concepts": 100,
    "gematria.concept_relations": 200
  }
}
```

```
CONTROL_TABLES: mode=db_on tables=8 schemas=control(3),gematria(3),public(2)
```

### Partial Query Failure Example

When some tables exist but row count queries fail:

```json
{
  "ok": true,
  "mode": "db_on",
  "error": null,
  "tables": {
    "public.ai_interactions": 10,
    "public.governance_artifacts": null,
    "control.agent_run": 5
  }
}
```

```
CONTROL_TABLES: mode=db_on tables=3 schemas=control(1),public(2)
```

**Note**: A `null` value for a table's row count indicates the COUNT query failed (e.g., permission denied, table locked, or other query error). The table exists but the count could not be retrieved.

## Interpreting Results

### Status Fields

- **`ok`**: `true` if database is ready and queries succeeded; `false` if database is unavailable
- **`mode`**: Database posture:
  - `"db_on"`: Database is available and queries succeeded
  - `"db_off"`: Database driver missing or connection failed
- **`error`**: Human-readable error message (null if ok)

### Tables Dictionary

The `tables` dictionary maps fully-qualified table names (`schema.table`) to row counts:

- **Integer value**: Number of rows in the table
- **`null`**: Table exists but row count query failed (permission denied, query error, etc.)

### Schema Summary

The human-readable summary includes:
- **`tables=N`**: Total number of tables found
- **`schemas=...`**: Comma-separated list of schemas with table counts (e.g., `control(3),gematria(3),public(2)`)

## JSON-Only Output

For machine-readable output only (no human summary):

```bash
pmagent control tables --json-only
```

This outputs only JSON to stdout, with no summary to stderr.

## Troubleshooting

### Database is Off

If `mode=db_off`:

1. **Check database driver**: Ensure `psycopg3` is installed
   ```bash
   pip install psycopg[binary]
   ```

2. **Check DSN configuration**: Verify `GEMATRIA_DSN` is set
   ```bash
   make dsns.echo
   ```

3. **Check database connection**: Use `pmagent health db` to diagnose connection issues
   ```bash
   pmagent health db
   ```

4. **Refer to**: [DB_HEALTH.md](DB_HEALTH.md) for detailed database health troubleshooting

### Null Row Counts

If some tables show `null` row counts:

1. **Check permissions**: Ensure the database user has SELECT permission on the tables
2. **Check table locks**: Tables might be locked by other transactions
3. **Check table state**: Tables might be in an inconsistent state
4. **Review error logs**: Check database logs for query errors

**Note**: A `null` count does not indicate the table is missing—it means the COUNT query failed. The table exists but the count could not be retrieved.

### Empty Tables Dictionary

If `tables: {}`:

- **Database has no tables**: This is normal for a fresh database installation
- **Schema filter**: The query excludes `pg_catalog` and `information_schema` tables
- **Permission issue**: The database user might not have access to `information_schema.tables`

## Related Commands

- **`pmagent control status`**: Check control-plane database status and specific table row counts
- **`pmagent health db`**: Detailed database health check
- **`pmagent health system`**: Aggregate system health (DB + LM + Graph)

## Related Documentation

- [CONTROL_STATUS.md](CONTROL_STATUS.md): Control-plane status check
- [DB_HEALTH.md](DB_HEALTH.md): Database health troubleshooting
- [SYSTEM_HEALTH.md](SYSTEM_HEALTH.md): System health aggregation

## Implementation Details

- **Script**: `scripts/control/control_tables.py`
- **CLI Command**: `pmagent control tables`
- **Make Target**: `make control.tables.smoke`
- **Tests**: `agentpm/tests/cli/test_phase3b_pmagent_control_tables_cli.py`

The command uses the centralized DB loader (`agentpm.db.loader`) and reuses the DB health check logic (`scripts.guards.guard_db_health`) to ensure consistent behavior with other health commands.

**Schema Filtering**: The query excludes system schemas (`pg_catalog`, `information_schema`) to focus on application tables. All base tables in other schemas are included.

