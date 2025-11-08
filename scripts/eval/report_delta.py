# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import glob
import json
import pathlib
import re
import sys
import time
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUTDIR = ROOT / "share" / "eval"
JSON_OUT = OUTDIR / "delta.json"
MD_OUT = OUTDIR / "delta.md"

EXPORT_DIR = ROOT / "exports"
LATEST = EXPORT_DIR / "graph_latest.json"


def _load_json(p: pathlib.Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def _parse_ts(name: str) -> int:
    base = pathlib.Path(name).name
    m = re.search(r"graph_(\d{8})(\d{6})?", base)
    if m:
        d = m.group(1)
        t = m.group(2) or "000000"
        return int(d + t)
    m2 = re.search(r"graph_(\d{4}-\d{2}-\d{2})[T_]?(\d{2}-\d{2}-\d{2})?", base)
    if m2:
        d = m2.group(1).replace("-", "")
        t = (m2.group(2) or "00-00-00").replace("-", "")
        return int(d + t)
    return 0


def _edge_key(e: dict[str, Any]) -> tuple[Any, Any]:
    return (e.get("source"), e.get("target"))


def _node_ids(doc: dict[str, Any]) -> set[Any]:
    nodes = doc.get("nodes", [])
    if isinstance(nodes, list):
        return {n.get("id") for n in nodes if isinstance(n, dict) and "id" in n}
    return set()


def _edge_pairs(doc: dict[str, Any]) -> set[tuple[Any, Any]]:
    edges = doc.get("edges", [])
    if isinstance(edges, list):
        return {_edge_key(e) for e in edges if isinstance(e, dict)}
    return set()


def _strengths(doc: dict[str, Any]) -> list[float]:
    edges = doc.get("edges", [])
    vals: list[float] = []
    if isinstance(edges, list):
        for e in edges:
            v = e.get("strength")
            if isinstance(v, int | float):
                vals.append(float(v))
    return vals


def main() -> int:
    print("[eval.delta] starting")
    OUTDIR.mkdir(parents=True, exist_ok=True)

    if not LATEST.exists():
        print("[eval.delta] FAIL no exports/graph_latest.json")
        return 2

    # pick most recent prior export (graph_*.json excluding latest path)
    candidates = [p for p in glob.glob(str(EXPORT_DIR / "graph_*.json"))]
    # exclude graph_latest.json if it matches pattern on some setups
    candidates = [c for c in candidates if pathlib.Path(c).name != "graph_latest.json"]
    if not candidates:
        # Write empty delta artifacts but succeed deterministically
        report = {"summary": {"has_previous": False}}
        JSON_OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
        MD_OUT.write_text(
            "# Gemantria Export Delta\n\n_No previous export found._\n",
            encoding="utf-8",
        )
        print(f"[eval.delta] wrote {JSON_OUT.relative_to(ROOT)}")
        print(f"[eval.delta] wrote {MD_OUT.relative_to(ROOT)}")
        print("[eval.delta] OK")
        return 0

    prev_fp = sorted(candidates, key=_parse_ts)[-1]
    prev_path = pathlib.Path(prev_fp)

    cur = _load_json(LATEST)
    prev = _load_json(prev_path)

    cur_nodes = _node_ids(cur)
    prev_nodes = _node_ids(prev)
    cur_edges = _edge_pairs(cur)
    prev_edges = _edge_pairs(prev)

    added_nodes = sorted(list(cur_nodes - prev_nodes))
    removed_nodes = sorted(list(prev_nodes - cur_nodes))
    added_edges = sorted(list(cur_edges - prev_edges))
    removed_edges = sorted(list(prev_edges - cur_edges))

    cur_strengths = _strengths(cur)
    prev_strengths = _strengths(prev)

    def _stats(arr: list[float]) -> dict[str, Any]:
        if not arr:
            return {"count": 0}
        return {
            "count": len(arr),
            "min": min(arr),
            "max": max(arr),
            "mean": sum(arr) / len(arr),
        }

    cur_stats = _stats(cur_strengths)
    prev_stats = _stats(prev_strengths)

    # Simple policy: no removals allowed by default; can be relaxed later.
    ok = (len(removed_nodes) == 0) and (len(removed_edges) == 0)

    report = {
        "ts_unix": int(time.time()),
        "summary": {
            "has_previous": True,
            "ok": ok,
            "removed_nodes": len(removed_nodes),
            "removed_edges": len(removed_edges),
        },
        "previous_file": str(prev_path.relative_to(ROOT)),
        "current_file": str(LATEST.relative_to(ROOT)),
        "nodes": {"added": added_nodes, "removed": removed_nodes},
        "edges": {"added": added_edges, "removed": removed_edges},
        "strength_stats": {"current": cur_stats, "previous": prev_stats},
    }
    JSON_OUT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    lines = []
    lines.append("# Gemantria Export Delta")
    lines.append("")
    lines.append(f"*previous:* `{report['previous_file']}`")
    lines.append(f"*current:*  `{report['current_file']}`")
    lines.append("")
    lines.append(
        f"*removed_nodes:* {len(removed_nodes)}  •  *removed_edges:* {len(removed_edges)}  "
        f"•  *ok:* {'✅' if ok else '❌'}"
    )
    lines.append("")
    lines.append("## Strength stats")
    lines.append("```json")
    lines.append(json.dumps(report["strength_stats"], indent=2, sort_keys=True))
    lines.append("```")
    lines.append("")
    lines.append("## Added/Removed (node ids, edge pairs)")
    lines.append("```json")
    lines.append(
        json.dumps(
            {"nodes": report["nodes"], "edges": report["edges"]},
            indent=2,
            sort_keys=True,
        )
    )
    lines.append("```")
    lines.append("")
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"[eval.delta] wrote {JSON_OUT.relative_to(ROOT)}")
    print(f"[eval.delta] wrote {MD_OUT.relative_to(ROOT)}")
    print("[eval.delta] OK" if ok else "[eval.delta] DONE_WITH_FAILS")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
