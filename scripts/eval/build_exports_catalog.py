# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import glob
import json
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
# Never write to share/** in CI. Use artifacts-first contract.
CI = os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true"
OUT = (
    ROOT / "_artifacts" / "eval" / "exports_catalog.md"
    if CI
    else ROOT / "share" / "eval" / "exports_catalog.md"
)


def _load_json(p: pathlib.Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _summ(p: pathlib.Path) -> tuple[int, int]:
    try:
        doc = _load_json(p)
        nodes = doc.get("nodes", [])
        edges = doc.get("edges", [])
        return len(nodes) if isinstance(nodes, list) else 0, (
            len(edges) if isinstance(edges, list) else 0
        )
    except Exception:
        return 0, 0


def main() -> int:
    print("[eval.catalog] starting")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(glob.glob(str(ROOT / "exports" / "graph_*.json")))
    lines = ["# Gemantria Exports Catalog", ""]
    if not files:
        lines.append("_No exports found._")
    else:
        lines.append("| file | size (KB) | nodes | edges |")
        lines.append("|---|---:|---:|---:|")
        for f in files:
            p = pathlib.Path(f)
            kb = round(p.stat().st_size / 1024, 1)
            n, e = _summ(p)
            lines.append(f"| exports/{p.name} | {kb} | {n} | {e} |")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[eval.catalog] wrote {OUT.relative_to(ROOT)}")
    print("[eval.catalog] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
