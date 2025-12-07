# Phase 27.I — Batch 2: Schemas Namespace Guard

## Summary

This PR implements Batch 2 of Phase 27.I (Directory Namespace Cleanup),
focusing on **Schemas**:

- Normalizes **docs-only** schema documentation into `docs/schemas/`.
- Confirms machine JSON schemas live under `schemas/`.
- Extends `guard_directory_namespace_policy.py` with a Schemas check.
- **Explicitly does NOT move or change SSOT schemas under `docs/SSOT/*.schema.json`.**

## Changes

### 1. Schema directory normalization

- Moved:
  - `docs/schema/SCHEMA.md` → `docs/schemas/SCHEMA.md`

- `docs/schema/` now contains only `AGENTS.md` (directory documentation).

- Machine schemas are already under `schemas/`:
  - `schemas/graph.schema.json`
  - `schemas/ai-nouns.schema.json`
  - `schemas/graph-stats.schema.json`
  - `schemas/graph-patterns.schema.json`
  - `schemas/gematria_output.schema.json`

### 2. Path reference updates

- Updated 2 script references to match reality:
  - `scripts/ingest_docs.py`: `docs/SSOT/graph.schema.json` → `schemas/graph.schema.json`
  - `scripts/export_stats.py`: `docs/SSOT/graph-stats.schema.json` → `schemas/graph-stats.schema.json`

- Other `docs/SSOT/*.schema.json` files remain untouched and governed by existing rules.

### 3. Directory namespace guard (Schemas)

- `scripts/guards/guard_directory_namespace_policy.py` extended:
  - `check_schemas_namespace()` ensures:
    - `schemas/` exists and contains `.json` schema files.
    - `docs/schema/` has no leftover files except `AGENTS.md`.
    - No `*.schema.json` files live at the repo root.

- Example output:

```json
{
  "ok": true,
  "checks": {
    "adrs": { "ok": true, "issues": [] },
    "schemas": { "ok": true, "issues": [] }
  }
}
```

### 4. SSOT docs updated

- `PHASE27I_DIRECTORY_UNIFICATION_PLAN.md`:
  - Clarifies schema zones:
    - `schemas/` = machine schemas
    - `docs/schemas/` = docs
    - `docs/schema/` = legacy docs only
    - `docs/SSOT/*.schema.json` = SSOT/domain schemas, **out of scope for 27.I**

- `DIRECTORY_DUPLICATION_MAP.md`:
  - Marks:
    - `schemas/`, `docs/schemas/`, `docs/SSOT/*.schema.json` as **kept**.
    - `docs/schema/` as **legacy docs** to be merged/removed.

## Health

- `ops.kernel.check`: passes
- `reality.green`: passes (all checks green)
- `guard_directory_namespace_policy.py`: passes for both ADRs and Schemas

This PR intentionally **does not** move or refactor `docs/SSOT/*.schema.json`.
Any future unification of those schemas will be a separate phase with explicit
design and tests.
