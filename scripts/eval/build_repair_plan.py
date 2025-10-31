#!/usr/bin/env python3
import json
import pathlib
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
LATEST = ROOT / "exports" / "graph_latest.json"
OUTJ = ROOT / "share" / "eval" / "repair_plan.json"
OUTM = ROOT / "share" / "eval" / "repair_plan.md"


def _load(p: pathlib.Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    print("[eval.repairplan] starting")
    if not LATEST.exists():
        print("[eval.repairplan] FAIL no exports/graph_latest.json")
        return 2
    doc = _load(LATEST)
    nodes = doc.get("nodes", []) or []
    edges = doc.get("edges", []) or []
    node_ids: set[Any] = {n.get("id") for n in nodes if isinstance(n, dict) and "id" in n}

    missing_ids: set[Any] = set()
    for e in edges:
        if not isinstance(e, dict):
            continue
        s, t = e.get("source"), e.get("target")
        if s not in node_ids:
            missing_ids.add(s)
        if t not in node_ids:
            missing_ids.add(t)
    if None in missing_ids:
        missing_ids.remove(None)

    # propose minimal stub nodes
    stubs: list[dict[str, Any]] = []
    for mid in sorted(missing_ids, key=lambda x: str(x)):
        stubs.append(
            {
                "id": mid,
                "label": f"[MISSING:{mid}] (stub)",
                "meta": {"proposed_stub": True},
            }
        )

    OUTJ.parent.mkdir(parents=True, exist_ok=True)
    OUTJ.write_text(
        json.dumps(
            {"missing_node_count": len(missing_ids), "proposed_stubs": stubs},
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    lines = []
    lines.append("# Gemantria Repair Plan")
    lines.append("")
    lines.append(f"*missing_node_count:* {len(missing_ids)}")
    lines.append("")
    lines.append("## Proposed stub nodes (first 25)")
    for s in stubs[:25]:
        lines.append(f"- id={s['id']} label={s['label']}")
    OUTM.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"[eval.repairplan] wrote {OUTJ.relative_to(ROOT)}")
    print(f"[eval.repairplan] wrote {OUTM.relative_to(ROOT)}")
    print("[eval.repairplan] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
