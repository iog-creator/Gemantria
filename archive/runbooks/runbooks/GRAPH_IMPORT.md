# Graph Import Runbook

## Purpose

This runbook explains how to import graph statistics from JSON files into the Postgres database. The `pmagent graph import` command loads graph_stats JSON into the `graph_stats_snapshots` table, making Postgres the source of truth for graph statistics.

## Quick Start

### CLI Usage (Primary Interface)

The `pmagent` CLI is the primary interface for graph imports:

```bash
# Import graph_stats.json with default path
pmagent graph import

# Or specify a custom input file
pmagent graph import --input path/to/graph_stats.json

# Or using Python module directly
python -m pmagent.cli graph import --input exports/graph_stats.json
```

### Make Target (Convenience Wrapper)

The Make target is a thin wrapper around `pmagent`:

```bash
make db.import.graph_stats
```

Both methods output:
- **JSON** to stdout (machine-friendly)
- **Human-readable summary** to stderr

Example output (success):
```
GRAPH_IMPORT: snapshots_imported=1 rows_inserted=7 snapshot_id=123e4567-e89b-12d3-a456-426614174000
{
  "ok": true,
  "inserted": 7,
  "errors": [],
  "source_path": "exports/graph_stats.json",
  "snapshot_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

Example output (failure):
```
GRAPH_IMPORT: failed (db_driver_missing: database driver not installed)
{
  "ok": false,
  "inserted": 0,
  "errors": ["db_driver_missing: database driver not installed"],
  "source_path": "exports/graph_stats.json",
  "snapshot_id": null
}
```

## Import Behavior

### What Gets Imported

The importer:
1. **Reads** the graph_stats JSON file
2. **Flattens** nested metrics (e.g., `{"centrality": {"avg_degree": 0.5}}` → `centrality.avg_degree`)
3. **Creates** a new snapshot with a unique UUID
4. **Inserts** rows into `gematria.graph_stats_snapshots` table
5. **Groups** all metrics from a single import under the same `snapshot_id`

### Snapshot Identification

- Each import creates a new snapshot with a unique UUID (`snapshot_id`)
- All metrics from a single JSON file share the same `snapshot_id`
- The `graph.overview` command queries the latest snapshot by `created_at` timestamp

### Data Types

- **Numeric values** (int, float) → stored in `metric_value` column
- **Complex objects** (dict, list) → stored as JSON in `metric_json` column
- **Nested metrics** → flattened with dot notation (e.g., `centrality.avg_degree`)

## Safety

### Hermetic Tests

All tests are hermetic and do not require a real database:
- Tests mock the database connection and file I/O
- No real Postgres instance is needed for testing
- Import logic is tested in isolation

### Real Imports

Real imports are only performed when you explicitly call the command:
- The command will fail if the database is unavailable
- Exit code 1 indicates import failure
- Exit code 0 indicates successful import

### Error Handling

The importer handles common errors gracefully:
- **Missing file**: Returns error with `missing_export` message
- **Invalid JSON**: Returns error with `invalid_json` message
- **Database unavailable**: Returns error with `db_driver_missing` or `db_unavailable` message
- **Table missing**: Automatically creates table if it doesn't exist

## Usage Examples

### Import Default File

```bash
pmagent graph import
```

Imports from `exports/graph_stats.json` (default path).

### Import Custom File

```bash
pmagent graph import --input share/exports/graph_stats_latest.json
```

### Check Import Status

After importing, verify the data:

```bash
# Check graph overview
pmagent graph overview

# Or via Make
make graph.overview
```

### Import and Verify

```bash
# Import
pmagent graph import --input exports/graph_stats.json

# Verify
pmagent graph overview
```

## Troubleshooting

### "missing_export" Error

**Problem**: Source file does not exist.

**Solution**:
1. Verify the file path is correct
2. Check if the file exists: `ls -la exports/graph_stats.json`
3. Use `--input` to specify the correct path

### "db_driver_missing" Error

**Problem**: Postgres database driver is not installed.

**Solution**:
1. Install the driver: `pip install psycopg[binary,pool]~=3.2`
2. Verify installation: `python -c "import psycopg; print('OK')"`
3. Check DB health: `pmagent health db`

### "db_unavailable" Error

**Problem**: Database connection failed.

**Solution**:
1. Check `GEMATRIA_DSN` environment variable
2. Verify database is running: `psql "$GEMATRIA_DSN" -c "SELECT 1;"`
3. Check DB health: `pmagent health db`

### "invalid_json" Error

**Problem**: Source file is not valid JSON.

**Solution**:
1. Validate JSON: `python -m json.tool exports/graph_stats.json`
2. Check file encoding (should be UTF-8)
3. Verify file is not corrupted

### Import Succeeds But Overview Shows No Data

**Problem**: Import worked but overview query doesn't find the data.

**Solution**:
1. Check if snapshot was created: Query `gematria.graph_stats_snapshots` table
2. Verify `created_at` timestamp is recent
3. Check if overview is querying the correct snapshot (latest by timestamp)

## Integration

### With Graph Overview

After importing, use `pmagent graph overview` to view statistics:

```bash
# Import
pmagent graph import

# View
pmagent graph overview
```

### With System Health

Graph import status is reflected in system health:

```bash
# Check overall system health
pmagent health system
```

The system health aggregate includes graph overview status.

### With Make Targets

The Makefile provides convenient wrappers:

```bash
# Import
make db.import.graph_stats

# Overview
make graph.overview
```

## Related Documentation

- **Graph Overview**: See `docs/runbooks/GRAPH_OVERVIEW.md` for viewing imported statistics
- **DB Health**: See `docs/runbooks/DB_HEALTH.md` for database health checks
- **System Health**: See `docs/runbooks/SYSTEM_HEALTH.md` for aggregated health status
- **Database Architecture**: See `docs/ADRs/ADR-001-database-architecture.md` for DB design

## Make Targets

- `make db.import.graph_stats` - Import graph stats from default location
- `make graph.overview` - Display graph overview (after import)
- `make test.phase3a.graph_stats` - Run graph stats importer tests

