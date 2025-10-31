#!/usr/bin/env python3
import json
import pathlib
import time
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
OUT = EVAL / "release_notes.md"


def _load(p: pathlib.Path) -> dict[str, Any] | None:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def main() -> int:
    print("[eval.release_notes] starting")
    EVAL.mkdir(parents=True, exist_ok=True)
    report = _load(EVAL / "report.json") or {}
    hist = _load(EVAL / "history.json") or {}
    delta = _load(EVAL / "delta.json") or {}
    idst = _load(EVAL / "id_stability.json") or {}
    prov = _load(EVAL / "provenance.json") or {}
    policy = (EVAL / "policy_diff.md").read_text(encoding="utf-8") if (EVAL / "policy_diff.md").exists() else ""
    s = report.get("summary", {})
    ok, fail, tasks = (
        s.get("ok_count", 0),
        s.get("fail_count", 0),
        s.get("task_count", 0),
    )
    hist_ok = (hist.get("summary", {}) or {}).get("ok_all", True)
    hist_n = (hist.get("summary", {}) or {}).get("series_n", 0)
    isb = idst.get("summary", {}) or {}
    jaccard = isb.get("jaccard")
    id_added = isb.get("added_ids")
    id_removed = isb.get("removed_ids")
    dsum = delta.get("summary", {}) or {}
    d_has_prev = dsum.get("has_previous")
    d_ok = dsum.get("ok", True)

    lines = []
    lines.append("# Gemantria – Release Notes (Local Eval)\n")
    lines.append(f"*generated:* {int(time.time())}")
    if prov:
        head = prov.get("repo", {}).get("git_head")
        branch = prov.get("repo", {}).get("git_branch")
        lines.append(f"*git:* `{head}` on `{branch}`")
    lines.append("\n## Summary")
    lines.append(f"- Manifest tasks: **{ok}/{tasks} OK**, **{fail} FAIL**")
    lines.append(f"- History: series={hist_n} • ok_all={'✅' if hist_ok else '❌'}")
    if jaccard is not None:
        lines.append(f"- ID stability: jaccard={jaccard} • added={id_added} • removed={id_removed}")
    if d_has_prev is not None:
        lines.append(f"- Delta: has_previous={d_has_prev} • ok={'✅' if d_ok else '❌'}\n")
    lines.append("## Policy Delta (strict vs dev)")
    lines.append(policy.strip() or "_No policy_diff.md present._\n")
    lines.append("## Provenance (excerpt)")
    if prov:
        pv = {
            "git_head": prov.get("repo", {}).get("git_head"),
            "manifest_version": prov.get("manifest_version"),
            "thresholds_version": prov.get("thresholds_version"),
            "exports_count": (prov.get("exports", {}) or {}).get("count"),
        }
        lines.append("```json")
        import json as _json

        lines.append(_json.dumps(pv, indent=2, sort_keys=True))
        lines.append("```")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[eval.release_notes] wrote {OUT.relative_to(ROOT)}")
    print("[eval.release_notes] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
