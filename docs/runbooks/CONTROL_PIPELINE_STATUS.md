# Control Pipeline Status Runbook

## Purpose

The `pmagent control pipeline-status` command provides a summary of recent pipeline runs from the `control.agent_run` table. It helps operators and developers understand pipeline execution patterns, success/failure rates, and recent activity without requiring direct database access or complex SQL queries.

## Quick Start

### CLI Usage (Primary Interface)

The `pmagent` CLI is the primary interface for control-plane operations:

```bash
# Summarize pipeline runs from last 24 hours (default)
pmagent control pipeline-status

# Custom time window (e.g., last 48 hours)
pmagent control pipeline-status --window-hours 48

# Or using Python module directly
python -m pmagent.cli control pipeline-status
```

### Make Target (Convenience Wrapper)

The Make target is a thin wrapper around `pmagent`:

```bash
make control.pipeline_status.smoke
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
  "window_hours": 24,
  "summary": {
    "total_runs": 0,
    "pipelines": {}
  }
}
```

```
CONTROL_PIPELINE_STATUS: mode=db_off window_hours=24 (Postgres database driver not available)
```

**Note:** DB-off output is expected in CI and acceptable per Rule-046 (Hermetic CI Fallbacks). The command behaves hermetically and does not crash when the database is unavailable.

### DB-On Example (Snippet)

When the database is ready and pipeline runs are present:

```json
{
  "ok": true,
  "mode": "db_on",
  "reason": null,
  "window_hours": 24,
  "summary": {
    "total_runs": 15,
    "pipelines": {
      "graph_builder": {
        "total": 8,
        "by_status": {
          "success": 6,
          "failed": 2,
          "running": 0,
          "other": 0
        },
        "last_run_started_at": "2024-01-15T14:30:00+00:00",
        "last_run_status": "success"
      },
      "noun_extractor": {
        "total": 5,
        "by_status": {
          "success": 5,
          "failed": 0,
          "running": 0,
          "other": 0
        },
        "last_run_started_at": "2024-01-15T13:15:00+00:00",
        "last_run_status": "success"
      },
      "enrichment": {
        "total": 2,
        "by_status": {
          "success": 1,
          "failed": 1,
          "running": 0,
          "other": 0
        },
        "last_run_started_at": "2024-01-15T12:00:00+00:00",
        "last_run_status": "failed"
      }
    }
  }
}
```

```
CONTROL_PIPELINE_STATUS: mode=db_on window_hours=24 total_runs=15 pipelines=graph_builder(8:6s/2f),noun_extractor(5:5s/0f),enrichment(2:1s/1f)
```

## Interpreting Results

### Status Fields

- **`ok`**: `true` if database is ready and queries succeeded; `false` if database is unavailable or queries failed.
- **`mode`**: Database posture:
  - `"db_on"`: Database is available and queries succeeded.
  - `"db_off"`: Database driver missing or connection failed.
- **`reason`**: Human-readable explanation of the status (null if ok).
- **`window_hours`**: Time window in hours used for the query (default: 24).

### Summary Fields

- **`total_runs`**: Total number of pipeline runs in the time window across all pipelines.
- **`pipelines`**: Dictionary mapping pipeline names (from `tool` column) to pipeline statistics.

### Pipeline Statistics

For each pipeline in the `pipelines` dictionary:

- **`total`**: Total number of runs for this pipeline in the time window.
- **`by_status`**: Breakdown by status:
  - **`success`**: Runs with no violations (empty `violations_json`).
  - **`failed`**: Runs with violations (non-empty `violations_json`).
  - **`running`**: Currently not implemented (always 0).
  - **`other`**: Runs that don't fit into success/failed categories.
- **`last_run_started_at`**: RFC3339 timestamp of the most recent run for this pipeline (or `null` if no runs).
- **`last_run_status`**: Status of the most recent run (`"success"`, `"failed"`, or `null`).

### Status Determination

Pipeline run status is determined from the `violations_json` column in `control.agent_run`:

- **Success**: `violations_json` is `null` or an empty array `[]`.
- **Failed**: `violations_json` is a non-empty array (contains violation records).

The `running` status is not yet implemented and will always be 0. Future enhancements may detect running pipelines from `result_json` or other indicators.

## JSON-Only Output

For machine-readable output only (no human summary):

```bash
pmagent control pipeline-status --json-only
```

This outputs only JSON to stdout, with no summary to stderr.

## Custom Time Window

To query a different time window:

```bash
# Last 48 hours
pmagent control pipeline-status --window-hours 48

# Last 7 days (168 hours)
pmagent control pipeline-status --window-hours 168
```

## Use Cases

### Pipeline Health Monitoring

Use this command to:
- Monitor pipeline execution frequency
- Track success/failure rates over time
- Identify pipelines with high failure rates
- Understand recent pipeline activity

### CI/CD Integration

In CI/CD pipelines:
- Check pipeline status before deployments
- Alert on high failure rates
- Generate pipeline health reports
- Track pipeline execution trends

### Debugging

When investigating issues:
- Identify which pipelines are failing
- Check when the last successful run occurred
- Compare failure rates across pipelines
- Understand pipeline execution patterns

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

**Note:** DB-off behavior is expected in CI environments per Rule-046. The command will return a hermetic `db_off` summary without crashing.

### No Pipeline Runs Found

If `total_runs=0` and `pipelines={}`:

1. **Check time window**: The default window is 24 hours. Try a longer window:
   ```bash
   pmagent control pipeline-status --window-hours 168  # Last 7 days
   ```

2. **Verify table exists**: Use `pmagent control tables` to confirm `control.agent_run` exists:
   ```bash
   pmagent control tables
   ```

3. **Check table contents**: Verify there are recent runs in the table:
   ```bash
   psql "$GEMATRIA_DSN" -c "SELECT COUNT(*) FROM control.agent_run WHERE created_at >= NOW() - INTERVAL '24 hours';"
   ```

### Pipeline Names Not Recognized

Pipeline names come from the `tool` column in `control.agent_run`. If pipeline names are unexpected:

1. **Check tool values**: Inspect what values are stored in the `tool` column:
   ```bash
   psql "$GEMATRIA_DSN" -c "SELECT DISTINCT tool FROM control.agent_run ORDER BY tool;"
   ```

2. **Verify data**: Ensure pipeline runs are being recorded correctly in the `control.agent_run` table.

## Related Documentation

- **Phase-3B Feature #9**: Control-plane pipeline status summary
- **Runbook**: `docs/runbooks/CONTROL_STATUS.md` (control-plane status check)
- **Runbook**: `docs/runbooks/CONTROL_TABLES.md` (table listing)
- **Runbook**: `docs/runbooks/CONTROL_SCHEMA.md` (schema introspection)
- **Tests**: `agentpm/tests/cli/test_phase3b_pmagent_control_pipeline_status_cli.py`
- **CLI**: `pmagent control pipeline-status` command
- **Rule-046**: Hermetic CI Fallbacks (DB-off behavior)

