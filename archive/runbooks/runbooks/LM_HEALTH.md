# LM Health Runbook

## Purpose

This runbook explains how to check LM Studio health posture and interpret the results. The LM health check verifies endpoint availability and response validity for the local Language Model server.

## Quick Start

### CLI Usage (Primary Interface)

The `pmagent` CLI is the primary interface for health checks:

```bash
# Check LM health
pmagent health lm

# Or using Python module directly
python -m pmagent.cli health lm
```

### Make Target (Convenience Wrapper)

The Make target is a thin wrapper around `pmagent`:

```bash
make lm.health.smoke
```

Both methods output:
- **JSON** to stdout (machine-friendly)
- **Human-readable summary** to stderr

Example output:
```
LM_HEALTH: mode=lm_ready (ok)
```

## LM Health Modes

The LM health check reports one of two modes:

### `lm_ready` - LM Studio Operational

**Meaning**: LM Studio endpoint is reachable and responding correctly.

**What it checks**:
- ✅ LM Studio endpoint is reachable (default: `http://127.0.0.1:1234`)
- ✅ `/v1/chat/completions` endpoint responds with valid JSON
- ✅ Response structure is correct (has `choices` or `error` field)

**Next steps**: You're ready to use LM Studio for AI-powered features. Proceed with normal operations.

### `lm_off` - LM Studio Unavailable

**Meaning**: LM Studio endpoint is not reachable or responding incorrectly.

**Common reasons**:
- **LM Studio not running**: The LM Studio server is not started
- **Connection refused**: Endpoint is not listening on the expected port
- **Timeout**: Endpoint is not responding within the timeout window (default: 1.0 seconds)
- **Invalid response**: Endpoint responded but with malformed JSON or unexpected structure
- **HTTP error**: Endpoint returned an error status code (e.g., 500)

**Next steps**:
1. **If LM Studio not running**: Start LM Studio:
   ```bash
   # Start LM Studio GUI (recommended for model loading)
   # Or use headless mode:
   lms server start --port 1234 --gpu=1.0
   ```
2. **If connection refused**: 
   - Verify LM Studio is running: Check the LM Studio GUI or process list
   - Check endpoint configuration in `.env.local` or `.env`:
     ```bash
     # Default endpoint
     LM_STUDIO_HOST=http://127.0.0.1:1234
     
     # Or use embed host/port
     LM_EMBED_HOST=127.0.0.1
     LM_EMBED_PORT=1234
     ```
   - Ensure the port matches your LM Studio server configuration
3. **If timeout**: 
   - LM Studio may be overloaded or slow to respond
   - Increase timeout if needed: `LM_HEALTH_TIMEOUT=2.0 make lm.health.smoke`
   - Check LM Studio logs for errors
4. **If invalid response**: 
   - Verify LM Studio version is compatible
   - Check LM Studio API documentation for expected response format
   - Review LM Studio logs for errors

**Note**: It is **safe and expected** for LM Studio to be off in many workflows. The health check always exits 0 (hermetic behavior) and is safe for CI environments.

## Detailed Health Check

For detailed JSON output, run the guard directly:

```bash
make guard.lm.health
```

This outputs structured JSON with:
- `ok`: Boolean indicating overall health
- `mode`: One of `lm_ready`, `lm_off`
- `details.endpoint`: The endpoint URL that was checked
- `details.errors`: List of error messages if any checks failed

Example output:
```json
{
  "ok": true,
  "mode": "lm_ready",
  "details": {
    "endpoint": "http://127.0.0.1:1234",
    "errors": []
  }
}
```

## Configuration

### Endpoint Configuration

The LM health check uses the following environment variables (in order of precedence):

1. **`LM_STUDIO_HOST`** (primary): Full URL including protocol
   ```bash
   LM_STUDIO_HOST=http://127.0.0.1:1234
   ```

2. **`LM_EMBED_HOST` + `LM_EMBED_PORT`** (fallback): Host and port separately
   ```bash
   LM_EMBED_HOST=127.0.0.1
   LM_EMBED_PORT=1234
   ```

3. **Default**: `http://127.0.0.1:1234` if no environment variables are set

### Timeout Configuration

Control the health check timeout:

```bash
LM_HEALTH_TIMEOUT=2.0 make lm.health.smoke
```

Default timeout is 1.0 seconds (fast fail when LM Studio is off).

## Integration with Other Tools

### PM Snapshot

The LM health check can be integrated into PM snapshots (future enhancement):

```bash
make pm.snapshot
```

### Bring-up Script

The bring-up script (`make bringup.001`) may include LM health check as part of Step 2 (LM Studio readiness).

## Troubleshooting

### "connection_refused" Error

**Problem**: Cannot connect to LM Studio endpoint.

**Solution**:
1. Verify LM Studio is running:
   ```bash
   # Check if process is running
   ps aux | grep -i "lm studio"
   
   # Or check if port is listening
   netstat -an | grep 1234
   # OR
   lsof -i :1234
   ```
2. Start LM Studio if not running
3. Verify endpoint configuration matches LM Studio server port

### "timeout" Error

**Problem**: LM Studio is not responding within the timeout window.

**Solution**:
1. Increase timeout: `LM_HEALTH_TIMEOUT=3.0 make lm.health.smoke`
2. Check LM Studio logs for errors or slow responses
3. Verify LM Studio is not overloaded (check CPU/GPU usage)
4. Try restarting LM Studio

### "invalid_response" Error

**Problem**: LM Studio responded but with unexpected JSON structure.

**Solution**:
1. Verify LM Studio version is compatible with the API
2. Check LM Studio logs for errors
3. Test endpoint manually:
   ```bash
   curl -X POST http://127.0.0.1:1234/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model":"test","messages":[{"role":"user","content":"hi"}],"max_tokens":1}'
   ```
4. Review LM Studio API documentation

### "http_error" Error

**Problem**: LM Studio returned an HTTP error status code.

**Solution**:
1. Check the error message for specific status code (e.g., 500)
2. Review LM Studio logs for server errors
3. Verify models are loaded in LM Studio
4. Try restarting LM Studio

## Related Documentation

- **Phase-3B Implementation**: See `AGENTS.md` for Phase-3B LM health guard details
- **LM Studio Setup**: See `docs/qwen_integration.md` for LM Studio configuration
- **DB Health Guard**: See `docs/runbooks/DB_HEALTH.md` for similar health check pattern
- **Environment Configuration**: See `env_example.txt` for LM Studio environment variables

## Make Targets

- `make lm.health.smoke` - Quick health check with summary output
- `make guard.lm.health` - Detailed JSON health check
- `make test.phase3b.lm.health` - Run LM health guard tests

