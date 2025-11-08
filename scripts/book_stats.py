# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

# scripts/book_stats.py
#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from statistics import mean

LOGS = Path("logs") / "book"


def load_meta():
    if not LOGS.exists():
        print("[stats] no logs/book/ directory found")
        return []
    metas = []
    for p in sorted(LOGS.glob("*.json")):
        if p.name.startswith("book_run."):  # skip run markers
            continue
        try:
            m = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(m, dict) and "chapter" in m:
                metas.append((p, m))
        except Exception:
            pass
    return metas


def main():
    metas = load_meta()
    if not metas:
        print("[stats] no chapter meta logs found (run a chapter first)")
        return 2

    elapsed = [m["elapsed_sec"] for _, m in metas if "elapsed_sec" in m]
    rc_ok = all(m.get("returncode", 1) == 0 for _, m in metas)
    susp = [str(m["chapter"]) for _, m in metas if m.get("suspicious_fast")]
    book = metas[0][1].get("book", "Unknown")
    N = len(metas)

    summary = {
        "book": book,
        "chapters_logged": N,
        "elapsed_total_sec": round(sum(elapsed), 2),
        "elapsed_avg_sec": round(mean(elapsed), 2) if elapsed else 0.0,
        "elapsed_min_sec": round(min(elapsed), 2) if elapsed else 0.0,
        "elapsed_max_sec": round(max(elapsed), 2) if elapsed else 0.0,
        "all_returncodes_zero": rc_ok,
        "suspicious_fast_chapters": susp,
    }
    out = LOGS / "summary.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("[stats] ---- Chapter Runtime Summary ----")
    print(json.dumps(summary, indent=2))
    if susp:
        print(f"[stats][warn] suspicious_fast chapters: {', '.join(susp)}")
    if not rc_ok:
        print("[stats][gate] non-zero return codes detected")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
