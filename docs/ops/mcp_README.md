# Knowledge MCP — Operator Notes (PR-3)

Endpoints (read-only JSON; bounded k ≤ 25):

- `mcp.hybrid_search(q_text text, k int=10)` → `[{"id","label","score"}]`

- `mcp.graph_neighbors(node_id text, depth int=1, k int=10)` → `[{"id","label","edge_w"}]`

- `mcp.lookup_ref(book text, chapter int, verse int, k int=10)` → `[{"ref":{"book","chapter","verse"},"text"}]`

All endpoints **fail safe**: if required tables/extensions are missing, they return an empty `items` array and a `"note"` message while preserving JSON shape.

**RO-on-tag policy:** Tag builds must use a read-only DSN (see RULES_INDEX.md / DSN guards). These endpoints contain **no write verbs** and are marked STABLE.

