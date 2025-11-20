# AGENTS.md - agentpm/tools Directory

## Directory Purpose

The `agentpm/tools/` directory contains tool functions for system health, control plane, documentation, ledger verification, and reality checks. These tools are called by the `pmagent` CLI and provide structured JSON responses.

## Key Components

### `system.health()`

**Purpose:** System health check aggregating DB, LM, and Graph component status.

**Location:** `agentpm/tools/system.py`

**Function Signature:**
```python
def health(**kwargs: Any) -> dict[str, Any]
```

**Returns:**
Dictionary with:
- `ok`: Boolean (always `True`; individual component status in nested dicts)
- `db`: DB health status from `check_db_health()`
- `lm`: LM health status from `check_lm_health()`
- `graph`: Graph overview from `compute_graph_overview()`
- `system`: System health from `compute_system_health()`

**Implementation:**
- Calls `scripts/guards/guard_db_health.py::check_db_health()`
- Calls `scripts/guards/guard_lm_health.py::check_lm_health()`
- Calls `scripts/graph/graph_overview.py::compute_graph_overview()`
- Calls `scripts/system/system_health.py::compute_system_health()`

### `system.control_summary()`

**Purpose:** Control-plane summary with aggregated status information.

**Location:** `agentpm/tools/system.py`

**Function Signature:**
```python
def control_summary(**kwargs: Any) -> dict[str, Any]
```

**Returns:**
Dictionary with:
- `ok`: Boolean (always `True`)
- `summary`: Complete control summary from `compute_control_summary()`

**Implementation:**
- Calls `scripts/control/control_summary.py::compute_control_summary()`
- Returns full summary including status, tables, schema, and pipeline_status

### `system.docs_status()`

**Purpose:** Documentation status and inventory.

**Location:** `agentpm/tools/system.py`

**Function Signature:**
```python
def docs_status(**kwargs: Any) -> dict[str, Any]
```

**Returns:**
Dictionary with:
- `ok`: Boolean (always `True`)
- `inventory`: Documentation inventory from `run_inventory()`

**Implementation:**
- Calls `agentpm/scripts/docs_inventory.py::run_inventory()`

### `system.ledger_verify()`

**Purpose:** Verify system state ledger against current artifact hashes.

**Location:** `agentpm/tools/system.py`

**Function Signature:**
```python
def ledger_verify(**kwargs: Any) -> dict[str, Any]
```

**Returns:**
Dictionary with:
- `ok`: Boolean (True if exit_code == 0)
- `exit_code`: Exit code from `verify_ledger()`
- `summary`: Verification summary from `verify_ledger()`

**Implementation:**
- Calls `agentpm/scripts/state/ledger_verify.py::verify_ledger()`
- Returns tuple unpacked as `(exit_code, summary)`

### `system.reality_check()`

**Purpose:** Reality check for automated bring-up (wraps `agentpm.reality.check.reality_check()`).

**Location:** `agentpm/tools/system.py`

**Function Signature:**
```python
def reality_check(**kwargs: Any) -> dict[str, Any]
```

**Parameters (via kwargs):**
- `mode`: `"HINT"` or `"STRICT"` (default: `"HINT"`)
- `skip_dashboards`: Boolean (default: `False`)

**Returns:**
Dictionary with:
- `ok`: Boolean (True if `overall_ok` is True in result)
- `result`: Complete verdict from `reality_check()`

**Implementation:**
- Calls `agentpm/reality/check.py::reality_check()` with kwargs
- Extracts `overall_ok` from result to set `ok` flag
- Returns full result nested under `result` key

**Note:** This is a thin wrapper around the core `reality_check()` function. The core function handles all the validation logic; this tool function provides the standard tool interface.

**CLI Mapping:**
- Called by `pmagent reality-check check` command via `pmagent/cli.py`
- Parameters passed through from CLI flags (`--mode`, `--no-dashboards`)
- Return value's `ok` field matches `overall_ok` from the core function

## API Contracts

All tool functions follow a consistent pattern:

1. **Accept `**kwargs`** for flexibility (CLI can pass any parameters)
2. **Return `dict[str, Any]`** with at least an `ok` boolean
3. **Call underlying helpers** from `scripts/` or `agentpm/` modules
4. **Never raise exceptions** (handle errors gracefully, return error info in dict)

**Standard Return Shape:**
```python
{
    "ok": bool,  # Always present
    # ... additional fields specific to tool
}
```

## Testing Strategy

**Unit Tests:**
- Test each tool function with mocked dependencies
- Verify return shape matches expected structure
- Test error handling (graceful degradation)

**Integration Tests:**
- Test tools with real DB/LM (when available)
- Verify tool functions work correctly when called from CLI

**CLI Tests:**
- Test `pmagent` commands that call these tools
- Verify JSON output shape and exit codes

## Development Guidelines

- All tools should accept `**kwargs` for flexibility
- Always return a dict with at least an `ok` boolean
- Never raise exceptions; handle errors gracefully
- Use existing helpers from `scripts/` and `agentpm/` rather than duplicating logic
- Follow the standard tool return shape pattern

## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
| `system.health()` | ADR-066 (LM Studio Control Plane Integration) |
| `system.control_summary()` | ADR-065 (Postgres SSOT) |
| `system.reality_check()` | ADR-066 (LM Studio Control Plane Integration), PMAGENT_REALITY_CHECK_DESIGN.md |
| `system.ledger_verify()` | ADR-065 (Postgres SSOT) |
