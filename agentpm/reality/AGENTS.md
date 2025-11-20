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
