-- RFC-078: Postgres Knowledge MCP — optional seed data (PLAN-073 M1 E01)
-- Idempotent seed with example tools and endpoints for documentation/testing.
-- Safe to re-run: uses INSERT ... ON CONFLICT DO NOTHING.

-- Example tools
INSERT INTO mcp.tools (name, "desc", tags, cost_est, visibility)
VALUES
  (
    'bible_search',
    'Search Bible passages by reference, keyword, or gematria value',
    ARRAY['bible', 'search', 'gematria'],
    0.1,
    'public'
  )
ON CONFLICT (name) DO NOTHING;

INSERT INTO mcp.tools (name, "desc", tags, cost_est, visibility)
VALUES
  (
    'gematria_calculate',
    'Calculate gematria value for Hebrew text using Mispar Hechrachi',
    ARRAY['gematria', 'hebrew', 'calculation'],
    0.05,
    'public'
  )
ON CONFLICT (name) DO NOTHING;

INSERT INTO mcp.tools (name, "desc", tags, cost_est, visibility)
VALUES
  (
    'graph_query',
    'Query the gematria knowledge graph for nodes, edges, and patterns',
    ARRAY['graph', 'query', 'gematria'],
    0.2,
    'public'
  )
ON CONFLICT (name) DO NOTHING;

-- Example endpoints
INSERT INTO mcp.endpoints (name, path, method, auth, notes)
VALUES
  (
    'bible_search',
    '/api/bible/search',
    'GET',
    'none',
    'Search Bible passages. Query params: q (keyword), ref (reference), gematria (value)'
  )
ON CONFLICT (name) DO NOTHING;

INSERT INTO mcp.endpoints (name, path, method, auth, notes)
VALUES
  (
    'gematria_calculate',
    '/api/gematria/calculate',
    'POST',
    'none',
    'Calculate gematria. Body: {text: "Hebrew text"}'
  )
ON CONFLICT (name) DO NOTHING;

INSERT INTO mcp.endpoints (name, path, method, auth, notes)
VALUES
  (
    'graph_query',
    '/api/graph/query',
    'POST',
    'bearer',
    'Query knowledge graph. Body: {query: "Cypher-like query", limit: 100}'
  )
ON CONFLICT (name) DO NOTHING;

