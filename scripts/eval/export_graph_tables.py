#!/usr/bin/env python3
import csv
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
G = EVAL / "graph_latest.json"
NCSV = EVAL / "nodes.csv"
ECSV = EVAL / "edges.csv"


def main() -> int:
    if not G.exists():
        print("[tables] missing", G)
        return 2
    data = json.loads(G.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    # nodes.csv
    with NCSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "label"])
        for n in nodes:
            w.writerow([n.get("id", ""), n.get("label", "")])
    # edges.csv
    with ECSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["src", "dst", "cosine", "rerank", "edge_strength", "class"])
        for e in edges:
            w.writerow(
                [
                    e.get("src", ""),
                    e.get("dst", ""),
                    e.get("cosine", ""),
                    e.get("rerank", ""),
                    e.get("edge_strength", ""),
                    e.get("class", ""),
                ]
            )
    print(f"[tables] wrote {NCSV.relative_to(ROOT)}, {ECSV.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
