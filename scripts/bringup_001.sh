#!/usr/bin/env bash
# Bring-up script for Gemantria pipeline verification
# Purpose: Validate environment, LM Studio readiness, run minimal pipeline, guards, evidence
# Usage: ./scripts/bringup_001.sh

set -euo pipefail

# CRITICAL: Verify venv BEFORE any Python operations (Rule 062)
if [ -z "${VIRTUAL_ENV:-}" ] || [ "${VIRTUAL_ENV}" != "/home/mccoy/Projects/Gemantria.v2/.venv" ]; then
  echo "🚨 ENVIRONMENT FAILURE 🚨" >&2
  echo "Expected venv: /home/mccoy/Projects/Gemantria.v2/.venv" >&2
  echo "Current venv: ${VIRTUAL_ENV:-NOT SET}" >&2
  echo "Current python: $(which python3 2>/dev/null || echo 'NOT FOUND')" >&2
  echo "ACTION REQUIRED: source .venv/bin/activate" >&2
  echo "🚨 DO NOT PROCEED 🚨" >&2
  exit 1
fi

echo "=== Gemantria Bring-up 001 ==="
echo "Timestamp: $(date -u +%Y%m%dT%H%M%SZ)"
echo "✓ Virtual environment verified: $VIRTUAL_ENV"
echo ""

# 0) Environment hard-gate (Rules 050/051/052 in force)
#    DSNs must be explicit; checkpointer must be Postgres for "real" runs.
#    Load DSNs via centralized loader (Rule 062) or from .env/.env.local

echo ">> Step 0: Environment hard-gate"

# Try loading from .env.local first, then .env (Rule 062: environment validation)
# Unset any existing template values first to allow centralized loader to work
unset GEMATRIA_DSN BIBLE_DB_DSN BIBLE_RO_DSN RO_DSN 2>/dev/null || true

if [ -f .env.local ]; then
    set -a
    source .env.local 2>/dev/null || true
    set +a
elif [ -f .env ]; then
    set -a
    source .env 2>/dev/null || true
    set +a
fi

# Reject template placeholders - unset if they contain < or >
if [ -n "${GEMATRIA_DSN:-}" ] && echo "$GEMATRIA_DSN" | grep -q '[<>]'; then
    unset GEMATRIA_DSN
fi
if [ -n "${BIBLE_DB_DSN:-}" ] && echo "$BIBLE_DB_DSN" | grep -q '[<>]'; then
    unset BIBLE_DB_DSN
fi

# Fallback: try Python centralized loader to get DSNs (Rule 001: centralized DSN access)
# The centralized loader can find DSNs from .env, env_example.txt defaults, or system
# Precedence: .env.local > .env > centralized loader > defaults
if [ -z "${BIBLE_DB_DSN:-}" ] || [ -z "${GEMATRIA_DSN:-}" ]; then
    echo ">> Loading DSNs via centralized loader..."
    eval "$(python3 <<'PYEOF'
from scripts.config.env import get_rw_dsn, get_bible_db_dsn, env
import os
env('PATH')  # Trigger .env loading
rw = get_rw_dsn()
# get_bible_db_dsn() looks for BIBLE_RO_DSN/RO_DSN/ATLAS_DSN_RO, but we need BIBLE_DB_DSN
# Try get_bible_db_dsn() first, then fallback to direct env check for BIBLE_DB_DSN
bible = get_bible_db_dsn() or os.getenv('BIBLE_DB_DSN')
# If still not found, try default from env_example.txt (local socket pattern)
if not bible:
    bible = os.getenv('BIBLE_RO_DSN') or os.getenv('RO_DSN')
# Final fallback: use default from env_example.txt pattern (local development)
if not bible:
    bible = "postgresql://postgres@/bible_db?host=/var/run/postgresql"
# Only export if we have real values (not template placeholders)
if rw and '<' not in rw and '>' not in rw:
    print(f'export GEMATRIA_DSN="{rw}"')
if bible and '<' not in bible and '>' not in bible:
    print(f'export BIBLE_DB_DSN="{bible}"')
PYEOF
)"
fi

# Validate DSNs are set (fail-closed)
: "${BIBLE_DB_DSN:?RO Bible DB DSN required (set in .env.local, .env, or via centralized loader)}"      # RO source (bible_db)
: "${GEMATRIA_DSN:?RW Gematria DB DSN required (set in .env.local, .env, or via centralized loader)}"   # RW outputs (gematria)

export CHECKPOINTER=postgres                        # not memory for this proof

echo "ENV OK: DSNs present; CHECKPOINTER=$CHECKPOINTER"
echo ""

# 1) Verify Always-Apply triad + make entrypoints exist (docs parity)
#    (No network work here; just show operator what to run)

echo ">> Step 1: Verify Always-Apply triad documentation"
if grep -q "Always-Apply Triad" AGENTS.md; then
    echo "✓ Always-Apply Triad found in AGENTS.md"
    grep -n "Always-Apply Triad" AGENTS.md | head -n1
else
    echo "✗ Always-Apply Triad NOT found in AGENTS.md"
    exit 1
fi

if grep -q "Make Targets" AGENTS.md || grep -q "make.*target" AGENTS.md -i; then
    echo "✓ Make targets documentation found in AGENTS.md"
    grep -n "Make Targets\|make.*target" AGENTS.md -i | head -n1 || true
else
    echo "⚠ Make targets documentation not explicitly found (may be in different section)"
fi
echo ""

# 2) Headless LM Studio readiness (no UI, fail-fast)
#    Tools are documented; use them in the listed order.

echo ">> Step 2: Headless LM Studio readiness checks"
echo "Running: python3 tools/lm_bootstrap_strict.py"
python3 tools/lm_bootstrap_strict.py || {
    echo "✗ LM Studio bootstrap failed"
    exit 1
}

echo "Running: python3 tools/smoke_lms_models.py"
python3 tools/smoke_lms_models.py || {
    echo "✗ LM Studio models smoke test failed"
    exit 1
}

echo "Running: python3 tools/smoke_lms_embeddings.py"
python3 tools/smoke_lms_embeddings.py || {
    echo "✗ LM Studio embeddings smoke test failed"
    exit 1
}
echo ""

# 3) Minimal pipeline run (immutable handoffs; SSOT schemas enforced)
#    Make targets are the agent entry points; each writes its SSOT envelope.

echo ">> Step 3: Minimal pipeline run"
echo "Running: make ai.nouns"
make ai.nouns || {
    echo "✗ ai.nouns failed"
    exit 1
}

echo "Running: make ai.enrich"
make ai.enrich || {
    echo "✗ ai.enrich failed"
    exit 1
}

echo "Running: make graph.build"
make graph.build || {
    echo "✗ graph.build failed"
    exit 1
}

echo "Running: make graph.score"
make graph.score || {
    echo "✗ graph.score failed"
    exit 1
}

echo "Running: make analytics.export"
make analytics.export || {
    echo "✗ analytics.export failed"
    exit 1
}
echo ""

# 4) Guards (fail-closed): schema + invariants + Hebrew + orphans + ADR note

echo ">> Step 4: Guards (fail-closed)"
make guards.all || {
    echo "✗ guards.all failed"
    exit 1
}
echo ""

# 5) Evidence bundle for this bring-up

echo ">> Step 5: Capture evidence bundle"
EVIDENCE_DIR="evidence/bringup_001"
mkdir -p "$EVIDENCE_DIR"

# Copy exports
if ls exports/*.json 1> /dev/null 2>&1; then
    cp -v exports/*.json "$EVIDENCE_DIR/" || true
else
    echo "⚠ No JSON exports found in exports/"
fi

# Copy report if exists
if [ -f "report.md" ]; then
    cp -v report.md "$EVIDENCE_DIR/" || true
fi

# Capture log tails (operator steps + guards)
{
    echo "=== ENV ==="
    env | grep -E 'DB_DSN|CHECKPOINTER' || true
    echo ""
    echo "=== MODELS ==="
    python3 tools/smoke_lms_models.py || echo "Models check failed"
    echo ""
    echo "=== EMB ==="
    python3 tools/smoke_lms_embeddings.py || echo "Embeddings check failed"
} > "$EVIDENCE_DIR/proof.txt"

echo "Evidence captured in: $EVIDENCE_DIR"
echo ""

# 6) Optional: quick atlas/telemetry proof (read-only)
# (Leave demo seeds OFF by default)

echo ">> Step 6: Optional Atlas proof (skipped by default)"
echo "To run: make atlas.proof.dsn"
echo ""

echo "=== Bring-up 001 Complete ==="
echo "Evidence: $EVIDENCE_DIR"
echo "Timestamp: $(date -u +%Y%m%dT%H%M%SZ)"

