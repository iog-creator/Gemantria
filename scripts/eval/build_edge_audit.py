#!/usr/bin/env python3
import csv, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
G = EVAL / "graph_latest.json"
CSV = EVAL / "edge_audit.csv"
JS  = EVAL / "edge_audit.json"

def main()->int:
    if not G.exists():
        print("[edge.audit] missing", G); return 2
    data = json.loads(G.read_text(encoding="utf-8"))
    edges = data.get("edges", [])
    # CSV
    with CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["src","dst","cosine","rerank","edge_strength","class"])
        for e in edges:
            w.writerow([e.get("src",""), e.get("dst",""),
                        e.get("cosine",""), e.get("rerank",""),
                        e.get("edge_strength",""), e.get("class","")])
    # JSON (verbatim minimal)
    JS.write_text(json.dumps(edges, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[edge.audit] wrote {CSV.relative_to(ROOT)}, {JS.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
