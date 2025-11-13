-- Migration 041: Control-plane MCP catalog view
-- Purpose: Create read-only view control.mcp_tool_catalog for Knowledge-MCP integration
-- Related: PLAN-075 E75, RFC-078 (Postgres Knowledge MCP)

-- Create read-only view projecting from control.tool_catalog
CREATE OR REPLACE VIEW control.mcp_tool_catalog AS
SELECT
    name AS tool_name,
    COALESCE(io_schema->>'input', '{}') AS input_schema_ref,
    COALESCE(io_schema->>'output', '{}') AS output_schema_ref,
    ring,
    (ring = 0) AS read_only
FROM control.tool_catalog
WHERE enabled = true;

-- Grant read access to RO role if it exists
DO $$
BEGIN
    PERFORM 1 FROM pg_roles WHERE rolname='gematria_ro';
    IF FOUND THEN
        GRANT USAGE ON SCHEMA control TO gematria_ro;
        GRANT SELECT ON control.mcp_tool_catalog TO gematria_ro;
    END IF;
END$$;

