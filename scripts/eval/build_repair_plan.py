#!/usr/bin/env python3
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
import os
DEFAULT_OUTDIR = ROOT / "share" / "eval"
OUTDIR = ROOT / os.environ.get("EVAL_OUTDIR", str(DEFAULT_OUTDIR.relative_to(ROOT)))
OUT = OUTDIR / "repair_plan.json"


def main():
    print("[eval.repairplan] starting")

    OUTDIR.mkdir(parents=True, exist_ok=True)

    # Load latest graph to analyze for repairs
    latest = ROOT / "exports" / "graph_latest.json"
    if not latest.exists():
        print(f"[eval.repairplan] FAIL no latest graph at {latest}")
        return 1

    try:
        graph = json.loads(latest.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[eval.repairplan] FAIL could not parse graph: {e}")
        return 1

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    # Simple repair plan logic - identify orphaned nodes, etc.
    repairs = []

    # Find nodes with no edges
    node_ids = {n.get("id") for n in nodes if n.get("id") is not None}
    connected_nodes = set()
    for e in edges:
        connected_nodes.add(e.get("source"))
        connected_nodes.add(e.get("target"))

    orphaned = node_ids - connected_nodes
    for node_id in orphaned:
        repairs.append({
            "action": "remove_node",
            "node_id": node_id,
            "reason": "orphaned (no edges)"
        })

    # Create repair plan
    plan = {
        "version": "1.0",
        "generated_from": str(latest.relative_to(ROOT)),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "repairs": repairs,
        "summary": f"Found {len(repairs)} repairs needed"
    }

    OUT.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    print(f"[eval.repairplan] wrote {OUT.relative_to(ROOT)}")
    print(f"[eval.repairplan] identified {len(repairs)} repairs")
    print("[eval.repairplan] done")


if __name__ == "__main__":
    exit(main() or 0)
