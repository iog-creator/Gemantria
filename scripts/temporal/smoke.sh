#!/usr/bin/env bash

set -euo pipefail

# Hermetic: no network, OK if no exports/schemas present.

python3 scripts/temporal/validate.py

echo "[temporal.smoke] OK (reuse-first)"
