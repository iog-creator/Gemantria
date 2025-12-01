#!/usr/bin/env python3
import sys

sys.path.insert(0, "/home/mccoy/Projects/Gemantria.v2/.venv/lib/python3.13/site-packages")

try:
    from mcp.server.fastmcp import FastMCP

    print("✅ FastMCP import successful")

    # Test basic server creation
    mcp = FastMCP("gemantria-ops")
    print("✅ FastMCP server creation successful")

    @mcp.tool()
    def test_tool() -> str:
        return "test response"

    print(
        f"✅ Tool registration successful, tools: {len(mcp._tools) if hasattr(mcp, '_tools') else 'unknown'}"
    )
    print("✅ MCP server components working")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ General error: {e}")
    sys.exit(1)
