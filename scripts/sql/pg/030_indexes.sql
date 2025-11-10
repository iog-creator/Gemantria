-- 030_indexes.sql
-- Performance indexes for Postgres-First SSOT
-- Idempotent: safe to run multiple times

BEGIN;

-- ===============================
-- GEMATRIA SCHEMA INDEXES
-- ===============================

-- Nodes: content_hash lookup, book/chapter/verse queries
CREATE INDEX IF NOT EXISTS idx_nodes_content_hash ON gematria.nodes(content_hash);
CREATE INDEX IF NOT EXISTS idx_nodes_book_chapter_verse ON gematria.nodes(book, chapter, verse);
CREATE INDEX IF NOT EXISTS idx_nodes_class ON gematria.nodes(class);
CREATE INDEX IF NOT EXISTS idx_nodes_gematria_value ON gematria.nodes(gematria_value);

-- Edges: source/destination lookups, edge type, strength filtering
CREATE INDEX IF NOT EXISTS idx_edges_src ON gematria.edges(src_node_id);
CREATE INDEX IF NOT EXISTS idx_edges_dst ON gematria.edges(dst_node_id);
CREATE INDEX IF NOT EXISTS idx_edges_type ON gematria.edges(edge_type);
CREATE INDEX IF NOT EXISTS idx_edges_strength ON gematria.edges(edge_strength DESC) WHERE edge_strength IS NOT NULL;

-- AI embeddings: node lookup, vector similarity (commented - see vector indexes below)
CREATE INDEX IF NOT EXISTS idx_ai_embeddings_node ON gematria.ai_embeddings(node_id);
CREATE INDEX IF NOT EXISTS idx_ai_embeddings_model ON gematria.ai_embeddings(model_name);

-- Full-text search (GIN indexes on text fields)
CREATE INDEX IF NOT EXISTS idx_nodes_hebrew_fts ON gematria.nodes USING gin(to_tsvector('english', hebrew_text)) WHERE hebrew_text IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_nodes_surface_fts ON gematria.nodes USING gin(to_tsvector('english', surface));

-- JSONB indexes (evidence, meta fields)
CREATE INDEX IF NOT EXISTS idx_edges_evidence_gin ON gematria.edges USING gin(evidence);

-- ===============================
-- TELEMETRY SCHEMA INDEXES
-- ===============================

-- Metrics log: time-series queries (BRIN for large tables)
CREATE INDEX IF NOT EXISTS idx_metrics_log_run ON telemetry.metrics_log(run_id);
CREATE INDEX IF NOT EXISTS idx_metrics_log_thread ON telemetry.metrics_log(thread_id);
CREATE INDEX IF NOT EXISTS idx_metrics_log_node_ts ON telemetry.metrics_log(node, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_log_event_ts ON telemetry.metrics_log(event, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_log_workflow_ts ON telemetry.metrics_log(workflow, started_at DESC);
-- BRIN index for time-series (efficient for large, append-only tables)
CREATE INDEX IF NOT EXISTS idx_metrics_log_started_at_brin ON telemetry.metrics_log USING brin(started_at);

-- AI interactions: session lookups, time-based queries
CREATE INDEX IF NOT EXISTS idx_ai_interactions_session ON telemetry.ai_interactions(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_interactions_created_at ON telemetry.ai_interactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_interactions_type ON telemetry.ai_interactions(interaction_type);

-- Checkpointer: thread lookups
CREATE INDEX IF NOT EXISTS idx_checkpointer_thread ON telemetry.checkpointer_state(thread_id);
CREATE INDEX IF NOT EXISTS idx_checkpointer_created_at ON telemetry.checkpointer_state(created_at DESC);

-- ===============================
-- OPS SCHEMA INDEXES
-- ===============================

-- Job queue: status filtering, time-based queries
CREATE INDEX IF NOT EXISTS idx_job_queue_status ON ops.job_queue(status) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_job_queue_created_at ON ops.job_queue(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_job_queue_type ON ops.job_queue(job_type);

-- ===============================
-- VECTOR SIMILARITY INDEXES (commented - enable after P3)
-- ===============================

-- HNSW index for fast approximate nearest neighbor search
-- CREATE INDEX IF NOT EXISTS idx_ai_embeddings_vector_hnsw ON gematria.ai_embeddings
--     USING hnsw (embedding vector_cosine_ops)
--     WITH (m = 16, ef_construction = 64);

-- IVFFlat index (alternative to HNSW, faster build, slower query)
-- CREATE INDEX IF NOT EXISTS idx_ai_embeddings_vector_ivfflat ON gematria.ai_embeddings
--     USING ivfflat (embedding vector_cosine_ops)
--     WITH (lists = 100);

COMMIT;

