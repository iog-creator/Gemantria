# DMS Query Protocol - Evidence-First (Rule 050)

## Problem

Agents sometimes query the DMS without first checking if the database is available, leading to:
- Assumptions that `db_off` mode is "expected"
- Excessive troubleshooting when DB is simply not running
- Violations of Rule 050 (Evidence-First Protocol)

## Root Cause

**Why assumptions happen:**
1. Agents see `db_off` mode and think "hermetic behavior is OK"
2. Agents don't check DB status BEFORE querying
3. No mandatory pre-flight check enforces evidence-first protocol
4. Error messages don't clearly point to the fix

## Permanent Fix

### 1. Pre-Flight DB Check (Mandatory)

**Before ANY DMS query, run:**
```bash
python scripts/ops/preflight_db_check.py --mode strict
```

**Or in Python scripts:**
```python
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
preflight = REPO / "scripts" / "ops" / "preflight_db_check.py"
result = subprocess.run([sys.executable, str(preflight), "--mode", "strict"])
if result.returncode != 0:
    print(result.stderr.decode(), file=sys.stderr)
    sys.exit(result.returncode)
```

### 2. Use Proper Tools

**For DMS queries, use pmagent commands (they handle schema correctly):**
```bash
pmagent control status --json-only
pmagent kb registry list --json-only
pmagent status kb --json-only
pmagent reality-check check --mode hint --json-only
```

### 3. Evidence-First Protocol (Rule 050)

**Always check status BEFORE querying:**
1. ✅ Check DB status: `pmagent reality-check check --mode hint`
2. ✅ If DB is off and required: Start it, then proceed
3. ✅ If DB is off and not required: Document why (hermetic context)
4. ❌ Never assume `db_off` is "expected" without checking context

### 4. When DB Off Is Acceptable

**Only in these contexts:**
- CI runs with `CI=1` or `HERMETIC=1`
- Explicitly hermetic test runs
- Development smoke tests that don't require DB

**Never acceptable:**
- Local development work
- DMS queries
- Phase work (16, 17, 18, etc.)
- `make reality.green` checks
- `make share.sync` operations

## Implementation

### Scripts That Query DMS

All scripts that query the DMS must:
1. Import and run pre-flight check
2. Fail-fast if DB required but offline
3. Use centralized DSN loaders (`get_rw_dsn()`, etc.)
4. Emit clear error messages pointing to `docs/hints/HINT-DB-002-postgres-not-running.md`

### Example: Updated Query Script

See `scripts/ops/query_dms_phase_status.py` for the correct pattern:
- Pre-flight DB check at startup
- Proper DSN loader usage
- Clear error messages

## Enforcement

**Rule 050 (Evidence-First Protocol) requires:**
- Check status BEFORE querying
- Never assume without evidence
- Fail-fast if required component is missing

**This protocol enforces:**
- No assumptions about DB state
- Clear error messages with fixes
- Mandatory pre-flight checks for DMS queries

## Related Documentation

- `docs/hints/HINT-DB-002-postgres-not-running.md` - Exact fix for DB offline
- `.cursor/rules/050-ops-contract.mdc` - Evidence-First Protocol
- `docs/SSOT/GEMATRIA_DSN_GOVERNANCE.md` - DSN requirements
- `scripts/ops/preflight_db_check.py` - Pre-flight check implementation

