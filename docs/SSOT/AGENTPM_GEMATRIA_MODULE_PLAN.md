# AgentPM Gematria Module — Extraction Plan

**Status:** Draft  
**Owner:** AgentPM (OS) + Gematria module maintainer  
**Last updated:** 2025-11-15T18:11:22Z

---

## 1. Purpose

This document describes how to extract the *true Gematria / numerics* logic
from the current Gemantria.v2 repo into a dedicated **Gematria module** managed
by the **AgentPM OS**.

- **AgentPM** is the OS / platform and eventual commercial product.
- **Gematria** is a Bible-specific numeric module (not the OS, not the full app).
- **BibleScholarAI** is the worship + showcase application built on top of
  modules like Gematria, bible_db, lexicon, search, etc.

This plan focuses on which parts of this repo become the **Gematria module
core**, which stay as Gemantria.v2 infrastructure, and how we will gradually
migrate.

---

## 2. Source Intake

Primary source for this plan:

- `docs/SSOT/GEMATRIA_NUMERICS_INTAKE.md`  
  (internal scan of numerics / Bible-pattern-related code in this repo)

From that intake, we identify:

- **Core Gematria modules** to port into AgentPM's `gematria` module.
- **Support / infra code** that remains here.
- **Tests and data** that should follow the core module.

The subsections below list top candidates as of this scan.

---

## 3. Candidate Core Gematria Components

These are candidate files that represent **true Gematria / Bible numerics or
close supporting logic**. The list is seeded automatically from the intake
and should be curated by the PM and human orchestrator.

### 3.1 Python modules (core numerics & helpers)

- `src/core/hebrew_utils.py` — Hebrew text normalization, gematria calculation
- `src/nodes/math_verifier.py` — Gematria calculation verification
- `src/nodes/ai_noun_discovery.py` — AI-powered noun discovery from Bible text
- `src/nodes/collect_nouns_db.py` — Database noun collection logic
- `src/ssot/noun_adapter.py` — Noun data adapter for SSOT exports
- `src/utils/osis.py` — OSIS reference parsing (Bible verse references)

### 3.2 Scripts (ETL / verification)

- `scripts/math_verifier.py` — Standalone math verification script
- `scripts/gematria_verify.py` — Gematria verification script
- `scripts/ai_noun_discovery.py` — Noun discovery script
- `scripts/extract_nouns_from_bible_db.py` — Bible database noun extraction
- `scripts/export_ai_nouns.py` — Export discovered nouns
- `scripts/export_noun_index.py` — Export noun index
- `scripts/backfill_noun_embeddings.py` — Backfill embeddings for nouns
- `scripts/guard_ai_nouns.py` — Guard/validation for AI-discovered nouns
- `scripts/sql/guard_hebrew_export.sql` — SQL guard for Hebrew exports
- `scripts/run_book.py` — Book processing orchestration
- `scripts/book_readiness.py` — Book readiness checks
- `scripts/audit_genesis_db.py` — Genesis database audit
- `scripts/smokes/book_extraction_correctness.py` — Book extraction smoke tests
- `scripts/smokes/book_smoke.py` — Book smoke tests

### 3.3 Tests

- `tests/unit/test_hebrew_utils.py` — Hebrew utilities unit tests
- `tests/unit/test_math_verifier.py` — Math verifier unit tests (if exists)
- `tests/integration/test_noun_discovery.py` — Noun discovery integration tests (if exists)

### 3.4 Data / schemas / exports

- `schemas/ai_nouns.schema.json` — AI nouns schema
- `schemas/graph_output.schema.json` — Graph output schema (includes gematria values)
- `schemas/noun_adapter.schema.json` — Noun adapter schema
- `share/exports/ai_nouns.json` — Exported AI-discovered nouns
- `share/exports/noun_index.json` — Noun index exports
- `share/exports/graph_latest.json` — Graph with gematria values
- `share/exports/graph_stats.json` — Graph statistics
- `configs/gematria.json` — Gematria configuration (if exists)
- `configs/hebrew_normalization.json` — Hebrew normalization config (if exists)

---

## 4. Target Package Layout under AgentPM

The eventual goal is a Gematria module under AgentPM, *not* inside this repo.
A rough target structure might look like:

```text
agentpm/modules/gematria/
    __init__.py
    core.py            # core gematria value logic
    hebrew.py          # Hebrew-specific utilities
    greek.py           # Greek-specific utilities (if any)
    bible_index.py     # mapping verses/passages to numeric views
    verification.py    # math verifier, consistency checks
    ingestion.py       # noun/term extraction, bible_db integration
    adapters.py        # adapters to/from AgentPM control-plane and exports
    tests/
        test_core.py
        test_hebrew.py
        test_verification.py
        ...
```

### 4.1 Module Responsibilities

**Core Gematria (`core.py`):**
- Gematria value calculation (Mispar Hechrachi, etc.)
- Hebrew letter-to-number mapping
- Greek letter-to-number mapping (if needed)
- Numeric pattern analysis

**Hebrew Utilities (`hebrew.py`):**
- Hebrew text normalization (NFKD → strip combining → strip maqaf/sof pasuq/punct → NFC)
- Surface-form gematria calculation
- Ketiv/Qere handling
- Variant type recording

**Verification (`verification.py`):**
- Math verification of gematria calculations
- Consistency checks
- Cross-reference validation

**Ingestion (`ingestion.py`):**
- Noun/term extraction from Bible text
- Bible database integration
- SSOT noun adapter logic

**Adapters (`adapters.py`):**
- Adapters to AgentPM control-plane
- Export format adapters
- Integration with bible_db module

---

## 5. What Stays in Gemantria.v2

These components remain in Gemantria.v2 as infrastructure / control-plane:

- **Control-plane logic:** LM budgets, LM logging, control schema
- **Pipeline orchestration:** LangGraph pipeline, checkpointer, state management
- **Export infrastructure:** Generic export scripts, share directory management
- **UI/Web:** React UI, webui components
- **Database infrastructure:** Generic DB utilities, connection pooling
- **Governance:** Rules, ADRs, documentation sync
- **CI/CD:** Test infrastructure, guards, quality gates

**Boundary:** Gematria module should be *pure* numerics/Bible logic with minimal
dependencies. It should not depend on Gemantria.v2-specific infrastructure.

---

## 6. Migration Strategy

### Phase 1: Extract Core Logic (Current)

1. Identify pure gematria/numerics functions
2. Extract to standalone module structure
3. Create minimal test suite
4. Document API contracts

### Phase 2: Create AgentPM Module

1. Create `agentpm/modules/gematria/` structure
2. Port core logic with minimal dependencies
3. Add AgentPM-specific adapters
4. Integrate with AgentPM control-plane

### Phase 3: Deprecate Gemantria.v2 Copies

1. Update Gemantria.v2 to import from AgentPM module
2. Remove duplicate code
3. Update tests to use AgentPM module
4. Update documentation

### Phase 4: Full Integration

1. BibleScholarAI uses AgentPM Gematria module
2. Gemantria.v2 becomes thin wrapper / showcase
3. All gematria logic centralized in AgentPM

---

## 7. Dependencies & Contracts

### 7.1 External Dependencies

- **bible_db:** Read-only Bible database (SSOT)
- **AgentPM control-plane:** For exports, logging, governance
- **LM Studio (optional):** For AI-powered noun discovery

### 7.2 Internal Contracts

- **Hebrew normalization:** Must follow Rule-002 (NFKD → strip → NFC)
- **Gematria calculation:** Mispar Hechrachi, finals=regular
- **Noun discovery:** Ketiv primary, variants recorded
- **Verification:** Math verifier must validate all calculations

### 7.3 API Contracts

- **Input:** Hebrew/Greek text, Bible references
- **Output:** Gematria values, normalized text, noun data
- **Formats:** JSON, JSON-LD (for semantic exports)

---

## 8. Open Questions

- [ ] Should Greek gematria be included in initial module, or deferred?
- [ ] How should noun discovery integrate with AgentPM's AI control-plane?
- [ ] Should the module support multiple gematria systems (Mispar Hechrachi, Mispar Gadol, etc.)?
- [ ] How should the module handle variant readings (Ketiv/Qere)?
- [ ] What is the migration timeline? (TBD by PM)

---

## 9. Next Steps

1. **Review this plan** with PM and human orchestrator
2. **Prioritize components** for Phase 1 extraction
3. **Create detailed extraction tasks** for each component
4. **Begin Phase 1** extraction work
5. **Update this plan** as extraction progresses

---

## 10. References

- `docs/SSOT/GEMATRIA_NUMERICS_INTAKE.md` — Source intake file
- `docs/rfcs/RFC-081-unified-ui-and-biblescholar-module.md` — Unification RFC
- `docs/SSOT/BIBLESCHOLAR_INTAKE.md` — BibleScholar intake (related)
- Rule-002 — Gematria validation rules
- ADR-XXX — (TBD) Gematria module architecture decision

