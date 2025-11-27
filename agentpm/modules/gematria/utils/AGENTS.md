# AGENTS.md - agentpm/modules/gematria/utils Directory

## Directory Purpose

The `agentpm/modules/gematria/utils/` directory contains utility functions for Gematria module operations, including:

- **ai_noun_discovery.py**: AI-powered organic noun discovery from Hebrew text
- **collect_nouns_db.py**: Database noun collection logic for retrieving nouns from the Bible database
- **hebrew_utils.py**: Hebrew text normalization and processing utilities
- **math_verifier.py**: Gematria calculation verification logic
- **noun_adapter.py**: Noun data adapter for canonical output format conversion
- **osis.py**: OSIS (Open Scripture Information Standard) reference parsing utilities

## Key Components

### AI Noun Discovery
- **Function**: `discover_nouns_for_book()` - Uses AI to organically discover and analyze nouns from Hebrew text
- **Location**: `ai_noun_discovery.py`
- **Dependencies**: LM Studio/Ollama (theology model), Bible database (read-only), Hebrew normalization utilities
- **Features**: AI-powered noun extraction, gematria calculation, classification (person/place/thing), frequency analysis

### Database Noun Collection
- **Function**: `collect_nouns_for_book()` - Retrieves nouns from the Bible database for a given book
- **Location**: `collect_nouns_db.py`
- **Dependencies**: Bible database (read-only), DSN configuration

### Hebrew Utilities
- **Functions**: Hebrew text normalization, gematria calculation, letter extraction
- **Location**: `hebrew_utils.py`
- **Dependencies**: None (pure functions)

### Math Verification
- **Function**: `verify_gematria_calculations()` - Verifies gematria calculations using LM models
- **Location**: `math_verifier.py`
- **Dependencies**: LM models (optional, falls back gracefully)

### Noun Adapter
- **Function**: `adapt_ai_noun()` - Converts AI-discovered nouns to canonical format
- **Location**: `noun_adapter.py`
- **Dependencies**: None (pure transformation)

### OSIS Utilities
- **Functions**: `extract_verse_references()`, `normalize_book_to_osis()` - OSIS reference parsing
- **Location**: `osis.py`
- **Dependencies**: None (pure parsing)

## Testing

Unit tests are located in `agentpm/modules/gematria/tests/`:
- `test_hebrew_utils.py` - Tests for Hebrew utilities
- `test_noun_adapter.py` - Tests for noun adapter
- `test_osis.py` - Tests for OSIS utilities

## Integration

These utilities are used by:
- Core Gematria pipeline (`agentpm/modules/gematria/core/`)
- Graph building nodes (`src/graph/nodes/`)
- Enrichment pipeline (`src/nodes/enrichment.py`)

