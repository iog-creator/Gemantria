# HINT: Missing Database DSN is a Fatal Error

## Problem Detection

**Symptoms**:
- Script requires database access but DSN environment variable is missing
- Agent proceeds with "code-only analysis" as a fallback
- Agent accepts missing DSN as acceptable output rather than blocking error
- Queries fail with "DSN not set" but work continues

**Root Cause**: Agent treats missing database credentials as a warning instead of a fatal blocker, violating DB-First governance.

## Exact Fix

### For Agents (Critical Rule)

**NEVER proceed if a required DSN is missing. STOP immediately.**

Required DSNs for this project:
- `GEMATRIA_DSN` - **MANDATORY** for all gematria/analysis work
- `BIBLE_DB_DSN` - **MANDATORY** for scripture/lexicon access

### Configuration Fix

Add to `.env`:
```bash
# Both point to same database (Phase 14+ merge)
GEMATRIA_DSN="postgresql://mccoy@/gematria?host=/var/run/postgresql"
BIBLE_DB_DSN="postgresql://mccoy@/bible_db?host=/var/run/postgresql"
```

### Verification

```bash
source .venv/bin/activate
set -a
source .env
set +a

# Test GEMATRIA_DSN
psql "$GEMATRIA_DSN" -c "SELECT current_database();"

# Test BIBLE_DB_DSN  
psql "$BIBLE_DB_DSN" -c "SELECT current_database();"
```

## Why This Matters

**Governance Rules Violated** when DSN is missing but work continues:
- **Rule-050/051/052**: Hard-block AlwaysApply (DB access is required, not optional)
- **Rule-066**: LLM Subordination (DB is SSOT, not code inference)
- **Rule-069**: DMS-First workflow (requires DB access)
- **Rule-070**: Gotchas Check (missing DSN is a critical gotcha)
- **Phase 14**: DB-First Gematria & Lexicon enrichment mandates
- **Phase 15**: COMPASS scoring requires DB-backed data

**Impact of proceeding without DB**:
- Code-only analysis produces **speculative** results
- Schema assumptions may be **completely wrong**
- Implementation based on wrong assumptions **will fail**
- Wastes time creating incorrect plans/documentation
- Violates architectural contracts

## Correct Agent Behavior

### ❌ WRONG (What I did initially)
```python
if not os.getenv("GEMATRIA_DSN"):
    print("WARNING: GEMATRIA_DSN not set, using code analysis")
    # Proceeds with code-only analysis
    analyze_codebase_for_schema()
```

### ✅ CORRECT (What I should have done)
```python
if not os.getenv("GEMATRIA_DSN"):
    print("FATAL ERROR: GEMATRIA_DSN not set")
    print("See: docs/SSOT/GEMATRIA_DSN_GOVERNANCE.md")
    print("See: docs/hints/HINT-DB-001-dsn-mandatory.md")
    sys.exit(1)
```

## When to Apply This Hint

Trigger this hint when:
- Script execution requires DB queries
- Schema inspection is needed
- Data verification must be performed
- Any "DB-First" mandate applies

**Do NOT accept**:
- "DSN not set, skipping DB checks" 
- "Falling back to code analysis"
- "Using cached/example data instead"

**Always STOP and fix the environment first.**

## Related Documentation

- [`docs/SSOT/GEMATRIA_DSN_GOVERNANCE.md`](file:///home/mccoy/Projects/Gemantria.v2/docs/SSOT/GEMATRIA_DSN_GOVERNANCE.md) - PM ruling on DSN requirements
- [`docs/hints/HINT-ENV-001-venv-not-activated.md`](file:///home/mccoy/Projects/Gemantria.v2/docs/hints/HINT-ENV-001-venv-not-activated.md) - Environment setup
- `AGENTS.md` - DSN Contract section
