#!/usr/bin/env bash
set -euo pipefail
for f in "$@"; do
  if [[ -f "$f" ]]; then
    echo "----- ${f} (head) -----"; head -n 30 "$f" || true
    echo "----- ${f} (tail) -----"; tail -n 30 "$f" || true
  else
    echo "SKIP: ${f} (not a file)"
  fi
done
