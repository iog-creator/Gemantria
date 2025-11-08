#!/usr/bin/env bash

set -euo pipefail

cd ui

npm pkg set type="module" >/dev/null 2>&1 || true

npm exec --yes playwright install --with-deps

UI_URL="${UI_URL:-http://localhost:5173}" npx playwright test ../tests/ui/xrefs-smoke.spec.ts --reporter=line

