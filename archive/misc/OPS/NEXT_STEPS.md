# Gemantria – NEXT STEPS (Ops Backlog, v1)

> SSOT link: RULES_INDEX.md • Triad: 050/051/052 • Tag lane: ops.tagproof (STRICT)

## A. DSN Centralization (burn-down)

- [x] PR: ops/dsn-burndown-1 — migrated first batch of Python offenders to centralized loader (see evidence: dsn.burndown-1.changed.txt).
- [ ] Migrate 3–5 paths from `scripts/guards/.dsn_direct.allowlist` per PR until empty.
- [ ] When empty: add `guard.dsn.centralized.strict` to `ops.tagproof` (if not already present).
- [ ] Add a short ADR after de-allowlisting (why centralization, precedence, guards).

## B. Atlas (Browser Hub + Proofs)

- [ ] Ship `docs/atlas/index.html` (Mermaid included; backlink to evidence).
- [ ] Script: generate Mermaid from **metrics_log** & **checkpointer_state** (read-only).
- [ ] Views: `execution_live.mmd`, `pipeline_flow_historical.mmd`, `dependencies.mmd`, `kpis.mmd`.
- [ ] Verify via browser snapshot in CI (required by policy).

## C. Pipeline Quality (from earlier plan)

- [ ] **Extraction correctness**: fix book ingestion edge cases; add `book.smoke` expansion.
- [ ] **Reranking stage**: finish and gate with eval JSON; expose COMPASS/thresholds.
- [ ] **Exports & UI p90 tile**: ensure `ui/` metrics card uses latest exports (file-first).

## D. Evidence Hardening

- [ ] Secrets masking guard (file/evidence scan): no `postgresql://user:` in artifacts.
- [ ] Extend tagproof to upload evidence index (JSON) for each tag.

## E. Operational Hygiene

- [ ] Backfill unit tests for env loader edge cases (socket DSNs, query params).
- [ ] Teach-mode docs: "How DSNs flow" (diagram + examples).

**Working rule**: one concern per PR; keep PRs small and evidence-first.

