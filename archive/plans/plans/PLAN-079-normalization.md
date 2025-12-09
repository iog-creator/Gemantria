# PLAN-079 — Normalize naming & metrics (pre-implementation)

**Context.** We've landed P0 scaffold for Guarded Tool Calls (schemas, control-plane SQL, stubs, tests). Before execution code lands, we will normalize names and metric conventions across DB, JSON Schemas, guards, and Makefile.

## Objectives

- **Normalize** DB objects and schema IDs; ensure re-runnable (idempotent) migrations.

- Lock **metric names** (status fields, created_at/updated_at) and MV prefixes.

- Add a **schema-naming guard** + Makefile target; no runtime wiring yet.

## Scope (Do)

1) **DB naming**

   - Tables prefix: `mcp_*` (e.g., `mcp_tool_catalog`, `mcp_agent_run`)

   - MVs prefix: `mv_mcp_*` (e.g., `mv_mcp_compliance_7d`)

   - Columns: prefer `status` (not `state`), add `created_at`, `updated_at` where applicable

   - Add **idempotent** migration: conditional renames + additive columns only

2) **JSON Schemas**

   - `$id` prefix: `gemantria://v1/...`

   - `title` present; top-level `type: "object"` and `additionalProperties: false`

3) **Guards & Makefile**

   - New guard `guard_schema_naming.py` (hermetic)

   - Makefile target: `guard.schema.naming`

## Non-goals

- No Tool Bus / RPC wiring, no adapter execution, no DSN probes.

## Deliverables

- **RFC-079** (tiny, accepted fast-track) — already drafted in previous step

- Migration file: `db/migrations/2025-11-guarded-calls-p0.naming.sql`

- Guard script + Make target

- Updated schemas with normalized `$id` + titles

## Acceptance criteria

- `ruff` green

- `make guard.schema.naming` ⇒ `ok: true`

- Greps show `mcp_*`, `mv_mcp_*` present; migration re-runnable without error

- No CI workflow changes in this PR

## Plan of record (POR) — PR sequence

- **PR-A (this):** PLAN-079 (this document only)

- **PR-B (naming):** RFC-079 + migration + guard + Make target + schema normalization (file-only)

- **PR-C (execution, separate lane):** jsonschema validation + PoR checks + adapters + TVs 01–05 green

## Risks & rollback

- Renames are guarded via `to_regclass`; additive columns are `IF NOT EXISTS`. Rollback: rename back and drop added columns if needed.

## References

- RULES_INDEX.md (Rule-050/051/052/062/067)

- docs/SSOT/GPT_SYSTEM_PROMPT.md (OPS template + browser verification)

- docs/rfcs/RFC-078-postgres-knowledge-mcp.md

- AGENTS.md (MCP/DSN pointers)
