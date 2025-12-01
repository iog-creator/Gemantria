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
JSON_OUT = OUTDIR / "history.json"
MD_OUT = OUTDIR / "history.md"

EXPORT_GLOB = str(ROOT / "exports" / "graph_*.json")


def _load_json(p: pathlib.Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def _parse_ts_from_name(name: str) -> tuple[int, str]:
    base = pathlib.Path(name).name
    m = re.search(r"graph_(\d{4}-?\d{2}-?\d{2})[T_]?(\d{2}-?\d{2}-?\d{2})?Z?", base)
    if m:
        d = m.group(1).replace("-", "")
        t = (m.group(2) or "000000").replace("-", "")
        try:
            return (int(d + t), base)
        except Exception:
            pass
    m2 = re.search(r"graph_(\d{8})(\d{6})?", base)
    if m2:
        d = m2.group(1)
        t = m2.group(2) or "000000"
        return (int(d + t), base)
    # fallback to mtime sort
    return (0, base)


def _summarize_file(p: pathlib.Path) -> dict[str, Any]:
    doc = _load_json(p)
    edges = doc.get("edges", [])
    nodes = doc.get("nodes", [])

    # Handle case where edges is an integer (stats files) vs array (graph files)
    if isinstance(edges, int):
        edge_count = edges
        strengths = []
    elif isinstance(edges, list):
        edge_count = len(edges)
        strengths = [e.get("strength") for e in edges if isinstance(e, dict)]
    else:
        edge_count = 0
        strengths = []

    nums = [float(x) for x in strengths if isinstance(x, int | float)]
    in_range = [x for x in nums if 0.30 <= x <= 0.95]
    frac = len(in_range) / max(1, len(nums))

    # Handle case where nodes is an integer (stats files) vs array (graph files)
    if isinstance(nodes, int):
        node_count = nodes
        dim_vals = []
    elif isinstance(nodes, list):
        node_count = len(nodes)
        dim_vals = [n.get("embedding_dim") for n in nodes if isinstance(n, dict)]
    else:
        node_count = 0
        dim_vals = []

    dim_present = [v for v in dim_vals if v is not None]
    dim_ok = all(v == 1024 for v in dim_present) if dim_present else True
    return {
        "file": str(p.relative_to(ROOT)),
        "nodes": node_count,
        "edges": edge_count,
        "strength": {"count": len(nums), "ok_frac_0.30_0.95": round(frac, 4)},
        "embedding_dim_if_present_1024": dim_ok,
    }


def main() -> int:
    print("[eval.history] starting")
    OUTDIR.mkdir(parents=True, exist_ok=True)

    files = sorted(glob.glob(EXPORT_GLOB), key=_parse_ts_from_name)
    if not files:
        JSON_OUT.write_text(
            json.dumps({"results": [], "summary": {"series_n": 0}}, indent=2),
            encoding="utf-8",
        )
        MD_OUT.write_text("# Gemantria Export History\n\n_No exports found._\n", encoding="utf-8")
        print(f"[eval.history] wrote {JSON_OUT.relative_to(ROOT)}")
        print(f"[eval.history] wrote {MD_OUT.relative_to(ROOT)}")
        print("[eval.history] DONE_WITH_EMPTY")
        return 0

    # Filter to only files that have actual graph data (arrays, not just counts)
    graph_files = []
    for f in files:
        try:
            doc = _load_json(pathlib.Path(f))
            nodes = doc.get("nodes", [])
            edges = doc.get("edges", [])
            # Only include files where nodes/edges are arrays with content
            if isinstance(nodes, list) and isinstance(edges, list) and len(nodes) > 0 and len(edges) > 0:
                graph_files.append(f)
        except Exception:
            continue

    if not graph_files:
        JSON_OUT.write_text(
            json.dumps({"results": [], "summary": {"series_n": 0}}, indent=2),
            encoding="utf-8",
        )
        MD_OUT.write_text(
            "# Gemantria Export History\n\n_No valid graph exports found._\n",
            encoding="utf-8",
        )
        print(f"[eval.history] wrote {JSON_OUT.relative_to(ROOT)}")
        print(f"[eval.history] wrote {MD_OUT.relative_to(ROOT)}")
        print("[eval.history] DONE_WITH_EMPTY")
        return 0

    series = [_summarize_file(pathlib.Path(f)) for f in graph_files]
    ok = all(
        [
            all(item["nodes"] > 0 for item in series),
            all(item["edges"] > 0 for item in series),
            all(item["strength"]["ok_frac_0.30_0.95"] >= 0.70 for item in series),
            all(item["embedding_dim_if_present_1024"] for item in series),
        ]
    )

    report = {
        "ts_unix": int(time.time()),
        "summary": {
            "series_n": len(series),
            "ok_all": ok,
            "nodes_nonzero_all": all(item["nodes"] > 0 for item in series),
            "edges_nonzero_all": all(item["edges"] > 0 for item in series),
            "ok_frac_threshold": 0.70,
        },
        "results": series,
    }
    JSON_OUT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    lines = []
    lines.append("# Gemantria Export History")
    lines.append("")
    lines.append(f"*series:* {len(series)}  •  *ok:* {'✅' if ok else '❌'}")
    lines.append("")
    lines.append("| file | nodes | edges | strength ok frac (0.30-0.95) | dims ok (if present) |")
    lines.append("|---|---:|---:|---:|:---:|")
    for item in series:
        lines.append(
            f"| {item['file']} | {item['nodes']} | {item['edges']} | "
            f"{item['strength']['ok_frac_0.30_0.95']} | {'✅' if item['embedding_dim_if_present_1024'] else '❌'} |"
        )
    lines.append("")
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"[eval.history] wrote {JSON_OUT.relative_to(ROOT)}")
    print(f"[eval.history] wrote {MD_OUT.relative_to(ROOT)}")
    print("[eval.history] OK" if ok else "[eval.history] DONE_WITH_FAILS")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
