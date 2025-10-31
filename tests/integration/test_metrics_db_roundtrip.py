import datetime as dt
import os
import uuid

import psycopg

from src.infra.metrics_core import MetricsClient


def test_metrics_insert_roundtrip():
    dsn = os.getenv("GEMATRIA_DSN")
    if not dsn:
        import pytest

        pytest.skip("no DB configured")
    mc = MetricsClient(dsn)
    run_id = uuid.uuid4()
    row = {
        "run_id": run_id,
        "workflow": "gemantria.v1",
        "thread_id": "t1",
        "node": "extraction",
        "event": "node_start",
        "status": "ok",
        "started_at": dt.datetime.now(dt.UTC),
        "finished_at": None,
        "duration_ms": None,
        "items_in": 10,
        "items_out": None,
        "error_json": None,
        "meta": {"batch_size": 10},
    }
    mc.emit(row)
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM metrics_log WHERE run_id=%s AND node=%s",
            (run_id, "extraction"),
        )
        assert cur.fetchone()[0] == 1
