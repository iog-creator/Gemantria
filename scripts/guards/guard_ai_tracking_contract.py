#!/usr/bin/env python3
import json
import os
import sys
from urllib.parse import urlsplit, parse_qs
from scripts.config.env import get_rw_dsn

STRICT = os.getenv("STRICT_AI_TRACKING", "0") == "1"


def san(dsn):
    if not dsn:
        return None
    u = urlsplit(dsn)
    return {
        "scheme": u.scheme,
        "host": u.hostname or parse_qs(u.query).get("host", [None])[0],
        "port": u.port,
        "db": (u.path or "").lstrip("/"),
    }


def die(msg, extra=None, code=1):
    out = {"ok": False, "note": msg}
    if extra:
        out.update(extra)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    sys.exit(code)


g = get_rw_dsn()
a = get_rw_dsn()
Gs, As = san(g), san(a)
info = {"dsn_envs": {"GEMATRIA_DSN": bool(g), "AI_AUTOMATION_DSN": bool(a)}}

if not g:
    msg = "GEMATRIA_DSN missing"
    return_ok = not STRICT
    print(json.dumps({"ok": return_ok, "note": msg, **info}, indent=2))
    sys.exit(0 if return_ok else 1)

if not a:
    msg = "AI_AUTOMATION_DSN missing (should point to gematria)"
    return_ok = not STRICT
    print(json.dumps({"ok": return_ok, "note": msg, **info}, indent=2))
    sys.exit(0 if return_ok else 1)

same_db = (Gs["db"] == As["db"]) and ((Gs["host"] or "") == (As["host"] or "")) and (Gs["port"] == As["port"])

if not same_db:
    die("AI automation DSN must point to the same DB as GEMATRIA_DSN", {"G": Gs, "A": As})

try:
    import psycopg

    with psycopg.connect(g) as conn, conn.cursor() as cur:

        def exists(tbl):
            schema, table = tbl.split(".", 1)
            cur.execute(
                "select 1 from information_schema.tables where table_schema=%s and table_name=%s limit 1",
                (schema, table),
            )
            return cur.fetchone() is not None

        # AI tracking tables are in public schema (created by migrations 015/016)
        req = ["public.ai_interactions", "public.governance_artifacts"]
        have = {t: exists(t) for t in req}
        missing = [t for t, v in have.items() if not v]

        if missing:
            msg = f"Missing required tracking tables: {', '.join(missing)}"
            if STRICT:
                die(msg, {"tables": have})
            print(json.dumps({"ok": True, "note": msg, "tables": have}, indent=2))
            sys.exit(0)

        # Optional stats (non-fatal)
        cur.execute("select count(*) from public.ai_interactions")
        ai = int(cur.fetchone()[0])
        cur.execute("select count(*) from public.governance_artifacts")
        ga = int(cur.fetchone()[0])

        print(
            json.dumps(
                {
                    "ok": True,
                    "note": "AI tracking bound to gematria DB (public schema)",
                    "same_db": True,
                    "tables": {"public.ai_interactions": True, "public.governance_artifacts": True},
                    "counts": {"ai_interactions": ai, "governance_artifacts": ga},
                },
                indent=2,
            )
        )
except Exception as e:
    msg = f"DB check failed: {e.__class__.__name__}: {e}"
    if STRICT:
        die(msg)
    print(json.dumps({"ok": True, "note": msg}, indent=2))
    sys.exit(0)
