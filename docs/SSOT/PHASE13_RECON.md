# Phase 13 Reconciliation — Vector Unify (SSOT)

## Purpose

This document records the reconciliation status of **Phase 13: Vector Unify**.

Goal of Phase 13:

- Unify all embeddings on **1024-dimensional vectors** (BGE-M3 compatible).

- Ensure the **doc_embedding pipeline** and related scripts operate consistently at 1024-D.

- Retire legacy 768-D embeddings and schema.

This file answers: **"Does current `main` already satisfy the Phase 13 contract?"**

---

## 1. DB Schema Evidence

### Table: control.doc_embedding

- Column: `embedding`

- Type: `vector(1024)` ✅

- Foreign key: `doc_fragment_id` → `control.doc_fragment`

- Indexes present for performance.

Conclusion:

- The database schema is aligned with Phase 13's 1024-D requirement.

---

## 2. Pipeline & Script Evidence

### scripts/code_ingest/embed_code_fragments.py

- Uses constant: `VECTOR_DIM = 1024` ✅

- Generates 1024-D embeddings for code fragments.

- Comments and logic explicitly reference 1024-D behavior.

### scripts/code_ingest/export_code_fragments.py

- Validates that embeddings are 1024-D before export ✅

- Knows about `control.doc_embedding` and its 1024-D requirement.

### scripts/governance/ingest_doc_embeddings.py

- Handles model-specific behavior (e.g., 768-D granite model).

- Implements **padding** from 768 → 1024 when needed.

- Emits warnings when dimensions mismatch expectations.

- Assumes DB schema expects `vector(1024)`.

### scripts/pipeline_orchestrator.py

- Embeddings backfill defaults: `dim: int = 1024` ✅

---

## 3. Migration Evidence

### Migration: 053_drop_verses_embedding_768.sql

- Drops old 768-D embedding storage.

- Confirms the design intent to move to a unified 1024-D embedding space.

Conclusion:

- The system has explicitly removed legacy 768-D paths in favor of 1024-D.

---

## 4. Contract Checklist

Phase 13 contract items:

1. **DB schema uses 1024-D vectors**  

   - ✅ `control.doc_embedding.embedding` is `vector(1024)`

2. **Embedding pipelines generate 1024-D vectors**  

   - ✅ `embed_code_fragments.py` uses `VECTOR_DIM = 1024`

   - ✅ `ingest_doc_embeddings.py` handles 768→1024 padding

3. **Export and validation expect 1024-D**  

   - ✅ `export_code_fragments.py` enforces 1024-D

4. **Legacy 768-D embeddings removed/deprecated**  

   - ✅ Migration 053 dropped 768-D storage

   - ✅ Warnings and code paths assume 1024-D schema

5. **Orchestrator and ops scripts aligned to 1024-D**  

   - ✅ `pipeline_orchestrator.py` defaults to 1024

---

## 5. Conclusion

**Phase 13 vector-unify requirements are fully satisfied on `main`.**

Therefore:

- The old Phase 13 PR **#585 — feat/phase13-vector-unify** is now **superseded by `main`**.

- Merging PR #585 as-is would be:

  - Redundant at best.

  - Potentially harmful due to conflicts and outdated assumptions.

**Recommended action:**

- Close PR #585 in GitHub with a note similar to:

  > "Closing as superseded. Phase 13 vector-unify requirements (1024-D doc embeddings and unified pipeline) are fully implemented on `main`. See `docs/SSOT/PHASE13_RECON.md` for evidence."

- Do **not** attempt to merge PR #585 into `main`.

---

## 6. Impact on Phase 15

- Phase 13 is no longer a hard blocker for Phase 15.

- Only **Phase 14 (relationship PoC)** remains as a true structural blocker that must be reconciled before Phase 15 RAG context work proceeds.

