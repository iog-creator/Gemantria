#!/usr/bin/env bash
set -euo pipefail
# Only check source files, not dependencies or rule docs
if grep -RIn --exclude-dir=.git --exclude-dir=.venv --exclude-dir=__pycache__ --exclude-dir=.cursor --include="*.py" --include="*.md" -E "(__mocks__|fixtures/mock|mockdata|Mock[A-Z]|jest\.mock\(|unittest\.mock)" . ; then
  echo "Mock artifacts detected. Mocks are prohibited in source code."
  exit 1
fi
echo "No mock artifacts detected in source code."
