-- Migration: Add Concept Network Verification Views
-- Purpose: Provide SQL views to verify persistence and dimensional health of embeddings
-- Created: PR-012 Fix Network Persistence (Dims Check, Auto-Commit, Verification View)

-- View to verify concept network persistence and dimensional health
CREATE OR REPLACE VIEW v_concept_network_health AS
SELECT
  COUNT(*)                           AS node_ct,
  AVG(vector_dims(embedding))::int   AS avg_dim,
  MIN(vector_dims(embedding))::int   AS min_dim,
  MAX(vector_dims(embedding))::int   AS max_dim,
  AVG(embedding <#> embedding)       AS avg_self_l2,   -- sanity (should be 0 on pgvector >=0.6; else NULL)
  NOW()                               AS observed_at
FROM concept_network;

-- View to verify concept relations health
CREATE OR REPLACE VIEW v_concept_relations_health AS
SELECT
  COUNT(*)                                         AS edge_ct,
  AVG(cosine)                                      AS avg_cosine,
  AVG(rerank_score)                                AS avg_rerank,
  AVG(edge_strength)                               AS avg_strength,
  COUNT(*) FILTER (WHERE relation_type='strong')   AS strong_ct,
  COUNT(*) FILTER (WHERE relation_type='weak')     AS weak_ct,
  NOW()                                            AS observed_at
FROM concept_relations;
