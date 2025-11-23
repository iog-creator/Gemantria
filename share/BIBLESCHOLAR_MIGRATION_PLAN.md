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

### Schema Dumps (Primary Input)

**These schema files are the authoritative source for understanding BibleScholar's data model:**

- `schemas/biblescholar/bible_db_structure.sql` (930 lines)
  - Complete PostgreSQL database schema dump for `bible_db`
  - Includes all tables, indexes, constraints, foreign keys
  - Schema: `bible` (main schema) + `public` (LangChain tables)
  - PostgreSQL 16.6 with pgvector extension

- `schemas/biblescholar/bible_db_verses_structure.sql` (120 lines)
  - Focused schema for `bible.verses` table
  - Includes indexes and constraints specific to verses
  - Vector embedding index (HNSW) for `embedding vector(768)`

- `schemas/biblescholar/bible_db_versification_structure.sql` (94 lines)
  - Versification mapping table structure
  - Cross-reference system mappings (`bible.versification_mappings`)

- `schemas/biblescholar/SCHEMA_INDEX.md`
  - Comprehensive schema documentation
  - Table descriptions, field details, foreign key relationships
  - Vector embedding details (768 vs 1024 dimensions)
  - Integration notes for Gemantria.v2

- `share/schemas/SCHEMA_REGISTRY.md`
  - Cross-project schema registry
  - Context for GPT/AI agents across all sibling projects

**Note:** These schema dumps are the primary input for understanding BibleScholar's data model and designing adapter layers. Code files (`database.py`, API endpoints) are secondary references that implement access to these schemas.

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

## 3.5 Schema Analysis Summary

This section provides a bridge from "what exists" (Current State) to "how we'll map it" (Feature Inventory), using the schema dumps as the authoritative source.

### Database Overview

- **Database**: `bible_db` (PostgreSQL 16.6)
- **Extension**: `vector` (pgvector) for embeddings
- **Main schema**: `bible` (core tables)
- **Public schema**: LangChain integration tables (`langchain_pg_collection`, `langchain_pg_embedding`)

### Core Schema Structure

**Primary Tables:**
- `bible.books` — Bible book metadata (book_id, name, testament, chapters)
- `bible.verses` — Verse text storage (verse_id, book_name, chapter_num, verse_num, text, translation_source, embedding vector(768))
- `bible.book_abbreviations` — Book name abbreviations for reference parsing

**Word-Level Tables:**
- `bible.hebrew_ot_words` — Hebrew Old Testament words (word_id, verse_id, word_text, strongs_id, grammar_code, transliteration, gloss, theological_term)
- `bible.greek_nt_words` — Greek New Testament words (similar structure to Hebrew)

**Lexicon Tables:**
- `bible.hebrew_entries` — Hebrew lexicon entries (entry_id, strongs_id, lemma, transliteration, definition, usage, gloss)
- `bible.greek_entries` — Greek lexicon entries (similar structure)
- `bible.hebrew_morphology_codes` — Hebrew morphology definitions (code, description, part_of_speech, morphology_type)
- `bible.greek_morphology_codes` — Greek morphology definitions

**Vector Embeddings:**
- `bible.verses.embedding` — `vector(768)` stored directly in verses table (HNSW index)
- `bible.verse_embeddings` — Separate embeddings table with `vector(1024)` (IVFFlat index)
- `public.langchain_pg_embedding` — LangChain embeddings `vector(1024)`

**Relationship Tables:**
- `bible.verse_word_links` — Links between verses and words (verse_id, word_id, word_type)
- `bible.proper_names` — Proper name entries with relationships (unified_name, description, parents, siblings, etc.)
- `bible.versification_mappings` — Cross-reference mappings between traditions

### Foreign Key Relationships

```
bible.books (book_id)
  └── bible.verses (book_name → books.name)
       ├── bible.hebrew_ot_words (verse_id → verses.verse_id)
       ├── bible.greek_nt_words (verse_id → verses.verse_id)
       ├── bible.verse_embeddings (verse_id → verses.verse_id)
       └── bible.verse_word_links (verse_id → verses.verse_id)
```

### Key Constraints & Indexes

- **Unique constraint on verses**: `(book_name, chapter_num, verse_num, translation_source)`
- **Unique constraint on Hebrew entries**: `strongs_id`
- **Vector indexes**: HNSW for `verses.embedding` (768-dim), IVFFlat for `verse_embeddings.embedding` (1024-dim)
- **Word indexes**: Indexed on `verse_id` and `strongs_id` for fast lookups

### BibleScholar Rule (Schema-Enforced)

**All biblical answers must come from `bible_db`. LMs only summarize/format; they never invent content outside the DB.**

This rule is reflected in the schema design:
- All verse text stored in `bible.verses.text` (DB-only source)
- All word-level data in `bible.hebrew_ot_words` and `bible.greek_nt_words` (DB-only source)
- All lexicon definitions in `bible.hebrew_entries` and `bible.greek_entries` (DB-only source)
- LangChain tables (`public.langchain_pg_*`) are for embeddings storage, not content generation
- No computed or generated fields in the schema — all content is stored, not synthesized

### Vector Dimension Considerations

- **Two embedding dimensions**: 768 (verses.embedding) and 1024 (verse_embeddings, langchain)
- **Different index types**: HNSW for 768-dim, IVFFlat for 1024-dim
- **Integration challenge**: Gemantria.v2 uses 1024-dim embeddings; may need dimension alignment or adapter layer

---

## 4. BibleScholar Feature Inventory (Grouped)

Based on `BIBLESCHOLAR_INTAKE.md` and `ARCHITECTURE.md`, features are grouped into 6 buckets:

### 4.1 Core Bible DB + Reference Parsing

**Schema Tables:**
- `bible.verses` — Primary verse storage (verse_id, book_name, chapter_num, verse_num, text, translation_source, embedding vector(768))
- `bible.books` — Book metadata (book_id, name, testament, chapters)
- `bible.book_abbreviations` — Book name abbreviations (book_name, abbreviation, source)

**BibleScholar modules:**
- `src/database/database.py` — Database connection and models
- `src/database/secure_connection.py` — Secure DB connection handling
- `src/utils/bible_reference_parser.py` — Parse Bible references (book:chapter:verse)
- `src/utils/load_bible_data.py` — Bible data loading utilities

**Features:**
- Verse lookup by reference (OSIS format) → queries `bible.verses` by (book_name, chapter_num, verse_num, translation_source)
- Book/chapter/verse parsing → uses `bible.books` and `bible.book_abbreviations`
- Multi-translation support (KJV, ASV, YLT, TAHOT) → `translation_source` column in `bible.verses`
- Database connection pooling and security

### 4.2 Search (Keyword + Vector)

**Schema Tables:**
- `bible.verses` — Keyword search on `text` column, vector search on `embedding vector(768)` (HNSW index)
- `bible.verse_embeddings` — Separate embeddings table with `embedding vector(1024)` (IVFFlat index) for semantic search

**BibleScholar modules:**
- `src/api/search_api.py` — General search API
- `src/api/vector_search_api.py` — Semantic/vector search endpoints
- `src/api/comprehensive_search.py` — Comprehensive Bible search functionality

**Features:**
- Keyword search across verses → full-text search on `bible.verses.text`
- Vector/semantic search using pgvector embeddings → similarity search on `bible.verses.embedding` (768-dim) or `bible.verse_embeddings.embedding` (1024-dim)
- Multi-translation search → filters by `translation_source` column
- Search result ranking and filtering

### 4.3 Lexicon / Word Studies

**Schema Tables:**
- `bible.hebrew_ot_words` — Hebrew word-level data (word_id, verse_id, word_text, strongs_id, grammar_code, transliteration, gloss, theological_term)
- `bible.greek_nt_words` — Greek word-level data (similar structure: word_id, verse_id, word_text, strongs_id, grammar_code, transliteration, gloss, theological_term)
- `bible.hebrew_entries` — Hebrew lexicon entries (entry_id, strongs_id, lemma, transliteration, definition, usage, gloss)
- `bible.greek_entries` — Greek lexicon entries (entry_id, strongs_id, lemma, transliteration, definition, usage, gloss)
- `bible.hebrew_morphology_codes` — Hebrew morphology definitions (code, description, part_of_speech, morphology_type)
- `bible.greek_morphology_codes` — Greek morphology definitions (code, description, part_of_speech, morphology_type)

**BibleScholar modules:**
- `src/api/lexicon_api.py` — Lexicon/word lookup endpoints

**Features:**
- Hebrew lexicon lookup (Strong's numbers, definitions, morphology) → queries `bible.hebrew_entries` by `strongs_id`, joins with `bible.hebrew_morphology_codes` for grammar explanations
- Greek lexicon lookup (Strong's numbers, definitions, morphology) → queries `bible.greek_entries` by `strongs_id`, joins with `bible.greek_morphology_codes`
- Word-level data from `bible.hebrew_ot_words` and `bible.greek_nt_words` → links to verses via `verse_id`, provides word position, transliteration, gloss
- Morphology code explanations → `bible.hebrew_morphology_codes` and `bible.greek_morphology_codes` provide detailed grammar descriptions

### 4.4 Contextual Insights & Cross-Language Views

**Schema Tables:**
- `bible.verse_word_links` — Links between verses and words (verse_id, word_id, word_type)
- `bible.proper_names` — Proper name entries with relationships (unified_name, description, parents, siblings, partners, offspring, tribe_nation, summary, type, etc.)
- `bible.versification_mappings` — Cross-reference mappings (source_tradition, source_book, source_chapter, source_verse, target_tradition, target_book, target_chapter, target_verse)

**BibleScholar modules:**
- `src/api/contextual_insights_api.py` — Contextual insights endpoints
- `src/api/cross_language_api.py` — Cross-language (Hebrew/Greek) search

**Features:**
- AI-powered contextual analysis (DB-grounded, LM-formatted) → uses `bible.verse_word_links` and `bible.proper_names` for context, LM only formats DB data
- Cross-references and related passages → queries `bible.versification_mappings` for cross-tradition references
- Hebrew/Greek word analysis within verse context → joins `bible.hebrew_ot_words` / `bible.greek_nt_words` with `bible.verses` via `verse_id`
- Theological term identification → uses `theological_term` column in `bible.hebrew_ot_words` and `bible.greek_nt_words`

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

**Schema Tables:**
- `public.langchain_pg_collection` — LangChain collection metadata
- `public.langchain_pg_embedding` — LangChain embeddings storage (vector(1024))

**BibleScholar modules:**
- `src/database/langchain_integration.py` — LangChain integration for AI workflows
- `src/utils/lm_indicator_adapter.py` — **ALREADY INTEGRATED** (Phase-5)

**Features:**
- LM Studio integration for summarization/formatting → LangChain tables store embeddings, but content comes from `bible` schema tables
- Contextual insights generation (DB data → LM formatting) → DB data from `bible.verses`, `bible.hebrew_ot_words`, `bible.greek_nt_words` is formatted by LM
- LM status indicators (via Gemantria control-plane exports) → `share/atlas/control_plane/lm_indicator.json`
- **Rule**: All biblical content comes from DB; LMs only format/summarize. LangChain tables are for embedding storage, not content generation.

---

## 5. Mapping Tables

### 5.1 Feature → AgentPM Module Mapping

| Feature Area | BibleScholar Today | AgentPM / Gemantria Target | Schema Tables | Dependency Type | Phase Window |
|--------------|-------------------|----------------------------|---------------|-----------------|--------------|
| **Gematria verse views** | (Not present) | `agentpm/biblescholar/gematria_flow.compute_verse_gematria` | (Computed, not stored) | Read-only, Gematria core | **DONE (6K)** |
| **Gematria phrase computation** | (Not present) | `agentpm/biblescholar/gematria_adapter.compute_phrase_gematria` | (Computed, not stored) | Read-only, Gematria core | **DONE (6J)** |
| **Bible reference parsing** | `src/utils/bible_reference_parser.py` | Future `agentpm/biblescholar/reference_parser.py` | `bible.books`, `bible.book_abbreviations` | Pure function (no DB) | Phase-7A |
| **Verse lookup** | `src/database/database.py` (verse queries) | Future `agentpm/biblescholar/bible_db_adapter.py` | `bible.verses` (verse_id, book_name, chapter_num, verse_num, text, translation_source) | Bible DB RO | Phase-7B |
| **Lexicon lookup (Hebrew)** | `src/api/lexicon_api.py` | Future `agentpm/biblescholar/lexicon_adapter.py` | `bible.hebrew_entries`, `bible.hebrew_ot_words`, `bible.hebrew_morphology_codes` | Bible DB RO | Phase-7C |
| **Lexicon lookup (Greek)** | `src/api/lexicon_api.py` | Future `agentpm/biblescholar/lexicon_adapter.py` | `bible.greek_entries`, `bible.greek_nt_words`, `bible.greek_morphology_codes` | Bible DB RO | Phase-7C |
| **Keyword search** | `src/api/search_api.py` | Future `agentpm/biblescholar/search_flow.py` | `bible.verses` (text column, translation_source filter) | Bible DB RO | Phase-7D |
| **Vector search** | `src/api/vector_search_api.py` | Control-plane Knowledge Slice + future BibleScholar search flow | `bible.verses.embedding` (vector(768)), `bible.verse_embeddings.embedding` (vector(1024)) | DB + embeddings | Phase-7E |
| **Contextual insights** | `src/api/contextual_insights_api.py` | Future `agentpm/biblescholar/insights_flow.py` | `bible.verse_word_links`, `bible.proper_names`, `bible.versification_mappings` | DB + LM (DB-grounded) | Phase-8A |
| **Cross-language search** | `src/api/cross_language_api.py` | Future `agentpm/biblescholar/cross_language_flow.py` | `bible.hebrew_ot_words`, `bible.greek_nt_words`, `bible.verse_word_links` | DB + embeddings | Phase-8B |
| **LM status indicator** | `src/utils/lm_indicator_adapter.py` | `agentpm/lm_widgets/adapter.py` (Phase-5) | (Control-plane exports, not bible_db) | Control-plane exports | **DONE (Phase-5)** |

### 5.2 Data Contract / Dependency Classification

**Core Rule:** All biblical answers must come from `bible_db`. LMs only summarize/format; they never invent content outside the DB.

| Capability | Bible Source (Schema) | AgentPM Data Source | Classification | Notes |
|-----------|----------------------|---------------------|----------------|-------|
| **Verse text** | `bible_db.bible.verses.text`, `bible_db.bible.verses.translation_source` | Future `bible_db` adapter (RO) | **DB-ONLY** | Read-only access to `bible.verses` table |
| **Hebrew words** | `bible_db.bible.hebrew_ot_words` (word_text, strongs_id, grammar_code, transliteration, gloss, theological_term) | Future `bible_db` adapter (RO) | **DB-ONLY** | Word-level Hebrew data, linked via verse_id |
| **Greek words** | `bible_db.bible.greek_nt_words` (word_text, strongs_id, grammar_code, transliteration, gloss, theological_term) | Future `bible_db` adapter (RO) | **DB-ONLY** | Word-level Greek data, linked via verse_id |
| **Lexicon entries** | `bible_db.bible.hebrew_entries.strongs_id`, `bible_db.bible.greek_entries.strongs_id` (lemma, transliteration, definition, usage, gloss) | Future `bible_db` adapter (RO) | **DB-ONLY** | Strong's number lookups, unique constraint on strongs_id |
| **Morphology codes** | `bible_db.bible.hebrew_morphology_codes`, `bible_db.bible.greek_morphology_codes` (code, description, part_of_speech, morphology_type) | Future `bible_db` adapter (RO) | **DB-ONLY** | Grammar explanations for morphology codes |
| **Gematria values** | (Computed, not stored) | `agentpm.modules.gematria.core` | **Pure function (no DB)** | Deterministic calculation from Hebrew text |
| **Vector embeddings** | `bible_db.bible.verses.embedding` (vector(768)), `bible_db.bible.verse_embeddings.embedding` (vector(1024)) | Control-plane Knowledge Slice or direct `bible_db` RO | **DB + embeddings** | Semantic search, dimension mismatch (768 vs 1024) |
| **Cross-references** | `bible_db.bible.versification_mappings` (source_tradition, source_book, source_chapter, source_verse, target_*) | Future `bible_db` adapter (RO) | **DB-ONLY** | Cross-tradition verse mappings |
| **Proper names** | `bible_db.bible.proper_names` (unified_name, description, relationships) | Future `bible_db` adapter (RO) | **DB-ONLY** | Proper name entries with contextual relationships |
| **LM explanations** | LM Studio via BibleScholar (DB-grounded) | Control-plane tracked LM calls | **LM-backed, DB-grounded** | DB data from `bible` schema → LM formatting only, never invents content |
| **LM status** | Gemantria control-plane | `share/atlas/control_plane/lm_indicator.json` | **Control-plane exports** | Already integrated (Phase-5) |

---

## 6. Migration Phases & Order of Operations

### Phase 6 (COMPLETE): Gematria Foundation

- **6G-6H**: Gematria module skeleton + first real numerics (Mispar Hechrachi)
- **6I**: Expanded numerics coverage (Mispar Gadol)
- **6J**: BibleScholar Gematria adapter (read-only)
- **6K**: BibleScholar Gematria verse flow (read-only)
- **6L**: This design document
- **6M**: Bible DB read-only adapter + passage flow (COMPLETE)
  - `agentpm/biblescholar/bible_db_adapter.py` — Read-only adapter for `bible_db`
  - `agentpm/biblescholar/bible_passage_flow.py` — Passage/verse retrieval flow
  - Verse lookup by book/chapter/verse (reference string parsing)
  - Multi-translation support (KJV default, extensible)
  - DB-off mode handling (graceful degradation)
  - Tests: `test_bible_db_adapter.py`, `test_bible_passage_flow.py`
- **6N**: Lexicon read-only adapter + word-study flow (COMPLETE)
  - `agentpm/biblescholar/lexicon_adapter.py` — Read-only adapter for lexicon tables
  - `agentpm/biblescholar/lexicon_flow.py` — Word-study retrieval flow
  - Hebrew/Greek lexicon lookup by Strong's number
  - Word-level data retrieval for verse references
  - Tables: `bible.hebrew_entries`, `bible.greek_entries`, `bible.hebrew_ot_words`, `bible.greek_nt_words`
  - DB-off mode handling (graceful degradation)
  - Tests: `test_lexicon_adapter.py`, `test_lexicon_flow.py`

### Phase 7: Core Bible DB Integration

**7A: Bible Reference Parsing** (✅ COMPLETE)
- ✅ Extract `bible_reference_parser.py` logic
- ✅ Create `agentpm/biblescholar/reference_parser.py`
- ✅ Pure function, no DB dependency
- ✅ OSIS format support
- ✅ Enhance `bible_passage_flow.parse_reference()` with OSIS support (Pending integration)

**7B: Bible DB Read-Only Adapter** (Partially complete via Phase-6M)
- ✅ `agentpm/biblescholar/bible_db_adapter.py` — COMPLETE (Phase-6M)
- ✅ `agentpm/biblescholar/bible_passage_flow.py` — COMPLETE (Phase-6M)
- 🔄 Enhanced reference parsing (OSIS format) — Phase-7A
- 🔄 Connection pooling and security — Future enhancement

**7C: Lexicon Adapter** (Partially complete via Phase-6N)
- ✅ `agentpm/biblescholar/lexicon_adapter.py` — COMPLETE (Phase-6N)
- ✅ `agentpm/biblescholar/lexicon_flow.py` — COMPLETE (Phase-6N)
- ✅ Hebrew/Greek lexicon lookup (Strong's numbers) — COMPLETE
- ✅ Word-level data retrieval — COMPLETE
- 🔄 Morphology code explanations — Future enhancement

**7D: Keyword Search Flow** (✅ COMPLETE)
- ✅ Create `agentpm/biblescholar/search_flow.py`
- ✅ Keyword search across verses (ILIKE)
- ✅ Multi-translation search
- ✅ Result ranking (ordered by book/chapter/verse) and filtering (limit)
- ✅ Uses `bible_db_adapter` (read-only)

**7E: Vector Search Integration** (Complete via Phase-6O)
- ✅ `agentpm/biblescholar/vector_adapter.py` — COMPLETE (Phase-6O)
- ✅ `agentpm/biblescholar/vector_flow.py` — COMPLETE (Phase-6O)
- ✅ Direct `bible_db` vector search adapter — COMPLETE
- ✅ Semantic similarity search using pgvector — COMPLETE
- ✅ Embedding-based verse retrieval — COMPLETE
- 🔄 Integration with control-plane Knowledge Slice — Future enhancement

### Phase 8: Advanced Features

**8A: Contextual Insights Flow** (✅ COMPLETE)
- ✅ Create `agentpm/biblescholar/insights_flow.py`
- ✅ DB-grounded contextual analysis (VerseContext aggregation)
- ✅ LM formatting (via `format_context_for_llm`)
- ✅ Cross-references and related passages (via vector search)
- ✅ **Rule**: All content from DB; LM only formats

**8B: Cross-Language Flow** (✅ COMPLETE)
- ✅ Create `agentpm/biblescholar/cross_language_flow.py`
- ✅ Hebrew/Greek word analysis within verse context
- ✅ Cross-language search capabilities (via vector similarity)
- ✅ Uses lexicon adapter + vector search

### Phase 9: UI Integration (Separate Episode)

**9A: UI Stubbing** (✅ COMPLETE)
- ✅ Add BibleScholar to Orchestrator Shell (Left Rail)
- ✅ Create `BibleScholarPanel` stub (hermetic)
- ✅ Create basic export script (`scripts/ui/export_biblescholar_summary.py`)

**9B: Full Integration (Planned)**
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
- BibleScholar has its own `verse_embeddings` table in `bible_db` with `vector(1024)`
- BibleScholar also has `verses.embedding` with `vector(768)` (HNSW index)
- Control-plane Knowledge Slice may have different embeddings (likely 1024-dim)
- **Schema shows dimension mismatch**: 768 vs 1024 dimensions
- May need adapter to bridge between systems or dimension conversion
- Or create unified embedding strategy

**Risk:** Duplicate embedding storage and inconsistent search results due to dimension mismatch.

**Mitigation:** 
- Evaluate embedding models and dimensions (768 vs 1024)
- Consider unified approach or dimension adapter
- Document which embedding table to use for which use case
- May need to standardize on one dimension or provide conversion layer

### 9.4 LM Integration Pattern

**Question:** How should contextual insights flow through control-plane LM tracking?

**Considerations:**
- BibleScholar rule: DB-grounded, LM-formatted (all content from `bible` schema, LM only formats)
- Control-plane tracks LM calls and budgets
- Need to ensure LM calls are properly logged
- May need adapter between BibleScholar flows and control-plane LM service
- LangChain tables (`public.langchain_pg_*`) are for embedding storage, not content generation

**Risk:** LM calls bypass control-plane tracking or generate content outside DB.

**Mitigation:** 
- Use control-plane LM service wrapper; no direct LM Studio calls from adapters
- Enforce DB-first pattern: query `bible` schema tables first, then format with LM
- Never allow LM to generate biblical content; only format/summarize DB results

### 9.5 Schema Evolution

**Question:** How to handle schema changes in `bible_db` as it evolves?

**Considerations:**
- `bible_db` is read-only SSOT, but schema may evolve (new columns, indexes, tables)
- Adapter layer should abstract schema details
- Need versioning strategy for schema compatibility
- May need migration path if schema changes break adapter contracts

**Risk:** Schema changes break adapter compatibility.

**Mitigation:**
- Use adapter pattern to abstract schema details
- Version adapter contracts
- Document schema dependencies clearly
- Test adapter against schema dumps regularly

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
- `schemas/biblescholar/bible_db_structure.sql` — Complete database schema dump (primary input)
- `schemas/biblescholar/bible_db_verses_structure.sql` — Verses table schema
- `schemas/biblescholar/bible_db_versification_structure.sql` — Versification mappings schema
- `schemas/biblescholar/SCHEMA_INDEX.md` — BibleScholar database schema documentation
- `share/schemas/SCHEMA_REGISTRY.md` — Cross-project schema registry
- `GEMATRIA_MASTER_REFERENCE_v2.md` — Master reference

---

**Document Status:** Draft — Awaiting PM review and approval

