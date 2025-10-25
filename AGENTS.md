# AGENTS.md — Gemantria Agent Framework

## How Cursor uses rules + AGENTS.md (Protocol)
**Bottom line:** Cursor should only always-apply the three navigator rules; everything else is task-scoped.

- **Always-apply (navigators only):** `000-ssot-index.mdc`, `010-task-brief.mdc`, `030-share-sync.mdc`.
- **Task-scoped rules:** All other rules are **not** always applied; Cursor selects them based on globs and the task brief.
- **What to read first:** `RULES_INDEX.md` for the active list and numbers; this AGENTS.md for authority on behavior; SSOT schemas when touching analytics exports.
- **Linking discipline:** Each rule's **Related Documentation** must reference AGENTS.md sections, SSOT schemas, and any enforcing scripts/Make targets it depends on.
- **Evidence:** After each change, run `make rules.audit docs.audit repo.audit` and then `make share.sync`. Paste the printed proofs into the PR.

## Mission

Build a deterministic, resumable LangGraph pipeline that produces verified gematria data and viz-ready artifacts.

## Priorities

1. **Correctness**: Code gematria > bible_db > LLM (LLM = metadata only)
2. **Determinism**: content_hash (SHA-256) identity; uuidv7 surrogate; fixed seeds; position_index
3. **Safety**: bible_db is READ-ONLY; parameterized SQL only; fail-closed if <50 nouns (ALLOW_PARTIAL=1 explicit)

## Critical Rules (Always Apply)

- **Code gematria > bible_db > LLM**: LLM provides metadata only, never affects core gematria calculations
- **Bible DB Read-Only**: Any write attempt must error; enforced at connection level
- **No Mock Datasets**: Tests are code-verified or DB-derived only; no **mocks** folders
- **Hebrew Normalization**: NFKD→strip combining→strip maqaf (U+05BE)/sof pasuq (U+05C3)/punct→NFC
- **Gematria Rules**: Finals=regular (Mispar Hechrachi); compute on surface form; keep calc strings
- **Identity**: content_hash (SHA-256) as deterministic ID; uuidv7 as sortable surrogate
- **Batch Semantics**: 50 nouns default; <50 nouns → abort + review.ndjson (ALLOW_PARTIAL=1 explicit + manifest)
- **Network**: pgvector embeddings (1024-dim, L2 normalized); cosine similarity; strong edges ≥0.90, weak edges ≥0.75; Qwen3 inference
- **Qwen Live Gate**: ENFORCE_QWEN_LIVE=1 → assert_qwen_live() before network aggregation; fail-closed unless verified
- **Schema Changes**: Require ADR + tests (+ migrations if DB) in same PR

## Environment Setup

### Automated Bootstrap (Recommended)

```bash
# One-command setup for new developers
./scripts/bootstrap_dev.sh

# Verify everything works
make doctor
```

### Manual Setup (Alternative)

```bash
# Create virtual environment
python3 -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install --upgrade "psycopg[binary]" pgvector requests python-dotenv

# Copy environment template
cp env_example.txt .env

# Edit .env with your local configuration
# Then verify setup:
make doctor
```

### Required Environment Variables

#### Database Configuration

```bash
# Gematria Database (read-write) - Primary database for concepts and networks
GEMATRIA_DSN=postgresql://user:pass@localhost:5432/gematria

# Bible Database (read-only) - Reference database with biblical text
BIBLE_DB_DSN=postgresql://user:pass@localhost:5432/bible_db
```

#### LM Studio Configuration

```bash
# LM Studio servers (split)
# - Answerer/Critic chat (LLM): :9991
# - Embeddings bi-encoder:      :9994
LM_STUDIO_HOST=http://127.0.0.1:9991
EMBED_URL=http://127.0.0.1:9994

# Model Configuration (see lineup)
ANSWERER_USE_ALT=0
ANSWERER_MODEL_PRIMARY=christian-bible-expert-v2.0-12b
ANSWERER_MODEL_ALT=Qwen2.5-14B-Instruct-GGUF
EMBEDDING_MODEL=text-embedding-bge-m3

# Embedding Configuration
USE_QWEN_EMBEDDINGS=true  # embeddings served on :9994 (BGE-M3 1024-dim)

# Production Safety: No Mocks in Production
ALLOW_MOCKS_FOR_TESTS=0           # Only set to 1 inside unit tests
ENFORCE_QWEN_LIVE=1               # Require live Qwen models for enrichment

# Connection Settings
LM_STUDIO_TIMEOUT=30
LM_STUDIO_RETRY_ATTEMPTS=3
LM_STUDIO_RETRY_DELAY=2.0
LM_STUDIO_MOCK=false
```

#### Pipeline Configuration

```bash
# Processing Batch Size
BATCH_SIZE=50

# Batch Overrides (when <50 nouns found)
ALLOW_PARTIAL=0|1                 # if 1, manifest must capture reason
PARTIAL_REASON=<string>           # required when ALLOW_PARTIAL=1

# Semantic Network Configuration
VECTOR_DIM=1024

# Rerank-Driven Relationship Configuration
NN_TOPK=20
RERANK_MIN=0.50
EDGE_STRONG=0.90
EDGE_WEAK=0.75

# Quality Thresholds
GEMATRIA_CONFIDENCE_THRESHOLD=0.90
AI_CONFIDENCE_THRESHOLD=0.95

# Confidence Gates (soft = warn, hard = fail)
AI_CONFIDENCE_SOFT=0.90
AI_CONFIDENCE_HARD=0.95

# Relations Configuration (KNN + optional rerank)
ENABLE_RELATIONS=true
ENABLE_RERANK=true
SIM_MIN_COSINE=0.15
KNN_K=8
RERANK_TOPK=50
RERANK_PASS=0.50

# Pattern Discovery Configuration
CLUSTER_ALGO=louvain
CENTRALITY=degree,betweenness,eigenvector

# Exports Configuration
EXPORT_DIR=exports
```

#### Development & Observability

```bash
# Checkpointer / Orchestration
CHECKPOINTER=memory|postgres      # default: memory
WORKFLOW_ID=gemantria.v1          # defaults to gematria.v1

# Metrics & Logging
METRICS_ENABLED=1                 # 0 disables DB writes (stdout JSON remains)
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR

# Observability (Optional)
PROM_EXPORTER_ENABLED=0           # set to 1 to enable OpenMetrics exporter
PROM_EXPORTER_PORT=9108

# Database Debug
DB_DEBUG=false
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
```

### External Dependencies

- **LM Studio**: Local LLM server with Qwen3 models for semantic intelligence
- **PostgreSQL**: Primary database with pgvector extension for embeddings
- **Bible Database**: Read-only reference database (enforced at connection level)

### Observability Infrastructure

- **Postgres Views**: `v_node_latency_7d`, `v_node_throughput_24h`, `v_recent_errors_7d`, `v_pipeline_runs`
- **Materialized View**: `mv_node_latency_7d` (refresh via `SELECT refresh_metrics_materialized();`)
- **Metrics Sink**: Fail-open (never blocks pipeline); stdout JSON + optional Postgres logging
- **GitHub MCP**: Active for repository operations (issues, PRs, search, Copilot integration)

## Definitions of Done & Ready

### Definition of Ready (DoR)

**All of these must be true before starting work:**

- Tests planned and estimated
- ADR touched if schema/behavior changes
- Gates runnable (make lint test.unit)
- Environment setup documented
- Acceptance criteria defined

### Definition of Done (DoD)

**All of these must be true before merge:**

- Tests pass with ≥98% coverage
- Linting passes
- ADR updated if behavior changes
- Rules updated if workflow changes
- Documentation synchronized

## Workflow (small green PRs)

- Branch `feature/<short>` → **write tests first** → code → `make lint test.unit test.int coverage.report` → commit → push → PR
- Coverage ≥98% (required gate)
- Commit msg: `feat(area): what [no-mocks, deterministic, ci:green]`

### PR Template (Required)

- **Goal**: What this PR achieves
- **Files changed**: List of modified files
- **Tests added/updated**: Test coverage changes
- **Acceptance**: lint, tests, coverage ≥98%, safety checks
- **ADRs/rules touched**: Links to any architectural changes

## Quality Gates

- **Coverage**: ≥98% across all modules
- **Linting**: 100% ruff compliance
- **Tests**: Unit + Integration + E2E passing
- **Safety**: No mock datasets; DB read-only enforcement; Qwen Live Gate
- **Documentation**: ADRs for schema changes; AGENTS.md updates for workflow changes

## Production Safety & Qwen Live Gate

### Qwen Live Gate (Critical)

- **ENFORCE_QWEN_LIVE=1**: Pipeline calls `assert_qwen_live()` before network aggregation
- **Fail-Closed Behavior**: QwenUnavailableError on any health check failure
- **Health Check Requirements**: Verify model availability, test embeddings (1024-dim), measure latency
- **Production Mode**: USE_QWEN_EMBEDDINGS=true required; ALLOW_MOCKS_FOR_TESTS=0
- **Model Validation**: Embedding models tested with `/v1/embeddings`; reranker with `/v1/chat/completions`
- **Evidence Requirements**: Production runs provide undeniable proof of live inference (DB logs + reports)

### Database Safety

- **Bible DB Read-Only**: Enforced at connection level; any write attempt errors
- **Noun Collection Source**: `v_hebrew_tokens(book, chapter, verse, lemma, pos)` with optional adapter via `HEBREW_TOKENS_SQL_OVERRIDE` for non-standard schemas.
- **Book Normalization**: `src/core/books.py#normalize_book` maps aliases (Gen/Bereshit → Genesis) to canonical names.
- **Phase 8 Sources**: `v_concept_occurrences(book, concept_id, chapter, count)` feeds temporal patterns and forecasts.
- **Parameterized SQL Only**: No f-strings in DB operations; banned `%s` parameterization required
- **Connection Pooling**: Configured for performance and safety
- **Data Persistence Completeness (Rule 037)**: `make data.verify` MUST pass locally; `make ci.data.verify` MUST pass in CI for PRs touching pipeline/db/export code.

### Testing Safety

- **No Mock Datasets**: Tests code-verified or DB-derived only; no `__mocks__` folders
- **ALLOW_MOCKS_FOR_TESTS=0**: Only set to 1 inside unit tests; never in production code
- **Contract Tests**: Validate interface compliance between modules

### Report Generation Requirements

- **Automatic Execution**: Reports generated after every pipeline run via `scripts/generate_report.py`
- **Environment Loading**: All scripts automatically load `.env` files via `ensure_env_loaded()`
- **Template Validation**: Exact markdown/JSON templates; no missing sections
- **Real Data Only**: Reports contain actual pipeline data (enrichments, metrics, network stats)
- **No Trust Tests**: Manual verification required; tests insufficient for report accuracy
- **Database Integrity**: All required tables exist; column names match schemas
- **Connectivity**: No more "GEMATRIA_DSN not set" errors due to standardized environment loading

## Quick Commands

### Development Setup

```bash
# Automated bootstrap (recommended for new setups)
./scripts/bootstrap_dev.sh

# Manual setup (if bootstrap script doesn't work)
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade "psycopg[binary]" pgvector requests python-dotenv
cp env_example.txt .env  # Edit .env with your local config

# Verify environment is ready
make doctor

# Run full test suite
make test

# Run individual test categories
make test.unit          # Unit tests only
make test.integration   # Integration tests only
make test.e2e          # End-to-end tests only

# Quality checks
make lint              # Code linting
make coverage.report   # Coverage report

# Graph analysis and export
make analyze.graph     # Compute communities and centrality
make exports.graph     # Export viz-ready JSON
make exports.jsonld    # Export JSON-LD and RDF/Turtle for semantic web
make webui             # Launch React visualization (localhost:5173)

# Verify LM Studio lineup (env-only split)
make models.verify        # answerer chat ping + embeddings dim
make models.swap          # test alt answerer model
make models.params        # print runtime tuning hints
```

### WebUI Visualization

```bash
# Launch interactive graph visualization
make webui   # Opens localhost:5173 with React + Visx graph viewer

# Features:
# - Force-directed graph layout with cluster coloring
# - Node selection with detailed centrality metrics
# - Interactive zoom and pan
# - Real-time data loading from exports/graph_latest.json
# - Responsive design for large networks
```

### Pipeline Execution

```bash
# Run pipeline for specific book
python -m src.graph.graph --book Genesis

# Run with custom batch size
python -m src.graph.graph --book Genesis --batch-size 25

# Check Qwen model health
make check.qwen
```

### Database Operations

```bash
# Apply migrations (be careful with order)
psql "$GEMATRIA_DSN" -f migrations/001_initial_schema.sql
psql "$GEMATRIA_DSN" -f migrations/002_create_checkpointer.sql

# Check pipeline runs
psql "$GEMATRIA_DSN" -c "SELECT * FROM pipeline_runs ORDER BY created_at DESC LIMIT 5;"
```

### Report Generation

```bash
# Generate reports for latest run
python scripts/generate_report.py

# Generate report for specific run
python scripts/generate_report.py --run-id <run_id>
```

### Documentation Requirements (ALWAYS REQUIRED - Pre-PR)

```bash
# Documentation verification (MANDATORY before PR)
# For ANY code change: corresponding documentation must be updated or created
# - Update/create AGENTS.md files for new directories/modules
# - Update/create cursor rules for new behaviors
# - Create ADRs for schema/architecture/process/safety changes
# - Update cross-references between ADRs, rules, and docs

# Run documentation verification
./scripts/test_docs_sync_rule.sh
```

### Runbook: Postgres checkpointer

1. Apply migration:
   ```bash
   psql "$GEMATRIA_DSN" -f migrations/002_create_checkpointer.sql
   ```
2. Verify locally:
   ```bash
   export CHECKPOINTER=postgres
   export GEMATRIA_DSN=postgresql://user:pass@localhost:5432/gemantria
   make lint test.unit test.integration coverage.report
   ```
3. Expected: tests green, coverage ≥98%, checkpoint storage and retrieval works end-to-end.

### Runbook: Metrics & Logging

1. Apply migration:
   ```bash
   psql "${GEMATRIA_DSN}" -f migrations/003_metrics_logging.sql
   ```
2. Verify locally:
   ```bash
   export METRICS_ENABLED=1
   export LOG_LEVEL=INFO
   export WORKFLOW_ID=gemantria.v1
   make lint test.unit test.integration coverage.report
   ```
3. Expected: JSON logs to stdout, metrics rows in DB when enabled, pipeline unaffected by metrics failures.

### Runbook: Observability Dashboards

1. Apply migration:
   ```bash
   psql "${GEMATRIA_DSN}" -f migrations/004_metrics_views.sql
   ```
2. Verify locally:
   ```bash
   export PROM_EXPORTER_ENABLED=0  # Optional exporter disabled by default
   export PROM_EXPORTER_PORT=9108
   make lint test.unit test.integration coverage.report
   ```
3. Expected: SQL views created, queries return data when metrics exist, exporter optional.

### Runbook: LLM Integration

1. Apply migration:
   ```bash
   psql "${GEMATRIA_DSN}" -f migrations/005_ai_metadata.sql
   ```
2. Configure LM Studio:
   ```bash
   export LM_STUDIO_HOST=http://127.0.0.1:1234
   export THEOLOGY_MODEL=christian-bible-expert-v2.0-12b
   export MATH_MODEL=self-certainty-qwen3-1.7b-base-math
   export LM_STUDIO_MOCK=false  # Set to true for testing without LM Studio
   ```
3. Verify locally:
   ```bash
   make lint test.unit test.integration coverage.report
   ```
4. Expected: AI enrichment node integrates with pipeline, confidence scores stored in `ai_enrichment_log`, fallback to mock mode when LM Studio unavailable.

### Runbook: Semantic Network & Qwen Integration

1. Apply migrations:
   ```bash
   psql "${GEMATRIA_DSN}" -f migrations/007_concept_network.sql
   psql "${GEMATRIA_DSN}" -f migrations/008_add_concept_network_constraints.sql
   ```
2. Configure Qwen models:
   ```bash
   export USE_QWEN_EMBEDDINGS=true
   export QWEN_EMBEDDING_MODEL=qwen-embed
   export QWEN_RERANKER_MODEL=qwen-reranker
   export LM_STUDIO_HOST=http://127.0.0.1:1234
   ```
3. Verify locally:
   ```bash
   make lint test.unit test.integration coverage.report
   ```
4. Expected: Network aggregator generates 1024-dim embeddings, stores in `concept_network`, computes similarity relationships, and updates reports with network metrics.

### Runbook: Qwen Live Gate (No-Mocks Enforcement)

1. Apply migration:
   ```bash
   psql "${GEMATRIA_DSN}" -f migrations/010_qwen_health_log.sql
   ```
2. Configure production environment:
   ```bash
   export USE_QWEN_EMBEDDINGS=true
   export ALLOW_MOCKS_FOR_TESTS=0
   export QWEN_EMBEDDING_MODEL=text-embedding-qwen3-embedding-0.6b
   export QWEN_RERANKER_MODEL=qwen.qwen3-reranker-0.6b
   export LM_STUDIO_HOST=http://127.0.0.1:1234
   ```
3. Start LM Studio and load models:
   ```bash
   lms server start
   lms load Qwen/Qwen3-Embedding-0.6B-GGUF --identifier text-embedding-qwen3-embedding-0.6b --gpu=1.0
   lms load DevQuasar/Qwen.Qwen3-Reranker-0.6B-GGUF --identifier qwen.qwen3-reranker-0.6b --gpu=1.0
   ```
4. Preflight check:
   ```bash
   make check.qwen
   ```
5. Run pipeline (fails if models unavailable):
   ```bash
   python -m src.graph.graph --book Genesis --batch-size 10
   ```
6. Verify evidence:
   ```bash
   psql "${GEMATRIA_DSN}" -c "SELECT verified, embed_dim, lat_ms_embed FROM qwen_health_log ORDER BY id DESC LIMIT 1;"
   python scripts/generate_report.py --run-id <run_id>  # Check Qwen Live Verification section
   ```
7. Expected: Pipeline hard-fails if Qwen models unavailable; health log shows verified=true; report confirms live inference.

## Rules (summary)

- Normalize Hebrew: **NFKD → strip combining → strip maqaf/sof pasuq/punct → NFC**
- Mispar Hechrachi; finals=regular. Surface-form gematria with calc strings.
- Ketiv primary; variants recorded with `variant_type`; store span_start/end for instances.
- Batches default to 50; abort + `review.ndjson` on failure; `ALLOW_PARTIAL=1` override logs manifest.
- Default edges: shared_prime (cap k=3); optional identical_value/gcd_gt_1 behind flags.
- Layouts persisted with (algorithm, params_json, seed, version). New params → new layout id.
- Checkpointer: `CHECKPOINTER=postgres|memory` (memory default); Postgres requires `GEMATRIA_DSN`.
- LLM Integration: LM Studio with Qwen3 models; confidence scores are metadata only (never affect core gematria); `USE_QWEN_EMBEDDINGS=true` enables real semantic vectors; **no mocks in production** - pipeline hard-fails unless Qwen models live and verified.
- Semantic Network: pgvector embeddings (1024-dim, L2 normalized) with cosine similarity; strong edges ≥0.90, weak edges ≥0.75; Qwen3 inference for relationship discovery.
- GitHub operations: Use MCP server for issues/PRs/search; confirm ownership; search before creating; use Copilot for AI tasks.
- Forest Governance: Rule 025 requires `docs/forest/overview.md` regeneration before any PR; prevents drift between low-level changes and global system state.

## Documentation System

The project uses a dual documentation system for comprehensive coverage:

### README.md Files (User-Facing)

- **Purpose**: Human-readable guides, setup instructions, usage examples
- **Location**: Every directory has a README.md
- **Coverage**: Project overview, architecture, quick start, API usage
- **Audience**: Developers, users, maintainers

### AGENTS.md Files (AI Assistant Guidance)

- **Purpose**: Structured guidance for AI assistants working on code
- **Location**: Source code and tool directories
- **Coverage**: Development patterns, API contracts, testing standards, code quality requirements
- **Audience**: AI assistants, automated tooling, future maintainers

### Cross-References

- **AGENTS.md files** reference corresponding README.md files for user documentation
- **README.md files** reference AGENTS.md files for detailed development guidance
- **Both** reference ADRs for architectural decisions and SSOT for canonical schemas

### Documentation Requirements by Directory Type

| Directory Type           | README.md   | AGENTS.md       | Examples                                           |
| ------------------------ | ----------- | --------------- | -------------------------------------------------- |
| Source Code (src/\*/)    | ✅ Required | ✅ Required     | `src/core/`, `src/graph/`, `src/services/`         |
| Tools (scripts/, tests/) | ✅ Required | ✅ Required     | `scripts/`, `tests/`, `migrations/`                |
| Documentation (docs/\*/) | ✅ Required | ✅ Required     | `docs/`, `docs/ADRs/`, `docs/SSOT/`                |
| Generated Output         | ✅ Required | ❌ Not required | `reports/`, `exports/`, `data/`                    |
| Configuration            | ✅ Required | ❌ Not required | `.cursor/`, `.cursor/rules/`                       |
| Archive                  | ✅ Required | ❌ Not required | `archive/` - Legacy files and historical reference |

## How agents should use rules

### Rule System Overview

Cursor rules provide automated enforcement of project standards, code quality, and development workflows. Rules are stored in `.cursor/rules/` directory and automatically apply to relevant files based on glob patterns.

- **Global constraints** live in `.cursor/rules/000-always-apply.mdc` (always applied).
- **Path-scoped rules** auto-attach via `globs` (e.g., production safety rules for pipeline code).
- **One-off procedures** live as agent-requested rules (invoke by referencing their `description` in prompts).
- **Critical safety** enforced via rules like `011-production-safety.mdc` (Qwen Live Gate, fail-closed behavior).
- **Workflow rules** govern development processes and external service integration.

### When to Create New Cursor Rules

**Create a new rule when you encounter:**

#### **Critical Safety Issues**
- **Database Safety**: New SQL injection risks or unsafe query patterns
- **AI Model Safety**: New requirements around Qwen Live Gate or model validation
- **Production Risks**: New scenarios requiring fail-closed behavior or mock prohibitions
- **Data Integrity**: New requirements for Hebrew normalization or gematria calculation standards

#### **Recurring Development Problems**
- **Code Quality**: Common linting errors or style violations that keep happening
- **Workflow Issues**: Repeated mistakes in PR process, branch naming, or commit standards
- **Integration Problems**: Persistent issues with external services (LM Studio, databases)
- **Documentation Gaps**: Missing AGENTS.md files or incomplete documentation requirements

#### **New Project Standards**
- **Architecture Changes**: New design patterns or component structures
- **Performance Requirements**: New optimization or monitoring standards
- **Testing Standards**: New testing coverage or validation requirements
- **Security Policies**: New authentication, authorization, or data protection requirements

#### **Process Improvements**
- **Automation Opportunities**: Manual processes that can be automated or validated
- **Quality Gates**: New validation steps that should be enforced during development
- **Compliance Requirements**: New regulatory or organizational standards to enforce

### How to Create Cursor Rules

#### **1. Rule File Structure**
Create new rule files in `.cursor/rules/` following the naming convention:

```
XXX-descriptive-name.mdc
```

**Example:**
```
034-temporal-patterns-spec.mdc
035-forecasting-spec.mdc
036-temporal-visualization-spec.mdc
```

#### **2. Rule File Format**
Each rule file must follow the Markdown Cursor (`.mdc`) format:

```mdc
---
description: Brief description of the rule's purpose and scope
globs:
  - path/patterns/where/rule/applies
  - additional/patterns/as/needed
alwaysApply: true/false  # true for critical rules, false for conditional
---

# Rule XXX — Human-Readable Title
Brief explanation of what the rule enforces and why it matters.

## Enforcement Criteria
- Specific requirement 1
- Specific requirement 2
- Concrete validation steps

## Examples
### Good Example
```python
# Correct implementation
def process_data(data):
    validate_input(data)  # Proper validation
    return transform(data)
```

### Bad Example
```python
# Incorrect - violates rule
def process_data(data):
    return transform(data)  # Missing validation
```

## Rationale
Why this rule exists, what problems it prevents, and business impact.

## Related Rules
- Rule YYY: Related constraint or requirement
- Rule ZZZ: Complementary validation

## Related Documentation
- ADR-XXX: Architectural decision reference
- docs/SSOT/schema.json: Schema validation reference
```

#### **3. Rule Numbering Convention**
- **Sequential**: Next available number in the sequence (000-999)
- **Logical Grouping**: Related rules should be numbered consecutively
- **Gap Policy**: No gaps allowed - `rules_audit.py` will fail on missing numbers
- **Deprecation**: Mark deprecated rules as aliases pointing to active rules

#### **4. Glob Pattern Guidelines**
- **Specific**: Target only the files that need the rule
- **Efficient**: Avoid overly broad patterns that slow down IDE performance
- **Clear**: Use descriptive patterns that are easy to understand
- **Tested**: Verify patterns match intended files before committing

**Common glob patterns:**
```mdc
globs:
  - "src/**/*.py"           # All Python files in src/
  - "scripts/**/*.py"       # All Python files in scripts/
  - "**/AGENTS.md"          # All AGENTS.md files anywhere
  - "src/services/*.py"     # Specific service files
  - "**/*test*.py"          # Test files (anywhere, any depth)
```

#### **5. Always Apply vs. Conditional Rules**
- **`alwaysApply: true`**: Critical safety rules, global constraints, quality gates
- **`alwaysApply: false`**: Feature-specific rules, optional validations, workflow helpers

**Always apply examples:**
- Database safety rules
- Qwen Live Gate requirements
- Core documentation sync rules
- Critical production safety constraints

**Conditional examples:**
- Phase-specific validation rules
- Optional performance optimizations
- Feature-specific patterns

### Rule Categories and Examples

#### **Safety & Security Rules**
- **Database Safety** (001): SQL injection prevention, parameterized queries
- **Production Safety** (011): Qwen Live Gate, mock prohibitions
- **Infrastructure Safety** (007): Checkpointer validation, state persistence

#### **Quality Assurance Rules**
- **Code Quality**: Linting standards, formatting requirements
- **Testing**: Coverage thresholds, test organization
- **Documentation**: AGENTS.md presence, ADR requirements

#### **Domain-Specific Rules**
- **Gematria Validation** (002): Hebrew processing, calculation accuracy
- **Graph Processing** (003): Batch semantics, network construction
- **Semantic Networks** (010): Embedding standards, similarity thresholds

#### **Workflow & Process Rules**
- **PR Workflow** (004): Branch naming, commit standards
- **GitHub Operations** (005): MCP usage, issue management
- **Documentation Sync** (009): AGENTS.md updates, cross-references

### Rule Creation Workflow

#### **Step 1: Problem Identification**
- Identify the recurring issue or requirement
- Gather evidence of the problem (bug reports, code reviews, failures)
- Define the desired behavior and success criteria

#### **Step 2: Rule Design**
- Write clear, actionable enforcement criteria
- Define appropriate glob patterns for scope
- Determine if rule should always apply or be conditional
- Create examples of good and bad implementations

#### **Step 3: Implementation**
- Create the `.mdc` file with proper formatting
- Test the rule against existing code to verify it works
- Ensure rule numbering doesn't create gaps
- Update documentation references

#### **Step 4: Documentation Integration**
- Add rule to AGENTS.md rules table (auto-updated by `rules_audit.py`)
- Create or update relevant ADR if architectural
- Update related AGENTS.md files with rule references
- Add to verification matrix if needed

#### **Step 5: Testing & Validation**
- Run `rules_audit.py` to ensure numbering integrity
- Run `rules_guard.py` to verify documentation sync
- Test rule application in Cursor IDE
- Verify CI/CD pipeline still passes

### Rule Maintenance

#### **Regular Review**
- Review rule effectiveness quarterly
- Update rules as project standards evolve
- Remove or deprecate rules that are no longer relevant
- Consolidate overlapping or redundant rules

#### **Performance Monitoring**
- Monitor IDE performance impact of rules
- Optimize glob patterns for efficiency
- Balance rule strictness with developer productivity
- Ensure rules provide value without being overly restrictive

#### **Documentation Updates**
- Keep rule descriptions current and accurate
- Update examples as code patterns change
- Maintain cross-references between rules, ADRs, and docs
- Ensure rules remain discoverable and understandable

### Integration with Development Workflow

- **IDE Integration**: Rules provide real-time feedback during editing
- **Pre-commit Hooks**: `rules_audit.py` and `rules_guard.py` validate rules
- **CI/CD Pipeline**: Automated rule validation in GitHub Actions
- **Documentation Sync**: Rules automatically inventoried in AGENTS.md and MASTER_PLAN.md

#> **Phase-8 consolidation:** Rule 034 is the single active temporal suite; Rules 035/036 are deprecated pointers.

## Rule System Governance

- **Change Policy**: Rule changes require ADR for significant behavioral changes
- **Deprecation Policy**: Deprecated rules clearly marked with replacement references
- **Audit Trail**: All rule changes tracked in git history
- **Team Consensus**: Major rule changes discussed and approved by team

<!-- RULES_INVENTORY_START -->
| # | Title |
|---:|-------|
| 000 | # --- |
| 001 | # --- |
| 002 | # --- |
| 003 | # --- |
| 004 | # --- |
| 005 | # --- |
| 006 | # --- |
| 007 | # --- |
| 008 | # --- |
| 009 | # --- |
| 010 | # --- |
| 011 | # --- |
| 012 | # --- |
| 013 | # --- |
| 014 | # --- |
| 015 | # --- |
| 016 | # --- |
| 017 | # --- |
| 018 | # --- |
| 019 | # --- |
| 020 | # --- |
| 021 | # --- |
| 022 | # --- |
| 023 | # --- |
| 024 | # --- |
| 025 | # --- |
| 026 | # --- |
| 027 | # --- |
| 028 | # --- |
| 029 | # --- |
| 030 | # --- |
| 031 | # --- |
| 032 | # --- |
| 033 | # --- |
| 034 | # --- |
| 035 | # --- |
| 036 | # --- |
<!-- RULES_INVENTORY_END -->

# test doc update
