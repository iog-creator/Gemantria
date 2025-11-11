# MCP Examples (psql)

> All endpoints return bounded JSON and are read-only. If infra is missing, they fail-safe with `items: []` and a `note`.

## Quickstart (psql)

```bash
# Resolve DSN via centralized loader (preferred) — Make target does this for you:
make mcp.examples.smoke
```

## Queries

### 1) Hybrid Search (text + vector fallback)

```sql
SELECT mcp.hybrid_search('light', 5);
```

### 2) Graph Neighbors (hop-limited)

```sql
SELECT mcp.graph_neighbors('node_1', 1, 5);
```

### 3) Scripture Lookup (bounded)

```sql
SELECT mcp.lookup_ref('Genesis', 1, 1, 5);
```

See also: `docs/ops/mcp_README.md` (contracts) and `docs/atlas/mcp_flow.mmd` (flow).

