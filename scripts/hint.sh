#!/usr/bin/env bash
#
# hint.sh — Uniform Runtime Hints Emitter (Rule-026 System Enforcement Bridge)
#
# Purpose: Emit standardized HINT: lines for clear CI log visibility and Cursor runtime tracking
# Requirements: Uniform Format, Runtime Clarity, Fallback Safe, Template Integration
# Related Rules: Rule-026 (System Enforcement Bridge)
# Related Agents: scripts/AGENTS.md Uniform Runtime Hints Emitter
#
set -euo pipefail
msg="${*:-}"
if [ -z "$msg" ]; then
  echo "HINT: (none)"
else
  # LOUD HINT: Make hints visible to all AIs and humans (Rule-026 System Enforcement Bridge)
  echo "🔥🔥🔥 LOUD HINT: $msg 🔥🔥🔥"
  echo "HINT: $msg"
fi
