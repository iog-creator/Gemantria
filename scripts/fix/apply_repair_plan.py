#!/usr/bin/env python3
import json
import pathlib
import sys
import time
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXPORTS = ROOT / "exports"
LATEST = EXPORTS / "graph_latest.json"
PLAN_J = ROOT / "share" / "eval" / "repair_plan.json"


def _load_json(p: pathlib.Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def _node_ids(nodes: list[dict[str, Any]]) -> set[Any]:
    out = set()
    for n in nodes:
        if isinstance(n, dict) and "id" in n:
            out.add(n["id"])
    return out


def main() -> int:
    print("[repair.apply] starting")
    if not LATEST.exists():
        print("[repair.apply] FAIL no exports/graph_latest.json")
        return 2
    if not PLAN_J.exists():
        print(
            "[repair.apply] FAIL no share/eval/repair_plan.json (run make eval.repairplan)"
        )
        return 2

    base = _load_json(LATEST)
    plan = _load_json(PLAN_J)
    nodes = list(base.get("nodes", []) or [])

    have = _node_ids(nodes)
    stubs = plan.get("proposed_stubs", []) or []
    added = []
    for s in stubs:
        sid = s.get("id")
        if sid not in have:
            nodes.append(s)
            added.append(sid)

    out = dict(base)
    out["nodes"] = nodes
    ts = time.strftime("%Y%m%d%H%M%S")
    out_path = EXPORTS / f"graph_repaired_{ts}.json"
    (EXPORTS / "graph_repaired.json").write_text(
        json.dumps(out, indent=2, sort_keys=True), encoding="utf-8"
    )
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")

    print(f"[repair.apply] added_stub_nodes={len(added)}")
    print(f"[repair.apply] wrote {out_path.relative_to(ROOT)}")
    print(f"[repair.apply] wrote {(EXPORTS / 'graph_repaired.json').relative_to(ROOT)}")
    print("[repair.apply] OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
