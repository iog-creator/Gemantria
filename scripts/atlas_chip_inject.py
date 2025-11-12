#!/usr/bin/env python3
import json
import os
import pathlib
import re
import time
import hashlib


def redact(d: str) -> str:
    return re.sub(r"//[^@]*@", "//<REDACTED>@", d) if d else d


def host_part(dsn: str) -> str:
    if not dsn:
        return ""
    # Try to extract host=... from query args; fall back to netloc path after '@'
    m = re.search(r"[?&]host=([^&]+)", dsn)
    if m:
        return m.group(1)
    m = re.search(r"//[^@]*@([^/]+)", dsn)
    return m.group(1) if m else ""


def hash_host(h: str) -> str:
    return hashlib.sha256(h.encode()).hexdigest()[:12] if h else ""


# Try to read last latency from SELECT1 receipt
lat_ms = None
try:
    sel = json.loads(pathlib.Path("share/mcp/db_select1.ok.json").read_text())
    lat_ms = sel.get("latency_ms")
except Exception:
    pass

dsn_env = os.environ.get("GEMATRIA_DSN", "")

# Write/refresh chip JSON
chip = {
    "strict": os.environ.get("STRICT", "") in ("1", "true", "TRUE", "on", "ON"),
    "checkpointer": os.environ.get("CHECKPOINTER", ""),
    "dsn": redact(dsn_env),
    "dsn_host_hash": hash_host(host_part(dsn_env)),
    "latency_ms": lat_ms,
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
}

adir = pathlib.Path("share/atlas")
adir.mkdir(parents=True, exist_ok=True)
(adir / "db_proof_chip.json").write_text(json.dumps(chip, indent=2))

# Ensure Atlas index has a marker attribute or comment
idx = adir / "index.html"
if idx.exists():
    text = idx.read_text(errors="ignore")
else:
    text = "<!doctype html><html><head><meta charset='utf-8'></head><body><div id='app'></div></body></html>"

if "data-db-strict=" not in text and "db-proof-chip" not in text:
    text = text.replace("<div id='app'", "<div id='app' data-db-strict=\"true\"><!-- db-proof-chip -->")

idx.write_text(text)

print(json.dumps({"index_html": str(idx), "marker": True, "latency_ms": lat_ms}))
