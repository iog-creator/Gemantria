\timing on
-- HYBRID (k=5)
EXPLAIN (ANALYZE, VERBOSE, COSTS, SUMMARY, BUFFERS)
SELECT mcp.hybrid_search('light', 5);

-- NEIGHBORS (depth=1, k=5)
EXPLAIN (ANALYZE, VERBOSE, COSTS, SUMMARY, BUFFERS)
SELECT mcp.graph_neighbors('node_1', 1, 5);

-- LOOKUP REF (k=5)
EXPLAIN (ANALYZE, VERBOSE, COSTS, SUMMARY, BUFFERS)
SELECT mcp.lookup_ref('Genesis', 1, 1, 5);

