# AGENTS.md - Utils Directory

## Directory Purpose

The `src/utils/` directory contains utility functions for text processing, JSON parsing, and OSIS (Open Scripture Information Standard) reference handling. These are pure utility functions used across the pipeline for data normalization and parsing.

## Key Components

### `json_sanitize.py` - LLM JSON Output Sanitization

**Purpose**: Clean and parse JSON output from LLM responses that may contain markdown code fences, control characters, or trailing text.

**Key Functions**:

- `coerce_json_one_line(text: str) -> str` - Clean LLM output to valid single-line JSON
  - Strips markdown code fences (```json ... ```)
  - Removes control characters (except tab/newline)
  - Trims to last closing brace to avoid trailing chatter
- `parse_llm_json(text: str) -> dict` - Parse LLM JSON with repair attempts
  - Attempts full JSON parse after coercion
  - Falls back to extracting top-level object if needed
  - Raises `json.JSONDecodeError` if parsing fails

**Requirements**:
- Handles malformed LLM output gracefully
- Preserves valid JSON structure
- Removes only problematic characters (control chars, code fences)
- Deterministic output for same input

### `osis.py` - OSIS Reference Utilities

**Purpose**: Extract and normalize biblical verse references to OSIS (Open Scripture Information Standard) format for consistent cross-referencing.

**Key Functions**:

- `extract_verse_references(text: str) -> List[Dict[str, str]]` - Extract verse references from text
  - Finds patterns like "Psalm 30:5" or "Genesis 1"
  - Normalizes book names to OSIS abbreviations
  - Returns list of dictionaries with 'label' and 'osis' keys
- `normalize_book_to_osis(book_name: str) -> str | None` - Normalize book name to OSIS abbreviation
  - Maps human-readable book names to OSIS standard abbreviations
  - Handles common variations (e.g., "psalm" → "Ps", "1 samuel" → "1Sam")
  - Returns None for unrecognized book names

**Requirements**:
- Supports all 66 canonical books (Old and New Testament)
- Handles common book name variations
- Case-insensitive matching
- Returns standardized OSIS format (e.g., "Gen.1.1", "Ps.30.5")

## API Contracts

### JSON Sanitization

```python
def coerce_json_one_line(text: str) -> str:
    """Clean LLM output to valid single-line JSON.
    
    Args:
        text: Raw LLM output potentially containing code fences, control chars
        
    Returns:
        Cleaned single-line JSON string
    """

def parse_llm_json(text: str) -> dict:
    """Parse LLM JSON with repair attempts.
    
    Args:
        text: Raw LLM output to parse
        
    Returns:
        Parsed JSON dictionary
        
    Raises:
        json.JSONDecodeError: If JSON cannot be parsed after repair attempts
    """
```

### OSIS Reference Extraction

```python
def extract_verse_references(text: str) -> List[Dict[str, str]]:
    """Extract verse references from text and normalize to OSIS format.
    
    Args:
        text: Text containing potential verse references
        
    Returns:
        List of dictionaries with 'label' (human-readable) and 'osis' (standardized) keys
        Example: [{"label": "Psalm 30:5", "osis": "Ps.30.5"}]
    """

def normalize_book_to_osis(book_name: str) -> str | None:
    """Normalize a book name to OSIS abbreviation.
    
    Args:
        book_name: Human-readable book name (e.g., "Genesis", "1 Samuel")
        
    Returns:
        OSIS book abbreviation (e.g., "Gen", "1Sam") or None if not recognized
    """
```

## Usage Patterns

### JSON Sanitization

```python
from src.utils.json_sanitize import parse_llm_json

# Handle LLM output that may contain code fences
llm_output = """```json
{"noun": "אדם", "gematria": 45}
```"""

parsed = parse_llm_json(llm_output)
# Returns: {"noun": "אדם", "gematria": 45}
```

### OSIS Reference Extraction

```python
from src.utils.osis import extract_verse_references, normalize_book_to_osis

# Extract references from text
text = "As mentioned in Genesis 1:1 and Psalm 30:5, the creation..."
refs = extract_verse_references(text)
# Returns: [
#   {"label": "Genesis 1:1", "osis": "Gen.1.1"},
#   {"label": "Psalm 30:5", "osis": "Ps.30.5"}
# ]

# Normalize book names
osis = normalize_book_to_osis("1 samuel")
# Returns: "1Sam"
```

## Testing Strategy

### Unit Tests

- **JSON Sanitization**: Test with various LLM output formats (code fences, control chars, trailing text)
- **OSIS Extraction**: Test with various verse reference patterns and book name variations
- **Edge Cases**: Empty strings, malformed JSON, unrecognized book names

### Coverage Requirements

- ≥98% code coverage for all utility functions
- Property-based testing for OSIS normalization (all 66 books)
- Fuzz testing for JSON sanitization with random control characters

## Development Guidelines

### Adding New Utilities

1. **Pure Functions**: All utilities should be pure (no side effects, deterministic)
2. **Type Hints**: All functions must have complete type annotations
3. **Error Handling**: Clear error messages for invalid inputs
4. **Documentation**: Comprehensive docstrings with examples

### Code Standards

- **No External Dependencies**: Use only Python standard library
- **Deterministic**: Same input always produces same output
- **Performance**: Optimized for high-frequency use in pipeline
- **Unicode Handling**: Proper handling of Hebrew text and special characters

## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
| `json_sanitize.py` | ADR-010 (LM Studio Integration), ADR-015 (JSON-LD Exports) |
| `osis.py` | ADR-001 (Two-DB Safety - Bible DB references) |

## Related Documentation

- **Parent**: [AGENTS.md](../AGENTS.md) - Repository overview
- **Core Utilities**: [../core/AGENTS.md](../core/AGENTS.md) - Core processing utilities
- **Rules**: [.cursor/rules/002-gematria-validation.mdc](../../.cursor/rules/002-gematria-validation.mdc)
