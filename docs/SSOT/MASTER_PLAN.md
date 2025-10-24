# MASTER_PLAN — Phase Ledger & Forest Baseline

## Phase Ledger (Synced 2025-10-21)

_Phase 8: Multi-Temporal Analytics & Predictive Patterns - Time-aware pattern mining with rolling windows and forecasting_

| Phase | PRs                                            | Scope                           | Verification Rules | CI                       |
| ----- | ---------------------------------------------- | ------------------------------- | ------------------ | ------------------------ |
| 0–3   | Core Infra                                     | DB, pipeline, aggregation       | 000-006            | —                        |
| 4     | Theological Enrichment                         | Enrichment, pattern extraction  | 013                | —                        |
| 5-A   | Enhanced Analytics Infra                       | PR-018-A (Schema + Export)      | 021-022, 030       | verify-stats.yml         |
| 5-B   | Correlation Engine                             | PR-018-B (Analytics Engine)     | 030                | verify-stats.yml         |
| 5-C   | Correlation Visualization                      | PR-018-C (Interactive Explorer) | 030-031            | verify-stats.yml         |
| 6     | Cross-Text Pattern Analysis                    | ADR-022 (Pattern Engine)        | 032                | verify-patterns.yml      |
| 7     | Advanced Visualization & Exploration           | ADR-023 (API + Dashboard)       | 033                | verify-visualization.yml |
| 8     | Multi-Temporal Analytics & Predictive Patterns | ADR-025 (Temporal Engine)       | 034-036            | verify-temporal.yml      |
| ∞     | Forest Governance                              | PR-FOREST-001                   | 025                | manual / docs            |

## Forest Baseline (2025-10-21)

### Rules Active

<!-- RULES_TABLE_START -->
| # | Title |
|---:|-------|
| 000 | # --- |
| 001 | # --- |
| 002 | # --- |
| 003 | # --- |
| 004 | # --- |
| 005 | # --- |
| 006 | # --- |
| 007 | # --- |
| 008 | # --- |
| 009 | # --- |
| 010 | # --- |
| 011 | # --- |
| 012 | # --- |
| 013 | # --- |
| 014 | # --- |
| 015 | # --- |
| 016 | # --- |
| 017 | # --- |
| 018 | # --- |
| 019 | # --- |
| 020 | # --- |
| 021 | # --- |
| 022 | # --- |
| 023 | # --- |
| 024 | # --- |
| 025 | # --- |
| 026 | # --- |
| 027 | # --- |
| 028 | # --- |
| 029 | # --- |
| 030 | # --- |
| 031 | # --- |
| 032 | # --- |
| 033 | # --- |
| 034 | # --- |
| 035 | # --- |
| 036 | # --- |
<!-- RULES_TABLE_END -->

### CI Workflows

- verify-stats.yml (PR-016/017 verification)
- verify-patterns.yml (Phase 6 pattern validation)
- verify-visualization.yml (Phase 7 API/dashboard validation)
- ci.yml (standard quality gates)

### ADRs Active

- ADR-016: Insight Metrics & Ontology
- ADR-018: Pattern Correlation Engine
- ADR-022: Cross-Text Pattern Analysis (NEW)
- ADR-023: Visualization API and Dashboard (NEW)

### Verification Matrix

See docs/VERIFICATION_MATRIX.md for rule ↔ script ↔ CI ↔ evidence mappings.

## Next Phases

- PR-023: Advanced pattern visualization (post Phase 6)
- PR-024: Multi-temporal analysis (post Phase 6)
