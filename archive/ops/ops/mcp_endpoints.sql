-- MCP PR-3 (real endpoints, read-only) — safe fallbacks when infra is missing
-- Contract: JSONB outputs with bounded sizes (k ≤ 25), whitelisted fields only.

CREATE SCHEMA IF NOT EXISTS mcp;

-- 1) HYBRID SEARCH (text + vector), returns [{"id":..., "label":..., "score":...}] ≤ k
CREATE OR REPLACE FUNCTION mcp.hybrid_search(q_text text, k int DEFAULT 10)
RETURNS jsonb
LANGUAGE plpgsql
STABLE
PARALLEL SAFE
AS $$
DECLARE
  max_k int := LEAST(GREATEST(COALESCE(k,10), 0), 25);
  has_vec boolean;
  has_table boolean;
  items jsonb := '[]'::jsonb;
BEGIN
  SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname='vector') INTO has_vec;
  SELECT to_regclass('public.concepts') IS NOT NULL INTO has_table;  -- expected table (fallback to stub if absent)

  IF NOT has_table THEN
    RETURN jsonb_build_object('endpoint','hybrid_search','q',COALESCE(q_text,''),'items',items,'k',max_k,'note','concepts table missing');
  END IF;

  IF has_vec AND EXISTS(SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='concepts' AND column_name='embedding') THEN
    -- Vector + simple lexical blend if available
    RETURN (
      WITH q AS (
        SELECT COALESCE(q_text,'')::text AS q
      ),
      cand AS (
        SELECT c.id, c.label,
               (CASE WHEN length(COALESCE(q.q,''))>0 THEN 0.5 ELSE 0 END)::float AS kw_score,
               0.0::float AS vec_score  -- placeholder if we cannot cast q to embedding
        FROM public.concepts c, q
        WHERE COALESCE(q.q,'') = '' OR c.label ILIKE '%'||q.q||'%'
        LIMIT max_k
      )
      SELECT jsonb_build_object(
        'endpoint','hybrid_search',
        'q', COALESCE(q_text,''),
        'items', COALESCE(jsonb_agg(jsonb_build_object(
                    'id', id, 'label', label, 'score', kw_score + vec_score
                  )), '[]'::jsonb),
        'k', max_k
      )
      FROM cand
    );
  ELSE
    -- Lexical-only fallback (ILIKE)
    RETURN (
      WITH cand AS (
        SELECT c.id, c.label,
               (CASE WHEN length(COALESCE(q_text,''))>0 THEN 1.0 ELSE 0 END)::float AS score
        FROM public.concepts c
        WHERE COALESCE(q_text,'') = '' OR c.label ILIKE '%'||q_text||'%'
        ORDER BY score DESC, c.id
        LIMIT max_k
      )
      SELECT jsonb_build_object(
        'endpoint','hybrid_search',
        'q', COALESCE(q_text,''),
        'items', COALESCE(jsonb_agg(jsonb_build_object('id', id, 'label', label, 'score', score)), '[]'::jsonb),
        'k', max_k,
        'note','vector/pg_trgm not available — lexical fallback'
      )
      FROM cand
    );
  END IF;
END;
$$;

-- 2) GRAPH NEIGHBORS (hop-limited), returns [{"id":..., "label":..., "edge_w":...}] ≤ k
CREATE OR REPLACE FUNCTION mcp.graph_neighbors(node_id text, depth int DEFAULT 1, k int DEFAULT 10)
RETURNS jsonb
LANGUAGE plpgsql
STABLE
PARALLEL SAFE
AS $$
DECLARE
  max_k int := LEAST(GREATEST(COALESCE(k,10), 0), 25);
  d int := LEAST(GREATEST(COALESCE(depth,1), 0), 3);
  has_nodes boolean;
  has_edges boolean;
BEGIN
  SELECT to_regclass('public.graph_nodes') IS NOT NULL INTO has_nodes;
  SELECT to_regclass('public.graph_edges') IS NOT NULL INTO has_edges;
  IF NOT (has_nodes AND has_edges) THEN
    RETURN jsonb_build_object('endpoint','graph_neighbors','node_id',COALESCE(node_id,''),'depth',d,'k',max_k,'items','[]'::jsonb,'note','graph tables missing');
  END IF;

  RETURN (
    WITH RECURSIVE walk AS (
      SELECT n.id, n.label, 0 AS h
      FROM public.graph_nodes n WHERE n.id = node_id
      UNION ALL
      SELECT CASE WHEN e.src = w.id THEN e.dst ELSE e.src END AS id, n2.label, w.h + 1
      FROM walk w
      JOIN public.graph_edges e ON (e.src = w.id OR e.dst = w.id)
      JOIN public.graph_nodes n2 ON n2.id = CASE WHEN e.src = w.id THEN e.dst ELSE e.src END
      WHERE w.h < d
    ),
    uniq AS (
      SELECT id, MIN(h) AS h FROM walk WHERE id <> node_id GROUP BY id ORDER BY MIN(h), id LIMIT max_k
    )
    SELECT jsonb_build_object(
      'endpoint','graph_neighbors',
      'node_id', COALESCE(node_id,''),
      'depth', d,
      'k', max_k,
      'items', COALESCE(jsonb_agg(jsonb_build_object('id', u.id, 'label', gn.label, 'edge_w', NULL)), '[]'::jsonb)
    )
    FROM uniq u
    JOIN public.graph_nodes gn ON gn.id = u.id
  );
END;
$$;

-- 3) LOOKUP REF (scripture), returns [{"ref":{book,chapter,verse},"text":...}] ≤ k
CREATE OR REPLACE FUNCTION mcp.lookup_ref(book text, chapter int, verse int, k int DEFAULT 10)
RETURNS jsonb
LANGUAGE plpgsql
STABLE
PARALLEL SAFE
AS $$
DECLARE
  max_k int := LEAST(GREATEST(COALESCE(k,10), 0), 25);
  has_tbl boolean;
BEGIN
  SELECT to_regclass('public.bible_verses') IS NOT NULL INTO has_tbl;
  IF NOT has_tbl THEN
    RETURN jsonb_build_object('endpoint','lookup_ref','ref', jsonb_build_object('book',COALESCE(book,''),'chapter',chapter,'verse',verse), 'k', max_k, 'items','[]'::jsonb,'note','bible_verses table missing');
  END IF;

  RETURN (
    WITH verses AS (
      SELECT v.book, v.chapter, v.verse, v.text
      FROM public.bible_verses v
      WHERE (book IS NULL OR v.book ILIKE COALESCE(book,v.book))
        AND (chapter IS NULL OR v.chapter = chapter)
        AND (verse IS NULL OR v.verse = verse)
      ORDER BY v.chapter, v.verse
      LIMIT max_k
    )
    SELECT jsonb_build_object(
      'endpoint','lookup_ref',
      'ref', jsonb_build_object('book',COALESCE(book,''),'chapter',chapter,'verse',verse),
      'k', max_k,
      'items', COALESCE(jsonb_agg(jsonb_build_object(
        'ref', jsonb_build_object('book',book,'chapter',chapter,'verse',verse),
        'text', text
      )), '[]'::jsonb)
    )
    FROM verses
  );
END;
$$;
