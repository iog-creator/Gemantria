#!/usr/bin/env python3
"""
guard_mcp_db_ro.py — RFC-078

Strict-friendly DB probe for the MCP Knowledge schema.
- Default: SKIP (no network) unless STRICT_DB_PROBE=1
- DSN sources (first found): ATLAS_DSN, GEMATRIA_RO_DSN, GEMATRIA_DSN
- Uses `psql` if available to avoid new deps.

Outputs JSON to stdout; non-zero exit only if probe requested and fails.
"""

import json, os, shutil, subprocess, sys


def main():
    want = os.getenv("STRICT_DB_PROBE", "0") == "1"
    dsn = os.getenv("ATLAS_DSN") or os.getenv("GEMATRIA_RO_DSN") or os.getenv("GEMATRIA_DSN")
    have_psql = shutil.which("psql") is not None
    out = {
        "ok": True,
        "probe_requested": want,
        "used_psql": bool(have_psql),
        "dsn_present": bool(dsn),
        "notes": [],
    }

    if not want:
        out["notes"].append("probe skipped (STRICT_DB_PROBE=0)")
        print(json.dumps(out, indent=2))
        return 0

    if not dsn:
        out["ok"] = False
        out["notes"].append("no DSN in env (ATLAS_DSN|GEMATRIA_RO_DSN|GEMATRIA_DSN)")
        print(json.dumps(out, indent=2))
        return 1

    if not have_psql:
        out["ok"] = False
        out["notes"].append("psql not found on PATH")
        print(json.dumps(out, indent=2))
        return 1

    try:
        q = r"select count(*) from information_schema.views where table_schema='mcp' and table_name='v_catalog';"
        res = subprocess.run(["psql", dsn, "-At", "-c", q], check=True, capture_output=True, text=True)
        cnt = int(res.stdout.strip() or "0")
        out["view_count"] = cnt
        out["ok"] = cnt >= 1
        if not out["ok"]:
            out["notes"].append("mcp.v_catalog missing")
    except Exception as e:
        out["ok"] = False
        out["notes"].append(f"probe error: {e}")

    print(json.dumps(out, indent=2))
    return 0 if out["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
