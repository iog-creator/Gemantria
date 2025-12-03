# AGENTS.md - Extractors Directory

## Directory Purpose

The `pmagent/extractors/` directory contains provenance management functions for extraction agents. These functions ensure that all extraction outputs carry proper metadata (model, seed, timestamp) for traceability and validation, implementing PLAN-072 M2+ Extraction Agents provenance requirements (TVs E06-E10).

## Key Components

### `provenance.py` - Provenance Management

**Purpose**: Provides functions to ensure and validate provenance metadata (model, seed, timestamp) on extraction outputs. Implements the provenance contract for extraction agents per PLAN-072.

**Key Functions**:

- `ensure_provenance(model: str, seed: int | str, analysis: str | None) -> Dict[str, Any]`
  - Ensures all provenance fields are present (model, seed, ts_iso)
  - Raises `ValueError` if model is missing/empty (E08)
  - Raises `ValueError` if seed is not an integer (E09)
  - Preserves analysis even if empty/whitespace (E10)
  - Returns dict with keys: `model` (str), `seed` (int), `ts_iso` (RFC3339 string)
  - Optionally includes `analysis` field if provided

- `guard_provenance(output: Dict[str, Any]) -> None`
  - Guard function for provenance validation (E08, E09)
  - Raises `ValueError` if provenance is invalid
  - Validates: model present and non-empty, seed present and integer
  - Used by guard systems to enforce provenance requirements

- `stamp_batch(items: Iterable[Dict[str, Any]], model: str, seed: int | str, base_dt: datetime | None = None) -> List[Dict[str, Any]]`
  - Deterministic batch stamping with monotonic timestamps
  - Accepts injected UTC base datetime (base_dt) for determinism
  - Adds +1s per record to ensure monotonic ts_iso within batch
  - Preserves input ordering 1:1
  - Seed affects only the 'seed' field; timestamps depend only on base_dt & index

- `rfc3339_now() -> str`
  - Returns current UTC time as RFC3339 string with 'Z' suffix
  - Format: `%Y-%m-%dT%H:%M:%SZ`

- `_coerce_seed_int(seed: Any) -> int`
  - Internal helper to coerce seed to integer
  - Raises `ValueError` if seed cannot be converted to int
  - Rejects boolean values explicitly

## API Contracts

### Provenance Dictionary Structure

All provenance-enabled outputs must contain:

```python
{
    "model": str,        # Non-empty string identifying the model used
    "seed": int,         # Integer seed value for reproducibility
    "ts_iso": str,       # RFC3339 timestamp in UTC (e.g., "2025-01-01T12:00:00Z")
    "analysis": str | None  # Optional analysis text (preserved even if empty/whitespace)
}
```

### Error Handling

- **E08 (Missing Model)**: `ValueError("model is required and must be non-empty string")`
- **E09 (Invalid Seed)**: `ValueError("seed must be int")` or `ValueError("seed must be int, not bool")`
- **Guard Errors**: `ValueError("provenance guard: missing 'model' field")` or similar

## Test Vectors (TVs E06-E10)

### E06 - Provenance Fields Present
Every extraction output must contain `model`, `seed`, and `ts_iso` fields.

### E07 - RFC3339 + Monotonic Timestamps
- `ts_iso` must be valid RFC3339 format (UTC, 'Z' suffix)
- Within a batch, timestamps must be monotonic (each item's timestamp > previous)

### E08 - Missing Model is Guardable Error
- `ensure_provenance("", ...)` raises `ValueError`
- `guard_provenance({"seed": 42, ...})` raises `ValueError`

### E09 - Non-Integer Seed is Guardable Error
- `ensure_provenance("model", "forty-two", ...)` raises `ValueError`
- `guard_provenance({"model": "model", "seed": "bad", ...})` raises `ValueError`

### E10 - Empty Analysis Preserves Provenance
- `ensure_provenance("model", 42, "")` includes `analysis: ""` in output
- `ensure_provenance("model", 42, "   ")` includes `analysis: "   "` in output
- `ensure_provenance("model", 42, None)` does not include `analysis` field

## Related ADRs

- **PLAN-072**: M2+ Extraction Agents provenance logic
- **Rule 006**: AGENTS.md Governance
- **Rule 027**: Docs Sync Gate

## Testing Strategy

Tests are located in `pmagent/tests/extractors/test_extraction_provenance_e06_e10.py`:

- `test_e06_provenance_fields_present()` - Validates all required fields present
- `test_e07_ts_iso_rfc3339()` - Validates RFC3339 format and monotonicity
- `test_e08_negative_missing_model_errors()` - Validates error handling for missing model
- `test_e09_negative_seed_type()` - Validates error handling for invalid seed
- `test_e10_edge_empty_analysis_keeps_provenance()` - Validates edge case handling

## Development Guidelines

- **Determinism**: Use `base_dt` parameter in `stamp_batch()` for reproducible timestamps
- **Validation**: Always call `guard_provenance()` in guard systems before accepting outputs
- **Error Messages**: Use clear, specific error messages that reference the test vector (E08, E09)
- **RFC3339 Compliance**: Always use UTC timezone and 'Z' suffix for timestamps
- **Seed Handling**: Coerce seeds to integers early; reject booleans explicitly

## Integration Points

- **Extraction Agents**: Call `ensure_provenance()` before returning extraction outputs
- **Guard Systems**: Call `guard_provenance()` to validate outputs before processing
- **Graph Assembly**: Uses provenance for batch correlation and rollup (see `pmagent/graph/assembler.py`)
- **Test Fixtures**: Provenance must be present in all extraction test fixtures

