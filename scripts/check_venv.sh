#!/usr/bin/env bash
# Venv check script - use at start of any session or before Python commands
# Rule 062: Environment Validation (Always Required)

set -euo pipefail

# Filter Cursor IDE integration noise (orchestrator-friendly output)
exec 2> >(grep -v "dump_bash_state: command not found" >&2 || true)

EXPECTED_VENV="/home/mccoy/Projects/Gemantria.v2/.venv"

if [ -z "${VIRTUAL_ENV:-}" ]; then
  echo "🚨 ENVIRONMENT FAILURE 🚨" >&2
  echo "Expected venv: $EXPECTED_VENV" >&2
  echo "Current venv: NOT SET" >&2
  echo "Current python: $(which python3 2>/dev/null || echo 'NOT FOUND')" >&2
  echo "ACTION REQUIRED: source .venv/bin/activate" >&2
  echo "🚨 DO NOT PROCEED 🚨" >&2
  exit 1
fi

if [ "${VIRTUAL_ENV}" != "$EXPECTED_VENV" ]; then
  echo "🚨 ENVIRONMENT FAILURE 🚨" >&2
  echo "Expected venv: $EXPECTED_VENV" >&2
  echo "Current venv: $VIRTUAL_ENV" >&2
  echo "Current python: $(which python3 2>/dev/null || echo 'NOT FOUND')" >&2
  echo "ACTION REQUIRED: source .venv/bin/activate" >&2
  echo "🚨 DO NOT PROCEED 🚨" >&2
  exit 1
fi

# Verify Python is from venv
PYTHON_PATH=$(which python3 2>/dev/null || echo "")
if [ -z "$PYTHON_PATH" ] || [[ "$PYTHON_PATH" != "$EXPECTED_VENV/bin/python3"* ]]; then
  echo "🚨 ENVIRONMENT FAILURE 🚨" >&2
  echo "Expected python: $EXPECTED_VENV/bin/python3" >&2
  echo "Current python: ${PYTHON_PATH:-NOT FOUND}" >&2
  echo "ACTION REQUIRED: source .venv/bin/activate" >&2
  echo "🚨 DO NOT PROCEED 🚨" >&2
  exit 1
fi

echo "✓ Virtual environment verified: $VIRTUAL_ENV"
echo "✓ Python: $PYTHON_PATH"

