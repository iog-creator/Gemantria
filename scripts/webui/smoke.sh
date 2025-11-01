#!/usr/bin/env bash

set -euo pipefail

# Hermetic by default; no network; no writes to share/ in CI.

python3 scripts/adapter/exports_to_viewer.py

if [ -f webui/build.sh ]; then

  echo "[webui] running existing webui/build.sh"

  bash webui/build.sh

elif [ -f scripts/webui/build_existing.sh ]; then

  echo "[webui] running scripts/webui/build_existing.sh"

  bash scripts/webui/build_existing.sh

else

  echo "[webui] no build script present; adapter bundle created only (OK)"

fi

echo "[webui.smoke] OK"
