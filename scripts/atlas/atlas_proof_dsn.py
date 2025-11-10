#!/usr/bin/env python3
"""
Atlas DSN Proof - Generate evidence JSON for DSN connectivity and table counts.

Read-only operation; emits HINT if DB unreachable (hermetic CI).
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.parse
from pathlib import Path
from gemantria.dsn import dsn_rw

# Add scripts directory to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

EVIDENCE_DIR = REPO / "docs" / "evidence"
DSN = dsn_rw()
# STRICT_ATLAS_DSN is a flag, not a DSN, so we keep os.getenv for it
# TODO: Consider adding a helper to the shim for non-DSN env vars
STRICT = os.getenv("STRICT_ATLAS_DSN", "0") == "1"


def redact_dsn(dsn: str | None) -> dict:
    """Redact DSN for evidence output."""
    if not dsn:
        return {"present": False}
    try:
        u = urllib.parse.urlsplit(dsn)
        q = dict(urllib.parse.parse_qsl(u.query))
        return {
            "present": True,
            "scheme": u.scheme,
            "host": u.hostname,
            "port": u.port,
            "dbname": (u.path or "/").lstrip("/"),
            "sslmode": q.get("sslmode"),
            "redacted": True,
        }
    except Exception:
        return {"present": True, "redacted": True}


def query_table_counts(dsn: str) -> dict[str, int]:
    """Query table counts for telemetry tables."""
    try:
        import psycopg

        conn = psycopg.connect(dsn)
        cur = conn.cursor()
        tables = {}
        # Query common telemetry tables
        for table in [
            "ai_interactions",
            "governance_artifacts",
            "metrics_log",
            "checkpointer_state",
            "pipeline_runs",
        ]:
            try:
                cur.execute(f"SELECT COUNT(*) FROM public.{table}")
                tables[table] = cur.fetchone()[0]
            except Exception:
                tables[table] = 0
        cur.close()
        conn.close()
        return tables
    except Exception as e:
        return {"error": str(e)}


def main() -> int:
    """Generate Atlas DSN proof evidence."""
    out = {
        "clock": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "ok": False,
        "dsn": redact_dsn(DSN),
        "tables": {},
        "note": "",
    }
    if not DSN:
        out["note"] = "DSN missing; staying in grey mode"
        out["ok"] = not STRICT
    else:
        try:
            tables = query_table_counts(DSN)
            if "error" in tables:
                out["note"] = f"DB query error: {tables['error']}"
                out["ok"] = not STRICT
            else:
                out["tables"] = tables
                out["ok"] = True
        except Exception as e:
            out["note"] = f"DB connection error: {e}"
            out["ok"] = not STRICT
    # Write evidence
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    evidence_path = EVIDENCE_DIR / "atlas_proof_dsn.json"
    evidence_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    if not out["ok"] and STRICT:
        print(f"STRICT: Atlas DSN proof failed: {out['note']}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
