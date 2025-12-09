# Ollama Auto-Discovery & Model Installation

**Phase-7E**: Automated tool discovery for Ollama model management.

## Overview

The Ollama auto-discovery system automatically:
1. **Detects** if Ollama server is running
2. **Lists** installed models via `/api/tags`
3. **Identifies** required models from environment configuration
4. **Pulls** missing models automatically via `/api/pull`
5. **Verifies** models are ready for use

## Components

### 1. Discovery Script (`scripts/ollama_discovery.py`)

Standalone script for model discovery and installation:

```bash
python3 scripts/ollama_discovery.py
```

**Behavior:**
- Checks `INFERENCE_PROVIDER` environment variable
- If `provider=ollama`, discovers and installs required models
- If `provider=lmstudio` or other, exits silently (no-op)

**Required Models:**
- `LOCAL_AGENT_MODEL` (e.g., `granite4:tiny-h`) ✅ Available in Ollama
- `EMBEDDING_MODEL` (e.g., `granite-embedding-english-r2` → `granite-embedding:278m`) ✅ Available in Ollama
- `THEOLOGY_MODEL` (optional)
- `MATH_MODEL` (optional)
- `RERANKER_MODEL` (e.g., `granite-embedding-reranker-english-r2`) ⚠️ **Not yet available in Ollama** - Use LM Studio or Qwen reranker

### 2. Health Check Integration (`scripts/guards/guard_lm_health.py`)

The LM health check (`pmagent health lm`) now automatically:
- Detects Ollama provider
- Runs discovery script if needed
- Verifies models are installed
- Tests chat endpoint for readiness

**Usage:**
```bash
pmagent health lm
# or
python3 scripts/guards/guard_lm_health.py
```

### 3. Adapter Helpers (`pmagent/adapters/ollama.py`)

New helper functions for model management:

```python
from pmagent.adapters.ollama import list_installed_models, check_model_installed

# List all installed models
models = list_installed_models()

# Check if specific model is installed
is_installed = check_model_installed("granite4:tiny-h")
```

## API Endpoints Used

Based on [Ollama API documentation](https://docs.ollama.com/api):

1. **GET `/api/tags`** - List installed models
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. **POST `/api/pull`** - Pull/download a model
   ```bash
   curl http://localhost:11434/api/pull -d '{"model": "granite4:tiny-h"}'
   ```

## Integration Points

### Automatic Discovery

The discovery script is automatically invoked by:
- `pmagent health lm` - Health check command
- `make bringup.001` - System bring-up verification (if configured)
- Any script that calls `check_lm_health()`

### Manual Discovery

Run discovery manually:
```bash
# With environment variables
INFERENCE_PROVIDER=ollama \
OLLAMA_BASE_URL=http://127.0.0.1:11434 \
LOCAL_AGENT_MODEL=granite4:tiny-h \
python3 scripts/ollama_discovery.py
```

## Example Workflow

1. **Set environment:**
   ```bash
   export INFERENCE_PROVIDER=ollama
   export OLLAMA_BASE_URL=http://127.0.0.1:11434
   export LOCAL_AGENT_MODEL=granite4:tiny-h
   export EMBEDDING_MODEL=text-embedding-bge-m3
   ```

2. **Run discovery:**
   ```bash
   python3 scripts/ollama_discovery.py
   ```

3. **Verify health:**
   ```bash
   pmagent health lm
   ```

4. **Use models:**
   ```python
   from pmagent.adapters.lm_studio import chat, embed
   
   # Chat (automatically routes to Ollama)
   response = chat("Hello", model_slot="local_agent")
   
   # Embeddings (automatically routes to Ollama)
   vectors = embed(["text1", "text2"])
   ```

## Model Availability Status

### ✅ Available in Ollama
- **Chat Models**: `granite4:tiny-h`, `granite4:micro`, `granite4:small`
- **Embedding Models**: `granite-embedding:278m` (multilingual), `granite-embedding:30m` (English-only)
- **Name Normalization**: LM Studio names automatically map to Ollama names
  - `granite-embedding-english-r2` → `granite-embedding:278m`
  - `ibm-granite/granite-embedding-english-r2` → `granite-embedding:278m`

### ⚠️ Not Available in Ollama (Use LM Studio)
- **Reranker Models**: `granite-embedding-reranker-english-r2` - Not in Ollama registry
  - **Workaround**: Use Qwen reranker (`qwen/qwen3-8b-reranker`) or keep reranker on LM Studio
  - **Future**: May be added to Ollama registry later

### 🔄 Hybrid Setup Recommended
For Phase-7E, consider:
- **Ollama**: Chat models (`granite4:tiny-h`) + Embeddings (`granite-embedding:278m`)
- **LM Studio**: Reranker models (until Granite reranker available in Ollama)

## Error Handling

The discovery system handles:
- **Ollama server not running**: Returns error, suggests `ollama serve`
- **Model pull failures**: Reports which models failed to install
- **Reranker/Embedding models not in registry**: Gracefully skips with warning (doesn't fail)
- **Network timeouts**: Uses 300s timeout for large model downloads
- **Missing configuration**: Skips discovery if `INFERENCE_PROVIDER != ollama`

## Phase-7E Integration

This auto-discovery system completes Phase-7E by:
- ✅ Eliminating manual `ollama pull` commands
- ✅ Integrating with existing health checks
- ✅ Providing programmatic model management
- ✅ Supporting both LM Studio and Ollama providers seamlessly

## Related Documentation

- [Ollama API Reference](https://docs.ollama.com/api)
- [LM Studio Setup](./LM_STUDIO_SETUP.md)
- [Ollama Alternative](./OLLAMA_ALTERNATIVE.md)
- [Phase-7E Implementation](../SSOT/PHASE_7E_PLAN.md)

