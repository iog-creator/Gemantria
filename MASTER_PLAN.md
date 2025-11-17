# Gematria v2.0 Master Plan

## Always-Apply Triad (Governance)

- **Rule-050 — LOUD FAIL** (activation/SSOT)
- **Rule-051 — Required-checks posture**
- **Rule-052 — Tool-priority (local+gh → codex → gemini/mcp)**

These rules are baseline and must appear in anchor docs to satisfy the triad guard.

<!-- guard.alwaysapply sentinel: 050 051 052 -->

| # | Title |
|---:|-------|
| 050 | OPS Contract v6.2.3 (AlwaysApply) |
| 051 | Cursor Insight & Handoff (AlwaysApply) |
| 052 | Tool Priority & Context Guidance (AlwaysApply) |

## Vision

Rebuild the complete Gematria system from scratch using existing assets in a clean, maintainable architecture.

> Governance fast-lane: All exports stamp `generated_at` as RFC3339 and set `metadata.source="fallback_fast_lane"`. Run guards in HINT-only mode (`STRICT_RFC3339=0`) on main/PRs and STRICT (`STRICT_RFC3339=1`) on release builds. Always run `make housekeeping` after docs or script changes so the contract stays enforced.

## Single-Sitting Development Plan

### P0.1: Project Setup & Documentation (30 min)

- [x] Create gematria.v2 workspace
- [x] Set up git repository with main branch
- [x] Copy flat grok_share/ files to workspace
- [x] Create initial PR-000 scaffold (folders, **init**.py files)
- [x] Document all ADRs in docs/adr/ folder
- [x] Set up Makefile with basic targets

### P0.2: Core Infrastructure (45 min)

- [ ] Implement Hebrew utils (hebrew_utils.py) with validation tests
- [ ] Create Pydantic schemas from gematria_output.json
- [ ] Set up configuration management (.env support)
- [ ] Create database connection layer (psycopg)
- [ ] Implement basic logging and error handling

### P0.3: Database Layer (45 min)

- [ ] Run 001_two_db_safety.sql migration
- [ ] Implement GematriaDB class with CRUD operations
- [ ] Create BibleDB read-only integration
- [ ] Add data validation and integrity checks
- [ ] Implement connection pooling

### P0.4: LangGraph Pipeline Foundation (60 min)

- [ ] Create StateGraph workflow skeleton
- [ ] Implement 6 core nodes (extraction, validation, enrichment, network, integration, retrieval)
- [ ] Add conditional edges and error handling
- [ ] Implement triple verification in extraction node
- [ ] Add Postgres checkpointer for resumability

### P0.5: LM Studio Integration (45 min)

- [ ] Implement LMStudioClient with model switching
- [ ] Add triple verification (local + math model + expected)
- [ ] Integrate AI enrichment for theological insights
- [ ] Add mock mode for testing without LM Studio
- [ ] Implement retry logic and error handling

### P0.6: Testing & Quality Gates (45 min)

- [ ] Set up pytest infrastructure with fixtures
- [ ] Implement contract tests for database layer
- [ ] Add unit tests for Hebrew utilities
- [ ] Create integration tests for pipeline
- [ ] Set up CI with ruff, mypy, and pytest gates

### P0.7: CLI & Production Deployment (30 min)

- [ ] Create run_pipeline.py CLI script
- [ ] Add FastAPI server for API access
- [ ] Implement health checks and monitoring
- [ ] Add graceful shutdown and error recovery
- [ ] Create production deployment scripts

### P0.8: Golden Data Integration (30 min)

- [ ] Load golden_genesis_min.json as seed data
- [ ] Validate against valid_cases.json
- [ ] Generate embeddings for semantic search
- [ ] Create initial network analysis
- [ ] Verify end-to-end pipeline with real data

## Architecture Decisions

### ADR-000: LangGraph StateGraph vs Queues

**Decision**: Use LangGraph StateGraph for workflow orchestration

- **Rationale**: Better error handling, resumability, and conditional logic than manual queues
- **Alternatives Considered**: Custom queue system, Apache Airflow
- **Consequences**: Learning curve but better maintainability and monitoring

### ADR-001: Two-Database Safety

**Decision**: Separate read-write (gematria) and read-only (bible_db) databases

- **Rationale**: Safety, performance, and clear data ownership boundaries
- **Alternatives Considered**: Single database with permissions, embedded SQLite
- **Consequences**: Added complexity but better data integrity and safety

### ADR-002: Gematria Rules

**Decision**: Mispar Hechrachi with finals = regulars, strip nikud completely

- **Rationale**: Standard academic practice, consistency with existing calculations
- **Alternatives Considered**: Mispar Gadol, include nikud in calculations
- **Consequences**: Matches existing data, clear validation rules

## Quality Gates

### Code Quality

- [ ] 100% ruff compliance (linting)
- [ ] 100% mypy compliance (typing)
- [ ] 95%+ test coverage
- [ ] No critical security vulnerabilities

### Data Quality

- [ ] 100% gematria calculation accuracy (validated against valid_cases.json)
- [ ] 100% schema compliance for all outputs
- [ ] All golden data loads successfully
- [ ] No data corruption in round-trip operations

### Performance Targets

- [ ] Pipeline processes 50 nouns in <5 minutes
- [ ] Database queries <100ms average
- [ ] Memory usage <1GB for full pipeline
- [ ] No memory leaks in long-running processes

## Success Criteria

- [ ] All P0 phases complete in single sitting
- [ ] Pipeline successfully processes Genesis with golden data
- [ ] All tests pass with 95%+ coverage
- [ ] Code is production-ready and maintainable
- [ ] Documentation is complete and accurate

## Risk Mitigation

- **Fallback**: Mock LM Studio mode for development
- **Testing**: Comprehensive TDD with golden data
- **Reusability**: Modular design allows component reuse
- **Documentation**: All decisions documented in ADRs

## Timeline: ~4 hours total

- P0.1-P0.3: Setup & Core (2 hours)
- P0.4-P0.5: Pipeline & AI (1.5 hours)
- P0.6-P0.8: Testing & Production (45 min)

- Phase-7F (COMPLETE): Flexible local LM architecture (Ollama + LM Studio per-slot routing)
- Phase-7G: Added `pmagent lm.status` command to introspect LM providers, models, and local service health.
- Phase-7G: Basic UI/TV wiring — system status JSON endpoint, HTML status page, and LM/DB health TVs.
- Phase-8A: Status explanation skill — `pmagent status.explain` uses DB/LM snapshots to produce a human-readable reality check.
- Phase-8B: Status explanation in UI — `/api/status/explain` + Explanation card on `/status` using the status.explain skill.
- Phase-8C: LM Insights graph — `/api/lm/indicator` endpoint and `/lm-insights` page visualizing LM indicator snapshots.
- Phase-8C (Governance/Docs): Doc content + embeddings RAG-ready — Full doc content and embeddings in control-plane for governance/docs RAG. Includes `pmagent docs.search` CLI, STRICT guards for Tier-0 docs (fragments + embeddings), and integration into `ops.tagproof`. See `docs/SSOT/DOC_CONTENT_VECTOR_PLAN.md` for details.
- Phase-8D (Governance/Docs): Atlas Governance Search Panel — `/api/docs/search` API endpoint and `/governance-search` HTML page for semantic search over Tier-0 governance docs. Integrated into Atlas viewer. See `docs/SSOT/ATLAS_GOVERNANCE_SEARCH_PANEL.md` for specification.
- Phase-8D: System dashboard — `/dashboard` front door that summarizes status + LM insights for non-technical users.
- Phase-8E: DB health graph — `/api/db/health_timeline` endpoint and `/db-insights` page visualizing DB health mode over time.
- Phase-9A: BibleScholar passage UI — `/api/bible/passage` endpoint and `/bible` page for passage + theology commentary.
