-- RFC-078: Postgres Knowledge MCP — initial schema (RO-friendly)
-- Idempotent guards ensure safe re-apply.

CREATE SCHEMA IF NOT EXISTS mcp;

-- Catalog of tools exposed to agents
CREATE TABLE IF NOT EXISTS mcp.tools (
  name        text PRIMARY KEY,
  "desc"      text NOT NULL,
  tags        text[] DEFAULT '{}',
  cost_est    real,
  visibility  text DEFAULT 'public' -- public|internal|experimental
);

-- HTTP/tool endpoints visible to agents
CREATE TABLE IF NOT EXISTS mcp.endpoints (
  name     text PRIMARY KEY,
  path     text NOT NULL,
  method   text NOT NULL DEFAULT 'GET',
  auth     text DEFAULT 'none',      -- none|bearer|basic|internal
  notes    text DEFAULT ''
);

-- Optional logs (RW in dev; OMIT in STRICT RO lanes)
CREATE TABLE IF NOT EXISTS mcp.logs (
  ts     timestamptz NOT NULL DEFAULT now(),
  agent  text NOT NULL,
  action text NOT NULL,
  target text NOT NULL,
  ok     boolean NOT NULL DEFAULT true
);

-- Read-only, tag-proof friendly view
CREATE OR REPLACE VIEW mcp.v_catalog AS
SELECT
  t.name,
  t."desc",
  t.tags,
  t.cost_est,
  t.visibility,
  e.path,
  e.method,
  e.auth
FROM mcp.tools t
LEFT JOIN mcp.endpoints e ON e.name = t.name;

-- Optional grants (no-op if role absent)
DO $$
BEGIN
  PERFORM 1 FROM pg_roles WHERE rolname='gematria_ro';
  IF FOUND THEN
    GRANT USAGE ON SCHEMA mcp TO gematria_ro;
    GRANT SELECT ON ALL TABLES IN SCHEMA mcp TO gematria_ro;
    GRANT SELECT ON ALL SEQUENCES IN SCHEMA mcp TO gematria_ro;
  END IF;
END$$;
