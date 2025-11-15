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

### 6D — Downstream App Read-Only Wiring

**Step 1: Gemantria-side adapter (✅ COMPLETE)**:
- Knowledge adapter module ✅ (`agentpm/knowledge/adapter.py`)
  - Reads `kb_docs.head.json` (hermetic, file-only)
  - Returns typed widget props for downstream apps
  - Fail-closed (offline-safe defaults)
- KB widget contract ✅ (`docs/SSOT/KB_WIDGETS.md`)
  - Documents JSON→props contract
  - Adapter rules (hermetic, read-only, file-based)
- Tests ✅ (`agentpm/tests/knowledge/test_kb_adapter.py`)
  - Happy path, missing file, malformed JSON, empty docs

**Step 2: StoryMaker integration** (📘 PLANNING):
- `useKnowledgeSlice()` hook
- Replace selected hardcoded metadata with DB-backed knowledge
- Tests: React with mocked KB responses

**Step 3: BibleScholar integration** (📘 PLANNING):
- KB client for lookup of canonical metadata
- Replace selected lookup logic with DB data

**Shared**:
- Apps MUST NOT query Postgres directly
- All reads go through Gemantria-owned adapter (`load_kb_docs_widget_props()`)

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

