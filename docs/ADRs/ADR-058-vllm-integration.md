# ADR-058: vLLM Provider Integration for Theology Model

## Status

Accepted

## Related ADRs

- ADR-007: LLM Integration and Confidence Metadata (foundation)
- ADR-010: Qwen3 Integration for Real Semantic Intelligence (embeddings/reranker)

## Context

The enrichment pipeline currently uses LM Studio (GGUF models) for theology model inference. To support Hugging Face Transformers models and improve performance, we need to add vLLM as an alternative inference provider while maintaining backward compatibility with LM Studio.

## Decision

Add vLLM as an alternative inference provider for the theology model with the following implementation:

1. **Provider Selection**: Environment variable `INFERENCE_PROVIDER=vllm|lmstudio` (default: `lmstudio`)
2. **Client Abstraction**: `InferenceClient` class providing OpenAI-compatible interface
3. **vLLM Server**: Script `scripts/vllm_serve.py` for launching vLLM server
4. **Model Support**: HF Transformers models via vLLM, GGUF models via LM Studio
5. **Backward Compatibility**: Existing LM Studio path remains functional

## Implementation Details

### Architecture Components

#### Inference Client (`src/services/inference_client.py`)

- **Provider Selection**: Reads `INFERENCE_PROVIDER` environment variable
- **Base URL Routing**: 
  - vLLM: `VLLM_BASE_URL` (default: `http://127.0.0.1:8001/v1`)
  - LM Studio: `OPENAI_BASE_URL` (default: `http://127.0.0.1:1234/v1`)
- **OpenAI Compatibility**: Implements OpenAI-compatible chat completions API
- **Batching Support**: Handles batched message requests

#### vLLM Server Launcher (`scripts/vllm_serve.py`)

- **Configuration**: Environment variables for model, port, GPU utilization
- **Model Support**: HF Transformers models (e.g., `sleepdeprived3/Christian-Bible-Expert-v2.0-12B`)
- **Performance Tuning**: Configurable GPU memory utilization, max model length

#### Enrichment Node Updates (`src/nodes/enrichment.py`)

- **Client Integration**: Uses `InferenceClient` instead of direct LM Studio calls
- **Provider Agnostic**: Works with both vLLM and LM Studio
- **Model Configuration**: `THEOLOGY_MODEL` environment variable (HF id for vLLM, model name for LM Studio)

### Configuration

```bash
# Provider selection
INFERENCE_PROVIDER=vllm  # or lmstudio

# vLLM configuration
VLLM_BASE_URL=http://127.0.0.1:8001/v1
THEOLOGY_MODEL=sleepdeprived3/Christian-Bible-Expert-v2.0-12B

# LM Studio configuration (legacy)
OPENAI_BASE_URL=http://127.0.0.1:1234/v1
THEOLOGY_MODEL=christian-bible-expert-v2.0-12b

# Embeddings and reranker (unchanged)
EMBEDDING_MODEL=BAAI/bge-m3
RERANKER_MODEL=Qwen/Qwen3-Reranker-8B
```

### Server Launch

```bash
# Start vLLM server
HF_MODEL=sleepdeprived3/Christian-Bible-Expert-v2.0-12B \
VLLM_PORT=8001 VLLM_GPU_UTIL=0.90 VLLM_MAXLEN=3072 \
python scripts/vllm_serve.py
```

## Consequences

### Positive

- **Performance**: vLLM provides better throughput for Transformers models
- **Model Flexibility**: Support for HF Transformers models alongside GGUF
- **Backward Compatibility**: LM Studio path remains available
- **Standard Interface**: OpenAI-compatible API for both providers
- **Future-Proofing**: Easy to add additional providers (e.g., OpenAI API, Anthropic)

### Negative

- **Additional Dependency**: Requires vLLM installation
- **Configuration Complexity**: Two provider paths to maintain
- **Testing Burden**: Need to test both provider paths

### Risks

- **Provider Availability**: vLLM server must be running when `INFERENCE_PROVIDER=vllm`
- **API Compatibility**: vLLM and LM Studio may have slight API differences
- **Model Loading**: vLLM server startup time and GPU memory requirements

## Alternatives Considered

### Option 1: Replace LM Studio with vLLM

- **Pro**: Single provider, simpler architecture
- **Con**: Breaks existing GGUF workflows, requires model conversion

### Option 2: Keep LM Studio Only

- **Pro**: No changes needed
- **Con**: Limited to GGUF models, slower performance

### Option 3: Hybrid Approach (Chosen)

- **Pro**: Best of both worlds, gradual migration path
- **Con**: Added complexity, dual provider support

## Testing Strategy

### Unit Tests

- Provider selection logic
- Base URL routing
- OpenAI-compatible API compliance

### Integration Tests

- Enrichment node with both providers
- Error handling when provider unavailable
- Model configuration validation

### End-to-End Tests

- Full pipeline with vLLM provider
- Full pipeline with LM Studio provider
- Provider switching without pipeline restart

## Future Considerations

### Additional Providers

- OpenAI API integration
- Anthropic Claude API
- Local model servers (TGI, etc.)

### Performance Optimization

- Model quantization (GPTQ/AWQ) for vLLM
- Batch size tuning per provider
- GPU memory optimization

### Unified Provider Interface

- Standardize on OpenAI-compatible API across all providers
- Provider health checks and auto-failover
- Provider performance metrics and selection

