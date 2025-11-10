-- 010_schemas.sql
-- Create schemas for Postgres-First SSOT organization
-- Idempotent: safe to run multiple times

BEGIN;

-- Domain graph: nodes, edges, embeddings, derived summaries
CREATE SCHEMA IF NOT EXISTS gematria;

-- Telemetry: metrics, AI interactions, checkpointer state
CREATE SCHEMA IF NOT EXISTS telemetry;

-- Operations: job queue, outbox, materialized views, admin helpers
CREATE SCHEMA IF NOT EXISTS ops;

COMMIT;

