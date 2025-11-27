#!/bin/bash
# Quick fix for duplicate venv prompt indicators
# Run this to clean up the current terminal session

EXPECTED_VENV="$(pwd)/.venv"

# Count how many times (.venv) appears in PS1
VENV_COUNT=$(echo "$PS1" | grep -o "(.venv)" | wc -l)

if [ "$VENV_COUNT" -le 1 ] && [ -n "${VIRTUAL_ENV:-}" ] && [ "${VIRTUAL_ENV}" == "$EXPECTED_VENV" ]; then
  echo "✅ Venv is already correctly activated (no duplicates)"
  exit 0
fi

echo "🔧 Fixing duplicate venv indicators ($VENV_COUNT found)..."

# Deactivate all venv instances (may need multiple calls)
for i in {1..10}; do
  if [ -n "${VIRTUAL_ENV:-}" ]; then
    deactivate 2>/dev/null || break
  else
    break
  fi
done

# Clean up prompt - remove all (.venv) prefixes
export PS1="${PS1//\(.venv\) /}"
export PS1="${PS1//\(.venv\)/}"

# Clear venv variables
unset VIRTUAL_ENV
unset VIRTUAL_ENV_PROMPT

# Reactivate properly (only once)
if [ -f "$EXPECTED_VENV/bin/activate" ]; then
  source "$EXPECTED_VENV/bin/activate" 2>/dev/null
  echo "✅ Venv reactivated cleanly"
  echo "   VIRTUAL_ENV: ${VIRTUAL_ENV:-NOT SET}"
  echo "   PS1 now shows: $(echo "$PS1" | head -c 50)..."
else
  echo "⚠️  No .venv found in current directory: $EXPECTED_VENV"
fi

