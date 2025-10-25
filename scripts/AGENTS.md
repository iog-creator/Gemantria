# AGENTS.md - Scripts Directory

## Directory Purpose

The `scripts/` directory contains executable scripts for pipeline operations, reporting, testing, and maintenance tasks. These scripts provide command-line interfaces for common development and operational workflows.

## Key Scripts

### `models_verify.py` — LM Studio Model & Endpoint Verifier (NEW)

Purpose: Verify live LM Studio endpoints and configured models without mocks.

- Endpoints (env-only split):
  - Embeddings: `EMBED_URL` → default `http://127.0.0.1:9994/v1`
  - Chat/Answerer: `LM_STUDIO_HOST` → default `http://127.0.0.1:9994` (or `:9991` when chat is on that port)
- Models:
  - `ANSWERER_MODEL_PRIMARY=christian-bible-expert-v2.0-12b`
  - `ANSWERER_MODEL_ALT=Qwen2.5-14B-Instruct-GGUF` (toggle with `ANSWERER_USE_ALT=1`)
  - `EMBEDDING_MODEL=text-embedding-bge-m3`

Usage:

```bash
make models.verify   # lists /v1/models, pings chat (expects "OK"), embeddings dim=1024
make models.swap     # same, but uses ANSWERER_MODEL_ALT
make models.params   # prints recommended runtime knobs
```

Notes:

- Requires servers running (headless): `lms server start --port 9994 [--port 9991/9993]`
- Script loads `.env` via `ensure_env_loaded()` and uses `/v1` endpoints.

### Lint Automation Scripts (NEW)

#### `longline_noqa.py` — Smart E501 `# noqa` Tagger

**Purpose**: Automatically add `# noqa: E501` comments to truly non-wrappable long lines that are safe to ignore.

**Detection Categories**:
- URLs and curl commands
- SQL keywords within string literals (SELECT/INSERT/UPDATE/DELETE/WITH)
- Compiled regex patterns (`re.compile(...)`)
- Structured payload dumps (`json.dumps`, large dict/array literals)
- Logging calls (`logger.debug/info/warning/error`) with format strings

**Usage**:
```bash
python scripts/longline_noqa.py  # Tags non-wrappable lines with # noqa: E501
```

**Safety**: Uses higher threshold (110 chars) to let black/ruff-format handle most wrapping.

#### `quick_fixes.py` — Mechanical Lint Fixes

**Purpose**: Apply safe, mechanical fixes for common lint issues without breaking functionality.

**Fix Categories**:
- **E722**: Replace bare `except:` with `except Exception:` (preserves indentation)
- **E402**: Mark late imports with `# noqa: E402` (heuristic after first def/class)
- **B904**: Add `from e` to exception chains in `except ... as e:` blocks
- **SIM108**: Handled by `ruff --fix` (ternary operator opportunities)

**Usage**:
```bash
python scripts/quick_fixes.py  # Apply mechanical fixes and invoke ruff --fix
```

**Safety**: Conservative approach - E402 uses `# noqa` instead of moving imports.

### `generate_report.py` - Pipeline Reporting (Critical - Always Apply)

**Purpose**: Generate comprehensive markdown and JSON reports from pipeline execution data
**Requirements** (Report Generation Verification):

- **Automatic Execution**: Run after every pipeline execution
- **Template Validation**: Exact markdown/JSON templates with no missing sections
- **Real Data Only**: Actual pipeline data (enrichments, metrics, network stats) - never zeros/empty
- **File Creation**: Proper timestamps and naming conventions in `reports/` directory
- **No Trust Tests**: Manual verification required; tests insufficient for accuracy
- **Database Integrity**: All required tables exist; column names match schemas
  **Capabilities**:
- Aggregated metrics from recent pipeline runs
- Qwen health verification status (live inference proof)
- Network aggregation statistics and edge analysis
- Performance and throughput analysis
  **Usage**:

```bash
python scripts/generate_report.py --run-id <uuid>  # Specific run report
python scripts/generate_report.py                 # Recent aggregated report
```

**Verification Checklist**:

- [ ] Reports contain non-zero enrichment data (not "0 enrichments")
- [ ] JSON reports have complete metrics data structures
- [ ] Timestamps match actual pipeline execution times
- [ ] All template sections populated with real database data
- [ ] Qwen health verification shows verified=true with latencies

### `ci-no-mocks.sh` - CI Quality Gate

**Purpose**: Ensure production readiness by running tests without mocks
**Requirements**:

- All external services available (LM Studio, databases)
- No mock data or simulated responses
- Full end-to-end pipeline validation
  **Execution**:

```bash
./scripts/ci-no-mocks.sh  # Sets USE_QWEN_EMBEDDINGS=true, etc.
```

### `analyze_graph.py` - Graph Pattern Analysis (NEW)

**Purpose**: Analyze semantic concept network for communities and centrality patterns
**Requirements**:

- Builds NetworkX graph from database relations
- Computes Louvain communities and centrality measures
- Persists results to `concept_clusters` and `concept_centrality` tables
- Integrates with pipeline for automated pattern discovery
  **Capabilities**:
- Community detection using Louvain algorithm
- Centrality analysis (degree, betweenness, eigenvector)
- Database persistence for reporting and visualization
  **Usage**:

```bash
python scripts/analyze_graph.py  # Analyze current network and persist patterns
make analyze.graph              # Same via Makefile target
```

### `export_graph.py` - Graph Visualization Export (NEW)

**Purpose**: Export semantic concept network as viz-ready JSON for UI consumption
**Requirements**:

- Creates graph_latest.json with nodes, edges, clusters, and centrality
- Includes cluster assignments and centrality scores
- Proper error handling and logging
- Configurable export directory via EXPORT_DIR environment variable
  **Capabilities**:
- Full graph topology export
- Cluster and centrality metadata inclusion
- Timestamped file naming for versioning
- Integration with visualization tools and dashboards
  **Usage**:

```bash
python scripts/export_graph.py   # Export current network to JSON
make exports.graph              # Same via Makefile target
```

### `export_jsonld.py` - Semantic Web Graph Export (NEW)

**Purpose**: Export semantic concept network as JSON-LD and RDF/Turtle for knowledge graph interoperability
**Requirements**:

- **JSON-LD Export**: Creates `graph_latest.jsonld` with proper @context and linked data structure
- **RDF/Turtle Export**: Creates `graph_latest.ttl` with W3C standard serialization
- **URI Namespace**: Uses `https://gemantria.ai/concept/` namespace for global identifiers
- **Metadata Integration**: Optionally includes concept metadata from `concept_metadata` table
- **Semantic Compliance**: Follows schema.org and custom gematria ontologies
  **Capabilities**:
- JSON-LD with proper @context for semantic web tools
- RDF/Turtle serialization using rdflib for knowledge graph ingestion
- Global URIs for cross-system linking and GraphRAG compatibility
- Optional rich metadata (descriptions, sources, languages)
- Cluster and centrality data as RDF properties
  **Usage**:

```bash
python scripts/export_jsonld.py  # Export current network to JSON-LD and RDF/Turtle
make exports.jsonld             # Same via Makefile target
```

**Output Files**:

- `exports/graph_latest.jsonld` - JSON-LD format for web standards
- `exports/graph_latest.ttl` - RDF/Turtle format for knowledge graphs
  **Verification Checklist**:
- [ ] JSON-LD validates against schema.org context
- [ ] RDF/Turtle parses correctly with standard tools
- [ ] All nodes and edges exported with proper URIs
- [ ] Metadata included when `concept_metadata` table exists

### `export_stats.py` - Graph Statistics Export (NEW)

**Purpose**: Export quick graph statistics for dashboard consumption and monitoring
**Requirements**:

- **Aggregated Metrics**: Computes comprehensive network statistics
- **Health Indicators**: Provides network health and quality metrics
- **Dashboard Ready**: JSON output formatted for UI consumption
- **Real-time Data**: Direct database queries for current state
- **NetworkX Fallback**: Optional centrality calculation when DB tables empty
  **Capabilities**:
- Node/edge/cluster counts and distributions
- Centrality averages (DB or NetworkX-computed)
- Edge strength analysis (strong/weak/candidate connection counts)
- Network density and health indicators
- Largest cluster identification
- Configurable centrality computation via `STATS_CENTRALITY_FALLBACK=1`
  **Usage**:

```bash
python scripts/export_stats.py   # Export current network statistics
```

**Output Format**:

```json
{
  "nodes": 1250,
  "edges": 5432,
  "clusters": 8,
  "density": 0.0069,
  "centrality": {
    "avg_degree": 0.045,
    "max_degree": 0.234,
    "avg_betweenness": 0.0012
  },
  "edge_distribution": {
    "strong_edges": 1200,
    "weak_edges": 2800,
    "avg_cosine": 0.76
  }
}
```

### `export_temporal_patterns()` & `export_forecast()` - Phase 8 Temporal Analytics Export (NEW)

**Purpose**: Export time-series pattern analysis and forecasting data for temporal visualization (Phase 8)

**Requirements**:

- **Temporal Patterns**: Analyzes concept/cluster frequency over sequential verse/chapter indices
- **Rolling Windows**: Computes metrics (mean, sum) over configurable rolling windows to identify trends
- **Change Point Detection**: Identifies statistically significant shifts in temporal series
- **Forecasting Models**: Implements naive, SMA, and ARIMA forecasting with fallback handling
- **Schema Validation**: Validates against `temporal-patterns.schema.json` and `pattern-forecast.schema.json`

  **Capabilities**:

- Rolling window analysis with configurable parameters
- Basic change point detection for trend shifts
- Multiple forecasting algorithms with graceful degradation
- Prediction intervals and error metrics (RMSE, MAE)
- Book-wise temporal series aggregation
- Metadata annotation with analysis parameters

  **Usage**:

```bash
python scripts/export_stats.py   # Includes temporal and forecast exports
make exports.stats              # Same via Makefile target
```

**Output Files**:

- `exports/temporal_patterns.json` - Time series patterns with rolling window analysis
- `exports/pattern_forecast.json` - Forecasting results with model performance metrics

**Verification Checklist**:

- [ ] Temporal patterns validate against `temporal-patterns.schema.json`
- [ ] Forecast data validates against `pattern-forecast.schema.json`
- [ ] Rolling window parameters properly configured
- [ ] Forecasting models attempt ARIMA with SMA fallback
- [ ] Change points detected and annotated in metadata

### `create_agents_md.py` — AGENTS.md File Creator

**Purpose:** Automatically creates missing AGENTS.md files in directories that require them according to Rule 009 - Documentation Sync.
**Rule References:** 009 (Documentation Sync), 017 (Agent Docs Presence), 006 (AGENTS.md Governance)
**Capabilities:**

- **Directory Scanning**: Identifies directories requiring AGENTS.md files
- **Template Generation**: Creates appropriate templates based on directory type (source/tools/docs)
- **Dry Run Mode**: Preview what would be created without making changes
- **Coverage Verification**: Reports on missing AGENTS.md files

**Usage:**

```bash
# Check what AGENTS.md files are missing
python scripts/create_agents_md.py --dry-run

# Create missing AGENTS.md files
python scripts/create_agents_md.py
```

**Required Directories (per Rule 009):**
- Source Code: `src/*/` (all subdirectories)
- Tool Directories: `scripts/`, `migrations/`, `tests/`
- Documentation: `docs/*/` (all subdirectories)

**Templates Generated:**
- **Source directories**: Component-focused templates with API contracts and testing sections
- **Tool directories**: Specialized templates for scripts/migrations/tests with appropriate standards
- **Docs directories**: Documentation maintenance templates with ADR cross-references

### verify_pr016_pr017.py — Metrics Contract Verifier

**Purpose:** Ensures exported statistics reflect live DB and UI contracts.
**Rule References:** 021 (Stats Proof), 022 (Visualization Contract Sync), 006 (AGENTS.md Governance), 013 (Report Verification)
**Usage:**

```bash
python scripts/verify_pr016_pr017.py --dsn "$GEMATRIA_DSN" \
  --stats exports/graph_stats.json \
  --graph exports/graph_latest.json
```

**Outputs:** `VERIFIER_PASS` on success; fails closed otherwise.

### rules_guard.py — Critical System Enforcement

**Purpose:** System-level validation ensuring rules aren't just documentation. Fail-closed verification for code changes.
**Rule References:** 027 (Docs Sync Gate), 017 (Agent Docs Presence), 006 (AGENTS.md Governance)
**Capabilities:**

- **Documentation Sync**: Verifies AGENTS.md/ADR/README updates when code changes
- **Rules System Integrity**: Runs rules_audit.py to validate rule numbering and documentation sync
- **AGENTS.md Coverage**: Ensures required AGENTS.md files exist per Rule 017 (src/AGENTS.md, src/services/AGENTS.md, webui/graph/AGENTS.md)
- **Fail-Closed Design**: Hard stops commits that violate critical rules
- **Pre-commit Integration**: Runs automatically via .pre-commit-config.yaml
- **CI/CD Integration**: Runs in GitHub Actions for PR validation

**Critical Checks:**

1. **Documentation Sync**: Code changes require corresponding docs updates
2. **Rules Audit**: Rule numbering contiguous, docs automatically synced
3. **AGENTS.md Coverage**: Required AGENTS.md files present per Rule 017

**Usage:**

```bash
python scripts/rules_guard.py  # Run all critical checks
```

**Outputs:** Pass/fail with detailed error messages; fails closed on violations.

### generate_forest.py — Forest Overview Generator

**Purpose:** Auto-rebuilds high-level project map from ADRs, rules, and CI files.
**Rule References:** 025 (Phase Gate & Forest Sync), 006 (AGENTS.md Governance)
**Capabilities:**

- Scans `.cursor/rules/` for active rules
- Lists CI workflows from `.github/workflows/`
- Catalogs ADRs from `docs/ADRs/`
- Generates `docs/forest/overview.md`
- Updates `docs/VERIFICATION_MATRIX.md`
  **Usage:**

```bash
python scripts/generate_forest.py  # Rebuild forest overview
make generate.forest              # Same via Makefile target
```

**Outputs:**

- `docs/forest/overview.md` - Human-readable project map
- `docs/VERIFICATION_MATRIX.md` - Rule ↔ script ↔ CI ↔ evidence mappings
- Console summary of changes

## Script Categories

### Pipeline Operations

- **Execution**: Run pipeline with various configurations
- **Monitoring**: Health checks and status reporting
- **Maintenance**: Database migrations and cleanup
- **Analysis**: Graph pattern discovery and community detection (`analyze_graph.py`)
- **Export**: Visualization data export (`export_graph.py`)

### Development Tools

- **Testing**: Automated test execution and reporting
- **Linting**: Code quality and style validation
- **Documentation**: Generate API docs and reports
- **Quality Gates**: CI validation without mocks (`ci-no-mocks.sh`)

### Deployment Scripts

- **Setup**: Environment preparation and configuration
- **Migration**: Database schema updates and data migration
- **Validation**: Post-deployment verification

## Script Standards

### Environment Loading (CRITICAL - Always Apply)

**All scripts must load environment variables consistently to prevent database connectivity issues.**

```python
# REQUIRED: Add this to ALL scripts that use environment variables
from src.infra.env_loader import ensure_env_loaded

# Load environment variables from .env file (REQUIRED)
ensure_env_loaded()
```

**Environment Loading Requirements:**

- **All scripts** using `os.getenv()` or database connections **MUST** call `ensure_env_loaded()` at startup
- **No exceptions** - inconsistent loading causes persistent database failures
- **Import order**: Import `ensure_env_loaded` before any database operations
- **Placement**: Call immediately after imports, before any environment variable access

**Why This Matters:**

- Prevents "GEMATRIA_DSN not set" errors
- Ensures consistent behavior across different execution contexts
- Fixes the root cause of persistent database connectivity issues
- Makes scripts work reliably from command line, CI, and automated systems

### Command-Line Interface

- **Help**: `--help` for all scripts
- **Arguments**: Clear parameter naming and validation
- **Output**: Consistent formatting and error codes
- **Logging**: Structured logging with appropriate verbosity

### Error Handling

- **Graceful Failures**: Clear error messages and exit codes
- **Recovery**: Where possible, suggest remediation steps
- **Logging**: Detailed error information for debugging

### Configuration

- **Environment**: Use environment variables for configuration
- **Defaults**: Sensible defaults with override capability
- **Validation**: Input validation with helpful error messages
- **Loading**: **MANDATORY** `ensure_env_loaded()` call for all database scripts

## Development Guidelines

### Adding New Scripts

1. **Purpose**: Clear, single responsibility
2. **Interface**: Command-line arguments and help
3. **Error Handling**: Robust error handling and logging
4. **Testing**: Unit tests for script logic
5. **Documentation**: Inline help and README updates

### Script Maintenance

1. **Updates**: Keep scripts current with API changes
2. **Testing**: Automated testing of script execution
3. **Documentation**: Update usage examples and parameters
4. **Deprecation**: Clear migration path for replaced scripts

## Execution Environment

### Dependencies

- **Python**: Required version and virtual environment
- **System Tools**: bash, make, git for CI/CD integration
- **External Services**: Database, LM Studio for full functionality

### Security Considerations

- **Input Validation**: Sanitize all user inputs
- **Credentials**: Secure handling of API keys and passwords
- **Permissions**: Appropriate file and database permissions
- **Audit Trail**: Logging of script execution and changes

## Testing Strategy

### Script Testing

- **Unit Tests**: Test script logic in isolation
- **Integration Tests**: Test with real dependencies
- **End-to-End**: Full workflow validation

### CI/CD Integration

- **Automated Execution**: Scripts run in CI pipelines
- **Artifact Generation**: Reports and logs as CI artifacts
- **Quality Gates**: Script success as merge requirements

## Maintenance & Operations

### Monitoring

- **Execution Logs**: Track script runs and performance
- **Failure Alerts**: Notification for script failures
- **Performance Metrics**: Execution time and resource usage

### Troubleshooting

- **Debug Mode**: Verbose logging for issue diagnosis
- **Dry Run**: Preview changes without execution
- **Rollback**: Safe reversal of script actions

### Documentation

- **README**: Script catalog with usage examples
- **Inline Help**: `--help` for all scripts
- **Runbooks**: Operational procedures using scripts
