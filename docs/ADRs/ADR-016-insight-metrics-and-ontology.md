# ADR-016: Insight Metrics & Ontology Enrichment

## Status

Accepted

## Context

We need minimal, interpretable metrics beyond centrality: cluster density/diversity and per-node cohesion/bridge/local-diversity. These will provide actionable insights into network structure and semantic relationships.

## Decision

- Add `concept_metrics` and `cluster_metrics` tables and `v_metrics_overview` view
- Compute metrics via `scripts/analyze_metrics.py` after graph analysis
- Extend JSON-LD context and exports with metrics keys when present
- Export stats include avg cluster density/diversity for dashboard monitoring

## Rationale

These metrics provide:

- **Semantic cohesion**: How well concepts fit within their cluster
- **Bridge score**: Cross-cluster connectivity potential
- **Local diversity**: Neighborhood semantic variety
- **Cluster density**: Internal connectivity strength
- **Cluster diversity**: Semantic spread within communities

Clean separation from centrality calculations, stable JSON-LD forward compatibility, and easy dashboard integration.

## Alternatives Considered

- **In-line centrality computation**: Would duplicate centrality logic and make exports inconsistent
- **External analytics tools**: Would require data export and lose integration benefits
- **Complex graph algorithms**: Would increase computational overhead without proportional insight value

## Consequences

- **Positive**: Richer semantic understanding, better cluster evaluation, enhanced visualization capabilities
- **Negative**: Additional storage and computation requirements
- **Neutral**: Metrics are optional and computed post-analysis

## Implementation Requirements

1. Apply migration `016_metrics.sql`
2. Run `scripts/analyze_metrics.py` after `analyze_graph.py`
3. Update export scripts to include metrics data
4. Add Makefile target for metric analysis

## Verification & Enforcement

- **Cursor Rules:** 021 (Stats Proof), 022 (Visualization Contract Sync), 013 (Report Verification), 006 (AGENTS.md Governance)
- **CI:** `.github/workflows/verify-stats.yml` runs verifier and WebUI type-check/tests/build
- **Local Runbook:** `make doctor && make analyze.metrics && make verify.metrics`

## Related ADRs

- ADR-014: Relations and Patterns
- ADR-015: Graph Metadata
- ADR-010: Concept Network Architecture
