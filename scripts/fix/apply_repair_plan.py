#!/usr/bin/env python3
import json
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXPORTS = ROOT / "exports"
LATEST = EXPORTS / "graph_latest.json"
import os
# Allow env overrides:
#   REPAIR_PLAN: path to repair_plan.json (default: share/eval/repair_plan.json)
#   REPAIRED_DIR: directory for outputs (default: exports/)
#   REPAIRED_BASENAME: base filename without timestamp (default: graph_repaired.json)
PLAN_J = ROOT / os.environ.get("REPAIR_PLAN", "share/eval/repair_plan.json")
REPAIRED_DIR = ROOT / os.environ.get("REPAIRED_DIR", "exports")
REPAIRED_BASENAME = os.environ.get("REPAIRED_BASENAME", "graph_repaired.json")


def main():
    print("[repair.apply] starting")

    # Load repair plan
    if not PLAN_J.exists():
        print(f"[repair.apply] FAIL no repair plan at {PLAN_J}")
        return 1

    try:
        plan = json.loads(PLAN_J.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[repair.apply] FAIL could not parse repair plan: {e}")
        return 1

    # Load latest graph
    if not LATEST.exists():
        print(f"[repair.apply] FAIL no latest graph at {LATEST}")
        return 1

    try:
        base = json.loads(LATEST.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[repair.apply] FAIL could not parse latest graph: {e}")
        return 1

    # Apply repairs
    nodes = base.get("nodes", [])
    repairs = plan.get("repairs", [])

    print(f"[repair.apply] applying {len(repairs)} repairs to {len(nodes)} nodes")

    # Simple repair logic - remove nodes marked for removal
    to_remove = set()
    for repair in repairs:
        if repair.get("action") == "remove_node":
            to_remove.add(repair.get("node_id"))

    nodes = [n for n in nodes if n.get("id") not in to_remove]

    # Update edges to remove references to removed nodes
    edges = base.get("edges", [])
    edges = [e for e in edges if e.get("source") not in to_remove and e.get("target") not in to_remove]

    print(f"[repair.apply] kept {len(nodes)} nodes and {len(edges)} edges")

    # Write repaired graph
    out = dict(base)
    out["nodes"] = nodes
    out["edges"] = edges
    ts = time.strftime("%Y%m%d%H%M%S")
    REPAIRED_DIR.mkdir(parents=True, exist_ok=True)
    out_latest = REPAIRED_DIR / REPAIRED_BASENAME
    out_ts = REPAIRED_DIR / f"{REPAIRED_BASENAME.rsplit('.',1)[0]}_{ts}.json"
    out_latest.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    out_ts.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")

    print(f"[repair.apply] wrote {out_ts.relative_to(ROOT)}")
    print(f"[repair.apply] wrote {out_latest.relative_to(ROOT)}")
    print("[repair.apply] done")


if __name__ == "__main__":
    exit(main() or 0)
