# ADR-065 — Postgres-First SSOT for Gemantria

**Status:** Trial (HINT) → Enforced (STRICT, DB-as-SSOT)

## Decision

Postgres is the **Single Source of Truth (SSOT)** for governance (Always-Apply 050/051/052), telemetry, and graph artifacts. Repo files are **pointers/mirrors**. CI defaults to **HINT** (no secrets); **STRICT** requires a DSN and fails closed on drift.

## Architecture

- **Schemas**
  - `gematria`: domain graph (nodes, edges, ai_embeddings), derived summaries
  - `telemetry`: metrics_log (time-series), ai_interactions, checkpointer_state
  - `ops`: job queue, outbox, matviews, admin helpers

- **Extensions**: `vector` (pgvector), `pg_trgm`, `pg_stat_statements`, `citext`, `pgcrypto` (optional: `pg_cron`, FDWs)

- **Indexes/Scale**: GIN (FTS/jsonb), BRIN (time-series), HNSW/IVFFlat (vector), partitioning on telemetry

- **Security**: RO/ RW roles with least privilege; RLS for multi-tenant; proofs always RO

## Rollout Phases

P0 Readiness (this ADR + SQL skeletons + Make targets)  
P1 Extensions & Schemas (idempotent DDL)  
P2 FTS & Trigrams  
P3 Vector search (dims=1024; HNSW/IVF)  
P4 Queue + LISTEN/NOTIFY  
P5 Observability (pg_stat_statements, auto_explain*)  
P6 RLS & tenant policy  
P7 Replication/FDW (if needed)

*auto_explain requires superuser or managed service capability.

## Operations

- **DSNs**: `ATLAS_DSN` (RO proofs), `ATLAS_DSN_RW` (constrained DDL). Never echo secrets.

- **Guards**: DB-first `guard.alwaysapply.dbmirror` (STRICT), pointer sentinels in `AGENTS.md` / `RULES_INDEX.md`.

- **Browser**: Atlas/Pages proofs must be visually verified (serve `docs/`).

## Consequences

- CI stays hermetic; PRs don't need secrets (HINT).  
- On STRICT, DB → files is enforced; mirrors drift causes failure (autofix path available).
