# PLAN-073 M1: Knowledge MCP Foundation (E01–E05)

**Status**: 📋 PLANNING/DESIGN  
**Related**: RFC-078 (Postgres Knowledge MCP), Rule-050/051/052, ADR-065 (Postgres SSOT)  
**Goal**: Implement minimal, hermetic Knowledge MCP foundation with read-only database access, envelope ingestion, query roundtrip, and proof snapshots.

---

## Overview

PLAN-073 M1 implements the foundational components for the Postgres-backed Knowledge MCP (RFC-078). This milestone establishes:

1. **Schema validation** (E01) — Ensure Knowledge MCP schema files/tables exist
2. **RO-DSN guard** (E02) — Add read-only DSN guard with redaction proof
3. **Envelope ingestion** (E03) — File→row ingest path (hermetic-friendly)
4. **Query roundtrip** (E04) — Minimal query over MCP tables (deterministic output)
5. **Proof snapshot** (E05) — Proof snapshot written under share/ with Atlas linkage

All components are **hermetic-friendly** (no external deps) and **off by default** (opt-in via environment flags).

---

## E01: Schema Files/Tables Existence

### Goal
Ensure Knowledge MCP schema files/tables exist (read-only lane). Provide minimal seed or describe via guard.

### Current State
- ✅ Schema file exists: `db/sql/078_mcp_knowledge.sql`
- ✅ Defines: `mcp.tools`, `mcp.endpoints`, `mcp.logs`, `mcp.v_catalog` view
- ⚠️ No guard to validate schema presence
- ⚠️ No minimal seed data

### Implementation Requirements

**Schema Guard** (`scripts/guards/guard_mcp_schema.py`):
- Validates `mcp` schema exists
- Validates required tables exist: `mcp.tools`, `mcp.endpoints`, `mcp.logs`
- Validates `mcp.v_catalog` view exists
- Hermetic: Uses centralized DSN loader, tolerates DB-off (HINT mode)
- STRICT mode: Fails if schema/tables/view missing
- Output: JSON verdict to `evidence/guard_mcp_schema.json`

**Minimal Seed** (`db/sql/078_mcp_knowledge_seed.sql`):
- Optional seed file with 3–5 example tools/endpoints
- Idempotent (INSERT ... ON CONFLICT DO NOTHING)
- Documents expected structure
- Not required for guard to pass (guard validates structure, not content)

**Make Targets**:
```makefile
# Apply schema (idempotent)
mcp.schema.apply:
	psql "$(GEMATRIA_DSN)" -f db/sql/078_mcp_knowledge.sql

# Apply seed (optional)
mcp.schema.seed:
	psql "$(GEMATRIA_DSN)" -f db/sql/078_mcp_knowledge_seed.sql

# Guard schema presence
guard.mcp.schema:
	python scripts/guards/guard_mcp_schema.py
```

**Guard Contract**:
- **HINT mode (default)**: Tolerates missing DB/schema, emits hints
- **STRICT mode**: Requires schema/tables/view to exist, fails if missing
- **Output format**: JSON with `ok`, `schema_exists`, `tables_present`, `view_exists`, `details`

---

## E02: RO-DSN Guard + Redaction Proof

### Goal
Add RO-DSN guard + redaction proof (echo target + guard JSON).

### Current State
- ✅ Guard exists: `scripts/ci/guard_mcp_db_ro.py`
- ✅ Validates `mcp.v_catalog` view via RO DSN
- ⚠️ No DSN redaction proof
- ⚠️ No echo target for DSN verification

### Implementation Requirements

**DSN Echo Target** (`make mcp.dsn.echo`):
- Prints redacted DSN (user/password masked as `<REDACTED>`)
- Uses centralized DSN loader (`get_ro_dsn()` or `get_mcp_ro_dsn()`)
- Shows which DSN source was used (ATLAS_DSN_RO, GEMATRIA_RO_DSN, etc.)
- Never prints raw credentials
- Format: `postgresql://<REDACTED>@host:port/database`

**Enhanced Guard** (`scripts/guards/guard_mcp_db_ro.py`):
- Extends existing guard with DSN redaction proof
- Validates DSN is redacted in all output (no raw credentials)
- Generates redaction proof artifact: `evidence/guard_mcp_db_ro_redaction.json`
- Verifies RO DSN connectivity (read-only, no writes)
- Validates `mcp.v_catalog` is accessible via RO DSN

**Make Targets**:
```makefile
# Echo redacted DSN (for operator sanity)
mcp.dsn.echo:
	python scripts/mcp/echo_dsn_ro.py

# Guard RO DSN + redaction
guard.mcp.db.ro:
	python scripts/guards/guard_mcp_db_ro.py
```

**Guard Contract**:
- **HINT mode (default)**: Tolerates missing DSN, emits hints
- **STRICT mode**: Requires RO DSN + `mcp.v_catalog` access, fails if missing
- **Redaction proof**: Validates no raw credentials in output/artifacts
- **Output format**: JSON with `ok`, `dsn_redacted`, `ro_access`, `view_accessible`, `redaction_proof`

---

## E03: Envelope Ingest Path

### Goal
Envelope ingest path (file→row), hermetic-friendly (no external deps).

### Current State
- ⚠️ No ingest script exists
- ⚠️ No envelope format defined
- ✅ Schema supports tools/endpoints ingestion

### Implementation Requirements

**Envelope Format** (`schemas/mcp_ingest_envelope.v1.schema.json`):
- JSON Schema for Knowledge MCP ingest envelope
- Fields:
  - `schema`: `"mcp_ingest_envelope.v1"`
  - `generated_at`: RFC3339 timestamp
  - `tools`: Array of tool objects (name, desc, tags, cost_est, visibility)
  - `endpoints`: Array of endpoint objects (name, path, method, auth, notes)
- Hermetic: No external schema dependencies

**Ingest Script** (`scripts/mcp/ingest_envelope.py`):
- Reads envelope JSON file
- Validates against schema
- Inserts/updates `mcp.tools` and `mcp.endpoints` tables
- Idempotent: Uses `INSERT ... ON CONFLICT DO UPDATE`
- Hermetic: No external deps (uses psycopg, centralized DSN loader)
- Tolerates DB-off: Exits 0 with error message if DB unavailable

**Make Targets**:
```makefile
# Ingest envelope from file
mcp.ingest:
	python scripts/mcp/ingest_envelope.py --envelope <path>

# Ingest from default location
mcp.ingest.default:
	python scripts/mcp/ingest_envelope.py --envelope share/mcp/envelope.json
```

**Ingest Contract**:
- **Input**: JSON envelope file (validated against schema)
- **Output**: Row counts (inserted, updated, skipped)
- **Idempotent**: Re-running with same envelope produces same final state
- **Hermetic**: No network calls, no external services
- **Error handling**: Graceful failure with clear error messages

---

## E04: Minimal Query Roundtrip

### Goal
Minimal query roundtrip over MCP tables (deterministic output).

### Current State
- ✅ `mcp.v_catalog` view exists (JOIN of tools + endpoints)
- ✅ Export script exists: `scripts/db/control_mcp_catalog_export.py`
- ⚠️ No minimal query script for testing roundtrip

### Implementation Requirements

**Query Script** (`scripts/mcp/query_catalog.py`):
- Executes minimal query: `SELECT * FROM mcp.v_catalog ORDER BY name LIMIT 10`
- Uses centralized DSN loader (RO DSN preferred)
- Deterministic output: Always returns same results for same data
- Output format: JSON array of catalog entries
- Hermetic: No external deps, tolerates DB-off

**Query Guard** (`scripts/guards/guard_mcp_query.py`):
- Validates query script executes successfully
- Validates output is deterministic (same query → same results)
- Validates output matches expected schema
- Generates query proof: `evidence/guard_mcp_query.json`

**Make Targets**:
```makefile
# Query catalog (minimal roundtrip)
mcp.query:
	python scripts/mcp/query_catalog.py

# Guard query roundtrip
guard.mcp.query:
	python scripts/guards/guard_mcp_query.py
```

**Query Contract**:
- **Query**: `SELECT * FROM mcp.v_catalog ORDER BY name LIMIT 10`
- **Deterministic**: Same data → same output (no randomness)
- **Output**: JSON array with catalog entries (name, desc, tags, path, method, etc.)
- **Hermetic**: No external deps, tolerates DB-off (HINT mode)

---

## E05: Proof Snapshot

### Goal
Proof snapshot written under share/ (json + txt pointers), linked from Atlas if present.

### Current State
- ✅ Proof artifacts exist: `share/mcp/*.json` (E21–E25 proofs)
- ⚠️ No unified Knowledge MCP proof snapshot
- ⚠️ No Atlas linkage

### Implementation Requirements

**Proof Snapshot Script** (`scripts/mcp/generate_proof_snapshot.py`):
- Aggregates E01–E04 proof artifacts:
  - Schema guard verdict (`evidence/guard_mcp_schema.json`)
  - RO DSN guard verdict (`evidence/guard_mcp_db_ro.json`)
  - Query guard verdict (`evidence/guard_mcp_query.json`)
  - Ingest envelope (if present: `share/mcp/envelope.json`)
- Generates unified proof snapshot: `share/mcp/knowledge_mcp_proof.json`
- Generates human-readable summary: `share/mcp/knowledge_mcp_proof.txt`
- Includes pointers to all component proofs

**Proof Snapshot Schema** (`schemas/mcp_proof_snapshot.v1.schema.json`):
- JSON Schema for proof snapshot
- Fields:
  - `schema`: `"mcp_proof_snapshot.v1"`
  - `generated_at`: RFC3339 timestamp
  - `components`: Object with E01–E04 proof statuses
  - `artifacts`: Array of artifact paths (relative to repo root)
  - `overall_ok`: Boolean (all components pass)

**Atlas Linkage**:
- Updates `docs/atlas/index.html` to include Knowledge MCP proof tile (if proof exists)
- Links to `share/mcp/knowledge_mcp_proof.json` and `.txt`
- Shows proof status (green/yellow/red badge)
- Graceful fallback: Hides tile if proof doesn't exist

**Make Targets**:
```makefile
# Generate proof snapshot
mcp.proof.snapshot:
	python scripts/mcp/generate_proof_snapshot.py

# Guard proof snapshot
guard.mcp.proof:
	python scripts/guards/guard_mcp_proof.py
```

**Proof Contract**:
- **Input**: E01–E04 proof artifacts (schema guard, RO DSN guard, query guard, ingest envelope)
- **Output**: Unified proof snapshot JSON + human-readable TXT
- **Atlas linkage**: Conditional tile in Atlas index (only if proof exists)
- **Hermetic**: No external deps, tolerates missing components (HINT mode)

---

## Make Targets Summary

```makefile
# Schema management
mcp.schema.apply          # Apply schema (idempotent)
mcp.schema.seed           # Apply seed (optional)
guard.mcp.schema          # Guard schema presence

# DSN management
mcp.dsn.echo              # Echo redacted DSN
guard.mcp.db.ro           # Guard RO DSN + redaction

# Ingest
mcp.ingest                # Ingest envelope from file
mcp.ingest.default        # Ingest from default location

# Query
mcp.query                 # Query catalog (minimal roundtrip)
guard.mcp.query           # Guard query roundtrip

# Proof
mcp.proof.snapshot        # Generate proof snapshot
guard.mcp.proof           # Guard proof snapshot

# Bundle (all-in-one)
mcp.all                   # Run all E01–E05 steps
guard.mcp.all             # Guard all E01–E05 components
```

---

## Guard Contracts Summary

All guards follow the same pattern:

- **HINT mode (default)**: Tolerates missing DB/components, emits hints
- **STRICT mode**: Requires all components, fails if missing
- **Output format**: JSON verdict to `evidence/guard_mcp_*.json`
- **Hermetic**: No external deps, no network calls
- **DSN usage**: Centralized DSN loader only (no `os.getenv` direct)

---

## Artifacts

**Schema Files**:
- `db/sql/078_mcp_knowledge.sql` (existing)
- `db/sql/078_mcp_knowledge_seed.sql` (new, optional)

**Scripts**:
- `scripts/guards/guard_mcp_schema.py` (new)
- `scripts/mcp/echo_dsn_ro.py` (new)
- `scripts/guards/guard_mcp_db_ro.py` (enhance existing)
- `scripts/mcp/ingest_envelope.py` (new)
- `scripts/mcp/query_catalog.py` (new)
- `scripts/guards/guard_mcp_query.py` (new)
- `scripts/mcp/generate_proof_snapshot.py` (new)
- `scripts/guards/guard_mcp_proof.py` (new)

**Schemas**:
- `schemas/mcp_ingest_envelope.v1.schema.json` (new)
- `schemas/mcp_proof_snapshot.v1.schema.json` (new)

**Proof Artifacts**:
- `evidence/guard_mcp_schema.json` (E01)
- `evidence/guard_mcp_db_ro.json` (E02, enhanced)
- `evidence/guard_mcp_db_ro_redaction.json` (E02)
- `evidence/guard_mcp_query.json` (E04)
- `share/mcp/knowledge_mcp_proof.json` (E05)
- `share/mcp/knowledge_mcp_proof.txt` (E05)

**Tests**:
- `agentpm/tests/mcp/test_mcp_knowledge_e01_e05.py` (new, 5 tests)

---

## Implementation Order

1. **E01**: Schema guard + seed (foundation)
2. **E02**: RO DSN guard enhancement + redaction proof
3. **E03**: Ingest envelope script + schema
4. **E04**: Query script + guard
5. **E05**: Proof snapshot + Atlas linkage

Each step is independently testable and can be implemented incrementally.

---

## Acceptance Criteria

- [ ] E01: Schema guard passes (HINT/STRICT modes)
- [ ] E02: RO DSN guard enhanced with redaction proof
- [ ] E03: Ingest script works with envelope file (hermetic)
- [ ] E04: Query script returns deterministic output
- [ ] E05: Proof snapshot generated and linked from Atlas
- [ ] All guards pass in HINT mode (hermetic CI)
- [ ] All guards pass in STRICT mode (tag builds)
- [ ] Tests: 5 tests for E01–E05 (all passing)
- [ ] Make targets: All targets work (schema, guard, ingest, query, proof)
- [ ] Documentation: AGENTS.md updated with new scripts/guards

---

## Related Documentation

- **RFC-078**: Postgres Knowledge MCP (catalog-as-a-service)
- **Runbook**: `docs/runbooks/MCP_KNOWLEDGE_DB.md` (bring-up, RO vs RW)
- **Schema**: `db/sql/078_mcp_knowledge.sql` (existing schema)
- **Guard**: `scripts/ci/guard_mcp_db_ro.py` (existing RO guard)
- **Export**: `scripts/db/control_mcp_catalog_export.py` (existing export)

---

## Next Steps

After PLAN-073 M1 completion:

1. **PLAN-073 M2**: Enhanced ingest (batch processing, validation)
2. **PLAN-073 M3**: Query expansion (filtering, pagination, search)
3. **PLAN-073 M4**: Atlas integration (full UI, dashboards, visualizations)

