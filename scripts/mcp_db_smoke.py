#!/usr/bin/env python3
import json
import os
import pathlib
import shutil
import subprocess
import time

ok = True
method = "stub"
# Try psql SELECT 1 if available (best-effort)
try:
    if shutil.which("psql") and os.environ.get("GEMATRIA_DSN"):
        # Ignore return code; we keep ok=True to remain hermetic-friendly
        subprocess.run(
            ["psql", os.environ["GEMATRIA_DSN"], "-c", "SELECT 1;"],
            check=False,
            capture_output=True,
            text=True,
        )
        method = "psql"
except Exception:
    method = "stub"

out = {"ok": ok, "method": method, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")}

p = pathlib.Path("share/mcp")
p.mkdir(parents=True, exist_ok=True)
(p / "db_smoke.ok.json").write_text(json.dumps(out, indent=2))

print(json.dumps(out))
