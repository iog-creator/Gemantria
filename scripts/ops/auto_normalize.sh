#!/usr/bin/env bash
# Auto-normalize: run before push/PR to keep CI green without babysitting.
# Behavior:
# - Runs pre-commit (if available) to auto-fix formatting.
# - Runs ruff format/check; blocks if issues remain.
# - Runs MCP guards (HINT always; STRICT only blocks if STRICT_PREPUSH=1).
# Env:
#   STRICT_PREPUSH=1   -> fail pre-push on STRICT guard errors.
#   SKIP_PRECOMMIT=1   -> skip pre-commit run.
#   DRY_RUN=1          -> do not modify files (best-effort).

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

VE_RUFF="$ROOT/.venv/bin/ruff"
RUFF_BIN="${VE_RUFF}"
[ -x "$RUFF_BIN" ] || RUFF_BIN="$(command -v ruff || true)"
[ -n "${RUFF_BIN}" ] || { echo "[auto] ruff not found"; exit 1; }

changed_before="$(git status --porcelain=v1 | wc -l | tr -d ' ')"

# 1) pre-commit (auto-fix), unless disabled
if [ "${SKIP_PRECOMMIT:-0}" != "1" ]; then
  if command -v pre-commit >/dev/null 2>&1; then
    if [ "${DRY_RUN:-0}" = "1" ]; then
      echo "[auto] pre-commit (dry-run): would run hooks"
    else
      echo "[auto] running pre-commit hooks..."
      pre-commit run --all-files || true
    fi
  else
    echo "[auto] pre-commit not installed; continuing"
  fi
fi

# 2) ruff format + check (auto-fix when not dry-run)
if [ "${DRY_RUN:-0}" = "1" ]; then
  echo "[auto] ruff format --check"
  "$RUFF_BIN" format --check .
else
  echo "[auto] ruff format (auto-fix)"
  "$RUFF_BIN" format .
fi

echo "[auto] ruff check (with --fix retry if needed)"
set +e
"$RUFF_BIN" check .
rc=$?
if [ $rc -ne 0 ] && [ "${DRY_RUN:-0}" != "1" ]; then
  "$RUFF_BIN" check . --fix
  rc=$?
fi
set -e

if [ $rc -ne 0 ]; then
  echo "[auto] ❌ ruff violations remain; aborting"
  exit 2
fi

# 3) Guards: HINT always; STRICT only blocks with STRICT_PREPUSH=1
mkdir -p evidence
if [ -f scripts/ci/guard_mcp_catalog.py ]; then
  python3 scripts/ci/guard_mcp_catalog.py | tee evidence/guard_mcp_catalog.hint.prepush.json >/dev/null || true
fi
STRICT_MCP=1 python3 scripts/ci/guard_mcp_catalog_strict.py 2>/dev/null | tee evidence/guard_mcp_catalog.strict.prepush.json >/dev/null || true

ok_strict="$(jq -r '.ok_repo // empty' evidence/guard_mcp_catalog.strict.prepush.json 2>/dev/null || echo '')"
if [ "${STRICT_PREPUSH:-0}" = "1" ] && [ "$ok_strict" != "true" ]; then
  echo "[auto] ❌ STRICT guard failed and STRICT_PREPUSH=1; aborting push"
  exit 3
fi

# 4) Summarize
changed_after="$(git status --porcelain=v1 | wc -l | tr -d ' ')"
if [ "$changed_after" != "$changed_before" ]; then
  echo "[auto] ℹ️ files changed during normalization; please add/commit and push again."
  exit 4
fi

echo "[auto] ✅ normalization clean"
exit 0

