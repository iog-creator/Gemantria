#!/usr/bin/env python3

import json, sys
from pathlib import Path


def main():
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("exports/ai_nouns.json")
    data = json.loads(p.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    total, missing_insight, lost_conf = 0, 0, 0

    for n in nodes:
        enr = n.get("enrichment") or {}
        if not enr:
            continue
        total += 1
        if not isinstance(enr.get("insight"), str) or not enr.get("insight").strip():
            missing_insight += 1
        raw = enr.get("_raw")
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict) and "confidence" in parsed and "confidence" not in enr:
                    lost_conf += 1
            except Exception:
                pass
    if missing_insight or lost_conf:
        print(
            f"ERROR: enrichment regressions: missing_insight={missing_insight}, lost_confidence={lost_conf} (over {total} enriched)",
            file=sys.stderr,
        )
        sys.exit(2)
    print(f"OK: enrichment details preserved on {total} nodes.")


if __name__ == "__main__":
    main()
