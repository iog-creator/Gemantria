BEGIN;
CREATE TABLE IF NOT EXISTS concept_metrics (
  concept_id UUID PRIMARY KEY,
  cluster_id INTEGER,
  semantic_cohesion FLOAT,
  bridge_score FLOAT,
  diversity_local FLOAT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS cluster_metrics (
  cluster_id INTEGER PRIMARY KEY,
  size INTEGER NOT NULL,
  density FLOAT,
  modularity FLOAT,
  semantic_diversity FLOAT,
  top_examples UUID[],
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE OR REPLACE VIEW v_metrics_overview AS
SELECT
  COUNT(*)::int AS node_ct,
  (SELECT COUNT(*) FROM concept_relations)::int AS edge_ct,
  (SELECT COUNT(DISTINCT cluster_id) FROM concept_clusters)::int AS cluster_ct,
  COALESCE((SELECT AVG(density) FROM cluster_metrics),0)::float AS avg_cluster_density,
  COALESCE((SELECT AVG(semantic_diversity) FROM cluster_metrics),0)::float AS avg_cluster_diversity;
COMMIT;
