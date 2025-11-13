# AGENTS.md - src/ Directory

## Directory Purpose

The `src/` directory contains core pipeline components including pattern correlation analysis, temporal span generation, and data structures for gematria calculations. This directory serves as the foundation for the Gemantria analysis pipeline.

## Key Components

### `correlations.py` - Pattern Correlation Engine

**Purpose**: Analyze cross-text pattern correlations and relationships between concepts across biblical texts. Implements pattern discovery algorithms for identifying semantic and numerical relationships.

**Key Features**:
- Cross-book pattern analysis
- Correlation strength calculation
- Pattern significance metrics (support, lift, confidence)
- Integration with graph analysis for relationship discovery

**Related ADRs**: ADR-018 (Pattern Correlation)

### `temporal.py` - Temporal Span Generation

**Purpose**: Generate temporal spans and time-series data for analyzing concept frequency and patterns over sequential verse/chapter indices. Supports rolling window analysis and change point detection.

**Key Features**:
- Verse/chapter index-based temporal series
- Rolling window calculations (mean, sum)
- Change point detection
- Integration with Phase 8 temporal analytics

**Related ADRs**: ADR-025 (Multi-Temporal Analytics)

## Subdirectories

The `src/` directory is organized into specialized subdirectories:

- **`core/`**: Fundamental utilities (Hebrew processing, ID generation) - See [core/AGENTS.md](core/AGENTS.md)
- **`graph/`**: LangGraph pipeline orchestration - See [graph/AGENTS.md](graph/AGENTS.md)
- **`nodes/`**: Individual pipeline node implementations - See [nodes/AGENTS.md](nodes/AGENTS.md)
- **`services/`**: External service integrations (DB, LM Studio) - See [services/AGENTS.md](services/AGENTS.md)
- **`infra/`**: Infrastructure components (DB, metrics, logging) - See [infra/AGENTS.md](infra/AGENTS.md)
- **`utils/`**: Utility functions (JSON sanitization, OSIS) - See [utils/AGENTS.md](utils/AGENTS.md)
- **`persist/`**: Persistence utilities (run tracking) - See [persist/AGENTS.md](persist/AGENTS.md)
- **`rerank/`**: Reranking and edge strength blending - See [rerank/AGENTS.md](rerank/AGENTS.md)
- **`ssot/`**: SSOT adapters (format normalization) - See [ssot/AGENTS.md](ssot/AGENTS.md)
- **`obs/`**: Observability components (Prometheus) - See [obs/AGENTS.md](obs/AGENTS.md)

## Development Workflow

### Code Generation

- **Use `codex.task`**: For AI-assisted code generation
- **Follow Patterns**: Use existing components as templates
- **Type Safety**: All functions must have complete type hints

### Quality Gates

- **Always sync share/**: Run `make share.sync` after changes
- **Run Tests**: Execute `make test.unit test.integration` before committing
- **Lint & Format**: Run `ruff format . && ruff check .` before PR
- **Coverage**: Maintain ≥98% test coverage

### Documentation

- **Update AGENTS.md**: When adding new components or changing behavior
- **Link ADRs**: Reference related ADRs in component documentation
- **Examples**: Include usage examples in docstrings

## Testing Strategy

### Unit Tests

- **Pure Functions**: Test correlation and temporal functions in isolation
- **Edge Cases**: Test boundary conditions and error scenarios
- **Determinism**: Verify same inputs produce same outputs

### Integration Tests

- **Pipeline Integration**: Test components work together in full pipeline
- **Data Flow**: Verify data transformations between stages
- **Performance**: Test with realistic data volumes

## Related ADRs

| Component | Related ADRs |
|-----------|--------------|
| `correlations.py` | ADR-018 (Pattern Correlation) |
| `temporal.py` | ADR-025 (Multi-Temporal Analytics) |
| Core Pipeline | ADR-001 (Two-DB Safety), ADR-002 (Gematria Validation), ADR-003 (Graph & Batch) |

## Related Rules

- **Rule 006**: AGENTS.md Governance
- **Rule 017**: Agent Docs Presence
- **Rule 002**: Gematria Validation
- **Rule 003**: Graph & Batch

## Related Documentation

- **Root**: [../AGENTS.md](../AGENTS.md) - Repository overview and agent framework
- **Subdirectories**: See individual AGENTS.md files in each subdirectory
- **SSOT**: [docs/SSOT/](../docs/SSOT/) - Schema definitions and contracts