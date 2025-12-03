# AgentPM-Next:M2 Design Spec — Doc-Fix Flows

**Status:** PM Design (Ready for Implementation)  
**Owner:** PM (ChatGPT) + Implementation Team  
**Last updated:** 2025-11-20  
**Related:** PLAN-092 (AgentPM-Next Planning Workflows), AgentPM-Next:M1 (PR #580)

---

## 1. Problem Statement

We now have a deterministic planning surface: `pmagent plan kb` → `build_kb_doc_worklist()` (JSON worklist, severity-ordered, grouped by subsystem).

**M2 should consume that worklist and produce/coordinate doc fixes**, without redefining KB semantics or registry logic.

---

## 2. Scope for M2

### In-Scope

- **New CLI surface**: `pmagent plan kb fix` (name can be refined, but treat this as the working handle)
- **Modes**:
  - Default: `--dry-run` (no writes, just proposed actions)
  - Optional: `--apply` (perform selected fixes, still conservative and deterministic)
- **Filters**: `--subsystem`, `--min-severity` (e.g. `missing|stale|out_of_sync|low_coverage|info`), `--limit`
- **Core behavior**:
  - Call `build_kb_doc_worklist()` to get the worklist
  - Filter by subsystem/severity/limit
  - For each item, construct a proposed action object, not an immediate mutation:
    ```json
    {
      "id", "subsystem", "severity", "doc_path?", "action_type", 
      "description", "suggested_edits"?, "notes"
    }
    ```
  - For `--dry-run`, only emit these actions as JSON + human summary; no filesystem writes
  - For `--apply`, execute a restricted set of actions (see below), log everything to evidence, and keep it idempotent

### Out-of-Scope for M2 (Explicitly)

- **No complex LM-driven rewriting loops**; at most, optional local LM assist for `suggested_edits` text, gated behind env flags
- **No schema or registry contract changes** (KB-Reg M1–M6 stay SSOT)
- **No DB schema changes**; no new tables

---

## 3. Action Model by Severity (What "Fix" Means)

### `missing` (KB_MISSING_DOCS / KB freshness `missing_docs`)

- **action_type**: `"create_stub_doc"`
- **Behavior (apply mode)**: Create a minimal, tagged stub file in the correct path with:
  - Standard front-matter (title, owning_subsystem, tags, "TODO: flesh out")
  - No speculative content; just scaffolding

### `stale` (KB_DOC_STALE)

- **action_type**: `"mark_stale_and_suggest_update"`
- **Behavior (apply mode)**:
  - Append or update a small "STALENESS NOTE" section in the doc (timestamped; references KB freshness rules)
  - Optionally include a short LM-assisted "update TODO" summary if LM is enabled; otherwise a template note
  - **Do not rewrite the doc automatically in M2**

### `out_of_sync` (KB_DOC_OUT_OF_SYNC)

- **action_type**: `"sync_metadata"`
- **Behavior (apply mode)**:
  - Fix obvious metadata/registry drift (e.g. wrong path in registry vs FS where clearly resolvable)
  - Update KB freshness markers (`last_refreshed_at`) only when a human-visible change has been made

### `low_coverage` (KB_LOW_COVERAGE_SUBSYSTEM)

- **action_type**: `"propose_new_docs"`
- **Behavior (dry-run)**:
  - Emit suggestions only (e.g. "Add AGENTS.md for X", "Add runbook for Y"); no automatic file creation in M2 except possibly a single optional stub per subsystem and only behind an explicit flag (e.g. `--allow-stubs-for-low-coverage`)

### `info` / `other`

- **action_type**: `"no_op"` or `"note_only"` — record as advisory; no automatic fix in M2

---

## 4. CLI Contract (Intended)

```bash
pmagent plan kb fix [--json-only] [--dry-run|--apply] [--subsystem SUB] [--min-severity LEVEL] [--limit N]
```

**Default behavior**: `--dry-run` (no writes)

**Flags**:
- `--json-only`: Output only JSON to stdout (no human-readable stderr)
- `--dry-run`: Emit proposed actions only (default)
- `--apply`: Execute actions (requires explicit opt-in)
- `--subsystem SUB`: Filter to specific subsystem (e.g. `pmagent`, `docs`, `webui`)
- `--min-severity LEVEL`: Filter to severity level or higher (`missing`, `stale`, `out_of_sync`, `low_coverage`, `info`)
- `--limit N`: Limit number of actions processed (default: 50)
- `--allow-stubs-for-low-coverage`: Allow creating stub files for low-coverage subsystems (only with `--apply`)

---

## 5. JSON Output Shape (SSOT for M2)

```json
{
  "mode": "dry-run" | "apply",
  "filters": {
    "subsystem": "pmagent|webui|docs|rules|root|...",
    "min_severity": "missing|stale|out_of_sync|low_coverage|info",
    "limit": 50
  },
  "source": {
    "worklist_items": N,
    "generated_at": "<RFC3339 timestamp>"
  },
  "actions": [
    {
      "id": "KB_MISSING_DOCS:docs/runbooks/PM_SNAPSHOT_CURRENT.md",
      "subsystem": "docs",
      "severity": "missing",
      "doc_path": "docs/runbooks/PM_SNAPSHOT_CURRENT.md",
      "action_type": "create_stub_doc",
      "description": "Create stub runbook for PM snapshot current state.",
      "suggested_edits": null,
      "applied": false,
      "notes": []
    }
  ],
  "summary": {
    "total_actions": N,
    "by_severity": {"missing": 2, "stale": 3, ...},
    "by_action_type": {"create_stub_doc": 2, "mark_stale_and_suggest_update": 3, ...}
  }
}
```

**Human mode**:
- **Stderr**: Short headline: "Doc-fix run (dry-run/apply) — X actions: Y missing, Z stale, …" + Top 5 actions with subsystem, path, severity, and 1-line description
- **Stdout**: The JSON above (machine-consumable, no extra noise)

---

## 6. Safety & Governance Model

### Default to Dry-Run

- `--apply` must be explicit; no accidental writes

### All Writes Go Through Single Executor

- Helper: `pmagent.plan.fix.apply_actions(actions)`
- Writes only under allowed directories:
  - `docs/**`
  - `AGENTS.md` files
  - `rules/docs` trees
  - **No writes outside approved paths**
- Logs a change manifest: `evidence/plan_kb_fix/run-<timestamp>.json` listing every touched file and action
- **Idempotent where possible** (e.g. re-running doesn't double-append markers)

### LM Usage (If Any) is Optional and Local-Only

- `USE_LM_FOR_DOC_FIX=1` gates generating `suggested_edits` snippets
- Even with LM, M2 never auto-applies large LM rewrites; only small, clearly delimited notes

### Integration with KB Freshness

- When an action tagged as "content updated" is applied, the fix code is allowed to call an existing freshness helper to update `last_refreshed_at`, not to re-invent that logic
- **No schema drift**: Reuse `analyze_freshness` and existing registry models

---

## 7. Implementation Artifacts

### Core Module

- **File**: `pmagent/plan/fix.py`
- **Functions**:
  - `build_fix_actions(worklist, filters) -> list[Action]`: Convert worklist items to action objects
  - `apply_actions(actions, dry_run=True) -> dict`: Execute actions (or simulate in dry-run)
  - `create_stub_doc(path, metadata) -> None`: Create minimal stub file
  - `mark_stale_note(doc_path, note) -> None`: Append staleness marker
  - `sync_metadata(registry, doc_id) -> None`: Fix registry/FS drift

### CLI Integration

- **File**: `pmagent/cli.py`
- **Command**: `@plan_app.command("fix")` (subcommand of `plan kb fix`)
- **Integration**: Calls `pmagent.plan.fix.build_fix_actions()` and `apply_actions()`

### Tests

- **File**: `pmagent/tests/cli/test_pmagent_plan_kb_fix.py`
- **Coverage**:
  - Dry-run produces correct action JSON
  - Apply mode creates/updates files correctly
  - No writes outside approved paths
  - Idempotence on repeated runs
  - Manifest logging works
  - Filters (subsystem, severity, limit) work correctly

### Documentation Updates

- **Files**:
  - `pmagent/AGENTS.md`: Add M2 fix flow section
  - `pmagent/plan/AGENTS.md`: Document fix module and safety model
  - `docs/SSOT/PMAGENT_CURRENT_VS_INTENDED.md`: Move `plan kb fix` from "INTENDED" to "CURRENT" once implemented

---

## 8. Acceptance Criteria for M2 (What "Done" Means for PM)

1. **Single CLI entrypoint exists** (`pmagent plan kb fix` or agreed alias) with the contract above

2. **Dry-run works**: Running with `--dry-run` on a live repo produces a structured `actions[]` list and **no writes** (confirmed by tests)

3. **Apply mode works**: Running with `--apply` on a controlled fixture actually creates/updates a small set of docs and logs a manifest, with tests verifying:
   - No writes outside approved paths
   - `applied` flags set correctly; manifests present
   - Idempotence on repeated runs

4. **AGENTS/SSOT docs updated**:
   - `pmagent/AGENTS.md` and `pmagent/plan/AGENTS.md` describe the M2 fix flow and its safety model
   - `PMAGENT_CURRENT_VS_INTENDED.md` moves `plan kb fix` from "INTENDED" to "CURRENT" once implemented

5. **Integration tests pass**: Full test suite (`test_pmagent_plan_kb_fix.py`) covers all action types, filters, and safety checks

---

## 9. Dependencies & Prerequisites

- **AgentPM-Next:M1** ✅ (PR #580 merged) — `pmagent plan kb` and `build_kb_doc_worklist()` must be operational
- **KB-Reg:M1–M6** ✅ — Registry, status views, hints, and freshness tracking must be in place
- **Rule-044** — Share manifest contract (registry is read-only in CI)
- **Rule-062** — Environment validation (venv checks)

---

## 10. Open Questions / Future Enhancements (Post-M2)

- **LM-assisted content generation**: Full LM-driven doc rewriting (gated behind explicit flags, not in M2)
- **Batch operations**: Process multiple subsystems in parallel
- **Interactive mode**: Prompt user for confirmation before applying each action
- **Integration with ADR workflow**: Auto-generate ADR stubs when new features are detected

---

**End of Design Spec**

