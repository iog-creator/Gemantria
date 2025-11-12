#!/usr/bin/env python3
import json, pathlib

trace = json.loads(pathlib.Path("share/mcp/session_trace.json").read_text()).get("trace_id", "")
emap = {}
edir = pathlib.Path("share/mcp/envelopes")
if edir.exists():
    for f in edir.iterdir():
        if f.is_file() and f.suffix in (".json", ".txt", ".ndjson"):
            emap[f.name] = trace
outp = pathlib.Path("share/mcp/envelope_trace.map.json")
outp.write_text(json.dumps(emap, indent=2))
print(json.dumps({"count": len(emap)}))
