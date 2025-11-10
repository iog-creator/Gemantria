#!/usr/bin/env python3
"""Export AI tracking data from gematria.ai_interactions and gematria.governance_artifacts"""

import os
import sys
import json
import datetime
from pathlib import Path

from scripts.config.env import get_rw_dsn, get_bible_db_dsn

# Load .env if present
env_file = Path(".env")
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            if key and value:
                os.environ.setdefault(key, value)

RFC3339 = "%Y-%m-%dT%H:%M:%S.%fZ"


def rfc3339_now() -> str:
    return datetime.datetime.now(datetime.UTC).strftime(RFC3339)


def _dsn() -> str | None:
    return os.getenv("AI_TRACKING_DSN") or get_rw_dsn()


def _try_import_psycopg():
    try:
        import psycopg

        return psycopg
    except Exception as e:
        print(f"[export_ai_tracking] psycopg not available: {e}", file=sys.stderr)
        return None


def export() -> int:
    dsn = _dsn()
    out_path = os.path.join("exports", "ai_tracking.json")
    os.makedirs("exports", exist_ok=True)

    if not dsn:
        # Fallback: leave a clear stub if no DSN configured
        stub = {
            "schema": "gemantria/ai-tracking.v1",
            "generated_at": rfc3339_now(),
            "note": "No AI_AUTOMATION_DSN configured; exporter produced stub only.",
            "totals": {"interactions": 0, "governance_artifacts": 0},
            "interactions": [],
            "governance_artifacts": [],
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(stub, f, ensure_ascii=False, indent=2)
        print("[export_ai_tracking] No DSN set; wrote stub exports/ai_tracking.json")
        return 0

    psycopg = _try_import_psycopg()
    if not psycopg:
        print("[export_ai_tracking] psycopg missing; cannot export from DB", file=sys.stderr)
        return 1

    # AI tracking tables are in the public schema in gematria DB (not in automation/ai/ops schemas)
    # Tables: ai_interactions, tool_usage_analytics, governance_artifacts, etc.
    # These were created by migrations/015 and 016
    schemas = ["public"]

    with psycopg.connect(dsn) as conn, conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
        # Find which schema has the tables
        schema = None
        for s in schemas:
            cur.execute(
                """
                select 1 from information_schema.tables 
                where table_schema=%s and table_name='ai_interactions'
            """,
                (s,),
            )
            if cur.fetchone():
                schema = s
                break

        if not schema:
            # Tables don't exist yet - write valid stub
            stub = {
                "schema": "gemantria/ai-tracking.v1",
                "generated_at": rfc3339_now(),
                "note": "AI tracking tables not yet created in database; exporter produced stub.",
                "totals": {"interactions": 0, "governance_artifacts": 0},
                "interactions": [],
                "governance_artifacts": [],
            }
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(stub, f, ensure_ascii=False, indent=2)
            print(f"[export_ai_tracking] No ai_interactions table in {schemas}; wrote stub {out_path}")
            return 0

        # Get interactions count
        cur.execute(f"select count(*) as cnt from {schema}.ai_interactions")
        interactions_count = cur.fetchone()["cnt"]

        # Get governance artifacts count
        cur.execute(f"select count(*) as cnt from {schema}.governance_artifacts")
        governance_count = cur.fetchone()["cnt"]

        # Get recent interactions (limit for export size)
        cur.execute(f"select * from {schema}.ai_interactions order by created_at desc limit 100")
        interactions = list(cur.fetchall())

        # Get recent governance artifacts (limit for export size)
        cur.execute(f"select * from {schema}.governance_artifacts order by last_updated desc limit 500")
        governance = list(cur.fetchall())

    doc = {
        "schema": "gemantria/ai-tracking.v1",
        "generated_at": rfc3339_now(),
        "totals": {
            "interactions": interactions_count,
            "governance_artifacts": governance_count,
        },
        "interactions": interactions,
        "governance_artifacts": governance,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2, default=str)
    print(
        f"[export_ai_tracking] Wrote {out_path} with {interactions_count} interactions / {governance_count} governance artifacts"
    )
    return 0


if __name__ == "__main__":
    sys.exit(export())
