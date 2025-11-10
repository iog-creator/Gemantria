# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

from __future__ import annotations

import contextlib
import os
import uuid
from typing import Any

import psycopg

from .structured_logger import get_logger, log_json
from scripts.config.env import get_rw_dsn

LOG = get_logger("gemantria.metrics")

METRICS_ENABLED = os.getenv("METRICS_ENABLED", "1") not in ("0", "false", "False")
WORKFLOW_ID = os.getenv("WORKFLOW_ID", "gemantria.v1")


class MetricsClient:
    def __init__(self, dsn: str | None):
        self._dsn = dsn
        self._enabled = bool(METRICS_ENABLED and dsn)
        self._pool = None

    def _conn(self):
        if not self._enabled:
            return None
        if self._pool is None:
            self._pool = psycopg.Connection.connect(self._dsn)  # simple conn; swap to pool later
        return self._pool

    def emit(self, row: dict[str, Any]) -> None:
        # Always emit to stdout JSON; db insert only if enabled
        with contextlib.suppress(Exception):
            log_json(LOG, 20, "metrics", **row)
        if not self._enabled:
            return
        conn = self._conn()
        if conn is None:
            return
        try:
            # Convert complex types for database insertion
            db_row = {}
            for k, v in row.items():
                if hasattr(v, "isoformat"):  # datetime objects
                    db_row[k] = v.isoformat()
                elif isinstance(v, dict):
                    # psycopg 3 requires explicit JSON serialization for dicts
                    import json

                    db_row[k] = json.dumps(v)
                else:
                    db_row[k] = v

            # Fill in missing required fields with defaults
            defaults = {
                "workflow": WORKFLOW_ID,
                "thread_id": "default",
                "status": "ok",
                "started_at": None,
                "finished_at": None,
                "duration_ms": None,
                "items_in": None,
                "items_out": None,
                "error_json": None,
                "meta": {},
            }
            for key, default_value in defaults.items():
                if key not in db_row:
                    db_row[key] = default_value

            # Use connection context manager properly - reuse same connection
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO metrics_log
                    (run_id, workflow, thread_id, node, event, status,
                     started_at, finished_at, duration_ms, items_in, items_out, error_json, meta)
                    VALUES (%(run_id)s, %(workflow)s, %(thread_id)s, %(node)s, %(event)s, %(status)s,
                            %(started_at)s, %(finished_at)s, %(duration_ms)s, %(items_in)s, %(items_out)s,
                            %(error_json)s, %(meta)s)
                    """,
                    db_row,
                )
            conn.commit()
        except Exception as e:
            # Fail-open for metrics; never break pipeline
            log_json(LOG, 30, "metrics_insert_failed", error=str(e))


def now():
    # psycopg can take python datetime; we'll pass None where not applicable
    import datetime as _dt  # noqa: E402

    return _dt.datetime.now(_dt.UTC)


class NodeTimer:
    def __init__(
        self,
        metrics: MetricsClient,
        run_id: uuid.UUID,
        thread_id: str,
        node: str,
        meta: dict | None = None,
    ):
        self.metrics, self.run_id, self.thread_id, self.node = (
            metrics,
            run_id,
            thread_id,
            node,
        )
        self.meta = meta or {}
        self.start_ts = now()

    def start(self, items_in: int | None = None):
        self.metrics.emit(
            {
                "run_id": self.run_id,
                "workflow": WORKFLOW_ID,
                "thread_id": self.thread_id,
                "node": self.node,
                "event": "node_start",
                "status": "ok",
                "started_at": self.start_ts,
                "finished_at": None,
                "duration_ms": None,
                "items_in": items_in,
                "items_out": None,
                "error_json": None,
                "meta": self.meta,
            }
        )

    def end(self, items_out: int | None = None, status: str = "ok"):
        end_ts = now()
        dur = (end_ts - self.start_ts).total_seconds() * 1000.0
        self.metrics.emit(
            {
                "run_id": self.run_id,
                "workflow": WORKFLOW_ID,
                "thread_id": self.thread_id,
                "node": self.node,
                "event": "node_end",
                "status": status,
                "started_at": self.start_ts,
                "finished_at": end_ts,
                "duration_ms": dur,
                "items_in": None,
                "items_out": items_out,
                "error_json": None,
                "meta": self.meta,
            }
        )

    def error(self, exc: Exception):
        end_ts = now()
        dur = (end_ts - self.start_ts).total_seconds() * 1000.0
        self.metrics.emit(
            {
                "run_id": self.run_id,
                "workflow": WORKFLOW_ID,
                "thread_id": self.thread_id,
                "node": self.node,
                "event": "node_error",
                "status": "error",
                "started_at": self.start_ts,
                "finished_at": end_ts,
                "duration_ms": dur,
                "items_in": None,
                "items_out": None,
                "error_json": {"type": type(exc).__name__, "msg": str(exc)},
                "meta": self.meta,
            }
        )


def get_metrics_client() -> MetricsClient:
    return MetricsClient(get_rw_dsn())
