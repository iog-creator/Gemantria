# Layer 3: AI Doc Ingestion + Classification — Implementation Plan

**Status**: Planning  
**PM Request**: Build AI-driven doc discovery/classification before tightening guards  
**Test Set**: 7 PDFs in `docs/` directory  
**Date**: 2025-11-30

---

## Executive Summary

The PM proposes implementing **Layer 3 (AI Doc Ingestion + Classification)** before Layers 1-2 to use the recently recovered PDFs as a test set for the AI librarian system. This plan evaluates the current DMS implementation, identifies gaps, and provides a concrete implementation roadmap that avoids duplication.

### Key Finding: Infrastructure Already Exists

**The DMS infrastructure is already substantially implemented.** The gap is not in the pipeline itself, but in:
1. **PDF discovery/extraction** (no PDF support currently)
2. **AI classification metadata** (fragments lack AI-driven annotations)
3. **Automatic triggering** (manual ingestion required)

---

## Current State Assessment

### ✅ What Already Exists

#### 1. Database Schema (Complete)
- `control.doc_registry` — Document metadata registry ([migration 046](file:///home/mccoy/Projects/Gemantria.v2/migrations/046_control_doc_registry_schema.sql))
  - Fields: `doc_id`, `logical_name`, `role`, `repo_path`, `share_path`, `is_ssot`, `enabled`
- `control.doc_fragment` — Content chunks ([migration 047](file:///home/mccoy/Projects/Gemantria.v2/migrations/047_control_doc_content_schema.sql))
  - Fields: `doc_id`, `version_id`, `fragment_index`, `fragment_type`, `content`
  - **Gap**: No `meta` JSONB field for AI classifications
- `control.doc_embedding` — Vector embeddings for RAG
  - Fields: `fragment_id`, `model_name`, `embedding` (1024-dim)
- `control.doc_version` — Content versioning with hashes

#### 2. Ingestion Scripts (Partially Complete)
- ✅ `scripts/governance/ingest_docs_to_db.py` — Registry metadata ingestion
  - Discovers: `AGENTS*.md`, `docs/SSOT/**/*.md`, `docs/runbooks/**/*.md`
  - **Gap**: Does not discover PDFs
- ✅ `scripts/governance/ingest_doc_content.py` — Markdown chunking
  - Chunks: headings, paragraphs, code blocks
  - **Gap**: No PDF text extraction
- ✅ `scripts/governance/ingest_doc_embeddings.py` — Embedding generation
  - Works on existing fragments

#### 3. KB Registry & Planning (Complete)
- ✅ `agentpm/plan/kb.py` — Worklist builder from KB registry
- ✅ `pmagent plan kb` — CLI command for doc health reporting
- ✅ `share/kb_registry.md` — Current status (empty: no documents)

### ❌ What's Missing (Why PDFs Are Invisible)

1. **PDF Discovery**: `ingest_docs_to_db.py` only searches for `.md` files
2. **PDF Text Extraction**: No PDF parsing library installed
3. **AI Classification**: No LLM-driven metadata annotation on fragments
4. **Fragment Metadata**: `control.doc_fragment` lacks `meta` JSONB column
5. **KB Registry Population**: No automated KB registry generation from doc_registry

---

## Root Cause Analysis

### Why the 7 PDFs Are Not Being Managed

The PDFs exist in `docs/*.pdf`:
```
docs/Building a Robust and Reliable Agentic AI System with DSPy.pdf
docs/Designing a Multi-Language Biblical Gematria Module.pdf
docs/Evaluating Gemantria's Postgres Usage and Enhancement Opportunities.pdf
docs/Gemantria Pipeline v2_ Architecture & Workflow Improvement Report.pdf
docs/Gemantria Project Master Reference.pdf
docs/Geometric Deep Learning for Structured and Relational AI in Gemantria.pdf
docs/Technical Audit of Gemantria's PostgreSQL & AI Integration.pdf
```

**But**:
1. `ingest_docs_to_db.py` only searches for `*.md` files (lines 85-95, 122-140)
2. No PDF extraction library in `pyproject.toml` dependencies
3. Even if discovered, no chunking logic for PDFs in `ingest_doc_content.py`
4. No AI classification step after chunking

### Why This Isn't "Another Duplicate Feature"

The PM's Layer 3 proposal **extends existing infrastructure** rather than duplicating it:
- ✅ Re-uses `control.doc_registry` (not creating new tables)
- ✅ Re-uses `control.doc_fragment` (adding `meta` column)
- ✅ Re-uses existing ingestion scripts (extending discovery + chunking)
- ✅ Adds AI classification layer (new capability, not duplicate)
- ✅ Generates KB registry from existing DB data (not a parallel system)

---

## Proposed Implementation Plan

### Phase 1: Extend Discovery (PDF Support)

**Goal**: Make PDFs discoverable by existing ingestion pipeline

#### Tasks:
1. **Add PDF dependency**
   - Install `pypdf` or `pdfplumber` (lightweight, pure Python)
   - Update `pyproject.toml` or `requirements.txt`

2. **Extend `ingest_docs_to_db.py`**
   - Add `iter_pdf_docs()` function to discover `docs/**/*.pdf`
   - Create `DocTarget` entries with `role="architecture"` or `role="audit"`
   - Compute content hashes for PDFs (same SHA-256 logic)

3. **Test**: Dry-run should show 7 PDFs discovered

**Files Modified**:
- `scripts/governance/ingest_docs_to_db.py` (lines 115-141: add PDF discovery)
- `pyproject.toml` (add `pypdf>=4.0.0` or equivalent)

---

### Phase 2: PDF Content Extraction

**Goal**: Chunk PDFs into fragments like Markdown

#### Tasks:
1. **Add `chunk_pdf()` function** to `ingest_doc_content.py`
   - Extract text from PDF (page by page or paragraph detection)
   - Create fragments with `fragment_type="page"` or `"paragraph"`
   - Preserve page numbers in `fragment_index`

2. **Update `ingest_doc_content.py` main loop**
   - Detect file extension (`.md` vs `.pdf`)
   - Route to appropriate chunking function

3. **Test**: Should produce fragments for all 7 PDFs

**Files Modified**:
- `scripts/governance/ingest_doc_content.py` (lines 68-155: add `chunk_pdf()`)

---

### Phase 3: AI Classification Metadata

**Goal**: Annotate fragments with AI-driven metadata

#### Tasks:
1. **Add `meta` JSONB column** to `control.doc_fragment`
   - Migration: `048_add_fragment_meta_column.sql`
   - Column: `meta JSONB DEFAULT '{}'::jsonb`

2. **Create AI classification module** (`agentpm/kb/classify.py`)
   - Function: `classify_fragment(content: str, doc_path: str) -> dict`
   - Inputs: fragment text, file name/path
   - Outputs (stored in `meta`):
     - `subsystem` (str): `"pm"`, `"ops"`, `"biblescholar"`, `"gematria"`
     - `doc_role` (str): `"architecture_blueprint"`, `"audit"`, `"tutorial"`, `"historical_log"`
     - `importance` (str): `"core"`, `"supporting"`, `"nice_to_have"`
     - `phase_relevance` (list[str]): `["Phase 14", "Phase 15"]`
     - `should_archive` (bool): AI suggestion
     - `kb_candidate` (bool): Should appear in KB registry
   - LLM call: Use PM-scoped model (not theology slot)
   - Governance: Track via control-plane `agent_run` table

3. **Integrate into ingestion pipeline**
   - New script: `scripts/governance/classify_fragments.py`
   - Reads fragments from `control.doc_fragment` WHERE `meta IS NULL` or `meta = '{}'`
   - Calls `classify_fragment()` for each
   - Updates `meta` column with AI response

4. **Test**: Dry-run classification on Phase 14 PDF fragments

**Files Created**:
- `agentpm/kb/classify.py` (new module)
- `scripts/governance/classify_fragments.py` (new script)
- `migrations/048_add_fragment_meta_column.sql` (new migration)

**Files Modified**:
- `agentpm/kb/__init__.py` (export `classify_fragment`)

---

### Phase 4: KB Registry Generation

**Goal**: Auto-generate KB registry from `doc_registry` + fragment classifications

#### Tasks:
1. **Create KB registry builder** (`scripts/kb/build_kb_registry.py`)
   - Query: All `doc_id` where any fragment has `meta->>'kb_candidate' = 'true'` and `status != 'archived'`
   - Aggregate per doc: subsystem, role, importance, phase_relevance
   - Output: `share/kb_registry.json` with structure:
     ```json
     {
       "version": "1.0",
       "generated_at": "...",
       "documents": [
         {
           "doc_id": "...",
           "path": "docs/Technical Audit of Gemantria's PostgreSQL & AI Integration.pdf",
           "subsystem": "pm",
           "role": "audit",
           "importance": "core",
           "fragments": [
             {
               "fragment_index": 0,
               "subsystem": "pm",
               "role": "architecture_blueprint",
               "phase_relevance": ["Phase 9", "Phase 13"],
               "kb_candidate": true
             }
           ]
         }
       ]
     }
     ```

2. **Wire to pmagent**
   - Add `pmagent kb refresh` command to regenerate registry
   - Update `pmagent status kb` to read new registry

3. **Test**: Generated registry should contain 7 PDFs

**Files Created**:
- `scripts/kb/build_kb_registry.py` (new script)

**Files Modified**:
- `pmagent/cli.py` (add `kb refresh` command)
- `agentpm/kb/registry.py` (update schema for new format)

---

### Phase 5: End-to-End Verification

**Goal**: Prove the AI librarian can rediscover and classify the 7 PDFs

#### Tasks:
1. **Full ingestion run**:
   ```bash
   python scripts/governance/ingest_docs_to_db.py  # Discover 7 PDFs
   python scripts/governance/ingest_doc_content.py # Extract text
   python scripts/governance/classify_fragments.py # AI classification
   python scripts/kb/build_kb_registry.py          # Generate registry
   ```

2. **Validation**:
   - `pmagent status kb` — Should show 7 PDFs as registered
   - `pmagent plan kb` — Should generate worklist from PDFs
   - Inspect DB: `SELECT logical_name, role FROM control.doc_registry WHERE repo_path LIKE '%pdf'`
   - Inspect fragments: `SELECT COUNT(*) FROM control.doc_fragment WHERE doc_id IN (...)`
   - Inspect classifications: `SELECT meta->>'subsystem', COUNT(*) FROM control.doc_fragment GROUP BY 1`

3. **AI Classification Review**:
   - Are the 7 PDFs correctly classified as `subsystem="pm"` or `"architecture"`?
   - Are any misclassified as `should_archive=true`?
   - Does `phase_relevance` make sense (e.g., Phase 14 PDF tagged for Phase 14)?

4. **KB Registry Inspection**:
   - Does `share/kb_registry.json` contain all 7 PDFs?
   - Do fragment metadata summaries align with AI classifications?

**Files Created**:
- Test script: `tests/integration/test_layer3_pdf_ingestion.py`

---

## Adjustments to PM Plan

### What We Keep from PM Plan:
✅ **Layer 3 first** — Agreed, build AI ingestion before tightening guards  
✅ **7 PDFs as test set** — Explicitly use these for validation  
✅ **Fragment-level metadata** — Store AI classifications in `meta` JSONB (not monolithic blobs)  
✅ **KB registry from DB** — Generate from `doc_registry`, not parallel system  
✅ **Never delete, only mark status** — Use `enabled=false` not `DELETE`  

### What We Adjust:
🔧 **Re-use existing tables** — No new `doc_fragment` table; extend existing with `meta` column  
🔧 **Extend existing scripts** — Modify `ingest_docs_to_db.py` and `ingest_doc_content.py` instead of new pipeline  
🔧 **Incremental deployment** — Each phase is independently testable and shippable  
🔧 **LLM Governance** — AI classification calls tracked via `control.agent_run` (already wired)  

### What We Defer (Future Enhancements):
⏭️ **Automatic re-ingestion** — For now, manual trigger via scripts; later add file watchers  
⏭️ **Multi-page PDF analysis** — Start with naive page-by-page; later add intelligent layout detection  
⏭️ **Status change approval flow** — AI proposes, orchestrator approves (needs UI)  
⏭️ **Expand beyond PDFs** — Once proven, add `.rst`, `.txt`, `.org`, etc.  

---

## Risk Mitigation

### Risk 1: PDF Extraction Quality
**Concern**: PDFs may have poor text extraction (scanned images, complex layouts)  
**Mitigation**:
- Start with text-based PDFs (all 7 are text-based, not scanned)
- Log extraction warnings for review
- Use `pdfplumber` which handles tables/layouts better than `pypdf`

### Risk 2: AI Classification Accuracy
**Concern**: LLM may misclassify critical docs as "archive" or wrong subsystem  
**Mitigation**:
- Use `dry_run` mode first to review classifications
- Human review step before auto-archive
- Log all AI decisions for audit
- Keep original AI response in `meta` for transparency

### Risk 3: Losing PDFs Again
**Concern**: PDFs could be moved/deleted before ingestion complete  
**Mitigation**:
- PDFs already in repo, tracked by git
- Content hashes in `doc_version` detect changes
- Recoverable from git history if deleted

### Risk 4: Performance (Large PDFs)
**Concern**: AI classification on every fragment may be slow/expensive  
**Mitigation**:
- Batch API calls (10 fragments per request)
- Cache classifications (don't re-run if `meta` already populated)
- Use lightweight model for classification (not theology slot)
- Run async with rate limiting

---

## Success Criteria

### Phase 1 Success:
- [ ] `python scripts/governance/ingest_docs_to_db.py --dry-run` shows 7 PDFs discovered
- [ ] No errors installing PDF library

### Phase 2 Success:
- [ ] All 7 PDFs fragmented into `control.doc_fragment`
- [ ] Fragment counts are reasonable (>10 fragments per PDF on average)
- [ ] Manual inspection of extracted text shows quality

### Phase 3 Success:
- [ ] `meta` column populated for all PDF fragments
- [ ] AI classifications are sensible (manual spot-check 10% of fragments)
- [ ] All control-plane `agent_run` entries logged

### Phase 4 Success:
- [ ] `share/kb_registry.json` contains all 7 PDFs
- [ ] `pmagent status kb` shows 7 registered docs
- [ ] `pmagent plan kb` generates actionable worklist

### Overall Success (PM Test):
> **"The AI system rediscovers known missing knowledge"**

- [ ] PDFs that were invisible are now in KB registry
- [ ] AI correctly identifies them as core PM/architecture docs
- [ ] None are misclassified as "should archive"
- [ ] Phase relevance tags match actual content (e.g., Phase 14 PDF → Phase 14 tag)
- [ ] KB worklist surfaces these docs as high-priority items

---

## Implementation Order

### Recommended Sequence:
1. **Phase 1** (1-2 hours) — PDF discovery, validate with dry-run
2. **Phase 2** (2-3 hours) — PDF extraction, test on 1 PDF first
3. **Phase 3** (3-4 hours) — AI classification module + migration
4. **Phase 4** (2-3 hours) — KB registry builder
5. **Phase 5** (1-2 hours) — End-to-end validation

**Total Estimate**: 9-14 hours of development + testing

### First Deliverable (MVP):
- Phases 1-2 only: **PDFs discoverable and fragmented**
- User can query `control.doc_fragment` to see extracted text
- Proves infrastructure works before adding AI layer

### Second Deliverable (AI Layer):
- Phases 3-4: **AI classification + KB registry generation**
- User can run `pmagent status kb` and see PDFs with classifications

---

## Artifacts to Create

### Code Files:
1. `agentpm/kb/classify.py` — AI classification logic
2. `scripts/governance/classify_fragments.py` — Classification runner
3. `scripts/kb/build_kb_registry.py` — KB registry generator
4. `migrations/048_add_fragment_meta_column.sql` — Schema update
5. `tests/integration/test_layer3_pdf_ingestion.py` — E2E test

### Modified Files:
1. `scripts/governance/ingest_docs_to_db.py` — Add PDF discovery
2. `scripts/governance/ingest_doc_content.py` — Add PDF chunking
3. `pmagent/cli.py` — Add `kb refresh` command
4. `pyproject.toml` — Add PDF library dependency

### Documentation:
1. `docs/SSOT/LAYER3_AI_DOC_INGESTION_PLAN.md` — Design doc (this file)
2. `agentpm/kb/AGENTS.md` — Document new classification module
3. `scripts/governance/AGENTS.md` — Document new scripts
4. Update `MASTER_PLAN.md` — Add Layer 3 to roadmap

---

## Next Steps (If Plan Approved)

### Immediate Actions:
1. **PM Review**: Confirm this plan aligns with Layer 3 vision
2. **User Confirmation**: Verify this addresses "why PDFs are invisible"
3. **Dependency Check**: Confirm `pypdf` or `pdfplumber` is acceptable
4. **Dry-Run Test**: Run Phase 1 discovery dry-run to validate approach

### Post-Approval:
1. Create implementation branch: `feature/layer3-ai-doc-ingestion`
2. Implement Phase 1 (PDF discovery)
3. Test on 7 PDFs
4. Iterate through Phases 2-5
5. Create PR with test evidence

---

## Conclusion

**The DMS infrastructure is already 70% built.** The PM's Layer 3 proposal fills the remaining 30%:
- PDF support (discovery + extraction)
- AI classification metadata
- KB registry auto-generation

This plan **extends existing code** rather than duplicating functionality, re-uses proven patterns (doc_registry, doc_fragment), and provides incremental validation at each phase. The 7 PDFs serve as a perfect test set to prove the AI librarian can rediscover and classify critical docs that were previously invisible.

**Recommendation**: Approve and proceed with Phase 1 implementation.
