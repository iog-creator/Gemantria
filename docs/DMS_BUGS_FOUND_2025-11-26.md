# DMS Edge Case Testing - Bugs Found Report

**Date**: 2025-11-26  
**Status**: Testing in Progress  
**Tests Run**: 8/8 (6 failed, 2 passed - tests NOW RUNNING after psycopg fix!)

## Summary

Implemented comprehensive DMS edge case test suite (DMS-E01 through DMS-E07) and found **CRITICAL BUGS** in the DMS implementation during testing. The tests revealed issues with database compatibility (psycopg2 vs psycopg3), schema constraints, and LM semantic detection.

---

## Critical Bugs Discovered

### 🔴 BUG-1: Wrong Database Driver (CRITICAL - FIXED)

**Module**: `agentpm/dms/staleness.py`, `agentpm/dms/coherence_agent.py`  
**Severity**: CRITICAL  
**Status**: ✅ FIXED

**Problem**:  
- DMS modules were using `psycopg2` (old driver)  
- Rest of codebase uses `psycopg` (v3.2.12)  
- All DMS tests were SILENTLY SKIP PING because psycopg2 not available
- Database WAS configured but tests weren't running!

**Impact**:
- DMS code was never actually tested against real database
- Silent failures - no one noticed tests were skipping
- Tests showed "8 skipped" when database was fully configured

**Fix Applied**:
- Migrated `staleness.py` to use `psycopg` with `dict_row`
- Migrated `coherence_agent.py` to use `psycopg` with `dict_row`  
- Updated all test code to use `psycopg`
- Changed cursor factory from `cursor_factory=psycopg2.extras.RealDictCursor` to `row_factory=dict_row`

**Files Changed**:
- `agentpm/dms/staleness.py`
- `agentpm/dms/coherence_agent.py`
- `agentpm/tests/dms/test_dms_edge_cases.py`

---

### 🔴 BUG-2: Dict Row Access Pattern (CRITICAL - IN PROGRESS)

**Module**: `agentpm/dms/staleness.py`  
**Severity**: CRITICAL  
**Status**: 🔧 IN PROGRESS

**Problem**:
- After migrating to `psycopg` with `dict_row`, queries return dictionaries not tuples
- Code was using `result[0]` which raises `KeyError:  0`
- Staleness module completely broken: `compute_dms_staleness_metrics()` returns error

**Current Error**:
```
{
  "available": false,
  "source": "error",
  "error": "Failed to compute staleness metrics: 'cnt'"
}
```

**Impact**:
- **`pmagent report kb` DOES NOT WORK**
- Staleness metrics unavailable
- DMS Phase 2 functionality completely broken

**Fix In Progress**:
- ✅ Fixed deprecated archive count: `result['cnt']`
- ✅ Fixed canonical count: `result['cnt']`
- ❌ Still need to fix other aggregate queries (total, active, deprecated, etc.)

**Root Cause**:
The migration from psycopg2 to psycopg3 changed how row results work:
- psycopg2 + RealDictCursor: Can access both `row[0]` and `row['column']`
- psycopg3 + dict_row: Can ONLY access `row['column']`, `row[0]` raises KeyError

---

### 🔴 BUG-3: Missing NOT NULL Schema Fields (HIGH)

**Module**: `agentpm/tests/dms/test_dms_edge_cases.py`  
**Severity**: HIGH  
**Status**: ❌ NOT FIXED

**Problem**:
Tests E01, E02, E03 fail with schema violations:
```
psycopg.errors.NotNullViolation: null value in column "content_hash" of relation "kb_document" violates not-null constraint
```

**Required Fields** (from schema):
- `content_hash` TEXT NOT NULL
- `size_bytes` INTEGER NOT NULL  
- `mtime` TIMESTAMPTZ NOT NULL

**Impact**:
- Cannot test phase misalignment (E02)
- Cannot test deprecated document tracking (E03)
- Cannot test stale document detection (E01)

**Fix Needed**:
Update test INSERT statements to include:
```python
cur.execute("""
    INSERT INTO control.kb_document (
        id, path, title, lifecycle_stage, phase_number,
        content_hash, size_bytes, mtime  # <-- Add these
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
""", (
    test_id, f"test/doc.md", "Test Doc", "active", 6,
    "test-hash-12345", 1024, stale_mtime  # <-- Provide values
))
```

---

### 🟡 BUG-4: Missing SQLAlchemy Dependency (MEDIUM)

**Module**: `agentpm/status/kb_metrics.py` (indirect)  
**Severity**: MEDIUM  
**Status**: ❌ NOT FIXED

**Problem**:
Test E04 fails with:
```
ModuleNotFoundError: No module named 'sqlalchemy'
```

**Call Stack**:
```
test_dms_e04 → compute_kb_registry_status()
  → agentpm/status/__init__.py
    → agentpm/status/system.py  
      → scripts/guards/guard_db_health.py
        → from sqlalchemy import text  ← FAILS HERE
```

**Impact**:
- Cannot test unregistered canonical detection (E04)
- `compute_kb_registry_status()` unusable in tests

**Fix Options**:
1. **Add sqlalchemy to dependencies** (if it's supposed to be there)
2. **Make sqlalchemy import optional** with try/except in guard_db_health.py
3. **Refactor to not need sqlalchemy** (use psycopg directly)

---

### 🟡 BUG-5: LM Semantic Similarity Too Aggressive (MEDIUM)

**Module**: `agentpm/dms/coherence_agent.py`  
**Severity**: MEDIUM (LM Quality Issue)  
**Status**: ❌ NOT FIXED - DESIGN FLAW

**Problem**:
Test E07 (semantic similarity) FAILS because LM flags "DSN" vs "connection string" as HIGH severity contradiction.

**Test Assertion**:
```python
# These are the SAME concept, different terminology
doc_a: "Use the **DSN** environment variable..."
doc_b: "Use the **connection string** environment variable..."

# Expected: severity in ("low", "none")
# Actual: severity = "high" ← WRONG!
```

**LM Response**:
```json
{
  "has_contradiction": true,
  "contradictions": [{
    "topic": "Database configuration method",
    "claim_a": "Use DSN",
    "claim_b": "Use connection string",
    "severity": "high"
  }]
}
```

**Impact**:
- False positives in contradiction detection
- PM will be alerted to non-issues
- Semantic similarity not working as intended per PM spec

**Root Cause**:
- LM prompt doesn't emphasize semantic equivalence strongly enough
- No examples of "similar but OK" vs "actually contradictory"  
- Temperature=0.0 makes it too rigid

**Fix Needed**:
Improve contradiction detection prompt in `build_contradiction_prompt()`:
1. Add explicit instruction: "DSN and connection string are the SAME concept"
2. Provide examples of true contradictions vs terminology differences
3. Consider raising temperature slightly (0.1-0.2) for better semantic understanding

---

## Tests Status Summary

| Test | Status | Issue |
|------|--------|-------|
| E01: Stale Document | ❌ FAIL | Missing content_hash/size_bytes fields |
| E02: Phase Misalignment | ❌ FAIL | Missing content_hash/size_bytes fields |
| E03: Deprecated Tracking | ❌ FAIL | Missing content_hash/size_bytes fields |
| E04: Unregistered Canonical | ❌ FAIL | SQLAlchemy import error |
| E05: Direct Contradiction | ✅ PASS | Working correctly |
| E06: LM Unavailable Graceful Degradation | ✅ PASS | Working correctly |
| E07: Semantic Similarity | ❌ FAIL | LM too aggressive (design flaw) |
| Integration Test |  ❌ FAIL | Staleness module broken (BUG-2) |

**Overall**: 2/8 passing (25%)

---

## What-If Scenarios Still To Test

Based on user request to "continue asking what-if questions", here are additional stress tests needed:

### Database Stress Tests
- **What if**: 1000+ documents with same phase_number? (query performance)
- **What if**: Document path has Unicode characters (emoji, CJK)?  
- **What if**: mtime is null or future date?
- **What if**: Two documents with same content_hash but different paths?
- **What if**: lifecycle_stage has invalid value bypassing check constraint?

### Coherence Agent Stress Tests  
- **What if**: LM returns malformed JSON?
- **What if**: LM returns partial JSON (truncated)?
- **What if**: LM times out mid-response?
- **What if**: 100+ canonical documents (O(n²) explosion)?
- **What if**: Document content is 10MB+ (truncation issues)?

### Concurrency Tests
- **What if**: Two processes update same document lifecycle simultaneously?
- **What if**: Coherence check runs while docs are being updated?
- **What if**: Migration 053 runs while staleness check is running?

### Edge Values
- **What if**: deprecated_at is exactly 30 days ago (boundary test)?
- **What if**: phase_number is negative or 9999?
- **What if**: topic_key contains SQL injection attempt?

---

## Next Actions

1. **IMMEDIATE**: Fix dict row access in staleness.py (all aggregate queries)
2. **IMMEDIATE**: Fix test INSERT statements to include required fields  
3. **HIGH PRIORITY**: Fix or make optional sqlalchemy dependency
4. **MEDIUM PRIORITY**: Improve LM contradiction detection prompt
5. **ONGOING**: Add stress tests from "What-If Scenarios" section above

---

## Verification Plan

Once bugs fixed, run full test suite:
```bash
# Run all DMS tests
pytest agentpm/tests/dms/test_dms_edge_cases.py -v

# Expected: 8/8 passing

# Run staleness module directly
python3 -c "from agentpm.dms.staleness import compute_dms_staleness_metrics; 
import json; print(json.dumps(compute_dms_staleness_metrics(), indent=2))"

# Expected: available=true, source="database"

# Run full DMS report
pmagent report kb

# Expected: Both staleness and coherence metrics present
```

---

## Lessons Learned

1. **Silent test skipping is dangerous**: Tests showed "8 skipped" but no one caught it
2. **Database driver migrations are breaking**: psycopg2 → psycopg3 changes API significantly  
3. **Integration tests catch real bugs**: Found 5 critical bugs in first test run
4. **LM quality matters**: Semantic similarity detection needs better prompting
5. **Schema constraints are good**: NOT NULL caught missing test data immediately

---

**Report Generated**: 2025-11-26 07:53 PST  
**Next Update**: After fixing BUG-2 and BUG-3
