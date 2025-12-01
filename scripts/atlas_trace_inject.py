#!/usr/bin/env python3
import json, pathlib

adir = pathlib.Path("share/atlas")
adir.mkdir(parents=True, exist_ok=True)
idx = adir / "index.html"
trace = json.loads(pathlib.Path("share/mcp/session_trace.json").read_text()).get("trace_id", "")
if idx.exists():
    text = idx.read_text(errors="ignore")
else:
    text = "<!doctype html><html><head><meta charset=\"utf-8\"></head><body><div id='app'></div></body></html>"
if "data-trace-id=" not in text:
    # Try multiple injection points
    if "<div id='app'" in text:
        text = text.replace("<div id='app'", f'<div id=\'app\' data-trace-id="{trace}" trace-link="true"')
    elif "<html" in text and "data-trace-id=" not in text:
        text = text.replace("<html", f'<html data-trace-id="{trace}" trace-link="true"', 1)
    elif "<body" in text:
        text = text.replace("<body", f'<body data-trace-id="{trace}" trace-link="true"', 1)
    else:
        # Fallback: inject as comment at start
        text = f'<!-- trace-link data-trace-id="{trace}" -->\n' + text
idx.write_text(text)
print(json.dumps({"index_html": str(idx), "trace_id": trace, "marker": True}))
