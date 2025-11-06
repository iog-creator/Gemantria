-- Postgres persistence for LangGraph saver + relations + centrality (idempotent)

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE SCHEMA IF NOT EXISTS gematria;

CREATE TABLE IF NOT EXISTS gematria.checkpoints(

  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),

  run_id uuid, node text, payload jsonb, created_at timestamptz default now()

);

CREATE TABLE IF NOT EXISTS gematria.concept_relations(

  src bigint, dst bigint, type text,

  cosine real, rerank_score real, edge_strength real CHECK (edge_strength >= 0 AND edge_strength <= 1),

  class text, created_at timestamptz default now()

);

CREATE TABLE IF NOT EXISTS gematria.concept_centrality(

  concept_id bigint, degree real, betweenness real, eigenvector real, run_id uuid

);

-- embeddings table created later when vector is enabled
