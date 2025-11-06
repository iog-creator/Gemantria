# Noun Adapter - Single Source of Truth

## Overview

The `src/ssot/noun_adapter.py` module provides the canonical noun shape used throughout the Gemantria pipeline. All agents must normalize noun objects through this adapter to ensure consistency across the system.

## Canonical Noun Shape

```python
{
  "noun_id": str,           # UUID or unique identifier
  "surface": str,           # Hebrew surface form (canonical)
  "hebrew_text": str,       # Alias for surface (backward compatibility)
  "letters": list[str],     # Individual Hebrew letters ["א", "ב", "ר", ...]
  "gematria_value": int,    # Calculated numerical value
  "class": str,             # person|place|thing|other
  "semantic_features": dict,# Optional computed features
  "analysis": dict,         # Theological analysis (analysis.theology block)
  "sources": list[dict],    # Source references [{"ref": "...", "offset": 123}]
}
```

## Adapter Functions

### `adapt_ai_noun(n: Dict[str, Any]) -> Dict[str, Any]`

Normalizes various noun input formats to the canonical shape.

**Input Variants Supported:**
- `{"hebrew": "...", "gematria": 123, "classification": "..."}`
- `{"hebrew_text": "...", "gematria_value": 123, "class": "..."}`
- `{"surface": "...", "letters": [...], "gematria": 123}`

**Features:**
- Handles `SimpleNamespace` objects from LLM responses
- Normalizes field names (hebrew→surface, gematria→gematria_value, etc.)
- Provides fallback values for missing fields
- Validates and normalizes classification values

### `_coerce_text(x: Any) -> str`

Safely extracts text from various input types, particularly LLM `SimpleNamespace` responses.

## Usage

```python
from src.ssot.noun_adapter import adapt_ai_noun

# Normalize AI-discovered noun
raw_noun = {"hebrew": "אברהם", "gematria": 248, "classification": "person"}
canonical = adapt_ai_noun(raw_noun)
# Result: {"surface": "אברהם", "gematria_value": 248, "class": "person", ...}
```

## Integration Points

- **AI Noun Discovery**: Normalizes LLM outputs before storage
- **Enrichment Agent**: Ensures consistent input format
- **Graph Builder**: Standardizes node data
- **Database Storage**: Prepares data for upsert operations

## Validation

The adapter enforces:
- String types for text fields
- Integer types for gematria values
- Valid classification values (person/place/thing/other)
- Proper list/dict structures for complex fields

## Backward Compatibility

The adapter maintains aliases like `hebrew_text` to support existing code while encouraging migration to the canonical `surface` field.
