# GPU Resource Management for Ollama + LM Studio

## Problem

When both Ollama and LM Studio run simultaneously, they compete for the same GPU, causing:
- Model loading/unloading conflicts
- Performance degradation
- Resource contention errors

## Solution: CPU-Only Mode for Ollama Embeddings

Since embeddings are lightweight and fast on CPU, configure Ollama to use CPU-only mode for embeddings while LM Studio uses the GPU for the theology model.

## Configuration

### Option 1: Systemd Service Override (Recommended for Systemd)

If Ollama is running as a systemd service:

```bash
# First, unload any models already in GPU memory
ollama ps  # Check loaded models
ollama rm <model-name>  # Unload models if needed

# Create override directory
sudo mkdir -p /etc/systemd/system/ollama.service.d

# Create override file (use both variables for maximum compatibility)
sudo tee /etc/systemd/system/ollama.service.d/override.conf > /dev/null << 'EOF'
[Service]
Environment="OLLAMA_NUM_GPU=0"
Environment="CUDA_VISIBLE_DEVICES="
EOF

# Reload systemd and restart Ollama
sudo systemctl daemon-reload
sudo systemctl restart ollama

# Verify Ollama is running and not using GPU
systemctl is-active ollama
curl http://localhost:11434/api/tags
nvidia-smi --query-compute-apps=pid,process_name --format=csv | grep -i ollama || echo "✓ Ollama not using GPU"
```

### Option 1b: Environment Variable (Manual Start)

If Ollama is started manually, add to `.env.local`:

```bash
# Force Ollama to use CPU-only mode (prevents GPU conflicts with LM Studio)
OLLAMA_NUM_GPU=0
```

Then restart Ollama:
```bash
# Stop Ollama
pkill ollama

# Restart Ollama with CPU-only mode
OLLAMA_NUM_GPU=0 ollama serve
```

### Option 2: CUDA_VISIBLE_DEVICES (Alternative)

If `OLLAMA_NUM_GPU` doesn't work, hide the GPU from Ollama:

```bash
# Start Ollama with GPU hidden (CPU-only)
CUDA_VISIBLE_DEVICES="" ollama serve
```

Or create a systemd override:
```bash
# Edit Ollama service
sudo systemctl edit ollama

# Add:
[Service]
Environment="CUDA_VISIBLE_DEVICES="
```

### Option 3: LM Studio GPU Limit

Alternatively, limit LM Studio's GPU usage:

```bash
# Start LM Studio server with partial GPU
lms server start --port 9994 --gpu=0.5
```

This allows both to share the GPU, but may cause slower performance.

## Verification

1. **Check Ollama is using CPU:**
   ```bash
   # Run a test embedding
   curl http://localhost:11434/api/embeddings \
     -d '{"model": "bge-m3:latest", "prompt": "test"}'
   
   # Monitor GPU usage (should not increase)
   watch -n 1 nvidia-smi
   ```

2. **Check LM Studio is using GPU:**
   ```bash
   # Check LM Studio process GPU usage
   nvidia-smi | grep lm-studio
   ```

3. **Test both simultaneously:**
   ```bash
   # Run embedding (Ollama - should use CPU)
   curl http://localhost:11434/api/embeddings ...
   
   # Run theology chat (LM Studio - should use GPU)
   curl http://localhost:9994/v1/chat/completions ...
   
   # Monitor GPU - only LM Studio should show GPU usage
   nvidia-smi
   ```

## Recommended Configuration

For the current setup (embeddings on Ollama, theology on LM Studio):

1. **Ollama**: CPU-only (`OLLAMA_NUM_GPU=0`)
   - Embeddings are fast enough on CPU
   - Prevents GPU conflicts
   - Leaves full GPU for LM Studio

2. **LM Studio**: Full GPU (`--gpu=1.0`)
   - Theology model benefits from GPU acceleration
   - No conflicts since Ollama is CPU-only

## Performance Impact

- **Embeddings on CPU**: ~10-50ms slower per request (acceptable for most use cases)
- **Theology on GPU**: Full performance (no change)
- **Overall**: Eliminates conflicts, stable operation

## Troubleshooting

### Ollama still using GPU after setting OLLAMA_NUM_GPU=0

1. Verify environment variable is set:
   ```bash
   env | grep OLLAMA_NUM_GPU
   ```

2. Restart Ollama completely:
   ```bash
   pkill ollama
   sleep 2
   OLLAMA_NUM_GPU=0 ollama serve
   ```

3. Check Ollama logs for GPU usage:
   ```bash
   journalctl -u ollama -f | grep -i gpu
   ```

### LM Studio still conflicting

1. Check LM Studio server settings:
   - Settings → Local Server → GPU Offload
   - Ensure it's set to use GPU

2. Verify only one model is loaded at a time:
   ```bash
   # Check loaded models
   lms ps
   ```

3. Monitor GPU memory:
   ```bash
   nvidia-smi --query-gpu=memory.used,memory.total --format=csv
   ```

## References

- [Ollama Environment Variables](https://github.com/ollama/ollama/blob/main/docs/faq.md)
- [LM Studio GPU Configuration](https://lmstudio.ai/docs)
- [NVIDIA GPU Management](https://developer.nvidia.com/nvidia-management-library-nvml)

