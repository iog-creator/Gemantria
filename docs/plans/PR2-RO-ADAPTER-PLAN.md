# PR-2 Plan: STRICT/Tag-Lane RO Adapter Wiring

**Context:** PR #415 (Guarded Tool Calls P0 execution) is merged. This PR wires the adapter to use read-only DSN on tag builds and proves `mcp.v_catalog` access.

## Objectives

- **Tag-lane RO DSN:** Adapter uses centralized RO DSN loader on tag builds only
- **STRICT proof:** `make guard.mcp.db.ro STRICT_DB_PROBE=1` validates `mcp.v_catalog` access
- **PR CI hermetic:** No DB probes in PR CI (adapter remains stubbed)
- **No writes:** Read-only operations only; no mutations

## Implementation Approach

### Adapter Changes (`pmagent/adapters/mcp_db.py`)

- Detect tag builds via environment (e.g., `CI_TAG_BUILD=1` or git tag detection)
- Use centralized DSN loader (`scripts.config.env.get_ro_dsn()` or `src.gemantria.dsn.dsn_ro()`)
- Query `mcp.v_catalog` view when in tag/STRICT mode
- Fall back to deterministic stub in PR CI (hermetic)

### CI/Tagproof Hook

- Tag workflow includes: `make guard.mcp.db.ro STRICT_DB_PROBE=1`
- Validates RO DSN connectivity and `mcp.v_catalog` view access
- Fails-closed if RO DSN unavailable or view missing

### References

- **AGENTS.md:** RO DSN precedence and centralized loader guidance
- **RFC-078:** Postgres Knowledge MCP catalog-as-a-service
- **Runbook:** `docs/runbooks/MCP_KNOWLEDGE_DB.md` (usage notes)

## Acceptance Criteria

- PR CI remains hermetic (no DB probes)
- Tag builds prove RO DSN + `mcp.v_catalog` access
- `make guard.mcp.db.ro STRICT_DB_PROBE=1` passes on tags
- No writes to database (read-only operations only)

## Out-of-Scope

- Tool Bus/RPC wiring
- pg_cron refresh automation (separate PR)
- Write operations or mutations

