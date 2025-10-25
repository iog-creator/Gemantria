BEGIN;

-- 1) Ensure relations table exists
CREATE TABLE IF NOT EXISTS concept_relations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id UUID NOT NULL,
  target_id UUID NOT NULL,
  cosine FLOAT NOT NULL,
  rerank_score FLOAT,
  decided_yes BOOLEAN,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT concept_relations_uniq UNIQUE (source_id, target_id)
);

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
