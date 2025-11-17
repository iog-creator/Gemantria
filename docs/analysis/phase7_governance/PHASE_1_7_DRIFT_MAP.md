# Phase 1-7 Drift Map

> Branch: feat/phase7.governance.rebuild.20251116-085215  
> Scope: Comprehensive analysis of Phases 1-7 (planned vs implemented)  
> Status: Draft v0.1 — Analysis complete, gaps identified

---

## Executive Summary

**Overall Status**: Core pipeline phases (0-11) are marked complete, but control-plane and runtime phases (3A-7) show significant drift between planned and implemented states.

**Key Findings**:
- **Phases 0-2, 3 (Core), 5, 8-11**: ✅ Complete as documented
- **Phase 3A-3D (Control Plane)**: ✅ Implementation complete, 3 pending items
- **Phase 4 (LM Insights)**: ✅ Complete
- **Phase 5 (LM Integration)**: ✅ Complete
- **Phase 6 (LM Studio Live + Knowledge)**: ⚠️ Partial (6A-6C complete, 6D-6E incomplete)
- **Phase 7 (Runtime Bring-Up + Governance)**: 🚧 In Progress (7F complete, governance reconstruction ongoing)

**Critical Gaps**:
1. Phase-6 downstream app wiring (6D) not complete
2. Phase-7 governance SSOT migration incomplete
3. Phase-1 Control Plane pending items (3 tasks) not resolved
4. No explicit Phase-2 Control Plane definition

---

## Phase 0: Governance v6.2.3

### Planned
- Always-Apply Triad (Rule-050, Rule-051, Rule-052)
- Internal guardrails active
- OPS Contract v6.2.3

### Implemented
- ✅ Always-Apply Triad documented and enforced
- ✅ Rules 000-068 present and contiguous
- ✅ OPS Contract v6.2.3 active
- ✅ Guard system operational

### Drift
- **None** — Phase 0 is complete and operational

---

## Phase 1: Data Layer (DB Foundation)

### Planned
- Two-database safety (GEMATRIA_DSN, BIBLE_DB_DSN)
- Hebrew normalization utilities
- Gematria calculation rules (Mispar Hechrachi)
- Database connection layer (psycopg)
- Connection pooling
- Data validation and integrity checks

### Implemented
- ✅ ADR-001: Two-Database Safety implemented
- ✅ Hebrew normalization (NFKD → strip combining → strip maqaf/sof pasuq/punct → NFC)
- ✅ Gematria calculations (Mispar Hechrachi, finals=regular)
- ✅ Database connection layer with centralized loaders
- ✅ Read-only Bible DB adapter
- ✅ Parameterized SQL enforcement

### Drift
- **Minor**: Some P0.2/P0.3 items from MASTER_PLAN still marked incomplete, but core functionality exists
- **Status**: ✅ Complete for production use

---

## Phase 2: Pipeline Core (LangGraph)

### Planned
- LangGraph StateGraph workflow
- 6 core nodes (extraction, validation, enrichment, network, integration, retrieval)
- Conditional edges and error handling
- Triple verification in extraction node
- Postgres checkpointer for resumability

### Implemented
- ✅ LangGraph StateGraph orchestration
- ✅ Integrated pipeline with 8 nodes (includes math_verifier)
- ✅ Postgres/memory checkpointer
- ✅ Triple verification (local + math model + expected)
- ✅ Comprehensive logging and error handling

### Drift
- **Enhancement**: Math verifier node added (not in original plan)
- **Status**: ✅ Complete and enhanced beyond original scope

---

## Phase 3: Exports & Badges

### Planned
- Graph exports (graph_latest.json, graph_stats.json)
- Pattern exports (temporal_patterns.json, pattern_forecast.json)
- Correlation exports (correlation_weights.json)
- Badge generation and manifest
- Schema validation

### Implemented
- ✅ All core exports implemented
- ✅ Unified envelope (Phase 11)
- ✅ COMPASS validation (>80% correctness threshold)
- ✅ Badge system with manifest
- ✅ JSON Schema validation

### Drift
- **None** — Phase 3 core is complete

---

## Phase 3A-3D: Control Plane

### Planned (Phase-3B Features)
- Control-plane schema (migration 040)
- `pmagent health` commands (system, db, lm, graph)
- `pmagent control` commands (status, tables, schema, summary, pipeline_status)
- DB-backed graph overview
- Control-plane compliance exports

### Implemented
- ✅ Migration 040: Control-plane schema
- ✅ `pmagent health system|db|lm|graph` (PR #524)
- ✅ `pmagent graph import|overview` (PR #525)
- ✅ `pmagent control status` (PR #526)
- ✅ `pmagent control tables` (PR #527)
- ✅ `pmagent control schema` (PR #528)
- ✅ `pmagent control pipeline_status` (PR #529)
- ✅ `pmagent control summary` (PR #530)
- ✅ Compliance exports (compliance.head.json, top_violations_7d/30d)

### Pending Items (3 remaining)
1. **[ ] Final test hardening in CI (STRICT vs HINT mode)**
   - Need to ensure proper STRICT/HINT mode enforcement in CI workflows
   - Tag lanes should run STRICT, PR lanes should run HINT

2. **[ ] Governance wiring (tag lanes run guards/exports)**
   - Wire control-plane guards and exports into tag lane CI workflows
   - Ensure exports run automatically on tag builds

3. **[ ] Atlas UI linkage for compliance exports**
   - Link compliance export artifacts to Atlas UI
   - Ensure webproof pages are accessible from Atlas dashboard

### Drift
- **Implementation**: ✅ Complete
- **Governance Integration**: ⚠️ 3 pending items block full completion
- **Status**: Implementation complete, governance wiring incomplete

---

## Phase 4: LM Insights & UI Polish

### Planned
- LM insights exports (lm_insights_7d.json)
- LM status page UX enhancements
- LM indicator export (lm_indicator.json) as canonical signal
- Governance/docs alignment

### Implemented
- ✅ Phase-4A: LM insights exports (PR #537)
- ✅ Phase-4B: LM status UX polish (PR #538)
- ✅ Phase-4C: LM indicator export (PR #539)
- ✅ Phase-4D: Governance/docs alignment (PR #540)

### Drift
- **None** — Phase 4 is complete

---

## Phase 5: StoryMaker & BibleScholar LM Integration

### Planned
- LM Indicator Widget Contract
- Shared adapter module (`load_lm_indicator_widget_props()`)
- StoryMaker integration (React tile)
- BibleScholar integration (header badge)
- Hermetic, db_off-safe, LM-off-safe implementation

### Implemented
- ✅ LM Indicator Widget contract defined
- ✅ Shared adapter module implemented
- ✅ StoryMaker integration (PR #1)
- ✅ BibleScholar integration (PR #2)
- ✅ Full test coverage (healthy, degraded, offline, missing-file, invalid-JSON)

### Drift
- **None** — Phase 5 is complete

---

## Phase 6: LM Studio Live Usage + DB-Backed Knowledge

### Planned
- 6A: LM Studio live usage enablement
- 6B: LM usage budgets & rate-tracking
- 6C: Minimal Postgres knowledge slice ("Knowledge v0")
- 6D: Downstream app read-only wiring
- 6E: Governance & SSOT updates

### Implemented

**6A: LM Studio Live Usage** ✅
- ✅ Config flag: `LM_STUDIO_ENABLED=true|false`
- ✅ Routing logic implemented
- ✅ Guarded call wrapper (`guarded_lm_call()`)
- ✅ First LM-enabled feature: `agentpm/runtime/lm_helpers.generate_text()`

**6B: LM Usage Budgets** ✅
- ✅ New table: `control.lm_usage_budget` (migration 042)
- ✅ Budget checks before LM calls
- ✅ Automatic fallback when exceeded
- ✅ Export: `lm_budget_7d.json`

**6C: Knowledge Slice** ✅
- ✅ New schema: `knowledge` (migration 043)
- ✅ Tables: `kb_document`, `kb_embedding`
- ✅ ETL ingestion script
- ✅ Export script
- ✅ Make targets: `atlas.kb.ingest`, `atlas.kb.export`
- ✅ Full test coverage

**6D: Downstream App Wiring** ⚠️ **INCOMPLETE**
- ❌ StoryMaker `useKnowledgeSlice()` hook — not implemented
- ❌ BibleScholar KB client — not implemented
- ❌ Shared API/CLI wrapper — not implemented
- ⚠️ Apps still query Postgres directly (violates Phase-6 design)

**6E: Governance & SSOT Updates** ⚠️ **PARTIAL**
- ✅ MASTER_PLAN updated
- ✅ AGENTS.md updated
- ✅ CHANGELOG.md updated
- ⚠️ Rule enforcement for downstream apps not fully implemented

### Drift
- **6A-6C**: ✅ Complete
- **6D**: ❌ **Critical Gap** — Downstream app wiring incomplete
- **6E**: ⚠️ Partial — Documentation updated, enforcement incomplete
- **Status**: ⚠️ Partial (60% complete)

---

## Phase 7: Runtime Bring-Up + Governance Reconstruction

### Planned (from MASTER_PLAN)
- 7A: Control-plane bring-up (migration 040)
- 7B: LM Studio model configuration normalization
- 7C: Snapshot integrity and drift review
- 7D: Optional UX polish for bring-up tooling
- 7E: Ollama provider integration (Granite 4.0 support)
- 7F: Flexible local LM architecture (per-slot provider routing)
- 7G: LM status command + UI/TV wiring
- Governance reconstruction (Postgres SSOT migration)

### Implemented

**7A: Control-Plane Bring-Up** ✅
- ✅ Migration 040 applied
- ✅ Control-plane schema operational

**7B: LM Config Normalization** ✅
- ✅ Model discovery scripts
- ✅ Ops ledger v0
- ✅ Configuration normalization

**7C: Snapshot Integrity** 🚧 **IN PROGRESS**
- ✅ Snapshot generation working
- ⚠️ Drift review ongoing (this document)

**7D: UX Polish** ⚠️ **PARTIAL**
- ✅ Basic bring-up tooling exists
- ⚠️ UX polish incomplete

**7E: Ollama Provider** ✅
- ✅ Ollama adapter implemented
- ✅ Granite 4.0 support
- ✅ Provider routing via `INFERENCE_PROVIDER`

**7F: Flexible LM Architecture** ✅
- ✅ Per-slot provider configuration
- ✅ All four slots configured (local_agent, embedding, reranker, theology)
- ✅ Default models set
- ✅ Test suite created

**7G: LM Status + UI** ✅
- ✅ `pmagent lm.status` command
- ✅ System status JSON endpoint (`/api/status/system`)
- ✅ HTML status page (`/status`)
- ✅ LM/DB health TVs

**Governance Reconstruction** 🚧 **IN PROGRESS**
- ✅ Phase-7 governance drift map created (OPS-001, OPS-002, OPS-003)
- ✅ Postgres governance SSOT plan defined
- ❌ DB migrations not yet implemented
- ❌ Ingestion scripts not yet implemented
- ❌ `.cursor/rules` generation from DB not yet implemented

### Drift
- **7A-7F, 7G**: ✅ Complete
- **7C**: 🚧 In progress (drift review ongoing)
- **7D**: ⚠️ Partial (basic tooling exists, UX polish incomplete)
- **Governance Reconstruction**: 🚧 In progress (plan complete, implementation pending)
- **Status**: ⚠️ Partial (70% complete, governance reconstruction critical path)

---

## Cross-Phase Drift Patterns

### 1. Control-Plane vs Pipeline Phases

**Pattern**: Control-plane features (Phase 3A-3D) are implementation-complete but governance-wiring incomplete.

**Impact**: Control-plane exists but is not fully integrated into CI/CD and governance workflows.

**Resolution**: Complete Phase-1 Control Plane pending items (3 tasks).

---

### 2. Downstream App Integration

**Pattern**: Phase-6 downstream app wiring (6D) incomplete, violating design principle that apps should not query Postgres directly.

**Impact**: StoryMaker and BibleScholar may be accessing DB directly instead of through Gemantria-owned APIs.

**Resolution**: Implement Phase-6D (downstream app read-only wiring).

---

### 3. Governance SSOT Migration

**Pattern**: Phase-7 governance reconstruction planned but not implemented. `.cursor/rules` remains de facto SSOT instead of Postgres.

**Impact**: Rules authority split between `.cursor/rules` and docs, no single source of truth in DB.

**Resolution**: Complete Phase-7 governance reconstruction (OPS-004+).

---

### 4. Test Hardening & CI Integration

**Pattern**: Multiple phases have incomplete CI integration:
- Phase-1 Control Plane: STRICT vs HINT mode enforcement incomplete
- Phase-6: Downstream app tests incomplete
- Phase-7: Governance migration tests not yet defined

**Impact**: Inconsistent enforcement across phases, some features not fully guarded.

**Resolution**: Complete test hardening across all phases.

---

## Phase Completion Matrix

| Phase | Planned | Implemented | Pending | Status |
|-------|---------|-------------|---------|--------|
| 0 | Governance v6.2.3 | ✅ Complete | 0 | ✅ 100% |
| 1 | Data Layer | ✅ Complete | 0 | ✅ 100% |
| 2 | Pipeline Core | ✅ Complete | 0 | ✅ 100% |
| 3 | Exports & Badges | ✅ Complete | 0 | ✅ 100% |
| 3A-3D | Control Plane | ✅ Implementation | 3 items | ⚠️ 90% |
| 4 | LM Insights | ✅ Complete | 0 | ✅ 100% |
| 5 | LM Integration | ✅ Complete | 0 | ✅ 100% |
| 6 | LM Live + Knowledge | ⚠️ Partial | 6D, 6E | ⚠️ 60% |
| 7 | Runtime + Governance | ⚠️ Partial | 7C, 7D, Gov | ⚠️ 70% |

---

## Critical Path to Phase-7 Completion

### Immediate Priorities

1. **Complete Phase-1 Control Plane Pending Items** (3 tasks)
   - Final test hardening in CI
   - Governance wiring for tag lanes
   - Atlas UI linkage

2. **Complete Phase-6D (Downstream App Wiring)**
   - StoryMaker `useKnowledgeSlice()` hook
   - BibleScholar KB client
   - Shared API/CLI wrapper

3. **Complete Phase-7 Governance Reconstruction**
   - DB migrations for governance schema
   - Ingestion scripts (rules, TVs, tags)
   - `.cursor/rules` generation from DB
   - Cutover plan execution

### Blockers

- **Phase-7 governance reconstruction** blocks full governance SSOT migration
- **Phase-6D incomplete** violates design principles (apps querying DB directly)
- **Phase-1 pending items** prevent full control-plane integration

---

## Recommendations

### Short-Term (Next Sprint)

1. **Complete Phase-1 Control Plane Pending Items**
   - Create PRs for each of the 3 pending tasks
   - Wire into CI workflows
   - Update MASTER_PLAN.md

2. **Resume Phase-7 Governance Reconstruction**
   - Execute OPS-004 (DB inspection + migration design)
   - Implement governance schema migrations
   - Begin ingestion script implementation

### Medium-Term (Next Month)

1. **Complete Phase-6D**
   - Implement StoryMaker knowledge hook
   - Implement BibleScholar KB client
   - Create shared API/CLI wrapper
   - Add enforcement guards

2. **Complete Phase-7 Governance Migration**
   - Implement `.cursor/rules` generation from DB
   - Execute cutover plan (Phase A → B → C)
   - Update all governance docs

### Long-Term (Next Quarter)

1. **Define Phase-2 Control Plane**
   - Create explicit Phase-2 definition
   - Plan PLAN-078 (Compliance Dashboards)
   - Prioritize PLAN-079 through PLAN-081

2. **Complete Phase-7 UX Polish**
   - Enhance bring-up tooling UX
   - Improve status page visualizations
   - Add governance dashboard

---

## Evidence Sources

- `MASTER_PLAN.md` (Phase Overview, Phase-7 planning section)
- `CHANGELOG.md` (Phase-3 through Phase-7 entries)
- `docs/SSOT/PHASE_5_PLAN.md` (Phase-5 completion summary)
- `docs/SSOT/PHASE_6_PLAN.md` (Phase-6 status)
- `docs/PHASE_7F_SUMMARY.md` (Phase-7F model readiness)
- `docs/analysis/PHASE_1_2_STATUS.md` (Control Plane status)
- `docs/analysis/phase7_governance/PHASE_7_GOVERNANCE_DRIFT_MAP.md` (Governance-specific drift)

---

## Conclusion

**Phases 0-5 are complete** with minor documentation gaps. **Phase 6 is 60% complete** with critical downstream app wiring missing. **Phase 7 is 70% complete** with governance reconstruction as the critical path.

**Primary blockers**:
1. Phase-7 governance SSOT migration (in progress, plan complete)
2. Phase-6D downstream app wiring (not started)
3. Phase-1 Control Plane pending items (3 tasks, not started)

**Next steps**: Complete Phase-1 pending items, then resume Phase-7 governance reconstruction, then complete Phase-6D.

