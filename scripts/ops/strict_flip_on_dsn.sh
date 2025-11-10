#!/usr/bin/env bash
set -euo pipefail
[ -z "${ATLAS_DSN:-${GEMATRIA_DSN:-}}" ] && { echo "NO-GO: DSN missing (export ATLAS_DSN or GEMATRIA_DSN)"; exit 1; }
STRICT_ALWAYS_APPLY=1 make -s guard.alwaysapply.dbmirror | tee evidence/guard_alwaysapply_dbmirror.strict.txt
STRICT_ALWAYS_APPLY=1 make -s guard.alwaysapply.autofix | tee evidence/guard_alwaysapply_autofix.strict.txt
STRICT_ATLAS_DSN=1     make -s atlas.proof.dsn              | tee evidence/atlas_proof_dsn.strict.txt
STRICT_PROMPT_SSOT=1   make -s guard.prompt.ssot            | tee evidence/guard_prompt_ssot.strict.txt
make -s governance.smoke | tee evidence/governance_smoke.strict.txt
git add AGENTS.md RULES_INDEX.md docs/evidence/atlas_proof_dsn.json evidence/*.txt 2>/dev/null || true
git commit -m "ops(strict): DB-as-SSOT flip; mirrors auto-synced; STRICT proofs recorded" 2>/dev/null || true

