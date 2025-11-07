---
archived_at: 2025-11-06
archived_by: automated-cleanup
reason: debug-documentation
status: archived
purpose: mcp-troubleshooting
superseded_by: current-mcp-setup
---

# MCP Server Debugging for Cursor (ARCHIVED)

## Current Configuration
- Server Name: gemantria-ops
- Type: command (stdio)
- Command: bash
- Args: /home/mccoy/mcp/gemantria-ops/run_server.sh
- Env: GEMANTRIA_ROOT=/home/mccoy/Projects/Gemantria.v2

## Debugging Steps

### 1. Check Cursor MCP Logs
1. Open Cursor
2. Go to View → Output (Ctrl+Shift+U)
3. Select "MCP Logs" from dropdown
4. Look for errors related to "gemantria-ops"

### 2. Test Server Manually
Run this in terminal:
```bash
cd /home/mccoy/Projects/Gemantria.v2
export GEMANTRIA_ROOT=/home/mccoy/Projects/Gemantria.v2
bash ~/mcp/gemantria-ops/run_server.sh &
SERVER_PID=$!
sleep 3
kill $SERVER_PID
```

### 3. Verify MCP Configuration
In Cursor Settings → MCP, verify:
- Name: gemantria-ops
- Type: command
- Command: bash
- Args: /home/mccoy/mcp/gemantria-ops/run_server.sh
- Environment: GEMANTRIA_ROOT=/home/mccoy/Projects/Gemantria.v2

### 4. Check for Python Path Issues
The server uses the project's .venv. Make sure Cursor can find it:
```bash
cd /home/mccoy/Projects/Gemantria.v2
source .venv/bin/activate
which python
python --version
```

### 5. Alternative: Test with Direct Python
If the wrapper script fails, try configuring MCP to use Python directly:
- Command: `/home/mccoy/Projects/Gemantria.v2/.venv/bin/python`
- Args: `/home/mccoy/mcp/gemantria-ops/server.py`
- Environment: GEMANTRIA_ROOT=/home/mccoy/Projects/Gemantria.v2

### 6. Check Cursor Version
MCP support was added in recent Cursor versions. Check:
- Cursor → About Cursor
- Should be version 0.40+ for full MCP support

### 7. Restart Cursor Completely
After any MCP configuration changes:
1. Close Cursor completely
2. Wait 10 seconds
3. Reopen Cursor
4. Check MCP logs again

## Common Issues

### Issue: "Server not found" or "Failed to start"
- Check file permissions: `ls -la ~/mcp/gemantria-ops/`
- Verify paths exist and are executable
- Check if .venv is activated properly

### Issue: "Import errors" in logs
- Python path issues with .venv
- Missing dependencies in .venv
- Try the "direct Python" configuration above

### Issue: "Timeout" errors
- Server taking too long to start
- Check for blocking operations in server.py

### Issue: No tools appear
- Server started but tools not registered
- Check MCP logs for tool discovery messages
- Verify server.py tool decorators are correct

## Quick Test Commands

```bash
# Test server startup
cd /home/mccoy/Projects/Gemantria.v2 && \
GEMANTRIA_ROOT=/home/mccoy/Projects/Gemantria.v2 \
bash ~/mcp/gemantria-ops/run_server.sh &
sleep 2 && kill %1

# Test Python environment
cd /home/mccoy/Projects/Gemantria.v2 && \
source .venv/bin/activate && \
python -c "import sys; print('Python path:', sys.executable)"

# Test MCP imports
cd /home/mccoy/Projects/Gemantria.v2 && \
source .venv/bin/activate && \
python -c "from mcp.server.fastmcp import FastMCP; print('MCP import OK')"
```
