# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import itertools
import json
import pathlib
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
LATEST = ROOT / "exports" / "graph_latest.json"
OUT = ROOT / "share" / "eval" / "integrity_diag.md"


def _load(p: pathlib.Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    print("[diag.integrity] starting")
    if not LATEST.exists():
        print("[diag.integrity] FAIL no exports/graph_latest.json")
        return 2
    doc = _load(LATEST)
    nodes = doc.get("nodes", []) or []
    edges = doc.get("edges", []) or []
    node_ids: set[Any] = {n.get("id") for n in nodes if isinstance(n, dict) and "id" in n}

    missing = []
    for e in edges:
        if not isinstance(e, dict):
            continue
        s, t = e.get("source"), e.get("target")
        if s not in node_ids or t not in node_ids:
            missing.append((s, t))

    examples = list(itertools.islice(missing, 10))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "# Integrity Diagnostics\n\n"
        f"*missing_endpoints:* {len(missing)}\n\n"
        "## Examples (up to 10)\n\n" + "\n".join(f"- {pair}" for pair in examples) + "\n",
        encoding="utf-8",
    )
    print(f"[diag.integrity] missing_endpoints={len(missing)}")
    print(f"[diag.integrity] wrote {OUT.relative_to(ROOT)}")
    print("[diag.integrity] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
