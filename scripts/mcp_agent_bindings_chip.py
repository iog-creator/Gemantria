#!/usr/bin/env python3
import json, os, time, pathlib

p = pathlib.Path
strict = os.environ.get("STRICT", "") in ("1", "true", "TRUE", "on", "ON")
# Load base bindings if present
base = {
    "strict": strict,
    "checkpointer": ("postgres" if strict else "memory"),
    "catalog": "mcp_catalog.v1",
}
base_path = p("share/mcp/agent_runtime.bindings.json")
if base_path.exists():
    try:
        base.update(json.loads(base_path.read_text()))
    except Exception:
        pass
# Add Atlas pointers
index = "share/atlas/index.html"
node0 = "share/atlas/nodes/0.html"
chip = {
    **base,
    "atlas": {"index": index, "nodes": [node0]},
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
}
outp = p("share/mcp/agent_runtime.bindings.chip.json")
outp.write_text(json.dumps(chip, indent=2))
print(json.dumps(chip))
