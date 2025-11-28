-- Migration: Add tool discovery columns to mcp.tools
-- Purpose: Enable semantic search and metadata filtering for MCP tool catalog
-- Date: 2025-11-22

-- Add embedding column for semantic search (1024-dim for BGE-M3/Granite)
ALTER TABLE mcp.tools ADD COLUMN IF NOT EXISTS embedding vector(1024);

-- Add metadata columns
ALTER TABLE mcp.tools ADD COLUMN IF NOT EXISTS subsystem TEXT;
ALTER TABLE mcp.tools ADD COLUMN IF NOT EXISTS visibility TEXT DEFAULT 'internal';
ALTER TABLE mcp.tools ADD COLUMN IF NOT EXISTS popularity_score INT DEFAULT 0;

-- Create HNSW index for semantic tool search
-- Note: Requires pgvector extension (should already be installed)
CREATE INDEX IF NOT EXISTS mcp_tools_embedding_hnsw
  ON mcp.tools
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- Update existing BibleScholar tools with metadata
UPDATE mcp.tools
SET subsystem = 'biblescholar',
    visibility = 'internal'
WHERE tags @> '{biblescholar}';

-- Add comment
COMMENT ON COLUMN mcp.tools.embedding IS '1024-dimensional embedding vector for semantic search (BGE-M3/Granite)';
COMMENT ON COLUMN mcp.tools.subsystem IS 'Subsystem identifier (e.g., biblescholar, knowledge, etc.)';
COMMENT ON COLUMN mcp.tools.visibility IS 'Tool visibility: internal (default) or external';
COMMENT ON COLUMN mcp.tools.popularity_score IS 'Popularity/usage score for ranking (higher = more popular)';

