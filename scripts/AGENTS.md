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

### `guards/guard_ai_tracking_contract.py` — AI Tracking DB Contract Guard (NEW - Rule 064)

**Purpose:** Enforce 3-role DB contract: AI tracking tables must live in gematria DB (public schema)

**Requirements:**
- **DSN Congruence**: `AI_AUTOMATION_DSN` must equal `GEMATRIA_DSN` (same host/port/db)
- **Table Presence**: Validates `public.ai_interactions` and `public.governance_artifacts` exist
- **Fail-Closed**: STRICT mode fails if contract violated; HINT mode warns only

**Usage:**
```bash
make guard.ai.tracking              # HINT mode (tolerant, for PRs)
make guard.ai.tracking.strict       # STRICT mode (fail-closed, for tags)
STRICT_AI_TRACKING=1 python3 scripts/guards/guard_ai_tracking_contract.py
```

**Output:**
```json
{
  "ok": true,
  "note": "AI tracking bound to gematria DB (public schema)",
  "same_db": true,
  "tables": {
    "public.ai_interactions": true,
    "public.governance_artifacts": true
  },
  "counts": {
    "ai_interactions": 1,
    "governance_artifacts": 79
  }
}
```

**Related:**
- **Rule 064**: AI-tracking in gematria (DSN congruence)
- **Migrations**: 015 (governance_artifacts), 016 (ai_interactions)
- **CI**: HINT on PRs, STRICT on tags (gated by `vars.STRICT_DB_MIRROR_CI`)

### `guards/guard_db_health.py` — DB Health Guard (Phase-3A)

**Purpose:** Check database health posture (driver availability, connection status, table readiness)

**Modes:**
- `ready`: All systems operational (driver available, connection works, tables accessible)
- `db_off`: Database unavailable (driver missing or connection failed)
- `partial`: Database connected but tables missing

**Usage:**
```bash
make guard.db.health        # Detailed JSON output
make db.health.smoke        # Human-readable summary
```

**Output:**
```json
{
  "ok": true,
  "mode": "ready",
  "checks": {
    "driver_available": true,
    "connection_ok": true,
    "graph_stats_ready": true
  },
  "details": {
    "errors": []
  }
}
```

**Related:**
- **Phase-3A**: DB activation and health checks
- **Runbook**: `docs/runbooks/DB_HEALTH.md`
- **Tests**: `agentpm/tests/db/test_phase3a_db_health_guard.py`

### `guards/guard_lm_health.py` — LM Health Guard (Phase-3B)

**Purpose:** Check LM Studio endpoint availability and response validity

**Modes:**
- `lm_ready`: LM Studio operational (endpoint reachable and responding correctly)
- `lm_off`: LM Studio unavailable (endpoint not reachable or responding incorrectly)

**Configuration:**
- **Endpoint**: `LM_STUDIO_HOST` (default: `http://127.0.0.1:1234`) or `LM_EMBED_HOST`/`LM_EMBED_PORT`
- **Timeout**: `LM_HEALTH_TIMEOUT` (default: 1.0 seconds)

**Usage:**
```bash
make guard.lm.health        # Detailed JSON output
make lm.health.smoke        # Human-readable summary
```

**Output:**
```json
{
  "ok": true,
  "mode": "lm_ready",
  "details": {
    "endpoint": "http://127.0.0.1:1234",
    "errors": []
  }
}
```

**Related:**
- **Phase-3B**: LM health guard and smoke command
- **Runbook**: `docs/runbooks/LM_HEALTH.md`
- **Tests**: `agentpm/tests/lm/test_phase3b_lm_health_guard.py`

### `hint.sh` — Uniform Runtime Hints Emitter (NEW)

**Purpose:** Emit standardized `HINT:` lines for clear CI log visibility and Cursor runtime tracking.

**Requirements:**
- **Uniform Format**: All hints start with `HINT:` for easy grepping
- **Runtime Clarity**: Key operations emit hints so CI logs are self-documenting
- **Fallback Safe**: Works even if hint.sh script is missing (echo fallback)
- **Template Integration**: Required in PR templates and NEXT_STEPS runbooks

**Usage:**
```bash
# Direct usage
./scripts/hint.sh "verify: database bootstrap OK"

# Via emit() function (preferred in scripts)
emit() { if [ -x scripts/hint.sh ]; then scripts/hint.sh "$*"; else echo "HINT: $*"; fi; }
emit "verify: target_db=$target_db"
```

**Output Format:**
```
HINT: verify: database bootstrap OK
HINT: eval: running advanced calibration
HINT: eval: writing quality trend badge
```

**Integration Points:**
- `scripts/ci/ensure_db_then_migrate.sh` - Database bootstrap hints
- `scripts/eval/calibrate_advanced.py` - Calibration operation hints
- `scripts/eval/quality_trend.py` - Quality trend generation hints
- PR templates - Require listing expected HINT lines
- NEXT_STEPS templates - Require HINT planning
- CI logs - Clear runtime visibility for Cursor and reviewers

### `calibrate_advanced.py` — Advanced Edge Strength Calibration (Phase-9)

**Purpose:** Optimize edge strength thresholds using between-class variance analysis for semantic network quality.

**Requirements:**
- **Optimization Algorithm**: Uses Otsu-like 2-threshold method on blended cosine + rerank scores
- **Grid Search**: Searches weight parameter W ∈ [0.0, 1.0] to find optimal blend ratios
- **Threshold Calculation**: Determines weak/strong edge boundaries for network classification
- **Calibration Output**: Saves optimal parameters to `calibration_adv.json`

**Capabilities:**
- Automatic threshold optimization for edge strength classification
- Statistical analysis using between-class variance maximization
- Configurable search space and precision parameters
- Integration with evaluation pipeline for automated recalibration

**Usage:**
```bash
python scripts/eval/calibrate_advanced.py  # Optimize thresholds and save to calibration_adv.json
make eval.graph.calibrate.adv            # Same via Makefile target
```

**Output:** `share/eval/calibration_adv.json` with suggested EDGE_BLEND_WEIGHT, EDGE_WEAK_THRESH, EDGE_STRONG_THRESH

**Emitted Hints:**
- `HINT: eval: running advanced calibration`

### `quality_trend.py` — Quality History Tracking & Trend Visualization (Phase-9)

**Purpose:** Monitor and visualize quality metrics over time with historical trend analysis.

**Requirements:**
- **Quality Parsing**: Extracts pass/fail status and edge distribution from quality reports
- **History Maintenance**: Appends metrics to `quality_history.jsonl` with timestamps
- **Trend Visualization**: Generates sparkline SVG badges showing quality trends
- **Rolling Window**: Maintains last 30 quality measurements for trend analysis

**Capabilities:**
- Real-time quality monitoring with historical persistence
- Visual trend indicators via SVG sparkline badges
- Statistical analysis of edge distribution changes over time
- Integration with CI/CD for automated quality tracking

**Usage:**
```bash
python scripts/eval/quality_trend.py     # Update history and generate trend badge
make eval.quality.trend                 # Same via Makefile target
```

**Outputs:**
- `share/eval/quality_history.jsonl` - Historical quality metrics with timestamps
- `share/eval/badges/quality_trend.svg` - Visual trend indicator badge

**Emitted Hints:**
- `HINT: eval: writing quality trend badge`

### `edge_audit.py` — Edge Anomaly Detection (Phase-9)

**Purpose:** Analyze semantic network edges for anomalous strength values using statistical outlier detection.

**Requirements:**
- **Dual Detection Methods**: Combines z-score (>3σ) and IQR (1.5×IQR) outlier detection for robust anomaly identification
- **Comprehensive Analysis**: Provides detailed statistics on edge strength distribution and anomaly counts
- **Audit Output**: Saves structured JSON report with anomaly details for review and alerting

**Capabilities:**
- Statistical outlier detection using both parametric (z-score) and non-parametric (IQR) methods
- Detailed anomaly reporting with deviation metrics and thresholds
- Integration with evaluation pipeline for automated quality monitoring
- Configurable detection parameters for different sensitivity levels

**Usage:**
```bash
python scripts/eval/edge_audit.py  # Analyze current graph for edge anomalies
make eval.edge.audit             # Same via Makefile target
```

**Output:** `share/eval/edge_audit.json` with complete anomaly analysis including:
- Edge strength distribution statistics
- Z-score and IQR anomaly detection results
- Summary counts and anomaly rates
- Detailed outlier lists with deviation metrics

**Emitted Hints:**
- `HINT: eval: auditing edges for anomalies`

### `anomaly_badge.py` — Edge Anomaly Visualization Badge (Phase-9)

**Purpose:** Generate visual SVG badge showing the count of anomalous edges detected in the semantic network.

**Requirements:**
- **Visual Status Indicator**: Color-coded badge (green=0, yellow=1-5, red=6+) for quick anomaly assessment
- **Audit Integration**: Reads edge_audit.json results to determine anomaly count
- **Graceful Fallback**: Handles missing audit files with safe defaults and error indicators

**Capabilities:**
- Automated badge generation with appropriate color coding
- Real-time reflection of network quality status
- CI/CD integration for automated quality monitoring
- Error handling with distinct error indicators (999 = error state)

**Usage:**
```bash
python scripts/eval/anomaly_badge.py  # Generate anomaly count badge
make eval.anomaly.badge              # Same via Makefile target
```

**Output:** `share/eval/badges/anomaly.svg` with:
- Color-coded status (green/yellow/red based on anomaly count)
- Numerical anomaly count display
- Accessible SVG format for web dashboards

**Emitted Hints:**
- `HINT: eval: writing anomaly badge`

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

### `update_share.py` & `sync_share.py` — Share Directory Synchronization

**Purpose**: Maintain a flat `share/` directory with canonical project files for external access and tooling.

**Requirements**:
- **Manifest-Driven**: Reads `docs/SSOT/SHARE_MANIFEST.json` for file list and destinations
- **Change Detection**: Only copies files that have actually changed (SHA-256 content comparison)
- **Preview Generation**: Creates small JSON head previews for large export files
- **Flat Layout**: All files copied to root `share/` directory (no subdirectories)

**Capabilities**:
- **Efficient Sync**: Compares file hashes before copying to avoid unnecessary I/O
- **Large File Handling**: Generates preview headers for JSON exports over 4KB
- **Progress Reporting**: Shows count of files updated vs total files processed
- **Error Handling**: Validates source files exist and manifest is well-formed

**Usage**:
```bash
# Via Makefile (recommended)
make share.sync

# Direct script execution
python scripts/update_share.py
python scripts/sync_share.py  # Wrapper script
```

**Output Examples**:
```bash
# When files changed
[update_share] OK — share/ refreshed (3/20 files updated)

# When no changes
[update_share] OK — share/ up to date (no changes)
```

**Manifest Structure**:
```json
{
  "items": [
    {
      "src": "AGENTS.md",
      "dst": "share/AGENTS.md"
    },
    {
      "src": "exports/graph_stats.json",
      "dst": "share/graph_stats.head.json",
      "generate": "head_json",
      "max_bytes": 4096
    }
  ]
}
```

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

### `verify_data_completeness.py` - Data Completeness Verification (Rule 037)

**Purpose**: Verify database schema completeness and data integrity for Rule 037 compliance
**Requirements**: Rule 037 (Data Persistence Completeness) - ensure complete data persistence

**Capabilities**:
- Table presence validation (concepts, concept_network, concept_relations)
- Join integrity checks between related tables
- Connection robustness testing
- No data writes - read-only verification

**Usage**:
```bash
python scripts/verify_data_completeness.py  # Check all tables and joins
```

**Verification Checklist**:
- [ ] All required tables exist and are populated
- [ ] Foreign key relationships are intact
- [ ] No orphaned records in join tables
- [ ] Database connection stable under load

### `book_readiness.py` - Book Pipeline Readiness Gate

**Purpose**: Validate system readiness for full book extraction (mini experiment → thresholds → schema validation)
**Requirements**: Rule 037 gate enforcement - block book runs until mini experiment passes

**Capabilities**:
- Mini experiment execution with real inference
- Threshold validation against configurable metrics
- SSOT schema validation (robust path discovery)
- Readiness report generation
- Service availability checking

**Usage**:
```bash
# Run mini experiment
python scripts/book_readiness.py run-mini --config config/mini_experiments.yaml

# Compute readiness metrics
python scripts/book_readiness.py compute --inputs graph_stats.json temporal_patterns.json pattern_forecast.json

# Validate gates (HARD-REQUIRED)
python scripts/book_readiness.py gate

# Assert readiness before book run
python scripts/book_readiness.py assert-pass
```

**Schema Path Robustness**:
- Searches `docs/SSOT/schemas/` first (preferred location)
- Falls back to `docs/SSOT/` for compatibility
- Accepts multiple naming patterns: `graph-stats.schema.json`, `graph_export.schema.json`

### `run_book.py` - Book Pipeline Orchestration

**Purpose**: Orchestrate deterministic book extraction with confidence-building phases
**Requirements**: Rule 049 governance - ops-mode controlled execution

**Capabilities**:
- Plan phase: Configuration validation and planning
- Dry-run phase: Service validation without inference
- Stop-loss phase: Partial execution with N-chapter limit
- Resume phase: Continue from interruption point
- YAML/JSON config support with graceful fallbacks

**Usage**:
```bash
# Plan extraction
python scripts/run_book.py plan --cfg config/book_config.yaml

# Dry run (validate services, no inference)
python scripts/run_book.py dry --cfg config/book_config.yaml

# Stop after N chapters
python scripts/run_book.py stop --cfg config/book_config.yaml --n 5

# Resume from interruption
python scripts/run_book.py resume
```

**Safety Features**:
- Deterministic seeding for reproducible runs
- Service availability validation before execution
- Partial execution tracking and resume capability
- Environment isolation per run

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
- **Automatic Centrality**: Computes and persists centrality metrics when missing from database
  **Capabilities**:
- Node/edge/cluster counts and distributions
- Centrality averages (DB-persisted with automatic computation)
- Edge strength analysis (strong/weak/candidate connection counts)
- Network density and health indicators
- Largest cluster identification
- Automatic centrality persistence using NetworkX algorithms
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

### `auto_update_agents_md.py` — Automatic AGENTS.md Updater (Rule-058)

**Purpose:** **AUTOMATICALLY** updates AGENTS.md files based on code changes detected from git. This script runs as part of `make housekeeping` to ensure documentation stays in sync without manual intervention.
**Rule References:** 006 (AGENTS.md Governance), 027 (Docs Sync Gate), 058 (Auto-Housekeeping)
**Capabilities:**

- **Automatic Detection**: Identifies code changes in directories requiring AGENTS.md files
- **Change Analysis**: Detects new functions, classes, and components in changed files
- **Auto-Update**: Updates AGENTS.md files with timestamp refresh or creates missing files
- **Git Integration**: Uses git diff to detect changed files
- **Non-Fatal**: Runs as part of housekeeping with graceful error handling

**Usage:**

```bash
# Auto-update based on git changes (runs automatically in make housekeeping)
python scripts/auto_update_agents_md.py

# Dry-run to see what would be updated
python scripts/auto_update_agents_md.py --dry-run
```

**Integration:**
- **Housekeeping**: Automatically runs as part of `make housekeeping` (Rule-058)
- **Makefile**: Integrated into housekeeping target
- **Non-Fatal**: Errors are logged but don't fail housekeeping (allows graceful degradation)

**Note:** This script is designed to reduce manual documentation maintenance. If you find yourself manually editing AGENTS.md files, that indicates the auto-update script needs enhancement, not that manual updates are required.

### `auto_update_changelog.py` — Automatic CHANGELOG.md Updater (Rule-058)

**Purpose:** **AUTOMATICALLY** updates CHANGELOG.md based on recent git commits. Extracts feature/fix/docs entries from conventional commit messages and adds them to the [Unreleased] section.
**Rule References:** 027 (Docs Sync Gate), 058 (Auto-Housekeeping)
**Capabilities:**

- **Commit Analysis**: Extracts conventional commit format (feat/fix/docs)
- **Feature Detection**: Detects Phase-3B Feature #X patterns and PR numbers
- **Auto-Update**: Adds entries to CHANGELOG.md [Unreleased] section
- **Duplicate Prevention**: Checks for existing entries before adding
- **Non-Fatal**: Runs as part of housekeeping with graceful error handling

**Usage:**

```bash
# Auto-update based on recent commits (runs automatically in make housekeeping)
python scripts/auto_update_changelog.py

# Dry-run to see what would be added
python scripts/auto_update_changelog.py --dry-run

# Check specific number of commits
python scripts/auto_update_changelog.py --limit 20
```

**Integration:**
- **Housekeeping**: Automatically runs as part of `make housekeeping` (Rule-058)
- **Makefile**: Integrated into housekeeping target
- **Non-Fatal**: Errors are logged but don't fail housekeeping (allows graceful degradation)

**Note:** This script is designed to reduce manual CHANGELOG maintenance. If you find yourself manually editing CHANGELOG.md, that indicates the auto-update script needs enhancement, not that manual updates are required.

### `validate_agents_md.py` — AGENTS.md Validation (Rule-017 + Rule-058)

**Purpose:** Validates that all required AGENTS.md files are present and have valid structure. Uses dynamic directory discovery to check all directories that require AGENTS.md files per Rule 017.
**Rule References:** 006 (AGENTS.md Governance), 017 (Agent Docs Presence), 027 (Docs Sync Gate), 058 (Auto-Housekeeping)
**Capabilities:**

- **Dynamic Discovery**: Automatically discovers directories requiring AGENTS.md files (matches `create_agents_md.py` approach)
- **Presence Validation**: Checks that all required AGENTS.md files exist
- **Structure Validation**: Verifies AGENTS.md files have required sections (`# AGENTS.md` header, `## Directory Purpose`)
- **Exclusion Handling**: Properly excludes generated/static directories (public, dist, build, .egg-info, cache dirs)
- **Comprehensive Coverage**: Validates AGENTS.md files in `src/`, `agentpm/`, `docs/`, `webui/`, and tool directories

**Usage:**

```bash
# Validate all required AGENTS.md files
python scripts/validate_agents_md.py

# Via Makefile (runs as part of housekeeping)
make housekeeping
```

**Integration:**
- **Housekeeping**: Runs as part of `make housekeeping` (Rule-058)
- **Validation**: Ensures Rule 017 compliance (all required AGENTS.md files present)
- **Dynamic**: Automatically adapts to new directories without hardcoded lists

**Note:** This script was updated to use dynamic directory discovery instead of a hardcoded list. It now correctly validates all directories that require AGENTS.md files, including all `agentpm/` subdirectories and `docs/` subdirectories.

### `check_agents_md_sync.py` — AGENTS.md Sync Checker

**Purpose:** Detects when code changes in a directory should trigger AGENTS.md updates. Compares file modification times and git history to identify potentially stale AGENTS.md files.
**Rule References:** 006 (AGENTS.md Governance), 027 (Docs Sync Gate), 017 (Agent Docs Presence)
**Capabilities:**

- **Change Detection**: Identifies code changes in directories requiring AGENTS.md files
- **Sync Verification**: Compares AGENTS.md modification times with code file modification times
- **Git Integration**: Uses git history for accurate modification time detection
- **Staged/Unstaged**: Can check staged changes or all changes since HEAD

**Usage:**

```bash
# Check all changes since HEAD
python scripts/check_agents_md_sync.py

# Check only staged changes
python scripts/check_agents_md_sync.py --staged

# Verbose output with detailed information
python scripts/check_agents_md_sync.py --verbose

# Via Makefile
make agents.md.sync
```

**When AGENTS.md Needs Updates:**
- New functions/classes/components are added
- API contracts or interfaces change
- Key behavior or patterns change
- Dependencies or integration points change

**Integration:**
- **Pre-commit**: Integrated into `rules_guard.py` as non-fatal hint
- **Makefile**: `make agents.md.sync` provides convenient access
- **CI**: Can be run in CI to detect documentation drift

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

### `eval/integrity_fast.py` — Fast Integrity Caching Wrapper

**Purpose:** Caches integrity verification results by manifest fingerprint to speed up repeated runs of `ops.verify`.
**Rule References:** 017a (Surgical Soft Integrity Caching)
**Capabilities:**

- **Manifest Fingerprinting**: Uses SHA-256 of release_manifest.json to detect changes
- **Cache Storage**: Stores results in `.cache/integrity/` directory
- **Timeout Protection**: Hard check limited to 180 seconds with graceful timeout handling
- **Status Caching**: Caches pass/fail/timeout status with timestamps
- **Skip on No Manifest**: Gracefully skips when manifest doesn't exist

**Usage:**

```bash
# Called automatically by eval.verify.integrity.soft
python scripts/eval/integrity_fast.py --manifest share/eval/release_manifest.json

# Clear cache if needed
make eval.cache.clear
```

**Cache Behavior:**

- **First Run**: Executes hard check, caches result (may take ~100+ seconds)
- **Subsequent Runs**: Returns cached result instantly when manifest unchanged
- **Manifest Changes**: Invalidates cache and re-runs hard check
- **No Manifest**: Skips with non-blocking status

**Performance Impact:**
- **First run**: ~100+ seconds (hard check execution time)
- **Cached runs**: ~0.02 seconds (JSON file read)
- **Cache invalidation**: Automatic on manifest changes

### `graph/graph_overview.py` — Graph Overview Command (Phase-3B)

**Purpose:** Query graph statistics from database and provide summary of graph metrics

**Modes:**
- `db_on`: Database connected and graph stats available
- `db_off`: Database unavailable (driver missing or connection failed)
- `partial`: Database connected but graph_stats table missing

**Usage:**
```bash
make graph.overview         # JSON to stdout, human summary to stderr
```

**Output:**
```json
{
  "ok": true,
  "mode": "db_on",
  "stats": {
    "nodes": 100,
    "edges": 200,
    "avg_degree": 4.0,
    "snapshot_count": 1,
    "last_import_at": "2024-01-15T10:30:00+00:00"
  },
  "reason": null
}
```

**Related:**
- **Phase-3B**: DB-backed graph overview command
- **Runbook**: `docs/runbooks/GRAPH_OVERVIEW.md`
- **Tests**: `agentpm/tests/db/test_phase3b_graph_overview.py`
- **DB Integration**: Uses `graph_stats_snapshots` table via `agentpm.db.models_graph_stats`

### `control/control_status.py` — Control Plane Status Check (Phase-3B Feature #6)

**Purpose:** Check control-plane database posture and table row counts for key control-plane tables

**Modes:**
- `ready`: Database connected and all tables accessible
- `db_off`: Database unavailable (driver missing or connection failed)
- `partial`: Database connected but some tables missing

**Monitored Tables:**
- `public.ai_interactions` - AI interaction tracking (Rule-061)
- `public.governance_artifacts` - Governance artifacts tracking (Rule-026, Rule-058)
- `control.agent_run` - Agent run audit log (Migration 040)
- `control.tool_catalog` - Tool catalog (Migration 040)
- `gematria.graph_stats_snapshots` - Graph statistics snapshots (Phase-3A)

**Usage:**
```bash
make control.status.smoke    # JSON to stdout, human summary to stderr
python -m pmagent.cli control status
```

**Output:**
```json
{
  "ok": true,
  "mode": "ready",
  "reason": null,
  "tables": {
    "public.ai_interactions": {
      "present": true,
      "row_count": 42,
      "latest_created_at": "2024-01-15T10:30:00+00:00"
    },
    ...
  }
}
```

**Human Summary:**
```
CONTROL_STATUS: mode=ready tables=ai_interactions(42),governance_artifacts(15),agent_run(8)
```

**Related:**
- **Phase-3B Feature #6**: Control-plane status check
- **Runbook**: `docs/runbooks/CONTROL_STATUS.md`
- **Tests**: `agentpm/tests/cli/test_phase3b_pmagent_control_status_cli.py`
- **CLI**: `pmagent control status` command

### `control/control_tables.py` — Control Plane Tables Listing (Phase-3B Feature #7)

**Purpose:** List all schema-qualified tables across Postgres schemas with row counts

**Modes:**
- `db_on`: Database connected and queries successful
- `db_off`: Database unavailable (driver missing or connection failed)

**Usage:**
```bash
make control.tables.smoke    # JSON to stdout, human summary to stderr
python -m pmagent.cli control tables
```

**Output:**
```json
{
  "ok": true,
  "mode": "db_on",
  "error": null,
  "tables": {
    "public.ai_interactions": 42,
    "public.governance_artifacts": 15,
    "control.agent_run": 8,
    "control.tool_catalog": 5,
    "gematria.graph_stats_snapshots": 3
  }
}
```

**Human Summary:**
```
CONTROL_TABLES: mode=db_on tables=8 schemas=control(3),gematria(3),public(2)
```

**Related:**
- **Phase-3B Feature #7**: Control-plane tables listing
- **Runbook**: `docs/runbooks/CONTROL_TABLES.md`
- **Tests**: `agentpm/tests/cli/test_phase3b_pmagent_control_tables_cli.py`
- **CLI**: `pmagent control tables` command

### `control/control_schema.py` — Control Plane Schema Introspection (Phase-3B Feature #8)

**Purpose:** Introspect control-plane table schemas (DDL) including columns, primary keys, and indexes

**Modes:**
- `db_on`: Database connected and schema queries successful
- `db_off`: Database unavailable (driver missing or connection failed)

**Monitored Tables:**
- `control.agent_run` - Agent run audit log
- `control.tool_catalog` - Tool catalog
- `control.capability_rule` - Capability rules
- `control.doc_fragment` - Document fragments
- `control.capability_session` - Capability sessions
- `public.ai_interactions` - AI interaction tracking
- `public.governance_artifacts` - Governance artifacts tracking

**Usage:**
```bash
make control.schema.smoke    # JSON to stdout, human summary to stderr
python -m pmagent.cli control schema
```

**Output:**
```json
{
  "ok": true,
  "mode": "db_on",
  "reason": null,
  "tables": {
    "control.agent_run": {
      "columns": [
        {
          "name": "id",
          "data_type": "uuid",
          "is_nullable": false,
          "default": "gen_random_uuid()"
        },
        ...
      ],
      "primary_key": ["id"],
      "indexes": [
        {
          "name": "idx_agent_run_project",
          "columns": ["project_id"],
          "unique": false
        },
        ...
      ]
    },
    ...
  }
}
```

**Human Summary:**
```
CONTROL_SCHEMA: mode=db_on tables=2 columns=19
```

**Related:**
- **Phase-3B Feature #8**: Control-plane schema introspection
- **Runbook**: `docs/runbooks/CONTROL_SCHEMA.md`
- **Tests**: `agentpm/tests/cli/test_phase3b_pmagent_control_schema_cli.py`
- **CLI**: `pmagent control schema` command
- **Migrations**: 015 (governance_artifacts), 016 (ai_interactions), 040 (control schema)

### `system/system_health.py` — System Health Aggregate (Phase-3B)

**Purpose:** Aggregate DB health, LM health, and graph overview into a single JSON + human-readable summary

**Components:**
- **DB Health**: Database driver, connection, and table readiness
- **LM Health**: LM Studio endpoint availability and response validity
- **Graph Overview**: Graph statistics from database

**Usage:**
```bash
make system.health.smoke    # Aggregated health check with summary
```

**Output:**
```json
{
  "ok": false,
  "components": {
    "db": { "ok": false, "mode": "db_off", ... },
    "lm": { "ok": false, "mode": "lm_off", ... },
    "graph": { "ok": false, "mode": "db_off", ... }
  }
}
```

**Human Summary:**
```
SYSTEM_HEALTH:
  DB_HEALTH:   mode=db_off (driver missing)
  LM_HEALTH:   mode=lm_off (endpoint not reachable)
  GRAPH_OVERVIEW: mode=db_off (Postgres database driver not available)
```

**Related:**
- **Phase-3B**: System health aggregate (DB + LM + Graph)
- **Runbook**: `docs/runbooks/SYSTEM_HEALTH.md`
- **Tests**: `agentpm/tests/system/test_phase3b_system_health.py`
- **Integration**: Calls `guard_db_health`, `guard_lm_health`, and `graph_overview` via subprocess

### `lm/print_lm_health_summary.py` — LM Health Summary Printer (Phase-3B)

**Purpose:** Print human-readable summary line from LM health JSON output

**Usage:**
```bash
python -m scripts.guards.guard_lm_health | python3 scripts/lm/print_lm_health_summary.py
```

**Output:**
```
LM_HEALTH: mode=lm_ready (ok)
LM_HEALTH: mode=lm_off (endpoint not reachable)
```

**Related:**
- **Phase-3B**: LM health guard and smoke command
- **Pattern**: Mirrors `scripts/db/print_db_health_summary.py` for consistency

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

**Preferred Approach (New Code):**
```python
# Use centralized loader for both .env loading and DSN access
from scripts.config.env import get_rw_dsn, get_ro_dsn, env

# scripts.config.env auto-loads .env via _ensure_loaded() when env() is called
# Trigger env loading by calling env() once (non-fatal)
try:
    env("PATH")  # Non-fatal call to trigger _ensure_loaded()
except Exception:
    pass

# Use centralized DSN functions
dsn = get_rw_dsn()
```

**Legacy Approach (Still Valid):**
```python
# For scripts that only need .env loading (no DSN access)
from src.infra.env_loader import ensure_env_loaded

# Load environment variables from .env file
ensure_env_loaded()
```

**Environment Loading Requirements:**

- **All scripts** using database connections **MUST** use centralized DSN loaders (`scripts.config.env` preferred)
- **DSN access**: Never use `os.getenv("GEMATRIA_DSN")` directly - use `get_rw_dsn()`, `get_ro_dsn()`, or `get_bible_db_dsn()`
- **Legacy scripts**: May use `src.infra.env_loader.ensure_env_loaded()` for .env loading only
- **Import order**: Import DSN loaders before any database operations
- **Placement**: Call env loading immediately after imports, before any environment variable access

**Why This Matters:**

- Prevents "GEMATRIA_DSN not set" errors
- Ensures consistent behavior across different execution contexts
- Centralized DSN management prevents drift and enforces policy
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
