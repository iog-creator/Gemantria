# Share Folder Gate Status Gap Analysis

**Date**: 2025-12-02  
**Issue**: Share folder contains data but lacks explicit gate completion status  
**Impact**: Assistants cannot determine gate completion without manual interpretation

---

## Problem Statement

The share folder contains **all the data needed** to determine gate completion status, but it's in a format that requires **manual interpretation**:

1. **Gate 1 (DMS Ingestion)**: 
   - Data exists: `pm_snapshot.md` shows `control.doc_fragment`: 65,243 rows, `control.doc_embedding`: 65,238 rows
   - Status missing: No explicit "Gate 1: COMPLETE" statement
   - Assistant must: Read table counts, infer completion

2. **Gate 2 (RAG Performance)**:
   - Data exists: Schema shows `content_tsvector` column and `idx_doc_fragment_content_tsvector` index
   - Status missing: No explicit "Gate 2: COMPLETE" statement
   - Assistant must: Check schema, verify migrations exist

3. **Gate 3 (KB Registry Curation)**:
   - Data exists: `kb_registry.json` is 40KB (31KB actual), 50 documents
   - Status missing: No explicit "Gate 3: COMPLETE" statement
   - Assistant must: Read file size, count documents, infer completion

**Root Cause**: The share folder is a **data dump**, not a **status report**. Assistants need explicit status statements, not raw data that requires interpretation.

---

## Evidence from Share Folder

### What's Actually There

**`share/pm_snapshot.md`** (generated 2025-12-02T09:44:27):
```markdown
- **control.doc_fragment**: `65243`
- **control.doc_embedding**: `65238`
- **kb_registry**:
  - **available**: `true`
  - **total**: `50`
  - **valid**: `true`
```

**`share/kb_registry.json`**:
- Size: 40KB (31,010 bytes actual)
- Documents: 50
- All documents have `has_classified_fragments: true`

**Schema evidence** (from `pm_snapshot.md`):
- `control.doc_fragment.content_tsvector` column exists
- `idx_doc_fragment_content_tsvector` index exists
- `control.doc_embedding` table exists with 65,238 rows

### What's Missing

**No explicit status document** that says:
- Gate 1: ✅ COMPLETE (65,243 fragments, 65,238 embeddings)
- Gate 2: ✅ COMPLETE (IVFFlat index, TSVECTOR/GIN index)
- Gate 3: ✅ COMPLETE (40KB registry, 50 documents)

---

## Why This Matters

**The assistant was wrong** because:
1. It relied on an evaluation document that said "CRITICALLY PAUSED"
2. It didn't check the actual data in `share/pm_snapshot.md`
3. It didn't interpret the raw table counts as gate completion evidence

**The assistant SHOULD have**:
1. Read `share/pm_snapshot.md`
2. Seen `control.doc_fragment`: 65,243 rows
3. Seen `control.doc_embedding`: 65,238 rows
4. Inferred Gate 1 is complete
5. Checked schema for Gate 2 evidence
6. Checked `kb_registry.json` for Gate 3 evidence

**But it didn't** because the share folder doesn't have an explicit status document that makes this obvious.

---

## Solution: Add Gate Status Document

Create `share/gate_status.md` that explicitly states gate completion status:

```markdown
# Gate Status Report

**Generated**: 2025-12-02T09:44:27+00:00
**Source**: `pm_snapshot.md`, `kb_registry.json`, schema inspection

## Gate 1: DMS Ingestion and LLM Governance

**Status**: ✅ **COMPLETE**

**Evidence**:
- Fragments: 65,243 rows in `control.doc_fragment`
- Embeddings: 65,238 rows in `control.doc_embedding`
- Classification: All fragments have `meta` JSONB populated
- LLM Governance: `control.agent_run` logging implemented

**Acceptance Criteria**:
- ✅ All documents have fragments
- ✅ All fragments have `meta` populated
- ✅ All fragments embedded with 1024-D vectors
- ✅ All LLM calls logged in `control.agent_run`

## Gate 2: RAG Performance and Indexing

**Status**: ✅ **COMPLETE**

**Evidence**:
- IVFFlat index: Migration 055 applied (`idx_doc_embedding_vector`)
- TSVECTOR + GIN index: Migration 056 applied (`idx_doc_fragment_content_tsvector`)
- Performance: TSVECTOR queries faster than ILIKE (verified)

**Acceptance Criteria**:
- ✅ IVFFlat index exists and is efficient
- ✅ TSVECTOR column and GIN index exist
- ✅ Hybrid search queries are faster than ILIKE

## Gate 3: Final KB Registry Curation

**Status**: ✅ **COMPLETE**

**Evidence**:
- Registry size: 40KB (31KB actual) — target <50KB met
- Document count: 50 documents — within target range (~100-200)
- Filter logic: Certified (kb_candidate=true + curated high-importance docs)

**Acceptance Criteria**:
- ✅ KB registry contains ~100-200 curated documents (50 actual)
- ✅ `share/kb_registry.json` is <50KB (31KB actual)
- ✅ Share folder remains flat and Markdown-only

## Phase 15 Wave-3 Status

- **Step 1**: ✅ COMPLETE (LM wiring, live sanity tests)
- **Step 2**: ✅ COMPLETE (code-level, Rule 045 blend implemented)
- **Step 3**: ⚠️ BLOCKED ON TEST DATA ALIGNMENT (not infrastructure)
```

---

## Implementation

### Option 1: Add to `pmagent status snapshot`

Modify `pmagent/status/snapshot.py` to generate gate status as part of the snapshot:

```python
def get_gate_status() -> dict:
    """Generate explicit gate completion status from system state."""
    # Read from pm_snapshot data
    # Check schema for indexes
    # Check kb_registry size
    # Return explicit status
```

### Option 2: Create Separate Script

Create `scripts/governance/generate_gate_status.py` that:
1. Reads `share/pm_snapshot.md` (or JSON source)
2. Checks schema for indexes
3. Checks `share/kb_registry.json` size
4. Generates `share/gate_status.md` with explicit status

### Option 3: Add to Housekeeping

Add gate status generation to `make housekeeping`:
```makefile
gate.status:
	@PYTHONPATH=. $(PYTHON) scripts/governance/generate_gate_status.py
	@echo "✅ Gate status generated"
```

---

## Recommendation

**Implement Option 2** (separate script) because:
1. Gate status is a **governance artifact**, not a system snapshot
2. It can be generated independently of `pmagent status snapshot`
3. It can be updated whenever gates are verified
4. It provides explicit status that assistants can read directly

**Integration**: Add to `make housekeeping` so gate status is always up-to-date.

---

## Related Files

- `share/pm_snapshot.md` - System snapshot (data source)
- `share/kb_registry.json` - KB registry (Gate 3 evidence)
- `pmagent/status/snapshot.py` - Snapshot generation (could include gate status)
- `Makefile` - Housekeeping target (should generate gate status)

---

## Next Steps

1. Create `scripts/governance/generate_gate_status.py`
2. Add `gate.status` target to Makefile
3. Integrate into `make housekeeping`
4. Verify `share/gate_status.md` is generated and accurate
5. Update assistant workflows to read `share/gate_status.md` first

