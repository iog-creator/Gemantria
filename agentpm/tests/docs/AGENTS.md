# AGENTS.md - Tests/Docs Directory

## Directory Purpose

The `agentpm/tests/docs/` directory contains tests for DMS (Documentation Management System) guards and related documentation validation components.

## Test Files

### `test_dms_guards.py` — DMS Guards Test Suite (PLAN-072 M1)

**Purpose:** Comprehensive test coverage for DMS guard HINT/STRICT mode behavior, DB-off tolerance, and output shape validation.

**Test Coverage:**

1. **`test_guard_docs_db_ssot_outputs_expected_shape`**
   - Validates guard outputs expected JSON structure
   - Checks required fields: `ok`, `mode`, `reason`, `details`, `generated_at`
   - Verifies `mode` is one of: "ready", "db_off", "partial"
   - Validates `details` structure (total_local_docs, total_registry_docs, missing lists)

2. **`test_guard_docs_db_ssot_hint_mode_db_off_tolerated`**
   - Verifies HINT mode tolerates DB-off (exits 0)
   - Mocks `get_control_engine()` to raise exception (simulating DB-off)
   - Asserts exit code 0, `ok=false`, `mode="db_off"`, hints array present

3. **`test_guard_docs_db_ssot_strict_mode_db_off_fails`**
   - Verifies STRICT mode fails when DB is off (exits 1)
   - Mocks `get_control_engine()` to raise exception
   - Asserts exit code 1, `ok=false`, `mode="db_off"`, no hints array

4. **`test_guard_docs_db_ssot_hint_mode_partial_tolerated`**
   - Verifies HINT mode tolerates partial sync (exits 0)
   - Mocks DB connection with missing docs in registry
   - Asserts exit code 0 even when sync is partial

5. **`test_guard_docs_db_ssot_strict_mode_partial_fails`**
   - Verifies STRICT mode fails when sync is partial (exits 1)
   - Mocks DB connection with missing docs
   - Asserts exit code 1 when `ok=false` in STRICT mode

6. **`test_guard_docs_db_ssot_strict_mode_success_exits_zero`**
   - Verifies STRICT mode exits 0 when sync is complete (`ok=true`)
   - Mocks successful DB connection with all docs in sync
   - Asserts exit code 0, `ok=true`, `mode="ready"`

7. **`test_guard_docs_consistency_runs`**
   - Happy-path test for `guard_docs_consistency.py`
   - Verifies guard runs without errors
   - Checks output structure (scanned, ok, fails fields)

**Test Approach:**
- Uses `unittest.mock` to simulate DB-off and partial sync scenarios
- No real DB required (hermetic tests)
- Subprocess execution for guard scripts to test actual behavior
- Validates both exit codes and JSON output structure

**Usage:**
```bash
pytest agentpm/tests/docs/test_dms_guards.py -q -v
pytest agentpm/tests/docs/test_dms_guards.py::TestGuardDocsDbSsot -v
```

**Related:**
- **PLAN-072 M1**: DMS guard fixes — See `docs/SSOT/PLAN_072_M1_DMS_GUARDS.md`
- **Guard**: `scripts/guards/guard_docs_db_ssot.py`
- **Guard**: `scripts/guards/guard_docs_consistency.py`

