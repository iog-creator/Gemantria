# AGENTS.md - Core Utilities Directory

## Directory Purpose

The `src/core/` directory contains fundamental utilities and data processing functions that are used across the entire Gemantria pipeline. These are pure functions with no external dependencies.

## Key Components

### `hebrew_utils.py` - Hebrew Text Processing

**Purpose**: Normalize and validate Hebrew text according to gematria requirements
**Key Functions**:

- `normalize_hebrew()` - NFKD → strip combining → strip maqaf/sof pasuq/punct → NFC
- `validate_hebrew_text()` - Ensure text contains valid Hebrew characters
- `calculate_gematria()` - Compute numerical values using Mispar Hechrachi
  **Requirements**:
- Must handle all Hebrew Unicode variants
- Surface-form calculation with preserved calc strings
- Deterministic results for same input

### `ids.py` - Identity & ID Generation

**Purpose**: Generate deterministic and sortable identifiers
**Key Functions**:

- `generate_content_hash()` - SHA-256 content hashing for identity
- `generate_uuid7()` - Time-sortable UUIDs for temporal ordering
- `create_deterministic_id()` - Consistent ID generation from inputs
  **Requirements**:
- Content-hash based identity (not database auto-increment)
- UUIDv7 for sortable surrogate keys
- No collisions across different inputs

## Design Principles

### Purity & Determinism

- All functions are pure (same input → same output)
- No side effects or external state dependencies
- Deterministic behavior for reproducible results

### Performance

- Optimized for high-throughput processing
- Minimal memory allocation
- Efficient Unicode handling

### Testing

- 100% test coverage required
- Property-based testing for edge cases
- Fuzz testing for Unicode edge cases

## Usage Patterns

### Hebrew Processing Pipeline

```python
# Normalize → Validate → Calculate
normalized = normalize_hebrew(raw_hebrew)
validate_hebrew_text(normalized)
value = calculate_gematria(normalized)
```

### Identity Generation

```python
# Content-based identity + sortable surrogate
content_id = generate_content_hash(text_data)
surrogate_id = generate_uuid7()
```

## Dependencies

- **Zero external dependencies** - pure Python standard library only
- **No database access** - operates on data objects only
- **No network calls** - synchronous processing only

## Maintenance Notes

- Changes here affect the entire pipeline - extensive testing required
- Hebrew Unicode handling must be validated against comprehensive test suite
- Performance optimizations must maintain correctness guarantees
