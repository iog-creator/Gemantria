# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
BADGES = EVAL / "badges"
BADGES.mkdir(parents=True, exist_ok=True)
OUT = BADGES / "quality.svg"


def badge(text, ok=True):
    color = "#4c1" if ok else "#e05d44"
    w = 150
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="20" role="img" aria-label="quality:{text}">  # noqa: E501
  <linearGradient id="g" x2="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/>
  <rect rx="3" width="{w}" height="20" fill="#555"/>
  <rect rx="3" x="60" width="{w - 60}" height="20" fill="{color}"/>
  <path fill="{color}" d="M60 0h4v20h-4z"/>
  <rect rx="3" width="{w}" height="20" fill="url(#g)"/>
  <g fill="#fff" text-anchor="start" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="6" y="14">quality</text>
    <text x="66" y="14">{text}</text>
  </g>
</svg>"""


def main():
    text = (
        (EVAL / "quality_report.txt").read_text(encoding="utf-8")
        if (EVAL / "quality_report.txt").exists()
        else ""
    )
    failed = "FAIL:" in text
    OUT.write_text(badge("PASS" if not failed else "FAIL", ok=not failed), encoding="utf-8")
    print(
        f"[quality.badge] wrote {OUT.relative_to(ROOT)} status={'PASS' if not failed else 'FAIL'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
