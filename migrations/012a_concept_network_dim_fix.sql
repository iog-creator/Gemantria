-- Migration: Fix Concept Network Vector Dimension
-- Purpose: Change vector dimension if runtime guard shows mismatch
-- Created: PR-012 (optional - run only if VECTOR_DIM != current column dimension)
-- Example: Change to 1024; adjust if needed (e.g., to 1536)

-- WARNING: This will alter existing data - backup first!
-- ALTER TABLE concept_network
--   ALTER COLUMN embedding TYPE vector(1024);

-- Example for different dimensions:
-- ALTER TABLE concept_network ALTER COLUMN embedding TYPE vector(1536);
-- ALTER TABLE concept_network ALTER COLUMN embedding TYPE vector(768);
