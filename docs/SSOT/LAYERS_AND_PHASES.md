# Layers and Phases — SSOT Index

**Last Updated:** 2025-01-30
**Purpose:** Authoritative index of all Layer/Phase implementations and their states

## Layer 3: AI Document Ingestion

**Status:** ✅ COMPLETE (merged to main)

- **Phase 1: PDF Discovery** — ✅ COMPLETE
  - **Commit:** `080004a4` (feat(layer3-phase1): add PDF discovery to doc ingestion pipeline)
  - **Artifact:** `scripts/governance/ingest_docs_to_db.py` (PDF discovery logic)
  - **State:** Merged to main

- **Phase 2: PDF Fragmentation** — ✅ COMPLETE
  - **Commit:** `ee4e8c12` (feat(layer3-phase2): add PDF content extraction to doc ingestion)
  - **Artifact:** `scripts/governance/ingest_doc_content.py` (PDF fragmentation logic)
  - **State:** Merged to main

- **Phase 3: AI Classification** — ✅ COMPLETE
  - **Commit:** `3f055af7` (feat(layer3-phase3): add AI classification metadata to document fragments)
  - **Artifacts:** 
    - `pmagent/kb/classify.py` (classification module)
    - `scripts/governance/classify_fragments.py` (runner)
    - `migrations/048_add_fragment_meta_column.sql` (schema)
  - **State:** Merged to main

- **Phase 4: KB Registry Build** — ✅ COMPLETE
  - **Artifact:** `share/kb_registry.json` (generated from DMS)
  - **Builder:** `scripts/kb/build_kb_registry.py`
  - **State:** Generated and committed to main

## Layer 4: Code Ingestion & Embeddings

**Status:** ✅ COMPLETE (merged to main)

- **Phase 1: Code Discovery** — ✅ COMPLETE (merged, commit 181675ef)
  - **Artifact:** `share/code_registry.json` (919 Python files)
  - **State:** Merged to main

- **Phase 2: Fragmentation** — ✅ COMPLETE (merged, commit 2bd52ecb)
  - **Artifact:** `share/code_fragments.json` (3,749 fragments)
  - **State:** Merged to main

- **Phase 3: Classification** — ✅ COMPLETE (merged, commit eccda205)
  - **Artifact:** `share/code_fragments_classified.json` (3,749 tagged fragments)
  - **State:** Merged to main

- **Phase 4: Embedding** — ✅ COMPLETE (commit 9294df56)
  - **Artifact:** `share/code_fragments_embedded.json` (3,749 fragments with 1024-D vectors)
  - **State:** Merged to main, schema-compliant

- **Phase 5: Export** — ✅ COMPLETE (commit ed04a74d)
  - **Artifact:** `scripts/code_ingest/export_code_fragments.py` (3,748 fragments exported to control-plane)
  - **State:** Merged to main, 1024-D embeddings verified

## Notes

- **Only merged features count as COMPLETE**
- Layer 4 work must be reviewed from stash before integration
- Stash location: `git stash show stash@{0}` on `feature/layer3-ai-doc-ingestion`
- SSOT plan document: `docs/SSOT/LAYER4_CODE_INGESTION_PLAN.md` (aspirational, not implemented)
