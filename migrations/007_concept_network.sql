BEGIN;

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Concept network table for storing embeddings
CREATE TABLE IF NOT EXISTS concept_network (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    concept_id      UUID NOT NULL,
    embedding       VECTOR(1024) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- Concept relations table for storing similarity relationships
CREATE TABLE IF NOT EXISTS concept_relations (
    source_id       UUID NOT NULL REFERENCES concept_network(id) ON DELETE CASCADE,
    target_id       UUID NOT NULL REFERENCES concept_network(id) ON DELETE CASCADE,
    similarity      DOUBLE PRECISION NOT NULL CHECK (similarity BETWEEN 0 AND 1),
    relation_type   TEXT CHECK (relation_type IN ('strong','weak')),
    created_at      TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (source_id, target_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_concept_network_concept_id
    ON concept_network (concept_id);

CREATE INDEX IF NOT EXISTS idx_concept_network_embedding
    ON concept_network USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_concept_relations_similarity
    ON concept_relations (similarity DESC);

CREATE INDEX IF NOT EXISTS idx_concept_relations_type
    ON concept_relations (relation_type);

-- Note: concept_id references noun_id from pipeline processing
-- No foreign key constraint as nouns are processed in-memory

COMMIT;
