# Phase-6 — LM Studio Live Usage + DB-Backed Knowledge

Status: PLANNING  
Scope: Enable LM Studio for real tasks under guardrails and begin using Postgres as the canonical knowledge spine  
Upstream Dependencies: Phase-5 complete on `main` (LM indicator widget contract + StoryMaker/BibleScholar integration)

## Objective

Move from "wired but off" to **real LM Studio usage** for selected features under strict guardrails, and establish Postgres as the canonical knowledge spine for downstream apps.

## Deliverables

### 6A — LM Studio Live Usage Enablement

**Objective**: Move from "wired but off" to **real LM Studio usage** for selected features under strict guardrails.

**Deliverables**:
- Config flag: `LM_STUDIO_ENABLED=true|false` ✅
- Routing logic: LM Studio handles specific features when enabled; otherwise fallback ✅
- Guarded call wrapper (`guarded_lm_call()`): ✅
  - call_site tracking
  - token usage (via control-plane logging)
  - latency (via control-plane logging)
  - success/failure (via control-plane logging)
  - logged into control-plane
- First LM-enabled feature: `agentpm/runtime/lm_helpers.generate_text()` ✅
  - Simple text generation helper that demonstrates LM Studio enablement
  - Can be used by downstream apps (StoryMaker, BibleScholar) or internal features
  - Respects `LM_STUDIO_ENABLED` flag with graceful fallback

**Tests**:
- LM Studio enabled + unreachable (fallback)
- LM Studio disabled (must not call)
- Budget exhaustion
- Logging correctness

---

### 6B — LM Usage Budgets & Rate-Tracking

**Objective**: Prevent runaway usage; enforce app-level LM budgets.

**Deliverables**:
- New table: `control.lm_usage_budget` ✅ (migration 042)
- Budget checks before LM calls ✅ (`check_lm_budget()` in `agentpm/runtime/lm_budget.py`)
- Automatic fallback when exceeded ✅ (wired into `guarded_lm_call()`, returns "budget_exceeded" mode)
- Export: `lm_budget_7d.json` ✅ (`scripts/db/control_lm_budget_export.py`, `make atlas.lm.budget`)
- Atlas dashboard for budgets (future work)

**Tests**:
- Budget exhaustion scenarios
- Budget resets
- Hermetic tests

---

### 6C — Minimal Postgres Knowledge Slice ("Knowledge v0")

**Objective**: Add the first DB-backed knowledge structure.

**Deliverables**:
- New schema: `knowledge` ✅ (migration 043)
- Tables:
  - `kb_document` (uuid, title, section, slug, body_md, tags[]) ✅
  - `kb_embedding` (doc_id → vector pgvector[1024]) ✅
- ETL ingestion script (markdown → DB) ✅ (`scripts/db/control_kb_ingest.py`)
  - Parses markdown files from `docs/knowledge_seed/` (or custom directory)
  - Extracts title (H1 or filename), section (parent directory), slug
  - UPSERTs into `knowledge.kb_document` (idempotent)
  - db_off-safe (fails gracefully with clear message)
- Export script ✅ (`scripts/db/control_kb_export.py`)
  - Exports subset of KB docs (LIMIT 50) to `share/atlas/control_plane/kb_docs.head.json`
  - Includes: id, title, section, slug, tags, preview (first 200 chars), created_at
  - db_off-safe (emits empty list when DB unavailable)
- Make targets:
  - `make atlas.kb.ingest` ✅
  - `make atlas.kb.export` ✅

**Tests**:
- ETL hermetic tests ✅ (`agentpm/tests/knowledge/test_kb_ingest_and_export.py`)
  - db_off handling (fail-soft, exit 0)
  - Export JSON structure validation
  - Slug generation and title extraction utilities
- db_off-safe mode using cached artifacts ✅

---

### 6J — BibleScholar Gematria Adapter (Read-Only)

**Objective**: Provide read-only access to Gematria numerics for BibleScholar.

**Status**: ✅ **COMPLETE** (2025-11-15)

**Deliverables**:
- `agentpm/biblescholar/gematria_adapter.py` — Read-only adapter for Gematria numerics
- Mispar Hechrachi and Mispar Gadol support
- DB-off mode handling (graceful degradation)

---

### 6M — Bible DB Read-Only Adapter + Passage Flow

**Objective**: Provide read-only access to bible_db for verse/passage retrieval.

**Status**: ✅ **COMPLETE** (2025-11-15)

**Deliverables**:
- `agentpm/biblescholar/bible_db_adapter.py` — Read-only adapter for `bible_db`
- `agentpm/biblescholar/bible_passage_flow.py` — Passage/verse retrieval flow
- Verse lookup by book/chapter/verse (reference string parsing)
- Multi-translation support (KJV default, extensible)
- DB-off mode handling (graceful degradation)

---

### 6O — Vector Similarity Adapter + Verse-Similarity Flow

**Objective**: Provide read-only vector similarity for finding similar verses.

**Status**: ✅ **COMPLETE** (2025-11-15, PR #557)

**Deliverables**:
- `agentpm/biblescholar/vector_adapter.py` — Vector similarity adapter (pgvector)
- `agentpm/biblescholar/vector_flow.py` — Verse-similarity flow wrapper
- Read-only vector similarity using pgvector cosine distance
- DB-off mode handling (graceful degradation)

---

### 6P — BibleScholar Reference Answer Slice

**Objective**: Single E2E BibleScholar interaction using LM Studio (guarded), bible_db (read-only), Gematria adapter, and optional knowledge slice.

**Status**: ✅ **COMPLETE** (2025-11-15, PR #560)

**Deliverables**:
- `agentpm/biblescholar/reference_slice.py` — `answer_reference_question()` orchestrates complete E2E flow
- Resolves verse context from bible_db (read-only)
- Retrieves Gematria patterns for Hebrew text
- Optionally finds similar verses using vector similarity
- Calls LM Studio via `guarded_lm_call()` with budget enforcement and provenance
- Returns structured `ReferenceAnswerResult` with answer, trace, context_used, and lm_meta

**Tests**:
- `agentpm/biblescholar/tests/test_reference_slice.py` (5/5 passing)
  - Happy path: All adapters + LM succeed
  - db_off scenario: DB unavailable, graceful degradation
  - budget_exceeded: LM budget exhausted, handled gracefully
  - Question-only: No verse reference provided
  - Verse without Hebrew: No Gematria patterns

**Constraints Met**:
- ✅ No new DSNs (uses existing adapters)
- ✅ DB-off hermetic mode (graceful degradation)
- ✅ Budget enforcement (via guarded_lm_call)
- ✅ Provenance required (LM metadata in result)
- ✅ Read-only adapters only

**Dependencies**: 6J, 6M, 6O, 6A, 6B, 6C (all COMPLETE)

---

### 6D — Downstream App Read-Only Wiring

**StoryMaker**:
- `useKnowledgeSlice()` hook
- Replace selected hardcoded metadata with DB-backed knowledge
- Tests: React with mocked KB responses

**BibleScholar**:
- KB client for lookup of canonical metadata
- Replace selected lookup logic with DB data

**Shared**:
- Apps MUST NOT query Postgres directly
- All reads go through a Gemantria-owned API or CLI wrapper

---

### 6E — Governance & SSOT Updates

**Deliverables**:
- Update MASTER_PLAN
- Update AGENTS.md
- Update CHANGELOG.md
- Rule: Downstream apps may not implement LM heuristics or DB logic without a Gemantria-owned module.

## PR Staging for Phase-6

**PR #1 (this PR)**:
- Add PHASE_6_PLAN.md
- Update MASTER_PLAN, AGENTS, CHANGELOG

**PR #2**:
- LM Studio enablement (6A)

**PR #3**:
- LM budget enforcement (6B)

**PR #4**:
- Knowledge slice schema + ETL (6C)

**PR #5**:
- StoryMaker DB wiring (6D)

**PR #6**:
- BibleScholar DB wiring (6D)

