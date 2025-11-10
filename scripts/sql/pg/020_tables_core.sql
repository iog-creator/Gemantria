-- 020_tables_core.sql
-- Core tables for Postgres-First SSOT
-- Idempotent: safe to run multiple times
-- Note: Existing migrations may have created some of these; this is additive

BEGIN;

-- ===============================
-- GEMATRIA SCHEMA: Domain Graph
-- ===============================

-- Nodes (concepts/nouns) - may already exist via migrations
CREATE TABLE IF NOT EXISTS gematria.nodes (
    node_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    surface TEXT NOT NULL,
    hebrew_text TEXT,
    gematria_value INTEGER,
    class TEXT,
    book TEXT,
    chapter INTEGER,
    verse INTEGER,
    content_hash TEXT UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Edges (relationships) - may already exist via migrations
CREATE TABLE IF NOT EXISTS gematria.edges (
    edge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    src_node_id UUID NOT NULL REFERENCES gematria.nodes(node_id) ON DELETE CASCADE,
    dst_node_id UUID NOT NULL REFERENCES gematria.nodes(node_id) ON DELETE CASCADE,
    edge_type TEXT NOT NULL,
    cosine_similarity NUMERIC(6,5),
    rerank_score NUMERIC(6,5),
    edge_strength NUMERIC(6,5), -- blend: 0.5*cosine + 0.5*rerank
    evidence JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- AI embeddings (vector storage)
CREATE TABLE IF NOT EXISTS gematria.ai_embeddings (
    embedding_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_id UUID NOT NULL REFERENCES gematria.nodes(node_id) ON DELETE CASCADE,
    embedding VECTOR(1024) NOT NULL,
    model_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ===============================
-- TELEMETRY SCHEMA: Metrics & Events
-- ===============================

-- Metrics log (time-series) - may already exist in gematria schema
CREATE TABLE IF NOT EXISTS telemetry.metrics_log (
    id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL,
    workflow TEXT NOT NULL,
    thread_id TEXT NOT NULL,
    node TEXT NOT NULL,
    event TEXT NOT NULL CHECK (event IN ('node_start','node_end','node_error','pipeline_start','pipeline_end')),
    status TEXT NOT NULL CHECK (status IN ('ok','error','skip')),
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    duration_ms NUMERIC,
    items_in INTEGER,
    items_out INTEGER,
    error_json JSONB,
    meta JSONB
);

-- AI interactions - may already exist in public schema
CREATE TABLE IF NOT EXISTS telemetry.ai_interactions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    interaction_type VARCHAR(50) NOT NULL,
    user_query TEXT,
    ai_response TEXT,
    tools_used TEXT[],
    context_provided JSONB,
    execution_time_ms INTEGER,
    success BOOLEAN DEFAULT true,
    error_details TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Checkpointer state (LangGraph persistence)
CREATE TABLE IF NOT EXISTS telemetry.checkpointer_state (
    checkpoint_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id TEXT NOT NULL,
    checkpoint_data JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ===============================
-- OPS SCHEMA: Operations & Admin
-- ===============================

-- Job queue (placeholder - see 060_queue.sql for full implementation)
CREATE TABLE IF NOT EXISTS ops.job_queue (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','running','completed','failed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT
);

COMMIT;

