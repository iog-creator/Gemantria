from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json

INDEX_HTML = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Atlas — Index</title><style>body{font-family:system-ui;margin:2rem}a{display:block;margin:.25rem 0}</style>
<h1>Atlas — Index</h1>
<p>Generated at: {ts}</p>
<nav>
  <a href="graph.html">Graph view</a>
  {node_links}
</nav>
</html>"""

GRAPH_HTML = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Atlas — Graph</title><style>body{font-family:system-ui;margin:2rem}</style>
<a href="index.html">← Back to Atlas</a>
<h1>Atlas — Graph</h1>
<p>Placeholder graph view. Generated at: {ts}</p>
</html>"""

NODE_HTML = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Atlas — Node {i}</title><style>body{font-family:system-ui;margin:2rem}</style>
<a href="../index.html">← Back to Atlas</a>
<h1>Atlas — Node {i}</h1>
<section id="audit">
  <h2>Audit</h2>
  <dl>
    <dt>Batch ID</dt><dd>{batch_id}</dd>
    <dt>Provenance Hash</dt><dd>{prov_hash}</dd>
  </dl>
</section>
<p>Generated at: {ts}</p>
</html>"""

def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

def _load_export(path: str) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return {}

def generate(out_dir: str = "share/atlas",
             export_paths=("share/exports/graph_latest.json", "exports/graph_latest.json")) -> dict[str, str]:
    ts = _now_iso()
    # Prefer the share/ export; fall back to local exports directory
    export = {}
    for p in export_paths:
        if Path(p).exists():
            export = _load_export(p); break

    # Derive node ids + simple audit info from export (if present); fallback to [0,1].
    nodes = [n.get("idx") for n in export.get("nodes", []) if isinstance(n, dict) and "idx" in n]
    if not nodes:
        nodes = [0, 1]

    batch_id = (export.get("meta") or {}).get("provenance_rollup") or {}
    batch_id_str = str(export.get("batch_id", batch_id))  # tolerate absent field
    # create a stable-ish fake hash if not present
    prov_hash = (export.get("meta") or {}).get("links") or {}
    prov_hash_str = str(hash(json.dumps(prov_hash, sort_keys=True)))  # display-only

    root = Path(out_dir)
    (root / "nodes").mkdir(parents=True, exist_ok=True)

    # Index with deep-links
    node_links = "\n  ".join(f'<a href="nodes/{i}.html">Node {i}</a>' for i in nodes[:10])
    (root / "index.html").write_text(INDEX_HTML.format(ts=ts, node_links=node_links), encoding="utf-8")
    (root / "graph.html").write_text(GRAPH_HTML.format(ts=ts), encoding="utf-8")

    paths = {"index": str(root / "index.html"), "graph": str(root / "graph.html"), "nodes": []}
    for i in nodes:
        p = root / "nodes" / f"{i}.html"
        p.write_text(NODE_HTML.format(i=i, ts=ts, batch_id=batch_id_str, prov_hash=prov_hash_str), encoding="utf-8")
        paths["nodes"].append(str(p))
    return paths

if __name__ == "__main__":
    print(json.dumps({"ok": True, "paths": generate()}))
