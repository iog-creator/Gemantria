-- Phase-1 Indexes / constraints

-- Concepts table indexes
CREATE INDEX IF NOT EXISTS idx_concepts_name ON gematria.concepts(name);
CREATE INDEX IF NOT EXISTS idx_concepts_hash ON gematria.concepts(content_hash);
CREATE INDEX IF NOT EXISTS idx_concepts_gematria ON gematria.concepts(gematria_value);

-- Relations table indexes
CREATE INDEX IF NOT EXISTS idx_relations_src ON gematria.concept_relations(src_concept_id);
CREATE INDEX IF NOT EXISTS idx_relations_dst ON gematria.concept_relations(dst_concept_id);
CREATE INDEX IF NOT EXISTS idx_relations_type ON gematria.concept_relations(relation_type);

-- Avoid duplicate directed edges of same type
CREATE UNIQUE INDEX IF NOT EXISTS uq_relations_src_dst_type
ON gematria.concept_relations(src_concept_id, dst_concept_id, relation_type);

-- Concept network indexes
CREATE INDEX IF NOT EXISTS idx_concept_network_concept_id ON gematria.concept_network(concept_id);

-- Concept clusters indexes
CREATE INDEX IF NOT EXISTS idx_concept_clusters_cluster_id ON gematria.concept_clusters(cluster_id);
