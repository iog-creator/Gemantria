#!/usr/bin/env bash
set -euo pipefail

# Optional, local-only Codex task wrapper.
# CI guard: do nothing unless explicitly allowed.

IN_CI=false
if [[ "${CI:-}" == "true" || -n "${GITHUB_ACTIONS:-}" || -n "${GITLAB_CI:-}" || -n "${BUILDKITE:-}" ]]; then IN_CI=true; fi

if $IN_CI && [[ "${ALLOW_CODEX:-0}" != "1" ]]; then
  echo "HINT[codex]: disabled in CI (set ALLOW_CODEX=1 to enable explicitly)."
  exit 0
fi

if ! command -v codex >/dev/null 2>&1; then
  cat <<'EOF'
LOUD FAIL
tool: codex
action: exec
args: (missing)
error: 'codex' CLI not found. Install with: npm i -g @openai/codex
EOF
  exit 127
fi

PROFILE="${PROFILE:-}"
CWD="${CWD:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"

usage() {
  cat <<USAGE
Usage: PROFILE=<name> CWD=<repo> scripts/agents/codex-task.sh "task instruction"
Env:
  PROFILE  Optional Codex profile (e.g., 'grok4')
  CWD      Repo root (defaults to git toplevel)
Examples:
  scripts/agents/codex-task.sh "List last 5 commits; propose 2-line release note."
  PROFILE=grok4 scripts/agents/codex-task.sh "Scan pytest failures; produce minimal patches."
USAGE
}

TASK="${*:-}"
if [[ -z "$TASK" ]]; then usage; exit 2; fi

set -x
if [[ -n "$PROFILE" ]]; then
  codex exec -C "$CWD" --profile "$PROFILE" "$TASK"
else
  codex exec -C "$CWD" "$TASK"
fi
