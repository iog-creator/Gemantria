#!/usr/bin/env bash
set -euo pipefail

python3 scripts/guards/generate_rules_inventory.py

git diff --exit-code -- AGENTS.md >/dev/null 2>&1 || {
  echo "RULES_INVENTORY drift detected; re-generated table differs from committed file."
  exit 1
}

echo "[rules_inventory_check] OK"

