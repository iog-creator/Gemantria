# ADR-031: SSOT Analytics Schemas & Report Plumbing

## Status

Accepted

## Date

2025-11-04

## Related PRs

#017

## Rules

029 (ADR coverage), 037/038 (Data/Exports integrity)

## Context

We need governed analytics outputs (stats, patterns, temporal, forecast) consumable by UI/ops.

## Decision

- Introduce JSON Schemas: `graph-stats`, `graph-patterns`, `temporal-patterns`, `pattern-forecast`.
- Provide exporters (`scripts/export_stats.py`) and report generator (`scripts/generate_report.py`) that validate outputs against SSOT before writing.

## Consequences

- Strong contract for UI/backend; deterministic artifacts.
- Strict validation may fail PRs with malformed data (desired).

## Implementation

- Schemas under `docs/SSOT/`.
- Exports to `exports/*.json`; reports via `make reports.generate`.

## Verification

- Local `make exports.stats && make reports.generate` succeed; CI verifies schema conformance post-merge.
