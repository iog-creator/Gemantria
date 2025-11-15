# BibleScholar → AgentPM Migration Plan (Phase-6L)

**Status:** Draft  
**Owner:** PM (ChatGPT) + Orchestrator (human)  
**Last updated:** 2025-11-15T11:06:09Z

---

## 1. Purpose & Scope

This document maps **BibleScholarProjectClean** (Flask/Jinja + API + database layer) into the **unified Gemantria.v2 / AgentPM OS** described in RFC-081. It provides a clear migration path that:

- Identifies which BibleScholar features map to which AgentPM modules
- Classifies dependencies (read-only, DB-backed, LM-backed)
- Defines the order of operations for migration
- Preserves the **BibleScholar rule**: biblical answers come from the DB, LMs only summarize/format

**This phase is design-only** — no runtime behavior changes, just documentation and planning.

---

## 2. Inputs & Reference Repos

### Source Systems

- **`BibleScholarProjectClean`** — Flask/Jinja web UI + REST API + PostgreSQL database layer
  - Location: `/home/mccoy/Projects/BibleScholarProjectClean`
  - Key components: API endpoints, database models, vector search, lexicon lookups, contextual insights
  - Database: `bible_db` (PostgreSQL 16.6 with pgvector)

- **`Gemantria.v2`** — Control-plane, Gematria numerics, LM governance, unified UI foundation
  - Location: `/home/mccoy/Projects/Gemantria.v2`
  - Key components: AgentPM modules, control-plane schema, exports, React UI foundation

- **`StoryMaker`** — UI patterns and flows (for later integration)

### Reference Documents

- `docs/SSOT/BIBLESCHOLAR_INTAKE.md` — Feature inventory from BibleScholarProjectClean
- `docs/SSOT/AGENTPM_GEMATRIA_MODULE_PLAN.md` — Gematria module extraction plan
- `docs/rfcs/RFC-081-unified-ui-and-biblescholar-module.md` — Unification architecture
- `docs/projects/biblescholar/ARCHITECTURE.md` — BibleScholar system architecture
- `agentpm/biblescholar/AGENTS.md` — Current BibleScholar module status
- `GEMATRIA_MASTER_REFERENCE_v2.md` — Master reference for Gemantria system

---

## 3. Current State Snapshot

### What We Have Now (AgentPM/BibleScholar)

**Phase-6J (COMPLETE):** `agentpm/biblescholar/gematria_adapter.py`
- Read-only adapter for phrase-level Gematria computation
- Calls `agentpm.modules.gematria.core` and `agentpm.modules.gematria.hebrew`
- Returns `GematriaPhraseResult` dataclass
- Supports `mispar_hechrachi` and `mispar_gadol` systems

**Phase-6K (COMPLETE):** `agentpm/biblescholar/gematria_flow.py`
- Read-only verse-level flow for Gematria computation
- Wraps `gematria_adapter` for whole verses
- Returns `VerseGematriaSummary` with multi-system support
- No DB writes, no control-plane mutations, no LM calls

### Gematria Module Status

**Core numerics** (`agentpm/modules/gematria/`):
- `core.py` — Mispar Hechrachi and Mispar Gadol implementations
- `hebrew.py` — Hebrew normalization (ADR-002 compliant) and letter extraction
- Tests: 31 tests covering both systems, edge cases, normalization

**Module responsibilities** (from `AGENTPM_GEMATRIA_MODULE_PLAN.md`):
- Gematria value calculation
- Hebrew text normalization
- Math verification (skeleton)
- Noun/term extraction (skeleton)
- OSIS reference parsing (skeleton)

---

## 4. BibleScholar Feature Inventory (Grouped)

Based on `BIBLESCHOLAR_INTAKE.md` and `ARCHITECTURE.md`, features are grouped into 6 buckets:

### 4.1 Core Bible DB + Reference Parsing

**BibleScholar modules:**
- `src/database/database.py` — Database connection and models
- `src/database/secure_connection.py` — Secure DB connection handling
- `src/utils/bible_reference_parser.py` — Parse Bible references (book:chapter:verse)
- `src/utils/load_bible_data.py` — Bible data loading utilities

**Features:**
- Verse lookup by reference (OSIS format)
- Book/chapter/verse parsing
- Multi-translation support (KJV, ASV, YLT, TAHOT)
- Database connection pooling and security

### 4.2 Search (Keyword + Vector)

**BibleScholar modules:**
- `src/api/search_api.py` — General search API
- `src/api/vector_search_api.py` — Semantic/vector search endpoints
- `src/api/comprehensive_search.py` — Comprehensive Bible search functionality

**Features:**
- Keyword search across verses
- Vector/semantic search using pgvector embeddings
- Multi-translation search
- Search result ranking and filtering

### 4.3 Lexicon / Word Studies

**BibleScholar modules:**
- `src/api/lexicon_api.py` — Lexicon/word lookup endpoints

**Features:**
- Hebrew lexicon lookup (Strong's numbers, definitions, morphology)
- Greek lexicon lookup (Strong's numbers, definitions, morphology)
- Word-level data from `bible.hebrew_ot_words` and `bible.greek_nt_words`
- Morphology code explanations

### 4.4 Contextual Insights & Cross-Language Views

**BibleScholar modules:**
- `src/api/contextual_insights_api.py` — Contextual insights endpoints
- `src/api/cross_language_api.py` — Cross-language (Hebrew/Greek) search

**Features:**
- AI-powered contextual analysis (DB-grounded, LM-formatted)
- Cross-references and related passages
- Hebrew/Greek word analysis within verse context
- Theological term identification

### 4.5 Gematria / Numerics

**BibleScholar modules:**
- (Not present in current BibleScholarProjectClean — this is new)

**AgentPM modules (COMPLETE):**
- `agentpm/biblescholar/gematria_adapter.py` — Phrase-level Gematria
- `agentpm/biblescholar/gematria_flow.py` — Verse-level Gematria flow

**Features:**
- Gematria computation for Hebrew phrases/verses
- Multi-system support (Mispar Hechrachi, Mispar Gadol)
- OSIS reference integration

### 4.6 LM-Driven Explanations (DB-Grounded)

**BibleScholar modules:**
- `src/database/langchain_integration.py` — LangChain integration for AI workflows
- `src/utils/lm_indicator_adapter.py` — **ALREADY INTEGRATED** (Phase-5)

**Features:**
- LM Studio integration for summarization/formatting
- Contextual insights generation (DB data → LM formatting)
- LM status indicators (via Gemantria control-plane exports)
- **Rule**: All biblical content comes from DB; LMs only format/summarize

---

## 5. Mapping Tables

### 5.1 Feature → AgentPM Module Mapping

| Feature Area | BibleScholar Today | AgentPM / Gemantria Target | Dependency Type | Phase Window |
|--------------|-------------------|----------------------------|-----------------|--------------|
| **Gematria verse views** | (Not present) | `agentpm/biblescholar/gematria_flow.compute_verse_gematria` | Read-only, Gematria core | **DONE (6K)** |
| **Gematria phrase computation** | (Not present) | `agentpm/biblescholar/gematria_adapter.compute_phrase_gematria` | Read-only, Gematria core | **DONE (6J)** |
| **Bible reference parsing** | `src/utils/bible_reference_parser.py` | Future `agentpm/biblescholar/reference_parser.py` | Pure function (no DB) | Phase-7A |
| **Verse lookup** | `src/database/database.py` (verse queries) | Future `agentpm/biblescholar/bible_db_adapter.py` | Bible DB RO | Phase-7B |
| **Lexicon lookup (Hebrew)** | `src/api/lexicon_api.py` | Future `agentpm/biblescholar/lexicon_adapter.py` | Bible DB RO | Phase-7C |
| **Lexicon lookup (Greek)** | `src/api/lexicon_api.py` | Future `agentpm/biblescholar/lexicon_adapter.py` | Bible DB RO | Phase-7C |
| **Keyword search** | `src/api/search_api.py` | Future `agentpm/biblescholar/search_flow.py` | Bible DB RO | Phase-7D |
| **Vector search** | `src/api/vector_search_api.py` | Control-plane Knowledge Slice + future BibleScholar search flow | DB + embeddings | Phase-7E |
| **Contextual insights** | `src/api/contextual_insights_api.py` | Future `agentpm/biblescholar/insights_flow.py` | DB + LM (DB-grounded) | Phase-8A |
| **Cross-language search** | `src/api/cross_language_api.py` | Future `agentpm/biblescholar/cross_language_flow.py` | DB + embeddings | Phase-8B |
| **LM status indicator** | `src/utils/lm_indicator_adapter.py` | `agentpm/lm_widgets/adapter.py` (Phase-5) | Control-plane exports | **DONE (Phase-5)** |

### 5.2 Data Contract / Dependency Classification

| Capability | Bible Source | AgentPM Data Source | Classification | Notes |
|-----------|-------------|---------------------|----------------|-------|
| **Verse text** | `bible_db.bible.verses` | Future `bible_db` adapter (RO) | **DB-ONLY** | Read-only access to `bible_db` |
| **Hebrew words** | `bible_db.bible.hebrew_ot_words` | Future `bible_db` adapter (RO) | **DB-ONLY** | Word-level Hebrew data |
| **Greek words** | `bible_db.bible.greek_nt_words` | Future `bible_db` adapter (RO) | **DB-ONLY** | Word-level Greek data |
| **Lexicon entries** | `bible_db.bible.hebrew_entries`, `bible_db.bible.greek_entries` | Future `bible_db` adapter (RO) | **DB-ONLY** | Strong's number lookups |
| **Gematria values** | (Computed) | `agentpm.modules.gematria.core` | **Pure function (no DB)** | Deterministic calculation |
| **Vector embeddings** | `bible_db.bible.verse_embeddings` | Control-plane Knowledge Slice or direct `bible_db` RO | **DB + embeddings** | Semantic search |
| **LM explanations** | LM Studio via BibleScholar | Control-plane tracked LM calls | **LM-backed, DB-grounded** | DB data → LM formatting only |
| **LM status** | Gemantria control-plane | `share/atlas/control_plane/lm_indicator.json` | **Control-plane exports** | Already integrated (Phase-5) |

---

## 6. Migration Phases & Order of Operations

### Phase 6 (COMPLETE): Gematria Foundation

- **6G-6H**: Gematria module skeleton + first real numerics (Mispar Hechrachi)
- **6I**: Expanded numerics coverage (Mispar Gadol)
- **6J**: BibleScholar Gematria adapter (read-only)
- **6K**: BibleScholar Gematria verse flow (read-only)
- **6L**: This design document

### Phase 7: Core Bible DB Integration

**7A: Bible Reference Parsing** (Next candidate)
- Extract `bible_reference_parser.py` logic
- Create `agentpm/biblescholar/reference_parser.py`
- Pure function, no DB dependency
- OSIS format support

**7B: Bible DB Read-Only Adapter**
- Create `agentpm/biblescholar/bible_db_adapter.py`
- Read-only access to `bible_db` database
- Verse lookup by OSIS reference
- Multi-translation support (KJV, ASV, YLT, TAHOT)
- Connection pooling and security

**7C: Lexicon Adapter**
- Create `agentpm/biblescholar/lexicon_adapter.py`
- Hebrew lexicon lookup (Strong's numbers)
- Greek lexicon lookup (Strong's numbers)
- Word-level data retrieval
- Morphology code explanations

**7D: Keyword Search Flow**
- Create `agentpm/biblescholar/search_flow.py`
- Keyword search across verses
- Multi-translation search
- Result ranking and filtering
- Uses `bible_db_adapter` (read-only)

**7E: Vector Search Integration**
- Integrate with control-plane Knowledge Slice
- Or create direct `bible_db` vector search adapter
- Semantic similarity search
- Embedding-based verse retrieval

### Phase 8: Advanced Features

**8A: Contextual Insights Flow**
- Create `agentpm/biblescholar/insights_flow.py`
- DB-grounded contextual analysis
- LM formatting (via control-plane)
- Cross-references and related passages
- **Rule**: All content from DB; LM only formats

**8B: Cross-Language Flow**
- Create `agentpm/biblescholar/cross_language_flow.py`
- Hebrew/Greek word analysis within verse context
- Cross-language search capabilities
- Uses lexicon adapter + vector search

### Phase 9: UI Integration (Separate Episode)

- Harvest Flask/Jinja UI patterns into React
- Create unified UI pages for BibleScholar features
- Integrate with existing `webui/graph` foundation
- Multi-translation support in UI
- Search interfaces, lexicon views, contextual insights panels

---

## 7. Design Principles & Constraints

### 7.1 BibleScholar Rule (Preserved)

**All biblical answers must come only from the `bible_db` database.**

- LLMs (including LM Studio) may only summarize, paraphrase, or format results from the database
- LLMs must **never** generate biblical content directly or use their own knowledge
- If the answer is not in the database, the system must respond: "Sorry, I can only answer using the Bible database. No answer found for your query."

This rule is enforced in all API endpoints, web UI, and LLM/system prompts.

### 7.2 Read-Only Adapters

All BibleScholar adapters in AgentPM are **read-only**:
- No database writes to `bible_db` (it's SSOT, read-only)
- No control-plane mutations (use control-plane exports for status)
- Pure functions where possible (Gematria, reference parsing)
- DB-backed where necessary (verse lookup, lexicon, search)

### 7.3 UI Unification

- **No new Flask/Jinja surfaces** — all UI work targets unified React app
- Existing Flask/Jinja panels are **reference implementations** to be harvested
- UI will be the unified React/Tailwind app (generalized `webui/graph`)
- BibleScholar features surface through React components, not separate web frameworks

### 7.4 Control-Plane Integration

- LM calls tracked via Gemantria control-plane
- LM status indicators via `lm_indicator.json` exports (already integrated)
- Knowledge Slice for vector search (if applicable)
- No direct LM Studio calls from BibleScholar adapters (go through control-plane)

---

## 8. Non-Goals / Out-of-Scope (for Phase-6L)

- **No live DB wiring** — that comes in Phase-7B when we intentionally turn on `bible_db` access
- **No changes to LM Studio routing** — control-plane handles this
- **No React work** — that's a separate UI episode (Phase-9)
- **No control-plane schema changes** — existing schema supports BibleScholar needs
- **No migration of Flask/Jinja UI code** — only harvesting patterns, not porting code

---

## 9. Risks & Open Questions

### 9.1 Database Access

**Question:** How to stage DB migrations for `bible_db` access?

**Considerations:**
- `bible_db` is read-only SSOT — no writes allowed
- Need connection pooling and security (see `secure_connection.py`)
- May need DSN configuration similar to `BIBLE_DB_DSN` in Gemantria
- Consider adapter pattern to abstract DB access

**Risk:** Direct DB access from AgentPM modules could bypass control-plane governance.

**Mitigation:** Use read-only adapters with explicit contracts; no writes possible.

### 9.2 UI Complexity

**Question:** How to surface complex BibleScholar queries through the unified UI without overwhelming non-expert users?

**Considerations:**
- BibleScholar has advanced features (cross-language search, morphology analysis)
- Unified UI should be approachable for medium-tech users
- May need progressive disclosure (basic → advanced features)
- Consider role-based feature visibility

**Risk:** UI becomes too complex or too simple, missing the target audience.

**Mitigation:** Start with core features (verse lookup, basic search), add advanced features incrementally.

### 9.3 Vector Search Integration

**Question:** Should vector search use control-plane Knowledge Slice or direct `bible_db` access?

**Considerations:**
- BibleScholar has its own `verse_embeddings` table in `bible_db`
- Control-plane Knowledge Slice may have different embeddings
- May need adapter to bridge between systems
- Or create unified embedding strategy

**Risk:** Duplicate embedding storage and inconsistent search results.

**Mitigation:** Evaluate embedding models and dimensions; consider unified approach.

### 9.4 LM Integration Pattern

**Question:** How should contextual insights flow through control-plane LM tracking?

**Considerations:**
- BibleScholar rule: DB-grounded, LM-formatted
- Control-plane tracks LM calls and budgets
- Need to ensure LM calls are properly logged
- May need adapter between BibleScholar flows and control-plane LM service

**Risk:** LM calls bypass control-plane tracking.

**Mitigation:** Use control-plane LM service wrapper; no direct LM Studio calls from adapters.

---

## 10. Next Steps

### Immediate (Phase-6L Complete)

1. ✅ Review and approve this migration plan
2. ✅ Mark Phase-6L "DESIGN COMPLETE"
3. ⏭️ Define Phase-7A (Bible reference parsing) implementation tasks

### Phase-7A Planning

**First implementation episode:**
- Extract `bible_reference_parser.py` logic
- Create `agentpm/biblescholar/reference_parser.py`
- Pure function, no DB dependency
- OSIS format parsing and validation
- Tests covering edge cases

**Success criteria:**
- Reference parser module exists and is tested
- OSIS format fully supported
- No DB dependencies
- Documented in `agentpm/biblescholar/AGENTS.md`

---

## 11. References

- `docs/SSOT/BIBLESCHOLAR_INTAKE.md` — Feature inventory
- `docs/SSOT/AGENTPM_GEMATRIA_MODULE_PLAN.md` — Gematria module plan
- `docs/rfcs/RFC-081-unified-ui-and-biblescholar-module.md` — Unification RFC
- `docs/projects/biblescholar/ARCHITECTURE.md` — BibleScholar architecture
- `agentpm/biblescholar/AGENTS.md` — Current module status
- `schemas/biblescholar/SCHEMA_INDEX.md` — BibleScholar database schema documentation
- `GEMATRIA_MASTER_REFERENCE_v2.md` — Master reference

---

**Document Status:** Draft — Awaiting PM review and approval

