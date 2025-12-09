# System Health Runbook

## Purpose

This runbook explains how to check overall system health by aggregating DB health, LM health, and graph overview into a single command. The `system.health.smoke` command provides a one-command view of all system components.

## Quick Start

### CLI Usage (Primary Interface)

The `pmagent` CLI is the primary interface for health checks:

```bash
# Check system health (aggregates DB + LM + Graph)
pmagent health system

# Or using Python module directly
python -m pmagent.cli health system
```

### Make Target (Convenience Wrapper)

The Make target is a thin wrapper around `pmagent`:

```bash
make system.health.smoke
```

Both methods output:
- **JSON** to stdout (machine-friendly)
- **Human-readable summary** to stderr

Example output:
```
{
  "ok": false,
  "components": {
    "db": {
      "ok": false,
      "mode": "db_off",
      ...
    },
    "lm": {
      "ok": false,
      "mode": "lm_off",
      ...
    },
    "graph": {
      "ok": false,
      "mode": "db_off",
      ...
    }
  }
}
SYSTEM_HEALTH:
  DB_HEALTH:   mode=db_off (driver not installed)
  LM_HEALTH:   mode=lm_off (endpoint not reachable)
  GRAPH_OVERVIEW: mode=db_off (Postgres database driver not available)
```

## System Health Status

The system health aggregate reports `ok: true` only when **all three components** are healthy:

- **DB**: `mode="ready"` (driver available, connection works, tables accessible)
- **LM**: `mode="lm_ready"` (endpoint reachable and responding correctly)
- **Graph**: `mode="db_on"` (database connected and graph stats available)

If any component is not ready, `ok: false` is reported.

## Component Details

### DB Health

**What it checks**: Database driver availability, connection status, and table readiness.

**Modes**:
- `ready`: All systems operational
- `db_off`: Database unavailable (driver missing or connection failed)
- `partial`: Database connected but tables missing

**See also**: `docs/runbooks/DB_HEALTH.md` for detailed DB health information.

### LM Health

**What it checks**: LM Studio endpoint availability and response validity.

**Modes**:
- `lm_ready`: LM Studio operational
- `lm_off`: LM Studio unavailable (endpoint not reachable or responding incorrectly)

**See also**: `docs/runbooks/LM_HEALTH.md` for detailed LM health information.

### Graph Overview

**What it checks**: Graph statistics from the database (node count, edge count, average degree, snapshot information).

**Modes**:
- `db_on`: Database connected and graph stats available
- `db_off`: Database unavailable (driver missing or connection failed)
- `partial`: Database connected but graph_stats table missing

**See also**: `docs/runbooks/GRAPH_OVERVIEW.md` for detailed graph overview information.

## Example Outputs

### All Components Off

When DB and LM are both unavailable (common in development environments):

```json
{
  "ok": false,
  "components": {
    "db": {
      "ok": false,
      "mode": "db_off",
      "checks": {
        "driver_available": false,
        "connection_ok": false,
        "graph_stats_ready": false
      },
      "details": {
        "errors": ["driver_missing: Postgres driver not installed"]
      }
    },
    "lm": {
      "ok": false,
      "mode": "lm_off",
      "details": {
        "endpoint": "http://127.0.0.1:1234",
        "errors": ["connection_refused: Connection refused"]
      }
    },
    "graph": {
      "ok": false,
      "mode": "db_off",
      "stats": {
        "nodes": null,
        "edges": null,
        "avg_degree": null,
        "snapshot_count": null,
        "last_import_at": null
      },
      "reason": "Postgres database driver not available"
    }
  }
}
```

```
SYSTEM_HEALTH:
  DB_HEALTH:   mode=db_off (driver not installed)
  LM_HEALTH:   mode=lm_off (endpoint not reachable)
  GRAPH_OVERVIEW: mode=db_off (Postgres database driver not available)
```

### All Components Ready

When all systems are operational:

```json
{
  "ok": true,
  "components": {
    "db": {
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
    },
    "lm": {
      "ok": true,
      "mode": "lm_ready",
      "details": {
        "endpoint": "http://127.0.0.1:1234",
        "errors": []
      }
    },
    "graph": {
      "ok": true,
      "mode": "db_on",
      "stats": {
        "nodes": 100,
        "edges": 200,
        "avg_degree": 4.0,
        "snapshot_count": 1,
        "last_import_at": "2024-01-15T10:30:00+00:00"
      },
      "reason": null
    }
  }
}
```

```
SYSTEM_HEALTH:
  DB_HEALTH:   mode=ready (ok)
  LM_HEALTH:   mode=lm_ready (ok)
  GRAPH_OVERVIEW: mode=db_on (ok)
```

### Mixed States

When some components are ready and others are not:

```json
{
  "ok": false,
  "components": {
    "db": {
      "ok": false,
      "mode": "partial",
      "checks": {
        "driver_available": true,
        "connection_ok": true,
        "graph_stats_ready": false
      },
      "details": {
        "errors": ["graph_stats_table_missing: gematria.graph_stats_snapshots does not exist"]
      }
    },
    "lm": {
      "ok": true,
      "mode": "lm_ready",
      "details": {
        "endpoint": "http://127.0.0.1:1234",
        "errors": []
      }
    },
    "graph": {
      "ok": false,
      "mode": "db_off",
      "stats": {
        "nodes": null,
        "edges": null,
        "avg_degree": null,
        "snapshot_count": null,
        "last_import_at": null
      },
      "reason": "Postgres database driver not available"
    }
  }
}
```

```
SYSTEM_HEALTH:
  DB_HEALTH:   mode=partial (graph_stats table missing)
  LM_HEALTH:   mode=lm_ready (ok)
  GRAPH_OVERVIEW: mode=db_off (Postgres database driver not available)
```

## Interpretation

### System Health Summary

The human-readable summary provides a quick overview:

```
SYSTEM_HEALTH:
  DB_HEALTH:   mode=<db_mode> (<reason>)
  LM_HEALTH:   mode=<lm_mode> (<reason>)
  GRAPH_OVERVIEW: mode=<graph_mode> (<reason>)
```

- **Mode**: Current state of the component (ready, db_off, lm_off, partial, etc.)
- **Reason**: Short explanation of the current state (ok, error message, etc.)

### Overall Health

The `ok` field in the JSON indicates overall system health:
- `ok: true`: All components are healthy and ready
- `ok: false`: At least one component is not ready

**Note**: It is **safe and expected** for DB and LM to be off in many workflows. The system health check always exits 0 (hermetic behavior) and is safe for CI environments.

## Troubleshooting

### All Components Off

**Problem**: DB, LM, and graph all report unavailable states.

**This is normal** in development environments where:
- Database driver is not installed
- LM Studio is not running
- Graph stats have not been imported

**Solution**: 
- If you need database features, see `docs/runbooks/DB_HEALTH.md`
- If you need LM Studio features, see `docs/runbooks/LM_HEALTH.md`
- If you need graph statistics, ensure database is set up and graph stats are imported

### Mixed States

**Problem**: Some components are ready, others are not.

**Solution**: 
- Check the individual component summaries in the output
- Refer to the respective runbooks for each component:
  - DB issues: `docs/runbooks/DB_HEALTH.md`
  - LM issues: `docs/runbooks/LM_HEALTH.md`
  - Graph issues: `docs/runbooks/GRAPH_OVERVIEW.md`

### Malformed JSON from Component

**Problem**: A component returns malformed JSON.

**Solution**:
- Check the component's individual command:
  - `make guard.db.health` for DB health
  - `make guard.lm.health` for LM health
  - `make graph.overview` for graph overview
- Review component logs for errors
- Ensure component scripts are up to date

## Related Documentation

- **DB Health**: `docs/runbooks/DB_HEALTH.md` - Detailed DB health information
- **LM Health**: `docs/runbooks/LM_HEALTH.md` - Detailed LM health information
- **Graph Overview**: `docs/runbooks/GRAPH_OVERVIEW.md` - Detailed graph overview information
- **Phase-3B Implementation**: See `AGENTS.md` for Phase-3B system health aggregate details

## Make Targets

- `make system.health.smoke` - Quick system health check with summary output
- `make test.phase3b.system.health` - Run system health aggregate tests
- `make guard.db.health` - Check DB health individually
- `make guard.lm.health` - Check LM health individually
- `make graph.overview` - Check graph overview individually

