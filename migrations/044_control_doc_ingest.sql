-- Migration 044: Control Doc Ingestion Tables
-- Purpose: Create tables for ingesting SSOT documentation into control schema
-- Related: E2E Pipeline (Reality Check #1) - SSOT Docs → DB → LM Studio Q&A
-- Note: Minimal schema for doc ingestion; no search index yet

-- Ensure control schema exists
CREATE SCHEMA IF NOT EXISTS control;

-- ===============================
-- DOC SOURCES
-- ===============================

CREATE TABLE IF NOT EXISTS control.doc_sources (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    path text NOT NULL,
    title text NOT NULL,
    tags text[] NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (path)
);

CREATE INDEX IF NOT EXISTS idx_doc_sources_path ON control.doc_sources (path);
CREATE INDEX IF NOT EXISTS idx_doc_sources_tags ON control.doc_sources USING GIN (tags);

-- ===============================
-- DOC SECTIONS
-- ===============================

CREATE TABLE IF NOT EXISTS control.doc_sections (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id uuid NOT NULL REFERENCES control.doc_sources(id) ON DELETE CASCADE,
    section_title text,
    body text NOT NULL,
    order_index int NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_doc_sections_source_id ON control.doc_sections (source_id);
CREATE INDEX IF NOT EXISTS idx_doc_sections_order ON control.doc_sections (source_id, order_index);
CREATE INDEX IF NOT EXISTS idx_doc_sections_body_text ON control.doc_sections USING gin(to_tsvector('english', body));

