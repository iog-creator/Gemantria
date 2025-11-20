# AGENTS.md

## Directory Purpose

The `agentpm/plan/` directory contains planning workflows powered by the KB registry. These helpers provide deterministic planning surfaces for PM/AgentPM workflows, including both read-only worklist generation and doc-fix execution.

## AgentPM-Next:M1 — Registry-Powered Planning Flows

**Purpose:** Provide a thin, deterministic planning surface that interprets KB registry status and hints to produce prioritized documentation worklists.

**Implementation:**
- **Helper**: `agentpm.plan.kb.build_kb_doc_worklist()` — Builds prioritized worklist from KB registry status and hints
- **CLI**: `pmagent plan kb list` — Returns prioritized documentation worklist with suggested actions
- **Worklist structure**: Items grouped by subsystem, ordered by severity (missing > stale > out_of_sync > low_coverage > info)
- **Hermetic**: No writes, no LM calls; purely interprets existing KB signals

**Usage:**
```bash
# Get worklist in JSON format
pmagent plan kb list --json-only

# Get worklist with human-readable output
pmagent plan kb list
```

**Worklist Item Structure:**
- `id`: Document ID or subsystem identifier
- `title`: Human-readable title
- `subsystem`: Owning subsystem (e.g., "docs", "agentpm", "webui")
- `type`: Document type (e.g., "ssot", "adr", "runbook")
- `severity`: Priority level ("missing", "stale", "out_of_sync", "low_coverage", "info")
- `reason`: Explanation of why this item is in the worklist
- `suggested_action`: Recommended action to address the issue

**Integration:**
- Uses `agentpm.status.snapshot.get_kb_status_view()` and `get_kb_hints()` for KB data
- Uses `agentpm.kb.registry.load_registry()` for document details
- Processes freshness data from KB-Reg:M6 freshness analysis
- Processes hints from KB-Reg:M4 hint generation

## AgentPM-Next:M2 — Doc-Fix Flows

**Purpose:** Consume worklist from M1 and execute doc fixes (create stubs, mark stale, sync metadata) with safety controls.

**Implementation:**
- **Helper**: `agentpm.plan.fix.build_fix_actions()` — Converts worklist items to fix action objects
- **Helper**: `agentpm.plan.fix.apply_actions()` — Executes fix actions (dry-run or apply mode)
- **CLI**: `pmagent plan kb fix` — Execute doc fixes from KB worklist
- **Safety**: Default dry-run mode; `--apply` requires explicit opt-in; only approved paths can be written

**Usage:**
```bash
# Dry-run (default): show proposed actions without writing
pmagent plan kb fix

# Apply fixes: actually create/update files
pmagent plan kb fix --apply

# Filter by subsystem or severity
pmagent plan kb fix --subsystem docs --min-severity missing

# JSON-only output for automation
pmagent plan kb fix --json-only
```

**Action Types by Severity:**
- `missing` → `create_stub_doc`: Create minimal stub file with front-matter
- `stale` → `mark_stale_and_suggest_update`: Append timestamped staleness note
- `out_of_sync` → `sync_metadata`: Fix registry/FS drift, update freshness markers
- `low_coverage` → `propose_new_docs`: Emit suggestions only (no auto-creation unless `--allow-stubs-for-low-coverage`)
- `info` → `no_op`: Advisory note only

**Safety Model:**
- **Default dry-run**: No writes unless `--apply` is explicitly specified
- **Approved paths only**: Writes restricted to `docs/**`, `AGENTS.md` files, `rules/docs/**`
- **Idempotent**: Re-running doesn't double-append markers or create duplicate files
- **Manifest logging**: All applied actions logged to `evidence/plan_kb_fix/run-<timestamp>.json`
- **No schema drift**: Reuses existing KB freshness helpers; no registry contract changes

**Integration:**
- Consumes worklist from `build_kb_doc_worklist()` (M1)
- Uses `agentpm.kb.registry` for document metadata and freshness tracking
- Updates `last_refreshed_at` when content is modified (via existing freshness helpers)
- See `docs/SSOT/AGENTPM_NEXT_M2_DESIGN.md` for full design spec
