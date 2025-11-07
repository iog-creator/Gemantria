#!/usr/bin/env python3
import json

# Read MCP config
with open("/home/mccoy/.cursor/mcp.json") as f:
    config = json.load(f)

print("📊 MCP Server Configuration Status:")
print("=" * 50)

servers = config.get("mcpServers", {})
print(f"Total configured servers: {len(servers)}")

for name, server_config in servers.items():
    print(f"\n🔧 {name}:")
    print(f"   Command: {server_config.get('command', 'N/A')}")
    if "args" in server_config:
        print(f"   Args: {' '.join(server_config['args'])}")
    if "env" in server_config:
        env_vars = list(server_config["env"].keys())
        print(f"   Env vars: {', '.join(env_vars)}")

    # Check if files exist
    if "command" in server_config:
        cmd = server_config["command"]
        if cmd.startswith("/"):
            import os

            if os.path.exists(cmd):
                print("   ✅ File exists")
            else:
                print("   ❌ File missing")
        elif cmd in ["uvx", "bash"]:
            print("   ✅ System command")
        else:
            print("   ❓ External command")

print("\n" + "=" * 50)
print("💡 To test: Restart Cursor, check MCP Logs for startup messages")
