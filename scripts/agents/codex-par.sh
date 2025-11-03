#!/bin/bash

# Parallel task runner for Codex CLI
# Usage: echo "task1\ntask2" | ./codex-par.sh [PROFILE=openai] [-f tasks.txt]

# CI guard
if [ "$CI" = "true" ] && [ "$ALLOW_CODEX" != "1" ]; then
  echo "HINT: Codex CLI is optional and local-only. To enable in CI, set ALLOW_CODEX=1."
  exit 0
fi

# Check for codex command
if ! command -v codex &> /dev/null; then
  echo "Error: 'codex' command not found. Please install Codex CLI and configure."
  exit 1
fi

# Default profile
PROFILE="${PROFILE:-openai}"

# Read tasks from file or stdin
TASKS=()
if [ "$1" = "-f" ] && [ -n "$2" ]; then
  while IFS= read -r line; do
    TASKS+=("$line")
  done < "$2"
else
  while IFS= read -r line; do
    TASKS+=("$line")
  done
fi

if [ ${#TASKS[@]} -eq 0 ]; then
  echo "Usage: echo \"task1\\ntask2\" | $0 [PROFILE=openai|grok4] or $0 -f tasks.txt"
  exit 1
fi

# Run tasks in parallel
PIDS=()
for TASK in "${TASKS[@]}"; do
  codex --profile "$PROFILE" --cwd "${CWD:-.}" "$TASK" &
  PIDS+=($!)
done

# Wait for all
for PID in "${PIDS[@]}"; do
  wait "$PID"
done