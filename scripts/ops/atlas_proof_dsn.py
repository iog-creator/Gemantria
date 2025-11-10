#!/usr/bin/env python3
import json
import os
import sys
import subprocess
import datetime as dt
import pathlib as p
from urllib.parse import urlparse

try:
    from scripts.config.env import get_rw_dsn, get_bible_db_dsn
except Exception as e:
    print(json.dumps({"ok": False, "error": f"env loader import failed: {e}"}))
    sys.exit(1)


def mask(dsn: str | None) -> str | None:
    if not dsn:
        return None
    try:
        u = urlparse(dsn)
        host = u.hostname or ""
        if u.port:
            host += f":{u.port}"
        path = (u.path or "").lstrip("/")
        qs = f"?{u.query}" if u.query else ""
        return f"{u.scheme}://****@{host}/{path}{qs}"
    except Exception:
        return "masked"


def git_sha_short():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return None


def main():
    strict = os.environ.get("STRICT_ATLAS_DSN", "0") == "1"
    rw, ro = get_rw_dsn(), get_bible_db_dsn()
    ok = (rw is not None) if strict else True
    out = {
        "ok": ok,
        "mode": "STRICT" if strict else "HINT",
        "ts_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "git_sha": git_sha_short(),
        "dsns": {
            "rw": {"set": rw is not None, "masked": mask(rw)},
            "ro": {"set": ro is not None, "masked": mask(ro)},
        },
    }
    base = p.Path("docs/evidence")
    base.mkdir(parents=True, exist_ok=True)
    jpath = base / "atlas_proof_dsn.json"
    hpath = base / "atlas_proof_dsn.html"
    jpath.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    hpath.write_text(
        f"""<!doctype html>
<meta charset="utf-8">
<title>Atlas DSN Proof</title>
<style>body{{font-family:system-ui,Segoe UI,Roboto,Helvetica,Arial,sans-serif;max-width:820px;margin:2rem auto;padding:0 1rem}}pre{{background:#111;color:#eee;padding:1rem;overflow:auto;border-radius:12px}}a{{text-decoration:none}}</style>
<h1>Atlas DSN Proof</h1>
<p><strong>Mode:</strong> {"STRICT" if strict else "HINT"} · <strong>Git SHA:</strong> {out["git_sha"] or "unknown"} · <strong>UTC:</strong> {out["ts_utc"]}</p>
<p><a href="../atlas/index.html">← Back to Atlas</a> · <a href="./atlas_proof_dsn.json">View JSON</a></p>
<h2>Masked DSNs</h2>
<pre>{json.dumps(out["dsns"], indent=2)}</pre>
""",
        encoding="utf-8",
    )
    if strict and not rw:
        print(json.dumps(out))
        sys.exit(2)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
