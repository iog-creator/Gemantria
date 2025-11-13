# AGENTS.md - Consumers Directory

## Directory Purpose

The `docs/consumers/` directory contains documentation for data consumers and export interfaces. This directory documents how external systems and tools consume Gemantria pipeline outputs, including noun indices, temporal strips, and envelope formats.

## Key Documents

### Consumer Documentation

- **NOUN_INDEX.md** - Noun Consumer Bridge Documentation
  - Documents noun index export format and usage
  - Provides SQL queries for direct database access
  - Includes acceptance criteria for headless verification
  - Export script: `scripts/export_noun_index.py`
  - Outputs: `share/exports/nouns.jsonl`, `share/exports/envelope.json`

- **TEMPORAL_STRIP.md** - Temporal Data Consumer Documentation
  - Documents temporal pattern consumption interfaces
  - Provides access patterns for time-series data
  - Includes visualization integration guidelines

## Documentation Standards

### Consumer Interface Documentation

All consumer documentation should include:

1. **Purpose** - What data is consumed and why
2. **Access Methods** - Scripts, SQL queries, or API endpoints
3. **Output Formats** - JSON, JSONL, or other data formats
4. **Usage Examples** - Code samples and command-line examples
5. **Acceptance Criteria** - How to verify consumer outputs

### Export Format Standards

- **JSONL format**: One JSON object per line for streaming consumption
- **Envelope format**: Wrapped data with metadata and schema version
- **SQL access**: Direct database queries for advanced consumers
- **Make targets**: Convenient `make` commands for common exports

## Development Guidelines

### Creating Consumer Documentation

1. **Identify consumer**: Document who/what consumes the data
2. **Document access**: Provide scripts, SQL, or API documentation
3. **Show examples**: Include working code samples and commands
4. **Define acceptance**: Specify verification criteria and tests
5. **Link exports**: Reference export scripts and Makefile targets

### Export Script Standards

- **DB-off tolerance**: Scripts must handle missing database gracefully
- **JSON evidence**: Emit structured JSON with `ok` status and error messages
- **Makefile targets**: Provide convenient `make` commands for execution
- **Schema validation**: Validate outputs against JSON schemas when available

## Related Documentation

### Export Scripts

- **scripts/export_noun_index.py**: Noun index export with envelope generation
- **scripts/export_graph.py**: Graph data export with nodes and edges
- **scripts/extract/extract_all.py**: Unified envelope extraction

### Makefile Targets

- **make exports.write**: Generate all export artifacts
- **make accept.ui**: Verify envelope format and content
- **make ui.extract.all**: Extract unified envelope for UI consumption

## Integration with Governance

### Rule 038 - Exports Smoke Gate

Consumer documentation supports export validation:

- **Format compliance**: Documents expected export formats
- **Schema validation**: References JSON schemas for validation
- **Acceptance criteria**: Defines verification procedures

### Rule 030 - Share Sync

Consumer outputs are synchronized to `share/` directory:

- **Export location**: Documents `share/exports/` structure
- **Sync procedures**: References `make share.sync` for synchronization
- **Artifact tracking**: Links to share manifest for artifact inventory

## Maintenance Notes

- **Keep current**: Update consumer docs when export formats change
- **Test examples**: Verify all code samples and commands work
- **Link schemas**: Maintain links to JSON schema definitions
- **Document changes**: Note breaking changes in export formats
