-- Migration 048: Control KB Document Registry
-- Purpose: Create control.kb_document table for DM-001 document inventory and duplicate detection
-- Context: DM-001 - Document Management registry for repo-wide doc inventory
-- Notes:
--   - Control schema already exists from migration 040; CREATE SCHEMA here is idempotent.
--   - This table tracks all markdown-like files in the repo for inventory and duplicate detection.
--   - Separate from knowledge.kb_document (which stores knowledge base content) and
--     control.doc_registry (which tracks logical document names).

BEGIN;

CREATE SCHEMA IF NOT EXISTS control;

-- ===============================
-- KB DOCUMENT (DM-001 Inventory)
-- ===============================

CREATE TABLE IF NOT EXISTS control.kb_document (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    path            text NOT NULL UNIQUE,        -- repo-relative path (e.g., docs/SSOT/MASTER_PLAN.md)
    title           text,                        -- first heading or derived title
    doc_type        text,                        -- ssot | reference | runbook | legacy | unknown
    project         text NOT NULL DEFAULT 'Gemantria.v2',  -- project identifier
    content_hash    text NOT NULL,               -- sha256 of full content
    size_bytes      integer NOT NULL,            -- file size
    mtime           timestamptz NOT NULL,        -- file last-modified time from filesystem
    referenced_by   text[] DEFAULT '{}',         -- optional: paths that reference this doc (if available)
    is_canonical    boolean NOT NULL DEFAULT false,
    status          text NOT NULL DEFAULT 'unreviewed',  -- unreviewed | canonical | archive_candidate | legacy
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_kb_document_project_hash ON control.kb_document (project, content_hash);
CREATE INDEX IF NOT EXISTS idx_kb_document_path ON control.kb_document (path);
CREATE INDEX IF NOT EXISTS idx_kb_document_doc_type ON control.kb_document (doc_type);
CREATE INDEX IF NOT EXISTS idx_kb_document_status ON control.kb_document (status);
CREATE INDEX IF NOT EXISTS idx_kb_document_content_hash ON control.kb_document (content_hash);

COMMENT ON TABLE control.kb_document IS 'DM-001: Document inventory registry for repo-wide markdown-like files';
COMMENT ON COLUMN control.kb_document.path IS 'Repository-relative file path (unique identifier)';
COMMENT ON COLUMN control.kb_document.title IS 'Document title extracted from first heading or filename';
COMMENT ON COLUMN control.kb_document.doc_type IS 'Document type: ssot | reference | runbook | legacy | unknown';
COMMENT ON COLUMN control.kb_document.project IS 'Project identifier (default: Gemantria.v2)';
COMMENT ON COLUMN control.kb_document.content_hash IS 'SHA-256 hash of file content for duplicate detection';
COMMENT ON COLUMN control.kb_document.size_bytes IS 'File size in bytes';
COMMENT ON COLUMN control.kb_document.mtime IS 'File last-modified timestamp from filesystem';
COMMENT ON COLUMN control.kb_document.referenced_by IS 'Array of paths that reference this document';
COMMENT ON COLUMN control.kb_document.is_canonical IS 'Whether this is the canonical version (for duplicates)';
COMMENT ON COLUMN control.kb_document.status IS 'Review status: unreviewed | canonical | archive_candidate | legacy';

COMMIT;

