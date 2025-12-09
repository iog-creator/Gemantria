# Gemantria — Phase-8 Plan (Scope & Milestones)

> Source of truth for Phase-8 goals; no CI/gate changes. Use alongside `docs/INDEX.md`.

## Objectives (P0)
- Reliable end-to-end graph updates with checkpointing (now in main).
- Deterministic batch semantics (single DEFAULT_BATCH_SIZE + env override).
- Bible DB strict read-only consumption (no writes to scripture tables).
- Governance continuity: Rule-037/038 gates, share no-drift, NEXT_STEPS.

## Deliverables (P0 → P1)
- P0: Evaluation harness skeleton (local smoke only), dataset notes, success metrics grid.
- P1: Automated eval report artifacts in `/share` (future PR; not part of this commit).

## Success Metrics (initial)
- Export integrity: 100% Rule-038 pass
- Join/coverage sanity: 100% Rule-037 pass
- Eval smoke: 100% tasks reach "OK" (non-flaky)
- Latency budget: TBD after real run; target p95 export step ≤ N sec

## Workstream Anchors
- Checkpointer usage patterns, Batch processor invariants, RO Bible node integration, Export smoke expansions (future), Reranker hygiene.
