# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import json
import pathlib
import time
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
LOG = EVAL / "run_log.jsonl"


def _load(p: pathlib.Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def main() -> int:
    print("[eval.runlog] starting")
    EVAL.mkdir(parents=True, exist_ok=True)
    row = {
        "ts_unix": int(time.time()),
        "provenance": _load(EVAL / "provenance.json"),
        "report": _load(EVAL / "report.json"),
        "history": _load(EVAL / "history.json"),
        "delta": _load(EVAL / "delta.json"),
        "id_stability": _load(EVAL / "id_stability.json"),
    }
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
    print(f"[eval.runlog] appended {LOG.relative_to(ROOT)}")
    print("[eval.runlog] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
