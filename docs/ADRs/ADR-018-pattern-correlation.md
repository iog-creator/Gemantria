# ADR-018: Pattern Correlation Engine
Status: Proposed

## Related Rules
000 (Always-Apply), 006 (AGENTS.md Governance), 013 (Report Verification), 021 (Stats Proof), 022 (Viz Contract Sync)

## Verification (to mirror ADR-016)
- DB checks for correlation tables/views
- Schema-validated export (e.g., `graph_correlations.schema.json`)
- UI contract tests (Pattern Explorer)
- CI workflow to run verifier + UI tests
