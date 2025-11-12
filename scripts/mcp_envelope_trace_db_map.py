#!/usr/bin/env python3
import json, os, pathlib, time

p = pathlib.Path
strict = os.environ.get("STRICT", "") in ("1", "true", "TRUE", "on", "ON")
source = "db" if strict and os.environ.get("CHECKPOINTER") == "postgres" else "file"
trace_id = None
st = p("share/mcp/session_trace.json")
if st.exists():
    try:
        trace_id = json.loads(st.read_text()).get("trace_id")
    except Exception:
        pass
emap = {}
edir = p("share/mcp/envelopes")
if edir.exists():
    for f in edir.iterdir():
        if f.is_file() and f.suffix in (".json", ".txt", ".ndjson"):
            emap[f.name] = trace_id
out = {"source": source, "map": emap, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
p("share/mcp/envelope_trace.dbmap.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out))
