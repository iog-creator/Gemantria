# AGENTS.md - Ingestion Directory

## Directory Purpose

The `docs/ingestion/` directory contains documentation for data ingestion workflows, real-data processing, and pipeline input handling. This directory documents how raw data enters the Gemantria pipeline and is processed into structured formats.

## Key Documents

### Ingestion Documentation

- **REAL_DATA_INGESTION.md** - Real-Data Ingestion Plan (Phase-9, reuse-first)
  - Documents ingestion workflow for real biblical text data
  - Specifies DSN access patterns (centralized loaders required)
  - Defines minimal configuration knobs and environment variables
  - Provides local dev/operator steps (outside CI)
  - Documents hermetic CI behavior (no network/DB)

## Documentation Standards

### Ingestion Workflow Documentation

All ingestion documentation should include:

1. **Data Sources** - Where data comes from (bible_db, external files, etc.)
2. **DSN Access** - Database connection patterns (centralized loaders)
3. **Configuration** - Environment variables and configuration knobs
4. **Workflow Steps** - Step-by-step ingestion procedures
5. **CI Behavior** - Hermetic CI requirements and validation

### DSN Access Requirements

- **Centralized loaders**: All DSN access must use `scripts.config.env` (preferred) or `src.gemantria.dsn` (legacy)
- **Never direct**: Never use `os.getenv("GEMATRIA_DSN")` directly
- **Guard enforcement**: `guard.dsn.centralized` enforces centralized DSN usage
- **DSN precedence**: Document DSN precedence order (`.env.local` > `.env` > centralized loader)

## Development Guidelines

### Creating Ingestion Documentation

1. **Document sources**: Specify data sources and access methods
2. **DSN patterns**: Document centralized DSN loader usage
3. **Configuration**: List all environment variables and their purposes
4. **Workflow**: Provide step-by-step ingestion procedures
5. **CI compliance**: Document hermetic CI requirements

### Ingestion Script Standards

- **DB-off tolerance**: Scripts must handle missing database gracefully
- **Centralized DSNs**: Use centralized loaders, never direct `os.getenv()`
- **Hermetic CI**: CI must remain hermetic (no network/DB)
- **Local-only**: Ingestion steps are dev/operator only, not in CI

## Related Documentation

### DSN Management

- **scripts/config/env.py**: Centralized DSN loader functions
- **docs/runbooks/DSN_SECRETS.md**: DSN security and management practices
- **Rule 001**: DB Safety (read-only Bible DB, parameterized SQL)

### Ingestion Scripts

- **scripts/run_book.py**: Book processing with chapter orchestration
- **scripts/pipeline_orchestrator.py**: Unified pipeline orchestration
- **make book.go**: Execute full book ingestion workflow

## Integration with Governance

### Rule 001 - DB Safety

Ingestion documentation enforces database safety:

- **Read-only Bible DB**: Documents enforced read-only access
- **Parameterized SQL**: References parameterized query patterns
- **DSN centralization**: Enforces centralized DSN loader usage

### Rule 046 - Hermetic CI Fallbacks

Ingestion workflows support hermetic CI:

- **No network/DB**: CI must remain hermetic (no external dependencies)
- **DB-off tolerance**: Scripts handle missing database gracefully
- **Local-only steps**: Ingestion procedures are dev/operator only

### Rule 062 - Environment Validation

Ingestion requires environment validation:

- **Venv activation**: Documents virtual environment activation
- **DSN verification**: Procedures for verifying database connections
- **Configuration checks**: Validates environment setup before ingestion

## Maintenance Notes

- **Keep current**: Update ingestion docs when workflows change
- **Test procedures**: Verify all ingestion steps work as documented
- **DSN updates**: Update DSN access patterns when loaders change
- **CI compliance**: Ensure all ingestion procedures remain CI-hermetic
