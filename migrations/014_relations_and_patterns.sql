BEGIN;

-- 1) Ensure relations table exists and has required columns
-- Migration 007 created basic table, this adds missing columns
CREATE TABLE IF NOT EXISTS concept_relations (
  source_id UUID NOT NULL,
  target_id UUID NOT NULL,
  similarity DOUBLE PRECISION,
  relation_type TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (source_id, target_id)
);

-- Add missing columns if they don't exist
DO $$
BEGIN
    -- Add cosine column if missing (rename similarity to cosine)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'concept_relations' AND column_name = 'cosine') THEN
        ALTER TABLE concept_relations ADD COLUMN cosine FLOAT;
        -- Copy similarity values to cosine if they exist
        UPDATE concept_relations SET cosine = similarity WHERE similarity IS NOT NULL;
    END IF;

    -- Add rerank_score column if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'concept_relations' AND column_name = 'rerank_score') THEN
        ALTER TABLE concept_relations ADD COLUMN rerank_score FLOAT;
    END IF;

    -- Add decided_yes column if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'concept_relations' AND column_name = 'decided_yes') THEN
        ALTER TABLE concept_relations ADD COLUMN decided_yes BOOLEAN;
    END IF;
END $$;

-- Optional helpful index
CREATE INDEX IF NOT EXISTS idx_concept_relations_pair
  ON concept_relations (source_id, target_id);

-- 2) Clusters
CREATE TABLE IF NOT EXISTS concept_clusters (
  concept_id UUID PRIMARY KEY,
  cluster_id INTEGER NOT NULL,
  modularity FLOAT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3) Centrality
CREATE TABLE IF NOT EXISTS concept_centrality (
  concept_id UUID PRIMARY KEY,
  degree FLOAT,
  betweenness FLOAT,
  eigenvector FLOAT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 4) Views (robust to missing rows)
CREATE OR REPLACE VIEW v_concept_relations_health AS
SELECT
  COUNT(*)::int AS edge_ct,
  COALESCE(AVG(cosine),0)::float AS avg_cosine,
  SUM((cosine >= 0.90)::int)::int AS strong_edges,
  SUM((cosine >= 0.75 AND cosine < 0.90)::int)::int AS weak_edges,
  COALESCE(AVG(rerank_score),0)::float AS avg_rerank_score,
  COALESCE(AVG((decided_yes::int)),0)::float AS rerank_yes_ratio
FROM concept_relations;

COMMIT;
