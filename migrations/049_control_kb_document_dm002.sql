-- 049_control_kb_document_dm002.sql
-- DM-002: add canonical/status classification fields to control.kb_document

BEGIN;

CREATE SCHEMA IF NOT EXISTS control;

ALTER TABLE control.kb_document
  ADD COLUMN IF NOT EXISTS is_canonical boolean,
  ADD COLUMN IF NOT EXISTS status text;

COMMIT;

