-- Phase 13, Step 3: Vector Unification DDL Migration
-- Migrates bible.verses.embedding from vector(768) to vector(1024)
--
-- WARNING: This is a DESTRUCTIVE operation that requires:
-- 1. Full backup of bible_db before execution
-- 2. Full corpus re-embedding using BGE-M3 (1024-D)
-- 3. Downtime during migration
--
-- Execution: Run via psql as superuser with bible_db maintenance mode enabled
--
-- Governance: Rules 063 (Git Safety), 004 (PR Workflow)

BEGIN;

-- Step 1: Verify current state
DO $$
DECLARE
    current_typmod INTEGER;
BEGIN
    SELECT atttypmod INTO current_typmod
    FROM pg_attribute
    WHERE attrelid = 'bible.verses'::regclass
      AND attname = 'embedding';
    
    -- For pgvector, atttypmod directly stores the dimension
    IF current_typmod != 768 THEN
        RAISE EXCEPTION 'Expected embedding dimension 768, found %', current_typmod;
    END IF;
    
    RAISE NOTICE 'Current embedding dimension: %', current_typmod;
END $$;

-- Step 2: Drop dependent indexes (HNSW index on 768-D column)
DROP INDEX IF EXISTS bible.verses_embedding_idx;

-- Step 3: NULL all existing embeddings (required for dimension change)
-- WARNING: This is the DESTRUCTIVE step - all 116k+ embeddings will be lost
UPDATE bible.verses SET embedding = NULL;

-- Step 4: Alter column to 1024-D
ALTER TABLE bible.verses
    ALTER COLUMN embedding TYPE vector(1024);

-- Step 5: Create new HNSW index for 1024-D
CREATE INDEX verses_embedding_1024_idx 
    ON bible.verses 
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Step 5: Verify new state
DO $$
DECLARE
    new_typmod INTEGER;
BEGIN
    SELECT atttypmod INTO new_typmod
    FROM pg_attribute
    WHERE attrelid = 'bible.verses'::regclass
      AND attname = 'embedding';
    
    IF new_typmod != 1024 THEN
        RAISE EXCEPTION 'Migration failed: dimension is %, expected 1024', new_typmod;
    END IF;
    
    RAISE NOTICE 'Migration successful: new dimension = %', new_typmod;
END $$;

COMMIT;

-- Post-migration checklist:
-- [ ] Verify bible.verses.embedding is now vector(1024)
-- [ ] Verify HNSW index exists for 1024-D
-- [ ] Run full re-embedding script (scripts/backfill_bge_embeddings.py)
-- [ ] Verify vector search returns results
-- [ ] Run integration tests
