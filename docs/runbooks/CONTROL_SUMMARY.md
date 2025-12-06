# Control Summary Runbook

## Purpose

The `pmagent control summary` command provides a single consolidated view of the entire control-plane posture by aggregating status, tables, schema, and pipeline-status into one JSON output. This is the Phase-3B consolidation feature that combines all control-plane introspection commands for convenient monitoring and integration with Atlas and future LM Studio hooks.

## Quick Start

### CLI Usage (Primary Interface)

The `pmagent` CLI is the primary interface for control-plane operations:

```bash
# Get aggregated control-plane summary
pmagent control summary

# Or using Python module directly
python -m pmagent.cli control summary
```

### Make Target (Convenience Wrapper)

The Make target is a thin wrapper around `pmagent`:

```bash
make control.summary.smoke
```

Both methods output:
- **JSON** to stdout (machine-friendly)
- **Human-readable summary** to stderr

## Example Outputs

### DB-Off Example

When the database is unavailable (driver missing, connection failed, etc.), all components return db_off mode:

```json
{
  "ok": true,
  "generated_at": "2024-01-15T10:30:00+00:00",
  "components": {
    "status": {
      "ok": false,
      "mode": "db_off",
      "reason": "Postgres database driver not available",
      "tables": {}
    },
    "tables": {
      "ok": false,
      "mode": "db_off",
      "error": "Postgres database driver not available",
      "tables": {}
    },
    "schema": {
      "ok": false,
      "mode": "db_off",
      "reason": "Postgres database driver not available",
      "tables": {}
    },
    "pipeline_status": {
      "ok": false,
      "mode": "db_off",
      "reason": "Postgres database driver not available",
      "window_hours": 24,
      "summary": {
        "total_runs": 0,
        "pipelines": {}
      }
    }
  }
}
```

```
CONTROL_SUMMARY: ok=true
```

**Note:** DB-off output is expected in CI and acceptable per Rule-046 (Hermetic CI Fallbacks). When all components are in db_off mode (hermetic behavior), the overall `ok` status is `true` because this is expected behavior, not an error.

### DB-On Example (Snippet)

When the database is ready and all components succeed:

```json
{
  "ok": true,
  "generated_at": "2024-01-15T14:30:00+00:00",
  "components": {
    "status": {
      "ok": true,
      "mode": "ready",
      "reason": null,
      "tables": {
        "control.agent_run": {
          "present": true,
          "row_count": 15,
          "latest_created_at": "2024-01-15T14:00:00+00:00"
        }
      }
    },
    "tables": {
      "ok": true,
      "mode": "db_on",
      "error": null,
      "tables": {
        "control.agent_run": 15,
        "control.tool_catalog": 8
      }
    },
    "schema": {
      "ok": true,
      "mode": "db_on",
      "reason": null,
      "tables": {
        "control.agent_run": {
          "columns": [...],
          "primary_key": ["id"],
          "indexes": [...]
        }
      }
    },
    "pipeline_status": {
      "ok": true,
      "mode": "db_on",
      "reason": null,
      "window_hours": 24,
      "summary": {
        "total_runs": 10,
        "pipelines": {
          "graph_builder": {
            "total": 6,
            "by_status": {
              "success": 5,
              "failed": 1,
              "running": 0,
              "other": 0
            },
            "last_run_started_at": "2024-01-15T14:00:00+00:00",
            "last_run_status": "success"
          }
        }
      }
    }
  }
}
```

```
CONTROL_SUMMARY: ok=true
```

## Interpreting Results

### Top-Level Fields

- **`ok`**: Overall status:
  - `true` if all components that reached `db_on` mode are `ok=true`, OR if all components are in `db_off` mode (hermetic behavior)
  - `false` if any component that reached `db_on` mode has `ok=false`, OR if any component has `mode="error"` (exception occurred)
- **`generated_at`**: RFC3339 timestamp when the summary was generated
- **`components`**: Dictionary containing all four component results

### Component Structure

Each component in `components` follows the same structure as its individual CLI command:

- **`status`**: From `pmagent control status` - control-plane database status and table row counts
- **`tables`**: From `pmagent control tables` - all schema-qualified tables with row counts
- **`schema`**: From `pmagent control schema` - DDL/schema introspection for control-plane tables
- **`pipeline_status`**: From `pmagent control pipeline-status` - recent pipeline runs summary

### Status Determination Logic

The overall `ok` status is determined conservatively:

1. **All components db_off**: `ok=true` (hermetic behavior is acceptable)
2. **Some components db_on, all ok**: `ok=true`
3. **Some components db_on, any failed**: `ok=false`
4. **Any component with mode="error"**: `ok=false` (exception occurred)

This ensures that:
- Hermetic CI environments (all db_off) are treated as acceptable
- Real database connections must all succeed for overall `ok=true`
- Exceptions are always treated as failures

## JSON-Only Output

For machine-readable output only (no human summary):

```bash
pmagent control summary --json-only
```

This outputs only JSON to stdout, with no summary to stderr.

## Use Cases

### Unified Monitoring Dashboard

Use this command to:
- Get a complete snapshot of control-plane health in one call
- Integrate with monitoring systems (Atlas, Prometheus, etc.)
- Generate consolidated health reports
- Track control-plane posture over time

### CI/CD Integration

In CI/CD pipelines:
- Single command to check all control-plane components
- Fail builds if `ok=false` (indicates real issues, not hermetic db_off)
- Generate comprehensive health reports for deployments
- Track control-plane metrics in CI dashboards

### LM Studio Hooks

For future LM Studio integration:
- Single JSON payload for control-plane status
- Consistent structure for AI agent decision-making
- Complete context in one API call
- Reduced latency compared to multiple individual calls

### Debugging

When investigating issues:
- See all control-plane components at once
- Identify which components are failing
- Compare component states across different environments
- Understand overall system posture quickly

## Error Handling

The summary command is designed to be resilient:

- **Component exceptions**: If any individual component raises an exception, it is caught and recorded as `mode="error"` in that component's result, without crashing the entire summary
- **Partial failures**: If some components succeed and others fail, the summary still returns complete results for all components
- **Hermetic behavior**: All components gracefully handle db_off scenarios, so the summary works in CI environments without databases

## Troubleshooting

### Overall ok=false

If `ok=false`:

1. **Check component modes**: Inspect each component in `components` to see which ones have `ok=false` or `mode="error"`
   ```bash
   pmagent control summary --json-only | jq '.components | to_entries | map({key, ok: .value.ok, mode: .value.mode})'
   ```

2. **Check individual components**: Run each component individually to get detailed error messages:
   ```bash
   pmagent control status
   pmagent control tables
   pmagent control schema
   pmagent control pipeline-status
   ```

3. **Refer to component runbooks**: Each component has its own runbook with troubleshooting:
   - [CONTROL_STATUS.md](CONTROL_STATUS.md)
   - [CONTROL_TABLES.md](CONTROL_TABLES.md)
   - [CONTROL_SCHEMA.md](CONTROL_SCHEMA.md)
   - [CONTROL_PIPELINE_STATUS.md](CONTROL_PIPELINE_STATUS.md)

### Component Exceptions

If a component has `mode="error"`:

1. **Check logs**: The error message is in the component's `reason` or `error` field
2. **Verify dependencies**: Ensure all required modules and functions are available
3. **Test individually**: Run the component's individual CLI command to see the full error

### Database is Off

If all components are `db_off`:

- This is **expected behavior** in CI environments per Rule-046
- The overall `ok=true` in this case because hermetic behavior is acceptable
- To test with a real database, ensure `GEMATRIA_DSN` is set and the database is accessible

## Related Documentation

- **Phase-3B Consolidation**: Aggregated control-plane summary
- **Runbook**: [CONTROL_STATUS.md](CONTROL_STATUS.md) (individual status command)
- **Runbook**: [CONTROL_TABLES.md](CONTROL_TABLES.md) (individual tables command)
- **Runbook**: [CONTROL_SCHEMA.md](CONTROL_SCHEMA.md) (individual schema command)
- **Runbook**: [CONTROL_PIPELINE_STATUS.md](CONTROL_PIPELINE_STATUS.md) (individual pipeline-status command)
- **Tests**: `pmagent/tests/cli/test_phase3b_pmagent_control_summary_cli.py`
- **CLI**: `pmagent control summary` command
- **Rule-046**: Hermetic CI Fallbacks (DB-off behavior)

