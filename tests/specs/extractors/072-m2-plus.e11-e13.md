# PLAN-072 M2+ — TVs E11–E13 (Determinism & Stable Ordering)

Scope: Hermetic PR lane (no DB/network). Tool Bus OFF.

- **E11 — Deterministic batch clock (API change)**: `stamp_batch(items, model, seed, base_dt)` MUST accept an injected UTC base datetime. With identical `(items, model, seed, base_dt)`, outputs MUST be identical.

- **E12 — Stable ordering**: Output order MUST match input order exactly (1:1 positional stability).

- **E13 — Seed separation**: With same `(items, base_dt)` but different `seed`, only the `seed` field changes; `ts_iso` sequence remains monotonic and identical.

Acceptance in PR lane: tests are **xfail** until implementation updates `provenance.stamp_batch` to support `base_dt` and determinism.
