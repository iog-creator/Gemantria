# PLAN-072 M2+ — Extraction Agents TVs (E06–E10)

Scope: PR lane, hermetic (no DB/network). Tool Bus OFF.

- E06 — Provenance present: every output has `model`, `seed`, `ts_iso` (RFC3339).

- E07 — RFC3339: `ts_iso` validates; within-batch monotonic.

- E08 — Negative: missing `model` is guardable error.

- E09 — Negative: `seed` must be integer.

- E10 — Edge: empty `analysis` still preserves provenance fields.

Acceptance (this PR): tests marked xfail until implementation; ruff green; spec added.

