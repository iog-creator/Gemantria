# Phase-9 — Real-Data Ingestion (Plan Only)

Status: plan-only PR; CI hermetic (no network/DB). Local profiles documented.



## Goals

- Define ingestion harness interfaces (reader, validator, snapshot rotation).

- Specify env: DATABASE_URL/PG* (local only), SNAPSHOT_DIR, MAX_ROWS (caps).

- Prove hermeticity: `make ci.ingest.check` must HINT+exit 0 in CI.



## Contracts

- No writes to share/ in CI.

- No outbound network in CI.

- Rerun-safe: idempotent snapshots; deterministic seeds.



## Next

- P9-A: stub harness + local README

- P9-B: validator + metrics envelope
