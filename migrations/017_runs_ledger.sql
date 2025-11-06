-- Migration 017: Runs ledger for pipeline execution tracking
-- Tracks pipeline runs with versions, evidence, and status

BEGIN;

-- Runs ledger table
CREATE TABLE IF NOT EXISTS runs (
    run_id UUID PRIMARY KEY,
    book TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    status TEXT NOT NULL CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
    versions JSONB NOT NULL DEFAULT '{}'::jsonb,
    evidence JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_runs_book_status ON runs(book, status);
CREATE INDEX IF NOT EXISTS idx_runs_started_at ON runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);

-- Checkpoints table for LangGraph node snapshots
CREATE TABLE IF NOT EXISTS checkpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    node TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for efficient checkpoint retrieval
CREATE INDEX IF NOT EXISTS idx_checkpoints_run_id_node ON checkpoints(run_id, node);
CREATE INDEX IF NOT EXISTS idx_checkpoints_run_id_created ON checkpoints(run_id, created_at DESC);

COMMIT;

