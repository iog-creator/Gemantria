# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import json
import pathlib
import time
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
OUT = EVAL / "anomalies.md"


def _load(p: pathlib.Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def main() -> int:
    print("[eval.anomalies] starting")
    EVAL.mkdir(parents=True, exist_ok=True)
    report = _load(EVAL / "report.json") or {}
    history = _load(EVAL / "history.json") or {}
    delta = _load(EVAL / "delta.json") or {}
    idstab = _load(EVAL / "id_stability.json") or {}

    lines = []
    lines.append("# Gemantria Eval — Anomalies")
    lines.append("")
    lines.append(f"*generated:* {int(time.time())}")
    lines.append("")

    # 1) Manifest tasks: list FAIL tasks (if any)
    fail = []
    for r in report.get("results") or []:
        if r.get("status") != "OK":
            fail.append(r.get("key"))
    if fail:
        lines.append("## ❌ Manifest Task Failures")
        for k in fail:
            lines.append(f"- {k}")
        lines.append("")
    else:
        lines.append("## ✅ Manifest Tasks")
        lines.append("- All tasks OK")
        lines.append("")

    # 2) History: if series_n==0 or ok_all==False
    hsum = history.get("summary") or {}
    if hsum.get("series_n", 0) == 0:
        lines.append("## ⚠️ History")
        lines.append("- No exports found for history.")
        lines.append("")
    elif not hsum.get("ok_all", True):
        lines.append("## ❌ History")
        lines.append("- Trend checks not all OK.")
        lines.append("")

    # 3) Delta: if ok == False
    dsum = delta.get("summary") or {}
    if dsum.get("has_previous") and not dsum.get("ok", True):
        lines.append("## ❌ Delta")
        lines.append(
            f"- removed_nodes={dsum.get('removed_ids') or dsum.get('removed_nodes')}, "
            f"removed_edges={dsum.get('removed_edges')}"
        )
        lines.append("")

    # 4) ID stability: if ok == False or jaccard below threshold
    isb = idstab.get("summary") or {}
    if isb.get("has_previous") and not isb.get("ok", True):
        lines.append("## ❌ ID Stability")
        lines.append(f"- jaccard={isb.get('jaccard')} added={isb.get('added_ids')} removed={isb.get('removed_ids')}")
        lines.append("")

    # 5) Referential integrity: extract counts from report result if present
    ri = None
    for r in report.get("results") or []:
        if r.get("key") == "exports_ref_integrity_latest":
            ri = r
            break
    if ri:
        c = ri.get("counts", {})
        if any(
            [
                c.get("missing_endpoints", 0) > 0,
                c.get("self_loops", 0) > 0,
                c.get("duplicate_node_ids", 0) > 0,
                c.get("duplicate_edge_pairs", 0) > 0,
            ]
        ):
            lines.append("## ⚠️ Referential Integrity (counts)")
            lines.append(
                f"- missing_endpoints={c.get('missing_endpoints', 0)} "
                f"self_loops={c.get('self_loops', 0)} "
                f"dup_node_ids={c.get('duplicate_node_ids', 0)} "
                f"dup_edge_pairs={c.get('duplicate_edge_pairs', 0)}"
            )
            lines.append("")

    if len(lines) <= 4:
        lines.append("_No anomalies detected._")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[eval.anomalies] wrote {OUT.relative_to(ROOT)}")
    print("[eval.anomalies] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
