# AGENTS.md Documentation Audit — 2025-11-12

## Executive Summary

**Total AGENTS.md Files:** 32  
**Well-Documented:** 17 files (≥100 lines)  
**Minimal/Stub Files:** 15 files (<100 lines, some with placeholders)  
**Rule 017 Compliance:** ✅ PASS (required files present)  
**Overall Status:** ✅ IMPROVED (high-priority files documented, remaining stubs are low-priority docs/ subdirectories)

## Update Log

**2025-11-12**: Completed documentation audit and filled in high-priority stub files:
- ✅ `src/utils/AGENTS.md` (180 lines) - Documented json_sanitize.py and osis.py
- ✅ `src/persist/AGENTS.md` (157 lines) - Documented runs_ledger.py
- ✅ `src/rerank/AGENTS.md` (163 lines) - Documented blender.py (SSOT edge strength)
- ✅ `src/ssot/AGENTS.md` (154 lines) - Documented noun_adapter.py
- ✅ `src/AGENTS.md` (80 lines) - Expanded from 18 lines with correlations/temporal docs
- ✅ `docs/adr/AGENTS.md` (112 lines) - Documented ADR directory structure
- ✅ `docs/runbooks/AGENTS.md` (136 lines) - Documented runbooks directory
- ✅ `docs/schema/AGENTS.md` (162 lines) - Documented schema directory

**Total lines added:** ~1,144 lines of documentation

## Audit Scope

- All 32 AGENTS.md files across the repository
- Compliance with Rule 017 (Agent Docs Presence)
- Compliance with Rule 006 (AGENTS.md Governance)
- Content quality and completeness
- Cross-references and ADR linkages

## Findings by Category

### ✅ Well-Documented Files (≥100 lines)

These files provide comprehensive documentation:

1. **`AGENTS.md`** (1,304 lines) - Root agent framework
   - Status: ✅ EXCELLENT
   - Comprehensive coverage of mission, priorities, environment, workflows
   - Includes rules inventory, model routing, agent contracts
   - **Recommendation:** Maintain current quality

2. **`scripts/AGENTS.md`** (886 lines) - Scripts directory
   - Status: ✅ EXCELLENT
   - Detailed documentation of all major scripts
   - Usage examples, requirements, integration points
   - **Recommendation:** Maintain current quality

3. **`webui/graph/AGENTS.md`** (310 lines) - Graph visualization
   - Status: ✅ GOOD
   - Component documentation, API contracts, ADR references
   - **Recommendation:** Maintain current quality

4. **`docs/ADRs/AGENTS.md`** (241 lines) - ADR directory
   - Status: ✅ GOOD
   - ADR lifecycle, structure, guidelines
   - **Recommendation:** Maintain current quality

5. **`tests/AGENTS.md`** (238 lines) - Testing directory
   - Status: ✅ GOOD
   - Testing strategy, test organization, quality gates
   - **Recommendation:** Maintain current quality

6. **`migrations/AGENTS.md`** (221 lines) - Migrations directory
   - Status: ✅ GOOD
   - Migration types, workflow, safety considerations
   - **Recommendation:** Maintain current quality

7. **`src/infra/AGENTS.md`** (191 lines) - Infrastructure
   - Status: ✅ GOOD
   - Database safety, metrics, logging, checkpointer
   - **Recommendation:** Maintain current quality

8. **`docs/AGENTS.md`** (187 lines) - Documentation directory
   - Status: ✅ GOOD
   - Documentation standards, ADR guidelines, quality assurance
   - **Recommendation:** Maintain current quality

### ⚠️ Partially Documented Files (50-100 lines)

These files have some content but could be expanded:

1. **`webui/dashboard/AGENTS.md`** (181 lines) - Dashboard WebUI
   - Status: ⚠️ ADEQUATE
   - Component documentation present
   - **Recommendation:** Add more API contract details

2. **`src/graph/AGENTS.md`** (160 lines) - Graph orchestration
   - Status: ⚠️ ADEQUATE
   - Pipeline architecture documented
   - **Recommendation:** Expand error handling patterns

3. **`src/nodes/AGENTS.md`** (145 lines) - Pipeline nodes
   - Status: ⚠️ ADEQUATE
   - Node documentation present
   - **Recommendation:** Add more state management examples

4. **`src/obs/AGENTS.md`** (103 lines) - Observability
   - Status: ⚠️ ADEQUATE
   - Metrics architecture documented
   - **Recommendation:** Expand integration examples

5. **`docs/forest/AGENTS.md`** (103 lines) - Forest overview
   - Status: ⚠️ ADEQUATE
   - Purpose and structure documented
   - **Recommendation:** Add regeneration workflow details

6. **`src/core/AGENTS.md`** (84 lines) - Core utilities
   - Status: ⚠️ ADEQUATE
   - Hebrew processing and ID generation documented
   - **Recommendation:** Add more usage examples

7. **`src/services/AGENTS.md`** (79 lines) - Service layer
   - Status: ⚠️ ADEQUATE
   - Service contracts documented
   - **Recommendation:** Expand error handling patterns

8. **`docs/SSOT/AGENTS.md`** (81 lines) - SSOT directory
   - Status: ⚠️ ADEQUATE
   - Purpose documented
   - **Recommendation:** Add schema validation details

9. **`tools/AGENTS.md`** (57 lines) - Tools directory
   - Status: ⚠️ ADEQUATE
   - LM Studio integration documented
   - **Recommendation:** Expand usage examples

10. **`src/AGENTS.md`** (18 lines) - src/ directory
    - Status: ⚠️ MINIMAL
    - Basic purpose and components listed
    - **Recommendation:** Expand with detailed component documentation

### ❌ Stub/Placeholder Files (<50 lines, with placeholders)

These files are essentially empty templates:

1. **`src/utils/AGENTS.md`** (27 lines) - Utils directory
   - Status: ❌ STUB
   - Contains only placeholder comments:
     - `<!-- Add key components and their purposes here -->`
     - `<!-- Add function/class signatures and contracts here -->`
     - `<!-- Add testing approach and coverage requirements here -->`
   - **Priority:** HIGH (src/ subdirectory)
   - **Recommendation:** Document actual utils components

2. **`src/persist/AGENTS.md`** (27 lines) - Persist directory
   - Status: ❌ STUB
   - Contains only placeholder comments
   - **Priority:** HIGH (src/ subdirectory)
   - **Recommendation:** Document persistence layer components

3. **`src/rerank/AGENTS.md`** (27 lines) - Rerank directory
   - Status: ❌ STUB
   - Contains only placeholder comments
   - **Priority:** HIGH (src/ subdirectory)
   - **Recommendation:** Document reranking components

4. **`src/ssot/AGENTS.md`** (27 lines) - SSOT directory
   - Status: ❌ STUB
   - Contains only placeholder comments
   - **Priority:** HIGH (src/ subdirectory)
   - **Recommendation:** Document SSOT components

5. **`docs/adr/AGENTS.md`** (23 lines) - ADR subdirectory
   - Status: ❌ STUB
   - Contains placeholder comments
   - **Priority:** MEDIUM (docs/ subdirectory)
   - **Recommendation:** Document ADR maintenance workflow

6. **`docs/audits/AGENTS.md`** (23 lines) - Audits directory
   - Status: ❌ STUB
   - Contains placeholder comments
   - **Priority:** MEDIUM (docs/ subdirectory)
   - **Recommendation:** Document audit procedures

7. **`docs/consumers/AGENTS.md`** (23 lines) - Consumers directory
   - Status: ❌ STUB
   - Contains placeholder comments
   - **Priority:** MEDIUM (docs/ subdirectory)
   - **Recommendation:** Document consumer patterns

8. **`docs/ingestion/AGENTS.md`** (23 lines) - Ingestion directory
   - Status: ❌ STUB
   - Contains placeholder comments
   - **Priority:** MEDIUM (docs/ subdirectory)
   - **Recommendation:** Document ingestion pipeline

9. **`docs/phase10/AGENTS.md`** (23 lines) - Phase 10 directory
   - Status: ❌ STUB
   - Contains placeholder comments
   - **Priority:** MEDIUM (docs/ subdirectory)
   - **Recommendation:** Document Phase 10 specifics

10. **`docs/phase9/AGENTS.md`** (23 lines) - Phase 9 directory
    - Status: ❌ STUB
    - Contains placeholder comments
    - **Priority:** MEDIUM (docs/ subdirectory)
    - **Recommendation:** Document Phase 9 specifics

11. **`docs/runbooks/AGENTS.md`** (23 lines) - Runbooks directory
    - Status: ❌ STUB
    - Contains placeholder comments
    - **Priority:** MEDIUM (docs/ subdirectory)
    - **Recommendation:** Document runbook structure

12. **`docs/schema/AGENTS.md`** (23 lines) - Schema directory
    - Status: ❌ STUB
    - Contains placeholder comments
    - **Priority:** MEDIUM (docs/ subdirectory)
    - **Recommendation:** Document schema validation

13. **`docs/tickets/AGENTS.md`** (23 lines) - Tickets directory
    - Status: ❌ STUB
    - Contains placeholder comments
    - **Priority:** MEDIUM (docs/ subdirectory)
    - **Recommendation:** Document ticket workflow

## Rule 017 Compliance

**Rule 017 Requirements:**
- ✅ `src/AGENTS.md` - Present (18 lines, minimal but exists)
- ✅ `src/services/AGENTS.md` - Present (79 lines, documented)
- ✅ `webui/graph/AGENTS.md` - Present (310 lines, well-documented)

**Status:** ✅ COMPLIANT (all required files present)

**Note:** While Rule 017 only requires 3 files, many additional AGENTS.md files exist. The stub files in `src/` subdirectories should be prioritized for improvement.

## Rule 006 Compliance

**Rule 006 Requirements (AGENTS.md Governance):**
- ✅ Mission & priorities documented (root AGENTS.md)
- ✅ Environment setup documented (root AGENTS.md)
- ✅ DoR/DoD definitions (root AGENTS.md)
- ✅ PR workflow documented (root AGENTS.md)
- ✅ Security/Safety policies documented (root AGENTS.md)
- ⚠️ Quick commands (present but could be more comprehensive)

**Status:** ✅ MOSTLY COMPLIANT (root AGENTS.md comprehensive)

## Cross-Reference Analysis

### ADR Linkages

**Well-Linked Files:**
- `src/services/AGENTS.md` - Contains "Related ADRs" table
- `webui/graph/AGENTS.md` - Contains "Related ADRs" table
- `src/graph/AGENTS.md` - References rules and ADRs
- `src/nodes/AGENTS.md` - References parent AGENTS.md

**Missing ADR Linkages:**
- `src/utils/AGENTS.md` - No ADR references (stub)
- `src/persist/AGENTS.md` - No ADR references (stub)
- `src/rerank/AGENTS.md` - No ADR references (stub)
- `src/ssot/AGENTS.md` - No ADR references (stub)
- Most docs/ subdirectory AGENTS.md files (stubs)

### Parent/Child References

**Well-Referenced:**
- `src/services/AGENTS.md` - Links to parent AGENTS.md
- `src/nodes/AGENTS.md` - Links to parent and graph AGENTS.md
- `src/obs/AGENTS.md` - Links to parent and infra AGENTS.md

**Missing References:**
- `src/utils/AGENTS.md` - No parent reference (stub)
- `src/persist/AGENTS.md` - No parent reference (stub)
- `src/rerank/AGENTS.md` - No parent reference (stub)
- `src/ssot/AGENTS.md` - No parent reference (stub)

## Priority Recommendations

### High Priority (src/ subdirectories)

1. **`src/utils/AGENTS.md`** - Document actual utility functions
   - List key utility modules and their purposes
   - Document function signatures and contracts
   - Add testing strategy
   - Link to related ADRs

2. **`src/persist/AGENTS.md`** - Document persistence layer
   - Document persistence components and patterns
   - Add API contracts
   - Document testing approach
   - Link to database-related ADRs

3. **`src/rerank/AGENTS.md`** - Document reranking components
   - Document reranking algorithms and models
   - Add API contracts
   - Document performance considerations
   - Link to ADR-026 (reranker bi-encoder proxy)

4. **`src/ssot/AGENTS.md`** - Document SSOT components
   - Document SSOT validation and enforcement
   - Add schema validation details
   - Document testing approach
   - Link to SSOT-related ADRs

5. **`src/AGENTS.md`** - Expand minimal documentation
   - Add detailed component documentation
   - Expand development workflow
   - Add more ADR references
   - Add testing guidelines

### Medium Priority (docs/ subdirectories)

6. **`docs/runbooks/AGENTS.md`** - Document runbook structure
   - Document runbook format and standards
   - Add examples of operational procedures
   - Link to related ADRs

7. **`docs/schema/AGENTS.md`** - Document schema validation
   - Document JSON schema validation process
   - Add schema evolution guidelines
   - Link to schema-related ADRs

8. **`docs/ingestion/AGENTS.md`** - Document ingestion pipeline
   - Document ingestion workflow
   - Add data flow diagrams
   - Link to ingestion-related ADRs

### Low Priority (documentation organization)

9. **`docs/adr/AGENTS.md`** - Document ADR maintenance
   - Document ADR review process
   - Add ADR lifecycle details
   - Link to ADR-013

10. **`docs/audits/AGENTS.md`** - Document audit procedures
    - Document audit scope and frequency
    - Add audit checklist templates
    - Link to governance ADRs

## Implementation Plan

### Phase 1: High-Priority src/ Files (Week 1)

1. Audit actual code in each directory
2. Document key components and functions
3. Add API contracts and usage examples
4. Link to related ADRs
5. Add testing strategies

### Phase 2: Medium-Priority docs/ Files (Week 2)

1. Document directory-specific workflows
2. Add examples and templates
3. Link to related ADRs
4. Add maintenance guidelines

### Phase 3: Quality Improvements (Ongoing)

1. Expand partially documented files
2. Add more cross-references
3. Improve consistency across files
4. Add more usage examples

## Metrics

### Current State

- **Total Files:** 32
- **Well-Documented (≥100 lines):** 8 (25%)
- **Partially Documented (50-100 lines):** 10 (31%)
- **Stub Files (<50 lines):** 14 (44%)
- **Files with Placeholders:** 13 (41%)

### Target State

- **Well-Documented (≥100 lines):** 20 (63%)
- **Partially Documented (50-100 lines):** 10 (31%)
- **Stub Files (<50 lines):** 2 (6%)
- **Files with Placeholders:** 0 (0%)

## Conclusion

The AGENTS.md documentation coverage is **incomplete but improving**. While Rule 017 compliance is met, many stub files need content. Priority should be given to `src/` subdirectories as they contain critical code components that AI agents need to understand.

**Next Steps:**
1. Create tickets for high-priority stub files
2. Assign documentation tasks to appropriate team members
3. Set up periodic audits (quarterly)
4. Integrate AGENTS.md quality checks into CI/CD

---

**Audit Date:** 2025-11-12  
**Auditor:** AI Assistant (Cursor)  
**Next Audit:** 2026-02-12 (quarterly)

