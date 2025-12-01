# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import json
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
OUTM = EVAL / "summary.md"
OUTJ = EVAL / "summary.json"


def _load(name):
    p = EVAL / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def main() -> int:
    graph = _load("graph_latest.json") or {}
    delta = _load("delta.json") or {}
    prov = _load("provenance.json") or {}
    cent = _load("centrality.json") or {}

    edges = graph.get("edges", [])
    strong = sum(1 for e in edges if e.get("class") == "strong")
    weak = sum(1 for e in edges if e.get("class") == "weak")
    other = len(edges) - strong - weak

    top10 = sorted(
        ((n, (cent.get(n) or {}).get("eigenvector", 0.0)) for n in (cent.keys() if isinstance(cent, dict) else [])),
        key=lambda x: x[1],
        reverse=True,
    )[:10]

    summary = {
        "generated_at": int(time.time()),
        "git": prov.get("git"),
        "counts": {
            "nodes": len(graph.get("nodes", [])),
            "edges": len(edges),
            "strong": strong,
            "weak": weak,
            "other": other,
        },
        "delta": delta.get("counts"),
        "artifacts": prov.get("counts", {}).get("artifacts"),
        "top10_eigenvector": top10,
    }
    OUTJ.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    md = []
    md.append("# Eval Run Summary\n")
    if prov.get("git"):
        g = prov["git"]
        md.append(f"- commit: `{g.get('commit')}`  branch: `{g.get('branch')}`  describe: `{g.get('describe')}`")
    md.append(f"- nodes: **{summary['counts']['nodes']}**  edges: **{summary['counts']['edges']}**")
    md.append(f"- edges by class: strong **{strong}**, weak **{weak}**, other **{other}**")
    if summary.get("delta"):
        d = summary["delta"]
        md.append(f"- delta strong: **{d['delta']['strong']:+d}**, delta weak: **{d['delta']['weak']:+d}**")
    if summary.get("artifacts") is not None:
        md.append(f"- artifacts cataloged: **{summary['artifacts']}**")
    if top10:
        md.append("\n**Top-10 eigenvector nodes**")
        for nid, ev in top10:
            md.append(f"- `{nid}` — {ev:.6f}")
    OUTM.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"[summary] wrote {OUTM.relative_to(ROOT)} and {OUTJ.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
