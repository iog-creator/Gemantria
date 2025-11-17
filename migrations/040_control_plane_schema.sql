-- Migration 040: Control Plane Schema
-- Purpose: Create control schema with tool catalog, capability rules, doc fragments,
--          capability sessions, agent runs, and compliance materialized views
-- Related: Phase-1 Plan (Guarded Tool Calls)
-- Note: UUIDs use gen_random_uuid() for now; future migration to UUIDv7 when available

CREATE SCHEMA IF NOT EXISTS control;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ===============================
-- TOOL CATALOG
-- ===============================

CREATE TABLE IF NOT EXISTS control.tool_catalog (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id bigint NOT NULL,
    name text NOT NULL,
    ring int NOT NULL,
    io_schema jsonb NOT NULL,
    enabled boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (project_id, name)
);

CREATE INDEX IF NOT EXISTS idx_tool_catalog_project ON control.tool_catalog (project_id);
CREATE INDEX IF NOT EXISTS idx_tool_catalog_ring ON control.tool_catalog (ring);
CREATE INDEX IF NOT EXISTS idx_tool_catalog_enabled ON control.tool_catalog (enabled) WHERE enabled = true;

-- ===============================
-- CAPABILITY RULES
-- ===============================

CREATE TABLE IF NOT EXISTS control.capability_rule (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id bigint NOT NULL,
    name text NOT NULL,
    ring int NOT NULL,
    allowlist text[],
    denylist text[],
    budgets jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (project_id, name)
);

CREATE INDEX IF NOT EXISTS idx_capability_rule_project ON control.capability_rule (project_id);
CREATE INDEX IF NOT EXISTS idx_capability_rule_ring ON control.capability_rule (ring);

-- ===============================
-- DOCUMENT FRAGMENTS (PoR)
-- ===============================

CREATE TABLE IF NOT EXISTS control.doc_fragment (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id bigint NOT NULL,
    src text NOT NULL,
    anchor text NOT NULL,
    sha256 text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (project_id, src, anchor)
);

CREATE INDEX IF NOT EXISTS idx_doc_fragment_project ON control.doc_fragment (project_id);
CREATE INDEX IF NOT EXISTS idx_doc_fragment_src ON control.doc_fragment (src);
CREATE INDEX IF NOT EXISTS idx_doc_fragment_sha256 ON control.doc_fragment (sha256);

-- ===============================
-- CAPABILITY SESSIONS
-- ===============================

CREATE TABLE IF NOT EXISTS control.capability_session (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id bigint NOT NULL,
    rule_id uuid NOT NULL REFERENCES control.capability_rule(id),
    por_json jsonb NOT NULL,
    tiny_menu text[] NOT NULL,
    ttl_s int NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_capability_session_project ON control.capability_session (project_id);
CREATE INDEX IF NOT EXISTS idx_capability_session_rule ON control.capability_session (rule_id);
CREATE INDEX IF NOT EXISTS idx_capability_session_created ON control.capability_session (created_at);

-- ===============================
-- AGENT RUNS (Audit Log)
-- ===============================

CREATE TABLE IF NOT EXISTS control.agent_run (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id bigint NOT NULL,
    session_id uuid REFERENCES control.capability_session(id),
    tool text NOT NULL,
    args_json jsonb NOT NULL,
    result_json jsonb NOT NULL,
    violations_json jsonb NOT NULL DEFAULT '[]'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_agent_run_project ON control.agent_run (project_id);
CREATE INDEX IF NOT EXISTS idx_agent_run_session ON control.agent_run (session_id);
CREATE INDEX IF NOT EXISTS idx_agent_run_created ON control.agent_run (created_at);
CREATE INDEX IF NOT EXISTS idx_agent_run_tool ON control.agent_run (tool);
CREATE INDEX IF NOT EXISTS idx_agent_run_violations ON control.agent_run USING GIN (violations_json);

-- ===============================
-- COMPLIANCE MATERIALIZED VIEWS
-- ===============================

CREATE MATERIALIZED VIEW IF NOT EXISTS control.mv_compliance_7d AS
SELECT
    '7d'::text AS window,
    COUNT(*)::int AS runs,
    ROUND(
        COUNT(*) FILTER (WHERE (result_json->>'por_ok')::boolean = true)::numeric /
        NULLIF(COUNT(*), 0),
        4
    )::numeric(5,4) AS por_ok_ratio,
    ROUND(
        COUNT(*) FILTER (WHERE (result_json->>'schema_ok')::boolean = true)::numeric /
        NULLIF(COUNT(*), 0),
        4
    )::numeric(5,4) AS schema_ok_ratio,
    ROUND(
        COUNT(*) FILTER (WHERE (result_json->>'provenance_ok')::boolean = true)::numeric /
        NULLIF(COUNT(*), 0),
        4
    )::numeric(5,4) AS provenance_ok_ratio,
    (
        SELECT jsonb_object_agg(code, cnt)
        FROM (
            SELECT
                violation->>'code' AS code,
                COUNT(*)::int AS cnt
            FROM control.agent_run,
                 jsonb_array_elements(violations_json) AS violation
            WHERE created_at >= now() - interval '7 days'
            GROUP BY violation->>'code'
            ORDER BY cnt DESC
            LIMIT 10
        ) top_violations
    ) AS violations_top,
    now() AS updated_at
FROM control.agent_run
WHERE created_at >= now() - interval '7 days';

CREATE MATERIALIZED VIEW IF NOT EXISTS control.mv_compliance_30d AS
SELECT
    '30d'::text AS window,
    COUNT(*)::int AS runs,
    ROUND(
        COUNT(*) FILTER (WHERE (result_json->>'por_ok')::boolean = true)::numeric /
        NULLIF(COUNT(*), 0),
        4
    )::numeric(5,4) AS por_ok_ratio,
    ROUND(
        COUNT(*) FILTER (WHERE (result_json->>'schema_ok')::boolean = true)::numeric /
        NULLIF(COUNT(*), 0),
        4
    )::numeric(5,4) AS schema_ok_ratio,
    ROUND(
        COUNT(*) FILTER (WHERE (result_json->>'provenance_ok')::boolean = true)::numeric /
        NULLIF(COUNT(*), 0),
        4
    )::numeric(5,4) AS provenance_ok_ratio,
    (
        SELECT jsonb_object_agg(code, cnt)
        FROM (
            SELECT
                violation->>'code' AS code,
                COUNT(*)::int AS cnt
            FROM control.agent_run,
                 jsonb_array_elements(violations_json) AS violation
            WHERE created_at >= now() - interval '30 days'
            GROUP BY violation->>'code'
            ORDER BY cnt DESC
            LIMIT 10
        ) top_violations
    ) AS violations_top,
    now() AS updated_at
FROM control.agent_run
WHERE created_at >= now() - interval '30 days';

-- ===============================
-- REFRESH FUNCTION
-- ===============================

CREATE OR REPLACE FUNCTION control.refresh_compliance("window" text)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    IF "window" = '7d' THEN
        REFRESH MATERIALIZED VIEW control.mv_compliance_7d;
    ELSIF "window" = '30d' THEN
        REFRESH MATERIALIZED VIEW control.mv_compliance_30d;
    ELSE
        RAISE EXCEPTION 'Invalid window: % (must be 7d or 30d)', "window";
    END IF;
END;
$$;

