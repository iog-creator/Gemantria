#!/bin/bash
# Auto-activate venv when entering project directory
# Source this in your ~/.bashrc or ~/.zshrc:
#   source /home/mccoy/Projects/Gemantria.v2/scripts/auto_activate_venv.sh

# Only auto-activate if we're in the Gemantria project directory
if [[ "$PWD" == "/home/mccoy/Projects/Gemantria.v2"* ]] || [[ "$PWD" == "$HOME/Projects/Gemantria.v2"* ]]; then
  EXPECTED_VENV="$(pwd)/.venv"
  # Check if venv is already active and correct (avoid duplicate activation)
  if [ -z "${VIRTUAL_ENV:-}" ] || [ "${VIRTUAL_ENV}" != "$EXPECTED_VENV" ]; then
    # Only activate if .venv exists
    if [ -f "$EXPECTED_VENV/bin/activate" ]; then
      # Check if PS1 already has (.venv) to avoid duplicates
      if [[ "$PS1" != *"(.venv)"* ]]; then
        source "$EXPECTED_VENV/bin/activate" 2>/dev/null || true
      fi
    fi
  fi
fi

