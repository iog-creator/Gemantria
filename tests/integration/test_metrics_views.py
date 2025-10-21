import os, psycopg, pytest

dsn = os.getenv("GEMATRIA_DSN")

@pytest.mark.skipif(not dsn, reason="no DB configured")
def test_views_exist():
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_views WHERE viewname='v_metrics_flat'")
        assert cur.fetchone() is not None
        cur.execute("SELECT 1 FROM pg_views WHERE viewname='v_node_latency_7d'")
        assert cur.fetchone() is not None
        cur.execute("SELECT 1 FROM pg_views WHERE viewname='v_node_throughput_24h'")
        assert cur.fetchone() is not None
        cur.execute("SELECT 1 FROM pg_views WHERE viewname='v_recent_errors_7d'")
        assert cur.fetchone() is not None
        cur.execute("SELECT 1 FROM pg_views WHERE viewname='v_pipeline_runs'")
        assert cur.fetchone() is not None

@pytest.mark.skipif(not dsn, reason="no DB configured")
def test_latency_view_shape():
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute("SELECT node, calls, avg_ms, p50_ms, p95_ms FROM v_node_latency_7d LIMIT 1")
        _ = cur.fetchone()  # shape validated if no error is raised
