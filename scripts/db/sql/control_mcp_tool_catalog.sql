-- Helper: ensure control.mcp_tool_catalog view exists for MCP exports
-- Phase-079 7B follow-up (used by scripts/db/mcp_catalog_stub.py)

CREATE SCHEMA IF NOT EXISTS control;

CREATE OR REPLACE VIEW control.mcp_tool_catalog AS
SELECT
    tc.name AS tool_name,
    COALESCE(tc.io_schema->>'input', '{}') AS input_schema_ref,
    COALESCE(tc.io_schema->>'output', '{}') AS output_schema_ref,
    tc.ring,
    (tc.ring = 0) AS read_only
FROM control.tool_catalog tc
WHERE tc.enabled = TRUE;

DO $$
BEGIN
    PERFORM 1 FROM pg_roles WHERE rolname = 'gematria_ro';
    IF FOUND THEN
        GRANT USAGE ON SCHEMA control TO gematria_ro;
        GRANT SELECT ON control.mcp_tool_catalog TO gematria_ro;
    END IF;
END$$;

