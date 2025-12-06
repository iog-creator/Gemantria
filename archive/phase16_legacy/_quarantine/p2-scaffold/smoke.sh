#!/usr/bin/env bash

set -euo pipefail

export MOCK_AI="${MOCK_AI:-1}"

export SKIP_DB="${SKIP_DB:-1}"

export PIPELINE_SEED="${PIPELINE_SEED:-4242}"

python3 -m src.pipeline.graph >/dev/null  # envelopes go to stdout if desired

echo "[smoke] pipeline ran with MOCK_AI=$MOCK_AI SKIP_DB=$SKIP_DB SEED=$PIPELINE_SEED"
