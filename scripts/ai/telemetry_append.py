#!/usr/bin/env python3
# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
from __future__ import annotations

import datetime as dt
import json
import sys

from scripts.db.pool import get_pool


def log(run_id: str, node: str, event: str, payload: dict):
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO telemetry.metrics_log(ts, run_id, node, event, payload)
               VALUES (%(ts)s,%(run)s,%(node)s,%(evt)s,%(pay)s)""",
            {"ts": dt.datetime.utcnow(), "run": run_id, "node": node, "evt": event, "pay": json.dumps(payload)},
        )
        conn.commit()


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit("usage: telemetry_append.py RUN NODE EVENT [JSON_PAYLOAD]")
    run, node, event = sys.argv[1:4]
    payload = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
    log(run, node, event, payload)
    print("ok")
