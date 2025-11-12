# PLAN-072 M2+ — Extraction Agents TVs (E06–E10)

Scope: Hermetic PR lane (no DB/network). Tool Bus OFF.

- **E06 — Provenance fields present**: every extractor output MUST include `model`, `seed`, `ts_iso` (RFC3339).

- **E07 — RFC3339 timestamp**: `ts_iso` parses as RFC3339; monotonic within batch.

- **E08 — Negative (missing model)**: missing `model` is a guardable error.

- **E09 — Negative (seed type)**: `seed` must be an integer; non-int is error.

- **E10 — Edge case (empty analysis)**: empty/whitespace `analysis` allowed but must not drop provenance.

Acceptance in PR lane: tests are marked **xfail** until implementation; guard stays hermetic.
