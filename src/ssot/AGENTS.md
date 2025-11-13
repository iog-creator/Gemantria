# AGENTS.md - SSOT Directory

## Directory Purpose

The `src/ssot/` directory contains Single Source of Truth (SSOT) adapters that normalize and standardize data formats across the pipeline. These adapters ensure consistent data representation and prevent format drift between pipeline stages.

## Key Components

### `noun_adapter.py` - AI Noun Format Adapter

**Purpose**: Adapt AI-discovered nouns from external discovery format to standardized internal pipeline format. Ensures consistent noun representation across all pipeline stages.

**Key Functions**:

- `adapt_ai_noun(ai_noun: Dict[str, Any]) -> Dict[str, Any]` - Convert AI noun to internal format
  - Generates deterministic `noun_id` from Hebrew text if not present (UUIDv5)
  - Normalizes field names (hebrew → surface, gematria → gematria_value)
  - Provides backward compatibility aliases (gematria, value, class, classification)
  - Sets default values for missing fields
  - Marks nouns as `ai_discovered: True`

**Requirements**:
- **Deterministic IDs**: Uses UUIDv5 with DNS namespace for stable noun_id generation
- **Field Normalization**: Maps external field names to internal standard names
- **Backward Compatibility**: Provides aliases for legacy field names
- **Default Values**: Sets safe defaults for missing optional fields

## API Contracts

### Noun Adaptation

```python
def adapt_ai_noun(ai_noun: Dict[str, Any]) -> Dict[str, Any]:
    """Adapt an AI-discovered noun to internal pipeline format.
    
    Args:
        ai_noun: Dictionary containing AI-discovered noun data with fields:
            - noun_id (optional): Existing noun identifier
            - hebrew: Hebrew text (required for ID generation)
            - letters: List of Hebrew letters
            - gematria: Gematria value
            - classification: Noun classification (person/place/thing)
            - meaning: English meaning/translation
            - primary_verse: Primary verse reference
            - freq: Frequency count
            - book: Book name
            - ai_discovered: Boolean flag (defaults to True)
            
    Returns:
        Adapted dictionary with standardized field names:
            - noun_id: Deterministic UUID (generated if missing)
            - surface: Hebrew surface form
            - hebrew_text: Hebrew text (alias)
            - letters: List of Hebrew letters
            - gematria_value: Gematria value
            - gematria: Gematria value (alias for compatibility)
            - value: Gematria value (alias for compatibility)
            - class: Classification
            - classification: Classification (alias)
            - meaning: English meaning
            - primary_verse: Primary verse reference
            - freq: Frequency count
            - book: Book name
            - ai_discovered: True (always set)
            - sources: Empty list (populated during enrichment)
    """
```

## Field Mapping

### Input → Output Field Mapping

| Input Field | Output Field(s) | Notes |
|------------|----------------|-------|
| `noun_id` | `noun_id` | Generated if missing (UUIDv5 from Hebrew) |
| `hebrew` | `surface`, `hebrew_text` | Primary Hebrew text |
| `letters` | `letters` | List of Hebrew letters |
| `gematria` | `gematria_value`, `gematria`, `value` | Multiple aliases for compatibility |
| `classification` | `class`, `classification` | Both names supported |
| `meaning` | `meaning` | English translation |
| `primary_verse` | `primary_verse` | Verse reference |
| `freq` | `freq` | Frequency count |
| `book` | `book` | Book name |
| `ai_discovered` | `ai_discovered` | Always set to True |

### Default Values

Fields with defaults when missing:
- `noun_id`: Generated from Hebrew text (UUIDv5)
- `letters`: `[]` (empty list)
- `gematria_value`: `0`
- `class`: `"unknown"`
- `meaning`: `""` (empty string)
- `primary_verse`: `""` (empty string)
- `freq`: `0`
- `book`: `""` (empty string)
- `ai_discovered`: `True`
- `sources`: `[]` (empty list, populated during enrichment)

## Usage Patterns

### Basic Noun Adaptation

```python
from src.ssot.noun_adapter import adapt_ai_noun

# AI-discovered noun from external source
ai_noun = {
    "hebrew": "אדם",
    "gematria": 45,
    "classification": "person",
    "meaning": "man, human",
    "book": "Genesis"
}

# Adapt to internal format
adapted = adapt_ai_noun(ai_noun)
# Returns:
# {
#     "noun_id": "uuid-v5-generated-id",
#     "surface": "אדם",
#     "hebrew_text": "אדם",
#     "letters": [],
#     "gematria_value": 45,
#     "gematria": 45,  # alias
#     "value": 45,  # alias
#     "class": "person",
#     "classification": "person",  # alias
#     "meaning": "man, human",
#     "primary_verse": "",
#     "freq": 0,
#     "book": "Genesis",
#     "ai_discovered": True,
#     "sources": []
# }
```

### Integration with AI Discovery

```python
# In AI noun discovery node
from src.ssot.noun_adapter import adapt_ai_noun

def discover_nouns(book: str) -> List[Dict]:
    # ... AI discovery logic ...
    ai_nouns = llm_discover_nouns(book)
    
    # Adapt all discovered nouns to internal format
    adapted_nouns = [adapt_ai_noun(noun) for noun in ai_nouns]
    
    return adapted_nouns
```

## Testing Strategy

### Unit Tests

- **Field Mapping**: Verify all input fields map correctly to output fields
- **ID Generation**: Test deterministic UUIDv5 generation from Hebrew text
- **Default Values**: Verify defaults applied for missing fields
- **Aliases**: Test backward compatibility aliases work correctly
- **Edge Cases**: Empty strings, None values, missing required fields

### Integration Tests

- **Pipeline Integration**: Test adaptation works in full pipeline context
- **Format Consistency**: Verify adapted nouns match expected internal format
- **ID Stability**: Verify same Hebrew text generates same noun_id

### Coverage Requirements

- ≥98% code coverage
- Test all field mappings
- Test all default value scenarios
- Verify UUIDv5 generation correctness

## Development Guidelines

### Adding New Adapters

1. **SSOT Principle**: Each adapter should be the single source for format conversion
2. **Determinism**: ID generation and field mapping must be deterministic
3. **Backward Compatibility**: Provide aliases for legacy field names
4. **Documentation**: Clear field mapping tables and usage examples

### Code Standards

- **Type Hints**: Complete type annotations with Dict[str, Any] for flexible input
- **Default Values**: Safe defaults for all optional fields
- **ID Generation**: Use UUIDv5 for deterministic, stable identifiers
- **Error Handling**: Graceful handling of missing or malformed input

## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
| `noun_adapter.py` | ADR-032 (Organic AI Discovery), ADR-037 (Data Persistence Completeness) |

## Related Documentation

- **Parent**: [AGENTS.md](../AGENTS.md) - Repository overview
- **AI Discovery**: [../nodes/AGENTS.md](../nodes/AGENTS.md) - Noun discovery node
- **Core Utilities**: [../core/AGENTS.md](../core/AGENTS.md) - ID generation utilities
- **Rules**: [.cursor/rules/002-gematria-validation.mdc](../../.cursor/rules/002-gematria-validation.mdc)
