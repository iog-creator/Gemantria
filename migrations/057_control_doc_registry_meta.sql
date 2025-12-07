-- 057_control_doc_registry_meta.sql
-- Phase 27.J: Add lifecycle metadata columns to control.doc_registry

BEGIN;

ALTER TABLE control.doc_registry
  ADD COLUMN importance text NOT NULL DEFAULT 'unknown';

ALTER TABLE control.doc_registry
  ADD CONSTRAINT doc_registry_importance_chk
  CHECK (importance IN ('critical', 'high', 'medium', 'low', 'unknown'));

ALTER TABLE control.doc_registry
  ADD COLUMN tags text[] NOT NULL DEFAULT '{}'::text[];

ALTER TABLE control.doc_registry
  ADD COLUMN owner_component text;

COMMIT;
