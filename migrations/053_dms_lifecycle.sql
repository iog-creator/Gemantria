-- Migration 053: DMS Lifecycle and Authority
-- Phase 1 of DMS Enhancement Plan
-- Adds lifecycle management, authority hierarchy, and document relations

-- Add lifecycle management to kb_document
ALTER TABLE control.kb_document
ADD COLUMN lifecycle_stage TEXT DEFAULT 'active'
  CHECK (lifecycle_stage IN ('draft', 'active', 'deprecated', 'archived')),
ADD COLUMN phase_number INT, -- NULL = global, specific phase otherwise
ADD COLUMN deprecated_at TIMESTAMPTZ,
ADD COLUMN deprecated_reason TEXT;

-- Add authority designation
ALTER TABLE control.kb_document
ADD COLUMN is_canonical BOOLEAN DEFAULT false,
ADD COLUMN topic_key TEXT; -- e.g., 'pm_contract', 'phase_12_plan'

-- Create indexes for efficient queries
CREATE INDEX idx_kb_lifecycle ON control.kb_document(lifecycle_stage);
CREATE INDEX idx_kb_phase ON control.kb_document(phase_number);
CREATE INDEX idx_kb_canonical ON control.kb_document(is_canonical) WHERE is_canonical = true;
CREATE INDEX idx_kb_topic ON control.kb_document(topic_key) WHERE topic_key IS NOT NULL;

-- Create document relations table for complex relationships
CREATE TABLE control.kb_document_relations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_doc_id UUID NOT NULL REFERENCES control.kb_document(id) ON DELETE CASCADE,
  target_doc_id UUID NOT NULL REFERENCES control.kb_document(id) ON DELETE CASCADE,
  relation_type TEXT NOT NULL 
    CHECK (relation_type IN ('supersedes', 'relates_to', 'depends_on', 'contradicts')),
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now(),
  created_by TEXT,
  UNIQUE(source_doc_id, target_doc_id, relation_type)
);

CREATE INDEX idx_kb_relations_source ON control.kb_document_relations(source_doc_id);
CREATE INDEX idx_kb_relations_target ON control.kb_document_relations(target_doc_id);
CREATE INDEX idx_kb_relations_type ON control.kb_document_relations(relation_type);

-- Create view for active canonical documents
CREATE VIEW control.kb_canonical_docs AS
SELECT * FROM control.kb_document
WHERE is_canonical = true 
  AND lifecycle_stage = 'active';

-- Migration metadata
COMMENT ON COLUMN control.kb_document.lifecycle_stage IS 'Document lifecycle: draft, active, deprecated, archived';
COMMENT ON COLUMN control.kb_document.is_canonical IS 'True if this is the authoritative source for its topic';
COMMENT ON COLUMN control.kb_document.topic_key IS 'Semantic key for grouping related docs (e.g., pm_contract)';
COMMENT ON COLUMN control.kb_document.phase_number IS 'Project phase this doc is specific to, NULL for global docs';
COMMENT ON TABLE control.kb_document_relations IS 'Tracks semantic relationships between documents';
