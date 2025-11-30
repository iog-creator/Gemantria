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
    - `agentpm/kb/classify.py` (classification module)
    - `scripts/governance/classify_fragments.py` (runner)
    - `migrations/048_add_fragment_meta_column.sql` (schema)
  - **State:** Merged to main

- **Phase 4: KB Registry Build** — ✅ COMPLETE
  - **Artifact:** `share/kb_registry.json` (generated from DMS)
  - **Builder:** `scripts/kb/build_kb_registry.py`
  - **State:** Generated and committed to main

## Layer 4: Code Ingestion & Embeddings

**Status:** 🔄 STASHED (not merged)

- **Phase 4.1: Code Discovery** — 🔄 STASHED
  - **Location:** `stash@{0}` on `feature/layer3-ai-doc-ingestion`
  - **Artifact:** `scripts/governance/ingest_docs_to_db.py` (with `iter_code_files()`)
  - **State:** WIP, not merged

- **Phase 4.2: Code Fragmentation** — 🔄 STASHED
  - **Location:** `stash@{0}` on `feature/layer3-ai-doc-ingestion`
  - **Artifact:** `scripts/governance/ingest_doc_content.py` (with `chunk_python_code()`, `chunk_typescript_code()`)
  - **State:** WIP, not merged

- **Phase 4.3: Code Embeddings** — 🔄 STASHED
  - **Location:** `stash@{0}` on `feature/layer3-ai-doc-ingestion`
  - **Note:** Reuses existing embedding pipeline
  - **State:** WIP, not merged

- **Phase 4.4: Code Classification** — 🔄 STASHED
  - **Location:** `stash@{0}` on `feature/layer3-ai-doc-ingestion`
  - **Artifact:** `agentpm/kb/classify.py` (with `classify_code_fragment()`)
  - **State:** WIP, not merged

- **Phase 4.5: KB Registry & Search** — 🔄 STASHED
  - **Location:** `stash@{0}` on `feature/layer3-ai-doc-ingestion`
  - **Artifacts:** 
    - `agentpm/kb/search.py` (semantic code search)
    - `pmagent/cli.py` (with `pmagent kb search` command)
  - **State:** WIP, not merged

## Notes

- **Only merged features count as COMPLETE**
- Layer 4 work must be reviewed from stash before integration
- Stash location: `git stash show stash@{0}` on `feature/layer3-ai-doc-ingestion`
- SSOT plan document: `docs/SSOT/LAYER4_CODE_INGESTION_PLAN.md` (aspirational, not implemented)
