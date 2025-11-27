# AGENTS.md - agentpm/docs Directory

## Directory Purpose

The `agentpm/docs/` directory contains documentation search and management components for the Gematria analysis pipeline, including semantic search, document classification, and documentation control panel operations.

## Key Components

| Component | Purpose | DB Requirement |
|-----------|---------|----------------|
| `search.py` | Semantic search over documentation content via control-plane embeddings | **REQUIRES DB** - Fails (exit 1) when DB unavailable |
| `docs_dashboard_refresh.py` | Generates documentation control panel exports (summary, canonical, archive candidates, unreviewed batch, orphans) | **REQUIRES DB** - Fails (exit 1) when DB unavailable |
| `docs_inventory.py` | Scans repository for markdown-like files and upserts metadata into `control.kb_document` | **REQUIRES DB** - Fails (exit 1) when DB unavailable |
| `docs_classify_direct.py` | Direct document classification - updates `control.kb_document` with canonical/archive_candidate status | **REQUIRES DB** - Fails (exit 1) when DB unavailable |
| `docs_dm002_sync.py` | Writes canonical/archive_candidate decisions from preview file into `control.kb_document` | **REQUIRES DB** - Fails (exit 1) when DB unavailable |
| `docs_dm002_preview.py` | Reads duplicate report and proposes canonical/archive classifications (does not touch DB) | **No DB required** - Works without DB |

## API Contracts

### `pmagent docs search <query>`
- **Purpose**: Semantic search over governance/docs content via control-plane embeddings
- **DB Requirement**: **REQUIRES DB** - Must fail (exit 1) when DB unavailable
- **Output**: JSON results with similarity scores and content snippets

### `pmagent docs dashboard-refresh`
- **Purpose**: Generate documentation control panel exports
- **DB Requirement**: **REQUIRES DB** - Must fail (exit 1) when DB unavailable
- **Output**: Exports to `share/exports/docs-control/` (summary.json, canonical.json, archive-candidates.json, unreviewed-batch.json, orphans.json)

### `pmagent docs inventory`
- **Purpose**: Scan repository and upsert document metadata into `control.kb_document`
- **DB Requirement**: **REQUIRES DB** - Must fail (exit 1) when DB unavailable
- **Output**: Summary of scanned/inserted/updated document counts

## Testing Strategy

- Commands that require DB must be tested with DB available and must fail correctly when DB unavailable
- Commands that don't require DB (e.g., `docs dm002-preview`) should work in hermetic/CI environments
- See `agentpm/tests/docs/` for test coverage

## Development Guidelines

- **DB-off handling (Rule-046)**: All operational commands in this directory **REQUIRE** the database and must **FAIL** (exit code 1) when DB unavailable. Print clear error: `"ERROR: This command requires the database to be available."`
- Use centralized DSN loaders from `scripts.config.env`; never call `os.getenv` for DSNs directly
- Semantic search uses control-plane embeddings stored in `control.kb_document` table
- Document classification updates `control.kb_document.is_canonical` and `control.kb_document.status` columns

## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
| Documentation search and classification | ADR-013 (Documentation synchronization), Rule-046 (Hermetic CI Fallbacks) |
| Control-plane document management | ADR-065 (Postgres SSOT), Rule-027 (Docs Sync Gate) |
