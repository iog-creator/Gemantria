#!/usr/bin/env python3
# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`

import os
import sys
import json
import uuid
import datetime as dt

import psycopg

run_id = f"telemetry-smoke-{uuid.uuid4()}"
dsn = os.environ.get("ATLAS_DSN_RW")
if not dsn:
    print("NO-GO: ATLAS_DSN_RW required for telemetry.smoke", file=sys.stderr)
    sys.exit(1)

conn = psycopg.connect(dsn)
cur = conn.cursor()
cur.execute(
    """INSERT INTO telemetry.metrics_log (ts, run_id, node, event, payload)
               VALUES (%s,%s,%s,%s,%s)""",
    (dt.datetime.utcnow(), run_id, "smoke", "start", json.dumps({"items_in": 0})),
)
cur.execute(
    """INSERT INTO telemetry.metrics_log (ts, run_id, node, event, payload)
               VALUES (%s,%s,%s,%s,%s)""",
    (dt.datetime.utcnow(), run_id, "smoke", "end", json.dumps({"items_out": 1})),
)
cur.execute(
    """INSERT INTO telemetry.ai_interactions (actor, req, res, meta)
               VALUES (%s,%s,%s,%s)""",
    (
        "lmstudio",
        json.dumps({"prompt": "ping"}),
        json.dumps({"text": "pong"}),
        json.dumps({"source": "telemetry.smoke"}),
    ),
)
conn.commit()
cur.close()
conn.close()

print(json.dumps({"ok": True, "run_id": run_id}))
