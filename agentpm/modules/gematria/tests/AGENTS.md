# AGENTS.md - agentpm/modules/gematria/tests Directory

## Directory Purpose

The `agentpm/modules/gematria/tests/` directory contains unit tests for the Gematria module components, ensuring correctness and reliability of Hebrew text processing, gematria calculations, and data transformations.

## Test Files

### Core Tests
- **test_core.py**: Tests for core Gematria calculation and Hebrew processing functions
- **test_hebrew.py**: Tests for Hebrew text normalization and letter extraction
- **test_hebrew_utils.py**: Tests for Hebrew utility functions (migrated from `tests/unit/`)

### Utility Tests
- **test_noun_adapter.py**: Tests for noun data adapter (`adapt_ai_noun()` function)
- **test_osis.py**: Tests for OSIS reference parsing utilities

## Test Coverage

The test suite covers:
- Hebrew text normalization (NFKD → strip combining → strip maqaf/sof pasuq/punct → NFC)
- Gematria calculations (Mispar Hechrachi, finals=regular)
- Noun data transformation and UUID generation
- OSIS reference extraction and normalization
- Edge cases (empty strings, missing fields, zero values)

## Running Tests

```bash
# Run all Gematria module tests
pytest agentpm/modules/gematria/tests/ -v

# Run specific test file
pytest agentpm/modules/gematria/tests/test_noun_adapter.py -v

# Run with coverage
pytest agentpm/modules/gematria/tests/ --cov=agentpm.modules.gematria --cov-report=html
```

## Test Migration Status

These tests were migrated from `tests/unit/` as part of the Gematria Module Extraction Plan (Phases 1-6):
- Phase 1: `test_hebrew_utils.py` migrated
- Phase 5: `test_noun_adapter.py` created
- Phase 6: `test_osis.py` created

## Integration

Tests verify functionality used by:
- Core Gematria pipeline (`agentpm/modules/gematria/core/`)
- Graph building nodes (`src/graph/nodes/`)
- Enrichment pipeline (`src/nodes/enrichment.py`)

