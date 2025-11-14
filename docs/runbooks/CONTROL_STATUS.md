# Control Status Runbook

## Purpose

The `pmagent control status` command provides a quick overview of the control-plane database posture and basic row counts for key tables. It helps operators understand the state of the control-plane infrastructure without requiring direct database access.

## Quick Start

### CLI Usage (Primary Interface)

The `pmagent` CLI is the primary interface for control-plane operations:

```bash
# Check control-plane status
pmagent control status

# Or using Python module directly
python -m pmagent.cli control status
```

### Make Target (Convenience Wrapper)

The Make target is a thin wrapper around `pmagent`:

```bash
make control.status.smoke
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
  "reason": "Postgres database driver not available",
  "tables": {
    "public.ai_interactions": {
      "present": false,
      "row_count": null,
      "latest_created_at": null
    },
    "public.governance_artifacts": {
      "present": false,
      "row_count": null,
      "latest_created_at": null
    },
    "control.agent_run": {
      "present": false,
      "row_count": null,
      "latest_created_at": null
    },
    "control.tool_catalog": {
      "present": false,
      "row_count": null,
      "latest_created_at": null
    },
    "gematria.graph_stats_snapshots": {
      "present": false,
      "row_count": null,
      "latest_created_at": null
    }
  }
}
```

```
CONTROL_STATUS: mode=db_off (Postgres database driver not available)
```

### Ready Example (With Tables)

When the database is ready and tables are populated:

```json
{
  "ok": true,
  "mode": "ready",
  "reason": null,
  "tables": {
    "public.ai_interactions": {
      "present": true,
      "row_count": 42,
      "latest_created_at": "2024-01-15T10:30:00+00:00"
    },
    "public.governance_artifacts": {
      "present": true,
      "row_count": 15,
      "latest_created_at": "2024-01-15T09:00:00+00:00"
    },
    "control.agent_run": {
      "present": true,
      "row_count": 8,
      "latest_created_at": null
    },
    "control.tool_catalog": {
      "present": true,
      "row_count": 5,
      "latest_created_at": "2024-01-14T12:00:00+00:00"
    },
    "gematria.graph_stats_snapshots": {
      "present": true,
      "row_count": 3,
      "latest_created_at": "2024-01-15T11:00:00+00:00"
    }
  }
}
```

```
CONTROL_STATUS: mode=ready tables=ai_interactions(42),governance_artifacts(15),agent_run(8),tool_catalog(5),graph_stats_snapshots(3)
```

### Partial Schema Example

When some tables exist but others are missing:

```json
{
  "ok": true,
  "mode": "ready",
  "reason": null,
  "tables": {
    "public.ai_interactions": {
      "present": true,
      "row_count": 10,
      "latest_created_at": "2024-01-15T10:30:00+00:00"
    },
    "public.governance_artifacts": {
      "present": false,
      "row_count": null,
      "latest_created_at": null
    },
    "control.agent_run": {
      "present": true,
      "row_count": 5,
      "latest_created_at": null
    },
    "control.tool_catalog": {
      "present": false,
      "row_count": null,
      "latest_created_at": null
    },
    "gematria.graph_stats_snapshots": {
      "present": true,
      "row_count": 2,
      "latest_created_at": "2024-01-15T11:00:00+00:00"
    }
  }
}
```

```
CONTROL_STATUS: mode=ready tables=ai_interactions(10),agent_run(5),graph_stats_snapshots(2)
```

## Interpreting Results

### Status Fields

- **`ok`**: `true` if database is ready and queries succeeded; `false` if database is unavailable or queries failed
- **`mode`**: Database posture:
  - `"ready"`: Database is available and queries succeeded
  - `"db_off"`: Database driver missing or connection failed
  - `"partial"`: Database available but some queries failed (rare)
- **`reason`**: Human-readable explanation of the status (null if ok)

### Table Fields

For each table in the `tables` dictionary:

- **`present`**: `true` if the table exists in the database; `false` if it doesn't exist
- **`row_count`**: Number of rows in the table (integer), or `null` if table doesn't exist or query failed
- **`latest_created_at`**: ISO 8601 timestamp of the most recent row's `created_at` column, or `null` if:
  - Table doesn't exist
  - Table has no rows
  - Table doesn't have a `created_at` column
  - Query failed

### Monitored Tables

The command inspects these control-plane tables:

1. **`public.ai_interactions`**: AI interaction tracking (Rule-061)
2. **`public.governance_artifacts`**: Governance artifacts tracking (Rule-026, Rule-058)
3. **`control.agent_run`**: Agent run audit log (Migration 040)
4. **`control.tool_catalog`**: Tool catalog (Migration 040)
5. **`gematria.graph_stats_snapshots`**: Graph statistics snapshots (Phase-3A)

## JSON-Only Output

For machine-readable output only (no human summary):

```bash
pmagent control status --json-only
```

This outputs only JSON to stdout, with no summary to stderr.

## Troubleshooting

### Database is Off

If `mode=db_off`:

1. **Check database driver**: Ensure `psycopg` or `psycopg2` is installed
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

### Tables Missing

If some tables show `"present": false`:

1. **Check migrations**: Ensure all migrations have been applied
   ```bash
   # Check migration status (if available)
   psql "$GEMATRIA_DSN" -c "SELECT version FROM schema_migrations ORDER BY version;"
   ```

2. **Apply missing migrations**: Run migrations if needed
   ```bash
   # Apply migrations (if script available)
   make db.migrate
   ```

3. **Check schema**: Verify table names match expected schema
   - `public.ai_interactions` (Migration 016)
   - `public.governance_artifacts` (Migration 015)
   - `control.agent_run` (Migration 040)
   - `control.tool_catalog` (Migration 040)
   - `gematria.graph_stats_snapshots` (Phase-3A model)

### Empty Tables

If tables are present but have `row_count: 0`:

- This is normal for new installations or after data cleanup
- Import data as needed:
  - Graph stats: `pmagent graph import`
  - AI interactions: Populated automatically during agent operations
  - Governance artifacts: Populated during `make housekeeping`

## Related Commands

- **`pmagent health db`**: Detailed database health check
- **`pmagent health system`**: Aggregate system health (DB + LM + Graph)
- **`pmagent graph overview`**: Graph statistics overview
- **`pmagent graph import`**: Import graph statistics into database

## Related Documentation

- [DB_HEALTH.md](DB_HEALTH.md): Database health troubleshooting
- [SYSTEM_HEALTH.md](SYSTEM_HEALTH.md): System health aggregation
- [GRAPH_IMPORT.md](GRAPH_IMPORT.md): Graph statistics import
- [GRAPH_OVERVIEW.md](GRAPH_OVERVIEW.md): Graph statistics overview

## Implementation Details

- **Script**: `scripts/control/control_status.py`
- **CLI Command**: `pmagent control status`
- **Make Target**: `make control.status.smoke`
- **Tests**: `agentpm/tests/cli/test_phase3b_pmagent_control_status_cli.py`

The command uses the centralized DB loader (`agentpm.db.loader`) and reuses the DB health check logic (`scripts.guards.guard_db_health`) to ensure consistent behavior with other health commands.

