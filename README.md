# Gemantria v2.0

_A comprehensive pipeline for Hebrew biblical text analysis combining traditional gematria with modern AI semantic networks. Features deterministic processing, graph visualization, and multiple export formats for academic and personal research._

📋 **[Repository Index](docs/INDEX.md)** - Quick navigation for all documentation and configuration

[![CI](https://github.com/iog-creator/Gemantria/workflows/CI/badge.svg)](https://github.com/iog-creator/Gemantria/actions)
[![License](https://img.shields.io/badge/license-Personal%20Use%20Only-red.svg)](LICENSE)

## 🌟 Overview

Gemantria is a sophisticated pipeline that combines traditional Hebrew gematria analysis with modern semantic AI to create verified concept networks from biblical text. The system produces both structured data exports and interactive visualizations.

### Current Status

**Phase 9**: Advanced evaluation pipeline with edge anomaly detection, quality monitoring, and comprehensive artifact generation. Features deterministic processing, extensive validation gates, and production-ready exports.

### Key Features

- **📚 Hebrew Text Analysis**: Traditional gematria calculations with modern verification
- **🤖 AI-Powered Semantics**: Qwen3 embeddings and reranking for concept relationships
- **🕸️ Network Analysis**: Graph algorithms for community detection and centrality metrics
- **📊 Interactive Visualization**: React-based graph explorer with real-time data loading
- **📋 Multiple Export Formats**: JSON-LD, RDF/Turtle, and structured JSON exports
- **🔒 Production Safety**: Qwen Live Gate and comprehensive validation gates
- **📈 Evaluation Pipeline**: Edge audit, anomaly detection, and quality monitoring
- **🎯 Deterministic Processing**: Reproducible results with comprehensive testing

---

## 🚀 60-Second Runbook (copy/paste)

**Zero decisions:**
```bash
make go
```

**Or manually:**
```bash
# 1) Install tooling (once)
pip install -U ruff pytest pre-commit
pre-commit install

# 2) Lint & format + fast fixes
make py.fullwave.c     # quickfix + longline + format + lint + (types optional)

# 3) Audits and smoke
make rules.navigator.check rules.audit repo.audit docs.audit
make test.smoke        # skips cleanly if LM Studio endpoints are down

# 4) Share artifacts
make share.sync
```

### Quality Gates (cheat-sheet)
| Gate | Command | Expectation |
|---|---|---|
| Lint | `ruff check` | Only intentional `E501` with `# noqa: E501` (URLs/SQL/regex/payloads) |
| Audits | `make rules.navigator.check rules.audit repo.audit docs.audit` | All green |
| Smoke | `make test.smoke` | 2 passed or skipped (if endpoints unavailable) |
| Share | `make share.sync` | Mirrors only allow-listed outputs |

### Book Readiness Flow

**Setup once (hard requirement):**
```bash
make deps.dev
```

Schema validation is **mandatory**. If it fails or `jsonschema` isn't installed, readiness checks will fail.

Artifacts mirrored to share: **only** `reports/readiness/readiness_report.json`.
Operational traces & logs live in `logs/` (not mirrored) to avoid churn.

### Whole-Book Operations (deterministic & safe)
```bash
# Plan chapters (no inference)
make book.plan
# Dry-run checks (no inference)
make book.dry
# Stop-loss: run first N chapters with real inference
make book.stop N=1
# Resume last run
make book.resume
```
Seeds and endpoints come from `config/book_plan.yaml` (and `.env`). Logs live under `logs/book/`.

> Navigator (always-apply) rules: `000-ssot-index.mdc`, `010-task-brief.mdc`, `030-share-sync.mdc` (see `AGENTS.md`).

### SSOT Cross-References (contracts & example heads)
| Domain | Schema (authoritative) | Example head export (for quick inspection) |
|---|---|---|
| Graph patterns | `SSOT_graph-patterns.schema.json` | `graph_stats.head.json` |
| Temporal patterns | `SSOT_temporal-patterns.schema.json` | `temporal_patterns.head.json` |
| Pattern forecast | `SSOT_pattern-forecast.schema.json` | `pattern_forecast.head.json` |

> Heads are truncated JSONs intended for PR review and CI proofs; full artifacts live under `exports/` in real runs.


> **Note:** Phase-8 rules are consolidated under **Rule 034** (Temporal Analytics Suite).### Smoke tests (models)
Run a quick health check against local LM Studio endpoints:
```bash
make test.smoke   # verifies /v1/models advertises the answerer; embeddings are 1024-dim
```
Override defaults with `LM_CHAT_HOST/LM_CHAT_PORT` and `LM_EMBED_HOST/LM_EMBED_PORT` if needed.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL with pgvector extension
- LM Studio with Qwen3 models (optional for development)
- Node.js 18+ (for webui)

### Installation

```bash
# Clone the repository
git clone https://github.com/iog-creator/Gemantria.git
cd Gemantria.v2

# Set up Python environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
make deps

# Set up environment variables (copy from env_example.txt)
cp env_example.txt .env
# Edit .env with your database and LM Studio settings
```

### Basic Usage

````bash
# Run pipeline for Genesis (requires BIBLE_DB_DSN; bible_db is read-only)
python -m src.graph.graph --book Genesis

# Generate exports
make exports.graph     # JSON graph data
make exports.jsonld    # JSON-LD + RDF/Turtle

# Launch visualization
make webui            # Opens http://localhost:5173
### Temporal Analytics (Phase 8)

```bash
# Produce temporal and forecast exports (validated against SSOT schemas)
python scripts/export_stats.py
python -m src.services.api_server &
curl -s 'http://127.0.0.1:8000/api/v1/temporal?unit=chapter&window=5' | jq
curl -s 'http://127.0.0.1:8000/api/v1/forecast?horizon=10' | jq
# Phase-8 endpoints read from exports/ (override with EXPORT_DIR)
````

# Run tests

make test

```

## 📁 Project Structure

```

gemantria/
├── src/ # Core pipeline code
│ ├── core/ # Core processing logic
│ ├── graph/ # Graph processing & LangGraph pipeline
│ ├── infra/ # Infrastructure (DB, logging, checkpointer)
│ ├── nodes/ # LangGraph node implementations
│ ├── obs/ # Observability & metrics
│ └── services/ # External service integrations
├── scripts/ # Utility scripts & export tools
├── tests/ # Test suites (unit, integration, e2e)
├── webui/graph/ # React visualization application
├── docs/ # Documentation
│ ├── ADRs/ # Architectural Decision Records
│ └── SSOT/ # Single Source of Truth schemas
├── migrations/ # Database schema migrations
├── reports/ # Generated pipeline reports
├── exports/ # Data export outputs
├── .cursor/rules/ # Cursor IDE configuration rules
└── AGENTS.md # Agent documentation for AI assistants

````

## 🏗️ Architecture

Gemantria follows a deterministic pipeline architecture with multiple safety gates:

1. **Text Extraction**: Extract Hebrew nouns from biblical text
2. **Gematria Calculation**: Compute traditional gematria values
3. **AI Enrichment**: Generate semantic insights using Qwen3 models
4. **Network Aggregation**: Build semantic relationships using embeddings
5. **Graph Analysis**: Apply community detection and centrality algorithms
6. **Export & Visualization**: Generate multiple formats and interactive UI

### Safety Gates

- **Qwen Live Gate**: Requires verified live Qwen models for production runs
- **Batch Validation**: Enforces 50-noun minimum (ALLOW_PARTIAL=1 for exceptions)
- **Read-Only Bible DB**: Enforces separation between reference and working data
- **Parameterized SQL**: Prevents SQL injection through query parameterization

## 📦 Shipping UX (Local Evaluation Dashboard)

Gemantria includes a polished evaluation system for local development and handoff:

```bash
# Generate complete evaluation package
make eval.package

# View interactive dashboard (opens browser)
make eval.open

# Download all artifacts as single bundle
make eval.bundle.all
```

**Dashboard Features:**
- **Status badges** embedded inline (PASS/FAIL/WARN indicators)
- **Release manifest viewer** with artifact inventory (expandable table)
- **Integrity verification** with hash checking
- **Offline operation** (works without internet)

**Artifacts include:**
- HTML dashboard with embedded badges and manifest viewer
- JSON reports, Markdown summaries, and CSV exports
- Deterministic tar.gz bundle for handoff
- Integrity verification reports

See [`docs/PHASE8_EVAL.md`](docs/PHASE8_EVAL.md) for complete documentation.

## 🔧 Configuration

### Environment Variables

See `env_example.txt` for complete configuration options. Key variables:

```bash
# Database
GEMATRIA_DSN=postgresql://user:pass@localhost:5432/gematria
BIBLE_DB_DSN=postgresql://user:pass@localhost:5432/bible_db

## AI Models (split endpoints)
# Chat models (answerer/critic) on :9991; embeddings on :9994
LM_STUDIO_HOST=http://127.0.0.1:9991
EMBED_URL=http://127.0.0.1:9994
ANSWERER_MODEL_PRIMARY=christian-bible-expert-v2.0-12b
ANSWERER_MODEL_ALT=Qwen2.5-14B-Instruct-GGUF
EMBEDDING_MODEL=text-embedding-bge-m3  # 1024-dim, L2-normalized

# Safety Gates
ENFORCE_QWEN_LIVE=1          # Require live models
ALLOW_MOCKS_FOR_TESTS=0      # Production safety
ALLOW_PARTIAL=0              # Batch validation
````

### Pipeline Configuration

```bash
# Processing settings
BATCH_SIZE=50               # Nouns per batch
VECTOR_DIM=1024             # Embedding dimensions

# Network parameters (see SSOT + report generator expectations)
EDGE_STRONG=0.88            # Strong relationship threshold
EDGE_WEAK=0.70              # Weak relationship threshold
NN_TOPK=10                  # KNN neighbors for relationships
```

## 📊 Outputs

### Data Exports

- **Graph JSON**: `exports/graph_latest.json` - Node-link format for visualization
- **JSON-LD**: `exports/graph_latest.jsonld` - Semantic web standard format
- **RDF/Turtle**: `exports/graph_latest.ttl` - W3C knowledge graph format
- **Statistics**: Runtime-generated metrics for dashboard consumption

### Reports

- **Pipeline Reports**: `reports/run_*.md` - Markdown summaries of each run
- **Health Reports**: Model health verification and latency metrics
- **Coverage Reports**: Test coverage and quality metrics

## 🧪 Development

### Testing

```bash
# Run all tests
make test

# Run specific test suites
make test.unit          # Unit tests only
make test.integration   # Integration tests
make test.e2e          # End-to-end tests

# Quality checks
make lint              # Code linting
make type              # Type checking
make coverage.report   # Coverage report
```

### Documentation

The project uses a comprehensive documentation system:

- **AGENTS.md**: AI assistant guides for each module
- **README.md**: User-facing documentation for each directory
- **ADR**: Architectural decision records in `docs/ADRs/`
- **SSOT**: Canonical schemas in `docs/SSOT/`
- **Rules**: Cursor IDE configuration in `.cursor/rules/`

### Contributing

1. Follow the established PR workflow in AGENTS.md
2. Ensure all changes include updated documentation
3. Run full test suite before submitting
4. Update relevant AGENTS.md and README.md files

## 📈 Roadmap

- **Phase 4** ✅: Semantic network with embeddings and relations
- **Phase 5** ✅: Enhanced analytics and pattern discovery
- **Phase 6** ✅: Multi-text support and cross-references
- **Phase 7** ✅: Advanced visualization and exploration tools
- **Phase 8** ✅: Temporal Analytics Suite (forecasts + visualization)
- **Phase 9** 🔄: Evaluation pipeline with edge audit & anomaly detection

## 📄 License

**Personal Use Only License** - see LICENSE file for details.

This software is provided free for personal, non-commercial use only. Commercial use requires a separate license agreement. Contact the repository owner for commercial licensing inquiries.

## 🤝 Contributing

See AGENTS.md for detailed contribution guidelines and development setup.

## 🙏 Acknowledgments

- Hebrew text processing using traditional gematria methods
- Qwen3 models for semantic understanding
- LangGraph for pipeline orchestration
- pgvector for embedding storage and similarity search

## Smoke tests (models)

Run a quick health check against local LM Studio endpoints:

```bash
make test.smoke   # verifies /v1/models has your answerer; embeddings are 1024-dim
```

Set `LM_CHAT_HOST/LM_CHAT_PORT` and `LM_EMBED_HOST/LM_EMBED_PORT` if not using defaults.

## CI guardrails
All gates run locally and in CI:
```bash
pre-commit run -a    # ruff, black, mypy, audits, share.sync
make ci.smart        # smart strict/soft choice + audits\nmake ci              # mirrors CI locally (legacy)
```
CI workflow lives in `.github/workflows/ci.yml`.
Nightly typing: non-blocking full-repo mypy report (see Actions → typing-nightly).
Nightly linting: non-blocking full-repo ruff report (see Actions → lint-nightly).
Nightly coverage: non-blocking full-repo pytest coverage (see Actions → coverage-nightly).

### Nightly Workflow Status
![typing-nightly](https://github.com/iog-creator/Gemantria/actions/workflows/typing-nightly.yml/badge.svg)
![lint-nightly](https://github.com/iog-creator/Gemantria/actions/workflows/lint-nightly.yml/badge.svg)
![coverage-nightly](https://github.com/iog-creator/Gemantria/actions/workflows/coverage-nightly.yml/badge.svg)

---

> Looking for the full documentation? See **README_FULL.md**.
