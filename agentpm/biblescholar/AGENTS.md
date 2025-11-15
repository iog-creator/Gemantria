# AGENTS.md — agentpm/biblescholar

## Directory Purpose

Home for BibleScholar-specific integration logic inside AgentPM, including
read-only adapters to Gematria and other core modules.

This directory must NOT perform database writes or mutate the control-plane
directly; it should provide pure, testable adapters that callers can use.

## Status

- Phase-6J: BibleScholar Gematria adapter (read-only) — IN PROGRESS

## Related SSOT Docs

- docs/SSOT/BIBLESCHOLAR_INTAKE.md
- docs/SSOT/AGENTPM_GEMATRIA_MODULE_PLAN.md
- docs/projects/biblescholar/README.md
- docs/projects/biblescholar/ARCHITECTURE.md

## API Contract

### `gematria_adapter.compute_phrase_gematria()`

**Purpose**: Compute gematria for a Hebrew phrase or verse text in a BibleScholar-friendly format.

**Contract**:
- **Read-only**: No database writes, no control-plane mutations
- **Pure function**: Deterministic output for given inputs
- **System support**: `mispar_hechrachi` (default) and `mispar_gadol`
- **Edge cases**: Handles empty strings, None, mixed scripts, non-Hebrew text gracefully
- **OSIS refs**: Optional OSIS reference can be attached to results

**Inputs**:
- `text: str` - Hebrew text (may contain diacritics, punctuation, mixed scripts)
- `system: str` - Numerics system name (default: `mispar_hechrachi`)
- `osis_ref: str | None` - Optional OSIS reference (e.g., "Gen.4.2")

**Outputs**:
- `GematriaPhraseResult` dataclass with:
  - `text: str` - Original input text
  - `normalized: str` - Normalized Hebrew (diacritics/punctuation removed)
  - `letters: list[str]` - Extracted Hebrew letters
  - `system: str` - Numerics system used
  - `value: int` - Computed gematria value (0 if no Hebrew letters found)
  - `osis_ref: str | None` - OSIS reference if provided

**Error Handling**:
- Invalid system names raise `ValueError` with list of valid systems
- Empty/None text returns result with `value=0`, `normalized=""`, `letters=[]`
- Non-Hebrew text returns result with `value=0` (no error)

## Usage Examples

```python
from agentpm.biblescholar.gematria_adapter import compute_phrase_gematria

# Basic usage (default system: mispar_hechrachi)
result = compute_phrase_gematria("אדם")
assert result.value == 45
assert result.normalized == "אדם"
assert result.letters == ["א", "ד", "ם"]

# With OSIS reference
result = compute_phrase_gematria("הבל", osis_ref="Gen.4.2")
assert result.value == 37
assert result.osis_ref == "Gen.4.2"

# Different numerics system
result = compute_phrase_gematria("אדם", system="mispar_gadol")
# Final mem (ם) = 600 in Gadol vs 40 in Hechrachi
assert result.value == 605  # א=1, ד=4, ם=600

# Edge cases
result = compute_phrase_gematria("")  # Empty string
assert result.value == 0
assert result.normalized == ""
assert result.letters == []

result = compute_phrase_gematria("Hello 123")  # No Hebrew
assert result.value == 0
assert result.normalized == ""
assert result.letters == []

result = compute_phrase_gematria("א hello ב")  # Mixed scripts
assert result.value == 3  # א=1, ב=2
assert result.normalized == "אב"
assert result.letters == ["א", "ב"]
```

## Testing

All adapter functions must have comprehensive tests covering:
- Canonical examples (אדם=45, הבל=37)
- Both numerics systems
- Edge cases (empty, None, mixed scripts, non-Hebrew)
- OSIS reference handling
- Invalid system names

Tests live in `agentpm/biblescholar/tests/test_gematria_adapter.py`.

## Future Extensions

- Batch processing for multiple phrases
- Comparison utilities (difference between systems)
- Integration with BibleScholar verse lookup
- Caching layer (if needed, still read-only)

