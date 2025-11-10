#!/usr/bin/env bash

set -euo pipefail

# Refuse to run outside the project venv

if [ -z "${VIRTUAL_ENV:-}" ] || [[ "$VIRTUAL_ENV" != *"/home/mccoy/Projects/Gemantria.v2/.venv"* ]]; then
  echo "LOUD FAIL: .venv not active. Run: source activate_venv.sh" >&2
  exit 42
fi

python3 -c 'import sys; assert sys.prefix.endswith(".venv"), "Not in .venv"' || exit 43

echo "OK: .venv active at $VIRTUAL_ENV"
