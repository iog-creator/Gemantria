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

## AgentPM-Next:M3 — Plan Next from MASTER_PLAN + NEXT_STEPS

**Purpose:** Provide a deterministic, read-only planning surface that interprets `MASTER_PLAN.md` and `NEXT_STEPS.md` to suggest the next few work items for the PM.

**Implementation:**
- **Helper**: `agentpm.plan.next.build_next_plan()` — Reads `docs/SSOT/MASTER_PLAN.md` and `NEXT_STEPS.md`, extracts `Current Focus`, `Next Milestone`, and the latest "Next Gate / Next Steps" bullets.
- **CLI**: `pmagent plan next` — Returns a small list of suggested next tasks plus planning context.

**Usage:**
```bash
pmagent plan next --json-only      # JSON only (scripts)
pmagent plan next                  # JSON to stdout + human summary to stderr
pmagent plan next --limit 5        # Return top 5 candidates
pmagent plan next --with-status    # Include system posture (reality-check + status explain)
```

**Output structure:**
- `available`: bool (True if both files exist and have content)
- `master_plan_path`: str (path to MASTER_PLAN.md)
- `next_steps_path`: str (path to NEXT_STEPS.md)
- `current_focus`: str | null (extracted from MASTER_PLAN.md)
- `next_milestone`: str | null (extracted from MASTER_PLAN.md)
- `candidates`: list of `{id, title, source, priority, raw_line}` (from NEXT_STEPS.md)
- `posture`: dict (if `--with-status`) with:
  - `mode`: "hermetic" (commands unavailable) or "live" (successful)
  - `reality`: dict from `pmagent reality-check check --mode hint --json-only`
  - `status`: dict from `pmagent status explain --json-only`
  - `error`: str (only in hermetic mode, explains why commands failed)
- `note`: str (if unavailable, explains why)

**Hermetic behavior:**
- File-only: no DB/LM calls, no writes (default)
- With `--with-status`: optionally calls `pmagent reality-check` and `pmagent status explain` via subprocess
  - In hermetic mode (commands unavailable): sets `posture.mode = "hermetic"` and includes error message
  - In live mode (commands succeed): sets `posture.mode = "live"` and includes full posture data
- Gracefully handles missing files (returns `available: false`)
- Extracts candidates from the last "# Next Gate" or "# Next Steps" heading in NEXT_STEPS.md

## AgentPM-Next:M4 — Plan Open (Capability Session Envelope)

**Purpose:** Open a specific NEXT_STEPS item as a structured, posture-aware `capability_session` envelope that describes "what this work session is" before running pipelines.

**Implementation:**
- **Helper**: `agentpm.plan.next.build_capability_session()` — Builds a capability_session envelope for a specific candidate ID
- **CLI**: `pmagent plan open <candidate_id>` — Returns a capability_session envelope with plan context and optional posture

**Usage:**
```bash
# Open a capability session in JSON format
pmagent plan open NEXT_STEPS:1 --json-only

# Open with human-readable summary
pmagent plan open NEXT_STEPS:1

# Open without posture (faster, file-only)
pmagent plan open NEXT_STEPS:1 --no-with-status
```

**Capability Session Structure:**
- `type`: "capability_session"
- `version`: "1.0"
- `id`: Candidate ID (e.g., "NEXT_STEPS:1")
- `title`: Candidate title from NEXT_STEPS.md
- `source`: "NEXT_STEPS"
- `plan`: Object with:
  - `current_focus`: Current focus from MASTER_PLAN.md
  - `next_milestone`: Next milestone from MASTER_PLAN.md
  - `raw_line`: Original bullet line from NEXT_STEPS.md
- `posture`: dict (if `--with-status`, default True) with:
  - `mode`: "hermetic" (commands unavailable) or "live" (successful)
  - `reality`: dict from `pmagent reality-check check --mode hint --json-only`
  - `status`: dict from `pmagent status explain --json-only`
  - `error`: str (only in hermetic mode, explains why commands failed)
- `available`: bool (False if candidate not found or files missing)
- `reason`: str (if unavailable, explains why)

**Hermetic behavior:**
- File-only: no DB/LM calls, no writes (default)
- With `--with-status` (default): optionally calls `pmagent reality-check` and `pmagent status explain` via subprocess
  - In hermetic mode (commands unavailable): sets `posture.mode = "hermetic"` and includes error message
  - In live mode (commands succeed): sets `posture.mode = "live"` and includes full posture data
- Gracefully handles missing candidates (returns `available: false` with reason)
- Reuses `build_next_plan()` internally to get full planning context

**Integration:**
- Use `pmagent plan next --with-status` to discover candidate IDs
- Use `pmagent plan open <id> --with-status` to create a capability_session envelope
- Envelope can be used for:
  - Pre-flight validation (describe work before execution)
  - AI tracking (log session intent without running pipelines)
  - Evidence generation (structured session metadata for handoffs)

## AgentPM-Next:M5 — Plan Reality Loop

**Purpose:** Run a single planning + posture loop that chains `plan next --with-status` + `plan open` and writes a structured `capability_session` envelope to `evidence/pmagent/` for each work session.

**Implementation:**
- **Helper**: `agentpm.plan.next.run_reality_loop()` — Runs a single planning + posture loop and persists capability_session envelope
- **CLI**: `pmagent plan reality-loop` — Executes the loop and writes envelope to `evidence/pmagent/capability_session-<timestamp>.json`

**Usage:**
```bash
# Run reality loop and write envelope (JSON summary only)
pmagent plan reality-loop --limit 3 --json-only

# Run reality loop with human-readable summary
pmagent plan reality-loop --limit 3

# Associate a suggested command with the session (intent only, NOT executed)
pmagent plan reality-loop --limit 3 --dry-run-command "make book.go"

# Validate and optionally persist to control.agent_run_cli (gated by DB availability)
pmagent plan reality-loop --limit 3 --track-session
```

**Reality Loop Behavior:**
1. Calls `build_next_plan(with_status=True)` to get candidates and posture
2. Picks the highest-priority candidate (first one from NEXT_STEPS)
3. Calls `build_capability_session(candidate_id, with_status=True)` to build envelope
4. Writes envelope to `evidence/pmagent/capability_session-<RFC3339-timestamp>.json`
5. Returns summary with `available`, `candidate`, `envelope_path`, and `envelope`

**Output Summary Structure:**
- `available`: bool (True if candidates found and envelope written)
- `candidate`: dict | None (selected candidate info: id, title, source)
- `envelope_path`: str | None (path to written JSON file)
- `envelope`: dict | None (full capability_session envelope)
- `dry_run_command`: str | None (the command string if `--dry-run-command` was provided)
- `tracking`: dict | None (if `--track-session` is set, contains validation and persistence result)
- `error`: str | None (if available=False, explains why)

**Hermetic behavior:**
- File-only: no DB/LM calls, no direct DB writes (default)
- Uses existing `pmagent reality-check` and `pmagent status explain` commands via subprocess
- Writes only to `evidence/pmagent/` directory (created if missing)
- Gracefully handles missing candidates (returns `available: false` with error, exit 0)
- RFC3339 timestamp in filename ensures unique files per run
- `--dry-run-command`: Records the intended command under `plan.dry_run_command` in the envelope; command is **never executed** (intent metadata only)
- `--track-session`: Validates envelope and optionally persists to `control.agent_run_cli` (gated by DB availability)
  - **Default OFF**: Tracking disabled by default; no DB calls unless flag is set
  - **DB-off behavior**: Returns `{"written": False, "mode": "db_off"}` when DB unavailable (no exceptions)
  - **Validation always runs**: Envelope is validated even when tracking is disabled
  - **Persistence gated**: Only attempts DB write when `--track-session` is set AND validation passes
  - **Tracking result**: JSON output includes `tracking` block with `ok`, `errors`, `warnings`, and `tracking` sub-block containing `written`, `mode`, `agent_run_cli_id`, `error`

**Integration:**
- Recommended flow: `pmagent plan next --with-status` → `pmagent plan open <id>` → `pmagent plan reality-loop` (writes capability_session evidence)
- Each reality loop run creates a new timestamped envelope file
- Envelopes can be used for:
  - Session tracking (what work was planned at what time)
  - Posture history (system state at planning time)
  - Evidence for handoffs (structured session metadata)
  - AI tracking integration (via `--track-session`, persists to `control.agent_run_cli` when DB available)
  - Command intent tracking (via `--dry-run-command`, records suggested command without execution)
- Use `pmagent plan history` to view recent sessions (see M6 below)
- Together, `reality-loop` + `history` + `--track-session` form the "planning + tracking shell" for session management

## AgentPM-Next:M6 — Plan History (Read-Only Session Viewer)

**Purpose:** List recent capability_session envelopes from `evidence/pmagent/` to view planning history without executing any commands.

**Implementation:**
- **Helper**: `agentpm.plan.next.list_capability_sessions()` — Reads and summarizes capability_session envelopes
- **CLI**: `pmagent plan history` — Lists recent sessions with metadata

**Usage:**
```bash
# List recent sessions (JSON only)
pmagent plan history --limit 10 --json-only

# List with human-readable summary
pmagent plan history --limit 10
```

**History Behavior:**
1. Reads all `capability_session-*.json` files from `evidence/pmagent/`
2. Sorts by file modification time (newest first)
3. Extracts summarized metadata from each envelope
4. Returns list of session summaries with:
   - `id`: Candidate ID (e.g., "NEXT_STEPS:1")
   - `title`: Candidate title
   - `source`: Source (e.g., "NEXT_STEPS")
   - `envelope_path`: Full path to envelope file
   - `timestamp`: RFC3339 timestamp from filename or file mtime
   - `dry_run_command`: str | None (if present)
   - `posture_mode`: str | None ("live" or "hermetic")
   - `reality_overall_ok`: bool | None (if posture.reality present)
   - `status_level`: str | None (if posture.status present)

**Output Structure:**
- `count`: int (number of sessions returned)
- `sessions`: list of session summary dicts (see above)

**Hermetic behavior:**
- Read-only: no DB/LM calls, no writes
- File-only: reads from `evidence/pmagent/` directory
- Gracefully handles empty directory (returns empty list)
- Skips invalid or unreadable JSON files
- Sorted newest-first by file modification time

**Integration:**
- Use with `pmagent plan reality-loop` to create and view planning history
- Together, `reality-loop` + `history` + `--track-session` form the "planning + tracking shell" for session management
- History provides read-only view of planned work sessions
- Tracking (via `--track-session`) persists sessions to `control.agent_run_cli` when DB is available (gated, default OFF)
