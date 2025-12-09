# HINT: Python Environment Not Activated

## Problem Detection

**Symptoms**:
- `GEMATRIA_DSN` environment variable is not set (shows as empty or "NOT SET")
- `ModuleNotFoundError: No module named 'src'` when running scripts
- Database connection errors: `psql: error: FATAL: database "mccoy" does not exist`
- Import errors for project modules

**Root Cause**: Python virtual environment (`.venv`) is not activated, or `PYTHONPATH` is not set to include the project root.

## Exact Fix

### For Interactive Shell
```bash
# Navigate to project root
cd /home/mccoy/Projects/Gemantria.v2

# Activate virtual environment
source .venv/bin/activate

# Set PYTHONPATH to include project root
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Verify environment
which python  # Should show: /home/mccoy/Projects/Gemantria.v2/.venv/bin/python
echo $GEMATRIA_DSN  # Should show: postgresql://... (not empty)
```

### For Script Execution via run_command Tool

**WRONG** (will fail):
```bash
python scripts/some_script.py
```

**CORRECT** (activates venv first):
```bash
bash -c '
source .venv/bin/activate
export PYTHONPATH="$(pwd):$PYTHONPATH"
python scripts/some_script.py
'
```

## Integration with Hints Control Plan

Add this hint to the control plan under "Environment Setup" category:

**Hint ID**: `HINT-ENV-001`  
**Title**: "Python venv not activated"  
**Trigger**: When `GEMATRIA_DSN` is empty or `ModuleNotFoundError: No module named 'src'` appears  
**Message**: 
```
CRITICAL: Python virtual environment not activated!

Problem: Scripts cannot access project modules or environment variables.

Fix:
1. Activate venv: source .venv/bin/activate
2. Set PYTHONPATH: export PYTHONPATH="$(pwd):$PYTHONPATH"
3. Verify: which python (should show .venv/bin/python)

For run_command tool, wrap commands in:
  bash -c 'source .venv/bin/activate && export PYTHONPATH="$(pwd):$PYTHONPATH" && <your_command>'
```

## Verification After Fix

Run these checks to confirm environment is correct:
```bash
# 1. Python location
which python
# Expected: /home/mccoy/Projects/Gemantria.v2/.venv/bin/python

# 2. Environment variables
echo $GEMATRIA_DSN
# Expected: postgresql://...

# 3. Module import
python -c "from src.infra.db import get_gematria_rw; print('OK')"
# Expected: OK

# 4. PYTHONPATH
echo $PYTHONPATH | grep -q "$(pwd)" && echo "PYTHONPATH includes project root" || echo "PYTHONPATH MISSING PROJECT ROOT"
# Expected: PYTHONPATH includes project root
```

## Related Issues

- If `scipy` import fails → Install: `pip install scipy` (within activated venv)
- If DB connection fails but DSN is set → Check Postgres service: `systemctl status postgresql`
- If `concept_correlations` view missing → Run migration: `psql "$GEMATRIA_DSN" -f migrations/017_concept_correlations.sql`
