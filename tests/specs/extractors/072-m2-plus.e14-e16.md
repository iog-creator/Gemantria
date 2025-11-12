# PLAN-072 M2+ — TVs E14–E16 (Provenance Propagation & Batch ID)

Scope: Hermetic PR lane (no DB/network). Tool Bus OFF.

- **E14 — Propagation to graph nodes**: Extractor outputs MUST carry `model`, `seed`, `ts_iso` into downstream graph nodes (e.g., `node.meta.provenance`).

- **E15 — Missing-provenance hard fail**: Graph assembler MUST raise a guardable error when any node lacks required provenance.

- **E16 — Batch ID (UUIDv7) determinism**: Each batch gets a `batch_id` (UUIDv7) generated from a fixed `(base_dt, seed)` pair; identical inputs → identical `batch_id`.

Acceptance (this PR): tests are **xfail** until implementation lands; remains hermetic.
