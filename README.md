# Gemantria v2.0

_A deterministic semantic network pipeline for Hebrew text analysis using gematria, embeddings, and AI inference._

[![CI](https://github.com/your-org/gemantria/workflows/CI/badge.svg)](https://github.com/your-org/gemantria/actions)
[![Coverage](https://codecov.io/gh/your-org/gemantria/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/gemantria)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🌟 Overview

Gemantria is a sophisticated pipeline that combines traditional Hebrew gematria analysis with modern semantic AI to create verified concept networks from biblical text. The system produces both structured data exports and interactive visualizations.

### Key Features

- **📚 Hebrew Text Analysis**: Traditional gematria calculations with modern verification
- **🤖 AI-Powered Semantics**: Qwen3 embeddings and reranking for concept relationships
- **🕸️ Network Analysis**: Graph algorithms for community detection and centrality metrics
- **📊 Interactive Visualization**: React-based graph explorer with real-time data loading
- **📋 Multiple Export Formats**: JSON-LD, RDF/Turtle, and structured JSON exports
- **🔒 Production Safety**: Qwen Live Gate and comprehensive validation gates

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL with pgvector extension
- LM Studio with Qwen3 models (optional for development)
- Node.js 18+ (for webui)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/gemantria.git
cd gemantria

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

```bash
# Run pipeline for Genesis
python -m src.graph.graph --book Genesis

# Generate exports
make exports.graph     # JSON graph data
make exports.jsonld    # JSON-LD + RDF/Turtle

# Launch visualization
make webui            # Opens http://localhost:5173

# Run tests
make test
```

## 📁 Project Structure

```
gemantria/
├── src/                    # Core pipeline code
│   ├── core/              # Core processing logic
│   ├── graph/             # Graph processing & LangGraph pipeline
│   ├── infra/             # Infrastructure (DB, logging, checkpointer)
│   ├── nodes/             # LangGraph node implementations
│   ├── obs/               # Observability & metrics
│   └── services/          # External service integrations
├── scripts/               # Utility scripts & export tools
├── tests/                 # Test suites (unit, integration, e2e)
├── webui/graph/           # React visualization application
├── docs/                  # Documentation
│   ├── ADRs/             # Architectural Decision Records
│   └── SSOT/             # Single Source of Truth schemas
├── migrations/           # Database schema migrations
├── reports/              # Generated pipeline reports
├── exports/              # Data export outputs
├── .cursor/rules/        # Cursor IDE configuration rules
└── AGENTS.md             # Agent documentation for AI assistants
```

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

## 🔧 Configuration

### Environment Variables

See `env_example.txt` for complete configuration options. Key variables:

```bash
# Database
GEMATRIA_DSN=postgresql://user:pass@localhost:5432/gematria
BIBLE_DB_DSN=postgresql://user:pass@localhost:5432/bible_db

# AI Models
LM_STUDIO_HOST=http://127.0.0.1:1234
THEOLOGY_MODEL=christian-bible-expert-v2.0-12b
MATH_MODEL=self-certainty-qwen3-1.7b-base-math
QWEN_EMBEDDING_MODEL=text-embedding-qwen3-embedding-0.6b

# Safety Gates
ENFORCE_QWEN_LIVE=1          # Require live models
ALLOW_MOCKS_FOR_TESTS=0      # Production safety
ALLOW_PARTIAL=0              # Batch validation
```

### Pipeline Configuration

```bash
# Processing settings
BATCH_SIZE=50               # Nouns per batch
VECTOR_DIM=1024             # Embedding dimensions

# Network parameters
EDGE_STRONG=0.90            # Strong relationship threshold
EDGE_WEAK=0.75              # Weak relationship threshold
NN_TOPK=20                  # KNN neighbors for relationships
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
- **Phase 5**: Enhanced analytics and pattern discovery
- **Phase 6**: Multi-text support and cross-references
- **Phase 7**: Advanced visualization and exploration tools

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

See AGENTS.md for detailed contribution guidelines and development setup.

## 🙏 Acknowledgments

- Hebrew text processing using traditional gematria methods
- Qwen3 models for semantic understanding
- LangGraph for pipeline orchestration
- pgvector for embedding storage and similarity search
