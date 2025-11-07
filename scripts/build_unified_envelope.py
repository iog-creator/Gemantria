#!/usr/bin/env python3

import os, json, pathlib, datetime, sys
BASE = pathlib.Path(".")
EXPORTS = BASE / "exports"  # Source: pipeline artifacts
SHARE_EXPORTS = BASE / "share" / "exports"  # Destination: unified envelope
V = BASE / "share" / "eval" / "edges"

def load(p):
    with open(p, "r", encoding="utf-8") as f: return json.load(f)
def dump(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: json.dump(obj, f, ensure_ascii=False, indent=2)
def iso_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def main():
    book = os.getenv("BOOK", "Genesis")
    sources = {
        "ai_nouns": str(EXPORTS / "ai_nouns.json"),
        "graph_latest": str(EXPORTS / "graph_latest.json"),
        "graph_stats": str(EXPORTS / "graph_stats.json"),
        "temporal_patterns": str(EXPORTS / "temporal_patterns.json"),
        "pattern_forecast": str(EXPORTS / "pattern_forecast.json"),
        "edge_class_counts": str(EXPORTS / "edge_class_counts.json"),
        "blend_ssot_report": str(V / "blend_ssot_report.json")
    }
    # Load (tolerate empty but existing JSONs)
    ai_nouns = load(sources["ai_nouns"]) if pathlib.Path(sources["ai_nouns"]).exists() else {"nodes":[]}
    graph     = load(sources["graph_latest"]) if pathlib.Path(sources["graph_latest"]).exists() else {"nodes":[],"edges":[]}
    stats     = load(sources["graph_stats"]) if pathlib.Path(sources["graph_stats"]).exists() else {}
    tpat      = load(sources["temporal_patterns"]) if pathlib.Path(sources["temporal_patterns"]).exists() else {"patterns":[],"metadata":{}}
    fcast     = load(sources["pattern_forecast"]) if pathlib.Path(sources["pattern_forecast"]).exists() else {}
    counts    = load(sources["edge_class_counts"]) if pathlib.Path(sources["edge_class_counts"]).exists() else {"strong":0,"weak":0,"other":0}
    blend     = load(sources["blend_ssot_report"]) if pathlib.Path(sources["blend_ssot_report"]).exists() else {"pass": None}

    envelope = {
        "schema": "gematria/unified-envelope.v1",
        "book": book,
        "generated_at": iso_now(),
        "sources": sources,
        "ai_nouns": ai_nouns,
        "graph": graph,
        "stats": stats,
        "temporal": {"temporal_patterns": tpat, "forecast": fcast},
        "correlation": {"edge_class_counts": counts, "blend_ssot_report": blend},
        "meta": {"pipeline": "langgraph.unified", "run_id": os.getenv("WORKFLOW_ID","local")}
    }
    dump(SHARE_EXPORTS / "unified_envelope.json", envelope)

    print("[unified] wrote share/exports/unified_envelope.json")

if __name__ == "__main__":
    sys.exit(main())
