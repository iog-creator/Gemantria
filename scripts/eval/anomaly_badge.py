#!/usr/bin/env python3
"""
Anomaly Badge Generator - Create SVG badge showing edge anomaly count.

This script reads the edge audit results and generates a visual badge
showing the number of anomalous edges detected in the semantic network.
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
BADGES = EVAL / "badges"
BADGES.mkdir(parents=True, exist_ok=True)
AUDIT_FILE = EVAL / "edge_audit.json"
OUT = BADGES / "anomaly.svg"


def emit_hint(msg: str) -> None:
    """Emit a standardized hint for CI visibility."""
    print(f"HINT: {msg}")


def badge(count: int) -> str:
    """
    Generate SVG badge showing anomaly count.

    Args:
        count: Number of anomalous edges detected

    Returns:
        SVG string for the badge
    """
    # Color coding: green for 0, yellow for 1-5, red for 6+
    if count == 0:
        color = "#4c1"  # green
    elif count <= 5:
        color = "#dfb317"  # yellow/amber
    else:
        color = "#e05d44"  # red

    text = f"{count}"
    width = 120  # Adjust width based on text length
    if len(text) > 3:
        width = 135

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20"
     role="img" aria-label="anomalies:{count}">
  <linearGradient id="g" x2="0" stop-color="#bbb" stop-opacity=".1"/>
  <stop offset="1" stop-opacity=".1"/>
  <rect rx="3" width="{width}" height="20" fill="#555"/>
  <rect rx="3" x="55" width="{width - 55}" height="20" fill="{color}"/>
  <path fill="{color}" d="M55 0h4v20h-4z"/>
  <rect rx="3" width="{width}" height="20" fill="url(#g)"/>
  <g fill="#fff" text-anchor="start"
     font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="6" y="14">anomalies</text>
    <text x="61" y="14">{text}</text>
  </g>
</svg>"""


def main() -> int:
    """Generate anomaly badge from audit results."""
    emit_hint("eval: writing anomaly badge")

    if not AUDIT_FILE.exists():
        print("[anomaly_badge] missing edge_audit.json - run edge_audit first")
        # Generate badge with 0 anomalies as fallback
        OUT.write_text(badge(0), encoding="utf-8")
        print(f"[anomaly_badge] wrote fallback {OUT.relative_to(ROOT)} (0 anomalies)")
        return 0

    try:
        audit_data = json.loads(AUDIT_FILE.read_text(encoding="utf-8"))
        anomaly_count = audit_data.get("summary", {}).get("total_anomalous", 0)

        OUT.write_text(badge(anomaly_count), encoding="utf-8")
        print(f"[anomaly_badge] wrote {OUT.relative_to(ROOT)} ({anomaly_count} anomalies)")

    except (json.JSONDecodeError, KeyError) as e:
        print(f"[anomaly_badge] error reading audit file: {e}")
        # Generate badge with error indicator
        error_badge = badge(999)  # Use 999 as error indicator
        OUT.write_text(error_badge, encoding="utf-8")
        print(f"[anomaly_badge] wrote error {OUT.relative_to(ROOT)} (999 = error)")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
