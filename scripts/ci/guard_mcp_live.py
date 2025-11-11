#!/usr/bin/env python3
"""
guard.mcp.sse — HINT mode

Checks presence of MCP SSE server for LM Studio bridge (non-fatal unless enabled).

STRICT: same checks but still non-fatal (optional integration).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

root = Path(".")
enable = os.getenv("ENABLE_LMSTUDIO_MCP", "0") == "1"

# Check if server script exists
server_script = Path.home() / "mcp/gemantria-ops/run_server_sse.sh"
server_py = Path.home() / "mcp/gemantria-ops/server.py"

exists_script = server_script.exists()
exists_server = server_py.exists()

# Check if server is running (port 8005)
import socket

port_open = False
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(("127.0.0.1", 8005))
    sock.close()
    port_open = result == 0
except Exception:
    port_open = False

# Health check (HTTP response)
# FastMCP SSE endpoint is at /sse (returns 200 with text/event-stream)
http_ok = False
if port_open:
    try:
        import urllib.request

        req = urllib.request.Request("http://127.0.0.1:8005/sse")
        req.add_header("Accept", "text/event-stream")
        with urllib.request.urlopen(req, timeout=2) as resp:
            http_ok = resp.status == 200 and "text/event-stream" in resp.headers.get("Content-Type", "")
    except Exception:
        http_ok = False

checked = exists_script and exists_server
healthy = port_open and http_ok

report = {
    "checked": checked,
    "healthy": healthy,
    "exists": {"script": exists_script, "server": exists_server},
    "port_open": port_open,
    "http_ok": http_ok,
    "enabled": enable,
    "notes": [
        "HINT: LM Studio MCP bridge (optional). Set ENABLE_LMSTUDIO_MCP=1 to require.",
        "Start server: make mcp.sse.start",
        "Health check: make mcp.sse.health",
    ],
}

if enable and not healthy:
    report["ok_repo"] = False
    print(json.dumps(report, indent=2), file=sys.stderr)
    sys.exit(1)
else:
    report["ok_repo"] = True
    print(json.dumps(report, indent=2))
    sys.exit(0)
