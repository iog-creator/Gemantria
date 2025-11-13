# AGENTS.md - Phase 9 Directory

## Directory Purpose

The `docs/phase9/` directory contains documentation for Phase 9 real-data ingestion, envelope formats, snapshot management, and validation procedures. This directory documents the ingestion harness interfaces, data formats, and snapshot rotation strategies.

## Key Documents

### Phase 9 Documentation

- **INGESTION_PLAN.md** - Phase-9 Real-Data Ingestion Plan
  - Documents ingestion harness interfaces (reader, validator, snapshot rotation)
  - Specifies environment variables (DATABASE_URL/PG*, SNAPSHOT_DIR, MAX_ROWS)
  - Proves hermeticity: `make ci.ingest.check` must HINT+exit 0 in CI
  - Defines contracts (no writes to share/ in CI, no outbound network, rerun-safe)

- **INGEST_ENVELOPE.md** - Ingestion Envelope Format Documentation
  - Documents envelope structure and field definitions
  - Specifies schema version and metadata requirements
  - Provides envelope validation procedures

- **ENVELOPE_FIELDS.md** - Envelope Field Reference
  - Detailed field definitions and data types
  - Required vs optional fields
  - Field validation rules and constraints

- **SNAPSHOTS.md** - Snapshot Management Documentation
  - Documents snapshot rotation strategies
  - Specifies snapshot naming and storage conventions
  - Provides snapshot validation and recovery procedures

- **VALIDATION_README.md** - Validation Procedures
  - Documents validation workflows and acceptance criteria
  - Specifies validation scripts and Makefile targets
  - Provides troubleshooting guidance

- **MAPPINGS.md** - Data Mapping Documentation
  - Documents field mappings between source and target formats
  - Specifies transformation rules and data conversions
  - Provides mapping validation procedures

- **FIRST_SNAPSHOT_PLAN.md** - Initial Snapshot Strategy
  - Documents first snapshot creation procedures
  - Specifies baseline data requirements
  - Provides snapshot verification steps

## Documentation Standards

### Phase 9 Documentation Format

All Phase 9 documentation should include:

1. **Purpose** - What the document describes and why
2. **Contracts** - Hermetic CI requirements and constraints
3. **Procedures** - Step-by-step workflows and validation steps
4. **Format Specs** - Data structure definitions and schemas
5. **Validation** - Acceptance criteria and verification procedures

### Hermetic CI Contracts

- **No writes to share/**: CI must not write to share/ directory
- **No outbound network**: CI must remain hermetic (no external dependencies)
- **Rerun-safe**: Idempotent snapshots with deterministic seeds
- **HINT+exit 0**: CI checks must HINT and exit 0 (never fail CI)

## Development Guidelines

### Creating Phase 9 Documentation

1. **Document interfaces**: Specify ingestion harness interfaces and contracts
2. **Hermetic compliance**: Document CI restrictions and hermetic requirements
3. **Format specs**: Provide detailed data format and schema documentation
4. **Validation**: Document validation procedures and acceptance criteria
5. **Snapshots**: Document snapshot management and rotation strategies

### Ingestion Script Standards

- **DB-off tolerance**: Scripts must handle missing database gracefully
- **Hermetic CI**: CI checks must HINT+exit 0, never fail CI
- **Idempotent**: Snapshots must be rerun-safe with deterministic seeds
- **Validation**: All ingestion outputs must be validated against schemas

## Related Documentation

### Ingestion Workflows

- **docs/ingestion/REAL_DATA_INGESTION.md**: Real-data ingestion procedures
- **scripts/pipeline_orchestrator.py**: Unified pipeline orchestration
- **make book.go**: Execute full book ingestion workflow

### Envelope Formats

- **schemas/ingest_envelope.schema.draft.json**: JSON schema for ingestion envelopes
- **docs/consumers/**: Data consumer interfaces and export formats
- **scripts/extract/extract_all.py**: Unified envelope extraction

## Integration with Governance

### Rule 046 - Hermetic CI Fallbacks

Phase 9 enforces hermetic CI requirements:

- **No network/DB**: CI must remain hermetic (no external dependencies)
- **DB-off tolerance**: Scripts handle missing database gracefully
- **HINT+exit 0**: CI checks emit HINTs and exit 0 (never fail CI)

### Rule 037 - Data Persistence Completeness

Phase 9 ensures complete data persistence:

- **Snapshot management**: Documents snapshot storage and rotation
- **Envelope validation**: Ensures all required fields are present
- **Schema compliance**: Validates data against JSON schemas

### Rule 038 - Exports Smoke Gate

Phase 9 supports export validation:

- **Format compliance**: Documents expected envelope formats
- **Schema validation**: References JSON schemas for validation
- **Acceptance criteria**: Defines verification procedures

## Maintenance Notes

- **Keep current**: Update Phase 9 docs when ingestion workflows change
- **Test procedures**: Verify all ingestion steps work as documented
- **Schema updates**: Update envelope schemas when formats change
- **CI compliance**: Ensure all ingestion procedures remain CI-hermetic
