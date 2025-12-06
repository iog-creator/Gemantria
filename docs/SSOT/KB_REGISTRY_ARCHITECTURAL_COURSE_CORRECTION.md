# KB Registry Architectural Course Correction

**Date**: 2025-12-02  
**Status**: Architectural Guidance (Not Yet Implemented)  
**Related**: `LAYER3_AI_DOC_INGESTION_PLAN.md`, `PHASE15_WAVE3_PLAN.md`, `PM_SHARE_LAYOUT_PHASE15.md`

---

## 1. Problem Statement

The KB registry was expanded to include all 994 documents from DMS, resulting in:
- **26,713 lines** (808KB) — too large for PM consumption
- **987 documents without fragments** — not RAG-ready
- **Share folder bloat** — violates DMS-First principle

This breaks the original Layer 3 design intent and cripples RAG effectiveness.

---

## 2. Architectural Solution

### 2.1 Separation of Concerns

| Component | Purpose | Size | Content |
|-----------|---------|------|---------|
| **KB Registry** | Curated planning index | ~100-200 docs | SSOT docs, runbooks, key ADRs, root AGENTS.md, classified fragments |
| **pgvector** | Full content search (RAG) | All 994 docs | All documents, fragmented and embedded |
| **Share Folder** | PM-facing summaries | Small | Curated summaries, not full dumps |

### 2.2 Design Principles

1. **DMS is SSOT** — Postgres/DMS is the single source of truth
2. **Share folder is render target** — Small, curated Markdown files derived from DMS
3. **KB Registry is curated** — Only important documents for planning/discovery
4. **All documents in pgvector** — Full RAG capability requires all 994 documents

---

## 3. Required Architectural Gates

### Gate 1: Completing the DMS Ingestion Schema (Layer 3 Prerequisites)

**Status**: `meta` JSONB column already exists (migration 048) ✅  
**Priority**: **IMMEDIATE** — Must be completed before Phase 15 Wave-3 Step 2

**Required Steps**:

1. **Verify Schema** (Already Complete):
   - ✅ `control.doc_fragment.meta` JSONB column exists
   - ✅ GIN index on `meta` exists (`idx_doc_fragment_meta`)

2. **Fragment All Documents**:
   ```bash
   # Run for all 994 documents (not just AGENTS.md)
   python scripts/governance/ingest_doc_content.py --only-agents=false
   ```
   - **Prerequisite**: Generates content chunks for all documents
   - Creates fragments in `control.doc_fragment` table
   - Currently: 7 documents have fragments, **987 do not** (must be fixed)
   - **Output**: All 994 documents have fragments ready for embedding

3. **Run AI Classification** (Layer 3 Phase 3) — **Strict LLM Governance**:
   ```bash
   # Classify all fragments (not just PDFs)
   python scripts/governance/classify_fragments.py --pdf-only=false
   ```
   - Populates `meta` JSONB column with AI classifications
   - Sets `kb_candidate=true` for fragments that should appear in KB registry
   - Determines `subsystem`, `doc_role`, `importance`, `phase_relevance`
   
   **Strict LLM Governance Requirements** (Mandatory):
   - **LLM Role**: The LLM used for AI classification must be treated as a **Metadata Classifier**
   - **System Prompt Constraints** (Required):
     - **Primary Role**: "Your sole function is structured data extraction and classification"
     - **Generative Ban**: You are **absolutely forbidden** from generating interpretation or narrative text
     - **Output Format**: Output must conform exactly to the classification schema
   - **Tracking**: Every LLM call must be tracked via `control.agent_run` table
     - Adhere to standard audit logging pattern
     - Record model, prompt, response, and classification results
     - Enable full traceability of AI decisions

4. **Embedding Consistency and Verification** (Mandatory):
   - All new fragments must use **1024-D embeddings** (canonical format)
   - Store embeddings in `control.doc_embedding` using 1024-D format
   - **Requirement**: Dimensional unification for high semantic accuracy in multilingual RAG
   - **Critical Violation**: Any attempt to use the legacy **768-D vectors** is a critical violation of Phase 13 mandates
   - **Verification**: The PM must verify that the embedding pipeline for the **987 new documents** exclusively uses the canonical **1024-D embeddings**
   - Verify existing embeddings are 1024-D before proceeding

**Acceptance Criteria**:
- ✅ All 994 documents have fragments in `control.doc_fragment`
- ✅ All fragments have `meta` JSONB populated (even if empty `{}`)
- ✅ AI classification has marked relevant fragments with `kb_candidate=true`
- ✅ All LLM classification calls logged in `control.agent_run`
- ✅ All embeddings are 1024-D format in `control.doc_embedding`

---

### Gate 2: RAG Performance and Indexing Mandates

**Status**: Requires implementation  
**Priority**: **MANDATORY** — Required for real-time RAG performance  
**⚠️ CRITICAL WARNING**: Failing to implement Gate 2 will result in a **fatal performance bottleneck** when Phase 15 RAG scoring (Wave-3 Step 2) is resumed. The existing system is **Behind Best Practices** in indexing.

**Required Steps**:

1. **Implement Vector Index (IVFFlat)**:
   ```sql
   -- Migration 049: Create IVFFlat index on control.doc_embedding
   -- MUST be executed after fragmenting 994 documents (>1000 embeddings)
   CREATE INDEX IF NOT EXISTS idx_doc_embedding_vector
       ON control.doc_embedding
       USING ivfflat (embedding vector_cosine_ops)
       WITH (lists = 100);
   ```
   - **Requirement**: IVFFlat index needs **>1000 rows** to be effective
   - **Timing**: Execute **immediately** after Gate 1 completion (fragmenting 994 docs will exceed threshold)
   - **Purpose**: Fast Approximate Nearest Neighbor (ANN) search for RAG
   - **Migration**: Use migration 049 DDL (create if missing)
   - **Current State**: Verify index exists and is efficient after large fragmentation run

2. **Implement Hybrid RAG Indexing** (Mandatory Enhancement):
   ```sql
   -- Add TSVECTOR column to control.doc_fragment
   ALTER TABLE control.doc_fragment
       ADD COLUMN IF NOT EXISTS content_tsvector tsvector;
   
   -- Create GIN index for full-text search
   CREATE INDEX IF NOT EXISTS idx_doc_fragment_content_tsvector
       ON control.doc_fragment
       USING gin (content_tsvector);
   
   -- Update trigger to auto-populate TSVECTOR
   CREATE OR REPLACE FUNCTION control.update_doc_fragment_tsvector()
   RETURNS TRIGGER AS $$
   BEGIN
       NEW.content_tsvector := to_tsvector('english', COALESCE(NEW.content, ''));
       RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;
   
   CREATE TRIGGER doc_fragment_tsvector_update
       BEFORE INSERT OR UPDATE ON control.doc_fragment
       FOR EACH ROW
       EXECUTE FUNCTION control.update_doc_fragment_tsvector();
   ```
   - **Purpose**: Enable **hybrid search** (combining semantic vector search with keyword filtering)
   - **Benefit**: 
     - Faster keyword filtering (replaces slow `ILIKE` queries)
     - Reliable real-time query performance
     - Supports Phase 15 RAG engine requirements (Option B)
   - **Current State**: System is **behind best practices** — currently using slow `ILIKE` for keyword search
   - **Architectural Gap**: This is a **performance bottleneck** that must be fixed
   - **Verification**: The PM must verify that the resulting hybrid search queries are **faster** than the previous `ILIKE` method

**Acceptance Criteria**:
- ✅ IVFFlat index exists and is efficient (>1000 rows after Gate 1)
- ✅ TSVECTOR column and GIN index exist on `control.doc_fragment.content`
- ✅ Hybrid search queries are **faster** than current `ILIKE` approach
- ✅ Real-time RAG queries meet performance targets

---

### Gate 3: Final KB Registry Curation (PM Usability)

**Status**: Requires implementation  
**Priority**: **FINAL STEP** — Restores PM usability after infrastructure completion

**Required Steps**:

1. **Filter KB Registry Logic** (Curation Logic Verification):
   - Update `scripts/kb/build_kb_registry.py` to filter by:
     - **Primary Filter**: Documents with `meta->>'kb_candidate' = 'true'` fragments (AI-classified)
     - **Plus Manually Curated High-Importance Documents**:
       - All SSOT docs (`is_ssot = true`)
       - All runbooks (`role = 'runbook'`)
       - Key ADRs (manually tagged or high importance)
       - Root-level AGENTS.md files (e.g., `AGENTS_ROOT`, `AGENTS::pmagent/AGENTS.md`)
   - **Target Size**: ~100-200 documents (not 994)
   - **Implementation**: Revert the query to JOIN `doc_fragment` and filter by `kb_candidate=true`, then UNION with curated high-importance docs
   - **Verification**: The final `build_kb_registry.py` script must use a database query that filters by `meta->>'kb_candidate' = 'true'` AND explicitly includes the manually curated categories (SSOT docs, Runbooks, Root AGENTS.md)

2. **Verify Small Share Artifacts** (Artifact Compliance):
   - **Size Constraint**: The PM must verify that `share/kb_registry.json` is **<50KB** (down from 808KB)
     - This confirms the **Share folder is a small, flat render target**
     - This confirms PM usability is restored
   - Ensure `share/kb_registry.md` is human-readable and concise
   - **Share Folder Requirements**:
     - Must remain **flat** (no subdirectories)
     - Must be **Markdown-only** (JSON converted to Markdown per existing process)
     - Must reflect successful **JSON to Markdown Conversion** process
   - **PM Consumption**: Registry must be small enough for PM to review in chat/context

**Acceptance Criteria**:
- ✅ KB registry contains ~100-200 curated documents (not 994)
- ✅ `share/kb_registry.json` is **<50KB** (not 808KB)
- ✅ `share/kb_registry.md` is human-readable and concise
- ✅ Share folder remains flat and Markdown-only
- ✅ PM can query pgvector for full content when needed (all 994 docs available via RAG)

---

## 4. Implementation Order

**CRITICAL**: Phase 15 Wave-3 Step 2 (Full Scoring) must be **paused** until these gates are complete.

### Sequential Execution (Mandatory):

**The PM must immediately prioritize the sequential execution of Gates 1, 2, and 3. Phase 15 Wave-3 Step 2 remains paused until RAG infrastructure is stabilized.**

1. **Gate 1** (DMS Ingestion) — **IMMEDIATE PRIORITY**:
   - Fragment all 994 documents (987 currently missing)
   - Run AI classification with `control.agent_run` logging
   - Verify all fragments have `meta` populated
   - Ensure all embeddings are 1024-D format
   - **Prerequisite**: Must complete before Gate 2 (need >1000 embeddings for IVFFlat)

2. **Gate 2** (RAG Performance) — **MANDATORY**:
   - Create IVFFlat index (migration 049) — execute immediately after Gate 1
   - Add TSVECTOR + GIN index for full-text search (hybrid RAG)
   - Verify hybrid search performance (faster than `ILIKE`)
   - **Purpose**: Enable real-time RAG queries for Phase 15

3. **Gate 3** (KB Registry Curation) — **FINAL STEP**:
   - Revert KB registry to curated subset (~100-200 docs)
   - Filter by `kb_candidate=true` + manually curated high-importance docs
   - Generate small PM-facing artifacts (<50KB JSON, concise Markdown)
   - Verify share folder remains small and flat

4. **Resume Phase 15 Wave-3 Step 2**:
   - Now that infrastructure is complete, proceed with Full RAG Scoring logic
   - RAG engine can now query all 994 documents via pgvector
   - KB registry provides curated planning index for PM

---

## 5. Current State Assessment

### Schema Status:
- ✅ `control.doc_fragment.meta` JSONB column exists (migration 048)
- ✅ GIN index on `meta` exists
- ✅ `control.doc_embedding` table exists (migration 047)
- ❌ IVFFlat index status: **Unknown** (needs verification)
- ❌ TSVECTOR column: **Missing** (needs implementation)

### Data Status:
- ✅ 994 documents in `control.doc_registry`
- ❌ 987 documents without fragments (need fragmentation)
- ✅ 7 documents with fragments (PDFs)
- ❌ AI classification incomplete (only PDFs classified)

### KB Registry Status:
- ❌ Currently contains all 994 documents (too large)
- ❌ Not filtered by `kb_candidate=true`
- ❌ Share folder contains 808KB registry (too large)

---

## 6. Related Documentation

- **Layer 3 Plan**: `docs/SSOT/LAYER3_AI_DOC_INGESTION_PLAN.md`
- **Phase 15 Wave-3**: `docs/SSOT/PHASE15_WAVE3_PLAN.md`
- **PM Share Layout**: `docs/SSOT/PM_SHARE_LAYOUT_PHASE15.md`
- **Doc Content Vector Plan**: `docs/SSOT/DOC_CONTENT_VECTOR_PLAN.md`

---

## 7. Notes

- This is a **refinement**, not a restart — builds on existing Layer 3 infrastructure
- DMS remains SSOT — all changes are additive to existing schema
- Share folder remains a render target — no new SSOT artifacts
- RAG capability requires all documents in pgvector — this is mandatory for Phase 15

---

---

## 8. PM Directive

**Architectural Directive:**

The PM must generate OPS instructions for the **sequential execution of Gate 1 immediately**. This includes fragmenting the 987 missing documents, running the LLM classification under strict governance, and verifying 1024-D embedding creation. The PM should be warned that failing to implement the required indexing (Gate 2) will result in a **fatal performance bottleneck** when Phase 15 RAG scoring (Wave-3 Step 2) is resumed.

**Directive to the PM:**

The PM must immediately prioritize the **sequential execution** of Gates 1, 2, and 3 outlined in this document. Phase 15 Wave-3 Step 2 (Full Scoring) remains **CRITICALLY PAUSED** until the RAG infrastructure is stabilized by this ingestion and indexing work.

**Immediate Actions Required:**

1. **Gate 1 OPS Blocks** — **IMMEDIATE PRIORITY**:
   - Fragment the **987 missing documents**
   - Run **AI classification** with strict LLM governance (Metadata Classifier role, no generative text)
   - Ensure all LLM calls are logged in `control.agent_run`
   - Verify all embeddings are **1024-D format** (critical violation if 768-D used)
   - Verify all fragments have `meta` populated

2. **Gate 2 OPS Blocks** — **MANDATORY** (Execute immediately after Gate 1):
   - Create IVFFlat index (migration 049) — **immediately** after fragmentation (>1000 embeddings)
   - Implement TSVECTOR + GIN index for hybrid RAG (replaces slow `ILIKE`)
   - Verify hybrid search queries are **faster** than previous method
   - **⚠️ WARNING**: Skipping Gate 2 will cause fatal performance bottleneck in Phase 15 RAG

3. **Gate 3 OPS Blocks** — Final step (PM Usability):
   - Revert KB registry to curated subset (~100-200 docs)
   - Filter by `kb_candidate=true` + manually curated high-importance docs
   - Generate small PM-facing artifacts (<50KB JSON)
   - Verify share folder compliance (flat, Markdown-only)

**Governance Requirements:**

- **LLM Governance**: All LLM calls for classification must be logged in `control.agent_run`
  - System prompt must enforce "Metadata Classifier" role
  - Absolutely forbidden from generating interpretation or narrative text
  - Output must conform exactly to classification schema
- **Embedding Consistency**: All embeddings must use 1024-D format (dimensional unification)
  - Critical violation if legacy 768-D vectors are used
- **Indexing Mandates**: 
  - IVFFlat index must be created after >1000 embeddings exist
  - TSVECTOR + GIN index must be implemented for hybrid RAG
  - Performance verification required (faster than `ILIKE`)
- **Artifact Compliance**:
  - KB registry must be <50KB for PM consumption (down from 808KB)
  - Share folder must remain flat and Markdown-only

**Next Steps**: PM will prepare OPS blocks for each gate in sequence, pausing Phase 15 Wave-3 Step 2 until infrastructure is complete.

