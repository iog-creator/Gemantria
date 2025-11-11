-- MCP PR-1 (stubs): read-only endpoint functions (returns small JSON)

-- NOTE: Real SQL will land in PR-2 (pgvector hybrid, real neighbors, scripture lookup).

CREATE SCHEMA IF NOT EXISTS mcp;

-- k bounded at 25 for safety; depth bounded at 3

CREATE OR REPLACE FUNCTION mcp.hybrid_search(q_text text, k int DEFAULT 10)
RETURNS jsonb
LANGUAGE sql
STABLE PARALLEL SAFE
AS $$
  SELECT jsonb_build_object(
    'endpoint','hybrid_search',
    'q', coalesce(q_text,''),
    'items', '[]'::jsonb,
    'k', LEAST(GREATEST(k,0),25)
  );
$$;

CREATE OR REPLACE FUNCTION mcp.graph_neighbors(node_id text, depth int DEFAULT 1, k int DEFAULT 10)
RETURNS jsonb
LANGUAGE sql
STABLE PARALLEL SAFE
AS $$
  SELECT jsonb_build_object(
    'endpoint','graph_neighbors',
    'node_id', coalesce(node_id,''),
    'depth', LEAST(GREATEST(depth,0),3),
    'items', '[]'::jsonb,
    'k', LEAST(GREATEST(k,0),25)
  );
$$;

CREATE OR REPLACE FUNCTION mcp.lookup_ref(book text, chapter int, verse int, k int DEFAULT 10)
RETURNS jsonb
LANGUAGE sql
STABLE PARALLEL SAFE
AS $$
  SELECT jsonb_build_object(
    'endpoint','lookup_ref',
    'ref', jsonb_build_object('book',coalesce(book,''),'chapter',chapter,'verse',verse),
    'items', '[]'::jsonb,
    'k', LEAST(GREATEST(k,0),25)
  );
$$;
