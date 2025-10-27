#!/usr/bin/env python3
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
BADGES = EVAL / "badges"
REPORT_JSON = EVAL / "report.json"


def _badge(label: str, value: str, color: str) -> str:
    text = f"{label}: {value}"
    w = 90 + 8 * max(0, len(text) - 8)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="20" role="img" aria-label="{text}">
  <linearGradient id="a" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient>
  <rect rx="3" width="{w}" height="20" fill="#555"/>
  <rect rx="3" x="55" width="{w - 55}" height="20" fill="{color}"/>
  <path fill="{color}" d="M55 0h4v20h-4z"/>
  <rect rx="3" width="{w}" height="20" fill="url(#a)"/>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="28" y="14">{label}</text>
    <text x="{(55 + (w - 55) / 2):.0f}" y="14">{value}</text>
  </g>
</svg>"""


def main() -> int:
    print("[eval.badges] starting")
    BADGES.mkdir(parents=True, exist_ok=True)
    ok = 0
    fail = 0
    if REPORT_JSON.exists():
        doc = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        s = doc.get("summary", {})
        ok = int(s.get("ok_count", 0))
        fail = int(s.get("fail_count", 0))
    status = "OK" if fail == 0 else "FAIL"
    color = "#4c1" if fail == 0 else "#e05d44"
    (BADGES / "report_status.svg").write_text(
        _badge("report", status, color), encoding="utf-8"
    )
    (BADGES / "strict_gate.svg").write_text(
        _badge("strict", status, color), encoding="utf-8"
    )
    print(f"[eval.badges] wrote {BADGES.relative_to(ROOT)}/report_status.svg")
    print(f"[eval.badges] wrote {BADGES.relative_to(ROOT)}/strict_gate.svg")
    print("[eval.badges] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
