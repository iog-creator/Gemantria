# AGENTS.md - src/rerank Directory

## Directory Purpose

The `src/rerank/` directory contains reranking components for optimizing semantic concept relationships using embedding-based similarity scoring. Recently consolidated to support organic AI discovery with unified edge strength calculations.

## Key Components

### `blender.py` - Edge Strength Blender

**Purpose**: Combines cosine similarity and reranker scores into unified edge strength values for semantic network classification.

**Key Functions**:
- `blend_scores()` - Applies configurable alpha blending: `edge_strength = α*cosine + (1-α)*rerank_score`
- `classify_edge()` - Classifies edges as strong/weak/candidate based on thresholds
- `validate_blend()` - Ensures blend calculations meet SSOT requirements (Rule 045)

**Requirements**:
- **Blend Formula**: Configurable EDGE_ALPHA parameter (default 0.5)
- **Threshold Validation**: EDGE_STRONG ≥ 0.90, EDGE_WEAK ≥ 0.75
- **SSOT Compliance**: Enforces edge strength blend contract across all exports

## API Contracts

### Blender Interface
```python
def blend_scores(cosine: float, rerank: float, alpha: float = 0.5) -> float:
    """Blend cosine and rerank scores into unified edge strength."""

def classify_edge(edge_strength: float) -> str:
    """Classify edge as 'strong', 'weak', or 'candidate'."""
```

## Testing Strategy

- **Unit Tests**: Blend formula validation and threshold classification
- **Integration Tests**: End-to-end reranking with live embeddings
- **Property Tests**: Statistical validation of blend distributions

## Development Guidelines

- Always use configurable alpha parameters for blend calculations
- Validate blend results against SSOT requirements
- Include threshold validation in all reranking operations
- Document alpha values used in production configurations

## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
| blender.py | ADR-026 (BGE-M3 Proxy) |
| Edge blending | ADR-015 (Semantic Reranking) |
