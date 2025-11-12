#!/usr/bin/env python3
import json
import os
import pathlib
import re
import subprocess
import time

out = {"ok": True, "errors": [], "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")}

env_dsn = os.environ.get("GEMATRIA_DSN", "")


def redact(d):
    return re.sub(r"//[^@]*@", "//<REDACTED>@", d) if d else d


try:
    make_dsn = subprocess.run(
        ["make", "-s", "echo.gematria_dsn"], check=False, text=True, capture_output=True
    ).stdout.strip()
except Exception as e:
    make_dsn, out["ok"] = "", False
    out["errors"].append(f"echo.gematria_dsn failed: {e}")

out["env_dsn"] = redact(env_dsn)
out["make_dsn"] = redact(make_dsn)
out["mismatch"] = bool(env_dsn) and bool(make_dsn) and (env_dsn != make_dsn)

p = pathlib.Path("share/mcp")
p.mkdir(parents=True, exist_ok=True)
(p / "dsn_mismatch.guard.json").write_text(json.dumps(out, indent=2))

print(json.dumps(out))
