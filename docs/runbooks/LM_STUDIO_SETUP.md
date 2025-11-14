# LM Studio Setup Runbook

## Purpose

This runbook provides step-by-step instructions for setting up LM Studio as a local Language Model backend for the Gemantria pipeline. LM Studio enables low-latency, cost-effective, offline-capable LLM inference with control-plane observability.

## Prerequisites

- **LM Studio**: Installed and accessible (GUI or CLI)
- **Python Environment**: Virtual environment activated (`.venv`)
- **Models**: Required models downloaded and available in LM Studio
- **Hardware**: Sufficient RAM/VRAM for model loading (see Hardware Requirements below)

## Quick Start

### 1. Install LM Studio

**Option A: GUI Installation (Recommended)**
- Download from [lmstudio.ai](https://lmstudio.ai)
- Install and launch LM Studio GUI
- GUI mode is required for model loading utility process

**Option B: CLI Installation**
```bash
# Install LM Studio CLI (if available)
# Follow LM Studio documentation for CLI installation
```

### 2. Configure Environment Variables

Create or update `.env.local` (or `.env`) with LM Studio settings:

```bash
# LM Studio Configuration (Phase-3C)
LM_STUDIO_ENABLED=1
LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1
LM_STUDIO_MODEL=christian-bible-expert-v2.0-12b

# Alternative: Use legacy host/port format
# LM_STUDIO_HOST=http://127.0.0.1:1234
# LM_EMBED_HOST=127.0.0.1
# LM_EMBED_PORT=1234

# Model Configuration
THEOLOGY_MODEL=christian-bible-expert-v2.0-12b
MATH_MODEL=self-certainty-qwen3-1.7b-base-math
EMBEDDING_MODEL=text-embedding-bge-m3
RERANKER_MODEL=qwen.qwen3-reranker-0.6b
```

**Note**: The centralized config loader (`scripts/config/env.py`) handles environment variable precedence. See Configuration section below for details.

### 3. Start LM Studio Server

**GUI Mode (Recommended)**
```bash
# Start LM Studio GUI (required for model loading utility)
DISPLAY=:0 lm-studio &

# Start server on port 1234 (default)
# Use LM Studio GUI: Settings → Local Server → Start Server
# Or use CLI:
lms server start --port 1234 --gpu=1.0
```

**Headless Mode (Advanced)**
```bash
# Start server without GUI (models must be pre-loaded)
lms server start --port 1234 --gpu=1.0
```

### 4. Verify Health

Check LM Studio health using the `pmagent` CLI:

```bash
# Quick health check
pmagent health lm

# Expected output:
# LM_HEALTH: mode=lm_ready (ok)
# {"ok": true, "mode": "lm_ready", ...}
```

If health check fails, see Troubleshooting section below.

### 5. Load Required Models

Models are loaded automatically on first use (dynamic loading), but you can pre-load them:

```bash
# List available models
lms ls

# Check loaded models
lms ps

# Load a specific model (if CLI supports it)
# Or use LM Studio GUI: Models → Load Model
```

**Required Models**:
- `christian-bible-expert-v2.0-12b` (theology enrichment)
- `self-certainty-qwen3-1.7b-base-math` (math verification)
- `text-embedding-bge-m3` (embeddings)
- `qwen.qwen3-reranker-0.6b` (reranking)

## Configuration

### Environment Variables

The LM Studio integration uses centralized configuration via `scripts/config/env.py`. Environment variables are checked in this order:

1. **`LM_STUDIO_ENABLED`**: Enable/disable LM Studio (default: unset = disabled)
2. **`LM_STUDIO_BASE_URL`**: Full base URL including `/v1` (default: `http://localhost:1234/v1`)
3. **`LM_STUDIO_MODEL`**: Model name to use (default: unset)
4. **`LM_STUDIO_API_KEY`**: Optional API key (default: unset)
5. **`LM_STUDIO_TIMEOUT_SECONDS`**: Request timeout (default: `30`)

**Legacy Support** (for backward compatibility):
- `LM_STUDIO_HOST`: Full URL (falls back to `LM_EMBED_HOST` + `LM_EMBED_PORT`)
- `LM_EMBED_HOST`: Hostname (default: `localhost`)
- `LM_EMBED_PORT`: Port number (default: `9994` for embeddings, `1234` for chat)

### Configuration Validation

The `get_lm_studio_settings()` function in `scripts/config/env.py` returns a dictionary:

```python
{
    "enabled": bool,      # True if LM_STUDIO_ENABLED=1 and base_url/model are set
    "base_url": str | None,  # Base URL with /v1 suffix
    "model": str | None,     # Model name
    "api_key": str | None,   # Optional API key
    "timeout": float,        # Timeout in seconds
}
```

### Health Check Configuration

Control health check timeout:

```bash
LM_HEALTH_TIMEOUT=2.0 pmagent health lm
```

Default timeout is 1.0 seconds (fast fail when LM Studio is off).

## Hardware Requirements

### Minimum Requirements

- **RAM**: 8GB+ system RAM for model loading
- **Storage**: ~4-8GB per model (varies by model size)
- **GPU**: Optional but recommended for faster inference
  - **VRAM**: 4GB+ for 4-bit quantized models
  - **GPU Offload**: Enabled by default when available

### Recommended Configuration

- **RAM**: 16GB+ system RAM
- **GPU**: NVIDIA GPU with 8GB+ VRAM
- **Storage**: 20GB+ free space for models
- **CPU**: Multi-core processor (4+ cores)

### Model Sizes

- `christian-bible-expert-v2.0-12b`: ~7GB (4-bit quantized)
- `self-certainty-qwen3-1.7b-base-math`: ~1GB (4-bit quantized)
- `text-embedding-bge-m3`: ~1GB
- `qwen.qwen3-reranker-0.6b`: ~500MB

## Integration with Pipeline

### Phase-3C Integration

The LM Studio adapter is integrated into the enrichment pipeline via:

1. **Routing Bridge** (`src/services/lm_routing_bridge.py`):
   - Uses `select_lm_backend()` to choose between LM Studio and remote LLMs
   - Calls `lm_studio_chat_with_logging()` for LM Studio requests
   - Falls back to legacy `chat_completion()` if LM Studio unavailable

2. **Control-Plane Logging** (`agentpm/runtime/lm_logging.py`):
   - Writes LM Studio calls to `control.agent_run` table
   - Graceful no-op when DB unavailable (hermetic DB-off behavior)
   - Tool identifier: `lm_studio`

3. **Enrichment Node** (`src/nodes/enrichment.py`):
   - Uses `chat_completion_with_routing()` for batched requests
   - Maintains backward compatibility with existing pipeline

### Usage in Pipeline

The enrichment pipeline automatically uses LM Studio when:

1. `LM_STUDIO_ENABLED=1` is set
2. `LM_STUDIO_BASE_URL` and `LM_STUDIO_MODEL` are configured
3. LM Studio health check passes (`pmagent health lm` returns `lm_ready`)

If LM Studio is unavailable, the pipeline falls back to legacy `chat_completion()` (which may also use LM Studio via legacy config).

## Troubleshooting

### "lm_off" Health Check

**Problem**: `pmagent health lm` returns `mode=lm_off`

**Solutions**:

1. **Check LM Studio is running**:
   ```bash
   # Check if process is running
   ps aux | grep -i "lm studio"
   
   # Or check if port is listening
   lsof -i :1234
   # OR
   netstat -an | grep 1234
   ```

2. **Verify endpoint configuration**:
   ```bash
   # Check environment variables
   env | grep LM_STUDIO
   
   # Test endpoint manually
   curl -X POST http://127.0.0.1:1234/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model":"test","messages":[{"role":"user","content":"hi"}],"max_tokens":1}'
   ```

3. **Check LM Studio logs**:
   - GUI: View logs in LM Studio GUI
   - CLI: Check server output for errors

### "connection_refused" Error

**Problem**: Cannot connect to LM Studio endpoint

**Solution**:
1. Start LM Studio server (see Quick Start section)
2. Verify port matches configuration (default: `1234`)
3. Check firewall settings if using remote host

### "timeout" Error

**Problem**: LM Studio not responding within timeout

**Solution**:
1. Increase timeout: `LM_STUDIO_TIMEOUT_SECONDS=60`
2. Check LM Studio logs for slow responses
3. Verify models are loaded (may take time on first load)
4. Check system resources (CPU/GPU usage)

### "model_not_found" Error

**Problem**: Model not available in LM Studio

**Solution**:
1. Download model in LM Studio GUI
2. Verify model name matches `LM_STUDIO_MODEL` exactly
3. Check model is loaded: `lms ps`
4. List available models: `lms ls`

### Control-Plane Logging Not Working

**Problem**: LM Studio calls not appearing in `control.agent_run` table

**Solution**:
1. Verify database is available: `pmagent health db`
2. Check `GEMATRIA_DSN` is set correctly
3. Verify `control.agent_run` table exists (created by migrations)
4. Check logs for DB connection errors

**Note**: Control-plane logging gracefully no-ops when DB unavailable (hermetic behavior). This is expected in CI environments.

## Performance Optimization

### Batch Processing

The enrichment pipeline processes nouns in batches of 4 to avoid overwhelming LM Studio:

```python
# Batch size is hardcoded in enrichment_node()
batch_size = 4
```

Adjust batch size if needed (balance latency vs throughput).

### GPU Offload

Enable GPU offload for faster inference:

```bash
# Start server with GPU offload
lms server start --port 1234 --gpu=1.0
```

### Model Quantization

Use 4-bit quantized models to reduce VRAM requirements:

- Models are typically quantized to 4-bit by default
- Reduces VRAM usage by ~75% with minimal quality loss
- Check model card for quantization details

## Related Documentation

- **LM Health Check**: See `docs/runbooks/LM_HEALTH.md` for health check details
- **Phase-3C Integration**: See `docs/rfcs/RFC-080-lm-studio-control-plane-integration.md` for design
- **ADR-066**: See `docs/ADRs/ADR-066-lm-studio-control-plane-integration.md` for architectural decision
- **Qwen Integration**: See `docs/qwen_integration.md` for Qwen-specific setup
- **Environment Configuration**: See `env_example.txt` for all environment variables

## Make Targets

- `make lm.health.smoke` - Quick LM Studio health check
- `make guard.lm.health` - Detailed JSON health check
- `make bringup.001` - Full bring-up verification (includes LM Studio check)

## Next Steps

After LM Studio is set up and verified:

1. **Run enrichment pipeline**: Test with a small batch of nouns
2. **Check control-plane logs**: Verify calls appear in `control.agent_run` table
3. **Monitor performance**: Use `pmagent control summary` to view LM Studio usage
4. **Optimize configuration**: Adjust batch sizes, timeouts, and model selection as needed

