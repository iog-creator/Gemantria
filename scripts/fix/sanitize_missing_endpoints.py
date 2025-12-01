# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import json
import pathlib
import sys
import time
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXPORTS = ROOT / "exports"
LATEST = EXPORTS / "graph_latest.json"


def _load(p: pathlib.Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def _node_id_set(doc: dict[str, Any]) -> set[Any]:
    out = set()
    for n in doc.get("nodes", []) or []:
        if isinstance(n, dict) and "id" in n:
            out.add(n.get("id"))
    return out


def main() -> int:
    print("[data.sanitize] starting")
    if not LATEST.exists():
        print("[data.sanitize] FAIL no exports/graph_latest.json")
        return 2
    doc = _load(LATEST)
    node_ids = _node_id_set(doc)

    kept_edges: list[dict[str, Any]] = []
    dropped_edges: list[dict[str, Any]] = []
    for e in doc.get("edges", []) or []:
        if not isinstance(e, dict):
            continue
        s, t = e.get("source"), e.get("target")
        if s in node_ids and t in node_ids:
            kept_edges.append(e)
        else:
            dropped_edges.append(e)

    sanitized = dict(doc)
    sanitized["edges"] = kept_edges

    ts = time.strftime("%Y%m%d%H%M%S")
    out_path = EXPORTS / f"graph_sanitized_{ts}.json"
    out_path.write_text(json.dumps(sanitized, indent=2, sort_keys=True), encoding="utf-8")

    # lightweight marker to latest sanitized
    (EXPORTS / "graph_sanitized.json").write_text(json.dumps(sanitized, indent=2, sort_keys=True), encoding="utf-8")  # noqa: E501

    print(f"[data.sanitize] kept_edges={len(kept_edges)} dropped_edges={len(dropped_edges)}")
    print(f"[data.sanitize] wrote {out_path.relative_to(ROOT)}")
    print(f"[data.sanitize] wrote {(EXPORTS / 'graph_sanitized.json').relative_to(ROOT)}")
    print("[data.sanitize] OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
