#!/usr/bin/env bash
set -euo pipefail

mkdir -p share/mcp

printf "%s\n" "STRICT trace @ $(date -u +'%Y-%m-%dT%H:%M:%SZ')" > share/mcp/strict_trace.ptr.txt

