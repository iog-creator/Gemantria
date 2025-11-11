#!/usr/bin/env python3
import json, os, subprocess, datetime, sys

def run_guard(args):
    try:
        p = subprocess.run(args, text=True, capture_output=True)
        out = p.stdout.strip() or '{}'
        try:
            data = json.loads(out)
        except Exception:
            data = {"raw": out}
        return {"rc": p.returncode, "out": data}
    except Exception as e:
        return {"rc": 99, "out": {"error": str(e)}}

strict = os.getenv("STRICT_GUARDS","0") in ("1","true","TRUE")
base = {
    "ts_utc": datetime.datetime.utcnow().isoformat() + "Z",
    "strict": strict,
}

imp = run_guard(["python3","scripts/ci/guard_jsonschema_import.py"])
ai  = run_guard([
    "python3","scripts/ci/guard_json_schema.py","--name","ai_nouns",
    "--schema-name","ai-nouns.schema.json",
    "--data-glob","share/**/*.json","--data-glob","evidence/**/*.json","--data-glob","ui/out/**/*.json",
    "--filename-contains","ai_nouns","--filename-contains","nouns"
])
gr  = run_guard([
    "python3","scripts/ci/guard_json_schema.py","--name","graph",
    "--schema-name","graph.schema.json",
    "--data-glob","share/**/*.json","--data-glob","evidence/**/*.json","--data-glob","ui/out/**/*.json",
    "--filename-contains","graph"
])

def summarize(x):
    out = x.get("out", {})
    exists = out.get("exists", {})
    stats = out.get("stats", {})
    return {
        "ok": out.get("ok"),
        "strict": out.get("strict"),
        "files_checked": stats.get("files_checked"),
        "data_files": len(exists.get("data_files", [])) if isinstance(exists.get("data_files"), list) else None,
        "errors": out.get("errors", [])[:3],
        "notes": out.get("notes", [])[:3],
        "rc": x.get("rc"),
    }

report = base | {
    "guards": {
        "jsonschema_import": summarize(imp),
        "ai_nouns": summarize(ai),
        "graph": summarize(gr),
    }
}
print(json.dumps(report, indent=2))
