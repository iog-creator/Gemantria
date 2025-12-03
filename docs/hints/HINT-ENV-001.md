# Python venv not activated

**Hint ID**: `HINT-ENV-001`  
**Scope**: environment  
**Kind**: REQUIRED  
**Priority**: 10  

## Problem

Scripts cannot access project modules or environment variables

## Fix

1. Activate venv: source .venv/bin/activate
2. Set PYTHONPATH: export PYTHONPATH=$(pwd):$PYTHONPATH
3. Verify: which python (should show .venv/bin/python)

**Severity**: CRITICAL

