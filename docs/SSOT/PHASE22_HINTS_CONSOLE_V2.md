# Phase 22.2 — DMS Hints & Orchestrator Console v2

**Status:** COMPLETE (governance only, no DB changes yet)  
**Scope:** Define how DMS hints should represent Orchestrator Console v2 and its webui contract.

## 1. Context

By Phase 20–22, Orchestrator Console v2 is:

- Surface-driven:
  - `share/SSOT_SURFACE_V17.json`
  - `share/PM_BOOTSTRAP_STATE.json`
  - `share/PHASE18_*`, `share/PHASE19_*`, `share/PHASE20_*`
  - Orchestrator/OA surfaces under `share/orchestrator/*` and `share/orchestrator_assistant/*`
- Registered in `PM_BOOTSTRAP_STATE.json` under `webui.console_v2` with:
  - `source`, `dev_server`, `ci_check`, `schema`, `view_model`, `dev_url`, `surfaces_consumed`.

Operator workflows are documented in:

- `share/PHASE22_OPERATOR_WORKFLOW.md` — how to build, serve, and smoke-test console v2.

## 2. Goal of This Phase

We do **not** modify the Postgres DMS or hint registry in this phase.

Instead, we:

- Define the **expected DMS hint posture** for console v2.
- Provide a clear contract for a future "Hints Phase" to implement without guessing.

## 3. Desired Hint Posture (Future Implementation)

### 3.1 Required Hint: Console Presence

A future `docs/hints/HINT-UI-001-console-v2-present.md` (name illustrative) should express:

- **What:** Orchestrator Console v2 exists and is the preferred orchestrator-facing UI.
- **Where:**
  - Code: `webui/orchestrator-console-v2/`
  - Dev server: `scripts/dev/serve_console_v2.py`
  - CI check: `scripts/pm/check_console_v2.py`
- **Surfaces consumed:**
  - `share/SSOT_SURFACE_V17.json`
  - `share/PM_BOOTSTRAP_STATE.json`
  - Phase 18–21 summaries
  - Orchestrator/OA surfaces
  - `share/atlas/control_plane/`, `share/exports/docs-control/`, `share/kb_registry.json`

This hint should be visible to:

- PM agents deciding whether console v2 is the canonical UI.
- Small models that need to know "where the UI lives" without reading the whole repo.

### 3.2 Optional Hint: WebUI Contract Alignment

A second hint (e.g., `HINT-UI-002-webui-contract-console-v2.md`) should later:

- Link console v2 to `docs/SSOT/webui-contract.md`.
- Clarify that console v2:
  - Reads **share/** surfaces only.
  - Does **not** talk directly to the DB or LMs.
  - Is governed by `CONSOLE_SCHEMA.json` + `VIEW_MODEL.json`.

## 4. Guardrails for Future DMS Work

When a future phase actually implements these hints:

- Follow existing hint templates from `docs/hints/*` (do **not** invent a new schema).
- Use the existing DMS hint ingestion pipeline only (no ad-hoc SQL).
- Add new hints as **WARN/INFO**, not as hard gates, unless explicitly decided.

## 5. How PM / OPS Should Treat This Phase

Until the DMS hints are implemented:

- Treat this doc as the **single source of truth** for how console v2 should appear in hints.
- When making PM decisions about UI or operator workflows:
  - Check:
    - `share/PM_BOOTSTRAP_STATE.json`
    - `share/PHASE22_OPERATOR_WORKFLOW.md`
    - This doc (`PHASE22_HINTS_CONSOLE_V2.md`)
- When the Hints Phase lands, update this doc to:
  - Link to the actual `docs/hints/HINT-UI-00X-*.md` files.
  - Record the migration/ingestion path used.
