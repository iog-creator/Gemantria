#!/usr/bin/env bash

set -euo pipefail

export MOCK_AI="${MOCK_AI:-1}"
export SKIP_DB="${SKIP_DB:-1}"
export PIPELINE_SEED="${PIPELINE_SEED:-4242}"

python3 scripts/quality/rerank_adapter.py

echo "[quality.smoke] OK (reuse-first)"
