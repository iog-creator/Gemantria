# MASTER_PLAN — Phase Ledger & Forest Baseline

## Phase Ledger (Synced 2025-10-21)

| Phase | PRs | Scope | Verification Rules | CI |
|--------|-----|--------|--------------------|----|
| 0–3 | Core Infra | DB, pipeline, aggregation | 000-006 | — |
| 4 | Theological Enrichment | Enrichment, pattern extraction | 013 | — |
| 5 | Metrics & Visualization | PR-016/017 | 021-022 | verify-stats.yml |
| 6 | Pattern Correlation | PR-018 | 023-024 | verify-correlations.yml |
| ∞ | Forest Governance | PR-FOREST-001 | 025 | manual / docs |

## Forest Baseline (2025-10-21)

### Rules Active
- Rule 000: Always-Apply (production safety, no mocks)
- Rule 006: AGENTS.md Governance
- Rule 013: Report Verification
- Rule 016: Visualization Contract Sync
- Rule 017: Agent Docs Presence
- Rule 021: Stats Proof (metrics verification)
- Rule 022: Visualization Contract Sync (UI contracts)
- Rule 025: Phase Gate & Forest Sync (NEW)

### CI Workflows
- verify-stats.yml (PR-016/017 verification)
- ci.yml (standard quality gates)

### ADRs Active
- ADR-016: Insight Metrics & Ontology
- ADR-018: Pattern Correlation Engine

### Verification Matrix
See docs/VERIFICATION_MATRIX.md for rule ↔ script ↔ CI ↔ evidence mappings.

## Next Phases
- PR-018: Pattern correlation implementation
- PR-019: Advanced analytics dashboard
- PR-020: Semantic export enhancements
