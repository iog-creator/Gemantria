# Phase 11 Planning Brief (Accelerated, 3 Days) — UI Edge Audit

## Objective

Hard-audit the UI for edge-cases: large datasets, low-spec devices, accessibility, export reliability, and model-workflow metrics.

## Scope

- Performance with very large envelopes (>100k nodes/edges); chunked rendering/pagination and summary-only fallback.

- Graceful handling of missing/incomplete fields (`year`, `start_year`, `end_year`).

- Accessibility audit (keyboard navigation, screen reader) incl. axe/WAVE checks; mobile/low-spec performance.

- Export pipeline resilience: UI "safe mode" when envelope missing/empty.

- Model workflow metrics: track Gemini vs Claude usage, iteration counts, escalation threshold review.

## Deliverables

- UI refactor for edge loads (chunked/summary views).

- Acceptance scripts: timed load/memory checks; accessibility smoke.

- Updated docs: performance guidance + fallback behaviors.

- Metrics mini-dashboard: iteration counts, escalations, and benchmark-aligned facets (RACE/COMPASS).

- Governance update if thresholds change (e.g., escalate after 1 iteration).

## Timeline (3 Days)

- **Day 1**: Kick-off; define metrics aligned to **RACE** (Readability, mAintainability, Correctness, Efficiency) and **COMPASS** (Correctness, Efficiency, Code Quality); instrument logging.

- **Day 2**: Implement UI refactor for large envelopes; add acceptance scripts (perf/memory); wire accessibility smoke.

- **Day 3**: Run audit on targets; team retro using "Liked/Learned/Lacked/Longed For"; finalize docs; merge.

## Risks & Mitigations

- Large-envelope slowdown → chunked rendering/pagination; summary view fallback.

- Cost/quality drift in model usage → track iterations/escalations; adjust escalation rule.

- Accessibility gaps → automated axe/WAVE + manual checks; document fixes.

- Export contract break → keep JSONL + envelope stable; version if changed; deprecate with warnings.

## Notes

- Keep UI work hermetic/local; no CI/Node changes.

- Preserve SSOT gates (`ruff format/check`) and existing Make targets.
