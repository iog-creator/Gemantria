-- 070_rls.sql
-- Row-Level Security policies for multi-tenant isolation
-- Idempotent: safe to run multiple times
-- Note: RLS is P6 (later phase); this is a skeleton

BEGIN;

-- ===============================
-- ROW-LEVEL SECURITY: Multi-Tenant Isolation
-- ===============================

-- Strategy: Use tenant_id column + RLS policies
-- Note: This requires adding tenant_id to tables and enabling RLS
-- This is a template for future implementation

-- Example structure (commented - requires schema changes):
/*
-- Enable RLS on tables
ALTER TABLE gematria.nodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE gematria.edges ENABLE ROW LEVEL SECURITY;
ALTER TABLE telemetry.metrics_log ENABLE ROW LEVEL SECURITY;

-- Add tenant_id column (if not exists)
-- ALTER TABLE gematria.nodes ADD COLUMN IF NOT EXISTS tenant_id UUID;
-- ALTER TABLE gematria.edges ADD COLUMN IF NOT EXISTS tenant_id UUID;
-- ALTER TABLE telemetry.metrics_log ADD COLUMN IF NOT EXISTS tenant_id UUID;

-- Policy: Users can only see their own tenant's data
CREATE POLICY tenant_isolation_nodes ON gematria.nodes
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id', true)::UUID);

CREATE POLICY tenant_isolation_edges ON gematria.edges
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id', true)::UUID);

CREATE POLICY tenant_isolation_metrics ON telemetry.metrics_log
    FOR SELECT
    USING (tenant_id = current_setting('app.tenant_id', true)::UUID);

-- Function to set tenant context (call before queries)
CREATE OR REPLACE FUNCTION ops.set_tenant_context(p_tenant_id UUID) RETURNS void AS $$
BEGIN
    PERFORM set_config('app.tenant_id', p_tenant_id::text, false);
END;
$$ LANGUAGE plpgsql;
*/

-- For now, RLS is disabled (single-tenant mode)
-- RLS will be implemented in P6 when multi-tenant support is required

COMMIT;

