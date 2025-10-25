# Core Pipeline Source Code

This directory contains the core implementation of the Gemantria semantic network pipeline. The code is organized into modules that follow a clear separation of concerns, with each module handling specific aspects of the text analysis, AI processing, and graph construction pipeline.

## 📁 Directory Structure

```
src/
├── core/              # Core processing logic and algorithms
├── graph/             # LangGraph pipeline orchestration and graph processing
├── infra/             # Infrastructure services (database, logging, checkpointer)
├── nodes/             # Individual LangGraph node implementations
├── obs/               # Observability and metrics collection
└── services/          # External service integrations (LM Studio, APIs)
```

## 🏗️ Architecture Overview

The pipeline follows a modular architecture where each module has clear responsibilities:

### Core Processing Flow

1. **Text Analysis** (`core/`): Extract and analyze Hebrew text
2. **Node Processing** (`nodes/`): Individual pipeline steps in LangGraph
3. **Graph Orchestration** (`graph/`): Coordinate the entire pipeline
4. **External Services** (`services/`): Handle AI model interactions
5. **Infrastructure** (`infra/`): Provide persistence and monitoring
6. **Observability** (`obs/`): Track performance and health

### Key Design Principles

- **Separation of Concerns**: Each module has a single, clear responsibility
- **Dependency Injection**: Services are injected rather than imported directly
- **Interface Contracts**: Clear interfaces between modules for testability
- **Configuration Management**: All settings managed through environment variables
- **Error Handling**: Comprehensive error handling with appropriate logging

## 🔧 Key Components

### Core Module (`core/`)

Contains the fundamental algorithms for Hebrew text processing, gematria calculations, and validation logic. This is where the core business logic resides.

### Graph Module (`graph/`)

Implements the LangGraph pipeline orchestration, managing the flow of data through various processing nodes and coordinating the overall execution.

### Infrastructure (`infra/`)

Provides essential services like database connections, structured logging, and state persistence through the checkpointer system.

### Services (`services/`)

Handles integrations with external dependencies like LM Studio for AI model access, with proper error handling and health checking.

### Nodes (`nodes/`)

Contains the individual processing steps that make up the LangGraph pipeline, each implementing a specific transformation or analysis.

## 🚀 Getting Started

### Running the Pipeline

```bash
# From project root
python -m src.graph.graph --book Genesis
```

### Development Setup

```bash
# Install dependencies
make deps

# Run tests
make test.unit

# Check types
make type
```

### Key Entry Points

- **`src/graph/graph.py`**: Main pipeline entry point
- **`src/infra/db.py`**: Database connection management
- **`src/services/lmstudio_client.py`**: AI model client

## 📋 Module Responsibilities

| Module      | Responsibility                        | Key Files                                   |
| ----------- | ------------------------------------- | ------------------------------------------- |
| `core/`     | Text processing, gematria, validation | `extraction.py`, `validation.py`            |
| `graph/`    | Pipeline orchestration                | `graph.py`, `pipeline.py`                   |
| `infra/`    | Persistence, logging                  | `db.py`, `structured_logger.py`             |
| `nodes/`    | Processing steps                      | `ai_enrichment.py`, `network_aggregator.py` |
| `services/` | External APIs                         | `lmstudio_client.py`, `config.py`           |
| `obs/`      | Metrics collection                    | `prom_exporter.py`                          |

## 🔒 Safety & Quality

### Code Quality Gates

- **Type Checking**: 100% mypy compliance
- **Linting**: ruff compliance with zero warnings
- **Testing**: 98%+ code coverage across all modules
- **Documentation**: AGENTS.md present in each module

### Safety Features

- **Read-Only Bible DB**: Reference database protected from writes
- **Parameterized SQL**: All database queries use parameterized statements
- **Qwen Live Gate**: AI models must be verified live before use
- **Batch Validation**: Minimum batch sizes enforced for reliability

## 📚 Documentation

- **[AGENTS.md](AGENTS.md)**: AI assistant guide for this module
- **Module READMEs**: Each submodule has its own README
- **ADR References**: See related architectural decisions in docs/ADRs/

## 🔄 Development Workflow

1. **Feature Development**: Create/modify code in appropriate module
2. **Testing**: Add/update tests in corresponding test directory
3. **Documentation**: Update AGENTS.md and README.md as needed
4. **Quality Checks**: Run `make lint type test.unit`
5. **Integration**: Test with full pipeline before PR

## 🤝 Contributing

When adding new modules or modifying existing ones:

1. Follow the established directory structure
2. Add comprehensive type hints
3. Include unit tests with 98%+ coverage
4. Update AGENTS.md with AI assistant guidance
5. Add README.md for user-facing documentation
6. Update this overview if adding new top-level modules
