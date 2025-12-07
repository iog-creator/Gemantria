from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Dict, Any
import html


SCHEMA_ID = "atlas.webproof.bundle.v1"
SCHEMA_VERSION = 1

# M14 artifact mappings: artifact_name -> (json_path, guard_verdict_path, title)
M14_ARTIFACTS = {
    "e66_graph_rollup": (
        "share/atlas/graph/rollup.json",
        "evidence/guard_m14_graph_rollup_versioned.verdict.json",
        "Graph Rollup Metrics (E66)",
    ),
    "e67_drilldown": (
        "share/atlas/nodes/drilldown.sample.json",
        "evidence/guard_m14_node_drilldowns_links.verdict.json",
        "Node Drilldown Links (E67)",
    ),
    "e68_screenshots": (
        "share/atlas/screenshots/manifest.json",
        "evidence/guard_m14_screenshot_manifest_canonicalized.verdict.json",
        "Screenshot Manifest (E68)",
    ),
    "e69_reranker": (
        "share/atlas/badges/reranker.json",
        "evidence/guard_m14_reranker_badges.verdict.json",
        "Reranker Badges (E69)",
    ),
}


def _generate_webproof_html(artifact_name: str, json_path: str, guard_path: str, title: str, out_dir: Path) -> Path:
    """Generate a single webproof HTML page with backlinks."""
    json_file = Path(json_path)
    guard_file = Path(guard_path)

    # Load JSON data for display
    json_data = {}
    if json_file.exists():
        try:
            json_data = json.loads(json_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    # Load guard verdict for display
    guard_data = {}
    if guard_file.exists():
        try:
            guard_data = json.loads(guard_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    # Calculate relative paths from output HTML to JSON/guard files
    # Output is in docs/atlas/webproof/, so:
    # - share/atlas/... -> ../../../share/atlas/...
    # - evidence/... -> ../../../evidence/...
    json_rel = f"../../../{json_path}"
    guard_rel = f"../../../{guard_path}"

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    html_content = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atlas Webproof • {html.escape(title)}</title>
<style>
body {{ font-family: system-ui, -apple-system, sans-serif; max-width: 900px; margin: 2em auto; padding: 0 1em; }}
h1 {{ color: #1a1a1a; }}
h2 {{ color: #333; margin-top: 1.5em; }}
.backlinks {{ background: #f5f5f5; padding: 1em; border-radius: 8px; margin: 1em 0; }}
.backlinks ul {{ list-style: none; padding: 0; }}
.backlinks li {{ margin: 0.5em 0; }}
.backlinks a {{ color: #0066cc; text-decoration: none; }}
.backlinks a:hover {{ text-decoration: underline; }}
pre {{ background: #f5f5f5; padding: 1em; border-radius: 4px; overflow-x: auto; }}
.badge {{ display: inline-block; background: #eef; border: 1px solid #ccd; border-radius: 4px; padding: 2px 8px; font-size: 0.85rem; }}
.ok {{ color: #28a745; }}
.error {{ color: #dc3545; }}
small {{ color: #666; }}
</style>
</head>
<body>
<h1>{html.escape(title)}</h1>
<p><a href="../index.html">← Back to Atlas</a></p>

<div class="backlinks">
<h2>Evidence Backlinks</h2>
<ul>
  <li><a href="{html.escape(json_rel)}" data-testid="backlink-{artifact_name}-json">Raw JSON: {html.escape(json_path)}</a></li>
  <li><a href="{html.escape(guard_rel)}" data-testid="backlink-{artifact_name}-guard">Guard Verdict: {html.escape(guard_path)}</a></li>
</ul>
</div>

<h2>JSON Data</h2>
<pre>{html.escape(json.dumps(json_data, indent=2, ensure_ascii=False))}</pre>

<h2>Guard Verdict</h2>
<pre>{html.escape(json.dumps(guard_data, indent=2, ensure_ascii=False))}</pre>

<hr>
<small>Generated at {now}</small>
</body>
</html>
"""

    out_file = out_dir / f"{artifact_name}.html"
    out_file.write_text(html_content, encoding="utf-8")
    return out_file


def generate_webproof_bundle(out_dir: Path, mode: str = "HINT") -> Dict[str, Any]:
    """Generate webproof HTML bundle with backlinks for all M14 artifacts."""
    out_dir.mkdir(parents=True, exist_ok=True)

    generated_files = []
    for artifact_name, (json_path, guard_path, title) in M14_ARTIFACTS.items():
        html_file = _generate_webproof_html(artifact_name, json_path, guard_path, title, out_dir)
        generated_files.append(str(html_file.relative_to(out_dir.parent.parent.parent)))

    # Generate index page
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    index_html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atlas Webproof Bundle • M14</title>
<style>
body {{ font-family: system-ui, -apple-system, sans-serif; max-width: 900px; margin: 2em auto; padding: 0 1em; }}
h1 {{ color: #1a1a1a; }}
ul {{ line-height: 1.8; }}
a {{ color: #0066cc; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<h1>Atlas Webproof Bundle • M14</h1>
<p><a href="../index.html">← Back to Atlas</a></p>
<h2>M14 Artifacts</h2>
<ul>
  <li><a href="e66_graph_rollup.html">Graph Rollup Metrics (E66)</a></li>
  <li><a href="e67_drilldown.html">Node Drilldown Links (E67)</a></li>
  <li><a href="e68_screenshots.html">Screenshot Manifest (E68)</a></li>
  <li><a href="e69_reranker.html">Reranker Badges (E69)</a></li>
</ul>
<hr>
<small>Generated at {timestamp}</small>
</body>
</html>
"""

    index_file = out_dir / "index.html"
    index_file.write_text(index_html, encoding="utf-8")
    generated_files.append(str(index_file.relative_to(out_dir.parent.parent.parent)))

    payload: Dict[str, Any] = {
        "schema": {"id": SCHEMA_ID, "version": SCHEMA_VERSION},
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": mode,
        "files": generated_files,
        "artifacts": list(M14_ARTIFACTS.keys()),
        "ok": True,
    }

    return payload


def main() -> int:
    out_dir = Path(os.environ.get("WEBPROOF_OUT", "docs/atlas/webproof"))
    mode = os.environ.get("STRICT_MODE", "HINT").upper()
    generate_webproof_bundle(out_dir, mode=mode)
    print(f"wrote webproof bundle to: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
