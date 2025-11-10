# ADR-065 — Postgres-First SSOT for Gemantria

**Status:** Proposed → Trial (HINT)  

This ADR declares **Postgres as the Single Source of Truth** (SSOT) for policy/telemetry/graph artifacts. Files remain **mirrors/pointers** so CI can run without secrets (HINT). STRICT enforces DB-first once a read-only DSN is provided.

## Decisions

- **DB-first SSOT**; files mirror via guards/exports.

- **Extensions:** vector, pg_trgm, pg_stat_statements, citext, pgcrypto (optional: pg_cron, fdw).

- **Schemas:** gematria (domain), telemetry (events), ops (queue/ops).

- **Patterns:** FTS (tsvector+GIN), pg_trgm fuzzy, pgvector (1024 dims; HNSW/IVFFlat), partitioned time-series + BRIN, SKIP LOCKED queue + NOTIFY, matviews for Atlas, RLS for tenants.

- **Rollout:** HINT by default; STRICT on DSN with autofix of mirrors.

## Phases

P0 Readiness → P1 Extensions/Schemas → P2 FTS → P3 Vectors → P4 Queue/NOTIFY → P5 Observability → P6 RLS → P7 Replication/FDW.

