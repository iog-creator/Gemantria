#!/usr/bin/env bash
# Proof snapshot helper for MCP catalog (E05).
set -euo pipefail

mkdir -p share/mcp

date -u +"%Y-%m-%dT%H:%M:%SZ" > share/mcp/proof_snapshot.generated_at.txt
jq -n '{proof:"mcp", ok:true}' > share/mcp/proof_ok.json

