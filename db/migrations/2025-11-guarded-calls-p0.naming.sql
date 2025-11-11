-- Idempotent normalization for Guarded Tool Calls P0
-- Safe to re-run: conditional renames & additive columns only.

DO $$
BEGIN
  IF to_regclass('public.tool_catalog') IS NOT NULL
     AND to_regclass('public.mcp_tool_catalog') IS NULL THEN
    EXECUTE 'ALTER TABLE tool_catalog RENAME TO mcp_tool_catalog';
  END IF;

  IF to_regclass('public.capability_rule') IS NOT NULL
     AND to_regclass('public.mcp_capability_rule') IS NULL THEN
    EXECUTE 'ALTER TABLE capability_rule RENAME TO mcp_capability_rule';
  END IF;

  IF to_regclass('public.doc_fragment') IS NOT NULL
     AND to_regclass('public.mcp_doc_fragment') IS NULL THEN
    EXECUTE 'ALTER TABLE doc_fragment RENAME TO mcp_doc_fragment';
  END IF;

  IF to_regclass('public.capability_session') IS NOT NULL
     AND to_regclass('public.mcp_capability_session') IS NULL THEN
    EXECUTE 'ALTER TABLE capability_session RENAME TO mcp_capability_session';
  END IF;

  IF to_regclass('public.agent_run') IS NOT NULL
     AND to_regclass('public.mcp_agent_run') IS NULL THEN
    EXECUTE 'ALTER TABLE agent_run RENAME TO mcp_agent_run';
  END IF;

  IF to_regclass('public.agent_queue') IS NOT NULL
     AND to_regclass('public.mcp_agent_queue') IS NULL THEN
    EXECUTE 'ALTER TABLE agent_queue RENAME TO mcp_agent_queue';
  END IF;
END$$;

-- Add common columns if missing
ALTER TABLE IF EXISTS mcp_tool_catalog         ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();
ALTER TABLE IF EXISTS mcp_tool_catalog         ADD COLUMN IF NOT EXISTS updated_at timestamptz;
ALTER TABLE IF EXISTS mcp_capability_rule      ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();
ALTER TABLE IF EXISTS mcp_capability_rule      ADD COLUMN IF NOT EXISTS updated_at timestamptz;
ALTER TABLE IF EXISTS mcp_doc_fragment         ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();
ALTER TABLE IF EXISTS mcp_doc_fragment         ADD COLUMN IF NOT EXISTS updated_at timestamptz;
ALTER TABLE IF EXISTS mcp_capability_session   ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();
ALTER TABLE IF EXISTS mcp_capability_session   ADD COLUMN IF NOT EXISTS updated_at timestamptz;
ALTER TABLE IF EXISTS mcp_agent_run            ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();
ALTER TABLE IF EXISTS mcp_agent_run            ADD COLUMN IF NOT EXISTS updated_at timestamptz;
ALTER TABLE IF EXISTS mcp_agent_queue          ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();
ALTER TABLE IF EXISTS mcp_agent_queue          ADD COLUMN IF NOT EXISTS updated_at timestamptz;

-- MV normalization (rename if legacy exists)
DO $$
BEGIN
  IF to_regclass('public.mv_compliance_7d') IS NOT NULL
     AND to_regclass('public.mv_mcp_compliance_7d') IS NULL THEN
    EXECUTE 'ALTER MATERIALIZED VIEW mv_compliance_7d RENAME TO mv_mcp_compliance_7d';
  END IF;
  IF to_regclass('public.mv_compliance_30d') IS NOT NULL
     AND to_regclass('public.mv_mcp_compliance_30d') IS NULL THEN
    EXECUTE 'ALTER MATERIALIZED VIEW mv_compliance_30d RENAME TO mv_mcp_compliance_30d';
  END IF;
END$$;
