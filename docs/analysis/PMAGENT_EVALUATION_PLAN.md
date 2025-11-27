# PMAgent Evaluation & Improvement Plan

**Date:** 2025-11-23  
**Evaluator:** Granite 4.0 Model (simulated)  
**Purpose:** Comprehensive evaluation and fixes for pmagent functionality

## Executive Summary

Systematic evaluation of pmagent core functionality identified 8 critical issues and 3 enhancement opportunities. All issues must be resolved before system can be considered fully functional for Granite 4.0 model usage.

## Issues Identified

### Critical Issues (Must Fix)

#### 1. **Semantic Search Threshold Too Restrictive**
- **Problem:** Default threshold of 0.15 filters out relevant results
- **Impact:** Users get "No relevant documents found" for valid queries
- **Evidence:** Query "SVG icon sizing" found results at 0.05 threshold but not at 0.15
- **Fix:** Lower default threshold to 0.10 or make it adaptive

#### 2. **`kb registry list` Missing `--limit` Option**
- **Problem:** Command doesn't support `--limit` flag despite being useful
- **Impact:** Can't limit output for large registries
- **Evidence:** `pmagent kb registry list --limit 5` returns error
- **Fix:** Add `--limit` option to `kb registry list` command

#### 3. **`kb registry show` Path Matching Failure**
- **Problem:** Cannot find documents with exact path match
- **Impact:** Can't retrieve document details via registry
- **Evidence:** `pmagent kb registry show "docs/runbooks/UI_VISUAL_VERIFICATION_CHECKLIST.md"` returns "Document not found"
- **Fix:** Fix path matching logic (normalization, partial match, or exact match)

#### 4. **`ask docs` Command Shows "db_off" Mode Incorrectly**
- **Problem:** Returns "db_off" mode even when DB is available
- **Impact:** Users think system is offline when it's not
- **Evidence:** `pmagent ask docs` shows `"mode": "db_off"` but `pmagent health db` shows `mode=ready`
- **Fix:** Fix DB connection check in `answer_doc_question` function

#### 5. **Generic Query Handling Poor**
- **Problem:** Single-word queries like "test" return no results
- **Impact:** Poor user experience for exploratory queries
- **Evidence:** `pmagent ask query "test"` returns "No relevant documents found"
- **Fix:** Improve query handling or provide better feedback for low-quality queries

#### 6. **Missing Error Context in Search Results**
- **Problem:** When search fails, no indication of why (threshold too high, no embeddings, etc.)
- **Impact:** Users can't diagnose search issues
- **Fix:** Add diagnostic information to search results

#### 7. **Inconsistent Command Output Formats**
- **Problem:** Some commands output JSON, some human-readable, some both
- **Impact:** Hard to script/automate pmagent usage
- **Fix:** Standardize output format with `--json-only` flag consistently

#### 8. **No Query Suggestions or Feedback**
- **Problem:** When search returns no results, no guidance on how to improve query
- **Impact:** Users don't know how to refine queries
- **Fix:** Add query suggestions or threshold hints

### Enhancement Opportunities

#### 9. **Adaptive Threshold Based on Result Count**
- **Enhancement:** Automatically lower threshold if no results found
- **Benefit:** Better user experience without manual threshold tuning

#### 10. **Search Result Preview/Content Snippets**
- **Enhancement:** Show content previews in search results
- **Benefit:** Users can see why document matched without opening it

#### 11. **Query History and Learning**
- **Enhancement:** Track successful queries to improve suggestions
- **Benefit:** System learns what queries work best

## Test Matrix

### Core Commands to Test

| Command | Status | Issues Found |
|---------|--------|--------------|
| `pmagent health db` | ✅ PASS | None |
| `pmagent status kb` | ✅ PASS | None |
| `pmagent kb registry list` | ❌ FAIL | Missing --limit option |
| `pmagent kb registry show` | ❌ FAIL | Path matching issue |
| `pmagent ask query` | ⚠️ PARTIAL | Threshold too high, no diagnostics |
| `pmagent ask docs` | ❌ FAIL | Shows db_off incorrectly |
| `pmagent plan kb list` | ⏸️ NOT TESTED | - |
| `pmagent reality-check check` | ⏸️ NOT TESTED | - |

## Implementation Plan

### Phase 1: Critical Fixes (Priority 1)

1. **Fix Threshold Default**
   - File: `agentpm/knowledge/vector_store.py`
   - Change: Default threshold from 0.15 to 0.10
   - File: `pmagent/cli.py`
   - Change: Default threshold from 0.15 to 0.10 in `ask_query` command

2. **Add --limit to kb registry list**
   - File: `pmagent/cli.py`
   - Change: Add `limit` option to `kb_registry_list` command

3. **Fix kb registry show path matching**
   - File: `pmagent/cli.py`
   - Change: Fix path matching logic in `kb_registry_show` command
   - Options: Normalize paths, support partial matches, or exact match with better error

4. **Fix ask docs db_off mode**
   - File: `agentpm/knowledge/qa_docs.py`
   - Change: Fix DB connection check to properly detect available DB

### Phase 2: User Experience Improvements (Priority 2)

5. **Add Search Diagnostics**
   - File: `agentpm/knowledge/vector_store.py`
   - Change: Return diagnostic info (threshold used, embedding count, etc.)

6. **Improve Generic Query Handling**
   - File: `agentpm/knowledge/vector_store.py`
   - Change: Add minimum query length check or better feedback

7. **Standardize Output Formats**
   - File: `pmagent/cli.py`
   - Change: Ensure all commands support `--json-only` consistently

8. **Add Query Feedback**
   - File: `pmagent/cli.py`
   - Change: When no results, suggest lowering threshold or refining query

### Phase 3: Enhancements (Priority 3)

9. **Adaptive Threshold**
   - File: `agentpm/knowledge/vector_store.py`
   - Change: Auto-lower threshold if no results at default

10. **Search Result Previews**
    - File: `agentpm/knowledge/vector_store.py`
    - Change: Include content preview in SearchResult

11. **Query History (Future)**
    - New feature: Track and learn from successful queries

## Testing Strategy

### Unit Tests
- Test threshold changes with known queries
- Test path matching with various path formats
- Test DB connection detection

### Integration Tests
- Test full search workflow with various queries
- Test registry commands with real data
- Test error handling and diagnostics

### User Acceptance Tests
- Test as Granite 4.0 model would use system
- Test common query patterns
- Test error scenarios

## Success Criteria

1. ✅ All critical issues (1-8) resolved
2. ✅ All core commands work as expected
3. ✅ Search finds relevant documents with default threshold
4. ✅ Error messages are clear and actionable
5. ✅ Commands are consistent and scriptable
6. ✅ System is usable by Granite 4.0 model without manual intervention

## Timeline

- **Phase 1:** 2-3 hours (critical fixes)
- **Phase 2:** 1-2 hours (UX improvements)
- **Phase 3:** 2-3 hours (enhancements)
- **Total:** 5-8 hours

## Risk Assessment

- **Low Risk:** Threshold changes, adding options
- **Medium Risk:** Path matching fixes (may affect existing usage)
- **High Risk:** DB connection detection (core functionality)

## Dependencies

- DB must be available for testing
- Embeddings must be up to date
- Knowledge base must be populated

## Next Steps

1. Review and approve this plan
2. Execute Phase 1 fixes
3. Test fixes thoroughly
4. Execute Phase 2 improvements
5. Final validation as Granite 4.0 model
6. Document changes in AGENTS.md and rules

