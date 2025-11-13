# AGENTS.md - Rerank Directory

## Directory Purpose

The `src/rerank/` directory contains reranking and edge strength blending utilities for semantic network construction. This module implements the SSOT (Single Source of Truth) for edge strength calculation by blending cosine similarity scores with reranker scores.

## Key Components

### `blender.py` - Edge Strength Blending (SSOT)

**Purpose**: Compute unified edge strength scores by blending cosine similarity with reranker scores. This is the **SSOT** for edge strength calculation per Rule 045 (Rerank Blend is SSOT).

**Key Functions**:

- `compute_rerank(source_text: str, target_text: str, cosine: float, meta: dict[str, Any] | None = None) -> float` - Compute reranker score
  - Hook for real reranker (e.g., LM Studio) with CI-safe fallback
  - Uses `MOCK_AI=1` to force deterministic fallback in CI
  - Currently uses fallback implementation (deterministic, monotonic in cosine)
- `_fallback_rerank(cosine: float, meta: dict[str, Any] | None = None) -> float` - Deterministic CI-safe rerank
  - Smoothstep-like shaping function: `3x² - 2x³` for x ∈ [0,1]
  - Monotonic in cosine, slightly reshaped to avoid matching cosine exactly
  - Guaranteed to work in CI without external dependencies
- `blend_strength(cosine: float, rerank: float) -> float` - Blend cosine and rerank scores
  - **SSOT Formula**: `edge_strength = (1 - BLEND_W) * cosine + BLEND_W * rerank`
  - Default `BLEND_W = 0.5` (configurable via `EDGE_RERANK_BLEND_W` env var)
  - Returns unified edge strength score in [0.0, 1.0] range
- `classify_strength(strength: float) -> str` - Classify edge strength
  - **strong**: `strength >= 0.90`
  - **weak**: `strength >= 0.75`
  - **other**: `strength < 0.75`

**Requirements**:
- **SSOT Compliance**: Edge strength calculation must use this module (Rule 045)
- **CI Safety**: Fallback implementation works without external dependencies
- **Deterministic**: Same inputs produce same outputs (critical for reproducibility)
- **Configurable**: Blend weight configurable via environment variable

## API Contracts

### Rerank Computation

```python
def compute_rerank(
    source_text: str,
    target_text: str,
    cosine: float,
    meta: dict[str, Any] | None = None
) -> float:
    """Compute reranker score with CI-safe fallback.
    
    Args:
        source_text: Source concept text
        target_text: Target concept text
        cosine: Pre-computed cosine similarity score
        meta: Optional metadata dictionary
        
    Returns:
        Reranker score in [0.0, 1.0] range
        
    Note:
        Currently uses fallback implementation. Future: integrate real reranker
        with MOCK_AI=1 guard for CI safety.
    """
```

### Edge Strength Blending

```python
def blend_strength(cosine: float, rerank: float) -> float:
    """Blend cosine similarity and reranker scores into unified edge strength.
    
    Args:
        cosine: Cosine similarity score [0.0, 1.0]
        rerank: Reranker score [0.0, 1.0]
        
    Returns:
        Blended edge strength [0.0, 1.0]
        
    Formula:
        edge_strength = (1 - BLEND_W) * cosine + BLEND_W * rerank
        where BLEND_W defaults to 0.5 (configurable via EDGE_RERANK_BLEND_W)
    """

def classify_strength(strength: float) -> str:
    """Classify edge strength into categories.
    
    Args:
        strength: Edge strength score [0.0, 1.0]
        
    Returns:
        Classification: "strong" (≥0.90), "weak" (≥0.75), or "other" (<0.75)
    """
```

## Edge Strength Calculation (SSOT)

### Formula

The edge strength calculation follows this formula (Rule 045):

```
edge_strength = α * cosine + (1 - α) * rerank_score
```

Where:
- `α = 1 - BLEND_W` (default: 0.5, so α = 0.5)
- `cosine`: Cosine similarity from embeddings [0.0, 1.0]
- `rerank_score`: Reranker output [0.0, 1.0]

### Classification Thresholds

- **Strong edges**: `edge_strength >= 0.90`
- **Weak edges**: `edge_strength >= 0.75`
- **Other edges**: `edge_strength < 0.75`

### Configuration

Blend weight is configurable via environment variable:

```bash
EDGE_RERANK_BLEND_W=0.5  # Default: equal weight (0.5 cosine + 0.5 rerank)
```

## Usage Patterns

### Basic Edge Strength Calculation

```python
from src.rerank.blender import compute_rerank, blend_strength, classify_strength

# Compute reranker score
cosine = 0.85
rerank = compute_rerank("source text", "target text", cosine)

# Blend into unified edge strength
strength = blend_strength(cosine, rerank)
# Returns: 0.5 * 0.85 + 0.5 * rerank

# Classify edge
category = classify_strength(strength)
# Returns: "weak" if 0.75 <= strength < 0.90
```

### Integration with Network Aggregation

```python
# In network_aggregator.py
from src.rerank.blender import compute_rerank, blend_strength, classify_strength

for source, target, cosine in pairs:
    rerank = compute_rerank(source.text, target.text, cosine)
    strength = blend_strength(cosine, rerank)
    category = classify_strength(strength)
    
    edge = {
        "source": source.id,
        "target": target.id,
        "cosine": cosine,
        "rerank": rerank,
        "edge_strength": strength,
        "class": category
    }
```

## Testing Strategy

### Unit Tests

- **Blend Formula**: Verify correct calculation: `(1-w)*cos + w*rerank`
- **Classification**: Test threshold boundaries (0.75, 0.90)
- **Fallback Rerank**: Verify deterministic, monotonic behavior
- **Edge Cases**: Test with boundary values (0.0, 1.0, negative, >1.0)

### Integration Tests

- **SSOT Compliance**: Verify all edge strength calculations use this module
- **CI Safety**: Test fallback behavior with `MOCK_AI=1`
- **Configuration**: Test blend weight configuration via environment variable

### Coverage Requirements

- ≥98% code coverage
- Test all classification thresholds
- Test blend weight variations
- Verify SSOT contract compliance

## Development Guidelines

### SSOT Enforcement

- **Single Source**: All edge strength calculations MUST use `blend_strength()`
- **No Duplication**: Never reimplement blend formula elsewhere
- **Rule 045**: This module is the SSOT for rerank blend calculation

### Adding Reranker Integration

When integrating a real reranker:

1. **CI Safety**: Always respect `MOCK_AI=1` for CI environments
2. **Timeout Handling**: Add timeouts for external reranker calls
3. **Error Handling**: Fallback to `_fallback_rerank()` on failures
4. **Determinism**: Ensure deterministic output for same inputs

### Code Standards

- **Type Hints**: Complete type annotations
- **Documentation**: Clear docstrings with formula explanations
- **Constants**: Use environment variables for configuration
- **Determinism**: Critical for reproducible pipeline runs

## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
| `blender.py` | ADR-026 (Reranker Bi-Encoder Proxy), ADR-045 (Rerank Blend SSOT) |

## Related Rules

- **Rule 045**: Rerank Blend is SSOT (AlwaysApply)
- **Rule 046**: Hermetic CI Fallbacks (MOCK_AI=1 support)

## Related Documentation

- **Parent**: [AGENTS.md](../AGENTS.md) - Repository overview
- **Network Aggregation**: [../nodes/AGENTS.md](../nodes/AGENTS.md) - Edge creation
- **Services**: [../services/AGENTS.md](../services/AGENTS.md) - Reranker service integration
- **Rules**: [.cursor/rules/045-rerank-blend-SSOT.mdc](../../.cursor/rules/045-rerank-blend-SSOT.mdc)
