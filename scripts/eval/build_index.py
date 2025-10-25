#!/usr/bin/env python3
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
OUT = EVAL / "index.md"


def main() -> int:
    print("[eval.index] starting")
    EVAL.mkdir(parents=True, exist_ok=True)
    artifacts = [
        ("report.md", "Latest manifest report"),
        ("history.md", "Temporal history/trend"),
        ("delta.md", "Delta (latest vs previous)"),
        ("provenance.md", "Provenance"),
        ("checksums.csv", "Checksums"),
    ]
    lines = []
    lines.append("# Gemantria Eval — Artifacts Index")
    lines.append("")
    lines.append(f"*generated:* {int(time.time())}")
    lines.append("")
    for fn, label in artifacts:
        p = EVAL / fn
        exists = p.exists()
        badge = "✅" if exists else "❌"
        lines.append(f"- {badge} **{label}** — {fn if exists else '(missing)'}")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[eval.index] wrote {OUT.relative_to(ROOT)}")
    print("[eval.index] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
