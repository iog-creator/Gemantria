#!/usr/bin/env bash
set -euo pipefail

# Run multiple Codex tasks in parallel (each fresh context).
# Read tasks from stdin (one per line) or pass files via -f.

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

declare -a TASKS
if [[ "${1:-}" == "-f" && -n "${2:-}" ]]; then
  mapfile -t TASKS < "$2"
else
  if [ -t 0 ]; then
    echo "Usage: PROFILE=<name> CWD=<repo> $0  # then pipe tasks via stdin (one per line)."
    exit 2
  else
    mapfile -t TASKS
  fi
fi

pids=()
for task in "${TASKS[@]}"; do
  [[ -z "$task" ]] && continue
  if [[ -n "$PROFILE" ]]; then
    codex exec -C "$CWD" --profile "$PROFILE" "$task" &
  else
    codex exec -C "$CWD" "$task" &
  fi
  pids+=("$!")
done

status=0
for pid in "${pids[@]}"; do
  wait "$pid" || status=$?
done
exit "$status"
