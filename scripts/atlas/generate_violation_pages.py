#!/usr/bin/env python3
"""
Generate violation drilldown pages for E88.

For each violation code found in compliance exports, generates an HTML page
at docs/atlas/webproof/violations/<violation_id>.html with links to:
- Node page
- Pattern page
- Guard receipt
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import quote

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

OUTPUT_DIR = REPO / "docs" / "atlas" / "webproof" / "violations"
CONTROL_PLANE_DIR = REPO / "share" / "atlas" / "control_plane"


def load_json_file(filepath: Path) -> dict | None:
    """Load JSON file, return None if missing or invalid."""
    if not filepath.exists():
        return None
    try:
        with filepath.open() as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def extract_violation_codes() -> set[str]:
    """Extract all unique violation codes from compliance exports."""
    codes: set[str] = set()

    # Load compliance exports
    violations_7d = load_json_file(CONTROL_PLANE_DIR / "top_violations_7d.json")
    violations_30d = load_json_file(CONTROL_PLANE_DIR / "top_violations_30d.json")
    compliance_summary = load_json_file(CONTROL_PLANE_DIR / "compliance_summary.json")

    # Extract from 7d violations
    if violations_7d and violations_7d.get("violations"):
        violations = violations_7d["violations"]
        if isinstance(violations, list):
            for item in violations:
                if isinstance(item, dict) and "violation_code" in item:
                    codes.add(item["violation_code"])
        elif isinstance(violations, dict):
            codes.update(violations.keys())

    # Extract from 30d violations
    if violations_30d and violations_30d.get("violations"):
        violations = violations_30d["violations"]
        if isinstance(violations, list):
            for item in violations:
                if isinstance(item, dict) and "violation_code" in item:
                    codes.add(item["violation_code"])
        elif isinstance(violations, dict):
            codes.update(violations.keys())

    # Extract from compliance summary top_offenders
    if compliance_summary and compliance_summary.get("metrics"):
        top_offenders = compliance_summary["metrics"].get("top_offenders", [])
        for offender in top_offenders:
            if isinstance(offender, dict) and "code" in offender:
                codes.add(offender["code"])

    return codes


def get_violation_counts(code: str) -> dict[str, int]:
    """Get violation counts for a code across windows."""
    counts = {"7d": 0, "30d": 0}

    violations_7d = load_json_file(CONTROL_PLANE_DIR / "top_violations_7d.json")
    violations_30d = load_json_file(CONTROL_PLANE_DIR / "top_violations_30d.json")

    # Count from 7d
    if violations_7d and violations_7d.get("violations"):
        violations = violations_7d["violations"]
        if isinstance(violations, list):
            for item in violations:
                if isinstance(item, dict) and item.get("violation_code") == code:
                    counts["7d"] = item.get("count", 0)
        elif isinstance(violations, dict) and code in violations:
            counts["7d"] = violations[code]

    # Count from 30d
    if violations_30d and violations_30d.get("violations"):
        violations = violations_30d["violations"]
        if isinstance(violations, list):
            for item in violations:
                if isinstance(item, dict) and item.get("violation_code") == code:
                    counts["30d"] = item.get("count", 0)
        elif isinstance(violations, dict) and code in violations:
            counts["30d"] = violations[code]

    return counts


def generate_violation_page(violation_code: str) -> str:
    """Generate HTML page for a violation code."""
    counts = get_violation_counts(violation_code)
    encoded_code = quote(violation_code, safe="")

    # Extract tool from code (e.g., "guard.dsn.centralized" -> "dsn")
    tool = "unknown"
    if "." in violation_code:
        parts = violation_code.split(".")
        if len(parts) >= 2:
            tool = parts[1]

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Violation: {violation_code} — E88</title>
<style>
body {{ font-family: system-ui, -apple-system, sans-serif; max-width: 1200px; margin: 2em auto; padding: 0 1em; line-height: 1.6; }}
h1 {{ color: #1a1a1a; border-bottom: 2px solid #ddd; padding-bottom: 0.5em; }}
h2 {{ color: #333; margin-top: 1.5em; }}
.tile {{ border: 1px solid #ddd; border-radius: 8px; padding: 1em; margin: 1em 0; background: #f9f9f9; }}
.metric {{ display: inline-block; margin: 0.5em 1em 0.5em 0; padding: 0.5em 1em; background: white; border-radius: 4px; border: 1px solid #ccc; }}
.metric-value {{ font-size: 1.5em; font-weight: bold; color: #0066cc; }}
.metric-label {{ font-size: 0.9em; color: #666; }}
.backlinks {{ background: #f5f5f5; padding: 1em; border-radius: 8px; margin: 1em 0; }}
.backlinks ul {{ list-style: none; padding: 0; }}
.backlinks li {{ margin: 0.5em 0; }}
.backlinks a {{ color: #0066cc; text-decoration: none; }}
.backlinks a:hover {{ text-decoration: underline; }}
.badge {{ display: inline-block; background: #eef; border: 1px solid #ccd; border-radius: 4px; padding: 2px 8px; font-size: 0.85rem; margin-left: 0.5em; }}
</style>
</head>
<body>
<h1>Violation: {violation_code} <span class="badge">E88</span></h1>
<p><a href="../../index.html">← Back to Atlas</a></p>

<div class="tile">
<h2>Violation Details</h2>
<p><strong>Code:</strong> <code>{violation_code}</code></p>
<p><strong>Tool:</strong> <code>{tool}</code></p>
<div class="metric">
  <span class="metric-value">{counts["7d"]}</span><br>
  <span class="metric-label">7d</span>
</div>
<div class="metric">
  <span class="metric-value">{counts["30d"]}</span><br>
  <span class="metric-label">30d</span>
</div>
</div>

<div class="backlinks">
<h2>Related Links</h2>
<ul>
  <li><a href="../../nodes/{encoded_code}.html" data-testid="backlink-node-page">Node Page: {violation_code}</a></li>
  <li><a href="../../patterns/{encoded_code}.html" data-testid="backlink-pattern-page">Pattern Page: {violation_code}</a></li>
  <li><a href="../../../evidence/guard_receipts/{encoded_code}.json" data-testid="backlink-guard-receipt">Guard Receipt: {violation_code}</a></li>
  <li><a href="../../dashboard/compliance_summary.html" data-testid="backlink-compliance-summary">Compliance Summary Dashboard</a></li>
  <li><a href="../../dashboard/compliance_timeseries.html" data-testid="backlink-compliance-timeseries">Compliance Time-Series Dashboard</a></li>
</ul>
</div>

<hr>
<small>Generated at <span id="generated-at"></span></small>
<script>
  document.getElementById('generated-at').textContent = new Date().toISOString();
</script>
</body>
</html>"""

    return html


def main() -> int:
    """Generate violation drilldown pages."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        codes = extract_violation_codes()

        if not codes:
            print("[generate_violation_pages] No violation codes found in exports", file=sys.stderr)
            # Create a placeholder page to satisfy guard
            placeholder_code = "guard.placeholder"
            output_path = OUTPUT_DIR / f"{quote(placeholder_code, safe='')}.html"
            with output_path.open("w") as f:
                f.write(generate_violation_page(placeholder_code))
            print(f"[generate_violation_pages] Created placeholder page: {output_path}")
            return 0

        generated = 0
        for code in codes:
            encoded_code = quote(code, safe="")
            output_path = OUTPUT_DIR / f"{encoded_code}.html"
            html = generate_violation_page(code)
            with output_path.open("w") as f:
                f.write(html)
            generated += 1

        print(f"[generate_violation_pages] Generated {generated} violation pages in {OUTPUT_DIR}")
        return 0
    except Exception as e:
        print(f"ERROR: Failed to generate violation pages: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
