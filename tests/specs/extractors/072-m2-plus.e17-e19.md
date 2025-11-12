# PLAN-072 M2+ — TVs E17–E19 (Graph Rollups, Audit Trail, Cross-batch Correlation)

Scope: Hermetic PR lane (no DB/network). Tool Bus OFF.

- **E17 — Graph-level provenance rollup:** `graph.meta.provenance_rollup` summarizes unique `model`s, `seed`s, and min/max `ts_iso`.

- **E18 — Per-node audit trail:** each node exposes `meta.audit` with `{batch_id, provenance_hash}`.

- **E19 — Cross-batch correlation:** a helper can correlate nodes across batches by stable keys (e.g., `data.idx`), returning a mapping `{key: [batch_ids...]}`.

Acceptance (this PR): tests are **xfail** until implementation lands; hermetic posture maintained.
