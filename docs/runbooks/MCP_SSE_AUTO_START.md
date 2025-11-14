# MCP SSE Server Auto-Start Guide

## Overview

The MCP SSE (Server-Sent Events) server provides a bridge between LM Studio and the Gemantria MCP server. This guide explains how to configure automatic or manual startup.

## Quick Start

### Enable Auto-Start

Add to your `.env.local` or `.env`:

```bash
AUTO_START_MCP_SSE=1
```

The server will automatically start when:
- Running `make bringup.001` (if `AUTO_START_MCP_SSE=1`)
- Running `make mcp.sse.ensure` (checks and starts if needed)

### Manual Start

```bash
# Start the server
make mcp.sse.start

# Check if it's running
make mcp.sse.health

# Stop the server
make mcp.sse.stop
```

## How It Works

### Auto-Start Mode (`AUTO_START_MCP_SSE=1`)

When enabled, the `scripts/mcp_sse_ensure.sh` script will:
1. Check if the server is already running on port 8005
2. If not running, automatically start it
3. Verify the server started successfully

**Integration points:**
- `make bringup.001` - Automatically ensures server is running before LM Studio checks
- `make mcp.sse.ensure` - Standalone check-and-start command
- `scripts/mcp_sse_ensure.sh` - Core script that can be called directly

### Manual Mode (default)

When `AUTO_START_MCP_SSE` is not set or set to `0`:
- Server must be started manually with `make mcp.sse.start`
- `make mcp.sse.ensure` will only check status, not start
- Use `--force` flag to override: `bash scripts/mcp_sse_ensure.sh --force`

## Troubleshooting

### Server Won't Start

1. **Check if port is already in use:**
   ```bash
   lsof -i :8005
   ```

2. **Check server logs:**
   ```bash
   tail -f /tmp/mcp_sse.log
   ```

3. **Verify server script exists:**
   ```bash
   test -f ~/mcp/gemantria-ops/run_server_sse.sh && echo "OK" || echo "Missing"
   ```

4. **Test manual start:**
   ```bash
   bash ~/mcp/gemantria-ops/run_server_sse.sh
   ```

### LM Studio Connection Errors

If you see `ECONNREFUSED 127.0.0.1:8005`:
1. Ensure server is running: `make mcp.sse.health`
2. If not running, start it: `make mcp.sse.start` or enable auto-start
3. Restart LM Studio after server is running

### Auto-Start Not Working

1. **Verify environment variable is set:**
   ```bash
   echo $AUTO_START_MCP_SSE
   ```

2. **Check script permissions:**
   ```bash
   ls -l scripts/mcp_sse_ensure.sh
   ```

3. **Test ensure script directly:**
   ```bash
   AUTO_START_MCP_SSE=1 bash scripts/mcp_sse_ensure.sh
   ```

## Configuration

### Environment Variables

- `AUTO_START_MCP_SSE` - Set to `1` to enable auto-start (default: `0`)
- `MCP_HOST` - Server host (default: `127.0.0.1`)
- `MCP_PORT` - Server port (default: `8005`)
- `GEMANTRIA_ROOT` - Project root directory (auto-detected if not set)

### Makefile Targets

- `make mcp.sse.start` - Start the server manually
- `make mcp.sse.ensure` - Check and start if `AUTO_START_MCP_SSE=1`
- `make mcp.sse.health` - Verify server is responding
- `make mcp.sse.stop` - Stop the server

## Integration with Cursor Rules

This auto-start capability follows Rule-012 (Connectivity Troubleshooting) and Rule-046 (Hermetic CI Fallbacks):

- **Graceful degradation**: If server can't start, operations continue (non-fatal)
- **Service discovery**: Automatically detects if server is already running
- **Environment validation**: Checks prerequisites before attempting start
- **Clear error messages**: Provides actionable feedback when startup fails

## Best Practices

1. **Development**: Enable auto-start in `.env.local` for convenience
2. **CI/CD**: Leave auto-start disabled (server not needed in CI)
3. **Production**: Use systemd service for persistent startup (future enhancement)
4. **Troubleshooting**: Use manual mode to isolate startup issues



