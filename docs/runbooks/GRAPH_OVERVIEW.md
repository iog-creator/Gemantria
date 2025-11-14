# Graph Overview Runbook

## Purpose

The `graph.overview` command provides a quick summary of graph statistics from the database. It queries the `graph_stats_snapshots` table to display key metrics like node count, edge count, average degree, and snapshot information.

## Quick Start

### CLI Usage (Primary Interface)

The `pmagent` CLI is the primary interface for graph operations:

```bash
# Check graph overview
pmagent graph overview

# Or using Python module directly
python -m pmagent.cli graph overview
```

**Note**: The `pmagent health graph` command is also available for backward compatibility, but `pmagent graph overview` is the preferred interface.

### Make Target (Convenience Wrapper)

The Make target is a thin wrapper around `pmagent`:

```bash
make graph.overview
```

Both methods output:
- **JSON** to stdout (machine-friendly)
- **Human-readable summary** to stderr

Example output:
```
{
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
GRAPH_OVERVIEW: nodes=100 edges=200 avg_degree=4.00 snapshots=1
```

## DB Health Integration

The `graph.overview` command honors DB health modes and will gracefully handle database unavailability:

### `db_on` Mode - Database Ready

**When**: Database is connected and `graph_stats_snapshots` table is accessible.

**Output**: Full statistics including:
- `nodes`: Number of nodes in the graph
- `edges`: Number of edges in the graph
- `avg_degree`: Average degree (calculated as `edges * 2 / nodes` if not stored)
- `snapshot_count`: Number of distinct snapshots in the database
- `last_import_at`: ISO8601 timestamp of the most recent import

**Example**:
```bash
$ make graph.overview
GRAPH_OVERVIEW: nodes=100 edges=200 avg_degree=4.00 snapshots=1
```

### `db_off` Mode - Database Unavailable

**When**: Database driver is missing or connection cannot be established.

**Output**: Error message with mode and reason.

**Example**:
```bash
$ make graph.overview
{
  "ok": false,
  "mode": "db_off",
  "stats": { ... },
  "reason": "driver not installed"
}
GRAPH_OVERVIEW: mode=db_off (driver not installed)
```

**Next steps**: See `docs/runbooks/DB_HEALTH.md` for troubleshooting.

### `partial` Mode - Table Missing

**When**: Database is connected but `graph_stats_snapshots` table does not exist.

**Output**: Error message indicating table is missing.

**Example**:
```bash
$ make graph.overview
{
  "ok": false,
  "mode": "partial",
  "stats": { ... },
  "reason": "graph_stats table missing"
}
GRAPH_OVERVIEW: mode=partial (graph_stats table missing)
```

**Next steps**: Run database migrations or import graph stats to create the table.

## Statistics Explained

### Nodes

Total number of nodes (vertices) in the graph. Retrieved from the latest snapshot's `nodes` metric.

### Edges

Total number of edges (connections) in the graph. Retrieved from the latest snapshot's `edges` metric.

### Average Degree

Average number of connections per node. Calculated as `(edges * 2) / nodes` if not explicitly stored in the database. This accounts for undirected edges (each edge connects two nodes).

**Note**: If `nodes = 0`, `avg_degree` will be `null` to avoid division by zero.

### Snapshot Count

Number of distinct graph statistics snapshots stored in the database. Each import of `graph_stats.json` creates a new snapshot with a unique `snapshot_id`.

### Last Import At

ISO8601 timestamp of the most recent graph statistics import. Indicates when the latest snapshot was created.

## Usage Examples

### Get JSON Output Only

```bash
make graph.overview 2>/dev/null
```

### Get Human Summary Only

```bash
make graph.overview 2>&1 | grep "GRAPH_OVERVIEW"
```

### Check if Graph Has Data

```bash
if make graph.overview 2>&1 | grep -q "nodes=[1-9]"; then
  echo "Graph has data"
else
  echo "Graph is empty or DB unavailable"
fi
```

## Integration with Other Tools

### PM Snapshot

The graph overview is not automatically included in PM snapshots, but can be run separately to check graph statistics.

### CI/CD

The command is safe to run in CI environments:
- Always exits with code 0 (hermetic, DB-off-safe)
- Returns structured JSON for programmatic parsing
- Handles database unavailability gracefully

## Troubleshooting

### "no snapshots found"

**Problem**: Database is ready but no graph statistics have been imported.

**Solution**: Import graph statistics:
```bash
make db.import.graph_stats
```

### "graph_stats table missing"

**Problem**: Database is connected but the `graph_stats_snapshots` table does not exist.

**Solution**: 
1. Run database migrations to create the table
2. Or import graph stats (which will create the table if needed)

### "driver not installed" or "connection failed"

**Problem**: Database is unavailable.

**Solution**: See `docs/runbooks/DB_HEALTH.md` for detailed troubleshooting.

## Related Documentation

- **DB Health**: See `docs/runbooks/DB_HEALTH.md` for database health checks
- **Graph Stats Import**: See `docs/runbooks/GRAPH_IMPORT.md` for importing graph statistics
- **Database Architecture**: See `docs/ADRs/ADR-001-database-architecture.md` for DB design

## Make Targets

- `make graph.overview` - Display graph overview (JSON + human summary)
- `make test.phase3b.graph.overview` - Run graph overview tests

