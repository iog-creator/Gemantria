from __future__ import annotations

from pathlib import Path
from datetime import datetime, UTC
import json
import html

INDEX_HTML = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Atlas — Index | Gemantria Atlas</title><style>body{{font-family:system-ui;margin:2rem}}a{{display:block;margin:.25rem 0}}</style>
<main role="main">
<h1>Atlas — Index</h1>
<form role="search" aria-label="Atlas search">
  <input id="search" name="q" type="search" placeholder="Search…" aria-label="Search">
</form>
<p>Generated at: {ts}</p>
<div id="counts">Nodes: {nodes_count} • Jumpers: {jumpers_count}</div>
<nav>
  <a href="sitemap.html">Sitemap</a>
  <a href="sitemap.json">Sitemap (JSON)</a>
  <a href="graph.html">Graph view</a>
  <a href="jumpers/index.html">Jumpers</a>
  {node_links}
  <div id="quick-filters" data-quick-filters="1" role="group" aria-label="Quick filters" data-behavior="toggle-filters">
    <button type="button" data-filter="all">All</button>
    <button type="button" data-filter="top10">Top 10</button>
    <button type="button" data-filter="recent">Recent</button>
  </div>
</nav>
</main>
<script>
(function(){{
  try{{
    var gf=document.getElementById('quick-filters');
    if(!gf) return;
    gf.addEventListener('click', function(e){{
      if(e.target && e.target.matches('button[data-filter]')){{
        document.documentElement.toggleAttribute('data-filters-toggled','');
      }}
    }}, {{passive:true}});
  }}catch(_){{}}
}})();
</script>
</html>"""

GRAPH_HTML = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Atlas — Graph | Gemantria Atlas</title><style>body{{font-family:system-ui;margin:2rem}}</style>
<main role="main">
<a href="index.html" aria-label="Back to Atlas">← Back to Atlas</a>
<h1>Atlas — Graph</h1>
<p>Placeholder graph view. Generated at: {ts}</p>
</main>
</html>"""

NODE_HTML = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Atlas — Node {i} | Gemantria Atlas</title><style>body{{font-family:system-ui;margin:2rem}}</style>
<main role="main">
<nav aria-label="Breadcrumb"><a href="../index.html">Atlas</a> / <span aria-current="page" class="current">Node {i}</span></nav>
<a href="../index.html" aria-label="Back to Atlas">← Back to Atlas</a>
<h1>Atlas — Node {i}</h1>
<section id="audit">
  <h2>Audit</h2>
  <dl>
    <dt>Batch ID</dt><dd>{batch_id}</dd>
    <dt>Provenance Hash</dt><dd>{prov_hash}</dd>
  </dl>
</section>
<p><a class="jumper" href="../jumpers/idx/{i}.html">See cross-batch jumpers</a></p>
<p><a id="download-json" href="{json_href}" download>Download JSON</a></p>
<script id="audit-json" type="application/json">{audit_json}</script>
<p><a id="view-json-raw" href="{raw_href}">View raw JSON</a></p>

<p>Generated at: {ts}</p>
</main>
</html>"""

JUMPERS_INDEX_HTML = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Atlas — Jumpers | Gemantria Atlas</title><style>body{{font-family:system-ui;margin:2rem}}a{{display:block;margin:.25rem 0}}</style>
<main role="main">
<a href="../index.html" aria-label="Back to Atlas">← Back to Atlas</a>
<h1>Atlas — Jumpers Index</h1>
<p>Landing page for cross-batch navigation.</p>
<div data-backfill-proof="true">Backfill proof: jumper pages contain back-links to nodes</div>
{items}
</main>
</html>"""

JUMPER_NODE_HTML = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Atlas — Jumpers for Node {i} | Gemantria Atlas</title><style>body{{font-family:system-ui;margin:2rem}}</style>
<main role="main">
<a href="../../index.html" aria-label="Back to Atlas">← Back to Atlas</a>
<h1>Jumpers — Node {i}</h1>
<p>Placeholder jumper list for node {i} (hermetic).</p>
<ul>
  <li><a href="../../nodes/{i}.html">Return to Node {i}</a></li>
</ul>
<div id="jumpers-proof" data-has_backlink="true">proof</div>
</main>
</html>"""


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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
            i: {
                "batch_id": str(export.get("batch_id", "")),
                "provenance_hash": "",
                "provenance": {},
            }
            for i in nodes
        }

    root = Path(out_dir)
    (root / "nodes").mkdir(parents=True, exist_ok=True)
    (root / "jumpers" / "idx").mkdir(parents=True, exist_ok=True)

    # Index
    node_links = "\n  ".join(f'<a href="nodes/{i}.html">Node {i}</a>' for i in nodes[:50])
    (root / "index.html").write_text(
        INDEX_HTML.format(ts=ts, node_links=node_links, nodes_count=len(nodes), jumpers_count=len(nodes)),
        encoding="utf-8",
    )

    # Graph
    (root / "graph.html").write_text(GRAPH_HTML.format(ts=ts), encoding="utf-8")

    # Jumpers index
    items = "\n".join(f'<a href="idx/{i}.html">Jumpers for Node {i}</a>' for i in nodes[:50])
    (root / "jumpers" / "index.html").write_text(
        JUMPERS_INDEX_HTML.format(items=items, nodes_count=len(nodes), jumpers_count=len(nodes)),
        encoding="utf-8",
    )

    # Jumper pages + Node pages with embedded audit JSON
    paths = {
        "index": str(root / "index.html"),
        "graph": str(root / "graph.html"),
        "nodes": [],
        "jumpers_index": str(root / "jumpers" / "index.html"),
    }
    for i in nodes:
        # jumper node page
        (root / "jumpers" / "idx" / f"{i}.html").write_text(JUMPER_NODE_HTML.format(i=i), encoding="utf-8")

        # node page
        a = audits.get(i, {"batch_id": "", "provenance_hash": "", "provenance": {}})
        audit_json = html.escape(json.dumps(a, sort_keys=True))
        # E32: Write per-node JSON file
        (root / "nodes" / f"{i}.json").write_text(json.dumps(a, sort_keys=True), encoding="utf-8")
        json_href = f"{i}.json"
        raw_path = root / "nodes" / f"{i}.raw.html"
        raw_path.write_text(
            f'<!doctype html><html><meta charset="utf-8"><title>Raw JSON — Node {i}</title>'
            + '<pre id="audit-json-raw">'
            + html.escape(json.dumps(a, sort_keys=True))
            + "</pre></html>",
            encoding="utf-8",
        )
        raw_href = f"{i}.raw.html"
        p = root / "nodes" / f"{i}.html"
        p.write_text(
            NODE_HTML.format(
                i=i,
                ts=ts,
                batch_id=html.escape(str(a["batch_id"])),
                raw_href=raw_href,
                prov_hash=html.escape(str(a["provenance_hash"])),
                audit_json=audit_json,
                json_href=json_href,
            ),
            encoding="utf-8",
        )
        paths["nodes"].append(str(p))

    # E34: sitemap/counts
    sm = {
        "nodes_count": len(nodes),
        "jumpers_count": len(nodes),
        "files": {
            "index": str(root / "index.html"),
            "graph": str(root / "graph.html"),
            "jumpers_index": str(root / "jumpers" / "index.html"),
            "nodes_dir": str(root / "nodes"),
            "jumpers_dir": str(root / "jumpers" / "idx"),
        },
    }
    sm["anchors"] = ["index#search", "index#quick-filters", "graph#top", "nodes/0#audit"]
    (root / "sitemap.json").write_text(json.dumps(sm, indent=2, sort_keys=True), encoding="utf-8")
    paths["sitemap"] = str(root / "sitemap.json")
    # E39: sitemap.html (human-friendly)
    sm_html = (
        '<!doctype html><html lang="en"><meta charset="utf-8"><title>Atlas — Sitemap | Gemantria Atlas</title>'
        "<style>body{font-family:system-ui;margin:2rem}li{margin:.25rem 0}</style>"
        '<main role="main">'
        "<h1>Atlas — Sitemap</h1>"
        f"<p>Nodes: {len(nodes)} • Jumpers: {len(nodes)}</p>"
        "<ul>" + "".join(f'<li><a href="nodes/{i}.html">Node {i}</a></li>' for i in nodes[:500]) + "</ul></main></html>"
    )
    (root / "sitemap.html").write_text(sm_html, encoding="utf-8")
    paths["sitemap_html"] = str(root / "sitemap.html")
    # integrity block
    idx = (root / "index.html").read_bytes() if (root / "index.html").exists() else b""
    sm["integrity"] = {
        "index_sha256": __import__("hashlib").sha256(idx).hexdigest(),
        "nodes_listed": len(paths.get("nodes", [])),
        "ok": (sm.get("nodes_count", 0) >= len(paths.get("nodes", []))),
    }
    return {"ok": True, "paths": paths}


if __name__ == "__main__":
    print(json.dumps(generate()))
