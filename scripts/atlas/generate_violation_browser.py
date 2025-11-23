#!/usr/bin/env python3
"""
Generate violations browser HTML for E89.

Reads compliance exports and generates a searchable/filterable/sortable
violations browser at docs/atlas/browser/violations.html.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, UTC
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

OUTPUT_FILE = REPO / "docs" / "atlas" / "browser" / "violations.html"
CONTROL_PLANE_DIR = REPO / "share" / "atlas" / "control_plane"

# Violation code descriptions
VIOLATION_DESCRIPTIONS = {
    "MISSING_POR": "Missing Proof of Record (POR) - Required documentation or evidence is missing",
    "ARG_SCHEMA_INVALID": "Argument Schema Invalid - Tool arguments do not match expected schema",
    "RING_VIOLATION": "Ring Violation - Tool call violates security ring constraints",
    "PROVENANCE_MISMATCH": "Provenance Mismatch - Document provenance does not match expected source",
    "FORBIDDEN_TOOL": "Forbidden Tool - Tool is not allowed in current context",
    "BUDGET_EXCEEDED": "Budget Exceeded - Resource budget limit exceeded",
    "RETRY_EXHAUSTED": "Retry Exhausted - Maximum retry attempts reached",
}


def load_json_file(filepath: Path) -> dict | None:
    """Load JSON file, return None if missing or invalid."""
    if not filepath.exists():
        return None
    try:
        with filepath.open() as f:
            return json.load(f)
    except Exception:
        return None


def get_violation_data() -> dict:
    """Load violation data from compliance exports."""
    violations_7d = load_json_file(CONTROL_PLANE_DIR / "top_violations_7d.json")
    violations_30d = load_json_file(CONTROL_PLANE_DIR / "top_violations_30d.json")
    summary = load_json_file(CONTROL_PLANE_DIR / "compliance_summary.json")

    # Extract violations from exports
    violations_list = []
    codes_seen = set()

    # Add 7d violations
    if violations_7d and violations_7d.get("violations"):
        for v in violations_7d["violations"]:
            code = v.get("violation_code", "")
            if code and code not in codes_seen:
                codes_seen.add(code)
                violations_list.append(
                    {
                        "code": code,
                        "count_7d": v.get("count", 0),
                        "count_30d": 0,
                        "count_total": 0,
                    }
                )

    # Add/update 30d violations
    if violations_30d and violations_30d.get("violations"):
        for v in violations_30d["violations"]:
            code = v.get("violation_code", "")
            count = v.get("count", 0)
            # Find existing or create new
            found = False
            for item in violations_list:
                if item["code"] == code:
                    item["count_30d"] = count
                    found = True
                    break
            if not found:
                violations_list.append(
                    {
                        "code": code,
                        "count_7d": 0,
                        "count_30d": count,
                        "count_total": 0,
                    }
                )

    # Get total counts from summary if available
    if summary and summary.get("metrics", {}).get("violations_by_code"):
        by_code = summary["metrics"]["violations_by_code"]
        for item in violations_list:
            code = item["code"]
            if code in by_code:
                item["count_total"] = by_code[code].get("total", 0)

    # Sort by total count descending
    violations_list.sort(key=lambda x: x["count_total"], reverse=True)

    return {
        "violations": violations_list,
        "generated_at": datetime.now(UTC).isoformat(),
    }


def generate_html(violation_data: dict) -> str:
    """Generate violations browser HTML."""
    violations = violation_data["violations"]
    generated_at = violation_data["generated_at"]

    # Build violations table rows
    rows_html = ""
    for v in violations:
        code = v["code"]
        safe_code = code.lower().replace("_", "-")
        description = VIOLATION_DESCRIPTIONS.get(code, "Unknown violation code")
        count_7d = v["count_7d"]
        count_30d = v["count_30d"]
        count_total = v["count_total"]

        rows_html += f"""
      <tr data-code="{code}" data-count-total="{count_total}">
        <td><a href="../webproof/violations/{safe_code}.html">{code}</a></td>
        <td>{description}</td>
        <td class="count">{count_7d}</td>
        <td class="count">{count_30d}</td>
        <td class="count">{count_total}</td>
        <td>
          <a href="../webproof/violations/{safe_code}.html">Drilldown</a> |
          <a href="../../share/atlas/control_plane/top_violations_7d.json">JSON</a>
        </td>
      </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Violations Browser — E89</title>
  <style>
    body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif; margin: 1.5rem; max-width: 1400px; }}
    h1 {{ margin-bottom: 0.25rem; }}
    .subtitle {{ color: #555; margin-bottom: 1rem; }}
    .badge {{ display: inline-block; background: #eef; border: 1px solid #ccd; border-radius: 4px; padding: 2px 8px; font-size: 0.85rem; margin-left: 0.5em; }}
    .filters {{ display: flex; gap: 0.75rem; margin: 1rem 0; flex-wrap: wrap; align-items: center; }}
    .filters input, .filters select {{
      padding: 0.4rem 0.6rem;
      font-size: 0.9rem;
      border: 1px solid #ccc;
      border-radius: 4px;
    }}
    .filters input[type="text"] {{
      flex: 1;
      min-width: 200px;
    }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; font-size: 0.9rem; }}
    th, td {{ border-bottom: 1px solid #ddd; padding: 0.6rem 0.8rem; text-align: left; }}
    th {{ background: #fafafa; font-weight: 600; cursor: pointer; user-select: none; }}
    th:hover {{ background: #f0f0f0; }}
    th.sort-asc::after {{ content: " ▲"; font-size: 0.7em; }}
    th.sort-desc::after {{ content: " ▼"; font-size: 0.7em; }}
    tr:hover {{ background: #f5f5ff; }}
    .count {{ text-align: right; font-variant-numeric: tabular-nums; }}
    .backlinks {{ background: #f5f5f5; padding: 1em; border-radius: 8px; margin: 1em 0; }}
    .backlinks ul {{ list-style: none; padding: 0; }}
    .backlinks li {{ margin: 0.5em 0; }}
    .backlinks a {{ color: #0066cc; text-decoration: none; }}
    .backlinks a:hover {{ text-decoration: underline; }}
    .no-results {{ padding: 2rem; text-align: center; color: #666; }}
  </style>
</head>
<body>
  <h1>Violations Browser <span class="badge">E89</span></h1>
  <div class="subtitle">
    PLAN-078 E89 · Unified Violation Browser · Generated at <code>{generated_at}</code>
  </div>

  <div class="filters">
    <input id="search" type="text" placeholder="Search violation code or description…" />
    <select id="codeFilter">
      <option value="">All codes</option>
{chr(10).join(f'      <option value="{v["code"]}">{v["code"]}</option>' for v in violations)}
    </select>
    <select id="sortBy">
      <option value="code">Sort by Code</option>
      <option value="count-total" selected>Sort by Total Count</option>
      <option value="count-7d">Sort by 7d Count</option>
      <option value="count-30d">Sort by 30d Count</option>
    </select>
    <select id="sortOrder">
      <option value="desc" selected>Descending</option>
      <option value="asc">Ascending</option>
    </select>
  </div>

  <table id="violationsTable">
    <thead>
      <tr>
        <th data-sort="code">Violation Code</th>
        <th data-sort="description">Description</th>
        <th data-sort="count-7d" class="sort-desc">7d Count</th>
        <th data-sort="count-30d">30d Count</th>
        <th data-sort="count-total">Total Count</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
{rows_html if rows_html else '      <tr><td colspan="6" class="no-results">No violations found</td></tr>'}
    </tbody>
  </table>

  <div class="backlinks">
    <h2>Related Dashboards & Exports</h2>
    <ul>
      <li><a href="../dashboard/compliance_summary.html" data-testid="backlink-compliance-summary">Compliance Summary Dashboard (E86)</a></li>
      <li><a href="../dashboard/compliance_timeseries.html" data-testid="backlink-compliance-timeseries">Compliance Time-Series Dashboard (E87)</a></li>
      <li><a href="guard_receipts.html" data-testid="backlink-guard-receipts">Guard Receipts Index (E91)</a></li>
      <li><a href="../../share/atlas/control_plane/compliance_summary.json" data-testid="backlink-json-summary">Compliance Summary JSON</a></li>
      <li><a href="../../share/atlas/control_plane/top_violations_7d.json" data-testid="backlink-json-7d">Top Violations 7d JSON</a></li>
      <li><a href="../../share/atlas/control_plane/top_violations_30d.json" data-testid="backlink-json-30d">Top Violations 30d JSON</a></li>
      <li><a href="../../share/atlas/control_plane/graph_compliance.json" data-testid="backlink-json-graph-compliance">Graph Compliance Metrics JSON (E90)</a></li>
      <li><a href="../../../evidence" data-testid="backlink-evidence-dir">Evidence Directory</a></li>
    </ul>
  </div>

  <script>
    const searchInput = document.getElementById("search");
    const codeFilter = document.getElementById("codeFilter");
    const sortBy = document.getElementById("sortBy");
    const sortOrder = document.getElementById("sortOrder");
    const table = document.getElementById("violationsTable");
    const rows = Array.from(table.querySelectorAll("tbody tr"));
    const headers = Array.from(table.querySelectorAll("thead th"));

    let currentSort = {{ column: "count-total", order: "desc" }};

    function applyFilters() {{
      const q = searchInput.value.toLowerCase();
      const code = codeFilter.value;
      
      rows.forEach(row => {{
        const text = row.innerText.toLowerCase();
        const rowCode = row.getAttribute("data-code") || "";
        const matchesText = !q || text.includes(q);
        const matchesCode = !code || rowCode === code;
        row.style.display = (matchesText && matchesCode) ? "" : "none";
      }});
    }}

    function sortTable() {{
      const column = sortBy.value;
      const order = sortOrder.value;
      currentSort = {{ column, order }};

      // Update header indicators
      headers.forEach(th => {{
        th.classList.remove("sort-asc", "sort-desc");
        if (th.getAttribute("data-sort") === column) {{
          th.classList.add(order === "asc" ? "sort-asc" : "sort-desc");
        }}
      }});

      // Sort rows
      const visibleRows = rows.filter(r => r.style.display !== "none");
      const tbody = table.querySelector("tbody");
      
      visibleRows.sort((a, b) => {{
        let aVal, bVal;
        
        if (column === "code") {{
          aVal = a.getAttribute("data-code") || "";
          bVal = b.getAttribute("data-code") || "";
        }} else if (column === "count-total") {{
          aVal = parseInt(a.getAttribute("data-count-total") || "0");
          bVal = parseInt(b.getAttribute("data-count-total") || "0");
        }} else if (column === "count-7d") {{
          const aCell = a.cells[2];
          const bCell = b.cells[2];
          aVal = parseInt(aCell?.textContent || "0");
          bVal = parseInt(bCell?.textContent || "0");
        }} else if (column === "count-30d") {{
          const aCell = a.cells[3];
          const bCell = b.cells[3];
          aVal = parseInt(aCell?.textContent || "0");
          bVal = parseInt(bCell?.textContent || "0");
        }} else {{
          aVal = a.cells[1]?.textContent || "";
          bVal = b.cells[1]?.textContent || "";
        }}

        if (typeof aVal === "string") {{
          return order === "asc" ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
        }} else {{
          return order === "asc" ? aVal - bVal : bVal - aVal;
        }}
      }});

      // Re-append sorted rows
      visibleRows.forEach(row => tbody.appendChild(row));
    }}

    // Header click sorting
    headers.forEach(th => {{
      if (th.getAttribute("data-sort")) {{
        th.addEventListener("click", () => {{
          const col = th.getAttribute("data-sort");
          if (currentSort.column === col) {{
            sortOrder.value = currentSort.order === "asc" ? "desc" : "asc";
          }} else {{
            sortBy.value = col;
            sortOrder.value = "desc";
          }}
          sortTable();
        }});
      }}
    }});

    searchInput.addEventListener("input", applyFilters);
    codeFilter.addEventListener("change", applyFilters);
    sortBy.addEventListener("change", sortTable);
    sortOrder.addEventListener("change", sortTable);

    // Initial sort
    sortTable();
  </script>
</body>
</html>"""

    return html


def main() -> int:
    """Generate violations browser HTML."""
    try:
        violation_data = get_violation_data()
        html = generate_html(violation_data)

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(html)

        print(f"[generate_violation_browser] Generated: {OUTPUT_FILE}")
        print(f"[generate_violation_browser] Violations: {len(violation_data['violations'])}")
        return 0
    except Exception as e:
        print(f"[generate_violation_browser] ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
