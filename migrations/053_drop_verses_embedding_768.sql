-- Phase 3: Vector Dimension Cleanup - Remove deprecated 768-D embedding column
-- 
-- This migration removes the deprecated bible.verses.embedding (vector(768)) column
-- and its HNSW index. All vector operations now use bible.verse_embeddings.embedding (vector(1024)).
--
-- Rationale:
-- - bible.verse_embeddings.embedding (1024-D) is the canonical source for vector similarity
-- - 768-D column in bible.verses.embedding is deprecated and unused
-- - Removing it simplifies the schema and eliminates dimension confusion
--
-- See:
-- - docs/SSOT/BIBLESCHOLAR_MIGRATION_PLAN.md
-- - agentpm/biblescholar/vector_adapter.py (uses verse_embeddings.embedding only)

-- Drop the HNSW index on verses.embedding (if it exists)
DROP INDEX IF EXISTS bible.verses_embedding_idx;

-- Drop the embedding column from bible.verses table
ALTER TABLE bible.verses DROP COLUMN IF EXISTS embedding;

-- Add comment documenting the change
COMMENT ON TABLE bible.verses IS 'Primary verse storage. Vector embeddings are stored in bible.verse_embeddings.embedding (vector(1024)), not in this table.';

