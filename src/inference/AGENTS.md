# AGENTS.md - src/inference Directory

## Directory Purpose

The `src/inference/` directory contains inference routing and model management components for the Gematria analysis pipeline. Provides unified interface for different AI model types (theology, general, math, embeddings, reranking) with LM Studio integration.

## Key Components

### `router.py` - Model Router

**Purpose**: Intelligent routing of inference requests to appropriate AI models based on task requirements. Provides unified interface for all model types used in the pipeline.

**Key Functions**:
- `pick()` - Selects appropriate model for given task type
- Model configuration management for different inference categories
- Environment-based model selection with fallbacks

**Requirements**:
- **Model Categories**: theology, general, math, embed, reranker
- **Provider Support**: LM Studio with configurable endpoints
- **Environment Configuration**: All models configurable via environment variables
- **Fallback Handling**: Graceful degradation when models unavailable

## API Contracts

### Router Interface
```python
def pick(task: str) -> dict:
    """Select appropriate model configuration for task type."""

# Model Configuration Structure
{
    "model": str,        # Model identifier
    "base_url": str,     # LM Studio endpoint
    "provider": str      # Inference provider
}
```

## Testing Strategy

- **Unit Tests**: Model selection logic validation
- **Integration Tests**: End-to-end model routing with LM Studio
- **Configuration Tests**: Environment variable handling and fallbacks
- **Provider Tests**: Different inference provider compatibility

## Development Guidelines

- Always use the router interface for model selection
- Include comprehensive environment variable documentation
- Provide clear model capability descriptions
- Document fallback behavior and error handling
- Maintain backwards compatibility for model configurations

## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
| router.py | ADR-010 (Qwen Integration) |
| Model routing | ADR-015 (Inference Architecture) |
