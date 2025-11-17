-- Migration: control.doc_registry_schema
-- Purpose: Add doc_registry, doc_version, and doc_sync_state tables
-- Context: Postgres Doc Registry Plan (DOC_REGISTRY_PLAN.md)
-- Notes:
--   - Uses control schema introduced in earlier migrations.
--   - Only tracks metadata / hashes, not full document contents.

BEGIN;

CREATE SCHEMA IF NOT EXISTS control;

CREATE TABLE IF NOT EXISTS control.doc_registry (
    doc_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    logical_name  TEXT NOT NULL UNIQUE, -- e.g. "AGENTS_ROOT", "MASTER_PLAN"
    role          TEXT NOT NULL,        -- e.g. "ssot", "runbook", "analysis", "derived"
    repo_path     TEXT NOT NULL,        -- e.g. "AGENTS.md"
    share_path    TEXT,                 -- e.g. "share/AGENTS.md" (if derived)
    is_ssot       BOOLEAN NOT NULL,     -- TRUE for canonical repo docs
    enabled       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS control.doc_version (
    id           BIGSERIAL PRIMARY KEY,
    doc_id       UUID NOT NULL REFERENCES control.doc_registry(doc_id) ON DELETE CASCADE,
    git_commit   TEXT,                  -- optional git SHA
    content_hash TEXT NOT NULL,         -- SHA-256 of the file contents
    size_bytes   BIGINT NOT NULL,
    recorded_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS control.doc_sync_state (
    id             BIGSERIAL PRIMARY KEY,
    doc_id         UUID NOT NULL REFERENCES control.doc_registry(doc_id) ON DELETE CASCADE,
    target         TEXT NOT NULL,       -- e.g. "share", "atlas_export"
    last_synced_at TIMESTAMPTZ,
    last_hash      TEXT,
    status         TEXT NOT NULL,       -- "ok", "stale", "error"
    message        TEXT,
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMIT;
