-- 000_extensions.sql
-- Enable required PostgreSQL extensions for Postgres-First SSOT
-- Idempotent: safe to run multiple times

BEGIN;

-- Vector similarity search (pgvector)
CREATE EXTENSION IF NOT EXISTS vector;

-- Trigram fuzzy matching
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Query performance monitoring
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Case-insensitive text
CREATE EXTENSION IF NOT EXISTS citext;

-- Cryptographic functions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Optional: scheduled jobs (requires superuser or managed service)
-- CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Optional: foreign data wrappers (for cross-DB queries)
-- CREATE EXTENSION IF NOT EXISTS postgres_fdw;

COMMIT;

