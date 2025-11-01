-- Phase-1 Base Schema (gematria) — v6.2.3

CREATE SCHEMA IF NOT EXISTS gematria;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

-- Core concepts table (from migration 037)
CREATE TABLE IF NOT EXISTS gematria.concepts (
  concept_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name              TEXT NOT NULL,
  hebrew_text       TEXT,
  gematria_value    INTEGER,
  strong_number     TEXT,
  primary_verse     TEXT,
  book              TEXT,
  chapter           INTEGER,
  freq              INTEGER,
  content_hash      TEXT UNIQUE,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Relations between concepts (semantic/graph edges)
CREATE TABLE IF NOT EXISTS gematria.concept_relations (
  relation_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  src_concept_id    UUID NOT NULL REFERENCES gematria.concepts(concept_id) ON DELETE CASCADE,
  dst_concept_id    UUID NOT NULL REFERENCES gematria.concepts(concept_id) ON DELETE CASCADE,
  relation_type     TEXT NOT NULL,
  weight            NUMERIC(6,5) NOT NULL DEFAULT 0.00000,
  evidence          JSONB DEFAULT '{}'::jsonb,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Centrality/metrics (latest snapshot per concept)
CREATE TABLE IF NOT EXISTS gematria.concept_centrality (
  concept_id        UUID PRIMARY KEY REFERENCES gematria.concepts(concept_id) ON DELETE CASCADE,
  degree            DOUBLE PRECISION,
  betweenness       DOUBLE PRECISION,
  closeness         DOUBLE PRECISION,
  eigenvector       DOUBLE PRECISION,
  metrics_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Concept network with embeddings (from migration 007)
CREATE TABLE IF NOT EXISTS gematria.concept_network (
  id                BIGSERIAL PRIMARY KEY,
  concept_id        UUID NOT NULL REFERENCES gematria.concepts(concept_id),
  embedding         VECTOR(1024),
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Concept clusters (for grouping similar concepts)
CREATE TABLE IF NOT EXISTS gematria.concept_clusters (
  concept_id        UUID PRIMARY KEY REFERENCES gematria.concepts(concept_id),
  cluster_id        INTEGER,
  cluster_center    BOOLEAN DEFAULT false,
  confidence        NUMERIC(4,3),
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
