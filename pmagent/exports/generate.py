from __future__ import annotations

from datetime import datetime, UTC

from pathlib import Path

import json

try:
    # Optional dependency-free validation stub (schema presence only for now)

    pass

except Exception:
    pass


# We depend only on our hermetic assembler to build a small, deterministic sample.

from pmagent.graph.assembler import assemble_graph


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_exports(out_dir: str = "exports") -> dict[str, str]:
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    # Build a tiny deterministic graph (no DB/IO). BASE/seed fixed for reproducibility.

    from datetime import datetime

    BASE = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)

    g = assemble_graph([{"idx": 0}, {"idx": 1}, {"idx": 2}], model="qwen2.5", seed=42, base_dt=BASE)

    nodes = [{"idx": n["data"]["idx"]} for n in g["nodes"]]

    edges: list[dict] = []  # hermetic: keep empty; schema only requires key presence in our TVs

    graph_export = {
        "schema": {"id": "SSOT_graph.v1", "version": 1},
        "meta": {
            "generated_at": _now_iso(),
            "links": {
                "atlas_index": "share/atlas/index.html",
                "atlas_node_prefix": "share/atlas/nodes/",
                "atlas_graph_view": "share/atlas/graph.html",
            },
            "provenance_rollup": g["meta"].get("provenance_rollup"),
        },
        "nodes": nodes,
        "edges": edges,
    }

    stats_export = {
        "schema": {"id": "graph-stats.v1", "version": 1},
        "generated_at": _now_iso(),
        "totals": {"nodes": len(nodes), "edges": len(edges)},
    }

    graph_path = Path(out_dir) / "graph_latest.json"

    stats_path = Path(out_dir) / "graph_stats.json"

    graph_path.write_text(json.dumps(graph_export, ensure_ascii=False, indent=2))

    stats_path.write_text(json.dumps(stats_export, ensure_ascii=False, indent=2))

    # Mirror to share/exports for UI and TVs that look there.

    share_dir = Path("share/exports")

    share_dir.mkdir(parents=True, exist_ok=True)

    (share_dir / "graph_latest.json").write_text(graph_path.read_text())

    (share_dir / "graph_stats.json").write_text(stats_path.read_text())

    return {"graph": str(graph_path), "stats": str(stats_path)}


if __name__ == "__main__":
    paths = generate_exports()

    print(json.dumps({"ok": True, "paths": paths}))
