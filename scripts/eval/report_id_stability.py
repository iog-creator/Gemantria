#!/usr/bin/env python3
import glob
import json
import pathlib
import re
import sys
import time
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUTDIR = ROOT / "share" / "eval"
JSON_OUT = OUTDIR / "id_stability.json"
MD_OUT = OUTDIR / "id_stability.md"

EXPORT_DIR = ROOT / "exports"
LATEST = EXPORT_DIR / "graph_latest.json"
THRESHOLDS = ROOT / "eval" / "thresholds.yml"


def _load_json(p: pathlib.Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def _read_yaml(path: pathlib.Path):
    import yaml  # dev-only dep

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _parse_ts(name: str) -> int:
    base = pathlib.Path(name).name
    m = re.search(r"graph_(\d{8})(\d{6})?", base)
    if m:
        d = m.group(1)
        t = m.group(2) or "000000"
        return int(d + t)
    m2 = re.search(r"graph_(\d{4}-\d{2}-\d{2})[T_]?(\d{2}-\d{2}-\d{2})?", base)
    if m2:
        d = m2.group(1).replace("-", "")
        t = (m2.group(2) or "00-00-00").replace("-", "")
        return int(d + t)
    return 0


def _node_id_set(doc: Any) -> set[Any]:
    ids = set()
    nodes = doc.get("nodes", [])
    if isinstance(nodes, list):
        for n in nodes:
            if isinstance(n, dict) and "id" in n:
                ids.add(n.get("id"))
    return ids


def main() -> int:
    print("[eval.idstability] starting")
    OUTDIR.mkdir(parents=True, exist_ok=True)

    if not LATEST.exists():
        print("[eval.idstability] FAIL no exports/graph_latest.json")
        return 2

    prev_cands = [p for p in glob.glob(str(EXPORT_DIR / "graph_*.json")) if pathlib.Path(p).name != "graph_latest.json"]
    if not prev_cands:
        JSON_OUT.write_text(json.dumps({"summary": {"has_previous": False}}, indent=2), encoding="utf-8")
        MD_OUT.write_text(
            "# Gemantria ID Stability\n\n_No previous export found._\n",
            encoding="utf-8",
        )
        print(f"[eval.idstability] wrote {JSON_OUT.relative_to(ROOT)}")
        print(f"[eval.idstability] wrote {MD_OUT.relative_to(ROOT)}")
        print("[eval.idstability] OK")
        return 0

    prev_path = pathlib.Path(sorted(prev_cands, key=_parse_ts)[-1])

    cur = _load_json(LATEST)
    prev = _load_json(prev_path)

    cur_ids = _node_id_set(cur)
    prev_ids = _node_id_set(prev)

    inter = len(cur_ids & prev_ids)
    union = len(cur_ids | prev_ids)
    jaccard = (inter / union) if union else 1.0

    added = sorted(list(cur_ids - prev_ids))
    removed = sorted(list(prev_ids - cur_ids))

    # thresholds
    th = _read_yaml(THRESHOLDS)
    j_min = float(th.get("id_stability", {}).get("min_node_id_jaccard", 0.95))
    allow_add = int(th.get("id_stability", {}).get("allow_added_node_ids", 0))
    allow_rem = int(th.get("id_stability", {}).get("allow_removed_node_ids", 0))

    ok = (jaccard >= j_min) and (len(added) <= allow_add) and (len(removed) <= allow_rem)

    report = {
        "ts_unix": int(time.time()),
        "summary": {
            "has_previous": True,
            "ok": ok,
            "jaccard": round(jaccard, 6),
            "added_ids": len(added),
            "removed_ids": len(removed),
            "thresholds": {
                "min_jaccard": j_min,
                "allow_added": allow_add,
                "allow_removed": allow_rem,
            },
        },
        "previous_file": str(prev_path.relative_to(ROOT)),
        "current_file": str(LATEST.relative_to(ROOT)),
        "added_ids": added[:50],  # cap to keep md readable
        "removed_ids": removed[:50],
    }
    JSON_OUT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    lines = []
    lines.append("# Gemantria ID Stability")
    lines.append("")
    lines.append(f"*previous:* `{report['previous_file']}`")
    lines.append(f"*current:*  `{report['current_file']}`")
    lines.append("")
    badge = "✅" if ok else "❌"
    lines.append(
        f"*jaccard:* {report['summary']['jaccard']}  •  *added:* {report['summary']['added_ids']}  •  *removed:* {report['summary']['removed_ids']}  •  *ok:* {badge}"
    )
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(report["summary"], indent=2, sort_keys=True))
    lines.append("```")
    lines.append("")
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"[eval.idstability] wrote {JSON_OUT.relative_to(ROOT)}")
    print(f"[eval.idstability] wrote {MD_OUT.relative_to(ROOT)}")
    print("[eval.idstability] OK" if ok else "[eval.idstability] DONE_WITH_FAILS")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
