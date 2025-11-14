#!/usr/bin/env python3
"""
E91 — Guard Receipts Index Generator

Scans the evidence/ directory for guard-related JSON receipts and
builds an HTML index page for Atlas under docs/atlas/browser/guard_receipts.html.

Design goals:
- DB-off tolerant (no DB access)
- Hermetic (reads only local evidence files)
- Simple search/filter UX friendly to orchestrators
"""

from __future__ import annotations

import html
import json
from datetime import datetime, UTC
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]

EVIDENCE_DIR = REPO / "evidence"
OUT_PATH = REPO / "docs" / "atlas" / "browser" / "guard_receipts.html"


def discover_receipts() -> list[dict]:
    """Discover guard receipt JSON files in evidence/ directory."""
    receipts: list[dict] = []

    if not EVIDENCE_DIR.exists():
        return receipts

    for path in sorted(EVIDENCE_DIR.glob("guard_*.json")):
        try:
            data = json.loads(path.read_text())
        except Exception:
            # Non-fatal: still list the file
            data = {}

        receipts.append(
            {
                "filename": str(path.relative_to(REPO)),
                "basename": path.name,
                "ok": bool(data.get("ok", True)) if isinstance(data, dict) else True,
                "meta": data.get("meta", {}) if isinstance(data, dict) else {},
            }
        )

    return receipts


def render_html(receipts: list[dict]) -> str:
    """Render HTML index page for guard receipts."""
    now = datetime.now(UTC).isoformat()
    rows = []

    for r in receipts:
        status = "ok" if r["ok"] else "fail"
        status_class = "status-ok" if r["ok"] else "status-fail"
        meta = r.get("meta") or {}
        guard_name = meta.get("guard", "") or r["basename"]
        ts = meta.get("generated_at", "")

        rows.append(
            f"<tr data-status='{html.escape(status)}'>"
            f"<td class='guard-name'>{html.escape(guard_name)}</td>"
            f"<td class='filename'>{html.escape(r['filename'])}</td>"
            f"<td class='{status_class}'>{html.escape(status)}</td>"
            f"<td class='timestamp'>{html.escape(ts)}</td>"
            "</tr>"
        )

    rows_html = "\n".join(rows) or (
        "<tr><td colspan='4'><em>No guard receipts discovered in evidence/ yet.</em></td></tr>"
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Guard Receipts Index — E91</title>
  <style>
    body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif; margin: 1.5rem; max-width: 1400px; }}
    h1 {{ margin-bottom: 0.25rem; }}
    .subtitle {{ color: #555; margin-bottom: 1rem; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; font-size: 0.9rem; }}
    th, td {{ border-bottom: 1px solid #ddd; padding: 0.4rem 0.6rem; text-align: left; }}
    th {{ background: #fafafa; font-weight: 600; }}
    tr:hover {{ background: #f5f5ff; }}
    .filters {{ display: flex; gap: 0.75rem; margin-top: 0.5rem; flex-wrap: wrap; }}
    .filters input, .filters select {{
      padding: 0.25rem 0.4rem;
      font-size: 0.9rem;
    }}
    .status-ok {{ color: #0a7b33; font-weight: 600; }}
    .status-fail {{ color: #b00020; font-weight: 600; }}
    .badge {{ display: inline-block; background: #eef; border: 1px solid #ccd; border-radius: 4px; padding: 2px 8px; font-size: 0.85rem; margin-left: 0.5em; }}
    .backlinks {{ background: #f5f5f5; padding: 1em; border-radius: 8px; margin: 1em 0; }}
    .backlinks ul {{ list-style: none; padding: 0; }}
    .backlinks li {{ margin: 0.5em 0; }}
    .backlinks a {{ color: #0066cc; text-decoration: none; }}
    .backlinks a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <h1>Guard Receipts Index <span class="badge">E91</span></h1>
  <div class="subtitle">
    PLAN-079 E91 · Generated at <code>{html.escape(now)}</code> · Files from <code>evidence/guard_*.json</code>
  </div>

  <div class="filters">
    <input id="search" type="text" placeholder="Search guard name or filename…" />
    <select id="statusFilter">
      <option value="">All statuses</option>
      <option value="ok">OK only</option>
      <option value="fail">Failures only</option>
    </select>
  </div>

  <table id="receiptsTable">
    <thead>
      <tr>
        <th>Guard</th>
        <th>Receipt File</th>
        <th>Status</th>
        <th>Timestamp</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>

  <div class="backlinks">
    <h2>Related Dashboards</h2>
    <ul>
      <li><a href="../dashboard/compliance_summary.html" data-testid="backlink-compliance-summary">Compliance Summary Dashboard (E86)</a></li>
      <li><a href="../dashboard/compliance_timeseries.html" data-testid="backlink-compliance-timeseries">Compliance Time-Series Dashboard (E87)</a></li>
      <li><a href="violations.html" data-testid="backlink-violations-browser">Violations Browser (E89)</a></li>
      <li><a href="../../../evidence" data-testid="backlink-evidence-dir">Evidence Directory</a></li>
    </ul>
  </div>

  <script>
    const searchInput = document.getElementById("search");
    const statusFilter = document.getElementById("statusFilter");
    const rows = Array.from(document.querySelectorAll("#receiptsTable tbody tr"));

    function applyFilters() {{
      const q = searchInput.value.toLowerCase();
      const status = statusFilter.value;
      rows.forEach(row => {{
        const text = row.innerText.toLowerCase();
        const rowStatus = row.getAttribute("data-status") || "";
        const matchesText = !q || text.includes(q);
        const matchesStatus = !status || rowStatus === status;
        row.style.display = (matchesText && matchesStatus) ? "" : "none";
      }});
    }}

    searchInput.addEventListener("input", applyFilters);
    statusFilter.addEventListener("change", applyFilters);
  </script>
</body>
</html>
"""


def main() -> int:
    """Generate guard receipts index HTML."""
    receipts = discover_receipts()
    html_content = render_html(receipts)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(html_content, encoding="utf-8")
    print(f"[generate_guard_receipts_index] Generated {OUT_PATH} with {len(receipts)} receipts")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
