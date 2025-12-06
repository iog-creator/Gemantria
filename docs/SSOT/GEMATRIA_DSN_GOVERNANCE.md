# GEMATRIA_DSN Governance (Mandatory Configuration)

## PM Ruling

- `GEMATRIA_DSN` is a **required** environment variable.
- It must point to the **same database** as `BIBLE_DB_DSN`.
- Missing or unset `GEMATRIA_DSN` is a **fatal blocker**.
- Agents must **not proceed** if `GEMATRIA_DSN` is missing.
- This is required for:
  - Phase 8 Metadata Enrichment
  - Phase 10 Correlation Analytics
  - Phase 14 Gematria Integration
  - Phase 15 COMPASS Structural Scoring
  - DMS table access
  - DB-first governance

## Required Configuration

Example .env:

```
BIBLE_DB_DSN=postgresql://user:pass@localhost:5432/gemantria
GEMATRIA_DSN=${BIBLE_DB_DSN}
```

or:

```
GEMATRIA_DSN=postgresql://user:pass@localhost:5432/gemantria
```

Both DSNs must point to the same Postgres instance.

## Rule Enforcement

- If `GEMATRIA_DSN` is missing → **STOP**
- If connection fails → **STOP**
- If schema cannot be loaded → **STOP**

No agent may continue operations until this condition is resolved.

## Governance Rules Integration

This ruling enforces:
- **Rule-050/051/052**: Hard-block AlwaysApply behavior
- **Rule-066**: LLM Subordination (DB is SSOT, not code inference)
- **Rule-069**: DMS-First workflow contracts
- **Rule-070**: Gotchas Check (missing DSN is a critical gotcha)
- **Phase 14**: DB-First Gematria & Lexicon enrichment
- **AGENTS.md**: DSN Contract requirements

## Historical Context

Originally, the project separated:
- `BIBLE_DB_DSN`: Read-heavy scripture access
- `GEMATRIA_DSN`: Compute-heavy numerics

As of **Phase 14**, both DSNs must point to the **same Postgres instance** containing:
- `bible.*` schemas (verses, tokens, morphology)
- `gematria.*` schemas (nouns, caches, embeddings)
- `analysis.*` schemas (concepts, relations, clusters)
- DMS tables (doc_registry, doc_version, etc.)

## Agent Behavior Contract

All agents (Gemini, Cursor, OPS scripts) MUST:

1. **Check GEMATRIA_DSN at startup**
2. **Fail immediately if not set**
3. **NOT proceed with code-only analysis as fallback**
4. **Escalate to PM/user with clear error message**

### Example Check (bash):
```bash
if [ -z "${GEMATRIA_DSN}" ]; then
  echo "FATAL ERROR: GEMATRIA_DSN not set"
  echo "See: docs/SSOT/GEMATRIA_DSN_GOVERNANCE.md"
  exit 1
fi
```

### Example Check (Python):
```python
import os
import sys

if not os.getenv("GEMATRIA_DSN"):
    print("FATAL ERROR: GEMATRIA_DSN not set", file=sys.stderr)
    print("See: docs/SSOT/GEMATRIA_DSN_GOVERNANCE.md", file=sys.stderr)
    sys.exit(1)
```

## Violation Response

If an agent proceeds without GEMATRIA_DSN:
- **Immediate halt** of all work
- **Escalation to PM** with governance violation notice
- **Correction** of any artifacts created under false assumptions
- **Re-execution** of all steps once DSN is configured

## Status: ACTIVE

This governance rule is **immediately effective** and applies to:
- All current and future phases
- All agents and automation
- All manual and automated workflows

**No exceptions.**
