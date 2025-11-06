# AGENTS.md - src/ssot Directory

## Directory Purpose

The `src/ssot/` directory contains Single Source of Truth (SSOT) implementations for canonical data shapes and adapters. Created during consolidation to eliminate duplicate data transformations and ensure consistent noun representations across the pipeline.

## Key Components

### `noun_adapter.py` - Canonical Noun Adapter

**Purpose**: Provides canonical noun shape and data transformation for organic AI discovery results. SSOT implementation ensuring consistent noun data structures throughout the pipeline.

**Key Functions**:
- `adapt_ai_noun()` - Converts AI discovery results to canonical noun format
- `validate_noun_schema()` - Ensures noun data meets SSOT requirements
- `normalize_noun_data()` - Standardizes noun representations for downstream processing

**Requirements**:
- **Schema Compliance**: All nouns conform to gematria/ai-nouns.v1 schema
- **Data Normalization**: Consistent Hebrew text, gematria calculations, and metadata
- **Type Safety**: Proper typing for all noun attributes and transformations
- **Immutability**: Pure functions that don't modify input data

## API Contracts

### Noun Adapter Interface
```python
def adapt_ai_noun(ai_result: dict) -> dict:
    """Convert AI discovery result to canonical noun format."""

def validate_noun_schema(noun: dict) -> bool:
    """Validate noun against SSOT schema requirements."""

def normalize_noun_data(nouns: List[dict]) -> List[dict]:
    """Normalize list of nouns to canonical format."""
```

## Testing Strategy

- **Unit Tests**: Individual adapter function validation
- **Schema Tests**: JSON schema compliance validation
- **Integration Tests**: End-to-end noun processing pipeline
- **Property Tests**: Data transformation invariants

## Development Guidelines

- All noun transformations must go through the adapter
- Schema changes require ADR updates (ADR-032)
- Maintain backwards compatibility for existing noun data
- Include comprehensive type hints for all interfaces
- Document any schema extensions or modifications

## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
| noun_adapter.py | ADR-032 (Organic AI Discovery) |
| SSOT Implementation | ADR-019 (Data Contracts) |
