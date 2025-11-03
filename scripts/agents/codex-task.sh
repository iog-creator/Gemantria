#!/bin/bash

# Single-task wrapper for Codex CLI
# Usage: ./codex-task.sh "your task instruction" [PROFILE=openai]

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

# Task from arg
if [ -z "$1" ]; then
  echo "Usage: $0 \"task instruction\" [PROFILE=openai|grok4]"
  exit 1
fi

TASK="$1"

# Run codex with profile and task
codex --profile "$PROFILE" --cwd "${CWD:-.}" "$TASK"