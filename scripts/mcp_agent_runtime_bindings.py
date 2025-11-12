#!/usr/bin/env python3
import json, os, time, pathlib

strict = os.environ.get("STRICT", "") in ("1", "true", "TRUE", "on", "ON")
checkpointer = (
    "postgres"
    if (strict and os.environ.get("CHECKPOINTER", "") == "postgres")
    else ("memory" if not strict else os.environ.get("CHECKPOINTER", "memory"))
)

out = {
    "strict": strict,
    "checkpointer": checkpointer,
    "catalog": "mcp_catalog.v1",
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
}
p = pathlib.Path("share/mcp")
p.mkdir(parents=True, exist_ok=True)
(p / "agent_runtime.bindings.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out))
