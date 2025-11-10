#!/usr/bin/env python3
# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`

import datetime as dt
import json
import os
import sys

import psycopg2

DSN = os.environ.get("ATLAS_DSN_RW")
if not DSN:
    sys.exit("NO-GO: ATLAS_DSN_RW required")


def log(run_id: str, node: str, event: str, payload: dict):
    with psycopg2.connect(DSN) as c, c.cursor() as cur:
        cur.execute(
            """INSERT INTO telemetry.metrics_log(ts, run_id, node, event, payload)
                       VALUES (%s,%s,%s,%s,%s)""",
            (dt.datetime.utcnow(), run_id, node, event, json.dumps(payload)),
        )


if __name__ == "__main__":
    run, node, event = sys.argv[1:4]
    payload = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
    log(run, node, event, payload)
    print("ok")
