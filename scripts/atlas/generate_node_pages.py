#!/usr/bin/env python3
"""
Atlas Node Pages (v1, PR-safe)
Reads Mermaid diagrams and _kpis.json (HINT-friendly) and writes per-node HTML pages under docs/atlas/nodes/.
Backlinks to ../index.html and optional evidence links if present.
STRICT/DB enrich may be added later behind STRICT_ATLAS_DSN.
"""

from __future__ import annotations

import json
import pathlib
import html
import datetime
import re
from typing import Dict, Set, Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
ATLAS_DIR = ROOT / "docs" / "atlas"
NODES_DIR = ATLAS_DIR / "nodes"
KPIS_JSON = ATLAS_DIR / "_kpis.json"
EVIDENCE_DIR = ATLAS_DIR.parent / "evidence"
OTEL_JSONL = ROOT / "evidence" / "otel.spans.jsonl"


def _load_kpis() -> Dict[str, Any]:
    """Load KPIs JSON if available."""
    if not KPIS_JSON.exists():
        return {"nodes": []}
    try:
        with KPIS_JSON.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {"nodes": []}


def _extract_nodes_from_mermaid(content: str) -> Set[str]:
    """Extract node IDs from Mermaid flowchart/gantt syntax."""
    nodes: Set[str] = set()
    # Match node definitions: "NodeName" or NodeName or NodeName[Label]
    # Also match edges: A --> B or "A" --> "B"
    # Skip click handlers and file paths
    patterns = [
        r'"([^"]+)"',  # Quoted nodes
        r"(\w+)\[",  # Nodes with labels: Node[Label]
        r"(\w+)\s*-->",  # Source nodes in edges
        r"-->\s*(\w+)",  # Target nodes in edges
        r'-->\s*"([^"]+)"',  # Quoted target nodes
    ]
    skip_keywords = {
        "flowchart",
        "TD",
        "LR",
        "gantt",
        "pie",
        "title",
        "section",
        "click",
        "Proof",
        "DSN",
        "View",
        "active",
        "runs",
        "errors",
        "latency",
        "details",
        "done",
        "des1",
        "des2",
        "des3",
        "des4",
    }
    skip_patterns = [
        r"\.html",  # File paths
        r"\.md",  # Markdown files
        r"http",  # URLs
        r"\.\./",  # Relative paths
        r"/evidence/",  # Evidence paths
    ]

    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0] if match else ""
            node = str(match).strip()
            # Filter out keywords, empty strings, and file paths
            if not node:
                continue
            if node in skip_keywords:
                continue
            # Skip if matches any skip pattern
            if any(re.search(sp, node, re.IGNORECASE) for sp in skip_patterns):
                continue
            # Only add if it looks like a valid node name (alphanumeric + underscore)
            if re.match(r"^[A-Za-z0-9_]+$", node):
                nodes.add(node)
    return nodes


def _collect_all_nodes() -> Dict[str, Dict[str, Any]]:
    """Collect all unique nodes from Mermaid files and _kpis.json."""
    nodes: Dict[str, Dict[str, Any]] = {}
    kpis = _load_kpis()

    # Try to get nodes from _kpis.json first (if it has a nodes array)
    if "nodes" in kpis and isinstance(kpis["nodes"], list):
        for n in kpis["nodes"]:
            nid = str(n.get("id") or "").strip()
            if nid:
                nodes[nid] = {
                    "id": nid,
                    "counts": n.get("counts", {}),
                    "last_seen": n.get("last_seen", "unknown"),
                    "window": n.get("window", kpis.get("window", "24h")),
                    "summary": n.get("summary", {}),
                }

    # Also extract from Mermaid files
    mermaid_files = [
        ATLAS_DIR / "execution_live.mmd",
        ATLAS_DIR / "dependencies.mmd",
        ATLAS_DIR / "kpis.mmd",
    ]

    for mmd_file in mermaid_files:
        if not mmd_file.exists():
            continue
        try:
            content = mmd_file.read_text(encoding="utf-8")
            extracted = _extract_nodes_from_mermaid(content)
            for nid in extracted:
                if nid not in nodes:
                    nodes[nid] = {
                        "id": nid,
                        "counts": {"ok": 0, "err": 0},
                        "last_seen": "unknown",
                        "window": kpis.get("window", "24h"),
                        "summary": {},
                    }
        except Exception:
            continue

    return nodes


def _write_node_page(node_id: str, rec: Dict[str, Any]) -> pathlib.Path:
    """Write a single node HTML page."""
    NODES_DIR.mkdir(parents=True, exist_ok=True)
    p = NODES_DIR / f"{node_id}.html"
    now = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    title = f"Atlas • {node_id}"
    counts = rec.get("counts") or {}
    ok = counts.get("ok", 0)
    err = counts.get("err", 0)
    last = rec.get("last_seen") or "unknown"
    window = rec.get("window") or "24h"
    summary = rec.get("summary") or {}

    # Check for evidence file
    ev_rel = f"../../evidence/{node_id}.md"
    has_ev = (EVIDENCE_DIR / f"{node_id}.md").exists()
    evidence_link = (
        f'<li><a href="{ev_rel}">Evidence (markdown)</a></li>'
        if has_ev
        else "<li><em>No dedicated evidence file</em></li>"
    )

    # Recent traces (last 3) for this node_id, if JSONL exists (HINT-safe)
    traces_html = "<em>No traces</em>"
    if OTEL_JSONL.exists():
        try:
            # Read last ~200 lines, filter by agent==node_id (llm.call) or tool==node_id (tool.call)
            lines = OTEL_JSONL.read_text(encoding="utf-8").splitlines()[-200:]
            items = []
            for ln in reversed(lines):
                try:
                    j = json.loads(ln)
                except Exception:
                    continue
                name = j.get("name")
                attrs = j.get("attrs") or {}
                if name == "llm.call" and attrs.get("agent") == node_id:
                    items.append(j)
                elif name == "tool.call" and attrs.get("tool") == node_id:
                    items.append(j)
                if len(items) >= 3:
                    break
            if items:

                def _fmt(it):
                    dur = it.get("dur_ms")
                    rid = it.get("run_id")
                    tid = it.get("trace_id")
                    sid = it.get("span_id")
                    return f"<li>{html.escape(it.get('ts', ''))} • {it.get('name')} • {dur}ms • run={html.escape(str(rid))} • trace={html.escape(str(tid or 'n/a'))} • span={html.escape(str(sid or 'n/a'))}</li>"

                traces_html = "<ul>" + "\n".join(_fmt(i) for i in items) + "</ul>"
        except Exception:
            pass

    body = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
body {{ font-family: system-ui, -apple-system, sans-serif; max-width: 800px; margin: 2em auto; padding: 0 1em; }}
h1 {{ color: #1a1a1a; }}
h2 {{ color: #333; margin-top: 1.5em; }}
ul {{ line-height: 1.6; }}
pre {{ background: #f5f5f5; padding: 1em; border-radius: 4px; overflow-x: auto; }}
small {{ color: #666; }}
</style>
</head>
<body>
<h1>{html.escape(title)}</h1>
<p><a href="../index.html">← Back to Atlas</a></p>
<ul>
  <li><strong>Window:</strong> {html.escape(str(window))}</li>
  <li><strong>OK:</strong> {ok} &nbsp; <strong>Errors:</strong> {err}</li>
  <li><strong>Last seen:</strong> {html.escape(str(last))}</li>
</ul>
<h2>Summary</h2>
<pre>{html.escape(json.dumps(summary, indent=2, ensure_ascii=False))}</pre>
<h2>Recent traces</h2>
{traces_html}
<h2>Related</h2>
<ul>
  {evidence_link}
  <li><a href="../dependencies.mmd">Dependencies (Mermaid)</a></li>
  <li><a href="../kpis.mmd">KPIs (Mermaid)</a></li>
  <li><a href="../execution_live.mmd">Execution Live (Mermaid)</a></li>
  <li><a href="../../evidence/otel.spans.jsonl">All spans (JSONL)</a></li>
</ul>
<hr>
<small>Generated at {now}</small>
</body>
</html>
"""
    p.write_text(body, encoding="utf-8")
    return p


def main():
    """Main entry point."""
    nodes = _collect_all_nodes()
    wrote = []
    for nid, rec in nodes.items():
        wrote.append(str(_write_node_page(nid, rec).relative_to(ROOT)))

    result = {"ok": True, "written": wrote, "count": len(wrote)}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
