#!/usr/bin/env bash
set -euo pipefail
msg="${*:-}"
if [ -z "$msg" ]; then
  echo "HINT: (none)"
else
  echo "HINT: $msg"
fi
