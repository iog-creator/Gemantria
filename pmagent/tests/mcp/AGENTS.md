# AGENTS.md - pmagent/tests/mcp Directory

## Directory Purpose

The `pmagent/tests/mcp/` directory contains tests for MCP (Model Context Protocol) components, including Knowledge MCP foundation tests (PLAN-073 M1).

## Key Test Files

### `test_mcp_catalog_e01_e05.py` — Knowledge MCP Foundation Tests (PLAN-073 M1)

**Purpose:** Test suite for Knowledge MCP foundation components (E01-E05).

**E01 Tests:**
- `test_e01_schema_guard_exists()` - Verifies schema guard script exists
- `test_e01_schema_guard_hint_mode()` - Verifies guard runs in HINT mode with DB-off (hermetic-friendly)
- `test_e01_schema_guard_evidence_file()` - Verifies guard writes evidence file

**E02 Tests:**
- `test_e02_echo_dsn_ro_redacts_credentials()` - Verifies echo_dsn_ro.py redacts credentials in DSN output
- `test_e02_guard_mcp_db_ro_hint_mode_db_off()` - Verifies guard runs in HINT mode with DB-off (hermetic-friendly)
- `test_e02_guard_mcp_db_ro_redaction_proof()` - Verifies guard generates redaction proof artifact

**E03 Tests:**
- `test_e03_ingest_envelope_validates_schema()` - Verifies ingest script validates envelope against schema
- `test_e03_ingest_envelope_db_off_hint_mode()` - Verifies ingest exits 0 in HINT mode when DB unavailable
- `test_e03_ingest_envelope_idempotent()` - Verifies ingest is idempotent (two runs produce same row counts)

**E04 Tests:**
- `test_e04_query_catalog_db_off_hint_mode()` - Verifies query script exits 0 in HINT mode when DB unavailable
- `test_e04_query_catalog_output_shape()` - Verifies query outputs valid JSON with expected keys
- `test_e04_guard_mcp_query_writes_evidence()` - Verifies guard writes evidence file with ok flag

**E05 Tests:**
- `test_e05_generate_proof_snapshot_builds_expected_shape()` - Verifies snapshot generator creates expected JSON and TXT files
- `test_e05_guard_mcp_proof_validates_schema_and_overall_ok()` - Verifies guard validates schema and overall_ok consistency

**Test Strategy:**
- Hermetic-friendly: Tests tolerate DB-off scenarios
- HINT mode validation: Ensures guards exit 0 in HINT mode even when DB unavailable
- Evidence file validation: Verifies guard outputs are written correctly
- Redaction validation: Ensures DSN credentials are never exposed in output

**Related:**
- **PLAN-073 M1**: Knowledge MCP Foundation
- **E01 Guard**: `scripts/guards/guard_mcp_schema.py`
- **E02 Echo Helper**: `scripts/mcp/echo_dsn_ro.py`
- **E02 Guard**: `scripts/ci/guard_mcp_db_ro.py`
- **Schema**: `db/sql/078_mcp_knowledge.sql`

## Testing Guidelines

- All tests should be hermetic-friendly (tolerate missing DB/services)
- Use subprocess to run guard scripts for integration testing
- Verify JSON output structure and evidence file generation
- Tests should pass in both HINT and STRICT modes when appropriate

