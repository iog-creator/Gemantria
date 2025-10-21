-- Migration: Add Qwen Health Log Table
-- Purpose: Store evidence of Qwen model availability checks for production verification
-- Created: PR-011b No-Mocks Enforcement + Live Qwen Gates

CREATE TABLE IF NOT EXISTS qwen_health_log (
    id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL,
    embedding_model TEXT NOT NULL,
    reranker_model TEXT NOT NULL,
    embed_dim INT,
    lat_ms_embed INT,
    lat_ms_rerank INT,
    verified BOOLEAN NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Index for efficient queries by run_id and recent health checks
CREATE INDEX IF NOT EXISTS idx_qwen_health_log_run_id ON qwen_health_log(run_id);
CREATE INDEX IF NOT EXISTS idx_qwen_health_log_created_at ON qwen_health_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_qwen_health_log_verified ON qwen_health_log(verified);

-- Comments for documentation
COMMENT ON TABLE qwen_health_log IS 'Stores Qwen model health check results for production verification';
COMMENT ON COLUMN qwen_health_log.run_id IS 'Pipeline run ID this health check belongs to';
COMMENT ON COLUMN qwen_health_log.embedding_model IS 'Name of embedding model verified';
COMMENT ON COLUMN qwen_health_log.reranker_model IS 'Name of reranker model verified';
COMMENT ON COLUMN qwen_health_log.embed_dim IS 'Embedding dimension verified (should be 1024)';
COMMENT ON COLUMN qwen_health_log.lat_ms_embed IS 'Latency in ms for embedding dry-run test';
COMMENT ON COLUMN qwen_health_log.lat_ms_rerank IS 'Latency in ms for reranker dry-run test';
COMMENT ON COLUMN qwen_health_log.verified IS 'Whether health check passed';
COMMENT ON COLUMN qwen_health_log.reason IS 'Human-readable result or failure reason';
