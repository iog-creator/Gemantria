#!/usr/bin/env python3
"""
Generate violation drilldown pages for E88.

For each violation code in compliance exports, generates an HTML page at:
docs/atlas/webproof/violations/<violation_code>.html

Each page includes:
- Violation code details
- Links to Node pages (if applicable)
- Links to Pattern pages (if applicable)
- Links to Guard receipt pages
- Links back to compliance dashboards
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

OUTPUT_DIR = REPO / "docs" / "atlas" / "webproof" / "violations"
CONTROL_PLANE_DIR = REPO / "share" / "atlas" / "control_plane"

# Violation code descriptions
VIOLATION_DESCRIPTIONS = {
    "MISSING_POR": "Missing Proof of Record (POR) - Required documentation or evidence is missing",
    "ARG_SCHEMA_INVALID": "Argument Schema Invalid - Tool arguments do not match expected schema",
    "RING_VIOLATION": "Ring Violation - Tool call violates security ring restrictions",
    "PROVENANCE_MISMATCH": "Provenance Mismatch - Source or origin verification failed",
    "FORBIDDEN_TOOL": "Forbidden Tool - Tool is not allowed in current context",
    "BUDGET_EXCEEDED": "Budget Exceeded - Resource or cost limits exceeded",
    "RETRY_EXHAUSTED": "Retry Exhausted - Maximum retry attempts reached",
}


def load_json_file(filepath: Path) -> dict | None:
    """Load JSON file, return None if missing or invalid."""
    if not filepath.exists():
        return None
    try:
        with filepath.open() as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def get_violation_codes() -> set[str]:
    """Extract all unique violation codes from compliance exports."""
    codes = set()

    # Check top_violations_7d.json
    violations_7d = load_json_file(CONTROL_PLANE_DIR / "top_violations_7d.json")
    if violations_7d and "violations" in violations_7d:
        for violation in violations_7d["violations"]:
            if "violation_code" in violation:
                codes.add(violation["violation_code"])

    # Check top_violations_30d.json
    violations_30d = load_json_file(CONTROL_PLANE_DIR / "top_violations_30d.json")
    if violations_30d and "violations" in violations_30d:
        for violation in violations_30d["violations"]:
            if "violation_code" in violation:
                codes.add(violation["violation_code"])

    # Check compliance_summary.json
    summary = load_json_file(CONTROL_PLANE_DIR / "compliance_summary.json")
    if summary and "metrics" in summary:
        by_code = summary["metrics"].get("violations_by_code", {})
        codes.update(by_code.keys())

    return codes


def get_violation_counts(code: str) -> dict[str, int]:
    """Get violation counts for a specific code from all exports."""
    counts = {"7d": 0, "30d": 0, "total": 0}

    violations_7d = load_json_file(CONTROL_PLANE_DIR / "top_violations_7d.json")
    if violations_7d and "violations" in violations_7d:
        for violation in violations_7d["violations"]:
            if violation.get("violation_code") == code:
                counts["7d"] = violation.get("count", 0)
                break

    violations_30d = load_json_file(CONTROL_PLANE_DIR / "top_violations_30d.json")
    if violations_30d and "violations" in violations_30d:
        for violation in violations_30d["violations"]:
            if violation.get("violation_code") == code:
                counts["30d"] = violation.get("count", 0)
                break

    summary = load_json_file(CONTROL_PLANE_DIR / "compliance_summary.json")
    if summary and "metrics" in summary:
        by_code = summary["metrics"].get("violations_by_code", {})
        counts["total"] = by_code.get(code, 0)

    return counts


def generate_violation_page(code: str) -> str:
    """Generate HTML page for a violation code."""
    description = VIOLATION_DESCRIPTIONS.get(code, f"Violation code: {code}")
    counts = get_violation_counts(code)

    # Generate safe filename from code
    safe_code = code.lower().replace("_", "-")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Violation: {code} — E88</title>
  <style>
    body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif; margin: 1.5rem; max-width: 1200px; }}
    h1 {{ margin-bottom: 0.25rem; }}
    .subtitle {{ color: #555; margin-bottom: 1rem; }}
    .badge {{ display: inline-block; background: #eef; border: 1px solid #ccd; border-radius: 4px; padding: 2px 8px; font-size: 0.85rem; margin-left: 0.5em; }}
    .info-box {{ background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 1em; margin: 1em 0; }}
    .counts {{ display: flex; gap: 1rem; margin: 1em 0; }}
    .count-item {{ background: white; border: 1px solid #dee2e6; border-radius: 4px; padding: 0.75rem; flex: 1; }}
    .count-value {{ font-size: 1.5rem; font-weight: bold; color: #dc3545; }}
    .count-label {{ font-size: 0.85rem; color: #6c757d; margin-top: 0.25rem; }}
    .links-section {{ margin: 1.5em 0; }}
    .links-section h2 {{ font-size: 1.1rem; margin-bottom: 0.5rem; }}
    .links-list {{ list-style: none; padding: 0; }}
    .links-list li {{ margin: 0.5rem 0; }}
    .links-list a {{ color: #0066cc; text-decoration: none; }}
    .links-list a:hover {{ text-decoration: underline; }}
    .back-link {{ margin-top: 2em; padding-top: 1em; border-top: 1px solid #dee2e6; }}
  </style>
</head>
<body>
  <h1>Violation: {code} <span class="badge">E88</span></h1>
  <div class="subtitle">
    PLAN-078 E88 · Violation Drilldown
  </div>

  <div class="info-box">
    <strong>Description:</strong> {description}
  </div>

  <div class="counts">
    <div class="count-item">
      <div class="count-value">{counts["7d"]}</div>
      <div class="count-label">Last 7 days</div>
    </div>
    <div class="count-item">
      <div class="count-value">{counts["30d"]}</div>
      <div class="count-label">Last 30 days</div>
    </div>
    <div class="count-item">
      <div class="count-value">{counts["total"]}</div>
      <div class="count-label">Total</div>
    </div>
  </div>

  <div class="links-section">
    <h2>Related Pages</h2>
    <ul class="links-list">
      <li><a href="../../dashboard/compliance_summary.html">Compliance Summary Dashboard</a></li>
      <li><a href="../../dashboard/compliance_timeseries.html">Compliance Time-Series</a></li>
      <li><a href="../../dashboard/compliance_heatmap.html">Compliance Heatmap</a></li>
      <li><a href="../../browser/violations.html">Violations Browser</a></li>
      <li><a href="../../browser/guard_receipts.html">Guard Receipts Index</a></li>
    </ul>
  </div>

  <div class="links-section">
    <h2>Node & Pattern Links</h2>
    <ul class="links-list">
      <li><a href="../../nodes/0.html">Node 0</a> (example)</li>
      <li><a href="../../nodes/1.html">Node 1</a> (example)</li>
      <li><em>Pattern links will be added when pattern pages are available</em></li>
    </ul>
  </div>

  <div class="links-section">
    <h2>Guard Receipts</h2>
    <ul class="links-list">
      <li><a href="../../browser/guard_receipts.html">View all guard receipts</a></li>
      <li><a href="../../webproof/control_compliance.html">Control Compliance Webproof</a></li>
    </ul>
  </div>

  <div class="back-link">
    <a href="../../browser/violations.html">← Back to Violations Browser</a>
  </div>
</body>
</html>
"""
    return html


def main() -> int:
    """Generate violation drilldown pages."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    codes = get_violation_codes()

    if not codes:
        print("[generate_violation_pages] No violation codes found in exports")
        # Still create at least one example page for testing
        codes = {"MISSING_POR"}

    generated = []
    for code in sorted(codes):
        safe_code = code.lower().replace("_", "-")
        output_path = OUTPUT_DIR / f"{safe_code}.html"
        html = generate_violation_page(code)
        output_path.write_text(html)
        generated.append(safe_code)
        print(f"[generate_violation_pages] Generated {output_path}")

    print(f"[generate_violation_pages] Generated {len(generated)} violation pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
