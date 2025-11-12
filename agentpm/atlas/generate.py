from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import html

INDEX_HTML = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Atlas — Index</title><style>body{{font-family:system-ui;margin:2rem}}a{{display:block;margin:.25rem 0}}</style>
<h1>Atlas — Index</h1>
<p>Generated at: {ts}</p>
<nav>
  <a href="graph.html">Graph view</a>
  <a href="jumpers/index.html">Jumpers</a>
  {node_links}
</nav>
</html>"""

GRAPH_HTML = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Atlas — Graph</title><style>body{{font-family:system-ui;margin:2rem}}</style>
<a href="index.html">← Back to Atlas</a>
<h1>Atlas — Graph</h1>
<p>Placeholder graph view. Generated at: {ts}</p>
</html>"""

NODE_HTML = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Atlas — Node {i}</title><style>body{{font-family:system-ui;margin:2rem}}</style>
<a href="../index.html">← Back to Atlas</a>
<h1>Atlas — Node {i}</h1>
<section id="audit">
  <h2>Audit</h2>
  <dl>
    <dt>Batch ID</dt><dd>{batch_id}</dd>
    <dt>Provenance Hash</dt><dd>{prov_hash}</dd>
  </dl>
</section>
<p><a class="jumper" href="../jumpers/idx/{i}.html">See cross-batch jumpers</a></p>
<script id="audit-json" type="application/json">{audit_json}</script>
<p>Generated at: {ts}</p>
</html>"""

JUMPERS_INDEX_HTML = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Atlas — Jumpers</title><style>body{{font-family:system-ui;margin:2rem}}a{{display:block;margin:.25rem 0}}</style>
<a href="../index.html">← Back to Atlas</a>
<h1>Atlas — Jumpers Index</h1>
<p>Landing page for cross-batch navigation.</p>
{items}
</html>"""

JUMPER_NODE_HTML = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Atlas — Jumpers for Node {i}</title><style>body{{font-family:system-ui;margin:2rem}}</style>
<a href="../../index.html">← Back to Atlas</a>
<h1>Jumpers — Node {i}</h1>
<p>Placeholder jumper list for node {i} (hermetic).</p>
<ul>
  <li><a href="../../nodes/{i}.html">Return to Node {i}</a></li>
</ul>
</html>"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _first_existing(paths: list[str]) -> Path | None:
    for p in paths:
        pp = Path(p)
        if pp.exists():
            return pp
    return None


def generate(
    out_dir: str = "share/atlas",
    export_paths=("share/exports/graph_latest.json", "exports/graph_latest.json"),
) -> dict:
    ts = _now_iso()
    export_path = _first_existing(list(export_paths))
    export = _load_json(export_path) if export_path else {}

    # Collect nodes + simple audit from export if present; fallback to small demo set
    nodes = []
    audits = {}
    for n in export.get("nodes", []):
        if isinstance(n, dict):
            i = n.get("data", {}).get("idx", n.get("idx"))
            if i is None:
                continue
            nodes.append(i)
            prov = (n.get("meta") or {}).get("provenance") or {}
            audit = (n.get("meta") or {}).get("audit") or {}
            audits[i] = {
                "batch_id": audit.get("batch_id", export.get("batch_id", "")),
                "provenance_hash": audit.get("provenance_hash", ""),
                "provenance": prov,
            }
    if not nodes:
        nodes = [0, 1, 2]
        audits = {
            i: {"batch_id": str(export.get("batch_id", "")), "provenance_hash": "", "provenance": {}}
            for i in nodes
        }

    root = Path(out_dir)
    (root / "nodes").mkdir(parents=True, exist_ok=True)
    (root / "jumpers" / "idx").mkdir(parents=True, exist_ok=True)

    # Index
    node_links = "\n  ".join(f'<a href="nodes/{i}.html">Node {i}</a>' for i in nodes[:50])
    (root / "index.html").write_text(INDEX_HTML.format(ts=ts, node_links=node_links), encoding="utf-8")

    # Graph
    (root / "graph.html").write_text(GRAPH_HTML.format(ts=ts), encoding="utf-8")

    # Jumpers index
    items = "\n".join(f'<a href="idx/{i}.html">Jumpers for Node {i}</a>' for i in nodes[:50])
    (root / "jumpers" / "index.html").write_text(JUMPERS_INDEX_HTML.format(items=items), encoding="utf-8")

    # Jumper pages + Node pages with embedded audit JSON
    paths = {
        "index": str(root / "index.html"),
        "graph": str(root / "graph.html"),
        "nodes": [],
        "jumpers_index": str(root / "jumpers" / "index.html"),
    }
    for i in nodes:
        # jumper node page
        (root / "jumpers" / "idx" / f"{i}.html").write_text(
            JUMPER_NODE_HTML.format(i=i), encoding="utf-8"
        )

        # node page
        a = audits.get(i, {"batch_id": "", "provenance_hash": "", "provenance": {}})
        audit_json = html.escape(json.dumps(a, sort_keys=True))
        p = root / "nodes" / f"{i}.html"
        p.write_text(
            NODE_HTML.format(
                i=i,
                ts=ts,
                batch_id=html.escape(str(a["batch_id"])),
                prov_hash=html.escape(str(a["provenance_hash"])),
                audit_json=audit_json,
            ),
            encoding="utf-8",
        )
        paths["nodes"].append(str(p))

    return {"ok": True, "paths": paths}


if __name__ == "__main__":
    print(json.dumps(generate()))
