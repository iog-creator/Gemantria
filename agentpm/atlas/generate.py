from __future__ import annotations

from pathlib import Path
from datetime import datetime, UTC
import json

INDEX_HTML = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Atlas — Index</title><style>body{{font-family:system-ui;margin:2rem}}a{{display:block;margin:.25rem 0}}</style>
<h1>Atlas — Index</h1>
<p>Generated at: {ts}</p>
<nav>
  <a href="graph.html">Graph view</a>
  <a href="nodes/0.html">Sample node 0</a>
  <a href="nodes/1.html">Sample node 1</a>
</nav>
</html>"""

GRAPH_HTML = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Atlas — Graph</title><style>body{{font-family:system-ui;margin:2rem}}</style>
<h1>Atlas — Graph</h1>
<p>Placeholder graph view. Generated at: {ts}</p>
</html>"""

NODE_HTML = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Atlas — Node {i}</title><style>body{{font-family:system-ui;margin:2rem}}</style>
<h1>Atlas — Node {i}</h1>
<p>Placeholder node page. Generated at: {ts}</p>
</html>"""


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate(out_dir: str = "share/atlas", nodes=(0, 1)) -> dict[str, str]:
    ts = _now_iso()
    root = Path(out_dir)
    (root / "nodes").mkdir(parents=True, exist_ok=True)
    (root / "index.html").write_text(INDEX_HTML.format(ts=ts), encoding="utf-8")
    (root / "graph.html").write_text(GRAPH_HTML.format(ts=ts), encoding="utf-8")
    paths = {
        "index": str(root / "index.html"),
        "graph": str(root / "graph.html"),
        "nodes": [],
    }
    for i in nodes:
        p = root / "nodes" / f"{i}.html"
        p.write_text(NODE_HTML.format(i=i, ts=ts), encoding="utf-8")
        paths["nodes"].append(str(p))
    return paths


if __name__ == "__main__":
    paths = generate()
    print(json.dumps({"ok": True, "paths": paths}))
