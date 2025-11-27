# AGENTS.md - agentpm/reality Directory

## Directory Purpose

The `agentpm/reality/` directory contains the reality check system for comprehensive environment validation (env/DSN, DB/control plane, LM/models, exports, eval smokes).

## Key Components

### `reality_check()`

**Purpose:** Single unified command for system environment validation with HINT/STRICT modes.

**Location:** `agentpm/reality/check.py`

**Function Signature:**
```python
def reality_check(mode: str = "HINT", skip_dashboards: bool = False) -> dict[str, Any]
```

**Parameters:**
- `mode`: `"HINT"` (default) or `"STRICT"`
  - **HINT mode (hermetic)**: Used on PRs and local dev. Fails soft: exits 0 if critical infra (env/DSN + DB/control-plane) is OK, but collects hints about missing or non-critical pieces (e.g., LM offline, no sample data, missing exports).
  - **STRICT mode (live-ready)**: Used on tags/releases and local strict bringup. Fails hard: any serious mismatch (DSN, control-plane schema, LM config, or eval smokes) → non-zero exit, recorded as violation.
- `skip_dashboards`: If `True`, skip exports and eval smoke checks (useful for infra-only validation).

**Returns:**
Dictionary with complete verdict containing:
- `command`: `"reality.check"`
- `mode`: `"HINT"` or `"STRICT"`
- `timestamp`: ISO 8601 timestamp
- `env`: Environment and DSN status
- `db`: DB and control plane status
- `lm`: LM health and slot status
- `exports`: Control plane export file status (if not skipped)
- `eval_smoke`: Eval smoke test results (if not skipped)
- `hints`: List of hint messages
- `overall_ok`: Boolean indicating if system passed validation for the given mode

**Behavior:**
- In **HINT mode**: Core infra (env/DSN, DB/control) must be OK; LM/exports/eval failures produce hints but don't fail the check. Used on PRs and local dev.
- In **STRICT mode**: All components must be OK or the check fails. Used on tags/releases and local strict bringup (e.g., `make bringup.live`).

**CLI Mapping:**
- `pmagent reality-check check --mode hint` → calls `reality_check(mode="HINT", skip_dashboards=False)`
- `pmagent reality-check check --mode strict` → calls `reality_check(mode="STRICT", skip_dashboards=False)`
- `pmagent reality-check check --no-dashboards` → calls `reality_check(mode="HINT", skip_dashboards=True)`
- Exit code: `0` if `overall_ok=True`, `1` if `overall_ok=False`

**Related Documentation:**
- `docs/SSOT/PMAGENT_REALITY_CHECK_DESIGN.md` - Full design specification
- `docs/SSOT/PMAGENT_CURRENT_VS_INTENDED.md` - Current vs intended state

## API Contracts

### Check Functions

#### `check_env_and_dsn() -> dict[str, Any]`
Validates environment variables and DSN availability using `scripts/config/env.py` helpers.

**Returns:**
- `ok`: Boolean indicating if env/DSN checks passed
- `dsn_ok`: Boolean indicating if at least RW DSN is available
- `details`: Dictionary with DSN availability details

#### `check_db_and_control() -> dict[str, Any]`
Validates DB and control plane status using `scripts/control/control_summary.py`.

**Returns:**
- `ok`: Boolean indicating if DB/control checks passed
- `control_schema`: Control schema name (typically `"control"`)
- `tables_expected`: Expected number of tables
- `tables_present`: Actual number of tables present
- Additional fields from `compute_control_summary()`

#### `check_lm_health_status() -> dict[str, Any]`
Validates LM health and model slot status using `scripts/guards/guard_lm_health.py` and `agentpm/lm/lm_status.py`.

**Returns:**
- `ok`: Boolean indicating if LM checks passed
- `provider`: LM provider name (`"lm_studio"`, `"ollama"`, etc.)
- `slots`: Dictionary with per-slot status (local_agent, embedding, reranker, theology)
- Additional fields from `check_lm_health()` and `compute_lm_status()`

#### `check_control_plane_exports() -> dict[str, Any]`
Validates control plane export files (hermetic JSON loader pattern).

**Returns:**
- `ok`: Boolean (always `True` in HINT mode; missing files are OK)
- `lm_indicator`: LM indicator JSON data or `None`
- `compliance_head`: Compliance summary JSON data or `None`
- `kb_docs_head`: KB docs summary JSON data or `None`
- `mcp_catalog`: MCP catalog JSON data or `None`

#### `run_eval_smoke() -> dict[str, Any]`
Runs eval smoke tests via make targets (`ci.exports.smoke`, `eval.graph.calibrate.adv`).

**Returns:**
- `ok`: Boolean indicating if all smoke tests passed
- `targets`: List of make targets executed
- `messages`: List of result messages per target

### Helper Functions

#### `print_human_summary(verdict: dict[str, Any], file=None) -> None`
Prints human-readable summary of verdict to stderr (or specified file).

#### `summarize_live_status(verdict: dict[str, Any]) -> str`
Builds a single-line LIVE STATUS banner based on subsystem health.

### `capability_envelope_validator.py`

**Purpose:** Hermetic validator for capability_session envelopes (from `pmagent plan reality-loop`). Checks envelopes against the future AI tracking mapping contract without writing to DB.

**Location:** `agentpm/reality/capability_envelope_validator.py`

**Key Functions:**

#### `validate_capability_envelope(envelope: dict[str, Any]) -> dict[str, Any]`
Validates a capability_session envelope dict against the AI tracking mapping contract.

**Returns:**
- `ok`: bool (True if all required fields present and valid)
- `errors`: list[str] (structural errors that prevent mapping)
- `warnings`: list[str] (missing optional fields or inconsistencies)
- `derived_tracking`: dict (computed fields for future DB mapping):
  - `command`: str (for control.agent_run_cli.command)
  - `request_json`: dict (full envelope for control.agent_run_cli.request_json)
  - `timestamp`: str (RFC3339 timestamp)

#### `validate_capability_envelope_file(path: Path) -> dict[str, Any]`
Validates a capability_session JSON file (wraps `validate_capability_envelope`).

**Returns:**
- Same as `validate_capability_envelope` plus:
  - `file_path`: str (path to the file)
  - `file_error`: str | None (if file read/parse failed)

#### `scan_capability_envelopes(evidence_dir: Path | None = None) -> dict[str, Any]`
Scans all capability_session envelopes in `evidence/pmagent/` and validates them.

**Returns:**
- `total_files`: int (total JSON files found)
- `ok_count`: int (files that passed validation)
- `error_count`: int (files with structural errors)
- `warning_count`: int (files with warnings but no errors)
- `files_with_errors`: list[dict] (file paths and error lists)
- `files_with_warnings`: list[dict] (file paths and warning lists)

**CLI Mapping:**
- `pmagent reality validate-capability-envelope <file> --json-only` → calls `validate_capability_envelope_file()`
- `pmagent reality validate-capability-history --json-only` → calls `scan_capability_envelopes()`

#### `validate_and_optionally_persist(envelope: dict[str, Any], *, tracking_enabled: bool) -> dict[str, Any]`
Validates a capability_session envelope and optionally persists to DB (gated by `tracking_enabled` flag).

**Returns:**
- Same as `validate_capability_envelope` plus:
  - `tracking`: dict | None (persistence result if `tracking_enabled=True` and validation passed)

**Behavior:**
- Always runs validation first (hermetic)
- If validation fails OR `tracking_enabled=False`: Returns validation result only (no DB calls)
- If validation passes AND `tracking_enabled=True`: Calls `maybe_persist_capability_session()` and merges result under `"tracking"` key

### `capability_envelope_writer.py`

**Purpose:** Gated writer path for persisting capability_session envelopes to `control.agent_run_cli`. All writes are behind an explicit opt-in flag and gracefully handle DB-off scenarios.

**Location:** `agentpm/reality/capability_envelope_writer.py`

**Key Functions:**

#### `maybe_persist_capability_session(envelope: dict[str, Any], *, tracking_enabled: bool) -> dict[str, Any]`
Optionally persists a capability_session envelope to `control.agent_run_cli`.

**Parameters:**
- `envelope`: Capability session envelope dict (from JSON file)
- `tracking_enabled`: If `False`, returns immediately with `mode="disabled"` (no DB calls)

**Returns:**
- `written`: bool (True if row was inserted)
- `mode`: str (`"disabled"` | `"db_off"` | `"db_on"` | `"error"`)
- `agent_run_cli_id`: str | None (UUID string if written, None otherwise)
- `error`: str | None (error message if `mode="error"`)

**Behavior:**
- **Hermetic**: Returns structured results; no exceptions raised
- **DB-off behavior**: Returns `{"written": False, "mode": "db_off"}` when DB unavailable
- **Mapping**: Uses `plan.dry_run_command` if present and non-empty, else `"plan.reality-loop"` for `command` field
- **Request JSON**: Stores full envelope structure in `request_json` field
- **Status**: Always sets `status="started"` (envelope represents planned work, not executed)

**DB Integration:**
- Uses `agentpm.control_plane.create_agent_run()` helper
- All DB failures are caught and returned as structured results (no exceptions)
- No side effects when DB is unavailable (hermetic behavior)

**Related Documentation:**
- `docs/SSOT/CAPABILITY_SESSION_AI_TRACKING_MAPPING.md` - Mapping design and writer contract
- `agentpm/plan/AGENTS.md` - Planning shell (reality-loop + history)
- `agentpm/control_plane.py` - `create_agent_run()` helper

### `sessions_summary.py`

**Purpose:** Read-only summary of capability_session envelopes and tracking posture. Provides a "reality lane" view of planned work sessions without changing any writer behavior.

**Location:** `agentpm/reality/sessions_summary.py`

**Key Functions:**

#### `summarize_tracked_sessions(*, limit: int = 20, evidence_dir: Path | None = None) -> dict[str, Any]`
Reads capability_session envelopes from `evidence/pmagent/` and returns a structured summary.

**Parameters:**
- `limit`: Maximum number of latest sessions to include (default: 20)
- `evidence_dir`: Directory containing capability_session files (defaults to `evidence/pmagent/`)

**Returns:**
- `envelopes`: dict with:
  - `count`: int (total number of capability_session files found)
  - `latest`: list[dict] (up to `limit` entries, sorted newest-first, each with: `id`, `title`, `source`, `dry_run_command`, `posture_mode`, `envelope_path`, `ts`)
- `tracking`: dict with:
  - `enabled_hint`: bool (based on `PMAGENT_TRACK_SESSIONS` env var, no side effects)
  - `db_mode`: str (`"db_on"` | `"db_off"` - detected via `get_rw_dsn()`)
  - `agent_run_cli`: dict | None (future: counts and mode histogram; currently `None` when DB-off or query not implemented)

**Behavior:**
- **Hermetic**: File-only reads, optional DB reads (gracefully handles DB-off)
- **DB-off behavior**: `agent_run_cli` fields set to `None`, `db_mode="db_off"` (still exits 0)
- **Invalid files**: Skips invalid JSON files gracefully (logs no errors, continues processing)
- **Timestamp extraction**: Uses filename (RFC3339 format) or envelope `timestamp` field as fallback

**CLI Mapping:**
- `pmagent reality sessions --limit N [--json-only]` → calls `summarize_tracked_sessions(limit=N)`
- JSON always printed to stdout; human-readable summary to stderr when not `--json-only`
- Exit code: `0` always (read-only, advisory)

**Related Documentation:**
- `agentpm/plan/AGENTS.md` - Planning shell (reality-loop + history)
- `docs/SSOT/CAPABILITY_SESSION_AI_TRACKING_MAPPING.md` - Mapping design

## Testing Strategy

**Unit Tests:**
- Test each check function independently with mocked dependencies
- Test `reality_check()` with different modes (HINT/STRICT) and `skip_dashboards` flag
- Verify verdict shape and `overall_ok` logic for both modes

**Integration Tests:**
- Test full `reality_check()` with real DB/LM (when available) and hermetic fallbacks
- Verify exit codes match `overall_ok` flag

**CLI Tests:**
- Test `pmagent reality-check check` command with `--mode hint/strict` and `--json-only` flags
- Verify JSON output shape and exit codes

## Development Guidelines

- All checks should be hermetic (work without DB/LM when unavailable)
- HINT mode should never fail on missing non-critical components
- STRICT mode should fail hard on any component failure
- Use existing helpers from `scripts/` and `agentpm/` rather than duplicating logic
- Follow the JSON verdict shape defined in `PMAGENT_REALITY_CHECK_DESIGN.md`

## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
| `reality_check()` | ADR-066 (LM Studio Control Plane Integration) |
| Control plane checks | ADR-065 (Postgres SSOT) |
| LM health checks | ADR-066 (LM Studio Control Plane Integration) |
