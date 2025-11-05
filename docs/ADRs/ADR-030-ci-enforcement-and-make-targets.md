# ADR-030: CI Enforcement via Rules Guard + Analytics Make Targets

## Status

Accepted

## Date

2025-11-04

## Related PRs

#016

## Rules

029 (ADR coverage), 027 (Docs sync), 050/051 OPS

## Context

We had governance rules but no hard, automated enforcement. Recent data issues showed policy drift risk.

## Decision

- Add CI workflow `System Enforcement` to run `scripts/rules_guard.py`, then `ruff format/check`.
- Expose `make exports.stats` and `make reports.generate` for deterministic analytics entrypoints.

## Consequences

- Fail-closed on missing docs/AGENTS.md/rules violations.
- Deterministic commands future PRs can rely on.
- Slight CI cost; large payoff in consistency.

## Implementation

- `.github/workflows/system-enforcement.yml` runs guard + ruff.
- Makefile targets call `scripts/export_stats.py` and `scripts/generate_report.py`.

## Verification

- CI green on PR-016; local runs produce governed exports.
