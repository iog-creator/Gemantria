-- MCP Catalog (DRAFT, PR-2) — read-only contracts for AI-safe endpoints

CREATE SCHEMA IF NOT EXISTS mcp;

-- A simple catalog view describing allowed endpoints, inputs, and bounds.

CREATE OR REPLACE VIEW mcp.catalog AS

SELECT * FROM (

  VALUES

    ('hybrid_search',  jsonb_build_object('inputs', jsonb_build_array('q_text','k'), 'max_k', 25, 'version', 1)),

    ('graph_neighbors',jsonb_build_object('inputs', jsonb_build_array('node_id','depth','k'), 'max_k', 25, 'version', 1)),

    ('lookup_ref',     jsonb_build_object('inputs', jsonb_build_array('book','chapter','verse','k'), 'max_k', 25, 'version', 1))

) AS t(name, spec);

-- All endpoints must be STABLE, PARALLEL SAFE, return jsonb with ≤k items, and never write.

-- Actual function bodies land in PR-1 (stubs) and PR-3 (real SQL); this catalog wires them for guards/UI.
