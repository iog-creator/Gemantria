# LM Studio Memory Management

## Problem

LM Studio is trying to load the Christian Bible Expert model (12B parameters, ~12GB) but failing due to insufficient GPU memory.

## Current GPU Memory Status

- **Total GPU Memory**: 16GB (RTX 5070 Ti)
- **Currently Used**: ~9GB
- **Available**: ~7GB
- **Model Size Needed**: ~12GB (Christian Bible Expert v2.0-12B)

## Solutions

### Option 1: Free Up GPU Memory (Recommended)

1. **Unload any models currently in GPU memory:**
   ```bash
   # Check what's using GPU
   nvidia-smi
   
   # If LM Studio has a model loaded, unload it via UI or API
   curl -X DELETE http://127.0.0.1:9994/v1/models/<model-id>
   ```

2. **Restart LM Studio** to clear any cached GPU memory:
   ```bash
   # Close LM Studio completely
   pkill lm-studio
   
   # Restart LM Studio
   lm-studio
   ```

3. **Use Model Quantization:**
   - Load a quantized version of the model (Q4, Q5, Q8)
   - Quantized models use less GPU memory
   - Example: `christian-bible-expert-v2.0-12b-Q4_K_M.gguf` (~6GB instead of 12GB)

### Option 2: Use CPU for Theology Model (Fallback)

If GPU memory is insufficient, configure the theology model to use CPU:

```bash
# In .env.local
THEOLOGY_PROVIDER=ollama
THEOLOGY_MODEL=granite4:tiny-h  # Use smaller model on CPU
```

**Note**: This will be slower but will work without GPU memory constraints.

### Option 3: Reduce Model Size

1. **Download a quantized version:**
   - Q4_K_M: ~6GB (recommended)
   - Q5_K_M: ~7.5GB
   - Q8_0: ~10GB

2. **Use a smaller model:**
   - Switch to a 7B or 8B parameter model instead of 12B
   - Trade-off: Less capability but fits in available memory

### Option 4: Increase Available GPU Memory

1. **Close other GPU applications:**
   - Close any games, video editors, or other GPU-intensive apps
   - Check for background processes using GPU

2. **Reduce Ollama memory usage:**
   - Ensure Ollama is using CPU-only (already configured)
   - Unload any Ollama models: `ollama ps` then unload if needed

## Verification

After applying a solution:

```bash
# Check GPU memory
nvidia-smi --query-gpu=memory.used,memory.total,memory.free --format=csv

# Try loading the model in LM Studio
# Monitor GPU memory during load
watch -n 1 nvidia-smi
```

## Recommended Approach

1. **Immediate**: Unload any existing models and restart LM Studio
2. **Short-term**: Use a quantized model (Q4_K_M recommended)
3. **Long-term**: Consider upgrading GPU or using model sharding

## Model Size Reference

- **Full precision (FP16)**: ~12GB for 12B parameters
- **Q8 quantization**: ~10GB
- **Q5 quantization**: ~7.5GB
- **Q4 quantization**: ~6GB (recommended for 16GB GPU)

## Troubleshooting

### "Out of memory" error persists

1. Check for memory leaks:
   ```bash
   # Monitor GPU memory over time
   watch -n 1 nvidia-smi
   ```

2. Clear GPU cache:
   ```bash
   # Restart LM Studio completely
   pkill -9 lm-studio
   # Wait a few seconds
   lm-studio
   ```

3. Check for other GPU processes:
   ```bash
   nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv
   ```

### Model loads but is very slow

- This indicates the model is running on CPU instead of GPU
- Check LM Studio settings → Local Server → GPU Offload
- Ensure GPU is enabled and selected

