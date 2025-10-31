#!/usr/bin/env bash
set -euo pipefail
echo "[repro] starting"
make eval.report
make eval.history
make eval.delta
make eval.idstability
make eval.index
make eval.catalog
echo "[repro] OK"
