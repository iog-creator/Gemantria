# scipy required for correlation fallback

**Hint ID**: `HINT-DEP-001`  
**Scope**: environment  
**Kind**: REQUIRED  
**Priority**: 12  

## Problem

Phase 10 Python fallback needs scipy.stats.pearsonr

## Symptom

ERROR: scipy not available for correlation computation fallback

## Fix

pip install scipy (within activated venv)

**Severity**: MEDIUM

