#!/usr/bin/env python3
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
import os
DEFAULT_OUTDIR = ROOT / "share" / "eval"
OUTDIR = ROOT / os.environ.get("EVAL_OUTDIR", str(DEFAULT_OUTDIR.relative_to(ROOT)))


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/eval/report_for_file.py <graph_file>")
        return 1

    graph_file = ROOT / sys.argv[1]
    if not graph_file.exists():
        print(f"[eval.report.repaired] FAIL no file at {graph_file}")
        return 1

    try:
        graph = json.loads(graph_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[eval.report.repaired] FAIL could not parse graph: {e}")
        return 1

    OUTDIR.mkdir(parents=True, exist_ok=True)

    # Generate simple report
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    report = {
        "file": str(graph_file.relative_to(ROOT)),
        "nodes": len(nodes),
        "edges": len(edges),
        "density": len(edges) / max(1, len(nodes)),
        "isolated_nodes": len([n for n in nodes if not any(e.get("source") == n.get("id") or e.get("target") == n.get("id") for e in edges)])
    }

    out_file = OUTDIR / f"report_{graph_file.stem}.json"
    out_file.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"[eval.report.repaired] wrote {out_file.relative_to(ROOT)}")
    print(f"[eval.report.repaired] analyzed {len(nodes)} nodes, {len(edges)} edges")

    return 0


if __name__ == "__main__":
    exit(main())
