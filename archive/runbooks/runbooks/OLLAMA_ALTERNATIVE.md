# Ollama Alternative to LM Studio

## Overview

**Ollama** is a programmatic alternative to LM Studio that offers better automation and LangChain/LangGraph integration. This document compares Ollama with LM Studio and provides migration guidance.

## Why Consider Ollama?

### Key Advantages

1. **Fully Programmatic**: No interactive prompts required
   - `ollama pull granite-4.0-h-tiny` - downloads models non-interactively
   - `ollama list` - lists installed models programmatically
   - All operations are scriptable

2. **LangChain/LangGraph Native Integration**
   - `ChatOllama` class provides direct integration
   - Works seamlessly with existing LangGraph pipelines
   - No custom adapter needed (though we can create one for consistency)

3. **Simpler Model Management**
   - Models are identified by simple names (e.g., `granite-4.0-h-tiny`)
   - No complex model IDs or GGUF variants to track
   - Automatic model discovery via API

4. **OpenAI-Compatible API**
   - Same API structure as LM Studio
   - Drop-in replacement for existing HTTP clients
   - Default port: `11434` (vs LM Studio's `9994`)

5. **Better Automation**
   - Health checks: `curl http://localhost:11434/api/tags`
   - Model status: `ollama list`
   - No GUI dependencies

## Comparison: LM Studio vs Ollama

| Feature | LM Studio | Ollama |
|---------|-----------|--------|
| **Model Download** | Interactive (`lms get` requires selection) | Programmatic (`ollama pull <model>`) |
| **Model Listing** | `lms ls` (works) | `ollama list` (works) |
| **API Endpoint** | `http://localhost:9994/v1` | `http://localhost:11434` |
| **LangChain Integration** | Custom adapter needed | Native `ChatOllama` |
| **Model Names** | Complex IDs (`ibm-granite/granite-4.0-h-tiny-GGUF`) | Simple names (`granite-4.0-h-tiny`) |
| **Automation** | Limited (interactive prompts) | Full (all CLI commands scriptable) |
| **Health Check** | Custom endpoint needed | Built-in `/api/tags` |
| **Model Management** | GUI-focused | CLI-first |

## Installation

### 1. Install Ollama

```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Or download from https://ollama.com/download
```

### 2. Start Ollama Service

```bash
# Start Ollama (runs as background service)
ollama serve

# Or use systemd (Linux)
sudo systemctl start ollama
sudo systemctl enable ollama
```

### 3. Download Granite 4.0 Models (Non-Interactive)

**Phase-7D: Granite 4.0 models are now available in Ollama!**

```bash
# Granite 4.0 chat models
ollama pull ibm/granite4.0-preview:tiny    # Recommended for local agent
ollama pull ibm/granite4.0-preview:micro   # Smaller alternative
ollama pull ibm/granite4.0-preview:small    # Larger alternative

# Granite embedding models
ollama pull ibm/granite-embedding:30m       # English-only embeddings
ollama pull ibm/granite-embedding:278m     # Multilingual embeddings + reranker

# Download other models (if needed)
ollama pull qwen2.5:14b
ollama pull qwen2.5:8b

# List installed models
ollama list
```

**Note**: The adapter automatically maps canonical model names (e.g., `granite-4.0-h-tiny`) to Ollama's naming convention (`ibm/granite4.0-preview:tiny`).

### 4. Verify Installation

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# List models
ollama list

# Test a model
ollama run granite-4.0-h-tiny "Hello, world!"
```

## LangChain Integration

### Using ChatOllama (Native)

```python
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama

# Chat model (recommended)
llm = ChatOllama(
    model="granite-4.0-h-tiny",
    base_url="http://localhost:11434",
    temperature=0.0,
)

# Use in LangGraph
from langgraph.graph import StateGraph

# Works directly with LangGraph nodes
response = llm.invoke("What is gematria?")
```

### Using OpenAI-Compatible API

```python
from langchain_openai import ChatOpenAI

# Ollama exposes OpenAI-compatible API
llm = ChatOpenAI(
    model="granite-4.0-h-tiny",
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # Ollama doesn't require real key
    temperature=0.0,
)
```

## Migration from LM Studio

### 1. Update Environment Variables

```bash
# Change provider
INFERENCE_PROVIDER=ollama

# Update base URL
OPENAI_BASE_URL=http://localhost:11434/v1

# Model names become simpler
LOCAL_AGENT_MODEL=granite-4.0-h-tiny
EMBEDDING_MODEL=granite-embedding-english-r2
RERANKER_MODEL=granite-reranker-english-r2
```

### 2. Update Adapter (if using custom adapter)

See `pmagent/adapters/ollama.py` for a drop-in replacement adapter.

### 3. Update Health Checks

```python
# Old (LM Studio)
def check_lm_studio_health():
    response = requests.get("http://localhost:9994/v1/models")
    return response.status_code == 200

# New (Ollama)
def check_ollama_health():
    response = requests.get("http://localhost:11434/api/tags")
    return response.status_code == 200
```

## Model Availability

### Granite Models

Ollama supports Granite models, but model names may differ:
- `granite-4.0-h-tiny` - Chat model
- `granite-embedding-english-r2` - Embedding model (if available)
- Custom Modelfile can be created for models not in Ollama's library

### Creating Custom Modelfiles

For models not in Ollama's library, create a `Modelfile`:

```dockerfile
FROM granite-4.0-h-tiny
PARAMETER temperature 0.0
PARAMETER top_p 0.9
SYSTEM """You are a helpful assistant."""
```

Then create:
```bash
ollama create christian-bible-expert -f Modelfile
```

## Advantages for Gemantria

1. **Automation-Friendly**: All model operations are scriptable
2. **CI/CD Ready**: No interactive prompts break automation
3. **LangGraph Native**: Direct integration without custom adapters
4. **Simpler Configuration**: Model names are human-readable
5. **Better Health Checks**: Built-in API endpoints
6. **Model Catalog**: Easier to track and manage models

## Disadvantages

1. **Model Library**: May not have all models LM Studio has
2. **Custom Models**: Requires Modelfile creation for some models
3. **Migration Effort**: Need to update adapters and configs
4. **Learning Curve**: Team needs to learn Ollama commands

## Recommendation

**For Phase-7D+**: Consider migrating to Ollama for:
- Better automation (no interactive prompts)
- Native LangChain/LangGraph integration
- Simpler model management
- CI/CD compatibility

**Migration Path**:
1. Install Ollama alongside LM Studio (dual support)
2. Create Ollama adapter (`pmagent/adapters/ollama.py`)
3. Add `INFERENCE_PROVIDER=ollama` option
4. Test with existing LangGraph pipeline
5. Gradually migrate models to Ollama
6. Deprecate LM Studio support in Phase-8

## References

- [Ollama Documentation](https://ollama.com/docs)
- [LangChain Ollama Integration](https://python.langchain.com/docs/integrations/llms/ollama)
- [Ollama API Reference](https://github.com/ollama/ollama/blob/main/docs/api.md)

