# ADR-064: RFC3339 Fast-Lane Contract for Graph Exports

## Status

Accepted — 2025-11-08. Evidence archived under `share/evidence/rfc3339-fastlane/`.

## Decision

All export persist paths MUST stamp `generated_at` as RFC3339 and set `metadata.source="fallback_fast_lane"`.

CI enforces:

- HINT-only on main/PRs.

- STRICT on release tags via `release-rfc3339-guard`.

## Rationale

Deterministic, auditable timestamps; avoids epoch drift from legacy runs.

## Consequences

Fail-closed on tags if contract is violated; normalization step converts legacy epochs.

## Evidence

- PR #260, #261, #262 merged.

- Workflow run log stored alongside HEAD in evidence bundle.

