#!/usr/bin/env python3
import glob
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "share" / "eval" / "exports_catalog.md"


def _load_json(p: pathlib.Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _summ(p: pathlib.Path):
    try:
        doc = _load_json(p)
        nodes = doc.get("nodes", [])
        edges = doc.get("edges", [])
        return len(nodes) if isinstance(nodes, list) else 0, (
            len(edges) if isinstance(edges, list) else 0
        )
    except Exception:
        return 0, 0


def main():
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
