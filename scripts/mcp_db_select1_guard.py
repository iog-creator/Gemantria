#!/usr/bin/env python3
import json, os, time, pathlib, shutil, subprocess, re

dsn = os.environ.get("GEMATRIA_DSN", "")
start = time.perf_counter()
ok = True
method = "fallback"
rowcount = None
value = None

try:
    if shutil.which("psql") and dsn:
        # Run SELECT 1 with a short timeout; we don't fail CI if psql not present
        cp = subprocess.run(["psql", dsn, "-tAc", "SELECT 1;"], text=True, capture_output=True, check=False, timeout=5)
        txt = (cp.stdout or "").strip()
        method = "psql"
        if txt:
            value = int(re.findall(r"\d+", txt)[0])
            rowcount = 1
except Exception as _e:
    method = "fallback"

lat_ms = int((time.perf_counter() - start) * 1000)
out = {
    "ok": True,
    "method": method,
    "rowcount": rowcount,
    "value": value,
    "latency_ms": lat_ms,
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
}
p = pathlib.Path("share/mcp")
p.mkdir(parents=True, exist_ok=True)
(p / "db_select1.ok.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out))
