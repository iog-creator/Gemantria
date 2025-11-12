#!/usr/bin/env python3
import json, os, time, pathlib

strict = os.environ.get("STRICT", "") in ("1", "true", "TRUE", "on", "ON")
cp_env = os.environ.get("CHECKPOINTER", "")
expected = "postgres" if strict else "memory"
mismatch = (cp_env != expected) and not (strict and cp_env == "postgres")
out = {
    "strict": strict,
    "checkpointer_env": cp_env,
    "expected_active": expected,
    "mismatch": bool(mismatch),
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
}
p = pathlib.Path("share/mcp")
p.mkdir(parents=True, exist_ok=True)
(p / "env_mismatch.warn.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out))
